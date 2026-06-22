# Xiaomi MiMo Provider Quirks

## Critical: reasoning_content in Multi-Turn Conversations

Xiaomi MiMo models (mimo-v2.5, mimo-v2.5-pro, mimo-v2-pro, mimo-v2-omni, mimo-v2-flash) require `reasoning_content` to be passed back in multi-turn conversations when thinking mode is enabled.

### The Problem

When using MiMo models in thinking mode:
1. Each assistant message contains a `reasoning_content` field alongside `content`
2. In subsequent requests, ALL historical `reasoning_content` must be included in the messages array
3. Missing `reasoning_content` causes **HTTP 400: Param Incorrect** with message: `text is not set`

### Error Symptoms

```
BadRequestError [HTTP 400]
Provider: xiaomi  Model: mimo-v2.5
Endpoint: https://api.xiaomimimo.com/v1
Error: HTTP 400: Param Incorrect
Details: {'code': '400', 'message': 'Param Incorrect', 'param': '`text` is not set', 'type': ''}
```

### Correct Message Format

When passing back assistant messages with reasoning_content:

```json
{
    "role": "assistant",
    "content": "Hello! I am MiMo.",
    "reasoning_content": "Okay, the user just asked me to introduce myself..."
}
```

### Affected Models

- mimo-v2.5-pro
- mimo-v2.5
- mimo-v2-pro
- mimo-v2-omni
- mimo-v2-flash

### Reference

Official documentation: https://platform.xiaomimimo.com/static/docs/usage-guide/passing-back-reasoning_content.md

### Workaround

If Hermes doesn't properly handle reasoning_content passthrough:
1. Try a different model (mimo-v2.5-pro or mimo-v2-flash)
2. Check for Hermes updates that add MiMo-specific handling
3. Consider using OpenRouter or another provider as fallback

---

## Vision / Image Content in Tool Messages (2026-06 fix)

### The Problem

When `vision_analyze` returns an image in its tool result, the image gets embedded as a list-type content in the tool message (`[{type: "text", ...}, {type: "image_url", ...}]`). When the **main model** is mimo-v2.5, the Xiaomi API rejects this format with the same `text is not set` error — even though mimo-v2.5 is listed as vision-capable in models.dev.

### Root Cause

mimo-v2.5's API does not accept list-type `content` in `role: "tool"` messages that contain `image_url` parts. The `text is not set` error is ambiguous — it fires for both missing `reasoning_content` AND for malformed tool message content.

### The Fix (source code)

Changed `_PROVIDER_VISION_MODELS["xiaomi"]` from `"mimo-v2.5"` to `"mimo-v2-omni"` in `agent/auxiliary_client.py` line 288. mimo-v2-omni handles image content correctly.

**Affected files:**
- `agent/auxiliary_client.py` — vision model mapping
- `tests/hermes_cli/test_xiaomi_provider.py` — test assertion
- `tests/agent/test_auxiliary_main_first.py` — test assertion

### How to Verify

```bash
# Test mimo-v2-omni directly with an image
export XIAOMI_API_KEY=your_key
node -e "
const https = require('https');
const fs = require('fs');
const b64 = fs.readFileSync('test.png').toString('base64');
const body = JSON.stringify({
  model: 'mimo-v2-omni',
  messages: [{role:'user', content:[
    {type:'text', text:'Describe this image.'},
    {type:'image_url', image_url:{url:'data:image/png;base64,'+b64}}
  ]}],
  max_tokens: 200
});
const req = https.request({hostname:'api.xiaomimimo.com',path:'/v1/chat/completions',method:'POST',
  headers:{'Content-Type':'application/json','Authorization':'Bearer '+process.env.XIAOMI_API_KEY}},
  res => {let d='';res.on('data',c=>d+=c);res.on('end',()=>console.log(JSON.parse(d).choices?.[0]?.message?.content))});
req.write(body);req.end();
"
```

### models.dev Data

models.dev lists mimo-v2.5 as vision-capable (`"attachment": true`, `"modalities": {"input": ["text","image","audio","video"]}`). This is technically correct (mimo-v2.5 can analyze images when sent directly), but the API rejects image content embedded in tool messages. The models.dev data doesn't distinguish between "can analyze images" and "accepts images in tool message format".

---

## API Key Format

- Pay-as-you-go: `sk-xxxxx` format, base URL: `https://api.xiaomimimo.com/v1`
- Token Plan: `tp-xxxxx` format, base URL: `https://token-plan-cn.xiaomimimo.com/v1`

**Do not mix** Token Plan keys with Pay-as-you-go endpoints or vice versa.

---

## Available Models

| Model ID | Capabilities | Context | Max Output |
|----------|--------------|---------|------------|
| mimo-v2.5-pro | Text, Deep Thinking, Streaming, Function Call, Structured Output, Web Search | 1M | 128K |
| mimo-v2.5 | Text, Full-modal Understanding, Deep Thinking, Streaming, Function Call, Structured Output, Web Search | 1M | 128K |
| mimo-v2-pro | Text, Deep Thinking, Streaming, Function Call, Structured Output, Web Search | 1M | 128K |
| mimo-v2-omni | Text, Full-modal Understanding, Deep Thinking, Streaming, Function Call, Structured Output, Web Search | 256K | 128K |
| mimo-v2-flash | Text, Deep Thinking, Streaming, Function Call, Structured Output, Web Search | 256K | 64K |

---

## Configuration

### Predefined Provider (via hermes setup)

```bash
hermes setup  # Select "Xiaomi MiMo" provider
```

### Custom Provider

```bash
hermes config set model.provider custom
hermes config set model.base_url "https://api.xiaomimimo.com/v1"
hermes config set model.api_key "sk-your-key-here"
hermes config set model.default mimo-v2.5-pro
```

### Environment Variables

```
XIAOMI_API_KEY=sk-xxxxx
XIAOMI_BASE_URL=https://api.xiaomimimo.com/v1
```
