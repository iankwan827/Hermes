# Ollama Gemma4 音频转录

## 关键发现

Gemma4 有 audio capability，但 Ollama API **没有 audio 参数**。
音频需要通过 `images` 参数传入（base64 编码）。

## 正确用法

```python
import requests, base64

# 1. 转换为 16kHz mono WAV
# ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav

# 2. 读取并 base64 编码
with open('audio.wav', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

# 3. 调用 API（关键：用 images 参数，不是 audio）
response = requests.post('http://localhost:11434/api/chat', json={
    "model": "gemma4:e4b-it-q4_K_M",
    "messages": [
        {"role": "system", "content": "你是一个语音转文字助手。请直接转录音频内容，不要添加任何解释。"},
        {"role": "user", "content": "转录：", "images": [audio_b64]}
    ],
    "stream": False,
    "think": False,  # 必须设为 False，否则 thinking 模式会干扰
    "options": {"temperature": 0.1, "num_predict": 1024}
})
```

## 注意事项

1. **音频格式**：必须是 16kHz mono WAV，其他格式可能识别失败
2. **think: false**：必须关闭 thinking 模式（v0.20.x+ 有回归 bug）
3. **转录质量**：不如 Whisper，适合快速预览，不适合精确转录
4. **API 端点**：`/api/chat` 不是 `/api/generate`
5. **images 参数**：虽然叫 images，但可以传音频

## 与 Whisper 对比

| 特性 | Gemma4 | Whisper |
|------|--------|---------|
| 精度 | 中 | 高 |
| 速度 | 快 | 中 |
| 时间戳 | 无 | 有 |
| 适用 | 快速预览 | 正式转录 |
