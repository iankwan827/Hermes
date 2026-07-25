---
name: feishu-drive
description: "飞书云盘API操作：创建文件夹、上传文件。通过curl调用open.feishu.cn API实现，无需额外SDK。"
tags: ["feishu", "lark", "cloud-drive", "upload"]
triggers:
  - "飞书云盘"
  - "上传到飞书"
  - "飞书文件夹"
  - "feishu drive"
---

# 飞书云盘文件管理

## 前置条件

环境变量已配置：
- `FEISHU_APP_ID` — 飞书应用ID
- `FEISHU_APP_SECRET` — 飞书应用密钥
- `FEISHU_DOMAIN` — feishu 或 lark

所需权限（飞书开放平台）：
- `drive:drive` — 云盘读写

## 获取 Tenant Access Token

```python
import json, subprocess, os

app_id = os.environ["FEISHU_APP_ID"]
app_secret = os.environ["FEISHU_APP_SECRET"]

result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    "-H", "Content-Type: application/json",
    "-d", json.dumps({"app_id": app_id, "app_secret": app_secret})
], capture_output=True, text=True)
token = json.loads(result.stdout)["tenant_access_token"]
```

## 创建文件夹

```python
# 在根目录创建文件夹
result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "https://open.feishu.cn/open-apis/drive/v1/files/create_folder",
    "-H", "Authorization: Bearer *** + token,
    "-H", "Content-Type: application/json",
    "-d", json.dumps({"name": "文件夹名", "folder_token": ""})
], capture_output=True, text=True)
folder_token = json.loads(result.stdout)["data"]["token"]

# 在指定文件夹下创建子文件夹
# 将 folder_token 改为目标父文件夹的token
```

## 列出文件夹内容

```python
result = subprocess.run([
    "curl", "-s",
    f"https://open.feishu.cn/open-apis/drive/v1/files?folder_token={folder_token}&page_size=50",
    "-H", "Authorization: Bearer *** + token
], capture_output=True, text=True)
files = json.loads(result.stdout)["data"]["files"]
for f in files:
    print(f"{f['type']}: {f['name']} ({f['token']})")
```

## 上传文件

```python
file_path = "/path/to/file.md"
file_name = os.path.basename(file_path)
file_size = os.path.getsize(file_path)

result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
    "-H", "Authorization: Bearer *** + token,
    "-F", f"file_name={file_name}",
    "-F", "parent_type=explorer",
    "-F", f"parent_node={folder_token}",
    "-F", f"size={file_size}",
    "-F", f"file=@{file_path}"
], capture_output=True, text=True)
file_token = json.loads(result.stdout)["data"]["file_token"]
```

**限制**：`upload_all` 单文件最大 20MB。超过需用分片上传。

## 完整示例：课件上传

```python
import json, subprocess, os

# 1. 获取token
app_id = os.environ["FEISHU_APP_ID"]
app_secret = os.environ["FEISHU_APP_SECRET"]
result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    "-H", "Content-Type: application/json",
    "-d", json.dumps({"app_id": app_id, "app_secret": app_secret})
], capture_output=True, text=True)
token = json.loads(result.stdout)["tenant_access_token"]

# 2. 创建/找到目标文件夹
folder_name = "八字"
# 先列出根目录找是否已存在
result = subprocess.run([
    "curl", "-s",
    "https://open.feishu.cn/open-apis/drive/v1/files?folder_token=&page_size=50",
    "-H", "Authorization: Bearer *** + token
], capture_output=True, text=True)
files = json.loads(result.stdout)["data"]["files"]
folder_token = None
for f in files:
    if f["name"] == folder_name and f["type"] == "folder":
        folder_token = f["token"]
        break

# 不存在则创建
if not folder_token:
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/drive/v1/files/create_folder",
        "-H", "Authorization: Bearer *** + token,
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"name": folder_name, "folder_token": ""})
    ], capture_output=True, text=True)
    folder_token = json.loads(result.stdout)["data"]["token"]

# 3. 上传文件
file_path = "/Users/guanmian/Pictures/八字课/拾易八字第一节课.md"
file_name = os.path.basename(file_path)
file_size = os.path.getsize(file_path)

result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
    "-H", "Authorization: Bearer *** + token,
    "-F", f"file_name={file_name}",
    "-F", "parent_type=explorer",
    "-F", f"parent_node={folder_token}",
    "-F", f"size={file_size}",
    "-F", f"file=@{file_path}"
], capture_output=True, text=True)
print(f"上传结果: {json.loads(result.stdout)}")
```

## 创建电子表格

