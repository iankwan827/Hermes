---
name: feishu-oauth
description: 飞书OAuth授权流程：获取/刷新user_access_token，固定端口8765，自动保存token到~/.hermes/profiles/main/feishu_user_token.json
category: productivity
---

# 飞书OAuth授权流程

## 前置条件
- App ID: `cli_aa933b5e9ef85cd2`
- App Secret: 存储在 `/tmp/feishu_app_secret.txt`（首次运行需从开发者后台获取并保存）
- 重定向URL: `http://localhost:8765`（已在飞书应用后台配置）
- 固定端口: **8765**（不要用其他端口）

## 流程

### 1. 检查现有token
```bash
python3 -c "import json; d=json.load(open('/Users/guanmian/.hermes/profiles/main/feishu_user_token.json')); print('access:', d.get('access_token','')[:20]); print('refresh:', d.get('refresh_token','')[:20])"
```

### 2. 尝试刷新token（如果access_token过期）

**⚠️ 关键：OIDC刷新端点需要 `tenant_access_token` 作为 Bearer，不是 app_id/app_secret 放在 body 里。**

```python
import json, urllib.request

with open('/Users/guanmian/.hermes/profiles/main/feishu_user_token.json') as f:
    token_data = json.load(f)

APP_ID = "cli_aa933b5e9ef85cd2"
# app_secret 优先从环境变量取，备选从文件取
import os
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
if not APP_SECRET:
    try:
        with open('/tmp/feishu_app_secret.txt') as f:
            APP_SECRET = f.read().strip()
    except FileNotFoundError:
        raise RuntimeError("需要 FEISHU_APP_SECRET 环境变量或 /tmp/feishu_app_secret.txt 文件")

# Step 1: 获取 tenant_access_token
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
tenant = json.loads(urllib.request.urlopen(req).read())
tenant_token = tenant.get("tenant_access_token", "")
if not tenant_token:
    raise RuntimeError(f"获取 tenant_token 失败: {tenant}")

# Step 2: 用 tenant_token 作为 Bearer 刷新 user_access_token
data = json.dumps({
    "grant_type": "refresh_token",
    "refresh_token": token_data["refresh_token"]
}).encode()

req2 = urllib.request.Request(
    "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token",
    data=data,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {tenant_token}"
    }
)
resp = json.loads(urllib.request.urlopen(req2).read())
if resp.get("code") == 0:
    new_data = resp["data"]
    token_data["access_token"] = new_data["access_token"]
    token_data["refresh_token"] = new_data["refresh_token"]  # refresh也会更新
    with open('/Users/guanmian/.hermes/profiles/main/feishu_user_token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    print("Token refreshed!")
else:
    print(f"Refresh failed: {resp.get('msg')} (code={resp.get('code')})")
    print("需要重新走授权流程")
```

**注意**：refresh_token 也会更新，必须同时保存新的 access_token 和 refresh_token。

### 3. 如果refresh失败，重新授权
```bash
# 启动OAuth服务器（后台运行）
python3 -c "
import http.server, urllib.parse, threading
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        code = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('code',[''])[0]
        if code:
            open('/tmp/feishu_auth_code.txt','w').write(code)
            self.send_response(200)
            self.send_header('Content-type','text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write('✅ 授权成功！'.encode())
            threading.Thread(target=self.server.shutdown).start()
    def log_message(self,*a): pass
http.server.HTTPServer(('localhost',8765),H).serve_forever()
" &

# 用browser打开授权页面（让用户点击授权）
# URL: https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_aa933b5e9ef85cd2&redirect_uri=http://localhost:8765&scope=auth:user.id:read%20docx:document%20docx:document:create%20docx:document:write_only%20drive:drive
```

