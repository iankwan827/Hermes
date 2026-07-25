---
name: feishu-courseware-upload
description: "课件上传飞书：一键上传markdown/文件到指定文件夹。支持创建文件夹、查找已有文件夹、上传文件。"
tags: ["feishu", "upload", "courseware", "cloud-drive"]
triggers:
  - "上传课件到飞书"
  - "飞书上传"
  - "课件上传"
---

# 课件上传飞书

## 快速启动

```python
import json, subprocess, os

def upload_to_feishu(file_path, folder_name="八字", subfolder=None):
    """
    上传文件到飞书指定文件夹
    """
    # 1. 获取token
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"app_id": app_id, "app_secret": app_secret})
    ], capture_output=True, text=True)
    token = json.loads(result.stdout)["tenant_access_token"]
    
    # 2. 查找或创建文件夹
    folder_token = find_or_create_folder(token, folder_name)
    if subfolder:
        folder_token = find_or_create_folder(token, subfolder, parent_token=folder_token)
    
    # 3. 上传文件
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
        "-H", "Authorization: Bearer " + token,
        "-F", f"file_name={file_name}",
        "-F", "parent_type=explorer",
        "-F", f"parent_node={folder_token}",
        "-F", f"size={file_size}",
        "-F", f"file=@{file_path}"
    ], capture_output=True, text=True)
    
    resp = json.loads(result.stdout)
    if resp.get("code") == 0:
        print(f"✅ 上传成功: {file_name}")
        return resp["data"]["file_token"]
    else:
        print(f"❌ 上传失败: {resp}")
        return None

def find_or_create_folder(token, folder_name, parent_token=""):
    """查找或创建文件夹"""
    result = subprocess.run([
        "curl", "-s",
        f"https://open.feishu.cn/open-apis/drive/v1/files?folder_token={parent_token}&page_size=50",
        "-H", "Authorization: Bearer " + token
    ], capture_output=True, text=True)
    files = json.loads(result.stdout)["data"]["files"]
    
    for f in files:
        if f["name"] == folder_name and f["type"] == "folder":
            return f["token"]
    
    # 不存在则创建
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/drive/v1/files/create_folder",
        "-H", "Authorization: Bearer " + token,
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"name": folder_name, "folder_token": parent_token})
    ], capture_output=True, text=True)
    return json.loads(result.stdout)["data"]["token"]
```

## 一键上传课件

```python
def upload_courseware(file_path, course_name="八字课"):
    """一键上传课件到飞书"""
    return upload_to_feishu(file_path, folder_name=course_name)
```

## 文件组织规范

```
~/Pictures/八字课/
├── scripts/                    # 可复用脚本
│   ├── create_docx.py         # 生成Word文档
│   └── upload_feishu.py       # 上传飞书
├── 第一课/                     # 每课一个文件夹
│   ├── *.png/jpg              # 课件图片
│   ├── 拾易*.md               # OCR课件
│   ├── *.mp3                  # 录音
│   ├── *_文字稿.md            # Whisper输出
│   ├── *_完整笔记.md          # 最终笔记
│   └── *_完整笔记.docx        # Word文档(上传用)
├── 语录/                       # 独立文件夹，每天更新
│   ├── 理华老师语录.pdf
│   └── 理华老师语录.md
└── 第N课/
```

**上传格式：** 优先用.docx（Word文档），飞书桌面版可下载查看，手机版可直接预览。HTML和飞书原生文档API不支持背景色样式。

## 创建带样式的飞书文档（API方式）

飞书文档支持通过API创建富文本块，实现类似参考文档的排版效果：

### Block Types（已验证可用）

| Type | 名称 | 用途 |
|------|------|------|
| 2 | text | 段落 |
| 3 | heading1 | 一级标题 |
| 4 | heading2 | 二级标题 |
| 5 | heading3 | 三级标题 |
| 12 | bullet | 无序列表 |
| 13 | ordered | 有序列表 |
| 14 | code | 代码块 |
| 15 | quote | 引用块 |
| 19 | callout | 提示块（浅色背景+emoji） |
| 22 | divider | 分隔线 |

### 创建文档流程

```python
# 1. 创建文档
result = curl_post('/open-apis/docx/v1/documents', {
    'title': '文档标题',
    'folder_token': '目标文件夹token'
})
doc_id = result['data']['document']['document_id']

# 2. 写入blocks
def te(content, bold=False):
    el = {"text_run": {"content": content, "text_element_style": {}}}
    if bold:
        el["text_run"]["text_element_style"]["bold"] = True
    return el

blocks = [
    {"block_type": 3, "heading1": {"elements": [te("大标题", bold=True)]}},
    {"block_type": 4, "heading2": {"elements": [te("章节标题", bold=True)]}},
    {"block_type": 19, "callout": {"elements": [te("🎤 讲师解读")]}} ,
    {"block_type": 22, "divider": {}},
    {"block_type": 2, "text": {"elements": [te("正文内容")]}}
]

curl_post(f'/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children', {
    "children": blocks
})
```

### Callout块样式参考