```python
import json, urllib.request, csv

with open('/Users/guanmian/.hermes/profiles/main/feishu_user_token.json') as f:
    token = json.load(f)["access_token"]

folder_token = "G3sFfLWiYlb7Z5dGUAbcNVotnqc"  # 目标文件夹

# 1. 创建电子表格
create_body = json.dumps({
    "title": "表格标题",
    "folder_token": folder_token
}).encode()
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets",
    data=create_body,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
result = json.loads(urllib.request.urlopen(req).read())
spreadsheet_token = result["data"]["spreadsheet"]["spreadsheet_token"]
url = result["data"]["spreadsheet"]["url"]

# 2. 获取默认Sheet ID并重命名
req2 = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query",
    headers={"Authorization": f"Bearer {token}"}
)
sheets = json.loads(urllib.request.urlopen(req2).read())["data"]["sheets"]
sheet_id = sheets[0]["sheet_id"]

rename_body = json.dumps({"requests": [{"updateSheet": {"properties": {"sheetId": sheet_id, "title": "Sheet1"}}}]}).encode()
req3 = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update",
    data=rename_body,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
urllib.request.urlopen(req3)

# 3. 写入数据（CSV转二维数组）
with open("data.csv", "r", encoding="utf-8-sig") as f:
    rows = list(csv.reader(f))

write_body = json.dumps({"valueRange": {"range": f"{sheet_id}!A1:{chr(64+len(rows[0]))}{len(rows)}", "values": rows}}).encode()
req4 = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values",
    data=write_body,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="PUT"
)
urllib.request.urlopen(req4)

# 4. 添加新Sheet（可选）
add_body = json.dumps({"requests": [{"addSheet": {"properties": {"title": "Sheet2", "index": 1}}}]}).encode()
req5 = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update",
    data=add_body,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
add_result = json.loads(urllib.request.urlopen(req5).read())
new_sheet_id = add_result["data"]["replies"][0]["addSheet"]["properties"]["sheetId"]
```

**注意**：
- 创建表格用 **user_access_token**（不是 tenant_token）
- CSV读取必须 `encoding='utf-8-sig'` 处理BOM头
- 写入数据范围格式：`{sheet_id}!A1:{列}{行}`（如 `A1:L21`）
- 添加Sheet后返回的 `sheetId` 可用于后续写入

## 刷新 User Access Token

user_access_token 有效期短（2小时），refresh_token 有效期30天。过期后用 refresh_token 续期：

```python
import json, urllib.request

# 1. 先获取 tenant_access_token
app_id = os.environ["FEISHU_APP_ID"]
app_secret = os.environ["FEISHU_APP_SECRET"]
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
    headers={"Content-Type": "application/json"}
)
tenant = json.loads(urllib.request.urlopen(req).read())
tenant_token = tenant["tenant_access_token"]

# 2. 用 refresh_token 刷新 user_access_token
with open(os.path.expanduser("~/.hermes/profiles/main/feishu_user_token.json")) as f:
    d = json.load(f)

req2 = urllib.request.Request(
    "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token",
    data=json.dumps({
        "grant_type": "refresh_token",
        "refresh_token": d["refresh_token"]
    }).encode(),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {tenant_token}"  # 注意：这里用tenant_token
    }
)
result = json.loads(urllib.request.urlopen(req2).read())
if result["code"] == 0:
    d["access_token"] = result["data"]["access_token"]
    d["refresh_token"] = result["data"]["refresh_token"]  # 新的refresh_token也存回去
    with open(os.path.expanduser("~/.hermes/profiles/main/feishu_user_token.json"), "w") as f:
        json.dump(d, f, indent=2)
```

**关键点**：refresh_access_token 接口用 **tenant_token** 做 Authorization（不是 user_token），传 user 的 refresh_token 做 body。刷新后新 refresh_token 也要存回文件。

## 读取Wiki文档内容

`feishu_doc_read` 在非评论上下文中不可用。替代方案：通过tenant_access_token调用API。

```python
# 1. 获取tenant_access_token（同上）

# 2. 获取wiki节点信息（找到实际doc_token）
wiki_token = "KagHwwL5ditT9ykLIcEcRSEfnfe"  # URL中的token
result = subprocess.run([
    "curl", "-s",
    f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={wiki_token}",
    "-H", "Authorization: Bearer " + tenant_token
], capture_output=True, text=True)
node_data = json.loads(result.stdout)
obj_token = node_data["data"]["node"]["obj_token"]  # 实际文档token

# 3. 读取文档内容
result = subprocess.run([
    "curl", "-s",
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{obj_token}/raw_content",
    "-H", "Authorization: Bearer " + tenant_token
], capture_output=True, text=True)
content = json.loads(result.stdout)["data"]["content"]
```

**注意：** Wiki URL中的token是node_token，需要先转换为obj_token才能读取内容。

## Pitfalls

1. **Shell引号问题**：在Python中构建curl命令时，Authorization header要用字符串拼接而非f-string（避免引号嵌套报错）
2. **file=@路径**：必须是绝对路径，相对路径可能找不到文件
3. **file_size**：必须精确匹配文件大小（字节），否则上传会失败
4. **folder_token为空**：表示根目录，不是null
5. **curl输出编码**：飞书API返回JSON，确保用`text=True`接收后json.loads解析
6. **环境变量**：FEISHU_APP_SECRET可能被shell截断，用`os.environ.get()`获取更安全
7. **user_access_token过期快**：OAuth token有效期短，过期后返回`code: 99991661`。云盘操作优先用tenant_access_token（通过app_id+app_secret获取），不需要用户授权，永不过期。
8. **tenant vs user token**：drive文件操作（上传/创建文件夹）用tenant_token即可；doc读写需要user_token。不要混用。
9. **电子表格需要user_access_token**：创建/写入飞书电子表格（sheets API）需要user_access_token，tenant_token不够。如果token过期，先用feishu-oauth流程刷新。
10. **CSV有BOM头**：读取飞书下载的CSV或Excel导出的CSV时，必须用 `encoding='utf-8-sig'`，否则第一列列名带 `﻿` 前缀导致KeyError。
11. **查找已有文件**：用户可能之前已创建过表格/上传过文件。不要直接说"没有"——先用 `session_search` 搜历史记录（包括被压缩的旧session），再用API列出文件夹内容，最后才下结论。
