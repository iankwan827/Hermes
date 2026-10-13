---
name: audio-transcribe
description: "录音转文字稿：llama.cpp+gemma GPU加速转录（主方案）/ whisper（备用）。支持断点续传、增量保存、长音频分段处理。"
tags: ["audio", "transcription", "speech-to-text", "gemma", "llama-cpp", "whisper"]
triggers:
  - "录音转文字"
  - "音频转录"
  - "转文字稿"
  - "whisper转录"
  - "gemma转录"
---

# 录音转文字稿

## ⛔ 启动前强制检查（铁律）

**用户原话："你咋又用whisper了，skill不是让你用gemma吗"**

执行转录前必须读这段，不准跳过：
1. ✅ **默认用 gemma**：`python3 -u ~/Pictures/录音/transcribe.py input.wav -l zh`
2. ❌ **不准用 whisper**：除非 gemma 明确诊断失败（进程卡死、模型加载失败、GPU被占用），否则绝对不用 whisper
3. ❌ **不准自作主张替换 skill 指定的参数和工具**

如果用户没有明确说"用whisper"，就用gemma。不需要问。

**执行顺序（不可打乱）：**
1. 先加载本skill（audio-transcribe）
2. 确认用gemma（transcribe.py）
3. 再执行转录

**禁止行为：** 不加载skill就直接跑whisper。这不是可选步骤。

## 流程

1. **检查音频文件** → 确认格式和时长
2. **选择转录方案** → gemma4 GPU加速(默认, ~3.5x实时) / whisper CPU(仅gemma失败时备用, ~3x实时)
3. **执行转录** → 后台运行，增量保存进度，完成后通知
4. **格式化输出** → markdown文字稿

## ⚠️ 录音操作极简原则（铁律）

**用户原话："不是说你废话太多，是你录音的流程不对"**

录音就三步：**启动 → 确认一次在跑 → 完事。**

- ❌ 不要反复测试音频设备
- ❌ 不要中途杀进程检查状态
- ❌ 不要多次重启验证
- ✅ 启动后 `ls -lht <目录> | head -3` 确认文件出现即可
- ✅ 确认在跑就不动它，等它自然完成

## ⚡ 主方案：llama.cpp + Gemma E4B（GPU加速）

### 已验证性能（2026-06-29 第七课）
- 2h35m音频 → 155 chunks → 约50分钟完成转录
- 每chunk约17秒处理速度，~250-300字输出
- 速度约3.5x实时，稳定无中断

### 前置条件
- llama.cpp **从源码编译**（brew安装不支持Metal GPU）
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
# 基本用法
python3 -u ~/Pictures/录音/transcribe.py input.wav -l zh

# 断点续传（崩溃后恢复）
python3 -u ~/Pictures/录音/transcribe.py input.wav -l zh --resume
```

### 转录脚本特性（transcribe.py）
- **增量保存**：每块转录完立即写`.progress.json`，崩了最多丢最后一块
- **断点续传**：`--resume` 从上次断点继续，不用从头来
- **超时600秒/块**（旧版300秒太短会崩）
- **UTF-8容错**：模型输出乱码不会崩，自动替换
- **领域术语提示词**：prompt中已内置八字命理专业术语正确写法（华盖/偏印/正印/比肩/劫财/食神/食伤/壬水/癸水/己土/排盘），大幅降低同音字错误
- **简体中文输出**：prompt中已加入"请用简体中文输出"，zh和yue模式都会输出简体
- 190分钟音频约50分钟完成（GPU）
- **默认chunk大小60秒**：190分钟音频 = ~190 chunks

### ⚠️ 转录进度监控（2026-06-30 新增）

**问题**：转录是后台长时间运行的（30-120分钟），agent容易误判进度或过早下结论。

**progress.json结构**：
```json
{
  "chunks": {"0": "转录文本...", "1": "转录文本...", ...},
  "completed": 53
}
```
- `completed` = 已完成的chunk数量，不是百分比
- `chunks` = 已完成chunk的编号和文本
- 总chunk数 = 音频时长(秒) / chunk_size(默认60)

**查进度的标准命令**：
```python
import json, subprocess
with open('进度文件.progress.json') as f:
    p = json.load(f)
r = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration','-of','csv=p=0','音频.wav'], capture_output=True, text=True)
dur = float(r.stdout.strip())
total = int(dur / 60) + 1
done = p['completed']
print(f'进度: {done}/{total} chunks ({done/total*100:.0f}%)')
```

**禁止**：
- ❌ 看到progress.json有内容就说"转录完成了" — `completed`可能远小于总chunk数
- ❌ 进程还活着就说"停了" — 要用`ps aux | grep llama-mtmd`确认
- ❌ 中途反复查看进度打扰用户 — 设后台watcher，跑完自动通知

**后台监控脚本模板**：
```bash
#!/bin/bash
PROGRESS="路径/音频.progress.json"
TOTAL=总chunk数
while true; do
    DONE=$(python3 -c "import json; print(json.load(open('$PROGRESS'))['completed'])" 2>/dev/null)
    if [ "$DONE" -ge "$TOTAL" ] 2>/dev/null; then
        echo "TRANSCRIPTION_COMPLETE"
        break
    fi
    sleep 60
done
```
用`terminal(background=true, notify_on_complete=true)`运行，完成后自动通知。

也可直接用现成脚本：`scripts/watch_transcribe.sh <progress.json> <总chunk数>`

### ⚠️ 关键坑
1. **brew安装的llama.cpp不支持Metal**：必须从源码编译
2. **验证GPU是否工作**：CPU使用率<5%=GPU在跑，CPU>100%=在用CPU
3. **Python输出缓冲**：必须用`python3 -u`运行，否则看不到实时进度
4. **转录脚本路径**：`/tmp/llama.cpp/build/bin/llama-mtmd-cli`（非系统PATH）

## 🔄 备用方案：Whisper（CPU）

仅在gemma不可用时使用。速度约3倍实时，精度高但无GPU加速。

```bash
/Users/guanmian/Library/Python/3.9/bin/whisper input.wav --model medium --language zh --output_format txt --output_dir .
## ⚠️ macOS ffmpeg concat陷阱

**问题：** `ffmpeg -f concat` 在macOS上有两个坑：
1. **进程替换 `<(...)` 不工作**：bash的进程替换传给ffmpeg会报"Error opening input"
2. **相对路径不工作**：file list用相对路径时报"No such file"

**正确做法：** 用Python生成file list，写入/tmp，使用绝对路径：
```python
import os
files = sorted([f for f in os.listdir('.') if f.startswith('rec_') and f.endswith('.wav')])
with open('/tmp/concat_list.txt', 'w') as fp:
    for f in files:
        fp.write(f"file '{os.path.abspath(f)}'\n")
```
```bash
ffmpeg -y -f concat -safe 0 -i /tmp/concat_list.txt -c copy output.wav
```

## ⚠️ record.py重启后5分钟无输出

**问题：** 杀掉旧record.py进程后重启新进程，前5分钟看不到任何输出和文件。

**原因：** `sd.rec()`是阻塞调用，录满300秒才返回并保存文件。进程在录音中，只是还没到保存时间。

**验证方法：** 用独立Python测试音频设备是否有声音：
```python
import sounddevice as sd, numpy as np
r = sd.rec(2*16000, samplerate=16000, channels=2, device=0, dtype='float32')
sd.wait()
print(f'max={np.max(np.abs(r)):.4f}')  # >0.01 = 有声音
```

**⚠️ 多进程冲突：** 如果有多个record.py同时运行，BlackHole设备会被占用，新进程可能静默失败。重启前先`pkill -f "record.py"`清理所有旧进程。

