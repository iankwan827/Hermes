# MiniMax Image Generation API Reference

## Endpoint

```
POST https://api.minimaxi.com/v1/image_generation
```

## Authentication

```
Authorization: Bearer <MINIMAX_CN_API_KEY>
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | "image-01" or "image-01-live" |
| prompt | string | Yes | Text description, max 1500 chars |
| aspect_ratio | string | No | 1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9 |
| response_format | string | No | "url" (default) or "base64" |
| width/height | int | No | [512,2048], divisible by 8. aspect_ratio takes priority |
| seed | int | No | For reproducibility |
| n | int | No | 1-9 images per request |
| prompt_optimizer | bool | No | Auto-optimize prompt (default false) |
| subject_reference | array | No | Image-to-image reference (see limitations below) |

## Subject Reference (图生图)

```json
{
  "subject_reference": [
    {
      "type": "character",
      "image_file": "data:image/jpeg;base64,..."
    }
  ]
}
```

**Critical limitations:**
- `type` only supports `"character"` (portrait) — NOT products
- Designed for face/identity consistency, not general object preservation
- Products WILL be deformed — never use for e-commerce final deliverables
- Multiple reference images may be supported (check docs for latest)

## What MiniMax Does NOT Support

| Feature | Status | Workaround |
|---------|--------|------------|
| **Inpainting / 局部重绘** | ❌ Not available | Use cutout+composite workflow |
| **Mask-based editing** | ❌ Not available | Generate clean background, composite product |
| **Product subject_ref** | ❌ Deforms product | Use rembg cutout + PIL composite |
| **Background removal** | ❌ Not built-in | Use rembg (separate tool) |

## Response

```json
{
  "id": "request_id",
  "data": {
    "image_urls": ["https://..."]
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

1. Image URLs expire after 24 hours — download locally
2. Base URL: `https://api.minimaxi.com` (NOT the `/anthropic` endpoint)
3. SSL: May need `check_hostname=False` on Windows
4. Prompt language: Chinese or English both work

## Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1002 | Rate limit |
| 1004 | Auth failed |
| 1008 | Insufficient balance |
| 1026 | Sensitive content |
| 2013 | Invalid parameters |
| 2049 | Invalid API key |
