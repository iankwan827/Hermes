---
name: douyin-download
description: |
  抖音视频下载+转文字稿。通过yt-dlp下载抖音视频，自动提取音频并用Whisper转录文字。
  触发方式：「下载抖音」「下载这个视频」「帮我下这个抖音链接」
  Download Douyin videos via yt-dlp, auto-transcribe to text. Supports short links and full URLs.
version: 2.0.0
created: 2026-06-20
updated: 2026-06-21
platforms: [windows]
---

# 抖音视频下载+转文字稿 Skill

## 完整工作流

### 1. 下载视频

```bash
mkdir -p D:/videos && unset PYTHONHOME && D:/temp-ytdl/Scripts/python.exe -m yt_dlp "抖音链接" -o "D:/videos/%(title)s.%(ext)s"
```

### 2. 提取音频（ffmpeg）

```bash
ffmpeg -i "D:/videos/视频文件名.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 D:/videos/temp_audio.wav -y
```

### 3. Whisper转文字稿

```bash
cd D:/videos && unset PYTHONHOME && /e/Python/python.exe -c "
import whisper
model = whisper.load_model('small')
result = model.transcribe('temp_audio.wav', language='zh')
# 输出转录结果
print(result['text'])
"
```

转录结果输出到终端，按需保存到文件。

### 4. 清理临时文件

```bash
rm -f D:/videos/temp_audio.wav
```

## 前置条件

### yt-dlp 安装（独立venv）

```bash
uv venv D:/temp-ytdl --python 3.12
uv pip install yt-dlp --python D:/temp-ytdl/Scripts/python.exe
```

### Whisper

已安装在 `/e/Python/` (Python 3.10.6 + openai-whisper)。
使用 `/e/Python/python.exe` 运行，不要用系统Python（PYTHONHOME冲突）。

### ffmpeg

已安装，路径 `/e/Users/Administrator/AppData/Local/Microsoft/WinGet/Links/ffmpeg`

## 支持的链接格式

- 短链接：`https://v.douyin.com/xxxxx/`
- 长链接：`https://www.douyin.com/video/1234567890`
- 分享文本中的链接（会自动提取URL）

## 输出

- 视频文件：`D:/videos/标题.mp4`
- 转录文字：终端输出（可保存为文件）

## Pitfalls

### PYTHONHOME 冲突（2026-06-20 验证）

- 症状：`AssertionError: SRE module mismatch` 或 `cannot import name 'NamespaceLoader'`
- 原因：环境变量PYTHONHOME指向了uv安装的cpython-3.11，与系统Python冲突
- 解决：命令前加 `unset PYTHONHOME`

### Whisper模型选择

- `base`：快但中文质量差（繁体+错字多）
- `small`：推荐，中文质量好，首次运行需下载461MB模型
- `medium`：更准但更慢，约1.5GB模型
- 首次使用某个模型会自动下载，之后缓存在 `~/.cache/whisper/`

### 视频格式

- 默认下载最高画质
- 格式可能是bytevc1（H.266），部分播放器不支持
- 如需MP4格式，可加 `--merge-output-format mp4`

### 去水印

抖音视频本身没有水印（与TikTok不同），无需额外参数。

### vision_analyze 在 Xiaomi 上的已知问题

v2.0 工作流已移除缩略图分析步骤（不再调用 vision_analyze）。如果未来需要恢复图片分析功能，注意 mimo-v2.5 的 native fast path 会把图片塞进 tool result，导致 `text is not set` 400 错误。详见 [references/vision-analyze-xiaomi-issue.md](references/vision-analyze-xiaomi-issue.md)。

## 完整示例

用户说：「下载这个抖音 https://v.douyin.com/0LBObpBNV0I/」

```bash
# 1. 下载
mkdir -p D:/videos && unset PYTHONHOME && D:/temp-ytdl/Scripts/python.exe -m yt_dlp "https://v.douyin.com/0LBObpBNV0I/" -o "D:/videos/%(title)s.%(ext)s"

# 2. 提取音频
ffmpeg -i "D:/videos/视频标题.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 D:/videos/temp_audio.wav -y

# 3. 转文字稿
cd D:/videos && unset PYTHONHOME && /e/Python/python.exe -c "
import whisper
model = whisper.load_model('small')
result = model.transcribe('temp_audio.wav', language='zh')
print(result['text'])
"

# 4. 清理
rm -f D:/videos/temp_audio.wav
```
