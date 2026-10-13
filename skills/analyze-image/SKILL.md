---
name: analyze-image
description: "图片分析：单张用vision_analyze，长图切片后逐段OCR，批量用脚本。"
tags: [vision, ocr, image]
triggers:
  - "分析图片"
  - "提取图片文字"
  - "图片OCR"
---

# 图片分析

## ⚠️ 强制检查清单（每次都必须执行）

收到图片后，**按顺序执行，不准跳步**：

1. **PIL检查尺寸**：
```python
from PIL import Image
img = Image.open(img_path)
w, h = img.size
```
2. **判断**：h > 2000px → 必须切片。w > 5000px → 用1500px段高，否则2000px。
3. **切片** → 逐段 `vision_analyze` → 合并

**禁止**：直接对 h>2000 的图片调用 vision_analyze。整张发会丢失50-70%内容。
**禁止**：因为"看起来不长"或"先试试"就跳过检查。

## ⚠️ 铁律：收到图片第一步必须检查尺寸！

**用户原话："你咋每次看完skill都不按skill来切呢""我不想每天都要重复说切开"**

```python
from PIL import Image
img = Image.open(img_path)
w, h = img.size
# h > 2000 → 必须切片，不准整张发！
```

| 场景 | 做法 |
|------|------|
| **单张短图** (h≤2000px) | 直接 `vision_analyze` |
| **单张长图** (h>2000px) | **必须切片**：2000px段高（w>5000用1500px）→ 逐段vision_analyze → 合并 |
| **批量/docx提取** | 用scripts/下的脚本 |

**整张长图直接发会丢失50-70%内容。不检查尺寸就发=没按skill来。**

## 长图切片（Mac）

```python
from PIL import Image
img = Image.open(img_path)
w, h = img.size
slice_h = 1500 if w > 5000 else 2000
for i, y in enumerate(range(0, h, slice_h)):
    seg = img.crop((0, y, w, min(y+slice_h, h)))
    seg.save(f"/tmp/seg_{i}.png")
# 然后逐段调用 vision_analyze
```

## 批量处理（Windows脚本）

脚本位于 `scripts/` 目录，详见 `references/batch-processing.md`。

核心脚本：
- `full_extract.py` — 自动切割长图，推荐
- `extract_from_docx.py` — 从docx提取图片并OCR
- `retry_zero.py` — 重试失败的图片

## ⚠️ 铁律：长图必须先切片再OCR

**用户原话："你咋每次看完skill都不按skill来切呢"**

收到图片后第一步必须用PIL检查尺寸，高度>2000px必须切片，不准整张长图直接发vision_analyze。

```python
from PIL import Image
img = Image.open(img_path)
w, h = img.size
slice_h = 1500 if w > 5000 else 2000
# 切片后逐段vision_analyze，再合并
```

### Slice and OCR

```python
from PIL import Image
import os

def ocr_courseware_image(image_path, output_path):
    img = Image.open(image_path)
    w, h = img.size
    if h <= 2000:
        return vision_analyze(image_path, "识别图片中的所有文字，保持原格式")
    
    slice_height = 2000
    slices = []
    for i in range(0, h, slice_height):
        end = min(i + slice_height, h)
        slice_path = f"/tmp/slice_{i}_{end}.png"
        img.crop((0, i, w, end)).save(slice_path)
        slices.append(slice_path)
    
    all_text = []
    for i, slice_path in enumerate(slices):
        result = vision_analyze(slice_path, "识别图片中的所有文字，保持原格式")
        all_text.append(result)
        os.remove(slice_path)
    
    full_text = "\n\n".join(all_text)
    with open(output_path, "w") as f:
        f.write(f"# {os.path.basename(image_path)} OCR结果\n\n")
        f.write(full_text)
    return output_path
```

### Batch courseware OCR

```python
import glob

def batch_ocr_courseware(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    images = glob.glob(f"{input_dir}/*.png") + glob.glob(f"{input_dir}/*.jpg")
    for img_path in images:
        output_path = f"{output_dir}/{os.path.basename(img_path).split('.')[0]}.md"
        ocr_courseware_image(img_path, output_path)
```

### Courseware pitfalls

