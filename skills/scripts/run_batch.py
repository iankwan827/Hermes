#!/usr/bin/env python3
import os, subprocess, sys

env_path = os.path.expanduser("~/AppData/Local/hermes/.env")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("XIAOMI_API_KEY="):
            os.environ["XIAOMI_API_KEY"] = line.split("=", 1)[1]
            break

print(f"Key loaded: {os.environ.get('XIAOMI_API_KEY', '')[:8]}...")

script = "D:/hermes-agent/scripts/batch_ocr.py"
result = subprocess.run([sys.executable, script], capture_output=False)
sys.exit(result.returncode)
