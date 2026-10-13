#!/usr/bin/env python3
"""
长时间录音脚本：每5分钟自动保存一个文件，适合直播课录制
用法: python3 record_live.py [输出目录] [每段秒数]
示例: python3 record_live.py ~/Pictures/八字课/录播 300
"""
import sys
import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime

# 参数
output_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop")
chunk_seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 300  # 默认5分钟
fs = 16000

# 找 BlackHole 设备
devices = sd.query_devices()
bh_device = None
for i, d in enumerate(devices):
    if 'BlackHole' in d['name']:
        bh_device = i
        print(f"使用设备 {i}: {d['name']}")
        break

if bh_device is None:
    print("❌ 未找到 BlackHole 设备！")
    sys.exit(1)

os.makedirs(output_dir, exist_ok=True)
start_time = datetime.now()
file_num = 1

print(f"开始录制... 每 {chunk_seconds} 秒保存一个文件")
print(f"输出目录: {output_dir}")
print(f"按 Ctrl+C 停止")

try:
    while True:
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"直播_{timestamp}_part{file_num:02d}.wav")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 录制 part {file_num}...")
        recording = sd.rec(
            int(chunk_seconds * fs),
            samplerate=fs,
            channels=1,
            device=bh_device,
            dtype='float32'
        )
        sd.wait()
        
        max_vol = np.max(np.abs(recording))
        mean_vol = np.mean(np.abs(recording))
        
        if max_vol < 0.001:
            print(f"  ⚠️ 警告: 静音! Max={max_vol:.4f}")
        else:
            print(f"  Max: {max_vol:.4f}, Mean: {mean_vol:.4f}")
        
        sf.write(filename, recording, fs)
        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"  保存: {filename} ({size_mb:.1f}MB)")
        
        file_num += 1

except KeyboardInterrupt:
    print(f"\n录制停止。共 {file_num - 1} 个文件")
