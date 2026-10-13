---
name: dingtalk-live
description: 进入钉钉直播间并录音。触发词：「直播」「钉钉直播」「理华直播」「进入直播间」「录直播」
---

# 钉钉直播间操作

## 进入直播间步骤

1. **清理前台窗口（关键！）**：
```bash
# 先隐藏Finder窗口，否则会挡住钉钉
osascript -e 'tell application "Finder" to set visible of every window to false'
sleep 0.5
```
⚠️ **Finder窗口经常挡住钉钉**：如果 cliclick 点击后截图显示的是Finder而不是钉钉，说明Finder在前台。必须先隐藏Finder。

2. **处理权限弹窗**：
```bash
# 如果出现"python3.11想要控制访达.app"弹窗，用AppleScript允许
osascript -e '
tell application "System Events"
    tell process "Finder"
        if exists sheet 1 of window 1 then
            click button "允许" of sheet 1 of window 1
        end if
    end tell
end tell'
```

3. **激活钉钉**：
```bash
osascript -e 'tell application "DingTalk" to activate'
sleep 1
```

4. **确认钉钉在前台**（截图验证）：
```bash
screencapture -x /tmp/dingtalk_check.png
# 用vision_analyze确认能看到黄色直播提示条
```

5. **点击黄色直播提示条进入直播间**：
```bash
# 方法A：使用已知坐标（窗口位置固定时）
cliclick c:1607,324

# 方法B：如果坐标不准，获取窗口位置重新计算
osascript -e '
tell application "System Events"
    tell process "DingTalk"
        set winPos to position of window 1
        set winSize to size of window 1
        log (item 1 of winPos) & "," & (item 2 of winPos) & "|" & (item 1 of winSize) & "x" & (item 2 of winSize)
    end tell
end tell'
# 黄色提示条大约在：窗口x+500, 窗口y+200 的位置
```
```

⚠️ **坐标说明**：黄色提示条"理华X号发起的直播正在直播"在钉钉聊天窗口顶部。坐标 **(1607, 324)** 是基于钉钉窗口在屏幕中间偏右时的值。如果钉钉窗口位置变了，需要重新获取。

### ⚠️ 进入直播间：直接按skill坐标点，不要分析截图（2026-07-16 教训）

**用户原话："你咋那么麻烦呢？每次点进去都出问题""skill 有坐标""你按 skill 坐标点进去就可以了"**

**正确流程（3步，不要多）：**
1. 隐藏Finder + 激活钉钉
2. 直接 `cliclick c:1607,324`（或根据窗口位置用 `(950,220)`）
3. 回复"录音已启动（第X课）"，不要问确认

**绝对不要：**
- ❌ 截图后用vision_analyze分析有没有黄色条
- ❌ 用Python检测像素颜色判断是否有直播条
- ❌ 反复截图对比
- ❌ 问用户"你看看截屏"
- ❌ 用户说"开始上课了"还问"进去了没"（用户原话：「我都和你说开始上课了，你还问我进去了没有？你有病么」）

**用户说"现在呢"=让你重新截一次图检查，不是让你分析。** 如果点完坐标用户说没进去，换个坐标再点，不要分析原因。

### ⚠️ 用户说"开始上课了"=已经在直播间，不要问确认（2026-07-21 教训）

**用户原话："我都和你说开始上课了，你还问我进去了没有？你有病么"**

当用户说"开始上课了开始录音"时：
1. 用户已经在直播间里了（否则没法上课）
2. 直接启动录音就行，不要问"进去了没"
3. 录音启动后，简短回复"录音在跑"即可，不要多话

**正确流程：** 用户说"开始上课了" → 查课次 → mkdir → record.py后台启动 → 回复一句"录音已启动（第X课）" → 结束

**错误流程：** 用户说"开始上课了" → 进直播间 → 点坐标 → 问"进去了没？" → 用户怒

**已验证坐标：**
- 钉钉窗口在屏幕中间偏右时：`(1607, 324)`
- 钉钉窗口在(448,121)大小1024x640时：`(950, 220)`
- 坐标不准时获取窗口位置重算：`osascript -e 'tell application "System Events" to tell process "DingTalk" to set winPos to position of window 1'`

**关键坑：Finder窗口会抢前台。** 如果Finder在钉钉前面，cliclick点击会被Finder拦截。必须先用AppleScript强制钉钉到前台：
```bash
osascript -e 'tell application "DingTalk" to activate'
osascript -e 'tell application "System Events" to tell process "DingTalk" to set frontmost to true'
```
如果Finder有权限弹窗（"python3想要控制访达.app"），必须先处理弹窗再操作钉钉。

4. **等待直播间加载**（2秒）：
```bash
sleep 2
```

5. **回复"录音已启动"**：用户已在直播间，不需要确认

## 录音

### ⚠️⚠️⚠️ 强制流程（不可跳过）⚠️⚠️⚠️

```
收到录音任务
  → 第1步：skill_view(name='macos-audio-recording')  ← 必须先加载！
  → 第2步：查已有课次，推断今天第几课
  → 第3步：mkdir 创建文件夹
  → 第4步：用 record.py 录制（不是自己写代码！）
