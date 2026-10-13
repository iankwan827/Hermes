# upload_notes.py 脚本文档

## 位置
`~/Pictures/八字课/scripts/upload_notes.py`

## 功能
将带📋/🎙️标记的markdown上传到飞书文档，创建彩色callout块。

## 解析逻辑（2026-07-24更新）

### Day标题处理
- 遇到`## DayN` → 创建heading block + 收集该Day下所有内容 → 创建**一个**callout块
- callout颜色由Day内容中的📋/🎙️标记决定

### Callout内容提取
- 📋标记行：提取行内内容（去除📋标记，保留`**1.**`等编号）
- 🎙️标记行：提取行内内容（去除🎙️标记，保留编号）
- 后续行：持续收集直到遇到下一个`## Day`标题

### 输出结构
```
## Day1          ← heading block (block_type=4)
📋 **1.**        ← callout_blue开始
食伤女发脾气...
📋 **2.**
甲木女一般...

## Day2          ← heading block
🎙️ **1.**        ← callout_orange开始
地支代表过程...
```

## 使用方法
```bash
python3 ~/Pictures/八字课/scripts/upload_notes.py "文档标题" markdown文件.md
```

## Token刷新
脚本自动处理token刷新（检测99991668错误时自动refresh）。

## 已知限制
- 大文件（3000+行）可能超时（>600秒），需后台运行
- callout内不支持heading block，所有标题转为加粗文本

## Bug修复记录
- **2026-07-24**：修复📋内联内容提取bug（旧版跳过`📋 **1.**`中的`**1.**`）
- **2026-07-24**：重构parse_md函数，每个Day一个callout块（旧版每个编号一个块）
