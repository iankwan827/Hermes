---
name: ecommerce-image
description: 电商产品图生成流程。接收客户参考图，询问平台需求，生成符合要求的产品图。使用MiniMax image-01模型。
version: 2.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [image-generation, ecommerce, product-image, minimax, workflow]
---

# 电商产品图生成 Skill

## 触发条件

用户发送图片并提到以下关键词时触发：
- 电商、产品图、主图、详情图
- 淘宝、京东、拼多多、1688、抖音
- 生图、生成图片、做图、抠图

## 核心原则（铁律）

1. **绝对不用 subject_ref** — MiniMax 的 subject_ref 一定会变形产品
2. **绝对不用 vision_analyze** — Xiaomi Token Plan 上有 api-key header 丢失的已知问题
3. **优先用 Gemini 方案** — 一步到位，主体100%不变，不需要抠图合成
4. **MiniMax 方案必须裁透明区域** — 不裁会导致产品"悬浮"
5. **MiniMax 方案背景不要桌面/家具** — 用纯背景（渐变、纯色、抽象），产品放上去就是主体
5. **优先用 Gemini "banana" 原生图编辑** — 传入原图+prompt，一步换背景，主体不变，效果远超抠图合成

## 工作流（按优先级）

### 方案 A：Gemini 原生图编辑（首选！）

一步到位，传入原图 + prompt，Gemini 保持产品主体不变，只换背景。

```python
import requests, json, os, base64, urllib3
urllib3.disable_warnings()

# 读原图
with open('产品原图.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Gemini 端点（PackyAPI）
url = "https://www.packyapi.com/v1beta/models/gemini-3-pro-image-preview:generateContent"
api_key = os.environ.get('OPENAI_API_KEY')

payload = {
    "contents": [{
        "parts": [
            {"text": "Keep the product exactly as it is, only change the background to <描述>. Do not modify the product at all."},
            {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}}
        ]
    }],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}

r = requests.post(url, json=payload,
                 headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                 verify=False, timeout=120)
result = r.json()

# 提取图片
for c in result.get("candidates", []):
    for p in c.get("content", {}).get("parts", []):
        if "inlineData" in p:
            img_bytes = base64.b64decode(p["inlineData"]["data"])
            with open("output.jpg", "wb") as f:
                f.write(img_bytes)
```

**prompt 要点：**
- 明确说 "Keep the product exactly as it is"
- 说 "Do not modify the product at all"
- 描述想要的背景

**可用模型（PackyAPI）：**
- `gemini-3-pro-image-preview` — 高质量，文字渲染好（推荐）
- `gemini-2.5-flash-image` — 快速，大批量

**优势：** 一步完成，不需要抠图/裁剪/合成/加阴影，主体保真度高

### 方案 B：抠图+纯背景合成（备选）

## 正确工作流（二选一）

收到用户图片后，先问用哪个方案：

### 方案A：Google Gemini（推荐，一步到位）

直接传原图给 Gemini，只换背景，主体不变。不需要抠图、合成。

```bash
PYTHON="E:/Users/Administrator/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe"
"$PYTHON" -c "
import requests, json, os, base64, urllib3
urllib3.disable_warnings()
env_path = os.path.expanduser('~/AppData/Local/hermes/.env')
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()
api_key = os.environ.get('OPENAI_API_KEY', '')
base_url = os.environ.get('OPENAI_BASE_URL', 'https://www.packyapi.com/v1')

# 读原图
with open('<原图路径>', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Gemini 端点
root = base_url.rstrip('/')
if root.endswith('/v1'): root = root[:-3]
url = f'{root}/v1beta/models/gemini-3-pro-image-preview:generateContent'

payload = {
    'contents': [{'parts': [
        {'text': 'Keep the product exactly as it is, only change the background to <背景描述>. Do not modify the product at all.'},
        {'inlineData': {'mimeType': 'image/png', 'data': img_b64}}
    ]}],
    'generationConfig': {'responseModalities': ['TEXT', 'IMAGE']}
}

r = requests.post(url, json=payload,
    headers={'Content-Type': 'application/json', 'x-goog-api-key': api_key},
    verify=False, timeout=120)
result = r.json()
for c in result.get('candidates', []):
    for p in c.get('content', {}).get('parts', []):
        if 'inlineData' in p:
            img_bytes = base64.b64decode(p['inlineData']['data'])
            with open('<输出路径>', 'wb') as f:
                f.write(img_bytes)
            print(f'完成: {<输出路径>} ({len(img_bytes)} bytes)')
"
```