### 4. 用授权码换token
```python
import json, urllib.request

# 获取tenant_access_token
with open('/tmp/feishu_app_secret.txt') as f:
    APP_SECRET = f.read().strip()
APP_ID = "cli_aa933b5e9ef85cd2"

data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=data,
    headers={"Content-Type": "application/json"}
)
tenant_token = json.loads(urllib.request.urlopen(req).read())["tenant_access_token"]

# 用code换user_access_token
code = open('/tmp/feishu_auth_code.txt').read().strip()
data = json.dumps({"grant_type": "authorization_code", "code": code}).encode()
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token",
    data=data,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {tenant_token}"}
)
resp = json.loads(urllib.request.urlopen(req).read())
if resp.get("code") == 0:
    with open('/Users/guanmian/.hermes/profiles/main/feishu_user_token.json', 'w') as f:
        json.dump(resp["data"], f)
    print("Token saved!")
```

## 重要规则
- **端口固定8765**，不要用其他端口
- Token保存到 `~/.hermes/profiles/main/feishu_user_token.json`
- App Secret需要用户从开发者后台手动复制（browser无法读取masked内容）
- 如果refresh失败，需要重新走授权流程（用户点击授权按钮）
- 授权URL的redirect_uri必须精确匹配 `http://localhost:8765`（不带路径，不带/callback）

## Pitfalls
- **redirect_uri必须精确匹配**: 配置的是`http://localhost:8765`，不能写成`http://localhost:8765/callback`，否则报错20029
- **Refresh token会过期**: expires_in=2592000（30天），过期后需要重新授权
- **Tenant token获取需要app_secret**: 如果app_secret不对，tenant_token为空，后续所有API调用都会失败
- **Browser无法读取App Secret**: 飞书开发者后台的App Secret是masked的，点击眼睛图标也无法通过JS读取，需要用户手动复制
- **飞书原生文档vs .docx**: 在飞书中打开.docx只是预览，不是原生文档。原生飞书文档才有callout块、高亮块等富文本功能

## 用法
当需要调用飞书API时：
1. 先检查token是否有效（试试调一个简单API）
2. 如果无效，先尝试refresh
3. 如果refresh失败，走完整授权流程（启动8765服务器 → browser打开授权页 → 用户点授权 → 拿code换token）
4. 拿到token后执行API调用

## 飞书文档API

创建原生飞书文档（带callout高亮块）：
- 参考: `references/feishu-docx-api.md`
- 创建文档: `POST /open-apis/docx/v1/documents` + `{"title": "...", "folder_token": "..."}`
- 添加块: `POST /open-apis/docx/v1/documents/{id}/blocks/{id}/children`
- 文本块用`text`字段，不是`paragraph`
- **Callout是容器块**: 先创建容器 → 再用 `blocks/{callout_id}/children` 添加子内容
- Token字段名: `access_token`（不是 `user_access_token`）

### 快速示例
```python
import json, urllib.request
token = json.load(open('/Users/guanmian/.hermes/profiles/main/feishu_user_token.json'))["access_token"]
doc_id = "xxx"

# 创建callout容器
# 颜色映射（实测）：bg=3→浅蓝灰, bg=5→浅橙黄
block = {
    "block_type": 19,
    "callout": {
        "background_color": 3,  # 浅蓝灰（课件内容）
        "border_color": 3,
        "emoji_id": "pushpin"
    }
}
data = json.dumps({"children": [block]}).encode()
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
    data=data,
    headers={"Content-Type": "application/json; charset=utf-8", "Authorization": f"Bearer {token}"}
)
resp = json.loads(urllib.request.urlopen(req).read())
callout_id = resp['data']['children'][0]['block_id']

# 往callout里添加内容
child_blocks = [
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "高亮内容第一行"}}]}},
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "高亮内容第二行"}}]}}
]
data = json.dumps({"children": child_blocks}).encode()
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{callout_id}/children",
    data=data,
    headers={"Content-Type": "application/json; charset=utf-8", "Authorization": f"Bearer {token}"}
)
resp = json.loads(urllib.request.urlopen(req).read())
```
