---
name: ecommerce-image
description: 电商产品图生成流程。接收客户参考图，询问平台需求，生成符合要求的产品图。使用MiniMax image-01模型。
version: 2.0.0
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

1. **绝对不用 subject_ref** — 生成的产品一定会变形，用户明确说过"我不需要生成那个假葫芦"
2. **绝对不用 vision_analyze** — Xiaomi Token Plan 上有 api-key header 丢失的已知问题
3. **抠图必须裁掉透明区域** — 不裁会导致产品"悬浮"
4. **背景不要桌面/家具** — 用纯背景（渐变、纯色、抽象），产品放上去就是主体，不存在悬浮问题

## 正确工作流（唯一做法）

```
1. MiniMax 纯文生图 → 纯背景（渐变/纯色/抽象，不要桌面家具）
2. rembg 抠原图 → 产品透明底图
3. 裁掉透明区域 → 必须！否则悬浮
4. PIL 合成 → 原图产品居中放在纯背景上
```

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
| 产品看起来"浮空" | 背景有桌面等参照物 | 换成渐变/纯色等无参照物的背景 |
| 产品变形 | 用了 subject_ref | 绝对不用 subject_ref |
| 产品太突兀 | 色调不匹配 | 调亮度0.90+饱和度1.05匹配背景光 |
| vision_analyze 报错 | api-key header 丢失 | 用 analyze-image skill 的 Python 脚本 |

## 技术细节

- MiniMax API 端点: `https://api.minimaxi.com/v1/image_generation`
- 模型: image-01
- 图片 URL 24小时过期，脚本自动下载到本地
- 脚本位于: `minimax-image/scripts/` 目录（minimax_image.py, remove_bg.py, ecommerce_image.py）
- rembg 已安装，模型在 `~/.u2net/`
- Python 路径: `E:/Users/Administrator/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe`

## 飞书图片交付

用 `MEDIA:<绝对路径>` 内嵌在回复文本中，gateway 自动上传为原生图片附件。

## 相关文件

- `references/minimax_api.md` - MiniMax API 详细文档
- 脚本位置: `minimax-image/scripts/minimax_image.py`（背景生成）
- 脚本位置: `minimax-image/scripts/remove_bg.py`（抠图）
- 脚本位置: `minimax-image/scripts/ecommerce_image.py`（旧版一键生成，不推荐）
