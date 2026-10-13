# Feishu API 读取文档

## 获取 Tenant Access Token

```python
import json, subprocess, os

app_id = os.environ.get("FEISHU_APP_ID")
app_secret = os.environ.get("FEISHU_APP_SECRET")

result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    "-H", "Content-Type: application/json",
    "-d", json.dumps({"app_id": app_id, "app_secret": app_secret})
], capture_output=True, text=True)
tenant_token = json.loads(result.stdout)["tenant_access_token"]
```

## 读取 Wiki 文档（两步）

Wiki token ≠ 文档 token，需要先查节点获取实际 doc_token：

```python
# 1. 获取 wiki 节点信息
wiki_token = "KagHwwL5ditT9ykLIcEcRSEfnfe"  # URL 中的 token
result = subprocess.run([
    "curl", "-s",
    f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={wiki_token}",
    "-H", "Authorization: Bearer " + tenant_token
], capture_output=True, text=True)
wiki_data = json.loads(result.stdout)
obj_token = wiki_data["data"]["node"]["obj_token"]  # 实际文档 token

# 2. 读取文档内容
result = subprocess.run([
    "curl", "-s",
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{obj_token}/raw_content",
    "-H", "Authorization: Bearer " + tenant_token
], capture_output=True, text=True)
doc_data = json.loads(result.stdout)
content = doc_data["data"]["content"]
```

## 常见错误

1. **feishu_doc_read 失败**：提示 "not in a Feishu comment context"，需要用 API 直接读
2. **Wiki token 和 doc token 不同**：必须先查 wiki 节点获取 obj_token
3. **Shell 引号问题**：Python 中构建 curl 命令时，Authorization header 用字符串拼接 `"Authorization: Bearer " + token`
