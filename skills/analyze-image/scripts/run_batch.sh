#!/bin/bash
# 加载环境变量并运行批量OCR
set -e
# 读取.env中的XIAOMI_API_KEY
while IFS='=' read -r key value; do
    if [ "$key" = "XIAOMI_API_KEY" ]; then
        export XIAOMI_API_KEY="$value"
        break
    fi
done < ~/AppData/Local/hermes/.env
echo "Key: ${XIAOMI_API_KEY:0:8}..."
UV_PYTHON="E:\\Users\\Administrator\\AppData\\Roaming\\uv\\python\\cpython-3.11-windows-x86_64-none\\python.exe"
"$UV_PYTHON" "D:/hermes-agent/scripts/batch_ocr.py" 2>&1
