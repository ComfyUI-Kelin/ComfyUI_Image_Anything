# ComfyUI Image Anything

**English** | [**中文**](README.zh-CN.md)

[![GitHub stars](https://img.shields.io/github/stars/ComfyUI-Kelin/ComfyUI_Image_Anything?style=social)](https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything)
[![GitHub forks](https://img.shields.io/github/forks/ComfyUI-Kelin/ComfyUI_Image_Anything?style=social)](https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Nodes-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

A comprehensive set of ComfyUI custom nodes for **batch image processing**, **dataset preparation**, **smart resizing**, and **folder iteration** — designed to streamline repetitive image workflows.

## Core Features

### 1. Image Folder Iterator
Iterate through images in a folder one by one, with **Auto Queue** support for fully automated batch processing.
- Sequential or loop mode
- Recursive subfolder scanning with directory structure preservation
- Outputs filename, subfolder path, index, and total count
- Paired with **Image Saver** for saving processed images while maintaining the original folder hierarchy

### 2. Dataset Auto-Annotation
Purpose-built for creating training datasets for image editing models (Qwen Edit, Kontext, etc.).
- **EditDatasetLoader**: Iterates through image folders with auto-stop, index lists for re-processing failed images, and paired data loading (target + control images)
- **EditDatasetSaver**: Structured saving with original or auto-incremented naming, overwrite control, and multi-format output (jpg/png/webp)

### 3. Smart Bucket Resizing
Optimized for SDXL/Flux model training — automatically detects aspect ratio and center-crops to the nearest standard bucket resolution with zero stretching and no black bars.
- Supported buckets: 1024x1024, 832x1152, 1152x832, 768x1344, 1344x768
- Modes: Smart auto-detect or force specific ratio

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
```
[Image Iterator] --> [Your Processing Nodes] --> [Image Saver]
      |-- filename -----------------------------> filename
      |-- subfolder ----------------------------> subfolder
```
1. Set the **folder_path** in Image Iterator
2. Enable **Subfolders On** if you need to scan subdirectories
3. Connect your processing nodes in between
4. Turn on **Auto Queue** in ComfyUI, click **Queue Prompt** — done!

### Prepare a Training Dataset
```
[EditDatasetLoader] --> [Processing / Captioning] --> [EditDatasetSaver]
```
1. Point the Loader to your image folder
2. Connect any processing nodes (resize, caption generation, style transfer, etc.)
3. Set the Saver's output root and naming style
4. Auto Queue handles the rest — stops automatically when all images are processed

## Node Reference

| Category | Node | Description |
|----------|------|-------------|
| Iterator | **Image Iterator** | Load images one-by-one from a folder with Auto Queue support |
| Iterator | **Image Saver** | Save processed images with optional subfolder structure preservation |
| Preprocess | **Smart Image Resize for Bucket** | Auto center-crop to SDXL/Flux standard training resolutions |
| Dataset | **EditDatasetLoader** | Iterate dataset images with paired loading and failure re-processing |
| Dataset | **EditDatasetSaver** | Save dataset outputs with structured naming and format control |
| Batch Save | **Batch Image Saver V2** | Dynamic batch saving with timestamp organization |
| Batch Save | **Image Collector** | Collect up to 5 images with custom save names |
| Batch Save | **Text Collector** | Collect up to 5 text outputs with custom filenames |
| Text | **Text Blocker** | Pause workflow for manual text review/editing before continuing |

### Finding Nodes in ComfyUI

All nodes are under the `ComfyUI_Image_Anything` category (marked with a traffic light icon):

| Subcategory | Path |
|-------------|------|
| Preprocess | `ComfyUI_Image_Anything` > `Preprocess` |
| Dataset | `ComfyUI_Image_Anything` > `Edit_Image` |
| Batch Save | `ComfyUI_Image_Anything` > `Batch_Save` |
| Iterator | `ComfyUI_Image_Anything` > `Iterator` |
| Text | `ComfyUI_Image_Anything` > `Text` |

## Output Structure

Each batch run creates an organized timestamp folder:
```
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

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

[MIT](LICENSE)
