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
export XIAOMI_API_KEY=sk-xxx && node -e "
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

## API Key — .env vs auth.json (Critical Distinction)

The `XIAOMI_API_KEY` lives in `~/.hermes/.env` as an environment variable source, but **Hermes's runtime credential state** lives in `~/.hermes/auth.json` under `credential_pool.xiaomi`. These are two different layers.

### auth.json credential states

Each credential has a `last_status` field:

| Status | Meaning |
|--------|---------|
| `ok` | Key is healthy |
| `exhausted` | Key is rate-limited or depleted (欠费/额度用尽) |
| `error` | Transient error (401/429/503) — auto-retried |

**Exhaustion causes:**
- `402` — Insufficient account balance (欠费)
- `401` — Invalid API key format or revoked key

**Key fact:** After paying outstanding balance, the key itself becomes valid again, but `auth.json` still shows `exhausted` and Hermes will refuse to use it. The exhaustion flag must be **manually reset**.

### Resetting exhaustion in auth.json

**Option 1 — Via Hermes CLI (if available):**
```bash
hermes auth reset xiaomi
```

**Option 2 — Manual edit (when CLI reset is unavailable):**

Read `~/.hermes/auth.json`, find the Xiaomi credential entry, and reset these fields:
```json
"last_status": "ok",
"last_error_code": null,
"last_error_reason": null,
"last_error_message": null,
"last_error_reset_at": null
```

Also remove any stale `manual` source entries (secondary keys added manually that are invalid — these show as `api-key-2` etc. with `401` errors and should be deleted from the pool).

### Pitfall: Multiple credentials in the pool — read the error carefully

`auth.json` can contain **multiple** Xiaomi credentials (e.g. `env:XIAOMI_API_KEY` + a manually added `api-key-2`). They may show different error codes:
- `402` on env key = 欠费 (key is valid, just no balance)
- `401` on manual key = invalid key (wrong key entirely)

**Always check which credential produced the error.** The error message includes the model name — if it says `mimo-v2.5` it's the real key; if it says a different model it might be a fallback key. Don't assume the error came from the env key without checking.

When resetting: remove invalid manual entries AND reset the env key's exhaustion status.

### Distinguishing a literal "***" key from a masked real key

Both `.env` display and `grep` output show `XIAOMI_API_KEY=***` for both cases. Distinguish by reading raw bytes:

```bash
grep -n "XIAOMI" ~/.hermes/.env
```

- **Literal placeholder**: line shows `XIAOMI_API_KEY=***` with no hidden characters (the actual value is three ASCII asterisk characters)
- **Masked real key**: identical in grep output — must check line count

If the same key appears twice (once commented `#XIAOMI_API_KEY=***`, once uncommented as `XIAOMI_API_KEY=***`), the uncommented literal wins at runtime. A literal `***` in `.env` means the key is **empty** — Hermes will have no valid key.

Fix: obtain a fresh key from https://platform.xiaomimimo.com and set it with:
```bash
hermes config set secrets.xiaomi.api_key <your-key>
```

## Gateway Restart After auth.json Changes

`auth.json` changes require a **gateway restart** to take effect. The correct sequence:

```bash
# Stop gateway (this drains cleanly)
cd ~/.hermes/hermes-agent
PYTHONHOME="" ./venv/Scripts/python.exe hermes_cli/main.py gateway stop

# Wait for exit, then start fresh
./venv/Scripts/python.exe hermes_cli/main.py gateway run
```

Do NOT use `--replace` flag if the old PID won't die cleanly. If `--replace` fails with "Permission denied killing PID", manually kill the stale process then `gateway run` normally. Verify with `tail -5 ~/.hermes/logs/gateway.log` (check timestamps match current time).

### Mac: use `hermes gateway restart`

On Mac, the simplest restart is just:
```bash
hermes gateway restart
```
No need to specify `bash` or `zsh` — the hermes command works regardless of shell.

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
