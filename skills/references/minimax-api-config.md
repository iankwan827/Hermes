# MiniMax Image Generation API Configuration

## Endpoint
```
POST https://api.minimaxi.com/v1/image_generation
```

## Authentication
```
Authorization: Bearer {MINIMAX_CN_API_KEY}
```

## Key Configuration Pitfall

The .env file has:
```
MINIMAX_CN_BASE_URL=https://api.minimaxi.com/anthropic
```

But the image generation endpoint does NOT use the `/anthropic` suffix. When building the URL:
1. Read MINIMAX_CN_BASE_URL from .env
2. Strip `/anthropic` suffix if present
3. Append `/v1/image_generation`

Correct URL: `https://api.minimaxi.com/v1/image_generation`
Wrong URL: `https://api.minimaxi.com/anthropic/v1/image_generation` (404 error)

## SSL on Windows

Windows may have SSL issues with the MiniMax API. Solution:
```python
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urllib.request.urlopen(req, timeout=120, context=ctx)
```

## Image-to-Image (subject_ref)

MiniMax supports generating images based on a reference image:

```json
{
  "model": "image-01",
  "prompt": "描述文字",
  "aspect_ratio": "1:1",
  "response_format": "url",
  "subject_ref": {
    "image_file": {
      "file_data": "data:image/jpeg;base64,{base64_data}"
    }
  }
}
```

## Supported Aspect Ratios
- 1:1 (square)
- 16:9 (landscape)
- 4:3, 3:2, 2:3, 3:4
- 9:16 (portrait)

## Response Format
```json
{
  "id": "...",
  "data": {
    "image_urls": ["https://..."]
  },
  "base_resp": {
    "status_code": 0,
    "status_msg": "success"
  }
}
```

## Plugin Configuration

Plugin location: `~/.hermes/hermes-agent/plugins/image_gen/minimax/`

Required files:
- `__init__.py` - Provider implementation
- `plugin.yaml` - Plugin metadata

Enable with: `hermes plugins enable image_gen/minimax`
Config: `hermes config set image_gen.provider minimax`