**优势：** 一步到位，主体100%不变，光影融合自然
**劣势：** 需要 PackyAPI Key + 网络能访问 www.packyapi.com
**可用模型：** `gemini-3-pro-image-preview`（高质量）、`gemini-2.5-flash-image`（快速）

### 方案B：MiniMax 抠图合成（备选，网络不通时用）

```
1. MiniMax 纯文生图 → 纯背景（渐变/纯色，不要桌面家具）
2. rembg 抠原图 → 产品透明底图
3. 裁掉透明区域 → 必须！否则悬浮
4. PIL 合成 → 原图产品居中放在纯背景上
```

**优势：** 不依赖 PackyAPI，MiniMax 直连
**劣势：** 步骤多，产品边缘可能不自然，需要调阴影/调色

### 选择建议

| 场景 | 推荐方案 |
|------|---------|
| 网络能访问 packyapi.com | 方案A（Gemini） |
| 网络不通 / 需要批量生成纯背景 | 方案B（MiniMax） |
| 要求主体100%不变 | 方案A（Gemini） |
| 要求文字渲染精确 | 方案A（Gemini） |

## 详细步骤

### Step 1: 生成背景

**核心原则：不要桌面、不要桌子、不要家具等有"着陆面"的元素。** 用纯背景（渐变、纯色、抽象纹理、氛围光），这样产品放上去就是主体展示，不会出现"悬浮在桌面上方"的违和感。

用 `minimax_image.py`（不用 subject_ref）：

```bash
PYTHON="E:/Users/Administrator/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe"
"$PYTHON" "E:/Users/Administrator/AppData/Local/hermes/skills/minimax-image/scripts/minimax_image.py" \
  "<背景描述>" -a 1:1 -o 背景.jpg
```

**推荐背景类型（按优先级）：**

| 类型 | prompt 示例 | 适用场景 |
|------|------------|---------|
| 渐变氛围 | "暖黄色渐变背景，柔和光晕，专业商业摄影灯光" | 通用电商主图 |
| 纯色+光影 | "深棕色纯色背景，顶部一束柔和聚光灯，极简" | 高端产品 |
| 抽象纹理 | "水墨晕染抽象背景，黑白灰色调，东方意境" | 中式/文化产品 |
| 自然元素 | "竹林虚化背景，绿色自然光斑，清新" | 户外/自然风格 |
| 暗调氛围 | "深色背景，微弱暖光从侧面打入，神秘质感" | 奢侈品/酒类 |

**绝对不要生成的背景：**
- ❌ 桌面、茶桌、木桌（产品会悬浮）
- ❌ 房间、书房、客厅（有地面参照物）
- ❌ 任何有"着陆面"的场景（产品没地方放就穿帮）

### Step 2: 抠图去背景

```bash
"$PYTHON" "E:/Users/Administrator/AppData/Local/hermes/skills/minimax-image/scripts/remove_bg.py" \
  输入图.jpg -o 产品抠图.png
```

### Step 3: 裁掉透明区域（必须！）

```python
import numpy as np
from PIL import Image

product_raw = Image.open('产品抠图.png').convert('RGBA')
arr = np.array(product_raw)
alpha = arr[:, :, 3]
rows = np.where(alpha.max(axis=1) > 10)[0]
cols = np.where(alpha.max(axis=0) > 10)[0]
pad = 5
product = product_raw.crop((
    max(0, cols[0] - pad), max(0, rows[0] - pad),
    min(arr.shape[1], cols[-1] + pad), min(arr.shape[0], rows[-1] + pad)
))
```