- 2000px slice height is the sweet spot (too large → vision blur; too small → inefficient)
- Don't compress originals — keep full resolution
- Supports: png, jpg, jpeg, webp
- Auto-cleans temp slice files after processing

## Pitfalls

### 0. ⚠️ vision_analyze对截屏图片也可能产生严重幻觉（2026-07-23 新增）

**问题：** 不仅课件长图，连用户截屏的课件图片vision_analyze也会完全识别错误。

**真实案例（第二十四课）：** 用户提供8张截屏，内容是"女命经典断语59条"（1-59条逐条列出）。vision_analyze连续8张全部误识别为"吃软饭男命的命理特征"，标题、内容全部错误。

**根因：** vision_analyze对课件截屏的注意力分布不均，可能只看到图片的一部分就下结论。

**正确流程：**
1. 截屏图片OCR优先用小米API（`api.xiaomimimo.com/v1/chat/completions`）
2. 不要信任vision_analyze对截屏的识别结果
3. 如果必须用vision_analyze → 逐片切小再识别，不能整张发

**小米API调用模板：**
```python
import os, json, base64, urllib.request, io
from PIL import Image

api_key = ''
with open(os.path.expanduser('~/.hermes/.env')) as f:
    for line in f:
        stripped = line.strip()
        if stripped.startswith('XIAOMI_API_KEY') and not stripped.startswith('#'):
            api_key = stripped.split('=', 1)[1].strip()
            break

img = Image.open(img_path)
buf = io.BytesIO()
img.save(buf, format='PNG')
b64 = base64.b64encode(buf.getvalue()).decode()
data_url = f'data:image/png;base64,{b64}'
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
payload = {
    'model': 'mimo-v2.5',
    'messages': [{'role': 'user', 'content': [
        {'type': 'text', 'text': '请完整OCR提取这张图片的所有文字，保持排版。'},
        {'type': 'image_url', 'image_url': {'url': data_url}},
    ]}],
    'max_tokens': 16000,
    'temperature': 0.1
}
req = urllib.request.Request('https://api.xiaomimimo.com/v1/chat/completions',
    data=json.dumps(payload).encode(), headers=headers, method='POST')
with urllib.request.urlopen(req, timeout=120) as resp:
    text = json.loads(resp.read())['choices'][0]['message']['content']
```

### 0. ⚠️ 长图不能只看顶部就下结论（2026-07-23 新增）

**问题：** 对8054px长图只看了前2000px就认为"课件只有5个标题框，没有详细文字"，实际每个标题下方在图片更底部有完整的白话解释、命理逻辑、应验率等内容。

**根因：** 看到前几段切片后就停止了，没有继续往下看。

**⚠️ 强制流程：**
1. 切片后必须**逐段查看所有切片**，不能只看前几段
2. 如果课件结构JSON显示有子节内容但OCR没读到 → 必须继续切更细的片往下看
3. 特别注意：课件标题框通常在顶部，详细内容在标题框下方较远处
4. 全部切片看完后才能判断"课件有没有详细内容"

**错误模式：**
- ❌ 看了前2段就停，说"课件只有标题"
- ❌ 看不到内容就自己编

**正确模式：**
- ✅ 逐段切片看完所有内容
- ✅ 确认每个知识点在课件中的完整内容后再写笔记

### 0. ⚠️ 不能凭文件名判断图片内容类型

**用户原话：「谁说这张是录音图呢」**

`rec_`前缀的png文件可能是课件截图，不是录音界面。`截图`、`微信`、`分享`等前缀也不能作为判断依据。

**强制流程：** 每张图片都必须用 `vision_analyze` 检查实际内容，不能根据文件名前缀跳过或归类。

### 0. ⚠️ vision_analyze对课件图片可能产生幻觉（2026-07-07 严重）
**问题**：vision_analyze直接读取课件图片时，可能返回完全错误的内容。
**真实案例**：rec_开头的png实际是「健康断病」课件，vision_analyze却返回「辛金」内容，导致整节课笔记全部错误。
**正确流程**：
1. 先用 `screencapture -x /tmp/screen.png` 截取mac屏幕确认用户看到的内容
2. 再用vision_analyze逐段OCR切片
3. OCR结果必须和截屏内容交叉验证
**铁律：vision_analyze的结果不能直接信任，必须交叉验证。**

