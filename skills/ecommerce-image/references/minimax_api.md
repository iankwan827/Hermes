# MiniMax Image Generation API Reference

## Endpoint

```
POST https://api.minimaxi.com/v1/image_generation
```

## Authentication

```
Authorization: Bearer <MINIMAX_CN_API_KEY>
```

## Request Body

```json
{
  "model": "image-01",
  "prompt": "Image description in Chinese or English",
  "aspect_ratio": "1:1",
  "response_format": "url",
  "subject_ref": {
    "image_file": {
      "file_data": "data:image/jpeg;base64,<base64_data>"
    }
  }
}
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Must be "image-01" |
| prompt | string | Yes | Text description of desired image |
| aspect_ratio | string | No | 1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16 (default: 1:1) |
| response_format | string | No | "url" or "base64" (default: "url") |
| subject_ref | object | No | Reference image for image-to-image generation |

## Subject Reference (Image-to-Image)

The `subject_ref` parameter allows generating images based on a reference image:

```json
{
  "subject_ref": {
    "image_file": {
      "file_data": "data:image/jpeg;base64,..."
    }
  }
}
```

This is useful for:
- E-commerce product images (maintain product appearance)
- Style transfer
- Product variation generation

## Response

```json
{
  "id": "request_id",
  "data": {
    "image_urls": [
      "https://hailuo-image-algeng-data.oss-cn-wulanchabu.aliyuncs.com/..."
    ]
  },
  "metadata": {
    "failed_count": "0",
    "success_count": "1"
  },
  "base_resp": {
    "status_code": 0,
    "status_msg": "success"
  }
}
```

## Important Notes

1. **Image URLs expire after 24 hours** - Download and save locally if needed
2. **Base URL**: Use `https://api.minimaxi.com` (not the `/anthropic` endpoint)
3. **API Key**: Use `MINIMAX_CN_API_KEY` from .env file
4. **SSL**: May need SSL context with `check_hostname=False` on Windows

## Example Usage (Python)

```python
import json, urllib.request, ssl, base64

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://api.minimaxi.com/v1/image_generation"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "image-01",
    "prompt": "A cute cat",
    "aspect_ratio": "1:1",
    "response_format": "url"
}

req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
    result = json.loads(resp.read())
```

## Platform-Specific Prompts

### Taobao (淘宝)
- 白底主图风格
- 突出产品
- 专业商业摄影

### JD (京东)
- 专业产品摄影
- 高清细节
- 品质感

### Pinduoduo (拼多多)
- 清晰展示
- 性价比氛围
- 促销感

### 1688
- 批发商品图
- 多角度展示
- 实惠感
