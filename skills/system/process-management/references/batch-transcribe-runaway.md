# batch_transcribe.sh 进程雪崩问题

## 问题描述
`batch_transcribe.sh` 脚本可能在循环执行时生成多个子进程，形成进程树雪崩。每个bash进程下面挂着一个whisper python进程（占用1.5-1.7GB内存）。

## 症状
- 任务管理器看到多个python.exe，最大的占1.6GB+
- 手动结束任务后，新进程立刻出现（PID变了但内存占用不变）
- `tasklist | findstr python` 显示进程数量不断增加

## 根本原因
脚本在while循环或递归调用中不断spawn新的bash+python进程对。

## 解决方案

### 方法1：批量按命令行模式杀（推荐）
```powershell
# 杀所有batch_transcribe相关进程
wmic process where "commandline like '%batch_transcribe%'" call terminate

# 清理残留的whisper进程
wmic process where "commandline like '%whisper%'" call terminate
```

### 方法2：手动查PID逐个杀
```powershell
# 查看所有batch_transcribe进程
wmic process where "name='bash.exe'" get ProcessId,ParentProcessId,CommandLine | grep batch_transcribe

# 逐个杀
wmic process where "ProcessId=<PID>" call terminate
```

## 注意事项
- 不要用 `killall python` — 会杀掉Hermes agent自身
- MSYS bash下 `taskkill` 转义有问题，优先用 `wmic`
- 杀完后验证：`tasklist | findstr python` 应该只剩Hermes的进程（约170-200MB）
