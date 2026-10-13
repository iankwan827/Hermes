# 详细配置指南

## 安装 BlackHole

```bash
brew trust steipete/tap
brew install blackhole-2ch
# 需要重启Mac才能生效
```

⚠️ brew install需要sudo密码，Hermes终端无PTY会报错，让用户手动执行。

## 创建多输出设备

### 方法A：GUI
1. 打开"音频MIDI设置"
2. 点"+" → "创建多输出设备"
3. 勾选：☑ Mac mini扬声器 + ☑ BlackHole 2ch
4. 右键 → "设为默认输出设备"

### 方法B：Swift脚本
```bash
swift scripts/create_multi_output_device.swift
```
自动检测设备，创建"HermesMO"多输出设备。

### ⚠️ 致命坑：子设备顺序

BlackHole必须排第一，否则录音静音：

```swift
// ✅ 正确
let subDevices: [[String: Any]] = [
    ["uid": "BlackHole2ch_UID"],   // ← 第一位！
    ["uid": "BuiltInSpeakerDevice"]
]

// ❌ 错误：录音静音
let subDevices: [[String: Any]] = [
    ["uid": "BuiltInSpeakerDevice"],
    ["uid": "BlackHole2ch_UID"]
]
```

### 验证

```bash
system_profiler SPAudioDataType | grep -B 5 "Default Output Device: Yes"
# 应显示"多输出设备"为默认
```

## ffmpeg avfoundation Bug 详情

在当前macOS系统上，ffmpeg avfoundation有严重bug：
- 计时器显示录了N秒，但实际文件只有几秒
- WAV/MP3/segment/不同采样率全部失败
- 根因：avfoundation与BlackHole虚拟设备的音频流同步问题

验证方法：录30秒 → `ffprobe` 检查时长是否=30秒

## Whisper 模型选择

| 模型 | 中文准确度 | 70分钟音频速度 | 适用场景 |
|------|-----------|---------------|---------|
| tiny | 低 | ~3分钟 | 快速预览 |
| base | 中 | ~8分钟 | 一般用途 |
| small | 中高 | ~15分钟 | 平衡选择 |
| **medium** | **高** | **~120分钟** | **推荐** |
| large-v3 | 最高 | ~240分钟 | 高精度 |

## 文件大小参考

| 格式 | 码率 | 1小时大小 |
|------|------|-----------|
| WAV 16kHz mono | 256 kbps | ~115 MB |
| MP3 128k | 128 kbps | ~57 MB |
