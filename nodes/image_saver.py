import os

import numpy as np
from PIL import Image

import folder_paths


class ImageSaver:
    def __init__(self):
        self.type = "output"
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "save_path": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "placeholder": "Absolute save path. Empty uses the ComfyUI output folder.",
                        "tooltip": "Folder path used to save the image.",
                    },
                ),
            },
            "optional": {
                "filename": (
                    "STRING",
                    {
                        "default": "",
                        "forceInput": True,
                        "tooltip": "Optional filename without extension. Leave disconnected or blank to use ComfyUI default naming.",
                    },
                ),
                "subfolder": (
                    "STRING",
                    {
                        "default": "",
                        "forceInput": True,
                        "tooltip": "Optional subfolder path. Keeps the iterator directory structure when connected.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("save_info",)
    FUNCTION = "save_image"
    OUTPUT_NODE = True
    CATEGORY = "\U0001F6A6 ComfyUI_Image_Anything/Iterator"
    DESCRIPTION = "Save an image to disk. Supports optional filename and subfolder inputs."

    def save_image(self, image, save_path="", filename="", subfolder=""):
        if save_path and save_path.strip():
            output_dir = save_path.strip()
        else:
            output_dir = self.output_dir

        if subfolder and subfolder.strip():
            output_dir = os.path.join(output_dir, subfolder.strip())

        os.makedirs(output_dir, exist_ok=True)

        i_array = image.cpu().numpy()
        if i_array.ndim == 4:
            i_array = i_array[0]

        i_array = (np.clip(i_array, 0, 1) * 255).astype(np.uint8)
        img = Image.fromarray(i_array)

        clean_filename = filename.strip() if isinstance(filename, str) else ""
        if clean_filename:
            full_filename = f"{clean_filename}.png"
            filepath = os.path.join(output_dir, full_filename)

            if os.path.exists(filepath):
                base = clean_filename
                counter = 1
                while os.path.exists(filepath):
                    full_filename = f"{base}_{counter:03d}.png"
                    filepath = os.path.join(output_dir, full_filename)
                    counter += 1
        else:
            full_output_folder, base_filename, counter, _, _ = folder_paths.get_save_image_path(
                "ComfyUI", output_dir, i_array.shape[1], i_array.shape[0]
            )
            full_filename = f"{base_filename}_{counter:05}_.png"
            filepath = os.path.join(full_output_folder, full_filename)

        img.save(filepath, format="PNG")
        return (filepath,)
