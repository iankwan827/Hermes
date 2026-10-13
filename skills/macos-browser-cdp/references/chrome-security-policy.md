# Chrome CDP 安全策略详解

## 核心问题

Chrome 149+ (macOS) 拒绝在默认 profile 目录上启用远程调试。

### 错误信息
```
DevTools remote debugging requires a non-default data directory. Specify this using --user-data-dir.
```

### 触发条件
```bash
# ❌ 这样做会失败
open -a "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir="$HOME/Library/Application Support/Google/Chrome"
```

### 原因分析
Chrome 的安全策略禁止在生产 profile 上启用调试端口，防止恶意代码通过 CDP 访问用户的 cookies、密码、浏览历史。

## 解决方案

### 方案 1：复制 profile（推荐，保留登录态）
```bash
# 1. 杀掉所有 Chrome
killall "Google Chrome" 2>/dev/null
pkill -9 -f "chrome_crashpad" 2>/dev/null
sleep 3

# 2. 复制 profile（必须用 rsync -a，cp -R 会丢失登录态）
rsync -a "$HOME/Library/Application Support/Google/Chrome/" /tmp/chrome-cdp-profile/

# 3. 启动 Chrome
open -a "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp-profile \
  --no-first-run

# 4. 验证
sleep 5 && curl -s http://127.0.0.1:9222/json/version
```

**优点**：保留登录态、书签、扩展
**缺点**：复制需要时间（~30秒），占用磁盘空间
**关键**：必须用 `rsync -a`，`cp -R` 会丢失 cookies 等登录态数据

### 方案 2：使用空 profile（快速，无登录态）
```bash
# 1. 杀掉所有 Chrome
killall "Google Chrome" 2>/dev/null
sleep 3

# 2. 启动 Chrome
open -a "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp-profile \
  --no-first-run

# 3. 验证
sleep 3 && curl -s http://127.0.0.1:9222/json/version
```

**优点**：快速启动，无需复制
**缺点**：没有登录态，需要手动登录

## 调试技巧

### 检查 Chrome 是否在监听端口
```bash
# 方法 1：curl
curl -s http://127.0.0.1:9222/json/version

# 方法 2：lsof
lsof -i :9222 -P -n

# 方法 3：netstat
netstat -an | grep 9222
```

### 检查 Chrome 进程
```bash
# 查看所有 Chrome 进程
pgrep -fl "Google Chrome"

# 查看 Chrome 主进程
ps aux | grep "Google Chrome" | grep -v grep | head -3
```

### 检查 Chrome 锁文件
```bash
ls -la "$HOME/Library/Application Support/Google/Chrome/SingletonLock"
ls -la "$HOME/Library/Application Support/Google/Chrome/SingletonSocket"
ls -la "$HOME/Library/Application Support/Google/Chrome/SingletonCookie"
```

### Chrome 启动参数说明
- `--remote-debugging-port=9222` — 开放 CDP 调试端口
- `--user-data-dir=<path>` — 指定 profile 目录（必须是非默认目录）
- `--no-first-run` — 跳过首次启动向导
- `--no-default-browser-check` — 跳过默认浏览器检查

## 常见错误

### 1. Chrome 启动但端口没监听
**原因**：使用了默认 profile 目录
**解决**：使用 `--user-data-dir` 指定非默认目录

### 2. Chrome 启动后立即退出
**原因**：端口被占用
**解决**：
```bash
lsof -i :9222 | grep LISTEN
kill <PID>
```

### 3. CDP 连接超时
**原因**：Chrome 还没完全启动
**解决**：等待 5 秒再验证

### 4. 登录态丢失
**原因**：使用了空 profile
**解决**：复制用户 profile 到临时目录

## 参考链接
- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/
- Chrome 启动参数: https://peter.sh/experiments/chromium-command-line-switches/
