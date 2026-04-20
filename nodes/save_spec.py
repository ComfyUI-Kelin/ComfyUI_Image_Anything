from .save_resolver import SAVE_SPEC_TYPE, normalize_save_spec


class IteratorSaveSpec:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_root": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Shared output folder used by both the iterator skip-check and the saver.",
                }),
                "keep_subfolder": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Keep Subfolder",
                    "label_off": "Flat Output",
                    "tooltip": "Keep the iterator subfolder structure under the output root.",
                }),
                "exists_policy": (["skip", "overwrite", "error"], {
                    "default": "skip",
                    "tooltip": "What the saver should do when the target file already exists.",
                }),
            },
        }

    RETURN_TYPES = (SAVE_SPEC_TYPE, "STRING")
    RETURN_NAMES = ("save_spec", "summary")
    FUNCTION = "build_spec"
    CATEGORY = "🚦 ComfyUI_Image_Anything/Iterator"
    DESCRIPTION = "Shared output rules used by both iterator-side skip detection and the final saver."

    def build_spec(self, output_root, keep_subfolder, exists_policy):
        spec = normalize_save_spec({
            "output_root": output_root,
            "keep_subfolder": keep_subfolder,
            "exists_policy": exists_policy,
        })

        summary = (
            f"Output: {spec['output_root']} | "
            f"Ext: .{spec['file_ext']} | "
            f"Exists: {spec['exists_policy']}"
        )
        return (spec, summary)
