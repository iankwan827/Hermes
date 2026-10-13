---
name: macos-audio-recording
description: "Use when recording system audio on macOS. sounddevice+BlackHole for recording, whisper for transcription. Covers livestream, lectures, stand-up comedy."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [macos, audio, recording, blackhole, whisper, livestream]
    related_skills: []
triggers:
  - "录音"
  - "录声音"
  - "录直播"
  - "录系统声音"
  - "音频录制"
  - "record audio"
---

# macOS 系统音频录制

## Overview

用 BlackHole 虚拟音频驱动 + sounddevice 录制系统声音，gemma 转文字。
**不要用 ffmpeg avfoundation**（有 bug，录出来的文件只有几秒）。
**不要用 whisper**（用户明确要求用gemma，见转录方案选择）。

## When to Use

- 录直播课/讲座/栋笃笑
- 录网页音频/会议
- 需要转文字的场景
- **任何涉及"录音""录声音""录直播"的任务，必须先加载此skill**

## ⚠️ 必须先加载此skill

用户原话："你之前录音没有写skill吗，咋你又对录音失忆了"

**禁止行为**：不查skill就自己写录音脚本。record.py已存在且经过验证，直接用。
**正确流程**：收到录音任务 → `skill_view(macos-audio-recording)` → 按skill执行。

### ⚠️ "看skill开始录音"的正确理解

用户说"看skill开始录音"= 加载录音skill然后开始录音，**不是**列出所有skill。
- ❌ 错误：`skills_list()` → 列出176个skill → 用户怒："啥啊，我要你看录音skill啊"
- ✅ 正确：`skill_view(name='macos-audio-recording')` → 按skill执行录音

同理，"看XXskill"在录音语境下=加载录音skill，不是查看其他skill。

## 前置条件（一次性配置）

1. `brew install blackhole-2ch`（需重启Mac）
2. `uv pip install sounddevice soundfile openai-whisper`
3. Audio MIDI Setup 创建多输出设备（扬声器+BlackHole），设为默认输出

详见 `references/setup.md`

## 录制流程

### 1. 录1分钟验证

```python
python3 -c "
import sounddevice as sd, soundfile as sf, numpy as np
rec = sd.rec(int(60*16000), samplerate=16000, channels=1, device=1, dtype='float32')
sd.wait()
mx = np.max(np.abs(rec))
print(f'Max: {mx:.4f}' + (' ✅' if mx > 0.01 else ' ❌ SILENT'))
sf.write('/tmp/test.wav', rec, 16000)
"
```

- 有内容 → 进入步骤2
- 静音 → 检查多输出设备配置（BlackHole必须排第一）

### 2. 正式录制
### 2. 正式录制

```bash
# 八字课录音（自动按课程建文件夹，不设上限，录到喊停）
python3 ~/Pictures/录音/record.py ~/Pictures/录音/八字课/第三课 300
# 300 = 每5分钟一段，不设总段数（默认999段=83小时）
# Ctrl+C 停止

# 其他内容录音
python3 ~/Pictures/录音/record.py ~/Pictures/录音/栋笃笑 300
```

**文件夹命名规则**：
- 八字课：`~/Pictures/录音/八字课/第N课/`（如：第一课、第二课、第三课）
- 栋笃笑：`~/Pictures/录音/栋笃笑/<演出名>/`
- 其他：`~/Pictures/录音/<内容名>/`

⚠️ **开录前必须先创建文件夹**：
```bash
# 八字课：查最新课次，+1创建
# ⚠️ 必须用 ls -d 列目录，不能用 grep+sort-V（中文数字排序会错！）
ls -d ~/Pictures/录音/八字课/第*课/ 2>/dev/null | xargs -I {} basename {} | sort -V | tail -1
# 输出"第十课" → 创建"第十一课"
mkdir -p ~/Pictures/录音/八字课/第十一课
```
record.py虽然会自动建目录，但**推断课次必须在开录前完成**，不能录完再补。其他内容同理，先建文件夹再录。

**⚠️ 必须加载此skill再操作录音**：不要自己写录音代码（sounddevice/scipy等），record.py已经处理好所有细节。用户原话："肯定要按skill来"。

