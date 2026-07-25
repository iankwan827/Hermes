# 飞书API详细笔记

## Markdown导入API

### 端点
- 上传: `POST /drive/v1/files/upload_all` (multipart/form-data)
- 导入: `POST /drive/v1/import_tasks`
- 查询: `GET /drive/v1/import_tasks/{ticket}`

### 上传参数
```
file_name: string (文件名)
parent_type: "explorer"
parent_node: string (文件夹token)
size: int (文件大小)
file: binary (文件内容)
```

### 导入参数
```json
{
    "file_extension": "md",
    "file_token": "上传返回的token",
    "type": "docx",
    "file_name": "文档标题",
    "point": {
        "mount_type": 1,
        "mount_key": "文件夹token"
    }
}
```

### 导入响应
```json
{
    "code": 0,
    "data": {
        "ticket": "任务ID"
    }
}
```

### 查询响应（成功）
```json
{
    "code": 0,
    "data": {
        "result": {
            "job_status": 0,
            "token": "文档ID",
            "type": "docx",
            "url": "https://xxx.feishu.cn/docx/xxx"
        }
    }
}
```

## 已知API限制

### block_type=20 (表格) - 不可用
- cells字段类型验证始终失败
- 尝试过的格式：字符串数组、嵌套block数组、二维数组
- 错误信息：`Invalid parameter type in json: cells`
- **结论**：必须用markdown导入方案

### block_type=19 (Callout) - 可用但需嵌套
- 是容器块，不能内联内容
- 必须先创建容器，再用create_child_block添加子block
- 颜色编号：bg=3/border=3→浅蓝灰，bg=5/border=5→浅橙黄

### block_type=14 (Code) - 可用
- 用于等宽字体显示（如代码、对齐的文本表格）
- language=1 为PlainText

## Token管理
- 文件：`~/.hermes/profiles/main/feishu_user_token.json`
- 字段名：`access_token`（不是`user_access_token`）
- 刷新：用refresh_token + app_secret调用 `/authen/v1/oidc/refresh_access_token`
- App ID: `cli_aa933b5e9ef85cd2`
- App Secret: `/tmp/feishu_app_secret.txt`
