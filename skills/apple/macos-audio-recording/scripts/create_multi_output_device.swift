#!/usr/bin/env swift
// 创建多输出设备：BlackHole + 扬声器（Mac mini扬声器 / HDMI显示器）
// 自动检测音频设备，创建 "HermesMO" 多输出设备并设为默认输出
// 用法: swift create_multi_output_device.swift
// 依赖: macOS CoreAudio framework（无需额外安装）

import AudioToolbox

func getDeviceName(_ deviceID: AudioObjectID) -> String {
    var nameAddress = AudioObjectPropertyAddress(
        mSelector: kAudioDevicePropertyDeviceNameCFString,
        mScope: kAudioObjectPropertyScopeGlobal,
        mElement: kAudioObjectPropertyElementMain
    )
    var name: CFString = "" as CFString
    var nameSize = UInt32(MemoryLayout<CFString>.size)
    AudioObjectGetPropertyData(deviceID, &nameAddress, 0, nil, &nameSize, &name)
    return name as String
}

func getDeviceUID(_ deviceID: AudioObjectID) -> String {
    var uidAddr = AudioObjectPropertyAddress(
        mSelector: kAudioDevicePropertyDeviceUID,
        mScope: kAudioObjectPropertyScopeGlobal,
        mElement: kAudioObjectPropertyElementMain
    )
    var uid: CFString = "" as CFString
    var uidSize = UInt32(MemoryLayout<CFString>.size)
    AudioObjectGetPropertyData(deviceID, &uidAddr, 0, nil, &uidSize, &uid)
    return uid as String
}

// 1. 列出所有设备，找到 BlackHole 和扬声器
var devAddress = AudioObjectPropertyAddress(
    mSelector: kAudioHardwarePropertyDevices,
    mScope: kAudioObjectPropertyScopeGlobal,
    mElement: kAudioObjectPropertyElementMain
)
var devSize: UInt32 = 0
AudioObjectGetPropertyDataSize(AudioObjectID(kAudioObjectSystemObject), &devAddress, 0, nil, &devSize)
let devCount = Int(devSize) / MemoryLayout<AudioObjectID>.size
var devIDs = [AudioObjectID](repeating: 0, count: devCount)
AudioObjectGetPropertyData(AudioObjectID(kAudioObjectSystemObject), &devAddress, 0, nil, &devSize, &devIDs)

var blackholeUID = ""
var speakerUID = ""
var speakerName = ""

for did in devIDs {
    let name = getDeviceName(did)
    if name == "BlackHole 2ch" {
        blackholeUID = getDeviceUID(did)
    }
    // 优先 Mac mini扬声器，其次任何非BlackHole的输出设备
    if name.contains("Mac mini扬声器") || (speakerUID.isEmpty && name.contains("扬声器")) {
        speakerUID = getDeviceUID(did)
        speakerName = name
    }
}

guard !blackholeUID.isEmpty else {
    print("❌ 未找到 BlackHole 2ch 设备！请先安装: brew install blackhole-2ch")
    exit(1)
}
guard !speakerUID.isEmpty else {
    print("❌ 未找到扬声器设备！")
    print("可用输出设备:")
    for did in devIDs {
        let name = getDeviceName(did)
        print("  \(did): \(name)")
    }
    exit(1)
}

print("BlackHole UID: \(blackholeUID)")
print("扬声器: \(speakerName) (UID: \(speakerUID))")

// 2. 删除已有的 HermesMO 设备（避免重复）
for did in devIDs {
    if getDeviceName(did) == "HermesMO" {
        AudioHardwareDestroyAggregateDevice(did)
        print("  已删除旧 HermesMO (\(did))")
    }
}

// 3. 创建多输出设备
let subDevices: [[String: Any]] = [
    ["uid": blackholeUID],
    ["uid": speakerUID]
]
let description: [String: Any] = [
    kAudioAggregateDeviceNameKey as String: "HermesMO",
    kAudioAggregateDeviceUIDKey as String: "com.hermes.mo.\(UUID().uuidString)",
    kAudioAggregateDeviceSubDeviceListKey as String: subDevices,
    kAudioAggregateDeviceIsPrivateKey as String: false,
    kAudioAggregateDeviceTapListKey as String: [] as [[String: Any]]
]

var newDevice: AudioObjectID = 0
let createResult = AudioHardwareCreateAggregateDevice(description as CFDictionary, &newDevice)

guard createResult == 0 && newDevice != 0 else {
    print("❌ 创建多输出设备失败: result=\(createResult)")
    exit(1)
}

print("✅ 已创建 HermesMO (ID: \(newDevice))")

// 4. 设为默认输出
var defaultOutAddr = AudioObjectPropertyAddress(
    mSelector: kAudioHardwarePropertyDefaultOutputDevice,
    mScope: kAudioObjectPropertyScopeGlobal,
    mElement: kAudioObjectPropertyElementMain
)
var setID = newDevice
let setResult = AudioObjectSetPropertyData(
    AudioObjectID(kAudioObjectSystemObject),
    &defaultOutAddr, 0, nil,
    UInt32(MemoryLayout<AudioObjectID>.size),
    &setID
)

if setResult == 0 {
    print("✅ 已设为默认输出设备")
    print("   你现在能通过 \(speakerName) 听到声音")
    print("   同时 BlackHole 可以捕获系统音频用于录制")
} else {
    print("⚠️ 设为默认输出失败: result=\(setResult)")
    print("   请手动在 Audio MIDI Setup 中设置")
}
