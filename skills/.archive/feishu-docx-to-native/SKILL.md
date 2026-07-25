---
name: feishu-docx-to-native
description: 将Markdown课程笔记转换为飞书原生文档（含callout高亮块、代码块表格）。输入.md文件，输出飞书文档URL。
category: productivity
---

# Markdown转飞书原生文档

## 核心流程
1. 读取Markdown文件
2. 解析为Feishu blocks（标题、callout、文本、代码块）
3. 创建飞书文档
4. 分批添加blocks

---

## 🚫 关键踩坑（必读）

### 1. Callout块（block_type=19）的语法高亮无法修改
```python
# 创建时的参数
"callout": {
    "background_color": 1,  # 1=浅蓝
    "border_color": 1,
    "emoji_id": "pushpin",
    "code_style": "PlainText"  # ⚠️ 这里只能设置一次
}

# ❌ 后续调用 update_block 无法修改 code_style
# Feishu API不支持修改已创建的callout块的 code_style
```

**结论**：创建callout时就要确定代码块的语法高亮语言，后续无法更改。

### 2. 代码块（block_type=14）不支持"plaintext"语言
```python
# 语法高亮参数
"code": {
    "language": 0,  # ❌ 报错：value not in enum
    "style": 1
}
```

**支持的语言枚举**：
- 1=PlainText → 会转成34=PlainText（UI显示）
- 34=PlainText → 有效值
- 12=CSS → 有效值
- 19=JavaScript → 有效值

**结论**：如果要显示纯文本表格，用语言34（PlainText），不要用1。

### 3. 原生表格（block_type=20）无法通过API创建
cells字段类型验证始终失败，**不要浪费时间尝试**。

**结论**：表格必须通过Markdown导入方案处理。

---

## ⭐ 推荐方案：API逐block创建（支持callout背景色）

### 为什么选这个方案
| 方案 | 表格 | Callout背景色 | 复杂度 |
|------|------|-------------|--------|
| **API逐block创建** ⭐ | ❌ block_type=20始终失败 | ✅ 支持 | 高（逐block循环） |
| ~~Markdown导入~~ | ✅ 原生带边框 | ❌ 无背景色 | 低 |

**结论**：需要callout背景色就必须用API方案。表格用代码块（block_type=14）替代。

---

## 完整流程
Callout块（block_type=19）**不能内联内容**。必须分两步：
1. 创建callout容器 → 获得 `callout_block_id`
2. 往容器里添加子block → 用 `create_child_block(doc_id, callout_block_id, child_blocks)`

```python
# 第1步：创建callout容器
result = create_blocks(doc_id, [{
    "block_type": 19,
    "callout": {"background_color": 3, "border_color": 3, "emoji_id": "pushpin"}
}])
callout_id = result['data']['children'][0]['block_id']

# 第2步：往callout里添加内容（用create_child_block，不是create_blocks）
child_blocks = [
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "第一行"}}]}},
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "第二行"}}]}}
]
create_child_block(doc_id, callout_id, child_blocks)
```

**错误写法**（不会报错但callout为空）：
```python
# ❌ elements不能放在callout里
{"block_type": 19, "callout": {"background_color": 3, "elements": [...]}}
```

### Callout语法高亮（code_style）
创建callout时可设置代码块的语法高亮语言：
```python
# 代码块表格（等宽字体，带背景色）
"callout": {
    "background_color": 3,  # 3=浅黄
    "border_color": 3,
    "emoji_id": "pushpin",
    "code_style": "CSS"  # 或 "PlainText", "JSON", "Python"
}
```

**⚠️ 注意**：`code_style` 只在创建时有效，后续无法修改。

### 代码块（block_type=14）
用于显示表格（等宽字体对齐）：
```python
# ✅ 正确写法（PlainText）
{
    "block_type": 14,
    "code": {
        "language": 34,  # 34=PlainText
        "style": 1
    }
}

# ❌ 错误写法（会报错）
{
    "block_type": 14,
    "code": {
        "language": 1,  # 1=PlainText无效，要用34
        "style": 1
    }
}
```

### Markdown解析顺序
Callout标记检测必须**优先于**普通标题检测，否则 `### 📋 课件内容` 会被当成H3标题：
```python
# ✅ 正确顺序
if line.startswith('### 📋 课件内容'):  # 先检测callout
    ...
elif line.startswith('#'):              # 再检测普通标题
    ...
```

---

## 注意事项
- 每批最多添加10-20个blocks
- 不指定index参数，让API自动追加
- 标题必须用对应的field名（heading1/heading2等），不能用text
- Token字段名是 `access_token`，不是 `user_access_token`

## ⚡ 快速可靠方案：纯文本blocks

当不需要保留格式（callout背景色、代码块语法高亮）时，**全部用text block（block_type=2）最可靠**：
```python
blocks = []
for p in content.split('\n'):
    if p.strip():
        blocks.append({
            "block_type": 2,
            "text": {"elements": [{"text_run": {"content": p}}]}
        })
# 批量写入，每批50个，全部成功
```
实测：609个文本块，13批全部成功。callout/code块偶尔报`invalid param`。

## 参考文件
- `references/feishu-api-notes.md` — API端点、参数格式、已知限制详细笔记
- `scripts/create_feishu_doc.py` — 工作脚本（支持两种方案）