### ⚠️ 杀进程前必须确认目标
**绝对不要批量杀所有后台进程。** 用户原话："你看你杀个进程都弄不好"。杀进程前必须用 `ps aux | grep <关键词>` 确认具体PID，只杀目标进程。录音进程（record.py / python3 record.py）和转录进程（llama-mtmd-cli / transcribe.py）绝对不能误杀。

### ⚠️ record.py必须传输出目录参数
不传参数时默认存到 `~/Desktop`，用户以为存在正确目录但实际没有。正确用法：
```bash
python3 -u ~/Pictures/录音/record.py ~/Pictures/录音/八字课/第七课
```
验证方法：启动后 `ls -lht <目标目录> | head -3` 确认文件出现在正确位置。

## ⚠️ 录音进程生命周期管理（铁律）

**问题：** 课结束后录音进程没人杀，一直跑着，下次开课时抢占BlackHole设备。

**规则1：结束录音必须主动杀进程**
- 用户说"停"/"结束"/"下课"/"录完了"时，**立即** `kill <PID>` 杀掉录音进程
- 不要等用户说"帮我杀进程"——用户说停=立刻杀
- 杀之前先 `ps aux | grep record.py` 确认PID，只杀目标进程

**规则2：启动新录音前先清理旧进程**
- 每次启动record.py前，先检查是否有旧的record.py在跑
- 如果有→先杀掉旧的→再启动新的
- 避免多进程抢占BlackHole设备

**规则3：记住PID**
- 启动录音后，记录PID到变量或备忘
- 结束时用这个PID杀进程，不要猜

**错误模式：**
- ❌ 课结束了但录音进程还在跑（周五的第十六课进程跑到周一）
- ❌ 启动新录音时旧进程还在抢占设备
- ❌ 用户说"停"但我没杀进程

**正确模式：**
- ✅ 用户说停→立刻 `kill <PID>`
- ✅ 启动前先 `ps aux | grep record.py` 清理旧进程
- ✅ 杀进程用具体PID，不用 `pkill -f` 一把梭

### ⚠️ record.py必须传输出目录参数
- `python3 record.py` 不传参数时默认存到 `~/Desktop`
- 必须传目录：`python3 record.py ~/Pictures/录音/八字课/第七课`
- 忘记传参数 → 录了半天文件存错地方 → 用户以为没录到

### ⚠️ 遵循skill定义
**不要自作主张替换skill定义的参数。** 用户原话："人家skill写用啥就用啥，不是我们说了算的。"
如果skill指定了某个参数但执行报错，应该告诉用户报错原因，让用户决定是否调整。

### ⚠️ 录完必须写skill
测试完新方法后立即写skill，否则下次失忆。用户原话："你没跑skill啊"。

### ⚠️ llama-mtmd-cli挂起不输出（根因已确认）
`transcribe.py`调用`llama-mtmd-cli`时可能卡住：进程在跑但CPU=0%、无输出。

**根因**：已有`llama-server`进程运行时占用GPU内存（~8GB），导致`llama-mtmd-cli`无法加载模型，卡在模型加载阶段。

**诊断方法**：
```bash
# 检查llama-mtmd-cli CPU使用率
ps aux | grep llama-mtmd | grep -v grep
# 0% CPU = 挂了，>100% CPU = 正在用CPU（也正常）
# 检查是否有llama-server在跑
ps aux | grep llama-server | grep -v grep
```

**解决**：杀掉所有llama进程后重试：
```bash
pkill -f "llama-mtmd-cli" 2>/dev/null
pkill -f "llama-server" 2>/dev/null
sleep 2
# 然后重新启动转录
python3 -u ~/Pictures/录音/transcribe.py input.wav -l zh
```

