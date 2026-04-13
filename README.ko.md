# ComfyUI Image Anything

[**English**](README.md) | [**中文**](README.zh-CN.md) | [**日本語**](README.ja.md) | **한국어**

[![GitHub stars](https://img.shields.io/github/stars/ComfyUI-Kelin/ComfyUI_Image_Anything?style=flat&logo=github&color=181717&labelColor=282828)](https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=flat&labelColor=1a1a2e)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Nodes-6366F1?style=flat&labelColor=1a1a2e&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJMMyA3djEwbDkgNSA5LTVWN3oiLz48L3N2Zz4=)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&labelColor=1a1a2e&logo=python&logoColor=white)](https://www.python.org/)

**일괄 이미지 처리**, **데이터셋 준비**, **폴더 반복 처리**를 위한 ComfyUI 커스텀 노드 모음 — 반복적인 이미지 워크플로우를 간소화하도록 설계되었습니다.

## 핵심 기능

### 1. Image Folder Iterator
폴더 내 이미지를 하나씩 순회하며, **Auto Queue**를 지원하여 완전 자동화된 일괄 처리가 가능합니다.
- 순차 모드 또는 루프 모드
- 디렉토리 구조를 유지하면서 하위 폴더 재귀 스캔
- 파일명, 하위 폴더 경로, 인덱스, 전체 개수 출력
- **Image Saver**와 함께 사용하여 원본 폴더 계층 구조를 유지하면서 처리된 이미지 저장

### 2. Dataset Auto-Annotation
이미지 편집 모델(Qwen Edit, Kontext 등)의 학습 데이터셋 생성에 특화되어 있습니다.
- **EditDatasetLoader**: 자동 중지 기능이 있는 이미지 폴더 순회, 실패한 이미지 재처리를 위한 인덱스 리스트, 쌍 데이터 로딩(target + control 이미지)
- **EditDatasetSaver**: 원본 또는 자동 증가 네이밍을 통한 구조화된 저장, 덮어쓰기 제어, 다중 포맷 출력 (jpg/png/webp)

### 3. Batch Workflow Saving
여러 워크플로우 단계의 이미지와 텍스트를 체계적인 타임스탬프 폴더에 저장합니다.
- **Image Collector + Text Collector + Batch Image Saver V2**: 모듈식 설계로, 임의 개수의 이미지 및 텍스트 배치를 조합 가능
- metadata.json을 자동 생성하고 재현성을 위해 전체 ComfyUI 워크플로우를 저장

## 설치

### 방법 1: Git Clone
```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/ComfyUI-Kelin/ComfyUI_Image_Anything.git
```

### 방법 2: ComfyUI Manager (권장)
ComfyUI Manager에서 **"ComfyUI_Image_Anything"**을 검색하여 설치하세요.

## 빠른 시작

### 폴더 내 이미지 일괄 처리
```
[Image Iterator] --> [Your Processing Nodes] --> [Image Saver]
      |-- filename -----------------------------> filename
      |-- subfolder ----------------------------> subfolder
```
1. Image Iterator에서 **folder_path**를 설정하세요
2. 하위 디렉토리 스캔이 필요한 경우 **Subfolders On**을 활성화하세요
3. 중간에 처리 노드를 연결하세요
4. ComfyUI에서 **Auto Queue**를 켜고 **Queue Prompt**를 클릭하면 완료됩니다!

### 학습 데이터셋 준비
```
[EditDatasetLoader] --> [Processing / Captioning] --> [EditDatasetSaver]
```
1. Loader에 이미지 폴더를 지정하세요
2. 처리 노드(리사이즈, 캡션 생성, 스타일 전환 등)를 연결하세요
3. Saver의 출력 루트와 네이밍 스타일을 설정하세요
4. Auto Queue가 나머지를 처리합니다 — 모든 이미지가 처리되면 자동으로 중지됩니다

## 노드 참조

| 카테고리 | 노드 | 설명 |
|----------|------|------|
| Iterator | **Image Iterator** | Auto Queue를 지원하며 폴더에서 이미지를 하나씩 로드 |
| Iterator | **Image Saver** | 하위 폴더 구조를 선택적으로 유지하면서 처리된 이미지 저장 |
| Dataset | **EditDatasetLoader** | 쌍 로딩 및 실패 재처리 기능으로 데이터셋 이미지 순회 |
| Dataset | **EditDatasetSaver** | 구조화된 네이밍과 포맷 제어로 데이터셋 출력 저장 |
| Batch Save | **Batch Image Saver V2** | 타임스탬프 기반 정리를 통한 동적 일괄 저장 |
| Batch Save | **Image Collector** | 사용자 지정 저장 이름으로 최대 5개 이미지 수집 |
| Batch Save | **Text Collector** | 사용자 지정 파일명으로 최대 5개 텍스트 출력 수집 |
| Text | **Text Blocker** | 계속 진행하기 전에 수동 텍스트 검토/편집을 위해 워크플로우 일시 정지 |

### ComfyUI에서 노드 찾기

모든 노드는 `ComfyUI_Image_Anything` 카테고리 아래에 있습니다 (신호등 아이콘으로 표시):

| 하위 카테고리 | 경로 |
|--------------|------|
| Dataset | `ComfyUI_Image_Anything` > `Edit_Image` |
| Batch Save | `ComfyUI_Image_Anything` > `Batch_Save` |
| Iterator | `ComfyUI_Image_Anything` > `Iterator` |
| Text | `ComfyUI_Image_Anything` > `Text` |

## 출력 구조

각 일괄 실행은 체계적인 타임스탬프 폴더를 생성합니다:
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

## 지원되는 이미지 포맷

PNG, JPG, JPEG, BMP, WebP, TIFF, TIF, GIF

## 기여

기여를 환영합니다! 자유롭게 이슈를 열거나 풀 리퀘스트를 제출해 주세요.

## 라이선스

[MIT](LICENSE)

> 이 번역은 기계 번역을 기반으로 합니다. 개선을 위한 기여를 환영합니다.
