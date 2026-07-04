---
name: system-operations
description: "Windows/Hermes 系统运维操作。包含跨设备 Git 同步和进程安全管理。触发方式：同步配置、杀进程、查进程、进程雪崩、git push被拒。"
tags: [system, windows, git, sync, process, operations]
---

# System Operations — Windows/Hermes 系统运维

跨设备配置同步 + Windows 进程安全管理。涵盖日常运维中最常见的两类系统级操作。

---

## 一、跨设备 Git 同步

在多台设备（Windows + Mac）间同步 Hermes 配置、技能和记忆。由 cron 每日自动触发，也可手动执行。

### 核心工作流

```bash
cd "$HERMES_HOME"  # 通常是 ~/.hermes 或 E:/Users/Administrator/AppData/Local/hermes

# 1. 暂存同步目录
git add skills/ config.yaml SOUL.md cron/jobs.json memories/ plugins/

# 2. 检查变更
git status --short

# 3. 如果有改动，提交
git commit -m "auto-sync: $(date +%Y-%m-%d) <设备名>更新"

# 4. 推送（可能被拒绝——见下方冲突处理）
git push origin main

# 5. 拉取远程更新
git pull origin main

# 6. 检查对方改了什么
git log --oneline -5
```

### ⚠️ 冲突处理：merge 优先于 rebase

**关键教训**：当两端都有独立改动导致 push 被拒绝时，**使用 `git merge` 而非 `git rebase`**。

Rebase 会在每个本地 commit 上逐个重放远程变更，导致大量冲突（尤其当两端都改了相同文件时）。Merge 则创建一个合并 commit，自动合并大部分变更。

**错误路径（避免）：**
```bash
# ❌ rebase 会导致级联冲突
git pull origin main --rebase
# 7 个文件冲突，每个文件多处 conflict markers
```

**正确路径：**
```bash
# ✅ merge 更宽容
git pull origin main
# 或显式 merge
git merge origin/main --no-commit --no-ff
# 然后检查状态
git status
# 确认无冲突后提交
git commit -m "merge: 合并远程更新"
```

**如果 merge 仍有冲突：**
```bash
# 查看冲突文件
git diff --name-only --diff-filter=U

# 对于 JSON 文件：保留两边的键，手动合并值
# 对于 SKILL.md：检查哪边的版本更新/更完整
# 对于 config.yaml：保留两边的配置项

# 解决后
git add <resolved-files>
git commit -m "merge: 解决冲突"
```

### 同步范围

**✅ 同步的文件：** skills/、config.yaml、SOUL.md、cron/jobs.json、memories/、plugins/

**❌ 不同步的文件：** .env（API密钥）、auth.json（OAuth令牌）、sessions/（会话数据）、logs/、*.db、cache/、gateway.lock/pid

### 常见问题

- **Push 被拒绝**：远程有本地没有的 commit → 先 pull（merge）再 push
- **.env 被 add**：`git reset HEAD .env` 然后加到 `.gitignore`

### 冲突解决实例

2026-07-03 场景：Windows 端 9 个文件变更，远程 Mac 端 1 个 commit。Rebase 产生 7 文件冲突，abort 后改 merge 成功自动合并。

教训：Rebase 适合单边修改的线性历史；Merge 适合两边都有独立修改的分叉历史。每日自动同步场景用 merge 更安全。

---

## 二、Windows 进程管理

### 核心原则

**永远不要用 `killall python` 或 `taskkill /IM python.exe /F`** — Hermes agent 本身就是 Python 进程，会把自己杀掉。

### 安全流程

**1. 列出所有 Python 进程**
```powershell
tasklist | findstr python
```

**2. 识别每个进程的具体内容**
```powershell
wmic process where "name='python.exe'" get ProcessId,ParentProcessId,CommandLine
```

**3. 检查进程树（处理自动重启）**
如果杀掉进程后它又出现，说明有父进程在自动重启：
```powershell
wmic process where "ProcessId=<ParentPID>" get Name,CommandLine
```

**4. 安全终止进程**
```powershell
# 只杀指定 PID，不要用 /IM 杀同名进程
taskkill /PID <目标PID> /F
```

### ⚠️ MSYS bash 下 taskkill 转义问题

MSYS 会把 `/PID` 解析成路径，导致 `taskkill /PID xxx /F` 报错。解决方案：
- 用 `wmic process where "ProcessId=xxx" call terminate`
- 或用 `cmd //c "taskkill /PID xxx /F"` 双斜杠转义

### 批量杀进程（按命令行模式匹配）

```powershell
# 杀所有包含特定关键字的进程
wmic process where "commandline like '%keyword%'" call terminate
```

### 常见进程占用

- whisper 模型（small）：约 1.5-1.7GB
- Hermes agent：约 170-200MB
- Python 基础：约 5MB

---

## Pitfalls

- ⚠️ Hermes agent = Python 进程，误杀会导致会话断开
- ⚠️ whisper 模型加载后占用 1.6GB 内存，需要等它加载完再操作
- ⚠️ 自动重启的进程：杀了子进程会重生，必须找到父进程
- ⚠️ Windows 下不要用 `kill` 命令（那是 MSYS/Git Bash 的），用 `taskkill` 或 `wmic`
- ⚠️ Git 同步时 merge 优于 rebase，rebase 会导致级联冲突