### 0. ⚠️ OCR切片可能遗漏整个章节（2026-07-07 新增）
**问题**：即使用正确的切片高度（2000px）逐段OCR，vision_analyze仍可能遗漏整个章节。
**真实案例**：健康断病课件有8个大点，OCR只识别出前3个，遗漏了第4-7点（古典、刑冲合、十神断病、高应验）。
**根因**：vision_analyze对长图切片的识别不完整，特别是当章节标题在切片边界附近时。
**正确流程**：
1. 完成所有切片OCR后，**必须交叉验证**
2. 用screencapture截取用户屏幕，用vision_analyze逐个数出所有章节标题
3. 对比OCR输出中的章节列表，检查是否有遗漏
4. 如果有遗漏，重新切片OCR遗漏的部分
**验证方法**：输出"课件截图显示N个大点，OCR输出识别M个章节，遗漏：[列表]"

### 0. ⚠️ vision说"没有"但用户说"有"→ 立刻截屏，不要争辩（2026-07-10 新增，2026-07-14 强化，2026-07-14 二次强化）
**问题**：vision_analyze可能完全漏掉图中确实存在的内容，而且反复重试（换切片高度、放大、逐块看）也不会改善。
**真实案例**：课件图"拾易八字课十八-25 上.png"，用户说第一行是"用神四大取法"、有两个案例命盘（庚申乙酉戊申庚申、壬戌丙午庚辰癸未）。我切了9块→14块→逐块看→放大Preview区域，每次都回复"没有"。用户反复纠正（"你肯定识别错了图片""你切的不够吧""你自己没识别出来""你失忆了？？"），我却一直重复问用户确认。
**根因**：vision模型对长图的注意力分布不均，同一张图多次识别返回不同内容，且无法通过调整参数解决。
**⚠️ 强制流程（铁律级别，不可跳过）**：
1. 如果用户说"图里有X"但vision说"没有X" → **立刻停止争辩，第一次就停下来**
2. 立刻用 `screencapture -x /tmp/screen.png` 截屏确认用户实际看到的内容
3. 对截屏用 vision_analyze 确认
4. 如果截屏也找不到 → 直接问用户，不要自己猜
5. **注意**：问题可能出在PIL读取（见上方"PIL返回错误像素数据"pitfall），不是vision的问题。截屏对比能同时验证两者。
**⚠️ 绝对禁止（违反任何一条=严重错误）**：
- 禁止说"我反复看了确实没有"（用户原话："你切的不够吧""你就是切错图片了"）
- 禁止说"这张图只有XXX"（用户原话："第一行人家就是用神四大取法"）
- 禁止用"你确定吗？""是不是另一张图？"来质疑用户
- 禁止反复用不同切片高度重试（500→800→1500）而不做截屏
- 禁止在截屏后还反复问用户"你看到的第一行是什么？"（用户原话："你自己没识别出来""你失忆了？？"）
**铁律：用户能看到的内容，vision看不到 = vision的问题。截屏验证一次，找不到就问用户，不要反复确认或争辩。**

### 0. ⚠️ 文件名对不上 = 可能搞错了文件（2026-07-10 新增）
**问题**：用户说文件夹里只有一张图叫"十八-25上"，但实际文件名是"拾易八字课十八-25 上.png"（前面多了"拾易八字课"）。用户说"你肯定不知道哪里搞来的图片"暗示我可能在看别的文件。
**正确流程**：
1. 先用`search_files`列出文件夹里所有图片文件
2. 用`vision_analyze`确认截屏内容和文件内容是否一致
3. 如果用户说内容对不上，重新用screencapture截屏对比
**不要假设文件名匹配就一定看对了文件。**

