---
name: feishu-doc-format
description: 飞书文档上传工作流。Markdown→飞书原生文档。核心原则：用upload_notes.py通用脚本，不要重写。
tags: [feishu, document, upload, format]
triggers:
  - "上传飞书文档"
  - "飞书文档格式"
  - "markdown转飞书"
  - "笔记上传飞书"
---

# 飞书文档上传规范

## 上传脚本（唯一入口）

**通用脚本**：`~/Pictures/八字课/scripts/upload_notes.py`

```bash
python3 ~/Pictures/八字课/scripts/upload_notes.py "<标题>" "<markdown文件>"
```

**示例**：
```bash
python3 ~/Pictures/八字课/scripts/upload_notes.py "拾易八字·第二期第一课·完整笔记" ~/Pictures/八字课/第一课/2期第一课_完整笔记_融合版.md
python3 ~/Pictures/八字课/scripts/upload_notes.py "拾易八字·第二三课·完整笔记" ~/Pictures/八字课/第二课/2期第二三课_完整笔记.md
```

**输出**：飞书原生文档（callout分色 + 标题层级 + 表格代码块 + 加粗）

## 脚本特性

- **Callout自动检测**：支持多种格式
  - `### 📋 课件内容` → 蓝色callout
  - `📋 **课件内容**` → 蓝色callout
  - `> 📋 **课件独有**` → 蓝色callout
  - `> **📋 课件独有**` → 蓝色callout
  - `### 🎙️ 讲师解读` → 橙色callout
  - `🎙️ **讲师解读**` → 橙色callout
  - `> 🎙️ 讲师解读` → 橙色callout
- **标题层级**：H1/H2/H3 自动识别
- **表格**：转为代码块（等宽字体对齐）
- **加粗**：`**text**` 识别并应用bold样式

## 核心原则

**没颜色就不合格** — 纯文本block堆砌不可接受。必须有callout分色、标题层级、格式化block。

## 飞书三板斧文件夹
- Token: `G3sFfLWiYlb7Z5dGUAbcNVotnqc`

## Token管理
- Token文件: `~/.hermes/profiles/main/feishu_user_token.json`
- 刷新方法: 见 `feishu-token-refresh` skill
- 401错误 → 先刷新token再重试

## 常见错误
1. **⚠️ 绝对不要重写上传脚本** — `~/Pictures/八字课/scripts/` 下已有完整脚本，直接用。用户原话："你不能用第一课的那个脚本吗"。之前踩过的坑不要重犯。
2. **不要用curl直接调飞书API** — shell引号与markdown `***` 冲突 → 用upload_notes.py
3. **callout必须先创建空容器再添加子block** — 脚本已处理
4. **code block的language必须是整数** — 1=PlainText
5. **原生表格(block_type=20)无法通过API创建** — 用代码块展示
6. **飞书API bullet list用block_type=12不是15** — 15会报invalid param（已验证）
7. **token过期** → 先刷新再调用
8. **第一课和第二课笔记格式不同** — 脚本都支持（📋课件内容/📋课件独有/🎙️讲师解读），不要手动改代码
9. **标题不要写死在脚本里** — 用upload_notes.py命令行参数传入
10. **大文件需要5-10分钟** — 160块 × 0.3秒间隔 + API调用，timeout要设够

## 脚本位置
所有脚本在 `~/Pictures/八字课/scripts/`:
- `upload_notes.py` — **通用上传脚本（推荐）**
- `create_feishu_doc.py` — 旧版脚本（标题写死，不推荐）
- `create_docx.py` — 带样式docx（warm-docs风格）
- `upload_feishu.py` — 文件上传到飞书
