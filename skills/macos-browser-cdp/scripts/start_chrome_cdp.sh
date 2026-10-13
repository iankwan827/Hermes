#!/bin/bash
# Chrome CDP 启动脚本
# 用法: ./start_chrome_cdp.sh [--copy-profile]
#
# 选项:
#   --copy-profile  复制用户 profile 到临时目录（保留登录态）
#   默认使用空 profile（快速启动）

set -e

# 配置
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CDP_PORT=9222
TEMP_PROFILE="/tmp/chrome-cdp-profile"
USER_PROFILE="$HOME/Library/Application Support/Google/Chrome"

# 解析参数
COPY_PROFILE=false
if [[ "$1" == "--copy-profile" ]]; then
    COPY_PROFILE=true
fi

echo "=== Chrome CDP 启动脚本 ==="

# 1. 杀掉所有 Chrome
echo "1. 杀掉所有 Chrome 进程..."
killall "Google Chrome" 2>/dev/null || true
pkill -9 -f "chrome_crashpad" 2>/dev/null || true
sleep 3

# 2. 准备 profile 目录
if [[ "$COPY_PROFILE" == true ]]; then
    echo "2. 复制用户 profile 到临时目录（用 rsync 保留登录态）..."
    rm -rf "$TEMP_PROFILE"
    rsync -a "$USER_PROFILE/" "$TEMP_PROFILE/"
    echo "   复制完成"
else
    echo "2. 使用空 profile..."
    rm -rf "$TEMP_PROFILE"
    mkdir -p "$TEMP_PROFILE"
fi

# 3. 启动 Chrome
echo "3. 启动 Chrome CDP 模式..."
open -a "Google Chrome" --args \
    --remote-debugging-port=$CDP_PORT \
    --user-data-dir="$TEMP_PROFILE" \
    --no-first-run \
    --no-default-browser-check

# 4. 等待 Chrome 启动
echo "4. 等待 Chrome 启动..."
sleep 5

# 5. 验证 CDP
echo "5. 验证 CDP 连接..."
RESPONSE=$(curl -s --connect-timeout 3 http://127.0.0.1:$CDP_PORT/json/version 2>&1)

if echo "$RESPONSE" | grep -q "Browser"; then
    echo "✅ CDP 启动成功！"
    echo "   端口: $CDP_PORT"
    echo "   Profile: $TEMP_PROFILE"
    echo "   WebSocket: $(echo "$RESPONSE" | grep -o '"webSocketDebuggerUrl": "[^"]*"' | cut -d'"' -f4)"
else
    echo "❌ CDP 启动失败"
    echo "   错误: $RESPONSE"
    exit 1
fi
