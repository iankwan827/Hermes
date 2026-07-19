# Session 跨 session 延续 - 改动记录

## 日期：2026-07-19

## 问题
Hermes session 之间没有共享记忆。session 超时或 restart 后，新 session 无法知道上一次做了什么。

---

## 改动 1：gateway/run.py（Hermes 源代码）

### 新增方法：`_auto_save_session`

位置：`gateway/run.py` 第 4275 行左右

```python
def _auto_save_session(self, agent) -> None:
    """保存agent的对话到last_session.json，供新session读取恢复上下文"""
    try:
        _msgs = getattr(agent, '_session_messages', None) or []
        if _msgs:
            import json as _json
            from pathlib import Path as _Path
            from hermes_constants import get_hermes_home as _gkh
            _save_dir = _gkh() / "last_session_context"
            _save_dir.mkdir(exist_ok=True)
            _save_file = _save_dir / "last_session.json"
            _clean = [m for m in _msgs if m.get("role") in ("user", "assistant") and m.get("content")]
            _clean = _clean[-100:]
            with open(_save_file, "w", encoding="utf-8") as _f:
                _json.dump(_clean, _f, ensure_ascii=False, indent=1)
            logger.info("Session context saved: %d messages -> %s", len(_clean), _save_file)
    except Exception as _save_err:
        logger.debug("Failed to save session context: %s", _save_err)
```

### 调用点 1：`_finalize_shutdown_agents` 方法

位置：`_finalize_shutdown_agents` 方法内，cleanup 前

```python
def _finalize_shutdown_agents(self, active_agents: Dict[str, Any]) -> None:
    for agent in active_agents.values():
        try:
            # === AUTO-SAVE: 保存shutdown时的对话 ===
            self._auto_save_session(agent)
            # === END AUTO-SAVE ===
            from hermes_cli.plugins import invoke_hook as _invoke_hook
            _invoke_hook(
                "on_session_finalize",
                session_id=getattr(agent, "session_id", None),
                platform="gateway",
                reason="shutdown",
            )
        except Exception:
            pass
        self._cleanup_agent_resources(agent)
```

### 调用点 2：`_stop_impl` 方法（idle agent 清理）

位置：`_stop_impl` 方法内，idle cache 清理循环

```python
for _entry in _idle_agents:
    _agent = (
        _entry[0] if isinstance(_entry, tuple) else _entry
    )
    # === AUTO-SAVE: 保存idle agent的对话 ===
    self._auto_save_session(_agent)
    # === END AUTO-SAVE ===
    self._cleanup_agent_resources(_agent)
```

### 调用点 3：`_session_expiry_watcher` 方法

位置：`_session_expiry_watcher` 方法内，清理 agent 前

```python
if _cached_agent and _cached_agent is not _AGENT_PENDING_SENTINEL:
    # === AUTO-SAVE: 保存超时session的对话 ===
    self._auto_save_session(_cached_agent)
    # === END AUTO-SAVE ===
    self._cleanup_agent_resources(_cached_agent)
```

---

## 改动 2：MEMORY 文件系统（不改代码）

### 新建目录：`~/.hermes/memory/`

| 文件 | 内容 |
|------|------|
| `01_douyin_platform.json` | 抖音/平台/小红书/热搜/发布时间 |
| `02_bazi.json` | 八字/排盘/Web系统/课程/过三关/女命/墓库 |
| `03_content_workflow.json` | 文案工作流/栋笃笑/阿强/开头技巧/审核/粤语/电商图 |
| `04_tools_config.json` | Vercel/GitHub/skill创建/素材保存/配置修改/错误诊断 |
| `05_user_profile.json` | 用户信息/风格/标准 |

### MEMORY 索引（system prompt 注入）

```
【MEMORY文件系统】详细记忆存~/.hermes/memory/，按主题分文件：
01_douyin_platform.json（抖音/平台/小红书/热搜/发布时间）、
02_bazi.json（八字/排盘/Web系统/课程/过三关/女命/墓库）、
03_content_workflow.json（文案工作流/栋笃笑/阿强/开头技巧/审核/粤语/电商图）、
04_tools_config.json（Vercel/GitHub/skill创建/素材保存/配置修改/错误诊断）、
05_user_profile.json（用户信息/风格/标准）。需要详情时read_file对应JSON。

【跨session延续】新session开始时，读取~/.hermes/last_session_context/last_session.json，
里面有上一次session超时前自动保存的完整对话（最后100条user/assistant消息）。
```

---

## 保存位置

- **对话保存：** `~/.hermes/last_session_context/last_session.json`
- **格式：** JSON 数组，每个元素是 `{"role": "user/assistant", "content": "..."}`
- **数量：** 最后 100 条 user/assistant 消息

---

## 使用方式

1. session 超时或 restart 时自动保存对话
2. 新 session 启动时，MEMORY 指示 agent 读取 `last_session.json`
3. agent 恢复上次对话上下文

## 注意

- `hermes update` 会覆盖 `gateway/run.py` 的改动
- 需要 `hermes gateway restart` 才能生效
