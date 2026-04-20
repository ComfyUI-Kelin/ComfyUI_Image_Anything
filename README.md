# ComfyUI Image Anything

[![GitHub stars](https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![GitHub forks](https://img.shields.io/github/forks/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Nodes-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

ComfyUI Image Anything 提供几组适合日常批处理的数据流节点：

- 逐张遍历文件夹图片
- 按原文件名稳定保存
- 自动跳过已经处理过的图片
- 支持递归子目录并保持目录结构
- 支持 Auto Queue 和 ComfyUI 实时运行下的连续批处理
- 支持数据集制作场景下的 Target / Control 配对处理

## 安装

### 方式一：Git Clone

```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/HuangYuChuh/ComfyUI_Image_Anything.git
```

### 方式二：ComfyUI Manager

在 ComfyUI Manager 中搜索 `ComfyUI_Image_Anything` 安装。

## 节点总览

### Preprocess

**Smart Image Resize for Bucket**

用于把图片裁切/缩放到常见训练分辨率桶，适合训练前预处理。

### Edit_Image

**EditDatasetLoader**

用于制作图像编辑数据集，支持：

- 逐张读取输入目录
- 指定起始索引
- 指定索引列表重跑
- Target / Control 成对加载
- 连接 `Processed Image Check` 后自动跳过已处理文件

**EditDatasetSaver**

用于保存数据集输出，支持：

- 保持原文件名
- 自动重命名加编号
- 保存 target image
- 保存 control image
- 保存 caption
- 覆盖已有文件或跳过已有文件
- 连接 `Processed Image Check` 时使用统一输出规则

### Batch_Save

**Image Collector / Text Collector / Batch Image Saver V2**

用于把多张图片和文本统一保存到一个批处理结果目录中。

### Iterator

**Processed Image Check**

这是新的“已处理图片检测”节点，用来告诉迭代器和保存器：

- 输出目录在哪里
- 是否保留子目录结构
- 文件已存在时是跳过、覆盖，还是报错

**Image Iterator**

逐张读取文件夹中的图片。

**Image Saver**

按文件名稳定保存处理后的结果，适合和 `Image Iterator` 一起使用。

### Text

**Text Blocker**

在流程中暂停并手动编辑文本后再继续执行。

## Processed Image Check

`Processed Image Check` 的作用很简单：

- 让系统知道输出目录在哪里
- 在每次处理前，先去输出目录里看对应结果是否已经存在
- 如果已经存在，就自动跳过这张图

### 参数

- `output_root`
  批处理输出目录。支持直接点击按钮选择本地文件夹。
- `keep_subfolder`
  是否保留输入目录的子目录结构。
- `exists_policy`
  输出已存在时的策略：
  - `skip`
  - `overwrite`
  - `error`

### 当前判断逻辑

假设输入图片是：

```text
input/cat/a.jpg
```

`output_root` 是：

```text
output
```

并且开启了 `keep_subfolder`，那么系统会检查：

```text
output/cat/a.png
```

如果这个文件已经存在：

- 这张图跳过
- 直接继续下一张

如果这个文件不存在：

- 继续处理
- 最终保存为 `output/cat/a.png`

## Iterator 工作流

### Image Iterator

`Image Iterator` 每次执行只处理一张图，但可以自动连续跑完整个文件夹。

#### 参数

- `folder_path`
- `sort_by`
  - `name_asc`
  - `name_desc`
  - `modified_asc`
  - `modified_desc`
- `mode`
  - `sequential`
  - `loop`
- `recursive`
- `start_index`
- `reset`
- `save_spec`
  可选。连接 `Processed Image Check` 后启用“已处理自动跳过”。

#### 输出

- `image`
- `mask`
- `filename`
- `filename_with_ext`
- `subfolder`
- `current_index`
- `total_count`

### Image Saver

#### 参数

- `image`
- `save_path`
- `filename`
- `subfolder`
- `save_spec`
  可选。连接 `Processed Image Check` 后，会按统一规则保存为稳定文件名。

## 推荐连接方式

```text
[Processed Image Check] ---> save_spec ---> [Image Iterator]
                         \-> save_spec ---> [Image Saver]

[Image Iterator] ---> [处理节点] ---> [Image Saver]
       |                                ^
       +---- filename ------------------+
       +---- subfolder -----------------+
```

## 连续批处理说明

### Auto Queue

使用 Auto Queue 时，迭代器会自动处理完整个文件夹，直到全部完成或全部被跳过。

### ComfyUI 实时运行

现在也支持 ComfyUI 的实时运行模式：

- 你只需要启动一次
- 每张处理完成后会自动继续下一张
- 遇到已存在的输出文件会自动跳过
- 当整个文件夹处理完成后会自动停止

## 递归扫描和目录保持

如果：

- `Image Iterator` 开启 `recursive=True`
- `Processed Image Check` 开启 `keep_subfolder=True`

那么输入目录结构会映射到输出目录。

### 示例

输入目录：

```text
/input/
  /cats/
    cat1.jpg
    cat2.jpg
  /dogs/
    dog1.jpg
```

输出目录：

```text
/output/
  /cats/
    cat1.png
    cat2.png
  /dogs/
    dog1.png
```

## Edit Dataset Workflow

### EditDatasetLoader

适合做图像编辑数据集，常见参数：

- `input_dir`
- `start_index`
- `auto_next`
- `reset_iterator`
- `index_list`
- `target_img_suffix`
- `control_img_suffix`
- `save_spec`

### EditDatasetSaver

常见参数：

- `output_root`
- `naming_style`
- `filename_prefix`
- `allow_overwrite`
- `filename_stem`
- `save_image_control`
- `save_image_target`
- `save_caption`
- `save_format`
- `output_dir`
- `save_spec`

### 配对加载示例

如果目录中有：

```text
Dog_O.jpg
Dog_W.png
```

并设置：

- `target_img_suffix = _O`
- `control_img_suffix = _W`

那么 Loader 读取 `Dog_O.jpg` 时，会自动寻找 `Dog_W.png` 作为 control 图输出。

## 节点查找

安装后可在以下分类中找到：

| 分类 | 路径 | 节点 |
|------|------|------|
| 预处理 | `ComfyUI_Image_Anything -> Preprocess` | Smart Image Resize for Bucket |
| 数据集 | `ComfyUI_Image_Anything -> Edit_Image` | EditDatasetLoader, EditDatasetSaver |
| 批量保存 | `ComfyUI_Image_Anything -> Batch_Save` | Batch Image Saver V2, Image Collector, Text Collector |
| 迭代器 | `ComfyUI_Image_Anything -> Iterator` | Processed Image Check, Image Iterator, Image Saver |
| 文本工具 | `ComfyUI_Image_Anything -> Text` | Text Blocker |
