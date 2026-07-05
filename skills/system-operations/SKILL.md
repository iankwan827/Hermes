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

### ⚠️ 冲突处理：merge 优先于 rebase，但 rebase 也可行

**核心原则**：当两端都有独立改动导致 push 被拒绝时，**优先使用 `git merge`**（更简单），但 `git rebase` 也能用（需要系统化冲突解决）。

#### 推荐路径：merge（简单自动合并）
```bash
# ✅ merge 更宽容，大多数冲突自动合并
git pull origin main
# 检查是否有冲突
git status
# 有冲突则手动解决，无冲突则完成
```

#### 备选路径：rebase（线性历史，需手动解决）
```bash
# 适用于 cron 任务或需要干净线性历史的场景
git pull origin main --rebase

# 查看冲突文件
git diff --name-only --diff-filter=U

# 解决后
git rebase --continue
```

#### 冲突解决策略（按文件类型）

| 文件类型 | 策略 | 说明 |
|---------|------|------|
| 状态文件（.curator_state, .usage.json） | 取较新版本 | 包含最近运行数据 |
| 内存文件（MEMORY.md） | 合并双方内容 | 两边的 tip 都有价值 |
| SKILL.md | 合并双方内容 | 两边的改动都保留 |
| config.yaml | 合并双方配置 | 保留所有配置项 |
| JSON 状态（jobs.json） | 取较新版本 | 时间戳和计数更新 |
| 重命名/删除冲突 | 保留重命名版本 | 保留新结构 |

#### rename/delete 冲突专项处理
```bash
# 当 Windows 端重命名了文件，Mac 端删除了原目录时
git add <新路径文件>   # 保留重命名后的文件
git rm <旧路径文件>    # 删除旧路径（如果存在）
# rebase --continue 或 commit
```

### 同步范围

**✅ 同步的文件：** skills/、config.yaml、SOUL.md、cron/jobs.json、memories/、plugins/

**❌ 不同步的文件：** .env（API密钥）、auth.json（OAuth令牌）、sessions/（会话数据）、logs/、*.db、cache/、gateway.lock/pid

### 常见问题

- **Push 被拒绝**：远程有本地没有的 commit → 先 pull（merge）再 push
- **.env 被 add**：`git reset HEAD .env` 然后加到 `.gitignore`

### 冲突解决实例

**2026-07-03 场景（merge 成功）：**
Windows 端 9 个文件变更，远程 Mac 端 1 个 commit。Rebase 产生 7 文件冲突，abort 后改 merge 成功自动合并。

**2026-07-04 场景（rebase + 手动解决）：**
Windows 端 17 文件变更，远程 Mac 端 4 commits（Chrome/CDP 修复）。Rebase 产生 8 文件冲突，通过系统化冲突解决（按文件类型策略）成功合并。

**教训对比：**
- Rebase 适合单边修改的线性历史；Merge 适合两边都有独立修改的分叉历史
- 8 个文件以下的冲突可用 rebase + 手动解决；超过 8 个文件建议用 merge
- 每日自动同步场景用 merge 更安全，但如果 cron 指定了 --rebase，可用上述策略手动解决

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
- ⚠️ Git 同步时 merge 优于 rebase（自动合并更多）；但如果 cron 指定了 --rebase，可用按文件类型策略手动解决冲突
