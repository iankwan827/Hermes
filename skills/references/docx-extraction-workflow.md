# Docx图片提取工作流

## 概述

从飞书/Word转写结果docx文件中提取嵌入图片，通过Xiaomi Vision API识别文字，输出按日期命名的md文件。

## 源文件结构分析（必须先做）

在运行提取脚本前，必须先分析源文件夹结构：

```bash
cd "E:/SD/skill/recording/notes"

# 1. 检查每个日期文件夹的文件类型
for d in */; do
  echo "=== $d ==="
  ls "$d"*.docx 2>/dev/null | head -3
done

# 2. 检查docx内是否有图片
PYTHON="E:\\Users\\Administrator\\AppData\\Roaming\\uv\\python\\cpython-3.11-windows-x86_64-none\\python.exe"
for f in *转写结果.docx; do
  "$PYTHON" -c "
import zipfile
with zipfile.ZipFile('$f') as z:
    c = sum(1 for n in z.namelist() if n.startswith('word/media/') and n.lower().endswith(('.jpg','.jpeg','.png')))
    print(f'$f: {c}张图片')
"
done

# 3. 检查散装图片
for d in */; do
  count=$(find "$d" \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    echo "$d: ${count}张散装图片"
  fi
done
```

## 文件夹分类

根据分析结果，文件夹分为三类：

1. **有docx且有图片**: 直接用 `extract_from_docx.py` 处理
2. **有docx但无图片**: 纯文字稿，不需要图片提取
3. **无docx但有散装图片**: 需要用 `extract_loose_images.py` 批量处理散装图片

**典型场景（2025-12至2026-02录音）**:
- 2025-12-15 到 2026-01-06: 有docx（转写结果），提取后还有散装截图
- 2026-01-07 到 2026-01-21: 只有"原文"docx（无图片），但有散装截图在 `images/` 子目录
- 2026-01-22, 01-26, 02-06: 无docx，只有散装截图
- 2025-12-12, 12-14: 完全空（无docx无图片）

## 提取流程

### Step 1: 处理docx文件

```bash
cd "D:/hermes-agent/imge_v3"
"E:\\Users\\Administrator\\AppData\\Roaming\\uv\\python\\cpython-3.11-windows-x86_64-none\\python.exe" extract_from_docx.py
```

输出: `D:/hermes-agent/imge_v3/docs/` 目录下的md文件

### Step 2: 检查失败项

```bash
grep "FAIL" extract_docx_log.txt
```

如果有FAIL，用 `retry_failed_images.py` 重试：

```bash
"E:\\Users\\Administrator\\AppData\\Roaming\\uv\\python\\cpython-3.11-windows-x86_64-none\\python.exe" \
  scripts/retry_failed_images.py "docx路径" "失败图片索引，逗号分隔"
```

### Step 3: 处理散装图片（如果有）

对于没有docx但有散装图片的文件夹，用 `extract_loose_images.py`：

```bash
cd "D:/hermes-agent/imge_v3"
"E:\\Users\\Administrator\\AppData\\Roaming\\uv\\python\\cpython-3.11-windows-x86_64-none\\python.exe" extract_loose_images.py
```

**注意**: 脚本会自动排除 `extracted/`、`md_images_from_md/`、`_assets/` 目录（这些是docx提取的副本）。

### Step 4: 检查散装图片失败项

```bash
grep "FAIL" extract_loose_log.txt
```

## 常见问题

### 1. 重复文件夹

同一天可能有多个docx文件（如 `extracted/` 子目录中也有）。提取脚本会覆盖同名输出文件。

**解决方案**: 提取前检查是否有重复，决定保留哪个版本。

### 2. 散装图片与docx重复

有些文件夹的散装图片实际上是docx提取时留下的副本（在 `assets/` 或 `extracted/images/` 目录中）。

**检查方法**:
```bash
# 对比docx内图片数 vs assets文件夹图片数
docx_count=$(zipinfo -1 file.docx | grep -c "word/media/")
assets_count=$(ls assets/ 2>/dev/null | wc -l)
echo "docx: $docx_count, assets: $assets_count"
```

如果数量相同，散装图片是重复的，不需要再处理。

### 3. 时间估算

- 每张图片处理时间: 3-10秒（取决于API响应速度）
- 18个文件（约500张图片）: 约2小时
- 不要说"快了"或"十几分钟"，实际时间可能很长

### 4. 失败重试

批量处理中约5-10%的图片可能失败（API超时、大图处理等）。

**必须主动重试**，不要只记日志。用户期望完整交付。

## 配置参数

在 `extract_from_docx.py` 顶部修改：

```python
NOTES_DIR = "E:/SD/skill/recording/notes"  # 源文件夹
OUTPUT_DIR = "D:/hermes-agent/imge_v3/docs"  # 输出目录
SEG_HEIGHT = 1500  # 切割段高
```

## 依赖

- Python 3.11 (uv python)
- Pillow
- Xiaomi Vision API (XIAOMI_API_KEY)
