---
name: hermes-vision-routing
description: Hermes图片路由与vision_analyze配置。处理provider特定的多模态兼容性问题。
tags: [hermes, vision, image, routing, xiaomi, provider]
triggers: [vision_analyze失败, 图片路由, image_input_mode, 多模态报错, text is not set, provider vision]
---

# Hermes Vision Routing Configuration

## Overview

Hermes has two modes for handling user-attached images:
- **native**: Image pixels attached directly to the conversation (requires main model to support vision)
- **text**: Pre-analyze with vision_analyze tool, prepend text description to message

Mode is determined by `agent.image_input_mode` in config.yaml:
- `auto` (default): Let Hermes decide based on models.dev capabilities
- `native`: Always attach pixels (only if main model supports vision)
- `text`: Always pre-analyze with vision_analyze

## Provider-Specific Quirks

### Xiaomi MiMo API

**Critical**: The xiaomi API (`api.xiaomimimo.com`) does NOT support multimodal content in tool messages (`role: tool`). Sending `image_url` parts inside a tool message's content array triggers:

```
HTTP 400: Param Incorrect — `text` is not set
```

Both `mimo-v2.5` and `mimo-v2-omni` support multimodal content in USER messages, but NOT in tool messages.

**Fix**: Set `agent.image_input_mode: text` in config.yaml:
```bash
hermes config set agent.image_input_mode text
```

This forces all images through vision_analyze pre-analysis, keeping multimodal content out of tool messages.

### Vision Model Selection (Optional)

`_PROVIDER_VISION_MODELS` in `agent/auxiliary_client.py` maps providers to their vision-specific models:
```python
_PROVIDER_VISION_MODELS = {
    "xiaomi": "mimo-v2-omni",
    "zai": "glm-5v-turbo",
}
```

**This override is NOT required for the Xiaomi fix.** Both mimo-v2.5 and mimo-v2-omni handle multimodal user messages correctly (verified 2026-06-22). The only required fix is `image_input_mode: text`. The `_PROVIDER_VISION_MODELS` override is optional — it lets you pin a specific vision model if needed, but leaving it unset is fine.

When `agent.image_input_mode: text`, images are pre-analyzed with the vision model, and only the text description enters the conversation.

## Debugging Path

When vision_analyze or image routing fails:

1. **Check models.dev data**: Does the provider's model actually support vision?
   ```python
   from agent.models_dev import get_model_capabilities
   caps = get_model_capabilities("provider", "model")
   print(caps.supports_vision)  # True/False
   ```

2. **Check config overrides**: Is `model.supports_vision` or `providers.<provider>.models.<model>.supports_vision` overriding models.dev?
   ```python
   from agent.image_routing import _supports_vision_override
   override = _supports_vision_override(cfg, "provider", "model")
   ```

3. **Check vision provider resolution**: What model does `resolve_vision_provider_client` actually return?
   ```python
   from agent.auxiliary_client import resolve_vision_provider_client
   provider, client, model = resolve_vision_provider_client(
       provider=None, model=None, async_mode=False)
   print(f"provider={provider}, model={model}, client={type(client).__name__}")
   ```

4. **Test API directly**: Send a minimal multimodal request to the provider's API to isolate format issues.

5. **Check message roles**: If the error is "text is not set", test with tool-role messages specifically — the issue is often that the provider doesn't support multimodal content in non-user roles.

## Config Reference

```yaml
agent:
  image_input_mode: text  # Force text mode for xiaomi compatibility
  
auxiliary:
  vision:
    provider: auto  # Auto-detect vision provider
    model: ''       # Use provider default (mimo-v2-omni for xiaomi)
    timeout: 120
```

## Key Files

- `agent/auxiliary_client.py` — `_PROVIDER_VISION_MODELS`, `resolve_vision_provider_client`, `async_call_llm`
- `agent/image_routing.py` — `decide_image_input_mode`, `_lookup_supports_vision`, `_supports_vision_override`
- `tools/vision_tools.py` — `vision_analyze_tool` implementation
- `gateway/run.py` — `_decide_image_input_mode`, `_enrich_message_with_vision`
