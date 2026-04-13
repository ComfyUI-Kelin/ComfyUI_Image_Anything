# ComfyUI Image Anything

[**English**](README.md) | [**中文**](README.zh-CN.md) | **日本語** | [**한국어**](README.ko.md)

<!-- Translated from README.md @ commit 547ccc6 -->

[![GitHub stars](https://img.shields.io/github/stars/ComfyUI-Kelin/ComfyUI_Image_Anything?style=flat&logo=github&color=181717&labelColor=282828)](https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=flat&labelColor=1a1a2e)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Nodes-6366F1?style=flat&labelColor=1a1a2e&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJMMyA3djEwbDkgNSA5LTVWN3oiLz48L3N2Zz4=)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&labelColor=1a1a2e&logo=python&logoColor=white)](https://www.python.org/)

**バッチ画像処理**、**データセット作成**、**フォルダイテレーション**のための包括的な ComfyUI カスタムノードセットです。繰り返しの多い画像ワークフローを効率化するために設計されています。

## 主な機能

### 1. Image Folder Iterator
フォルダ内の画像を1枚ずつ順番に処理します。**Auto Queue** に対応しており、完全自動のバッチ処理が可能です。
- 順次モードまたはループモード
- サブフォルダの再帰スキャンとディレクトリ構造の保持
- ファイル名、サブフォルダパス、インデックス、合計数を出力
- **Image Saver** と組み合わせることで、元のフォルダ階層を維持しながら処理済み画像を保存

### 2. Dataset Auto-Annotation
画像編集モデル（Qwen Edit、Kontext など）のトレーニングデータセット作成に特化しています。
- **EditDatasetLoader**: 画像フォルダを自動停止付きでイテレーション、失敗画像の再処理用インデックスリスト、ペアデータの読み込み（ターゲット画像 + コントロール画像）
- **EditDatasetSaver**: 元のファイル名または自動連番による構造化保存、上書き制御、マルチフォーマット出力（jpg/png/webp）

### 3. Batch Workflow Saving
複数のワークフローステージからの画像とテキストを、タイムスタンプ付きのフォルダに整理して保存します。
- **Image Collector + Text Collector + Batch Image Saver V2**: モジュラー設計で、任意の数の画像バッチとテキストバッチを組み合わせ可能
- metadata.json を自動生成し、再現性のために完全な ComfyUI ワークフローを保存

## インストール

### 方法 1: Git Clone
```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything.git
```

### 方法 2: ComfyUI Manager（推奨）
ComfyUI Manager で **"ComfyUI_Image_Anything"** を検索してインストールしてください。

## クイックスタート

### フォルダ内の画像をバッチ処理する
```
[Image Iterator] --> [Your Processing Nodes] --> [Image Saver]
      |-- filename -----------------------------> filename
      |-- subfolder ----------------------------> subfolder
```
1. Image Iterator で **folder_path** を設定します
2. サブディレクトリをスキャンする場合は **Subfolders On** を有効にします
3. 中間に処理ノードを接続します
4. ComfyUI の **Auto Queue** をオンにして、**Queue Prompt** をクリックすれば完了です！

### トレーニングデータセットを作成する
```
[EditDatasetLoader] --> [Processing / Captioning] --> [EditDatasetSaver]
```
1. Loader に画像フォルダを指定します
2. 処理ノード（リサイズ、キャプション生成、スタイル変換など）を接続します
3. Saver の出力先ルートと命名スタイルを設定します
4. Auto Queue が残りを処理し、すべての画像が処理されると自動的に停止します

## ノードリファレンス

| カテゴリ | ノード | 説明 |
|----------|--------|------|
| Iterator | **Image Iterator** | フォルダから画像を1枚ずつ読み込み、Auto Queue に対応 |
| Iterator | **Image Saver** | サブフォルダ構造を保持しながら処理済み画像を保存 |
| Dataset | **EditDatasetLoader** | ペアデータの読み込みと失敗時の再処理に対応したデータセットイテレーター |
| Dataset | **EditDatasetSaver** | 構造化された命名とフォーマット制御でデータセット出力を保存 |
| Batch Save | **Batch Image Saver V2** | タイムスタンプ整理による動的バッチ保存 |
| Batch Save | **Image Collector** | 最大5枚の画像をカスタム名で収集 |
| Batch Save | **Text Collector** | 最大5つのテキスト出力をカスタムファイル名で収集 |
| Text | **Text Blocker** | 手動でテキストの確認・編集を行うためにワークフローを一時停止 |

### ComfyUI でノードを見つける

すべてのノードは `ComfyUI_Image_Anything` カテゴリ（信号機アイコン付き）の下にあります：

| サブカテゴリ | パス |
|-------------|------|
| Dataset | `ComfyUI_Image_Anything` > `Edit_Image` |
| Batch Save | `ComfyUI_Image_Anything` > `Batch_Save` |
| Iterator | `ComfyUI_Image_Anything` > `Iterator` |
| Text | `ComfyUI_Image_Anything` > `Text` |

## 出力構造

各バッチ実行時に、タイムスタンプ付きの整理されたフォルダが作成されます：
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

## 対応画像フォーマット

PNG, JPG, JPEG, BMP, WebP, TIFF, TIF, GIF

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ComfyUI-Kelin/ComfyUI_Image_Anything&type=Date)](https://star-history.com/#ComfyUI-Kelin/ComfyUI_Image_Anything&Date)

## コントリビューション

コントリビューションを歓迎します！Issue の作成や Pull Request の送信はお気軽にどうぞ。

## ライセンス

[MIT](LICENSE)

> この翻訳は機械翻訳をベースにしています。改善のための貢献を歓迎します。
