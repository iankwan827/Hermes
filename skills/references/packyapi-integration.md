# PackyAPI Integration Reference

## Overview
PackyAPI is an OpenAI-compatible API gateway supporting 56+ models including GPT, Claude, Gemini, MiniMax, MiMo.

## Endpoint
```
POST https://api.packyapi.com/v1/images/generations
```

## Authentication
```
Authorization: Bearer <PACKYAPI_KEY>
```

## Compatible Models for Image Generation
- `gpt-image-2` - OpenAI's latest image model
- `gemini-3-pro-image` - Google's professional asset production model (Nano Banana Pro)
  - Designed for complex instructions and high-fidelity text rendering
  - Part of Gemini's native image generation family

## Integration with Hermes

### Method 1: Environment Variables (Recommended)
Set in .env or via `hermes config set`:
```
OPENAI_BASE_URL=https://api.packyapi.com/v1
OPENAI_API_KEY=<packyapi_key>
```

Then use existing `image_gen/openai` plugin - no code changes needed.

### Method 2: Direct API Call
```python
import json, urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://api.packyapi.com/v1/images/generations"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "gemini-3-pro-image",
    "prompt": "产品描述",
    "n": 1,
    "size": "1024x1024"
}

req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
    result = json.loads(resp.read())
```

## Pricing
- Pay-as-you-go model
- Various discounts per model (check https://www.packyapi.com/pricing)
- `gemini-3-pro-image` pricing: check platform for current rates

## Limitations
- Parameter format may differ from MiniMax (e.g., aspect_ratio → size)
- Some models may not support all features through OpenAI-compatible endpoint
- Test thoroughly before production use

## Use Cases
- Alternative to MiniMax for ecommerce product images
- Access to multiple providers with single API key
- Gemini's text rendering quality for product labels/text
