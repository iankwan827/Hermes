---
name: douyin-download
description: |
  抖音视频下载。通过yt-dlp下载抖音视频，支持短链接和长链接。
  触发方式：「下载抖音」「下载这个视频」「帮我下这个抖音链接」
  Download Douyin videos via yt-dlp. Supports short links (v.douyin.com) and full URLs.
version: 1.0.0
created: 2026-06-20
platforms: [windows]
---

# 抖音视频下载 Skill

## 核心命令

```bash
unset PYTHONHOME && D:/temp-ytdl/Scripts/python.exe -m yt_dlp "抖音链接" -o "D:/videos/%(title)s.%(ext)s"
```

## 前置条件

### yt-dlp 安装

系统Python环境可能有问题（PYTHONHOME冲突），需要创建独立venv：

```bash
# 创建独立venv
uv venv D:/temp-ytdl --python 3.12

# 安装yt-dlp
uv pip install yt-dlp --python D:/temp-ytdl/Scripts/python.exe
```

### 关键修复：unset PYTHONHOME

Windows上PYTHONHOME可能指向错误的Python路径，导致所有Python解释器都报错。
**必须在命令前加 `unset PYTHONHOME`**，否则会报 `SRE module mismatch` 错误。

## 使用方法

### 下载单个视频

```bash
unset PYTHONHOME && D:/temp-ytdl/Scripts/python.exe -m yt_dlp "https://v.douyin.com/xxxxx/" -o "D:/videos/%(title)s.%(ext)s"
```

### 支持的链接格式

- 短链接：`https://v.douyin.com/xxxxx/`
- 长链接：`https://www.douyin.com/video/1234567890`
- 分享文本中的链接（会自动提取URL）

### 输出路径

默认保存到 `D:/videos/` 目录，文件名使用视频标题。

## Pitfalls

### PYTHONHOME 冲突（2026-06-20 验证）

- 症状：`AssertionError: SRE module mismatch` 或 `cannot import name 'NamespaceLoader'`
- 原因：环境变量PYTHONHOME指向了uv安装的cpython-3.11，与系统Python冲突
- 解决：命令前加 `unset PYTHONHOME`

### 视频格式

- 默认下载最高画质
- 格式可能是bytevc1（H.266），部分播放器不支持
- 如需MP4格式，可加 `--merge-output-format mp4`

### 去水印

抖音视频本身没有水印（与TikTok不同），无需额外参数。

## 示例

用户说：「下载这个抖音 https://v.douyin.com/0LBObpBNV0I/」

执行：
```bash
mkdir -p D:/videos && unset PYTHONHOME && D:/temp-ytdl/Scripts/python.exe -m yt_dlp "https://v.douyin.com/0LBObpBNV0I/" -o "D:/videos/%(title)s.%(ext)s"
```
