# Windows进程管理常用命令

## 列出Python进程
```powershell
tasklist | findstr python
```

## 查看进程详细信息（命令行+父进程）
```powershell
wmic process where "name='python.exe'" get ProcessId,ParentProcessId,CommandLine
```

## 杀指定PID
```powershell
taskkill /PID <PID> /F
```

## 查看特定父进程
```powershell
wmic process where "ProcessId=<ParentPID>" get Name,CommandLine
```

## 查看所有服务
```powershell
net start
```

## 查看计划任务
```powershell
schtasks /query /fo list /v
```

## PowerShell替代命令
```powershell
# 获取进程信息
Get-Process -Id <PID> | Select-Object Path,StartTime

# 查看进程树
Get-CimInstance Win32_Process -Filter "ProcessId=<PID>" | Select-Object ParentProcessId,CommandLine
```

## 常见进程占用
- whisper模型（small）：约1.5-1.7GB
- Hermes agent：约170-200MB
- Python基础：约5MB
