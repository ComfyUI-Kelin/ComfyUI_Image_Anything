import os


SAVE_SPEC_TYPE = "ITERATOR_SAVE_SPEC"


def normalize_extension(file_ext, default="png"):
    ext = (file_ext or default).strip().lower().lstrip(".")
    if not ext:
        ext = default
    return f".{ext}"


def normalize_subfolder(subfolder):
    if not subfolder:
        return ""

    normalized = os.path.normpath(subfolder).replace("/", os.sep).replace("\\", os.sep)
    if normalized in (".", ""):
        return ""
    if os.path.isabs(normalized) or normalized.startswith(".."):
        raise ValueError(f"Invalid subfolder path: {subfolder}")
    return normalized


def normalize_save_spec(save_spec):
    if not isinstance(save_spec, dict):
        raise ValueError("save_spec must be a dictionary created by Iterator Save Spec.")

    output_root = (save_spec.get("output_root") or "").strip()
    if not output_root:
        raise ValueError("save_spec.output_root cannot be empty.")

    return {
        "output_root": output_root,
        "keep_subfolder": bool(save_spec.get("keep_subfolder", True)),
        "file_ext": "png",
        "exists_policy": save_spec.get("exists_policy", "skip"),
    }


def build_output_path(save_spec, filename, subfolder="", leaf_dir=""):
    spec = normalize_save_spec(save_spec)
    clean_name = (filename or "").strip()
    if not clean_name:
        raise ValueError("filename cannot be empty when using save_spec.")

    parts = [spec["output_root"]]
    if leaf_dir:
        parts.append(leaf_dir)
    if spec["keep_subfolder"]:
        normalized_subfolder = normalize_subfolder(subfolder)
        if normalized_subfolder:
            parts.append(normalized_subfolder)

    output_dir = os.path.join(*parts)
    return os.path.join(output_dir, f"{clean_name}{normalize_extension(spec['file_ext'])}")


def ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def is_processing_complete(output_path, save_spec):
    normalize_save_spec(save_spec)
    return os.path.exists(output_path)


def resolve_existing_output(output_path, exists_policy):
    if not os.path.exists(output_path):
        return "write"
    if exists_policy == "overwrite":
        return "overwrite"
    if exists_policy == "skip":
        return "skip"
    raise FileExistsError(f"Output already exists: {output_path}")
