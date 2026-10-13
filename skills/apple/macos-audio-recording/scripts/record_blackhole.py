#!/usr/bin/env python3
"""
从 BlackHole 录制系统音频（sounddevice 方案）
用法: python3 record_blackhole.py [输出文件] [时长秒数]
示例: python3 record_blackhole.py output.wav 60
"""
import sys
import sounddevice as sd
import soundfile as sf
import numpy as np

# 参数
output_file = sys.argv[1] if len(sys.argv) > 1 else "recording.wav"
duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
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
    print("可用音频设备:")
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            print(f"  {i}: {d['name']} (in:{d['max_input_channels']})")
    sys.exit(1)

# 录制
print(f"录制 {duration} 秒到 {output_file} ...")
recording = sd.rec(
    int(duration * fs),
    samplerate=fs,
    channels=1,
    device=bh_device,
    dtype='float32'
)
sd.wait()

# 验证
max_vol = np.max(np.abs(recording))
mean_vol = np.mean(np.abs(recording))
print(f"最大振幅: {max_vol:.4f}, 平均振幅: {mean_vol:.4f}")

if max_vol < 0.001:
    print("⚠️ 警告: 录音几乎静音！请检查:")
    print("  1. 系统输出是否设为多输出设备（含 BlackHole）")
    print("  2. 是否有应用在播放音频")
    sys.exit(1)

# 保存
sf.write(output_file, recording, fs)
print(f"✅ 已保存到 {output_file}")