**⚠️ 不要问用户第几课**，直接查已有文件夹推断：
```bash
# ✅ 正确：用 ls -d 列出所有目录再排序
ls -d ~/Pictures/录音/八字课/第*课/ 2>/dev/null | xargs -I {} basename {} | sort -V | tail -1

# ❌ 错误：grep+sort-V 会漏掉中文数字文件夹
# grep "第.*课" | sort -V | tail -1 → 可能返回"第四课"而不是"第十课"
```

- 每5分钟自动切一个文件
- Ctrl+C 停止
- 后台录：`terminal(background=true, notify_on_complete=true)`

### 3. 合并+转录

```bash
# 合并所有段（注意文件名是 rec_*.wav，不是 part*.wav）
cd ~/Pictures/录音/八字课/第N课
python3 -c "
import soundfile as sf, numpy as np, glob
files = sorted(glob.glob('rec_*.wav'))
data = [sf.read(f)[0] for f in files]
combined = np.concatenate(data)
sf.write('完整.wav', combined, 16000)
print(f'{len(combined)/16000:.0f}秒，{len(combined)/16000/60:.1f}分钟')
"
```
# whisper转录（CPU，约3倍实时）
cd ~/Pictures/录音/<内容名> && python3 -m whisper 完整.wav --model medium --language zh --output_format txt --output_dir .
```

- 粤语用 `--language zh`（medium不支持yue）
- MPS不支持whisper，只能CPU
- 70分钟音频约需120分钟转录

## 文件组织

```
~/Pictures/录音/
├── record.py          （通用录音脚本）
├── transcribe.py      （转录脚本）
├── 八字课/
│   ├── 第一课/        （录音文件+转录）
│   ├── 第二课/
│   └── 第三课/        （今天录音）
├── 栋笃笑/
└── <其他>/
```

**每次录音前先确认课程编号**：问用户今天是第几课，或者查看 `~/Pictures/录音/八字课/` 下已有文件夹推断。

## Gemma转录（GPU加速）

### 前置条件
- llama.cpp需**从源码编译**开启Metal支持，brew安装的版本不支持GPU
- 模型：`~/models/gemma-4-E4B-it-Q4_K_M.gguf` + `mmproj-gemma-4-E4B-it-bf16.gguf`

### 编译llama.cpp（Metal GPU）
```bash
cd /tmp && git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
cmake -B build -DGGML_METAL=ON -DLLAMA_CURL=OFF
cmake --build build --config Release -j$(sysctl -n hw.ncpu)
```
编译后二进制在 `/tmp/llama.cpp/build/bin/llama-mtmd-cli`

### 运行转录
```bash
# 优先用brew版本（CPU模式，已验证可用）
python3 -u ~/Pictures/录音/transcribe.py <音频文件> -l zh

