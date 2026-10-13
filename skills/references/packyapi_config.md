# PackyAPI 配置指南

## 环境变量（.env）

```
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://www.packyapi.com/v1
```

## ⚠️ 关键注意事项

1. **Base URL 是 `www.packyapi.com`**，不是 `api.packyapi.com`
2. **Gemini 端点格式不同**：`/v1beta/models/{model}:generateContent`
3. **认证用 `x-goog-api-key` header**，不是 `Authorization: Bearer`
4. **Clash fake IP 会导致 SSL 失败** — 需要关掉 fake IP 或加直连规则

## Gemini 生图（图片生成）

```python
import requests, json, base64, os, ssl, urllib3
urllib3.disable_warnings()

api_key = os.environ['OPENAI_API_KEY']
url = "https://www.packyapi.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

payload = {
    "contents": [{"parts": [{"text": "Generate: <prompt>"}]}],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}

r = requests.post(url, json=payload,
    headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    verify=False, timeout=120)

result = r.json()
for c in result.get("candidates", []):
    for p in c.get("content", {}).get("parts", []):
        if "inlineData" in p:
            img_bytes = base64.b64decode(p["inlineData"]["data"])
            with open("output.png", "wb") as f:
                f.write(img_bytes)
```

## Gemini 图生图（换背景，主体不变）

```python
# 读取原图
with open("product.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "contents": [{"parts": [
        {"text": "Keep the product exactly as is, only change background to <描述>"},
        {"inlineData": {"mimeType": "image/png", "data": img_b64}}
    ]}],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}
# 同上请求
```

## Gemini 识图（图片分析）

```python
with open("image.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "contents": [{"parts": [
        {"text": "描述这张图片的内容"},
        {"inlineData": {"mimeType": "image/png", "data": img_b64}}
    ]}],
    "generationConfig": {"responseModalities": ["TEXT"]}
}
# 只返回文字，不生成图片
```

## 可用模型

| 模型 | 用途 | 特点 |
|------|------|------|
| gemini-3-pro-image-preview | 生图/识图 | 高质量，文字渲染好 |
| gemini-2.5-flash-image | 生图/识图 | 快速，便宜 |

## OpenAI 格式（不支持 Gemini 生图）

`/v1/images/generations` 端点**不支持** Gemini 模型，会报 `not supported model for image generation`。必须用 Gemini 原生端点。