### 0. ⚠️ tesseract中文OCR输出充满形近字错误（2026-07-07 新增）
**问题**：tesseract对中文专业术语识别率低，特别是形近字错误。
**真实案例**：
- "肺痨" → "肺许"（形近字）
- "胸闷" → "胸闽"（形近字）
- "逢三冲" → "估三冲"（形近字）
- "墓库逢冲" → "墓库钴冲"（形近字）
- "食神见杀" → "食神见炎"（形近字）
- "比劫争强" → "比动争强"（形近字）
- "若逢岁运" → "着冲岁运"（完全错误）
- "必应手术伤残" → "必应手术伤严"（形近字）
**正确流程**：
1. 用tesseract快速定位**章节边界**（哪个y坐标开始是哪个章节）
2. 用vision_analyze对**关键段落**逐字识别，获取准确文字
3. 对比tesseract输出和vision_analyze输出，**修正所有OCR错误**
4. 将修正后的正确文字写入笔记
**注意**：tesseract的价值在于快速扫描定位，不在于准确识别文字。用它找章节边界，用vision_analyze获取准确内容。

### 0. ⚠️ delegate_task子agent的vision OCR完全不可靠（2026-07-10 新增，2026-07-18 二次验证）
**问题**：用delegate_task派子agent做OCR，每个子agent返回的内容完全不同且互相矛盾。同一张图多次识别返回不同内容（"从格论断" vs "命局中的体用与富贵贫贱" vs "用神四大取法"）。
**根因**：子agent的vision模型幻觉严重，且无法交叉验证。
**正确做法**：不要用delegate_task做OCR。用execute_code直接调用Xiaomi API逐切片OCR，结果更可靠。
**2026-07-18验证**：delegate_task子agent对同一张图返回"从格论断"（幻觉），而Xiaomi API直接调用返回正确的"用神四大取法+婚姻判断"。

### 0. ⚠️ PIL/Pillow可能对PNG返回完全错误的像素数据（2026-07-14 新增，严重，2026-07-14 二次强化）
**问题**：PIL读取PNG文件后，metadata完全正确（尺寸、模式、帧数都对），但渲染出的像素内容是**完全不同的图片**。文件大小、md5、修改时间都一致，但PIL输出的内容和macOS Preview显示的完全不同。
**真实案例**：文件"拾易八字课十八-25 上.png"（2,961,019 bytes, 5025x6705, RGBA），Preview显示"用神四大取法"思维导图，但PIL切片后vision_analyze看到的是"十神详解"表格。反复切片（800px→500px→重新读取）结果一致——PIL一直在读错误的像素数据。sips转换、ffmpeg转换、qlmanage渲染出来的也都是错误内容。
**根因**：未知。可能是PIL的PNG解码器对某些PNG文件处理异常，或文件系统缓存问题。
**⚠️ 关键发现**：当PIL读错时，sips/ffmpeg/qlmanage等所有工具都会输出相同错误内容（共享底层解码器）。唯一可靠的替代方案是用macOS Preview截图。
**⚠️ 强制验证流程**：
1. 切片OCR后，如果内容和用户描述不一致 → **立刻截屏验证**（不要继续重试PIL）
2. 用 `open -a Preview <file>` 打开文件
3. 用AppleScript确保Preview窗口在最前面并显示图片顶部：
```python
subprocess.run(['osascript', '-e', '''
tell application "Preview" to activate
delay 1
tell application "System Events"
    tell application process "Preview" to set frontmost to true
    delay 0.3
    keystroke "3" using {command down}
    delay 0.5
    key code 115
    delay 0.5
end tell
'''])
```
4. 用 `screencapture -x /tmp/screen.png` 截屏
5. 用vision_analyze看截屏中Preview窗口的实际内容
6. **逐段滚动截图OCR**：用 `key code 121`（Page Down）滚动，每页screencapture一次
**⚠️ 绝对禁止**：
- 禁止用sips/ffmpeg/qlmanage"转换格式"来绕过PIL bug——它们也会输出错误内容
- 禁止反复重试PIL切片（换切片高度、重新读取等）——只会浪费时间
- 禁止在发现PIL读错后还继续用PIL——第一次发现就切换到Preview截图方案
**铁律：PIL的metadata正确 ≠ 像素数据正确。发现内容不一致 → 第一次就切换到Preview截图方案，不要再碰PIL。**