# 断点续传（崩溃后恢复）
python3 -u ~/Pictures/录音/transcribe.py <音频文件> -l zh --resume
```
- `-l zh` = 普通话，`-l yue` = 粤语
- `-u` = 禁用Python输出缓冲，实时看进度
- `--n-gpu-layers 99` = 全部层放GPU（仅编译版本有效）
- 每块转录完立即写`.progress.json`，崩了最多丢最后一块
- `--resume` 从上次断点继续，不用从头来
- 超时600秒/块（旧版300秒太短会崩）
- 190分钟音频约50分钟完成（GPU），CPU模式约2-3小时

### ⚠️ 关键坑
1. **brew安装的llama.cpp不支持Metal**：ggml库没编译Metal → 必须从源码编译才有GPU加速
2. **但brew版本可以用CPU模式**：`/opt/homebrew/bin/llama-mtmd-cli` 已存在，配合 transcribe.py 可以正常转录，只是速度慢一些（无Metal加速）
3. **验证GPU是否工作**：CPU使用率<5%说明GPU在跑，CPU>100%说明在用CPU
4. **Python输出缓冲**：必须用`python3 -u`运行，否则看不到实时进度
5. **转录脚本路径**：brew版本在 `/opt/homebrew/bin/llama-mtmd-cli`，编译版本在 `/tmp/llama.cpp/build/bin/llama-mtmd-cli`
6. **transcribe.py内置八字术语提示词**：已自动处理华盖/偏印/正印/比肩/劫财/食神/食伤/壬水/癸水/己土/排盘等专业术语，不需要手动写prompt

## ⚠️ 录音进程管理三条铁律

> 2026-07-13 用户纠正：周五的录音进程没杀掉，跑到周一抢占设备。

| # | 铁律 | 原因 | 正确做法 |
|---|------|------|----------|
| 1 | **用户说停→立刻杀进程** | 用户知道什么时候结束，等=浪费时间 | 收到停止指令后立即 `process(action='kill', session_id=xxx)` |
| 2 | **启动新录音前先清理旧进程** | 旧进程占用BlackHole设备，新进程拿不到音频 | 开录前先 `ps aux | grep record.py` 检查，有残留就杀 |
| 3 | **记住PID，用具体PID杀** | pkill一把梭可能杀错进程（比如误杀转录进程） | 启动时记PID，结束时 `kill <具体PID>`，不用 `pkill -f` |

**⚠️ 与现有pitfall的区分**：
- Pitfall #19 "绝对不能杀录音进程" = 不要**主动**杀（未收到用户指令时）
- 铁律 #1 "用户说停→立刻杀进程" = 收到**用户明确指令**后要果断
- 区别在于**谁发起的**：用户发起→执行；你发起→禁止

## Common Pitfalls

1. **ffmpeg avfoundation假的**：计时器显示录了N秒，文件只有几秒。只用sounddevice。
2. **不要怀疑用户配置**：录不到先查自己的命令，用户多输出设备通常没问题。
3. **Whisper MPS报错**：稀疏张量不支持MPS，只能CPU。
4. **粤语转录**：用 `--language zh`，不要用 `yue`。
5. **录完检查时长**：用 `ffprobe` 检查，不要信ffmpeg输出的时间。
6. **录完必须写skill**：测试完新方法后立即写skill，否则下次失忆（用户原话教训）。
7. **⚠️录音时间设长一点**：用户说课不止2.5小时，录30段×5分钟=2.5小时不够用。宁可设60段（5小时），录完了喊停就行。
8. **⚠️不要只录1分钟验证就忘了继续**：用户原话"你1分钟后忘记继续录就坏了"。录1分钟验证后立刻开始正式录制，不要停下来等。
9. **Gemma转录必须从源码编译llama.cpp**：brew安装的版本不支持Metal GPU。编译命令：`cmake -B build -DGGML_METAL=ON -DLLAMA_CURL=OFF`。验证GPU：CPU<5%=在跑GPU。`--n-gpu-layers 99`全层放GPU。详见`audio-transcribe` skill。
10. **Whisper速度对比**：whisper medium CPU约3倍实时，gemma GPU正常情况下更快但不稳定。如果gemma速度只有1倍实时，说明GPU没跑起来。
11. **⚠️ 必须加载本skill再录音**：用户明确要求"肯定要按skill来"。录音前必须先 `skill_view(name='macos-audio-recording')`，用 `record.py` 脚本，不要自己写录音代码。自己写的代码容易缺依赖（如scipy）、采样率不对（自写代码曾用44100Hz，record.py标准是16000Hz）、没有自动切段功能。用户对"失忆"极度敏感（原话"你又对录音失忆了"），每次录音前查skill是硬性要求。
12. **⚠️ 录制时长必须问用户或设足够长**：用户上课/直播可能超过2小时。不要默认设30段（2.5h），应该问用户预计多长，或者直接设60段（5h）。宁可多录不要少录——录完了用户喊停就行，但录不够就丢了内容。用户原话："不和你说了不止2个半小时吗"。
13. **转录方案选择**：优先用 `llama.cpp + gemma-4-E4B-it`（通过 `transcribe.py`），不是whisper。用户明确要求用gemma。用 `-l zh` 参数指定国语。
14. **⚠️ record.py后台运行必须加PYTHONUNBUFFERED**：不加的话看不到任何输出（stdout被缓冲），误以为没在录。正确用法：`PYTHONUNBUFFERED=1 python3 -u record.py ...`。验证录音是否在跑：`ls -la`看文件大小是否在增长，或用python测试`sd.rec()`看音量。
15. **⚠️ 不要同时跑多个record.py进程**：旧进程不退会导致新进程拿不到音频设备（BlackHole被占用），表现为进程在跑但不创建文件。开工前先按三条铁律#2检查并清理残留。
16. **ffmpeg合并用绝对路径**：macOS的ffmpeg concat格式文件必须用绝对路径，相对路径会报`Error opening input`。正确写法：`printf "file '/Users/xxx/xxx.wav'" > /tmp/concat.txt`。
17. **⚠️ 录音文件必须存到正确路径**：`~/Pictures/录音/八字课/第X课/`，不是 `~/Pictures/八字课/录播/`。用户原话："谁和你说是这样的文件夹，你看看skill"。开录前必须：1) 查已有课次文件夹 2) 推断今天第几课 3) mkdir创建文件夹 4) 用record.py录到该文件夹。不能自己选路径。
18. **⚠️ 课次编号必须开录前推断**：`ls -d ~/Pictures/录音/八字课/第*课/ | xargs basename | sort -V | tail -1` 查最新课次，+1创建新文件夹。不能录完再补，也不能猜。今天录了第六课（2026-06-26），文件夹是 `~/Pictures/录音/八字课/第六课/`。
19. **⚠️ 推断课次后不要问用户！** 用户已经告诉你上课了，直接+1创建文件夹开始录。用户原话："你妹啊，你不会算数吗"。只有在不确定是续录还是新开时才问。
20. **⚠️ 转录必须用 transcribe.py + gemma，不要用 whisper**：用户明确要求用gemma。`python3 -u ~/Pictures/录音/transcribe.py <音频> -l zh`。whisper精度虽高但不是用户要的。用户原话："你有毛病啊，看skill做啊"。即使gemma没编译Metal版本，brew安装的llama-mtmd-cli也能用（只是CPU模式，慢一些）。
21. **⚠️ 查最新课次用 `ls -d` 列目录，不要用 grep+sort**：`ls -d ~/Pictures/录音/八字课/第*课/ | xargs basename` 正确列出所有目录。中文数字排序 `sort -V` 有问题（第十课排在第四课前面），但列出目录本身没问题。
22. **⚠️ 绝对不能主动杀录音进程**（铁律#1的反面）：未收到用户指令时，即使你认为进程有问题也不要kill。录音每5分钟保存一个文件，先等5分钟看文件是否生成。用户原话："你是不是有毛病，他妈的我开始上课了，你杀掉进程，那不是前面的没了吗"。**收到用户明确停止指令后**，按铁律#1立刻杀。
23. **⚠️ 重启record.py必须传输出目录参数**：record.py第一个参数是输出目录，默认~/Desktop。重启时容易忘记传参数，导致录到错误位置。正确：`python3 -u record.py ~/Pictures/录音/八字课/第X课`。错误：`python3 record.py`（会录到Desktop）。
24. **⚠️ 验证录音进程在跑的最可靠方法**：`ls -lht <录音目录> | head -3` 看文件大小是否在增长。不要靠进程日志判断（可能被缓冲）。两个独立方法：1) `ps aux | grep record.py` 确认PID存在 2) `ls -la` 看文件数和大小。
20. **⚠️ 重启record.py必须传输出目录参数**：record.py第一个参数是输出目录，默认~/Desktop。重启时容易忘记传参数，导致录到错误位置。正确：`python3 -u record.py ~/Pictures/录音/八字课/第X课`。错误：`python3 record.py`（会录到Desktop）。
21. **⚠️ 验证录音进程在跑的最可靠方法**：`ls -lht <录音目录> | head -3` 看文件大小是否在增长。不要靠进程日志判断（可能被缓冲）。两个独立方法：1) `ps aux | grep record.py` 确认PID存在 2) `ls -la` 看文件数和大小。
15. **录音文件必须存到正确路径**：`~/Pictures/录音/八字课/第X课/`，不是 `~/Pictures/八字课/录播/`。用户原话："谁和你说是这样的文件夹，你看看skill"。开录前必须：1) 查已有课次文件夹 2) 推断今天第几课 3) mkdir创建文件夹 4) 用record.py录到该文件夹。不能自己选路径。
16. **课次编号必须开录前推断**：`ls -d ~/Pictures/录音/八字课/第*课/ | xargs basename | sort -V | tail -1` 查最新课次，+1创建新文件夹。不能录完再补，也不能猜。今天录了第六课（2026-06-26），文件夹是 `~/Pictures/录音/八字课/第六课/`。
17. **⚠️ 推断课次后不要问用户！** 用户已经告诉你上课了，直接+1创建文件夹开始录。用户原话："你妹啊，你不会算数吗"。只有在不确定是续录还是新开时才问。
23. **⚠️ 转录必须用 transcribe.py + gemma，不要用 whisper**：用户明确要求用gemma。`python3 -u ~/Pictures/录音/transcribe.py <音频> -l zh`。whisper精度虽高但不是用户要的。用户原话："你有毛病啊，看skill做啊"。即使gemma没编译Metal版本，brew安装的llama-mtmd-cli也能用（只是CPU模式，慢一些）。
24. **⚠️ 查最新课次用 `ls -d` 列目录，不要用 grep+sort**：`ls -d ~/Pictures/录音/八字课/第*课/ | xargs basename` 正确列出所有目录。中文数字排序 `sort -V` 有问题（第十课排在第四课前面），但列出目录本身没问题。
25. **⚠️ 创建文件夹后必须验证课次正确（2026-07-23 教训）**：创建新课次文件夹后，必须重新 `ls -d` 确认文件夹列表，验证新文件夹确实是最新且编号正确。今天犯错：最新课次是第24课，但创建了第26课文件夹（跳过了25），用户纠正后才杀掉重启正确课次。**铁律：创建后验证 = ls 确认新文件夹在列表中且编号 = 前一个+1。**

## ⚠️ 录音文件存储管理

**WAV文件很大**：每5分钟约9MB，一节课（2-3小时）约26个文件共230MB。合并后单个WAV约450MB。
**23节课WAV总计约26GB**，占满磁盘。

### WAV转MP3省空间

用户原话：\"转成mp3，省点位置\"

**关键发现**：每课有两类WAV文件：
- 分片文件：`rec_*.wav`（录制时每5分钟一个）
- 合并文件：`完整.wav` 或 `*_合并.wav`（分片合并后的完整音频）

**正确流程**（不要转分片，只转合并文件）：
```bash
# 1. 查看哪些课有合并文件
for d in ~/Pictures/录音/八字课/*/; do
  name=$(basename "$d")
  merged=$(ls "$d"*完整*.wav "$d"*合并*.wav 2>/dev/null | head -1)
  parts=$(ls "$d"rec_*.wav 2>/dev/null | wc -l)
  [ -n "$merged" ] && echo "$name: 合并=$(basename "$merged"), 片段=$parts"
done

# 2. 只转合并后的WAV为MP3（128kbps，约WAV的1/10大小）
cd ~/Pictures/录音/八字课
for f in $(find . -name "*.wav" -not -name "rec_*" -not -name "回放_*"); do
  mp3="${f%.wav}.mp3"
  [ ! -f "$mp3" ] && ffmpeg -i "$f" -codec:a libmp3lame -b:a 128k "$mp3" -y
done

# 3. 确认MP3生成后删除WAV
find . -name "*.wav" -not -name "rec_*" -not -name "回放_*" -delete
```

**不要做的事**：
- ❌ 转分片rec_*.wav（浪费时间，合并文件已包含全部内容）
- ❌ 用192kbps或更高（128kbps对语音足够，文件更小）
- ❌ 转完不删WAV（MP3和WAV同时存在等于没省空间）

**空间对比**：26GB WAV → 2.6GB MP3（128kbps），省90%。

### 删除分片文件

合并完成后，分片rec_*.wav可以删除（合并文件已包含全部内容）：
```bash
cd ~/Pictures/录音/八字课
find . -name "rec_*.wav" -delete
find . -name "回放_*.wav" -delete
```

### 转录完成后可删WAV

txt转录稿只有几MB。删WAV可省90%+空间。
```bash
# 查看哪些课有转录稿
ls ~/Pictures/录音/八字课/*/完整*转录.txt 2>/dev/null

# 删除已转录课的WAV（保留txt和mp3）
cd ~/Pictures/录音/八字课/第N课 && rm -f rec_*.wav 完整.wav
```

**macOS删除Containers目录需sudo**：游戏/应用容器（如原神22GB、星铁14GB）受系统保护，`rm -rf`报Operation not permitted，需`sudo rm -rf`。

## Verification Checklist

- [ ] 多输出设备包含扬声器+BlackHole，设为默认输出
- [ ] 录1分钟验证有内容（Max > 0.01）
- [ ] 正式录制每段5分钟，文件大小约9MB
- [ ] whisper转录有中文输出
