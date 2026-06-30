---
name: process-management
description: Windows进程管理安全操作。正确识别和终止进程，避免误杀Hermes agent自身。
triggers:
  - 杀进程
  - 终止进程
  - taskkill
  - 进程管理
---

# Windows进程管理安全操作

## 核心原则

**永远不要用 `killall python` 或 `taskkill /IM python.exe /F`** — Hermes agent本身就是Python进程，会把自己杀掉。

## 安全流程

### 1. 列出所有Python进程

```powershell
tasklist | findstr python
```

### 2. 识别每个进程的具体内容

```powershell
wmic process where "name='python.exe'" get ProcessId,ParentProcessId,CommandLine
```

这会显示每个Python进程的：
- PID
- 父进程PID
- 完整命令行（能看到在运行什么脚本）

### 3. 检查进程树（处理自动重启）

如果杀掉进程后它又出现，说明有父进程在自动重启。需要：
1. 查看ParentProcessId
2. 找到父进程是什么
3. 杀掉父进程，或同时杀掉父子进程

```powershell
# 查看父进程是什么
wmic process where "ProcessId=<ParentPID>" get Name,CommandLine
```

### 4. 安全终止进程

```powershell
# 只杀指定PID，不要用 /IM 杀同名进程
taskkill /PID <目标PID> /F
```

## Pitfalls

- ⚠️ Hermes agent = Python进程，误杀会导致会话断开
- ⚠️ whisper模型加载后占用1.6GB内存，需要等它加载完再操作
- ⚠️ 自动重启的进程：杀了子进程会重生，必须找到父进程
- ⚠️ Windows下不要用 `kill` 命令（那是MSYS/Git Bash的），用 `taskkill`

## 常见场景

**whisper转录脚本（batch_transcribe.sh）**：
- 可能出现进程雪崩：脚本循环生成新的whisper进程，杀一个重生一个
- 特征：多个bash.exe运行 `batch_transcribe.sh`，每个下面挂着whisper python进程
- 详细解决方案见 `references/batch-transcribe-runaway.md`
- 快速处理：用 `wmic process where "commandline like '%batch_transcribe%'" call terminate` 批量杀

**批量杀进程（按命令行模式匹配）**：
```powershell
# 杀所有包含特定关键字的进程
wmic process where "commandline like '%keyword%'" call terminate
```
比逐个找PID快得多，适合进程雪崩场景。

**MSYS bash下taskkill转义问题**：
- MSYS会把 `/PID` 解析成路径，导致 `taskkill /PID xxx /F` 报错
- 解决方案：直接用 `wmic process where "ProcessId=xxx" call terminate`
- 或用 `cmd //c "taskkill /PID xxx /F"` 双斜杠转义