### 0. ⚠️ 同一张图多次识别返回不同内容 = vision完全不可信（2026-07-14 新增）
**问题**：对同一张图（拾易八字课十八-25 上.png），第一次全图vision说"十神定义表格"，切9块后逐块看说"十神定义/含义/心性"，切14块后逐块看说"气的运用/食神/伤官/七杀"。同一张图3次识别返回3种不同内容。
**根因**：vision模型在长图上注意力不稳定，每次"看到"的部分不同。
**正确做法**：
1. 如果同一张图多次识别结果不一致 → vision完全不可信
2. 立刻切换到截屏验证（screencapture）或API直接调用
3. 不要再浪费时间用不同参数重试
**铁律：vision返回不一致 = 模型不稳定，不是参数问题。换方案，不要调参数。**

### 0. ⚠️ xiaomi provider的supports_vision_tool_messages=False导致vision_analyze原生路径失败（2026-07-14 源码级根因）
**问题**：vision_analyze对切片后的课件图片返回 `"Image attached natively for the main model"` 而非OCR文字。图片被附加到上下文但模型看不到内容。
**⚠️ 源码级根因（2026-07-14）**：xiaomi provider的ProviderProfile设置了`supports_vision=True`但`supports_vision_tool_messages=False`。`vision_tools.py`的`_supports_media_in_tool_results()`检查的是`profile.supports_vision`而不是`profile.supports_vision_tool_messages`，导致原生fast path被错误启用。
- **飞书发图片** → 挂在user message → xiaomi支持 → ✅
- **browser_vision截屏** → 挂在tool context → xiaomi支持 → ✅  
- **vision_analyze原生路径** → 挂在tool result multimodal envelope → xiaomi**不支持** → ❌

**修复方法（临时workaround）**：设置auxiliary.vision配置强制走辅助LLM路径：
```bash
hermes config set auxiliary.vision.provider xiaomi
hermes config set auxiliary.vision.model mimo-v2.5
```
**原理**：`_explicit_aux_vision_override()`检测到provider不是auto/空→返回True→`decide_image_input_mode`返回"text"→走辅助LLM文本路径→绕开原生path。
**根本修复**：`_supports_media_in_tool_results()`应检查`profile.supports_vision_tool_messages`而非`profile.supports_vision`（需提PR）。
- vision_analyze 的原生快速路径（`_vision_analyze_native`）把图片放在 **tool result** 的 multimodal envelope 里
- mimo-v2.5 能看 **user message** 里的图片（飞书发图、browser_vision截屏都走这条路，所以能用）
- 但 mimo-v2.5 **看不到 tool result 里的图片** → 返回 "Image attached natively" 但模型实际没看到内容
- 设置 auxiliary.vision 配置碰巧改变了路由（`_explicit_aux_vision_override` 返回 True → 强制走辅助 LLM 文本路径），绕开了这个 bug，所以"修好了"——但不是修了配置，是换了路径

**⚠️ 为什么飞书发图能识别但 vision_analyze 不能**：
- 飞书发图 → 平台集成把图片挂在 **user message** 里 → mimo-v2.5 能看 ✅
- browser_vision 截屏 → 图片也挂在 context 里 → mimo-v2.5 能看 ✅
- vision_analyze 原生路径 → 图片挂在 **tool result** 里 → mimo-v2.5 看不到 ❌

**修复/Workaround（按优先级）**：
1. **设置 auxiliary.vision 配置**（改变路由，绕开原生路径）：
```bash
hermes config set auxiliary.vision.provider xiaomi
hermes config set auxiliary.vision.model mimo-v2.5
```
2. **直接调用小米 API**（最可靠，完全绕开 vision_analyze 工具）：
```python
```python
import os, json, base64, urllib.request, io
from PIL import Image

api_key = ''
with open(os.path.expanduser('~/.hermes/.env')) as f:
    for line in f:
        stripped = line.strip()
        if stripped.startswith('XIAOMI_API_KEY') and not stripped.startswith('#'):
            api_key = stripped.split('=', 1)[1].strip()
            break