**为什么要裁：** rembg 输出的图片通常底部有大量透明空间（比如800px高但内容只到653行），不裁掉放上去就是悬浮。

### Step 4: 合成

纯背景下合成更简单，不需要贴桌面阴影，产品居中即可：

```python
from PIL import Image, ImageEnhance

bg = Image.open('背景.jpg').convert('RGBA')

# ① 缩放：占背景 35-45% 高度（纯背景下产品可以大一些）
target_h = int(bg.height * 0.40)
ratio = target_h / product.height
product = product.resize((int(product.width * ratio), target_h), Image.LANCZOS)

# ② 居中放置
x = (bg.width - product.width) // 2
y = (bg.height - product.height) // 2

# ③ 调色匹配背景光（根据背景色调调整）
product_rgb = product.convert('RGB')
product_rgb = ImageEnhance.Brightness(product_rgb).enhance(0.95)
product_rgb = ImageEnhance.Color(product_rgb).enhance(1.05)
product_final = product_rgb.convert('RGBA')
product_final.putalpha(product.split()[3])

# ④ 合成
result = bg.copy()
result.paste(product_final, (x, y), product_final)
result.convert('RGB').save('最终产品图.jpg', quality=95)
```

**如果用户要求有阴影：** 加柔和的中心阴影即可，不需要方向性投影（因为没有桌面参照）：
```python
from PIL import ImageFilter, ImageDraw
shadow = Image.new('RGBA', (product.width + 40, 30), (0, 0, 0, 0))
draw = ImageDraw.Draw(shadow)
draw.ellipse([20, 0, product.width + 20, 25], fill=(0, 0, 0, 40))
shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
result.paste(shadow, (x - 20, y + product.height - 10), shadow)
```

### Step 5: 验证效果

用 analyze_image.py 确认：
```bash
"$PYTHON" "E:/Users/Administrator/AppData/Local/hermes/skills/analyze-image/scripts/analyze_image.py" \
  最终产品图.jpg "简要回答：1.产品有没有悬浮感？2.底部和桌面接触自然吗？3.整体融合度如何？"
```

不通过则调整 y 坐标或阴影参数重新合成。

## 平台风格对照

| 平台 | 风格特点 |
|------|----------|
| 淘宝 | 白底主图，突出产品，800x800 |
| 京东 | 专业摄影，高清细节，品质感 |
| 拼多多 | 清晰展示，性价比氛围 |
| 1688 | 批发商品图，多角度展示 |
| 通用 | 专业商业摄影风格 |

## 多角度生成（3-5张）

用户要求多角度时，每次换不同风格的纯背景，然后分别合成：

```python
scenes = [
    "暖黄色渐变背景，柔和光晕，专业商业摄影灯光",
    "深棕色纯色背景，顶部一束柔和聚光灯，极简",
    "水墨晕染抽象背景，黑白灰色调，东方意境",
    "竹林虚化背景，绿色自然光斑，清新",
    "深色背景，微弱暖光从侧面打入，神秘质感",
]
# 每个背景生成 → 裁剪抠图 → 合成 → 输出
```

## 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 产品变形 | 用了 subject_ref | 用 Gemini banana 原生编辑，或抠图合成 |
| 产品看起来"浮空" | 背景有桌面等参照物 | 用 Gemini 换背景，或换纯色/渐变背景 |
| 产品太突兀 | 色调不匹配 | Gemini 自动匹配；抠图方案调亮度0.95+饱和度1.05 |
| vision_analyze 报错 | api-key header 丢失 | 用 analyze-image skill 的 Python 脚本 |
| PackyAPI SSL 错误 | Clash fake IP 拦截 | 用 www.packyapi.com（不是 api.packyapi.com） |
| Gemini 返回 no image | 模型不在当前分组 | 登录 PackyAPI 控制台切换分组 |

## 技术细节