参考文档：https://forchangesz.feishu.cn/wiki/KagHwwL5ditT9ykLIcEcRSEfnfe
- 浅色背景 + emoji装饰
- 加粗标题 + 内容
- 适合讲师解读、重点提示

### ⚠️ Callout背景色 (background_color) — API不生效！

飞书API的callout `background_color` 参数**返回success但实际不生效**，视觉上无任何效果。这是飞书API的已知限制。

**解决方案：用Word docx格式**

生成带样式的 `.docx` 文件（python-docx），上传到飞书后样式保留：

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# 添加带背景色的段落
p = doc.add_paragraph()
pPr = p._element.get_or_add_pPr()
shd = OxmlElement('w:shd')
shd.set(qn('w:val'), 'clear')
shd.set(qn('w:color'), 'auto')
shd.set(qn('w:fill'), 'E8F4FD')  # 浅蓝 hex
pPr.append(shd)

# 添加左边框
pBdr = OxmlElement('w:pBdr')
left = OxmlElement('w:left')
left.set(qn('w:val'), 'single')
left.set(qn('w:sz'), '12')
left.set(qn('w:space'), '4')
left.set(qn('w:color'), 'E67E22')  # 橙色边框
pBdr.append(left)
pPr.append(pBdr)

run = p.add_run("内容文本")
doc.save('output.docx')
```

常用背景色hex：
- 浅蓝 `E8F4FD` — 课件内容
- 浅橙 `FDF2E9` — 讲师解读
- 浅绿 `E8F8E8` — 重点提示
- 浅黄 `FFF9E6` — 注意事项

### Callout块内容写入流程

callout创建时elements必须为空，内容需单独写入子block：

```python
# 1. 创建空callout
bid = add_block({"block_type": 19, "callout": {"elements": []}})

# 2. 获取子block ID
r = curl_get(f'/docx/v1/documents/{doc_id}/blocks/{bid}')
child_id = r['data']['block']['children'][0]

# 3. 用 update_text_elements 更新内容（不是 replace_text！）
curl_patch(f'/docx/v1/documents/{doc_id}/blocks/{child_id}', {
    "update_text_elements": {
        "elements": [{"text_run": {"content": "内容", "text_element_style": {}}}]
    }
})
```

## ⚠️ Pitfalls

### Shell引号与markdown解析

terminal/execute_code 工具会将 `***` 解析为 markdown 粗斜体，导致 Authorization header 被截断。

**解决方案**：把Python脚本写到文件再执行，避免内联字符串中的特殊字符。

```python
# 写脚本到文件
write_file(path="upload.py", content='''import json, subprocess, os
with open('/tmp/feishu_user_token.json') as f:
    token = json.load(f)['access_token']
sp = ' '
header = 'Authorization:' + sp + 'Bearer' + sp + token
# ... 使用 header 发请求
''')
# 再执行
terminal("python3 upload.py")
```

### OAuth重新授权流程

当应用添加新权限（如docx:document:create）后，已有token不包含新scope，需要用户重新授权：

1. 在飞书开发者后台 → 安全设置 → 重定向URL，添加 `http://localhost:8765`
2. 启动本地服务器接收回调
3. 用户点击授权链接
4. 用返回的code换新token

```python
# 授权链接
auth_url = f'https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={app_id}&redirect_uri=http%3A%2F%2Flocalhost%3A8765&scope={scopes}'

# 用code换token（用app_access_token，不是tenant_access_token）
app_token = get_app_access_token()  # /auth/v3/app_access_token/internal
result = curl_post('/open-apis/authen/v1/oidc/access_token', {
    'grant_type': 'authorization_code',
    'code': auth_code
}, header=f'Authorization: Bearer *** + app_token)
```

### Token过期自动刷新

user_access_token 有效期2小时，过期后需刷新。刷新流程：

```python
def refresh_user_token():
    # 1. 获取app_access_token
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"app_id": app_id, "app_secret": app_secret})
    ], capture_output=True, text=True)
    app_token = json.loads(result.stdout)["app_access_token"]
    
    # 2. 用refresh_token换新token
    with open('/tmp/feishu_user_token.json') as f:
        token_data = json.load(f)
    
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token",
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Bearer *** + app_token,
        "-d", json.dumps({
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"]
        })
    ], capture_output=True, text=True)
    
    resp = json.loads(result.stdout)
    if resp.get("code") == 0:
        token_data["access_token"] = resp["data"]["access_token"]
        token_data["refresh_token"] = resp["data"]["refresh_token"]
        with open('/tmp/feishu_user_token.json', 'w') as f:
            json.dump(token_data, f)
        return resp["data"]["access_token"]
```

### 上传前先让用户确认

用户偏好：**先看内容再决定是否上传飞书**。不要自动上传，等用户确认后再执行。

## 注意事项

- 文件大小限制：单文件最大20MB
- 环境变量：FEISHU_APP_ID, FEISHU_APP_SECRET
- folder_token为空字符串表示根目录
- 飞书API创建文档需要 docx:document:create 权限，当前应用未配置
- 参考样式来源：`wechat_editor` 仓库（https://github.com/littleben/wechat_editor），styles.js里有19种排版风格（但粘贴到飞书不保留）
