---
name: hermes-source-mods
description: "修改 Hermes 源码添加功能。定位关键文件、理解 hook 系统、修改核心逻辑。用于 MEMORY/插件/skill 都解决不了的场景。"
tags: [hermes, development, source-code, customization]
---

# Hermes 源码修改指南

当插件/MEMORY/skill 都不够用时，直接改源码。

## 关键文件速查

| 功能 | 文件路径 |
|------|----------|
| Session 超时/重置 | `gateway/run.py` → `_session_expiry_watcher()` (line ~5628) |
| Session 管理 | `gateway/session.py` → `_is_session_expired()`, `_should_reset()` |
| 插件系统 | `hermes_cli/plugins.py` → `VALID_HOOKS`, `invoke_hook()` |
| Agent 核心循环 | `run_agent.py` → `class AIAgent` (line 320) |
| 消息持久化 | `run_agent.py` → `_persist_session()`, `_session_messages` |
| Session DB | `hermes_state.py` → `SessionDB`, `state.db` |
| 工具注册 | `tools/registry.py` |
| 工具集定义 | `toolsets.py` |
| CLI 命令 | `hermes_cli/commands.py` |

## 项目布局

```
~/.hermes/hermes-agent/
├── run_agent.py          # AIAgent 核心循环
├── gateway/run.py        # Gateway 主逻辑（session 管理、插件调用）
├── gateway/session.py    # Session 状态、超时策略
├── hermes_cli/plugins.py # 插件系统、VALID_HOOKS
├── hermes_state.py       # SQLite session store
├── tools/                # 每个工具一个文件
├── plugins/              # 内置插件
└── toolsets.py           # 工具集定义
```

## Session 生命周期（gateway 环境）

1. 用户发消息 → gateway 分配/复用 session
2. 每 5 分钟 `_session_expiry_watcher()` 检查超时
3. 超时判断：`_is_session_expired()` 检查 idle/daily 策略
4. 超时清理顺序：
   - `invoke_hook("on_session_finalize", ...)` — hook 还能访问 agent
   - `_cleanup_agent_resources(agent)` — 清理工具资源
   - `_evict_cached_agent(key)` — 从缓存移除
   - `entry.expiry_finalized = True` — 标记完成
5. **关键：hook 在 agent 清理之前触发，此时 `_session_messages` 还在**

## 已实现：自动保存 session 对话（跨 session 延续）

### 双层保存架构

**问题：** CLI 进程（`hermes gateway restart`）和 Gateway 进程是两个独立进程。CLI 杀 Gateway 时，Gateway 的 graceful shutdown 可能来不及执行。

**解决方案：两层都保存**

#### 层 1：Gateway 内部（agent 级别）
代码位置：`gateway/run.py` — `_auto_save_session()` helper 方法

四个触发点：
1. **session 超时** — `_session_expiry_watcher()` 里，agent 清理前调用
2. **restart 时活跃 agent** — `_finalize_shutdown_agents()` 里
3. **restart 时 idle agent** — idle cache 清理循环里
4. **`/new` 或 `/reset`** — `_handle_reset_command()` 里（`slash_commands.py`）

#### 层 2：CLI 层面（进程级别）— 关键！
代码位置：`hermes_cli/gateway.py`

在 `gateway stop` 和 `gateway restart` 的 handler 开头，**直接从 state.db 读取**，不依赖 Gateway 进程：

```python
# === AUTO-SAVE: 在重启前保存当前session对话 ===
import sqlite3
from hermes_constants import get_hermes_home
_db_path = get_hermes_home() / "profiles" / "main" / "state.db"
_conn = sqlite3.connect(str(_db_path))
_cur = _conn.cursor()
# 找最近的 feishu session
_cur.execute("SELECT id FROM sessions WHERE source='feishu' ORDER BY started_at DESC LIMIT 1")
_row = _cur.fetchone()
if _row:
    _sid = _row[0]
    _cur.execute("SELECT role, content FROM messages WHERE session_id=? AND role IN ('user','assistant') AND content IS NOT NULL AND content != '' ORDER BY timestamp", (_sid,))
    _msgs = [{"role": r, "content": c} for r, c in _cur.fetchall()][-100:]
    # 保存到 ~/.hermes/last_session_context/last_session.json
```

**为什么需要两层：**
- Gateway 层：在 agent 还活着时保存（最完整）
- CLI 层：在杀进程前从数据库读（兜底，不依赖 graceful shutdown）

### 完整流程

