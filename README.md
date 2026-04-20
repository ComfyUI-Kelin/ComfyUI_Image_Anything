# ComfyUI Image Anything

**English** | [**中文**](README.zh-CN.md) | [**日本語**](README.ja.md) | [**한국어**](README.ko.md)

[![GitHub stars](https://img.shields.io/github/stars/ComfyUI-Kelin/ComfyUI_Image_Anything?style=flat&logo=github&color=181717&labelColor=282828)](https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=flat&labelColor=1a1a2e)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Nodes-6366F1?style=flat&labelColor=1a1a2e&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJMMyA3djEwbDkgNSA5LTVWN3oiLz48L3N2Zz4=)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&labelColor=1a1a2e&logo=python&logoColor=white)](https://www.python.org/)

A comprehensive set of ComfyUI custom nodes for **batch image processing**, **dataset preparation**, and **folder iteration**. It is designed to make repeated image workflows easier to run, resume, and organize.

## Core Features

### 1. Image Folder Iterator
Iterate through images in a folder one by one, with **Auto Queue** and **Instant Run** support for automated batch processing.

- Sequential or loop mode
- Recursive subfolder scanning with directory structure preservation
- Outputs filename, original filename, subfolder path, index, and total count
- Can skip images that already have processed outputs when connected to **Processed Image Check**
- Paired with **Image Saver** for stable filename-based saving

### 2. Processed Image Check
Compare the input image name with the output folder before processing. If the expected output already exists, the iterator skips that image and moves to the next one.

- Choose the output folder with a local folder picker
- Keep the original subfolder structure when processing recursively
- Choose what happens when an output already exists: skip, overwrite, or error
- Works with both normal iterator workflows and dataset workflows

### 3. Dataset Auto-Annotation
Purpose-built for creating training datasets for image editing models (Qwen Edit, Kontext, etc.).

- **EditDatasetLoader**: Iterates through image folders with auto-stop, index lists for re-processing failed images, paired data loading, and optional processed-output skipping
- **EditDatasetSaver**: Structured saving with original or auto-incremented naming, overwrite control, and multi-format output (jpg/png/webp)

### 4. Batch Workflow Saving
Save images and text from multiple workflow stages into organized timestamp folders.

- **Image Collector + Text Collector + Batch Image Saver V2**: Modular design, combine any number of image and text batches
- Auto-generates metadata.json and saves the full ComfyUI workflow for reproducibility

## Installation

### Option 1: Git Clone
```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything.git
```

### Option 2: ComfyUI Manager (Recommended)
Search for **"ComfyUI_Image_Anything"** in ComfyUI Manager and install.

## Quick Start

### Batch Process a Folder of Images
```text
[Processed Image Check] ---> save_spec ---> [Image Iterator]
                         \-> save_spec ---> [Image Saver]

[Image Iterator] --> [Your Processing Nodes] --> [Image Saver]
      |-- filename -----------------------------> filename
      |-- subfolder ----------------------------> subfolder
```

1. Set **folder_path** in Image Iterator.
2. Set **output_root** in Processed Image Check.
3. Connect `save_spec` to both Image Iterator and Image Saver.
4. Turn on Auto Queue or Instant Run, then queue once.

### Example Skip Logic
If the input image is:

```text
input/cat/a.jpg
```

And Processed Image Check uses:

```text
output_root = output
keep_subfolder = true
```

The workflow checks:

```text
output/cat/a.png
```

If that file exists, `a.jpg` is skipped. If it does not exist, the workflow processes it and Image Saver writes `output/cat/a.png`.

### Prepare a Training Dataset
```text
[Processed Image Check] ---> save_spec ---> [EditDatasetLoader]
                         \-> save_spec ---> [EditDatasetSaver]

[EditDatasetLoader] --> [Processing / Captioning] --> [EditDatasetSaver]
```

1. Point the Loader to your image folder.
2. Set the Saver to **Keep Original** naming when using Processed Image Check.
3. Choose the Saver's `save_format` if you need jpg/png/webp.
4. Auto Queue handles the rest and stops automatically when all images are processed or skipped.

## Node Reference

| Category | Node | Description |
|----------|------|-------------|
| Iterator | **Processed Image Check** | Defines the output folder and skip rules for already processed images |
| Iterator | **Image Iterator** | Load images one-by-one from a folder with Auto Queue and Instant Run support |
| Iterator | **Image Saver** | Save processed images with optional subfolder structure preservation |
| Dataset | **EditDatasetLoader** | Iterate dataset images with paired loading, failure re-processing, and processed-output skipping |
| Dataset | **EditDatasetSaver** | Save dataset outputs with structured naming and format control |
| Batch Save | **Batch Image Saver V2** | Dynamic batch saving with timestamp organization |
| Batch Save | **Image Collector** | Collect up to 5 images with custom save names |
| Batch Save | **Text Collector** | Collect up to 5 text outputs with custom filenames |
| Text | **Text Blocker** | Pause workflow for manual text review/editing before continuing |

### Finding Nodes in ComfyUI

All nodes are under the `ComfyUI_Image_Anything` category (marked with a traffic light icon):

| Subcategory | Path |
|-------------|------|
| Dataset | `ComfyUI_Image_Anything` > `Edit_Image` |
| Batch Save | `ComfyUI_Image_Anything` > `Batch_Save` |
| Iterator | `ComfyUI_Image_Anything` > `Iterator` |
| Text | `ComfyUI_Image_Anything` > `Text` |

## Output Structure

Each batch run creates an organized timestamp folder:
```text
output/
  batch_saves/
    task_20251130_143022/
      cover_01.png
      detail_02.png
      prompt.txt
      metadata.json
      workflow.json       # Full ComfyUI workflow (drag to reload)
```

## Supported Image Formats

PNG, JPG, JPEG, BMP, WebP, TIFF, TIF, GIF

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ComfyUI-Kelin/ComfyUI_Image_Anything&type=Date)](https://star-history.com/#ComfyUI-Kelin/ComfyUI_Image_Anything&Date)

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

[MIT](LICENSE)
