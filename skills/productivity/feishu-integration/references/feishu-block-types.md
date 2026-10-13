# 飞书文档 Block Types 参考

## 已验证可用的Block Types

| Type | 名称 | API字段 | 用途 |
|------|------|---------|------|
| 2 | text | `text` | 段落 |
| 3 | heading1 | `heading1` | 一级标题 |
| 4 | heading2 | `heading2` | 二级标题 |
| 5 | heading3 | `heading3` | 三级标题 |
| 12 | bullet | `bullet` | 无序列表 |
| 13 | ordered | `ordered` | 有序列表 |
| 14 | code | `code` | 代码块 |
| 15 | quote | `quote` | 引用块 |
| 19 | callout | `callout` | 提示块（⚠️背景色API不生效） |
| 22 | divider | `divider` | 分隔线 |

## ⚠️ 已知限制

- **callout background_color**: API返回success但视觉无效果，需用docx方案
- **callout elements**: 创建时必须为空，内容需通过子block更新
- **表格**: API支持但格式有限，复杂表格建议用docx

## 创建文档API端点

```
POST /open-apis/docx/v1/documents                    # 创建文档
POST /open-apis/docx/v1/documents/{id}/blocks/{id}/children  # 添加blocks
PATCH /open-apis/docx/v1/documents/{id}/blocks/{id}  # 更新block
DELETE /open-apis/docx/v1/documents/{id}/blocks/{id}  # 删除block
GET /open-apis/docx/v1/documents/{id}/blocks/{id}/children   # 获取子blocks
```

## 认证

- 用户空间文件夹操作需 `user_access_token`
- 应用空间操作可用 `tenant_access_token`
- Token文件: `/tmp/feishu_user_token.json`
