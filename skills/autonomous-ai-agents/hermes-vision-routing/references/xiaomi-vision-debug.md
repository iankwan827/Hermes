# Xiaomi MiMo Vision Routing — Debugging Session (2026-06-22)

## Problem

vision_analyze tool failed with:
```
HTTP 400: Param Incorrect — `text` is not set
Provider: xiaomi  Model: mimo-v2.5
Endpoint: https://api.xiaomimimo.com/v1
```

## Root Cause

The xiaomi API does NOT accept multimodal content (image_url parts) in tool-role messages. When Hermes routes images in "native" mode, the image is attached as a tool message with multimodal content. The xiaomi API rejects this format.

**Verification** (direct API test):
```python
# This FAILS with "text is not set":
requests.post(f'{base_url}/chat/completions', json={
    'model': 'mimo-v2.5',
    'messages': [
        {'role': 'system', 'content': 'You are a helpful assistant'},
        {'role': 'user', 'content': 'Look at this screenshot'},
        {'role': 'assistant', 'content': None, 'tool_calls': [...]},
        {'role': 'tool', 'tool_call_id': 'call_1', 'content': [
            {'type': 'text', 'text': 'Here is the screenshot'},
            {'type': 'image_url', 'image_url': {'url': data_url}}
        ]},
        {'role': 'user', 'content': 'What do you see?'}
    ]
})

# This WORKS (image in user message):
requests.post(f'{base_url}/chat/completions', json={
    'model': 'mimo-v2.5',
    'messages': [{'role': 'user', 'content': [
        {'type': 'text', 'text': 'What color is this?'},
        {'type': 'image_url', 'image_url': {'url': data_url}}
    ]}]
})
```

Both mimo-v2.5 and mimo-v2-omni support multimodal in USER messages, but NOT in TOOL messages.

## Fix Applied

1. **Config** (required): `agent.image_input_mode: text` — forces all images through vision_analyze pre-analysis
2. **Code** (optional): `_PROVIDER_VISION_MODELS["xiaomi"] = "mimo-v2-omni"` — pins vision_analyze to omni model. NOT required — mimo-v2.5 works fine for user-role multimodal too. Only needed if you want to explicitly pin a vision model.

## Debugging Steps That Worked

1. Read request dump from `E:\Users\Administrator\AppData\Local\hermes\sessions\request_dump_*.json`
2. Checked message 17 had `role=tool` with multimodal content → API rejects this
3. Direct API test confirmed both models work with USER-role multimodal, but not TOOL-role
4. `resolve_vision_provider_client` returned (None, None, None) when `model.supports_vision: false` was set (too broad — blocks all vision)

## Pitfall

Do NOT use `model.supports_vision: false` as a fix — it blocks vision support for ALL models including mimo-v2-omni. Use `agent.image_input_mode: text` instead, which only changes the routing mode without disabling vision capabilities.

## models.dev Data

```
mimo-v2.5: attachment=True, modalities.input=['text','image','audio','video']
mimo-v2-omni: attachment=True, modalities.input=['text','image','audio','video','pdf']
```

models.dev says both support vision, which is correct for USER messages. The issue is specifically TOOL messages.