### PackyAPI 配置（Gemini 生图）
- **正确端点：** `https://www.packyapi.com/v1`（不是 api.packyapi.com）
- **Gemini 原生端点：** `https://www.packyapi.com/v1beta/models/{model}:generateContent`
- **认证：** `x-goog-api-key: <key>`（不是 Authorization: Bearer）
- **环境变量：** `OPENAI_API_KEY` + `OPENAI_BASE_URL=https://www.packyapi.com/v1`
- **插件：** `image_gen/openai` 已改造支持双端点（OpenAI + Gemini）
- **默认模型：** `gemini-3-pro-image-preview`

### MiniMax API（备选）
- 端点: `https://api.minimaxi.com/v1/image_generation`
- 模型: image-01
- 图片 URL 24小时过期，脚本自动下载到本地
- 脚本位于: `minimax-image/scripts/` 目录

### rembg 抠图
- 已安装，模型在 `~/.u2net/`
- Python 路径: `E:/Users/Administrator/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe`

### 替代方案：PackyAPI 接入

PackyAPI 是 OpenAI 兼容的 API 网关（56 个模型），可直接用现有 `image_gen/openai` 插件接入：

```bash
# 设置环境变量
hermes config set env.OPENAI_BASE_URL "https://api.packyapi.com/v1"
hermes config set env.OPENAI_API_KEY "PackyAPI密钥"

# 可用模型：gpt-image-2, gemini-3-pro-image 等
```

**⚠️ Gemini 模型端点差异（重要）：**

| 模型 | 端点 | 认证方式 |
|------|------|----------|
| gpt-image-2 | `/v1/images/generations` | `Authorization: Bearer <key>` |
| gemini-*-image | `/v1beta/models/{model}:generateContent` | `x-goog-api-key: <key>` |

Gemini 模型走 Google 原生端点，请求格式不同：
```json
{
  "contents": [{"parts": [{"text": "prompt"}]}],
  "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}
```
返回 base64 图片在 `inlineData` 字段里。

OpenAI 插件已更新支持 Gemini 模型（v1.1.0），但 PackyAPI 的 Gemini 端点需要确认是否走 OpenAI 兼容格式还是 Google 原生格式。

优势：
- 一个密钥用多个模型（GPT、Gemini、Claude 等）
- gemini-3-pro-image 文字渲染质量可能更好
- 不用写新插件，改 URL 即可

已知问题：
- 代理软件（Clash fake IP 模式）会拦截 `api.packyapi.com` 的 SSL 连接，需加直连规则

## 飞书图片交付

用 `MEDIA:<绝对路径>` 内嵌在回复文本中，gateway 自动上传为原生图片附件。

## 经验教训

- **2026-06-01**: subject_ref 一定会变形产品，不能用于电商图最终交付
- **2026-06-01**: 纯背景（渐变/纯色）比场景图更适合产品展示，不存在悬浮问题
- **2026-06-01**: rembg 输出底部有大量透明区域，必须裁剪
- **2026-06-01**: MiniMax API 不支持 inpainting（局部重绘），无法替换变形区域
- **2026-06-01**: vision_analyze 在 Xiaomi Token Plan 上不可用，必须用 analyze-image skill 的 Python 脚本
- **2026-06-01**: **Gemini "banana" 是最佳方案** — 传入原图+prompt换背景，主体100%不变，一步到位，不需要抠图合成
- **2026-06-01**: PackyAPI Gemini 端点是 `/v1beta/models/{model}:generateContent`，不是 OpenAI 的 `/v1/images/generations`
- **2026-06-01**: PackyAPI base URL 是 `www.packyapi.com` 不是 `api.packyapi.com`

## 相关文件

- `references/packyapi-gemini-integration.md` — PackyAPI Gemini 端点、认证、请求格式完整参考
- `references/minimax_api.md` — MiniMax API 详细文档
- 脚本位置: `minimax-image/scripts/minimax_image.py`（背景生成）
- 脚本位置: `minimax-image/scripts/remove_bg.py`（抠图）/scripts/remove_bg.py`（抠图）
