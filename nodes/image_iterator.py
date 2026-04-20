import os

import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence

from .auto_queue_control import stop_current_iteration
from .save_resolver import build_output_path, is_processing_complete, normalize_save_spec


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".tif", ".gif"}


class ImageIterator:
    _counters = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Absolute path to the image folder",
                    "tooltip": "Folder that contains the images to iterate.",
                }),
                "sort_by": (["name_asc", "name_desc", "modified_asc", "modified_desc"], {
                    "default": "name_asc",
                    "tooltip": "Sort images by name or modified time.",
                }),
                "mode": (["sequential", "loop"], {
                    "default": "sequential",
                    "tooltip": "Sequential stops after the last pending image. Loop wraps around.",
                }),
                "recursive": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Subfolders On",
                    "label_off": "Subfolders Off",
                    "tooltip": "Scan subfolders recursively.",
                }),
            },
            "optional": {
                "start_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "tooltip": "Start index used on first run or after reset.",
                }),
                "reset": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Reset",
                    "label_off": "Continue",
                    "tooltip": "Reset the iterator back to the start index.",
                }),
                "save_spec": ("ITERATOR_SAVE_SPEC", {
                    "forceInput": True,
                    "tooltip": "Optional shared save rules. Completed outputs are skipped automatically.",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "filename", "filename_with_ext", "subfolder", "current_index", "total_count")
    FUNCTION = "load_next_image"
    OUTPUT_NODE = False
    CATEGORY = "🚦 ComfyUI_Image_Anything/Iterator"
    DESCRIPTION = "Iterate through a folder of images. Optionally skips files that already have finished outputs."

    @classmethod
    def _get_counter_key(cls, folder_path, sort_by, recursive=False):
        return f"{folder_path}|{sort_by}|{recursive}"

    @classmethod
    def _get_image_list(cls, folder_path, sort_by, recursive=False):
        if not os.path.isdir(folder_path):
            return []

        files = []
        if recursive:
            for root, _dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        rel_path = os.path.relpath(os.path.join(root, filename), folder_path)
                        files.append(rel_path)
        else:
            for filename in os.listdir(folder_path):
                full_path = os.path.join(folder_path, filename)
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_EXTENSIONS and os.path.isfile(full_path):
                    files.append(filename)

        if sort_by == "name_asc":
            files.sort()
        elif sort_by == "name_desc":
            files.sort(reverse=True)
        elif sort_by == "modified_asc":
            files.sort(key=lambda rel_path: os.path.getmtime(os.path.join(folder_path, rel_path)))
        elif sort_by == "modified_desc":
            files.sort(key=lambda rel_path: os.path.getmtime(os.path.join(folder_path, rel_path)), reverse=True)

        return files

    @staticmethod
    def _resolve_pending_index(image_files, start_index, mode, save_spec):
        total_count = len(image_files)
        if total_count == 0:
            return None

        if save_spec is None:
            if mode == "loop":
                return start_index % total_count
            return start_index if 0 <= start_index < total_count else None

        if mode == "loop":
            base_index = start_index % total_count
            candidate_indices = list(range(base_index, total_count)) + list(range(0, base_index))
        else:
            if start_index >= total_count:
                return None
            candidate_indices = range(start_index, total_count)

        for index in candidate_indices:
            image_rel_path = image_files[index]
            subfolder = os.path.dirname(image_rel_path)
            image_filename = os.path.basename(image_rel_path)
            filename_no_ext = os.path.splitext(image_filename)[0]
            output_path = build_output_path(save_spec, filename_no_ext, subfolder=subfolder)
            if not is_processing_complete(output_path, save_spec):
                return index

        return None

    def load_next_image(self, folder_path, sort_by="name_asc", mode="sequential",
                        recursive=False, start_index=0, reset=False, save_spec=None):
        if not folder_path or not os.path.isdir(folder_path):
            raise ValueError(f"Invalid folder path: {folder_path}")

        image_files = self._get_image_list(folder_path, sort_by, recursive)
        total_count = len(image_files)
        if total_count == 0:
            raise ValueError(f"No supported image files found in folder: {folder_path}")

        counter_key = self._get_counter_key(folder_path, sort_by, recursive)
        if reset or counter_key not in ImageIterator._counters:
            current_index = start_index
        else:
            current_index = ImageIterator._counters[counter_key]

        spec = normalize_save_spec(save_spec) if save_spec is not None else None
        next_index = self._resolve_pending_index(image_files, current_index, mode, spec)
        if next_index is None:
            ImageIterator._counters[counter_key] = total_count
            stop_current_iteration(
                "ImageIterator",
                folder_path=folder_path,
                sort_by=sort_by,
                mode=mode,
                total_count=total_count,
                skipped_completed=spec is not None,
            )

        current_index = next_index
        image_rel_path = image_files[current_index]
        image_path = os.path.join(folder_path, image_rel_path)

        subfolder = os.path.dirname(image_rel_path)
        image_filename = os.path.basename(image_rel_path)
        filename_no_ext = os.path.splitext(image_filename)[0]

        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)

        output_images = []
        output_masks = []

        for frame in ImageSequence.Iterator(img):
            frame = ImageOps.exif_transpose(frame)

            if frame.mode == "I":
                frame = frame.point(lambda value: value * (1 / 255))
            image = frame.convert("RGB")

            image_np = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]

            if "A" in frame.getbands():
                mask = np.array(frame.getchannel("A")).astype(np.float32) / 255.0
                mask = 1.0 - torch.from_numpy(mask)
            elif frame.mode == "P" and "transparency" in frame.info:
                mask = np.array(frame.convert("RGBA").getchannel("A")).astype(np.float32) / 255.0
                mask = 1.0 - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

            output_images.append(image_tensor)
            output_masks.append(mask.unsqueeze(0))

            if img.format == "MPO":
                break

        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        if mode == "loop":
            ImageIterator._counters[counter_key] = (current_index + 1) % total_count
        else:
            ImageIterator._counters[counter_key] = current_index + 1

        return (
            output_image,
            output_mask,
            filename_no_ext,
            image_filename,
            subfolder,
            current_index,
            total_count,
        )

    @classmethod
    def IS_CHANGED(cls, folder_path, sort_by="name_asc", mode="sequential",
                   recursive=False, start_index=0, reset=False, save_spec=None):
        counter_key = cls._get_counter_key(folder_path, sort_by, recursive)
        current = cls._counters.get(counter_key, start_index)
        return f"{current}_{reset}_{bool(save_spec)}"
