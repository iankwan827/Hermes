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

## ⚡ 首选方案：OpenCLI 浏览器桥（推荐）

**OpenCLI Browser Bridge 是抖音下载的首选方法**，它复用本机 Chrome/Edge 的登录态，不需要导出 Cookie。

```bash
# 1. 打开视频页面
opencli browser default open "https://www.douyin.com/video/<AWEME_ID>"
sleep 4

# 2. 用 JS 提取视频直链（credentials:'include' 复用浏览器 Cookie）
opencli browser default eval "(async () => {
  const a = window.location.pathname.split('/').pop();
  const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
  const d = await r.json();
  const w = d.aweme_detail;
  if (!w) return '';
  return (w.video?.play_addr?.url_list || [])[0] || '';
})()"

# 3. 用 curl 下载（视频直链有效期约几分钟，获取后立即下载）
curl -s -o "output.mp4" -L "<video_url>" -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.douyin.com/"
```

**提取作者信息**（同一页面）：
```bash
opencli browser default eval "(async () => {
  const a = window.location.pathname.split('/').pop();
  const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
  const d = await r.json();
  const w = d.aweme_detail;
  if (!w) return JSON.stringify({error: 1});
  return JSON.stringify({nickname: w.author?.nickname, sec_uid: w.author?.sec_uid});
})()"
```

**前置条件**：Chrome/Edge 必须运行，OpenCLI Browser Extension 必须已连接（`opencli daemon status` 检查）。

## 备选方案：TikHub API下载（免Cookie）

当 OpenCLI 不可用时，可用 TikHub API 获取下载链接：

```bash
# 1. 用TikHub API获取视频下载链接（需要API Key，见 tikhub-api skill）
TIKHUB_KEY=$(cat "E:/Users/Administrator/AppData/Local/hermes/skills/research/tikhub-api/references/api_key.txt")
curl -X GET "https://api.tikhub.io/api/v1/douyin/web/fetch_video_high_quality_play_url?aweme_id=<AWEME_ID>" \
  -H "Authorization: Bearer $TIKHUB_KEY"

# 2. 从返回的 original_video_url 字段下载
curl -sk -L -o "output.mp4" "<original_video_url>" -H "User-Agent: Mozilla/5.0"
```

**优点**：不需要Cookie，不需要浏览器运行
**缺点**：每次请求消耗API额度（$0.001/次）

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

### Whisper粤语支持

Whisper的 `language='yue'`（粤语）在当前安装版本（openai-whisper via `/e/Python/`）中**不支持**，会报 `ValueError: tuple.index(x): x not in tuple`。回退方案：用 `language='zh'` 转录，输出为普通话字符，但实际语音内容仍能识别。粤语专属词汇可能转录不准，需人工校对关键台词。

### yt-dlp 需要 Cookie 才能下载抖音

yt-dlp 直接下载抖音视频会报 `Fresh cookies (not necessarily logged in) are needed`。

**⚠️ 不要花时间导出 Chrome Cookie**——DPAPI 解密在 Windows 上不可靠（v20 加密 + InvalidTag），且 `--cookies-from-browser chrome` 在 Chrome 运行时会锁文件。

**正确做法**：用 OpenCLI 浏览器桥（首选）或 TikHub API（备选），见上方「首选方案」和「备选方案」。**不要纠结 Cookie 问题**——OpenCLI 复用浏览器登录态，不需要任何 Cookie 导出。

### 视频格式

- 默认下载最高画质
- 格式可能是bytevc1（H.266），部分播放器不支持
- 如需MP4格式，可加 `--merge-output-format mp4`

### 去水印

抖音视频本身没有水印（与TikTok不同），无需额外参数。

### Whisper Cantonese limitation（2026-06-22）

Whisper的`small`/`medium`/`large`模型不支持粤语（yue）语言代码，传`language='yue'`会报`ValueError`。只能用`language='zh'`转录，输出普通话字符。对于粤语内容，转录结果需要手动校对粤语写法（如"害怕"→"驚"，"自己"→"自己"等）。建议在转录后保存文件时标注"此为普通话字符转录，实际语音为粤语"。

### vision_analyze 在 Xiaomi 上的已知问题

v2.0 工作流已移除缩略图分析步骤（不再调用 vision_analyze）。如果未来需要恢复图片分析功能，注意 mimo-v2.5 的 native fast path 会把图片塞进 tool result，导致 `text is not set` 400 错误。详见 [references/vision-analyze-xiaomi-issue.md](references/vision-analyze-xiaomi-issue.md)。

## 批量下载：从低粉爆款库提取作者 → 下载主页视频

当有一批视频链接（如低粉爆款库），想下载每个作者的全部视频时：

### 第一步：从视频列表提取作者信息

```bash
# 对每个视频打开页面，提取作者 sec_uid
opencli browser default open "https://www.douyin.com/video/<AWEME_ID>"
sleep 4
opencli browser default eval "(async () => {
  const a = window.location.pathname.split('/').pop();
  const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
  const d = await r.json();
  const w = d.aweme_detail;
  if (!w) return JSON.stringify({error:1});
  return JSON.stringify({nickname: w.author?.nickname, sec_uid: w.author?.sec_uid});
})()"
```

### 第二步：去重作者，打开主页

```bash
opencli browser default open "https://www.douyin.com/user/<SEC_UID>"
sleep 5
```

### 第三步：提取视频列表（按播放量排序）

```bash
opencli browser default eval "(() => {
  const links = Array.from(document.querySelectorAll('a[href*=\"/video/\"]'));
  const seen = new Set(); const ids = [];
  links.forEach(a => { const m = a.href.match(/\\/video\\/(\\d+)/);
    if (m && !seen.has(m[1])) { seen.add(m[1]); ids.push(m[1]); } });
  return ids.slice(0,20).join(',');
})()"
```

### 第四步：逐个下载

对每个视频ID，用上方「首选方案」提取下载链接并 curl 下载。

**已验证效果**：90条低粉爆款 → 87个唯一作者 → 5个作者下载48个视频（每个约10个）。

**⚠️ 注意**：Chrome 必须运行，OpenCLI Browser Extension 必须已连接（`opencli daemon status` 检查）。

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