**备用方案**：如果gemme实在不行，换whisper（CPU慢但可靠）：
```bash
/Users/guanmian/Library/Python/3.9/bin/whisper input.mp3 --model medium --language zh --output_format txt --output_dir .
```
whisper medium模型CPU速度约3倍实时，3.6小时音频约需2小时。可以先提取后半段音频再转录，节省时间。

### ⚠️ 不要只录1分钟验证就忘了继续
录1分钟验证后立刻开始正式录制，不要停下来等。用户原话："你1分钟后忘记继续录就坏了"。

### ⚠️ 不要中途误判转录状态

**用户原话："你这不对啊，录了那么多，肯定没按skill跑啊"**

转录进程在后台跑时，progress.json是中间状态，不是最终结果。不要看到progress就当完成了。

**正确做法：** 用`ps aux | grep llama-mtmd`确认进程是否还在跑。进程在跑=还没完成，等notify_on_complete通知。

**错误做法：** 看到progress.json有数据就说"转录完成"，实际只跑了27%。
录1分钟验证后立刻开始正式录制，不要停下来等。用户原话："你1分钟后忘记继续录就坏了"。

### ⚠️ 录制时长设足够长
用户上课/直播可能超过2小时。宁可设60段（5小时），录完了喊停就行。

### ⚠️ 转录方案选择
优先用 `llama.cpp + gemma-4-E4B-it`（通过 `transcribe.py`），不是whisper。用户明确要求用gemma。

### ⚠️ 课程文件夹命名必须按顺序
**用户原话："第八不应该到第九吗？"**

上完第八课，下一个文件夹应该是**第九课**，不是第十课。
- ❌ 错误：第八课 → 第十课（跳课）
- ✅ 正确：第八课 → 第九课（按顺序）
- 创建文件夹前先 `ls ~/Pictures/录音/八字课/` 看现有课程编号，取最大值+1

### ⚠️ 不要声称完成但没执行
**用户原话："完了，你现在啥也不干就开始说干完了"**

❌ 错误模式：说"转录完成"但实际还没跑；说"录上了"但还没验证
✅ 正确模式：先执行 → 确认输出 → 再报告结果
- 每个步骤必须有实际tool output支撑，不能凭空说"完成了"
- 如果还在执行中，说"正在跑"而不是"完成了"

## ⚠️ Whisper领域特定听错

Whisper对专业术语容易听错，特别是八字/命理领域的同音字：

| 听错结果 | 正确内容 | 说明 |
|----------|----------|------|
| 鬼害 | 癸亥 | 天干癸+地支亥，同音 |
| 鬼水 | 癸水 | 天干癸的同音 |
| 人鬼水 | 壬癸水 | 壬癸连读混淆 |
| 官鬼 | 官杀 | 十神术语混淆 |
| 人水 | 壬水 | 天干壬的同音 |
| 同步型 | 同五行 | 同音字 |

**处理方法**：转录完成后用 `grep` 搜索常见错误词，批量替换。

## ⚠️ CLI路径（不在PATH）

Whisper CLI安装在Python 3.9下，不在默认PATH：
```bash
/Users/guanmian/Library/Python/3.9/bin/whisper
# 或
python3.9 -m whisper
```

## ⚠️ 语言参数

- **粤语（yue）medium模型不支持**：会报 `ValueError: tuple.index(x): x not in tuple`
- **只能用 `--language zh`**：whisper会用普通话识别
- **large-v3模型**支持 `yue`，但体积大、速度慢

## ⚠️ 输出格式

`--output_format md` **不是有效选项**！可选格式：`txt, vtt, srt, tsv, json, all`

## ⚠️ 录制验证（录音后必做）

```bash
ffprobe -v quiet -show_entries stream=duration -of csv=p=0 recording.wav
ffmpeg -i recording.wav -af volumedetect -f null /dev/null 2>&1 | grep mean_volume
```
- mean_volume < -50 dB → 静音，检查音频路由
- 时长明显短于预期 → 录制中断
- 正常（-20~-30 dB）→ 开始转录
