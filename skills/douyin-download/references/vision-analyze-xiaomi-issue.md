# vision_analyze 在 Xiaomi mimo-v2.5 上的问题

## 根因（2026-06-21 分析）

mimo-v2.5 **支持** vision（能在 user message 里看图），但 **不支持** tool result 里带图片。

Hermes 的 `_should_use_native_vision_fast_path()` 判断逻辑：
```python
return (
    _supports_media_in_tool_results(provider, model)   # xiaomi → False ✓
    or _lookup_supports_vision(provider, model, cfg) is True  # xiaomi → True (models.dev)
)
```
`or` 条件导致走 native fast path → 图片被塞进 tool result → Xiaomi API 返回 400 `text is not set`。

## 错误信息
```
Error code: 400 - {'error': {'code': '400', 'message': 'Param Incorrect', 'param': '`text` is not set', 'type': ''}}
Provider: xiaomi  Model: mimo-v2.5
Endpoint: https://api.xiaomimimo.com/v1
```

## 绕过方案

1. 在 config.yaml 配置 `auxiliary.vision.provider` 和 `auxiliary.vision.model` 指定专用 vision 模型（如 OpenRouter Gemini），避免走 native fast path
2. 不用 vision_analyze，改用本地工具（如 Whisper 转录、或 Python 脚本直接调用 Xiaomi Vision API）

## 相关代码位置

- `_should_use_native_vision_fast_path()`: `tools/vision_tools.py:479`
- `_supports_media_in_tool_results()`: `tools/vision_tools.py:419`（xiaomi 不在已知支持列表里，返回 False 是对的）
- `_lookup_supports_vision()`: `agent/image_routing.py:260`（从 models.dev 查，mimo-v2.5 标记 supports_vision=True）
- `_PROVIDER_VISION_MODELS`: `agent/auxiliary_client.py:287`（"xiaomi": "mimo-v2.5"）

## 时间线

- 2026-05-30 首次出现此错误（token-plan-cn.xiaomimimo.com）
- 2026-06-09 曾修复可用（可能当时走 legacy path）
- 2026-06-16/19/20 vision_analyze 成功（走 native fast path，但当时可能主模型不同）
- 2026-06-21 再次报错（mimo-v2.5 作为主模型时 native fast path 触发）
