#!/usr/bin/env python3
"""录音脚本：sounddevice + BlackHole，每5分钟自动切文件
用法: python3 record.py [输出目录] [每段秒数] [总段数]
示例: python3 record.py ~/Pictures/录音/栋笃笑 300 14
"""
import sys
import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime

output_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop")
chunk_seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 300
total_chunks = int(sys.argv[3]) if len(sys.argv) > 3 else 999
fs = 16000

# 找BlackHole设备
devices = sd.query_devices()
bh_device = None
for i, d in enumerate(devices):
    if 'BlackHole' in d['name']:
        bh_device = i
        print(f"使用设备 {i}: {d['name']}")
        break

if bh_device is None:
    print("❌ 未找到BlackHole设备！")
    sys.exit(1)

os.makedirs(output_dir, exist_ok=True)
start_time = datetime.now()

print(f"开始录制... 每{chunk_seconds}秒保存一个文件，共{total_chunks}段")
print(f"输出目录: {output_dir}")
print(f"按 Ctrl+C 停止")

try:
    for file_num in range(1, total_chunks + 1):
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"rec_{timestamp}_part{file_num:02d}.wav")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 录制第{file_num}/{total_chunks}段...")
        recording = sd.rec(int(chunk_seconds * fs), samplerate=fs, channels=1, device=bh_device, dtype='float32')
        sd.wait()
        
        max_vol = np.max(np.abs(recording))
        if max_vol < 0.001:
            print(f"  ⚠️ 静音! Max={max_vol:.4f}")
        else:
            print(f"  Max: {max_vol:.4f}")
        
        sf.write(filename, recording, fs)
        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"  保存: {filename} ({size_mb:.1f}MB)")

except KeyboardInterrupt:
    print(f"\n录制停止。共{file_num}个文件")
