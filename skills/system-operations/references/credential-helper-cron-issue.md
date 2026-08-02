# Windows Credential Manager 阻塞 Git Push（Cron 场景）

## 问题描述

在 Windows 上，`git credential.helper=manager`（Windows Credential Manager）在 cron 后台任务中会弹出 GUI 对话框请求凭据确认。由于 cron 运行时没有交互式终端，该对话框无法被操作，导致 `git push` 挂起直到超时。

## 症状

- `git push origin main` 卡住，长时间无输出
- `GIT_CURL_VERBOSE=1` 显示 `HTTP 401 Unauthorized` 后无后续
- fetch/pull 正常（因为只需要读取凭据），push 失败（因为需要写入/确认）

## 根因

Windows Credential Manager 的 credential helper 在 push 时需要用户交互确认（弹窗），在非交互式环境（cron、background terminal）中无法完成。

## 修复方案

### 方案 A：切换到 store 凭据（推荐）

```bash
git config credential.helper store
```

这会使用 `~/.git-credentials` 文件存储凭据，不需要 GUI 交互。

### 方案 B：禁用交互式提示

```bash
GIT_TERMINAL_PROMPT=0 git push origin main
```

这会阻止 git 尝试交互式输入，配合已有的凭据文件可以完成 push。

### 方案 C：环境变量覆盖（一次性）

```bash
GIT_ASKPASS=echo GIT_TERMINAL_PROMPT=0 git push origin main
```

## 诊断

```bash
# 检查当前凭据 helper
git config --list | grep credential

# 检查凭据文件是否存在
cat ~/.git-credentials | head -1

# 测试 push 是否正常
GIT_TERMINAL_PROMPT=0 git push origin main
```

## 时间线

- 2026-08-01：在 cron 双向同步任务中首次发现
- 之前可能因为凭据缓存而未触发（Windows Credential Manager 有缓存机制）