```

**禁止行为（用户原话"你看看skill"）：**
- ❌ 不加载skill就自己写录音脚本
- ❌ 自定义文件夹路径（如 `~/Pictures/八字课/录播/`）
- ❌ 不推断课次就开录

**正确文件夹**：`~/Pictures/录音/八字课/第N课/`（如第六课）

用 record.py 录制直播间系统声音：

```bash
# 第2步：查最新课次
ls ~/Pictures/录音/八字课/ | grep "第.*课" | sort -V | tail -1
# 输出"第五课" → 今天录"第六课"

# 第3步：创建文件夹
mkdir -p ~/Pictures/录音/八字课/第六课

# 第4步：录制（BlackHole 2ch采集系统声音）
cd ~/Pictures/录音 && python3 record.py ~/Pictures/录音/八字课/第六课 300 999
```
- 参数2：每段秒数（300=5分钟）
- 参数3：总段数（999=不限）
- 采样率16000Hz，立体声
- Ctrl+C 停止，自动保存WAV

## 停止录音

在录音终端按 `Ctrl+C`，脚本会自动保存WAV文件。

## 转录

```bash
cd ~/Pictures/录音 && python3 transcribe.py 录音文件.wav -l zh
```

## 完整流程（一键）

```bash
# 1. 激活钉钉
osascript -e 'tell application "DingTalk" to activate'
sleep 0.5

# 2. 点击黄色直播提示条
cliclick c:1607,324
sleep 2

# 3. 启动录音（后台）
cd ~/Pictures/录音 && python3 record.py ~/Pictures/录音/钉钉直播/$(date +%Y%m%d) 300 999 &
```

## ⚠️ 进入直播间常见问题（实战经验）

### 1. Finder窗口遮挡（高频！）

**问题：** 激活钉钉后，Finder窗口仍然在最前面，导致截图看不到钉钉界面，cliclick点击也点不到黄色提示条。

**解决：** 进入直播间前先隐藏Finder：
```bash
osascript -e 'tell application "Finder" to set visible of every window to false'
```
或用AppleScript强制钉钉到最前台：
```bash
osascript -e '
tell application "DingTalk" to activate
delay 0.5
end tell
tell application "System Events"
    tell process "DingTalk"
        set frontmost to true
    end tell
end tell
```

**验证：** 不需要截图确认，直接点坐标就行。

### 2. 坐标(1607,324)不一定准确

**问题：** 坐标(1607,324)是基于钉钉窗口在特定位置时的值。如果窗口被移动、缩放、或被其他窗口挡住，坐标会偏移。

**正确流程：**
1. 先获取钉钉窗口位置：`osascript -e 'tell application "System Events" to tell process "DingTalk" to set winPos to position of window 1'`
2. 窗口在(448,121)大小1024x640时，黄色提示条大约在(950,220)
3. 窗口在之前位置时，(1607,324)有效
4. **最可靠方法：** 直接用已验证坐标点击，不要截图分析

### 3. Python3权限弹窗

**问题：** 首次运行python3脚本时，macOS可能弹出"python3.11想要控制访达.app"的权限请求，挡住所有操作。

**解决：**
```bash
osascript -e '
tell application "System Events"
    tell process "Finder"
        if exists sheet 1 of window 1 then
            click button "允许" of sheet 1 of window 1
        end if
    end tell
end tell
```
如果以上不行，需要在 系统设置→隐私与安全性→辅助功能 中手动允许。

### 4. 录音文件5分钟才出现

**问题：** record.py每300秒（5分钟）保存一个文件。启动后5分钟内看不到新文件是正常的，不代表没在录。

**验证录音是否正常：**
```bash
python3 -c "
import sounddevice as sd, numpy as np
r = sd.rec(1*16000, samplerate=16000, channels=1, device=0, dtype='float32')
sd.wait()
print(f'实时音量: max={np.max(np.abs(r)):.4f}')
"
```
- max > 0.01 → 有声音，录音正常
- max < 0.001 → 静音，检查BlackHole配置

**不要因为看不到文件就重启录音！** 会导致多进程冲突。

### 5. 多进程冲突

**问题：** 多次启动record.py会导致多个进程同时抢占BlackHole音频设备，录音异常。

**解决：** 每次启动前先清理：
```bash
pkill -f "record.py" 2>/dev/null
sleep 1
# 然后再启动新的
```

## 注意事项

- **cliclick必须安装**：`brew install cliclick`
- **BlackHole 2ch必须配置**：多输出设备包含BlackHole+扬声器
- **钉钉窗口位置**：坐标(1607,324)是窗口在当前屏幕位置的值，如果钉钉窗口移动了需要重新校准
- **录音是后台进程**：用 `process(action='poll')` 查看状态
- **停止录音**：`process(action='kill', session_id=xxx)` 或在终端按Ctrl+C

## ⚠️ Pitfalls

### ⚠️ 录音目录不能猜（用户纠正）

**问题：** 直接创建"第五课"目录，实际最新是第十课，今天应为第十一课。用户原话："你没事吧，咋可能第五课呢"

**根因：** `ls | grep "第.*课" | sort -V` 会漏掉部分中文数字文件夹（排序问题），只返回"第四课"。

**正确做法（两种都行）：**
```bash
# 方法1：列出所有第*课文件夹（推荐）
ls -d ~/Pictures/录音/八字课/第*课/ 2>/dev/null | xargs -I {} basename {}

