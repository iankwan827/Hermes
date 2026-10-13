# mimo-v2.5 Multimodal Tool Result 不支持问题

## 发现时间
2026-07-14（首次发现），2026-07-14 深入代码定位根因

## 问题
mimo-v2.5 通过 xiaomi API 不支持在 tool result 中携带图片（multimodal tool results）。

## 影响
- vision_analyze 的原生快速路径返回 "Image attached natively" 但模型实际看不到图片
- 飞书发图、browser_vision 截屏不受影响（图片在 user message 里）

## 代码级根因

### ProviderProfile 配置
文件：`plugins/model-providers/xiaomi/__init__.py`
```python
xiaomi = ProviderProfile(
    name="xiaomi",
    supports_vision=True,              # ✅ user message 里能看图片
    supports_vision_tool_messages=False, # ❌ tool result 里不能看图片
)
```

### Hermes 代码 bug
文件：`tools/vision_tools.py` 第586-595行
```python
def _supports_media_in_tool_results(provider: str, model: str) -> bool:
    # ...
    try:
        from providers import get_provider_profile
        profile = get_provider_profile(p)
        if profile is not None and profile.supports_vision:  # ← BUG: 检查的是 supports_vision
            return True                                       #   应该检查 supports_vision_tool_messages
    except Exception:
        pass
    return False
```

**函数名叫 `_supports_media_in_tool_results`（检查 tool result 里能不能放图片），但检查的是 `supports_vision`（用户消息里能不能看图片），而不是 `supports_vision_tool_messages`（tool result 里能不能看图片）。**

### 因果链
1. `_supports_media_in_tool_results("xiaomi", "mimo-v2.5")` → 检查 `profile.supports_vision` → True
2. `_should_use_native_vision_fast_path()` → True（因为 `_supports_media_in_tool_results` 返回 True）
3. `_vision_analyze_native()` → 图片放在 tool result 的 multimodal envelope 里
4. mimo-v2.5 看不到 tool result 里的图片 → 返回 "Image attached natively" 但实际没内容

### 为什么飞书发图能用
飞书平台集成把图片挂在 **user message** 的 content 里（不是 tool result），mimo-v2.5 的 `supports_vision=True` 覆盖了这个场景。

### browser_vision 为什么能用
截屏图片也挂在 context 里，不是在 tool result 的 multimodal envelope 里。

### 为什么修配置"有效"
- 修复前：auxiliary.vision provider=auto → `_explicit_aux_vision_override` 返回 False → native 路径 → ❌
- 修复后：auxiliary.vision provider=xiaomi → 返回 True → text 路径 → ✅
- **不是修了配置，是换了路由路径绕开了 bug**

### 路由决策代码
文件：`agent/image_routing.py` 第264-346行
- `_explicit_aux_vision_override`：provider 不是 auto/空 → 返回 True → 强制 "text" 路径
- `decide_image_input_mode`：auto 模式下先检查 `_explicit_aux_vision_override`，再检查 `_lookup_supports_vision`

## Workaround
1. 设置 auxiliary.vision 配置改变路由（推荐）
2. 直接调用小米 API（最可靠，完全绕开 vision_analyze 工具）

## 状态
Hermes 上游 bug：`_supports_media_in_tool_results` 应该检查 `supports_vision_tool_messages` 而不是 `supports_vision`。
