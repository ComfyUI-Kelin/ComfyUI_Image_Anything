# ComfyUI Image Anything

[**English**](README.md) | **中文** | [**日本語**](README.ja.md) | [**한국어**](README.ko.md)

[![GitHub stars](https://img.shields.io/github/stars/ComfyUI-Kelin/ComfyUI_Image_Anything?style=flat&logo=github&color=181717&labelColor=282828)](https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=flat&labelColor=1a1a2e)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Nodes-6366F1?style=flat&labelColor=1a1a2e&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJMMyA3djEwbDkgNSA5LTVWN3oiLz48L3N2Zz4=)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&labelColor=1a1a2e&logo=python&logoColor=white)](https://www.python.org/)

**ComfyUI Image Anything** 提供适合批量图片处理、数据集制作、文件夹迭代和批量保存的 ComfyUI 自定义节点。

## 核心功能

### 1. 图片文件夹迭代器
从指定文件夹中逐张加载图片，配合 **Auto Queue** 或 **Instant Run** 可以自动连续处理整个文件夹。

- 支持顺序处理和循环处理
- 支持递归扫描子文件夹
- 输出文件名、完整文件名、子文件夹路径、当前索引和总数量
- 连接 **Processed Image Check** 后，可以自动跳过已经处理过的图片
- 配合 **Image Saver** 可以按原文件名稳定保存

### 2. Processed Image Check
这是“已处理图片检测”节点。它会在每张图处理前，先检查输出文件夹里是否已经有对应结果。

- 可以点击按钮选择本地输出文件夹
- 递归处理时可以保留原来的子文件夹结构
- 文件已存在时可以选择 skip、overwrite 或 error
- 同时支持普通图片迭代流程和数据集流程

### 3. 数据集自动标注
适合制作图像编辑模型训练数据集，例如 Qwen Edit、Kontext 等。

- **EditDatasetLoader**：逐张加载数据集图片，支持失败索引重跑、Target/Control 配对加载、已处理文件自动跳过
- **EditDatasetSaver**：结构化保存 control image、target image 和 caption，支持 jpg/png/webp

### 4. 批量工作流保存
把多个阶段的图片和文本统一保存到时间戳文件夹中。

- **Image Collector + Text Collector + Batch Image Saver V2**：可以自由组合多个图片批次和文本批次
- 自动保存 metadata.json 和完整 ComfyUI workflow，方便复现

## 安装方法

### 方式一：克隆仓库
```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything.git
```

### 方式二：ComfyUI Manager
在 ComfyUI Manager 中搜索 **ComfyUI_Image_Anything** 并安装。

## 快速使用

### 普通图片批处理
```text
[Processed Image Check] ---> save_spec ---> [Image Iterator]
                         \-> save_spec ---> [Image Saver]

[Image Iterator] --> [你的处理节点] --> [Image Saver]
      |-- filename ---------------------> filename
      |-- subfolder --------------------> subfolder
```

1. 在 **Image Iterator** 设置 `folder_path`。
2. 在 **Processed Image Check** 设置 `output_root`。
3. 把 `save_spec` 同时连接到 **Image Iterator** 和 **Image Saver**。
4. 打开 Auto Queue 或 Instant Run，只需要启动一次。

### 跳过逻辑示例
假设输入图片是：

```text
input/cat/a.jpg
```

Processed Image Check 设置为：

```text
output_root = output
keep_subfolder = true
```

系统会检查：

```text
output/cat/a.png
```

如果这个文件已经存在，就跳过 `a.jpg`；如果不存在，就继续处理并最终保存为 `output/cat/a.png`。

### 数据集批处理
```text
[Processed Image Check] ---> save_spec ---> [EditDatasetLoader]
                         \-> save_spec ---> [EditDatasetSaver]

[EditDatasetLoader] --> [处理或生成标题] --> [EditDatasetSaver]
```

1. Loader 指向你的图片文件夹。
2. 使用 Processed Image Check 时，Saver 的命名方式请选择 **Keep Original**。
3. 如果需要 jpg/png/webp，可以在 Saver 的 `save_format` 里选择。
4. Auto Queue 会自动跑完整个文件夹；已处理过的文件会自动跳过。

## 节点说明

| 分类 | 节点 | 说明 |
|------|------|------|
| Iterator | **Processed Image Check** | 设置输出文件夹和已处理图片检测规则 |
| Iterator | **Image Iterator** | 从文件夹逐张读取图片，支持 Auto Queue 和 Instant Run |
| Iterator | **Image Saver** | 保存处理后的图片，可保留子文件夹结构 |
| Edit_Image | **EditDatasetLoader** | 数据集逐张读取，支持配对加载和已处理跳过 |
| Edit_Image | **EditDatasetSaver** | 保存数据集输出，支持 control/target/caption 和多格式 |
| Batch_Save | **Batch Image Saver V2** | 批量保存多个图片和文本输出 |
| Batch_Save | **Image Collector** | 收集最多 5 张图片 |
| Batch_Save | **Text Collector** | 收集最多 5 段文本 |
| Text | **Text Blocker** | 执行中暂停并允许手动编辑文本 |

## Processed Image Check 参数

- `output_root`：处理结果保存到哪里。
- `keep_subfolder`：是否保留输入文件夹里的子目录结构。
- `exists_policy`：输出文件已存在时的处理方式。
- `skip`：已存在就跳过，推荐用于断点续跑。
- `overwrite`：已存在也覆盖。
- `error`：已存在就报错停止。

## 数据集流程补充

**EditDatasetLoader** 支持：

- `input_dir`：输入图片文件夹
- `start_index`：从第几张开始
- `auto_next`：是否自动下一张
- `reset_iterator`：是否重置进度
- `index_list`：只重跑指定索引，例如 `"5,12,23"`
- `target_img_suffix` / `control_img_suffix`：Target 和 Control 图片配对
- `save_spec`：连接 Processed Image Check 后启用已处理跳过

**EditDatasetSaver** 支持：

- `output_root`：输出根目录
- `naming_style`：Keep Original 或 Rename
- `allow_overwrite`：是否允许覆盖已有文件
- `save_format`：jpg/png/webp
- `save_spec`：连接 Processed Image Check 后使用统一输出规则

## 支持格式

PNG、JPG、JPEG、BMP、WebP、TIFF、TIF、GIF

## 节点查找

安装后，在 ComfyUI 节点列表中查找：

| 分类 | 路径 | 节点 |
|------|------|------|
| 数据集 | `ComfyUI_Image_Anything` -> `Edit_Image` | EditDatasetLoader, EditDatasetSaver |
| 批量保存 | `ComfyUI_Image_Anything` -> `Batch_Save` | Batch Image Saver V2, Image Collector, Text Collector |
| 迭代器 | `ComfyUI_Image_Anything` -> `Iterator` | Processed Image Check, Image Iterator, Image Saver |
| 文本工具 | `ComfyUI_Image_Anything` -> `Text` | Text Blocker |

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ComfyUI-Kelin/ComfyUI_Image_Anything&type=Date)](https://star-history.com/#ComfyUI-Kelin/ComfyUI_Image_Anything&Date)