# 方法2：直接看目录
ls ~/Pictures/录音/八字课/ | grep "第"
```
看到最新是"第十课"→ 今天录"第十一课"。

**禁止：** 不查目录就猜课次。每次都要先查。grep+sort-V可能漏文件夹。

### ⚠️ Finder窗口挡住钉钉（用户纠正）

**问题：** 执行`cliclick c:1607,324`时，如果Finder窗口在钉钉前面，点击会落在Finder上而不是钉钉黄色提示条。

**正确做法：**
1. 先用AppleScript强制钉钉到前台：`osascript -e 'tell application "DingTalk" to activate'`
2. 用System Events确认：`osascript -e 'tell application "System Events" to tell process "DingTalk" to set frontmost to true'`
3. 等1秒再点击
4. 如果Finder持续挡住，先隐藏Finder：`osascript -e 'tell application "Finder" to set visible of every window to false'`（注意：此命令可能超时，分步执行）

**验证方法：** 截图确认钉钉在最前面再点击。

### ⚠️ Python权限弹窗阻断自动化（用户纠正）

**问题：** 首次用Python/screencapture等工具操作其他应用时，macOS会弹出"xxx想要控制xxx.app"或"python3.11想访问其他App的数据"权限请求。这个弹窗会挡住钉钉界面，导致点击失效。

**正确做法：**
1. 截图检查是否有权限弹窗
2. 如果有，用AppleScript点击"允许"按钮：`osascript -e 'tell application "System Events" to click button "允许" of sheet 1 of window 1 of process "Finder"'`
3. 如果sheet方式失败，用cliclick直接点"允许"按钮的坐标
4. 权限授权后不会再弹出

**⚠️ 如果弹窗关不掉：** 告诉用户手动点"允许"，不要死磕。弹窗是系统级的，自动化有时无法绕过。

**注意：** 权限弹窗是系统级的，不是钉钉的。一旦授权永久生效。
- **Python环境**：macOS自带Python3.9，homebrew可能有3.11，确保sounddevice安装在使用的Python版本上

### ⛔ vision_analyze对截屏的识别可能严重错误（2026-07-07）

**用户原话：「你好好看看哪里来的飞书文档」「你是不是专门只截浏览器」「不是，我怀疑是你没截到正确的屏幕」**

screencapture -x 截屏是正确的，但 vision_analyze 分析截屏内容时可能**完全识别错**。真实案例：
- 实际截屏显示：钉钉直播间（八字排盘界面）
- vision_analyze 返回：飞书文档（第十二课笔记）
- 我信了它的分析，连续回复3次错误内容

**根因：** vision_analyze对复杂界面（多个窗口、直播画面、排盘软件等）的识别不可靠，容易把一个应用误识别为另一个。

**正确做法：**
1. 截屏后**不要用vision_analyze分析内容来描述给用户**
2. 直接把截屏文件路径发给用户确认
3. 如果需要识别截屏内容（如八字排盘），用vision_analyze时要明确告诉它"这不是飞书文档，请准确识别"
4. 用户说"不对"时，不要猜另一个答案，重新截屏让用户确认

**错误模式：**
- ❌ 截屏 → vision_analyze分析 → 把分析结果告诉用户 → 用户说不对
- ✅ 截屏 → 把文件路径发给用户 → 用户确认内容

### ⛔ 截屏后必须让用户确认，不能自己猜内容（2026-07-07）

**用户原话：「那你完蛋了，连截屏都不会了」「你截图文件夹干嘛」**

截屏后应该：
1. 告诉用户截屏已保存到哪个路径
2. 让用户确认截屏内容是否正确
3. 不要用vision_analyze的分析结果来描述屏幕内容

**正确回复模板：**
```
截屏已保存到 /tmp/xxx.png
你看看显示的是什么？
```