#### `hermes gateway restart`（从终端执行）
```
终端执行 hermes gateway restart
  → gateway_command() (gateway.py:6334)
    → _gateway_command_inner() (gateway.py:6470)
      → subcmd == "restart" (gateway.py:6784)
        → 【CLI层保存】从 state.db 读取 session 消息并保存
        → launchd_restart() 或 systemd_restart()
          → terminate_pid(pid) 发 SIGTERM
            → Gateway 信号 handler → runner.stop() → _stop_impl()
              → 【Gateway层保存】_auto_save_session() 保存 agent 消息
              → 清理资源、退出
          → service manager 重启 Gateway
```

#### `/new` 或 `/reset`（从聊天中执行）
```
用户发 /new
  → _handle_reset_command() (slash_commands.py:64)
    → 获取旧 agent
    → 【Gateway层保存】_auto_save_session(old_agent)
    → _cleanup_agent_resources(old_agent)
    → _evict_cached_agent(session_key)
    → 创建新 session
```

### 新 session 恢复
MEMORY 指示新 session 读取 `~/.hermes/last_session_context/last_session.json`

## 插件 Hook 系统

`VALID_HOOKS`（hermes_cli/plugins.py line 128）：
- `on_session_start` / `on_session_end` / `on_session_finalize` / `on_session_reset`
- `pre_tool_call` / `post_tool_call`
- `pre_llm_call` / `post_llm_call`
- `pre_gateway_dispatch`

插件位置：`~/.hermes/plugins/<name>/`（user plugins）或 `plugins/`（bundled）

## 扩展 MEMORY 容量

内置 MEMORY 有 2200 字符限制。详细方案见 [references/memory-file-system.md](references/memory-file-system.md)。

### 用户关键纠正
**"不要摘要，就完整的50或者100条记录，MEMORY空间也很小，满了一压缩，就差不多把以前的事情忘记了"**

- MEMORY 会压缩/合并，导致细节丢失
- 用户要的是完整记录，不是摘要
- 解决方案：MEMORY 只做索引，完整内容存 JSON 文件

## 贡献回官方仓库

改完源码后可以提 PR 给 NousResearch/hermes-agent：

### 流程
```bash
# 1. Fork 官方仓库（GitHub API）
curl -X POST https://api.github.com/repos/NousResearch/hermes-agent/forks \
  -H "Authorization: token $GITHUB_TOKEN"

# 2. 添加 fork remote
git remote add fork https://github.com/<username>/hermes-agent.git

# 3. 推送改动
git config http.proxy http://127.0.0.1:7897
git push fork main
git config --unset http.proxy

# 4. 用 API 创建 PR
curl -X POST https://api.github.com/repos/NousResearch/hermes-agent/pulls \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"title":"...","body":"...","head":"<username>:main","base":"main"}'
```

### PR 描述模板
```
## Problem
<描述问题>

## Solution
<描述方案>

**gateway/run.py:**
- New: `方法名()` 
- Called from: <触发点>

Saves to `~/.hermes/last_session_context/last_session.json`
```

### 注意
- 推到官方仓库需要 GitHub token（存在 `~/.git-credentials`）
- `hermes update` 会覆盖源码修改，PR 被合并后就不用手动维护了
- 官方仓库 21 万 star，PR 可能需要等较长时间 review

## ⚠️ Pitfalls

1. **`hermes update` 会覆盖源码修改** — 改完记得记录，更新后需要重新应用
2. **不能从 gateway 内部重启** — `hermes gateway restart` 会被拦截，需从外部终端执行
3. **state.db 在 profile 目录** — `~/.hermes/profiles/main/state.db`（286MB+），不是 `~/.hermes/state.db`
4. **Agent 消息在 `_session_messages`** — 不是 `messages` 或 `history`
5. **Hook 参数有限** — `on_session_finalize` 只传 `session_id`, `platform`, `reason`，不传消息内容，需要从 agent 对象读取
6. **直接改代码，不要提 workaround** — 用户原话："你加一个程序在这里不就好了"。发现系统已有相关功能（如 session 超时检测），直接找到代码修改，不要提替代方案（如 MEMORY 摘要、手动保存等）。用户期望的是直接解决，不是绕路。
7. **找到杀进程的代码，在它前面加** — 用户原话："杀死当前session的代码前面应该可以加入我们的代码"。定位到具体的 kill/stop/cleanup 代码行，在它之前插入保存逻辑。不要只改一处，要找到所有触发路径（超时、restart、stop、/new、/reset）。
8. **CLI 和 Gateway 是两个进程** — CLI 命令（`hermes gateway restart`）不能直接访问 Gateway 的 agent 对象。CLI 层面的保存需要从 state.db 读取，不能依赖 agent 内存。
9. **用户要完整记录，不要摘要** — 用户原话："不要摘要，就完整的50或者100条记录"。MEMORY 的 2200 字符限制会导致压缩丢信息，详细内容必须存文件。
