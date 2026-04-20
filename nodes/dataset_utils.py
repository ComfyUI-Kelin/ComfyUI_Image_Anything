import fnmatch
import os

import numpy as np
import torch
from PIL import Image, ImageOps

from .auto_queue_control import stop_current_iteration
from .save_resolver import (
    build_output_path,
    normalize_extension,
    normalize_save_spec,
)


_LOADER_COUNTERS = {}
_SAVER_COUNTERS = {}
_SAVE_SPEC_IMAGE_FORMATS = ("png", "jpg", "webp")


class EditDatasetLoader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_dir": ("STRING", {"default": "", "multiline": False, "tooltip": "Path to image folder"}),
                "start_index": ("INT", {"default": 0, "min": 0, "max": 999999, "step": 1}),
                "auto_next": ("BOOLEAN", {"default": True, "label_on": "Auto Next", "label_off": "Fixed Index"}),
                "reset_iterator": ("BOOLEAN", {"default": False, "label_on": "Reset Index", "label_off": "Continue"}),
            },
            "optional": {
                "index_list": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Comma-separated indices to process, e.g. '5,12,23'. Leave empty for sequential mode.",
                }),
                "control_img_suffix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Suffix for Control Image to find (e.g. _W). Replaces target suffix.",
                }),
                "target_img_suffix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Suffix for Target Image to load (e.g. _O). Acts as filter.",
                }),
                "save_spec": ("ITERATOR_SAVE_SPEC", {
                    "forceInput": True,
                    "tooltip": "Optional shared save rules. Completed outputs are skipped automatically.",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "STRING", "INT")
    RETURN_NAMES = ("control_img", "target_img", "filename_stem", "directory", "current_index")
    FUNCTION = "load_data"
    CATEGORY = "🚦 ComfyUI_Image_Anything/Edit_Image"

    @classmethod
    def IS_CHANGED(cls, input_dir, start_index, auto_next, reset_iterator,
                   index_list="", target_img_suffix="", control_img_suffix="", save_spec=None, **kwargs):
        if reset_iterator:
            return float("NaN")
        if not auto_next:
            return float("nan")
        return float("NaN")

    @staticmethod
    def _build_filename_stem(filename, target_img_suffix=""):
        stem = os.path.splitext(filename)[0]
        if target_img_suffix and target_img_suffix in stem:
            stem = stem.replace(target_img_suffix, "")
        return stem

    @staticmethod
    def _iter_expected_outputs(filename_stem, save_spec):
        if save_spec is None:
            return []

        outputs = []
        for file_ext in _SAVE_SPEC_IMAGE_FORMATS:
            outputs.append(build_output_path(save_spec, filename_stem, leaf_dir="target_images", file_ext=file_ext))
            outputs.append(build_output_path(save_spec, filename_stem, leaf_dir="control_images", file_ext=file_ext))
        outputs.append(build_output_path(save_spec, filename_stem, leaf_dir="target_images", file_ext="txt"))
        return outputs

    @classmethod
    def _is_completed(cls, filename_stem, save_spec):
        return any(os.path.exists(path) for path in cls._iter_expected_outputs(filename_stem, save_spec))

    def load_data(self, input_dir, start_index, auto_next, reset_iterator,
                  index_list="", target_img_suffix="", control_img_suffix="", save_spec=None):
        global _LOADER_COUNTERS

        if not os.path.exists(input_dir):
            print(f"EditDatasetLoader: Directory {input_dir} not found.")
            return self._empty_result(input_dir=input_dir)

        valid_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
        all_files = os.listdir(input_dir)

        if target_img_suffix:
            search_pattern = f"*{target_img_suffix}.*"
            filtered_files = fnmatch.filter(all_files, search_pattern)
            files = [name for name in filtered_files if os.path.splitext(name)[1].lower() in valid_extensions]
        else:
            files = [name for name in all_files if os.path.splitext(name)[1].lower() in valid_extensions]

        files.sort()
        if not files:
            print(f"EditDatasetLoader: No images found in {input_dir} (Suffix: {target_img_suffix})")
            return self._empty_result(input_dir=input_dir)

        target_indices = None
        if index_list and index_list.strip():
            try:
                target_indices = [int(value.strip()) for value in index_list.split(",") if value.strip().isdigit()]
                if target_indices:
                    print(f"EditDatasetLoader: Index list mode - processing indices: {target_indices}")
            except ValueError:
                print(f"EditDatasetLoader: Invalid index_list format '{index_list}', falling back to sequential mode")
                target_indices = None

        key = f"{input_dir}_list_{index_list}" if target_indices else input_dir
        if reset_iterator or key not in _LOADER_COUNTERS:
            _LOADER_COUNTERS[key] = 0 if target_indices else start_index
            if reset_iterator:
                print(f"EditDatasetLoader: Iterator reset for {input_dir}")

        spec = normalize_save_spec(save_spec) if save_spec is not None else None

        final_index = None
        current_stem = ""
        filename = ""

        if target_indices:
            while True:
                list_position = _LOADER_COUNTERS[key]
                if list_position >= len(target_indices):
                    print(f"EditDatasetLoader: All {len(target_indices)} specified indices processed. Stopping workflow.")
                    _LOADER_COUNTERS[key] = len(target_indices)
                    stop_current_iteration(
                        "EditDatasetLoader",
                        input_dir=input_dir,
                        iteration_mode="index_list",
                        total_count=len(files),
                        processed_count=len(target_indices),
                        target_indices=target_indices,
                    )

                candidate_index = target_indices[list_position]
                if candidate_index >= len(files):
                    print(f"EditDatasetLoader: Index {candidate_index} out of range (Total: {len(files)}). Skipping.")
                    if auto_next:
                        _LOADER_COUNTERS[key] += 1
                        continue
                    return self._empty_result(input_dir=input_dir, current_index=candidate_index)

                candidate_filename = files[candidate_index]
                candidate_stem = self._build_filename_stem(candidate_filename, target_img_suffix)
                if self._is_completed(candidate_stem, spec):
                    print(f"EditDatasetLoader: Skipping completed sample {candidate_stem} (index {candidate_index}).")
                    if auto_next:
                        _LOADER_COUNTERS[key] += 1
                        continue
                    return self._empty_result(input_dir=input_dir, current_index=candidate_index)

                final_index = candidate_index
                filename = candidate_filename
                current_stem = candidate_stem
                break
        else:
            while True:
                candidate_index = _LOADER_COUNTERS[key] if auto_next else start_index
                if candidate_index >= len(files):
                    print(f"EditDatasetLoader: Index {candidate_index} out of range (Total: {len(files)}). Stopping workflow.")
                    if auto_next:
                        _LOADER_COUNTERS[key] = len(files)
                    stop_current_iteration(
                        "EditDatasetLoader",
                        input_dir=input_dir,
                        iteration_mode="sequential" if auto_next else "fixed_index",
                        total_count=len(files),
                        current_index=candidate_index,
                        start_index=start_index,
                    )

                candidate_filename = files[candidate_index]
                candidate_stem = self._build_filename_stem(candidate_filename, target_img_suffix)
                if self._is_completed(candidate_stem, spec):
                    print(f"EditDatasetLoader: Skipping completed sample {candidate_stem} (index {candidate_index}).")
                    if auto_next:
                        _LOADER_COUNTERS[key] += 1
                        continue
                    return self._empty_result(input_dir=input_dir, current_index=candidate_index)

                final_index = candidate_index
                filename = candidate_filename
                current_stem = candidate_stem
                break

        image_path = os.path.join(input_dir, filename)

        if auto_next:
            _LOADER_COUNTERS[key] += 1
            if target_indices:
                remaining = len(target_indices) - _LOADER_COUNTERS[key]
                print(f"EditDatasetLoader: Processed {current_stem} (index {final_index}). Remaining: {remaining}")
            else:
                print(f"EditDatasetLoader: Processed {current_stem} ({final_index}). Next: {final_index + 1}")

        tensor = self._load_img(image_path)
        control_tensor = self._empty_image()

        if target_img_suffix and control_img_suffix:
            if target_img_suffix in filename:
                target_filename_base = filename.replace(target_img_suffix, control_img_suffix)
                target_stem = os.path.splitext(target_filename_base)[0]
                match_file = None

                for candidate in os.listdir(input_dir):
                    if candidate.startswith(target_stem) and os.path.splitext(candidate)[1].lower() in valid_extensions:
                        if os.path.splitext(candidate)[0] == target_stem:
                            match_file = candidate
                            break

                if match_file:
                    control_tensor = self._load_img(os.path.join(input_dir, match_file))
                else:
                    print(f"EditDatasetLoader: Control file for {filename} not found (Target component: {target_stem})")
            else:
                print(f"EditDatasetLoader: target suffix '{target_img_suffix}' not found in filename '{filename}'")

        return (control_tensor, tensor, current_stem, input_dir, final_index)

    def _load_img(self, path):
        if not path or not os.path.exists(path):
            return self._empty_image()
        try:
            image = Image.open(path)
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
            array = np.array(image).astype(np.float32) / 255.0
            return torch.from_numpy(array)[None,]
        except Exception as exc:
            print(f"Error loading {path}: {exc}")
            return self._empty_image()

    def _empty_image(self):
        return torch.zeros((1, 512, 512, 3), dtype=torch.float32)

    def _empty_result(self, input_dir="", current_index=-1):
        return (self._empty_image(), self._empty_image(), "", input_dir, current_index)


class EditDatasetSaver:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_root": ("STRING", {"default": "", "tooltip": "Root directory for saving"}),
                "naming_style": (["Keep Original", "Rename (Prefix + Auto-Inc)"],),
                "filename_prefix": ("STRING", {"default": "Dataset"}),
                "allow_overwrite": ("BOOLEAN", {"default": False, "label_on": "Overwrite", "label_off": "Skip Existing"}),
            },
            "optional": {
                "filename_stem": ("STRING", {"default": "", "forceInput": True}),
                "save_image_control": ("IMAGE",),
                "save_image_target": ("IMAGE",),
                "save_caption": ("STRING", {"forceInput": True}),
                "save_format": (["jpg", "png", "webp"],),
                "output_dir": ("STRING", {"forceInput": True, "tooltip": "Optional: Override output_root with this path"}),
                "save_spec": ("ITERATOR_SAVE_SPEC", {
                    "forceInput": True,
                    "tooltip": "Optional shared save rules. When connected, use Keep Original naming.",
                }),
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save_dataset"
    CATEGORY = "🚦 ComfyUI_Image_Anything/Edit_Image"

    def save_dataset(self, output_root, naming_style, filename_prefix, allow_overwrite,
                     filename_stem="", save_image_control=None, save_image_target=None, save_caption=None,
                     save_format="jpg", output_dir=None, save_spec=None):
        if save_spec is not None:
            return self._save_with_spec(
                save_spec=save_spec,
                naming_style=naming_style,
                filename_stem=filename_stem,
                save_image_control=save_image_control,
                save_image_target=save_image_target,
                save_caption=save_caption,
                save_format=save_format,
            )

        if output_dir and output_dir.strip():
            output_root = output_dir

        if not output_root:
            print("EditDatasetSaver: No output_root provided.")
            return {}

        control_dir = os.path.join(output_root, "control_images")
        target_dir = os.path.join(output_root, "target_images")
        os.makedirs(control_dir, exist_ok=True)
        os.makedirs(target_dir, exist_ok=True)

        if naming_style == "Rename (Prefix + Auto-Inc)":
            global _SAVER_COUNTERS
            key = f"{output_root}_{filename_prefix}"
            if key not in _SAVER_COUNTERS:
                max_idx = -1
                for folder in (control_dir, target_dir):
                    if not os.path.exists(folder):
                        continue
                    for existing_name in os.listdir(folder):
                        if not existing_name.startswith(filename_prefix):
                            continue
                        try:
                            base_name = os.path.splitext(existing_name)[0]
                            remain = base_name[len(filename_prefix):]
                            if remain.startswith("_") and remain[1:].isdigit():
                                max_idx = max(max_idx, int(remain[1:]))
                        except Exception:
                            continue
                _SAVER_COUNTERS[key] = max_idx + 1

            current_idx = _SAVER_COUNTERS[key]
            final_name = f"{filename_prefix}_{current_idx:04d}"
            _SAVER_COUNTERS[key] += 1
        else:
            final_name = filename_stem.strip() if filename_stem else "unknown"

        target_path = os.path.join(target_dir, f"{final_name}.{save_format}")
        control_path = os.path.join(control_dir, f"{final_name}.{save_format}")
        caption_path = os.path.join(target_dir, f"{final_name}.txt")

        paths_to_check = []
        if save_image_control is not None:
            paths_to_check.append(control_path)
        if save_image_target is not None:
            paths_to_check.append(target_path)
        if save_caption is not None:
            paths_to_check.append(caption_path)

        if not allow_overwrite and any(os.path.exists(path) for path in paths_to_check):
            print(f"EditDatasetSaver: Skipping existing sample {final_name}.")
            return {}

        print(f"EditDatasetSaver: Saving {final_name} (Style: {naming_style})...")

        if save_image_control is not None:
            self._save_image(save_image_control, control_path)

        if save_image_target is not None:
            self._save_image(save_image_target, target_path)

        if save_caption is not None:
            try:
                with open(caption_path, "w", encoding="utf-8") as handle:
                    handle.write(save_caption)
            except Exception as exc:
                print(f"Error saving caption {caption_path}: {exc}")

        return {}

    def _save_with_spec(self, save_spec, naming_style, filename_stem,
                        save_image_control=None, save_image_target=None, save_caption=None, save_format="jpg"):
        spec = normalize_save_spec(save_spec)
        if naming_style != "Keep Original":
            raise ValueError("Iterator Save Spec only supports 'Keep Original' naming in EditDatasetSaver.")

        final_name = (filename_stem or "").strip()
        if not final_name:
            raise ValueError("filename_stem is required when using save_spec in EditDatasetSaver.")

        target_path = build_output_path(spec, final_name, leaf_dir="target_images", file_ext=save_format)
        control_path = build_output_path(spec, final_name, leaf_dir="control_images", file_ext=save_format)
        caption_path = os.path.splitext(target_path)[0] + ".txt"

        requested_paths = []
        if save_image_control is not None:
            requested_paths.append(control_path)
        if save_image_target is not None:
            requested_paths.append(target_path)
        if save_caption is not None:
            requested_paths.append(caption_path)

        if spec["exists_policy"] == "skip" and requested_paths and all(os.path.exists(path) for path in requested_paths):
            print(f"EditDatasetSaver: Skipping completed sample {final_name}.")
            return {}

        if spec["exists_policy"] == "error":
            for path in requested_paths:
                if os.path.exists(path):
                    raise FileExistsError(f"Output already exists: {path}")

        if save_image_control is not None:
            self._save_image(save_image_control, control_path)

        if save_image_target is not None:
            self._save_image(save_image_target, target_path)

        if save_caption is not None:
            os.makedirs(os.path.dirname(caption_path), exist_ok=True)
            with open(caption_path, "w", encoding="utf-8") as handle:
                handle.write(save_caption)

        print(f"EditDatasetSaver: Saved {final_name} via shared save_spec.")
        return {}

    def _save_image(self, tensor, path):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            img_tensor = tensor[0]
            array = 255.0 * img_tensor.cpu().numpy()
            image = Image.fromarray(np.clip(array, 0, 255).astype(np.uint8))

            extension = normalize_extension(os.path.splitext(path)[1]).lstrip(".")
            format_name = {
                "png": "PNG",
                "jpg": "JPEG",
                "jpeg": "JPEG",
                "webp": "WEBP",
            }.get(extension, "PNG")

            save_kwargs = {}
            if format_name == "JPEG":
                if image.mode not in ("RGB", "L"):
                    image = image.convert("RGB")
                save_kwargs["quality"] = 95
            elif format_name == "WEBP":
                save_kwargs["quality"] = 95
            elif format_name == "PNG":
                save_kwargs["optimize"] = True

            image.save(path, format=format_name, **save_kwargs)
        except Exception as exc:
            print(f"Error saving image {path}: {exc}")