def encode_pil_image(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'data:image/png;base64,{b64}'

def ocr_slice(img, seg_idx, total):
    data_url = encode_pil_image(img)
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {
        'model': 'mimo-v2.5',
        'messages': [{'role': 'user', 'content': [
            {'type': 'text', 'text': f'这是课件长图的第{seg_idx+1}/{total}段。请完整OCR提取所有文字，保持排版。'},
            {'type': 'image_url', 'image_url': {'url': data_url}},
        ]}],
        'max_tokens': 16000,
        'temperature': 0.1
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request('https://api.xiaomimimo.com/v1/chat/completions', data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        return result['choices'][0]['message']['content']
```
**验证**：如果vision_analyze连续2次返回"Image attached natively"，立即切换到API直接调用。
**注意**：用户原话"你都被切片给vision肯定看不到啊"——不要说vision不行，切换方案即可。

### 0. ⚠️ 用户指出诊断矛盾时不要辩护，立刻深入排查（2026-07-14 新增）
**问题**：vision_analyze返回"Image attached natively"后，我诊断为auxiliary.vision配置为空，设了provider/model后"修复"。但用户指出矛盾："那你截屏mac屏幕的时候识别又没有问题"——browser_vision截屏能识别说明mimo-v2.5本身支持视觉，auxiliary.vision配置不应该影响原生视觉能力。我一开始没意识到这个矛盾，还试图辩解（"可能只是碰巧重试成功了"），直到深入排查才发现真正根因是Hermes源码bug。
**教训**：用户指出逻辑矛盾 = 你的诊断一定有问题。不要辩护，不要说"可能碰巧"，立刻：
1. 承认矛盾存在
2. 检查源码（不是只改配置碰运气）
3. 验证因果链：如果A成立，那B应该也成立——不成立说明A的诊断不对
**铁律：用户追问矛盾 = 必须查源码，不能停在配置层面。**

### 0. ⚠️ vision_analyze返回空结果或异常内容 → 诊断优先级（2026-07-05，2026-07-14 强化，2026-07-14 二次修正）
**问题**：vision_analyze调用成功但返回空analysis、"Image attached natively"、或完全错误的内容。
**⚠️ 根因（2026-07-14 二次修正）**："Image attached natively"不是配置问题，是 mimo-v2.5 不支持 multimodal tool results（见上方 pitfall 0 详细解释）。auxiliary.vision 配置修复碰巧改变了路由绕开了 bug。
**⚠️ 诊断优先级（铁律）**：当vision_analyze返回异常时，**按顺序执行，不准跳步**：
1. **确认症状**：是"Image attached natively"还是空结果还是错误内容？
   - "Image attached natively" → mimo-v2.5 tool result 不支持图片（见 pitfall 0），设 auxiliary.vision 配置或直接调 API
   - 空结果/错误内容 → 继续下一步
2. **查文件**：确认图片文件本身没问题（用screencapture截屏对比，排除PIL读错）
3. **查配置**：auxiliary.vision 配置是否完整（provider/model 不为空）
4. **换方案**：直接调用小米 API 绕开 vision_analyze 工具

### 0. ⚠️ 必须先加载本skill再做任何OCR工作（2026-07-06 用户纠正）
用户原话："你按skill做啊，你看你又没找skill了。一点都不可靠。"在对课件图片做OCR时，直接调用vision_analyze而没有先加载analyze-image skill，导致切片步骤被跳过。**铁律**：任何涉及图片OCR/分析的任务，第一步必须加载analyze-image skill，然后按skill流程执行。不要因为"觉得图片不长"或"先试试"就跳过。

### 1. ⚠️ 不检查尺寸就发vision_analyze = 内容丢失（2026-06-30 再次犯错）
用户多次纠正（2026-06-29和06-30两次）：看到skill里的切片规则但不执行，直接整张长图发vision_analyze，导致丢失50-70%内容。用户原话："你咋每次看完skill都不按skill来切呢"。**强制流程**：`Image.open → .size → h>2000? → 切片 → 逐段识别`。不要因为"看起来不长"或"先试试"就跳过检查。这不是可选步骤，是铁律。

### 1. 长图必须切片
整张发送会丢失50-70%内容。实测：ratio=3.5的图，整张=7.6KB → 切片=22.6KB (+196%)。

### 2. 尺寸用PIL读，不要手动解析文件头
`Image.open(img_path).size` 格式无关。手动解析PNG/JPEG文件头会出错。

### 2.1 ⚠️ RGBA模式图片不能直接保存为JPEG（2026-07-26 新增）
**问题**：PIL读取JPEG图片后返回RGBA模式，直接 `img.save('output.jpg', format='JPEG')` 会报错 `OSError: cannot write mode RGBA as JPEG`。
**原因**：某些JPEG图片（特别是手机拍摄或截图）PIL会以RGBA模式读取。
**修复**：保存前先转换为RGB：
```python
img = Image.open(img_path).convert('RGB')
# 然后再切片保存
seg.save(f'slice_{i}.jpg', quality=90)
```
**铁律**：保存为JPEG前必须 `.convert('RGB')`，保存为PNG则不需要（PNG支持RGBA）。

### 3. 超大图(20M+像素)先缩放
否则MemoryError。总像素>20M就resize。

### 4. write_file会破坏Python引号
写脚本用 `terminal` 的heredoc方式，不要用write_file。写完用 `python -m py_compile` 验证。

### 5. 中文数字匹配按长度降序
"二十二"中的"二"会被单独匹配。先匹配长的：二十五→二十四→...→二→一。

### 7. 批量前先分析源文件夹结构
不要直接跑脚本。先 `ls` 看有什么文件，确认哪些要处理、哪些是副本。

### 9. ⚠️ vision_analyze返回"Image attached natively"而非OCR文字（2026-07-09，2026-07-14 源码级根因）

**同根因于上方 pitfall 0**：xiaomi provider的`supports_vision_tool_messages=False`，`_supports_media_in_tool_results()`误用`supports_vision`判断。修复命令见上方。

**最佳 workaround**：用Xiaomi API直接调用，完全绕开vision_analyze工具：

```python
import json, base64, urllib.request, io
from PIL import Image

api_key = open(os.path.expanduser('~/.hermes/.env')).read().split('XIAOMI_API_KEY=')[1].split('\n')[0].strip()

def encode_pil_image(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'data:image/png;base64,{b64}'

# 切片后逐段调用
for i, seg in enumerate(slices):
    data_url = encode_pil_image(seg)
    payload = {
        'model': 'mimo-v2.5',
        'messages': [{'role': 'user', 'content': [
            {'type': 'text', 'text': '请完整OCR提取这张图片中的所有文字'},
            {'type': 'image_url', 'image_url': {'url': data_url}},
        ]}],
        'max_tokens': 16000, 'temperature': 0.1
    }
    req = urllib.request.Request(
        'https://api.xiaomimimo.com/v1/chat/completions',
        data=json.dumps(payload).encode(),
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    )
    text = json.loads(urllib.request.urlopen(req).read())['choices'][0]['message']['content']
```

**注意**：API端点是 `https://api.xiaomimimo.com/v1`，不是 `https://token-plan-cn.xiaomimimo.com/v1`（后者401）。

### 7. 失败的图片必须主动重试
不要只记日志。提取失败路径，写脚本单独重试。

### ⚠️ 课件图片分类到课程文件夹：看转录稿内容，不看图片上的课次标记（2026-07-21 教训）

**用户原话：「你不要看图片写的课程，你要看我们转录的文字内容」**

课件图片上可能标注了课次（如"拾易八字课二十二-25"），但这个标注**不可靠**——老师可能复制了旧课件模板、图片可能来自其他来源。

**正确流程：**
1. 先用Xiaomi API OCR课件图片，提取主题关键词（如"财运""学历""性爱""天干相合"）
2. 在最近几课的转录稿中 `grep` 这些关键词
3. 按匹配度最高的转录稿归属到对应课程文件夹
4. 不确定的问用户，不要自己猜

**错误做法：**
- ❌ 看图片上写的"二十二课"就直接放到第二十二课文件夹
- ❌ 不看转录稿就分类

**原因：** 课件图片的标注可能是老师复制旧模板时遗留的，实际讲课内容可能在另一课。转录稿是实际讲课的忠实记录，以此为准。

## 参考文档
- `references/batch-processing.md` — 批量处理完整流程
- `references/bazi_knowledge_organization.md` — 八字知识库组织方法
- `references/mimo-vision-tool-result-bug.md` — mimo-v2.5 multimodal tool result 不支持问题的代码级分析
