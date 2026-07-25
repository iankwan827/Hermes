# 飞书Docx API参考

## 创建块（添加内容）

**端点**: `POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children`

**Content-Type**: `application/json; charset=utf-8`

### 文本块 (block_type=2)
```json
{
  "block_type": 2,
  "text": {
    "elements": [
      {
        "text_run": {
          "content": "文本内容",
          "text_element_style": {
            "bold": true,
            "background_color": 5,
            "text_color": 1
          }
        }
      }
    ]
  }
}
```

### 高亮块/Callout (block_type=19) — ⚠️ 容器块！

Callout是**容器块**，不能内联内容。必须分两步：

**第1步：创建callout容器**
```json
{
  "block_type": 19,
  "callout": {
    "background_color": 3,
    "border_color": 3,
    "emoji_id": "pushpin"
  }
}
```

**第2步：往容器里添加子block**
```
POST /open-apis/docx/v1/documents/{doc_id}/blocks/{callout_block_id}/children
```
```json
{
  "children": [
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "第一行"}}]}},
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "第二行"}}]}}
  ]
}
```

**❌ 错误写法**（不会报错但callout为空）：
```json
{"block_type": 19, "callout": {"background_color": 3, "elements": [...]}}
```

**background_color 可选值** (实测结果):
- 3: 浅蓝灰色（实际渲染，非文档描述的浅黄色）
- 5: 浅橙黄色（实际渲染，非文档描述的浅蓝色）
- 其他值待测试

**border_color 可选值**: 同上

**emoji_id 常用值**: pushpin, speech_balloon, star, check, warning, info

### 标题块 (block_type=3~11)
- 3: H1 → field: `heading1`
- 4: H2 → field: `heading2`
- 5: H3 → field: `heading3`
- 每个level有独立field名，不能用 `text` 代替

### 其他块类型
- 12: 无序列表, 13: 有序列表
- 14: 代码块, 15: 引用
- 17: 待办事项, 22: 分割线
- 20: 表格（⚠️ 无法通过API创建，只能用纯文本模拟）

## 获取文档块列表

**端点**: `GET /open-apis/docx/v1/documents/{document_id}/blocks`**

## 删除文档

**端点**: `DELETE /open-apis/drive/v1/files/{file_token}?type=docx`

## Token注意

- Token字段名是 `access_token`（不是 `user_access_token`）
- Token文件: `~/.hermes/profiles/main/feishu_user_token.json`

## 常见错误

- **1770001 invalid param**: 字段名错误。文本块用`text`不是`paragraph`；标题用`heading1`/`heading2`等
- **400 Bad Request**: Content-Type必须是`application/json; charset=utf-8`
- **20004**: 授权码已过期，需要重新授权
- **20014**: Refresh token已过期，需要重新走OAuth流程
- **Callout为空**: 没有用 `create_child_block` 往容器里添加子block
