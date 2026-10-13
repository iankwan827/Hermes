#!/bin/bash
# 转录进度监控脚本
# 用法: bash watch_transcribe.sh <progress.json路径> <总chunk数>
# 配合 terminal(background=true, notify_on_complete=true) 使用

PROGRESS="${1:?用法: $0 <progress.json> <总chunk数>}"
TOTAL="${2:?用法: $0 <progress.json> <总chunk数>}"

if [ ! -f "$PROGRESS" ]; then
    echo "ERROR: $PROGRESS 不存在"
    exit 1
fi

echo "开始监控转录进度: 目标 $TOTAL chunks"
while true; do
    DONE=$(python3 -c "import json; print(json.load(open('$PROGRESS'))['completed'])" 2>/dev/null)
    if [ -z "$DONE" ]; then
        sleep 30
        continue
    fi
    echo "进度: $DONE/$TOTAL ($(( DONE * 100 / TOTAL ))%)"
    if [ "$DONE" -ge "$TOTAL" ] 2>/dev/null; then
        echo "TRANSCRIPTION_COMPLETE: $DONE chunks done"
        break
    fi
    sleep 60
done
