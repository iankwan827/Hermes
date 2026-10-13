# PackyAPI Gemini 集成指南

## 概述

PackyAPI 是 OpenAI 兼容的 API 聚合平台，支持 Gemini 图生图模型。
可用于替代 MiniMax 进行电商产品图生成。

## 配置

### 环境变量（.env）
```
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://www.packyapi.com/v1
```

### 可用模型
- `gemini-3-pro-image-preview` — 高质量，文字渲染好
- `gemini-2.5-flash-image` — 快速，大批量

## API 端点

### 图生图（换背景）
```
POST https://www.packyapi.com/v1beta/models/{model}:generateContent
```

请求格式：
```json
{
  "contents": [{
    "parts": [
      {"text": "Keep the product exactly as it is, only change the background to <背景描述>. Do not modify the product at all."},
      {"inlineData": {"mimeType": "image/png", "data": "<base64原图>"}}
    ]
  }],
  "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}
```

认证：
```
x-goog-api-key: <OPENAI_API_KEY>
```

### 图片识别
同一个端点，responseModalities 设为 `["TEXT"]`：
```json
{
  "contents": [{"parts": [
    {"text": "请详细描述这张图片中的产品"},
    {"inlineData": {"mimeType": "image/png", "data": "<base64图片>"}}
  ]}],
  "generationConfig": {"responseModalities": ["TEXT"]}
}
```

## Python 示例

```python
import requests, json, os, base64, urllib3
urllib3.disable_warnings()

api_key = os.environ.get('OPENAI_API_KEY', '')
url = "https://www.packyapi.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

# 读原图
with open('product.png', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "contents": [{"parts": [
        {"text": "Keep the product exactly as it is, only change the background to warm Chinese calligraphy studio"},
        {"inlineData": {"mimeType": "image/png", "data": img_b64}}
    ]}],
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

## 与 MiniMax 对比

| 特性 | MiniMax | Gemini (PackyAPI) |
|------|---------|-------------------|
| 主体一致性 | ❌ 会变形 | ✅ 100%不变 |
| 文字渲染 | 一般 | 高质量 |
| 价格 | 较低 | 中等 |
| 生图质量 | 高 | 高 |
| 图生图 | subject_ref（不可靠） | 原生支持 |

## 注意事项

- SSL 问题：Clash fake IP 模式可能拦截，需配置直连规则
- base URL 必须用 `www.packyapi.com` 不是 `api.packyapi.com`
- 认证用 `x-goog-api-key` header 不是 `Authorization: Bearer`
