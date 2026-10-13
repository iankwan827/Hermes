---
name: camofox-auto-start
description: "Browser backend readiness: ensure a browser is running before browser tools are used. Covers Chrome CDP (macOS/Linux), Camofox (Windows), and diagnostics."
version: 3.0.0
author: hermes-agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [browser, camofox, chrome, cdp, auto-start, setup]
---

# Browser Backend Readiness

每次使用浏览器工具之前，确保浏览器 backend 已启动并可连接。

## ⚠️ 核心原则：先诊断再行动

`browser_navigate` 超时时，**不要直接重试**。先分清是：
1. **浏览器没打开** — backend 进程没启动或 CDP 端口没监听
2. **网页加载慢** — 浏览器在跑但目标网站响应慢

**诊断步骤（必做）：**
```bash
# 检查 CDP 端口是否在监听
curl -s http://127.0.0.1:9222/json/version 2>/dev/null
# 或检查 Camofox
curl -s http://localhost:9377/health 2>/dev/null
```

有响应 → 浏览器在跑，可能是网页问题；无响应 → 浏览器没启动。

**Safari 不支持 CDP，Hermes 只能控制 Chromium 系浏览器（Chrome、Brave、Edge）。**

---

## macOS / Linux：Chrome CDP 模式（推荐）

### 1. 检查 Chrome CDP 是否已在运行

```bash
curl -s http://127.0.0.1:9222/json/version 2>/dev/null
```

如果返回 JSON（含 `"Browser": "Chrome/..."`），已就绪，跳到第 4 步。

### 2. 启动 Chrome CDP 模式

用 `terminal` 工具的 `background=true` 启动：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check
```

**为什么需要 `--user-data-dir`？** 如果 Chrome 已经在运行，再启动一个实例会复用已有进程（没有 `--remote-debugging-port`），CDP 端口不会打开。独立的 user-data-dir 强制启动新进程。

### 3. 等待 CDP 就绪

```bash
for i in 1 2 3 4 5; do
  sleep 2
  result=$(curl -s http://127.0.0.1:9222/json/version 2>/dev/null)
  if echo "$result" | grep -q '"Browser"'; then
    echo "Chrome CDP ready"
    break
  fi
done
```

### 4. 配置 Hermes 连接 CDP

```bash
hermes config set browser.cdp_url "ws://127.0.0.1:9222"
```

配置改完后，新开的 session 自动生效（当前 session 需要 `/reset`）。

---

## Windows：Camofox 模式

项目位置：`D:\hermes-agent\camofox-browser`

### 1. 检查 Camofox 是否在运行

```bash
curl -s http://localhost:9377/health 2>/dev/null
```

如果返回 `{"ok":true,...}` 且 `browserRunning: true`，已就绪。

### 2. 启动 Camofox

```bash
cd D:/hermes-agent/camofox-browser && node server.js
```

用 `terminal` 工具的 `background=true` 启动。

### 3. 等待就绪

每 2 秒检查，最多等 15 秒：

```bash
for i in 1 2 3 4 5 6 7; do
  sleep 2
  result=$(curl -s http://localhost:9377/health 2>/dev/null)
  if echo "$result" | grep -q '"ok":true'; then
    echo "Camofox ready"
    break
  fi
done
```

### 4. 验证

`browserRunning` 必须为 `true` 才能使用 browser 工具。

---

## 触发条件

在以下情况之前执行：
- `browser_navigate` 调用之前
- 任何需要浏览器的工具调用之前

**agent 必须在调用 browser_navigate 之前主动加载本 skill 并执行检查。**

---

## Pitfalls

### browser_navigate 超时 — 先查 backend 状态

超时不等于网页慢。99% 的情况是浏览器 backend 没启动。按上面的诊断步骤检查。

### 端口被占用

**macOS (9222)：**
```bash
lsof -i :9222
# 找到 PID 后 kill
kill <PID>
```

**Windows (9377)：**
```bash
netstat -ano | grep 9377
taskkill /PID <pid> /F
```

### Camofox 服务启动但浏览器未就绪

健康检查返回 `{"ok":true, "browserRunning":false}` 时，底层浏览器还在初始化。等 10-15 秒后重检。不要在 `browserRunning: false` 时调用 `browser_navigate`。

### Chrome 已在运行导致 CDP 端口打不开

必须用独立 `--user-data-dir`。直接启动 Chrome 实例会复用已有进程，CDP 端口永远不会开。这是最常见的坑。

### hermes config set 后不生效

配置变更在**新 session** 生效。当前 session 用 `/reset` 或退出重进。gateway 环境用 `hermes gateway restart`（不能从 gateway 内部执行，需要另开终端）。

### 不要随便 kill Chrome

用户已经登录的网站（如飞书）的 session 保存在 Chrome 进程里。kill Chrome 再重启会导致登录态丢失，需要重新扫码。只有在 CDP 端口确实被占用时才 kill。如果 `browser_navigate` 超时，先检查是不是网页问题，不要直接杀进程。

### browser_navigate 超时 ≠ 需要重启浏览器

90% 的超时是网页加载慢或网络问题，不是浏览器挂了。先 `curl -s http://127.0.0.1:9222/json/version` 确认 CDP 还活着，再决定是否重启。

### Windows 上 curl 可能找不到

git-bash 下 curl 通常可用。PowerShell 替代：
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:9222/json/version
```
