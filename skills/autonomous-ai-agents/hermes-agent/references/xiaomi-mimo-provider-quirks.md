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
