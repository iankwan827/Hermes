---
name: feishu-token-refresh
description: 自动刷新飞书user_access_token。当Feishu API返回token过期或401时使用。
tags: [feishu, token, oauth, refresh]
triggers:
  - "飞书token过期"
  - "飞书401"
  - "feishu token expired"
  - "刷新飞书token"
---

# 飞书Token自动刷新

## 触发条件
- Feishu API返回401/403/token_expired
- `feishu_doc_read`等工具报"Feishu client not available"
- 用户说"刷新token"或"token过期"

## 刷新步骤

### 1. 获取当前refresh_token
```python
import json
with open('/Users/guanmian/.hermes/profiles/main/feishu_user_token.json') as f:
    d = json.load(f)
refresh_token = d['refresh_token']
```

### 2. 获取tenant_access_token
```python
import urllib.request
app_id = os.environ.get('FEISHU_APP_ID')
app_secret = os.environ.get('FEISHU_APP_SECRET')

req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    tenant_token = json.loads(resp.read())['tenant_access_token']
```

### 3. 用refresh_token刷新user_access_token
```python
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token',
    data=json.dumps({
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }).encode(),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant_token}'
    }
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())

if result['code'] == 0:
    new_data = result['data']
    d['access_token'] = new_data['access_token']
    d['refresh_token'] = new_data['refresh_token']
    with open('/Users/guanmian/.hermes/profiles/main/feishu_user_token.json', 'w') as f:
        json.dump(d, f, indent=2)
    print("✅ Token refreshed!")
```

## 一键刷新脚本
```bash
python3 -c "
import json, urllib.request, os
with open(os.path.expanduser('~/.hermes/profiles/main/feishu_user_token.json')) as f:
    d = json.load(f)
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({'app_id': os.environ['FEISHU_APP_ID'], 'app_secret': os.environ['FEISHU_APP_SECRET']}).encode(),
    headers={'Content-Type': 'application/json'})
tenant = json.loads(urllib.request.urlopen(req).read())['tenant_access_token']
req2 = urllib.request.Request(
    'https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token',
    data=json.dumps({'grant_type': 'refresh_token', 'refresh_token': d['refresh_token']}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {tenant}'})
r = json.loads(urllib.request.urlopen(req2).read())
if r['code'] == 0:
    d['access_token'] = r['data']['access_token']
    d['refresh_token'] = r['data']['refresh_token']
    json.dump(d, open(os.path.expanduser('~/.hermes/profiles/main/feishu_user_token.json'), 'w'), indent=2)
    print('✅ OK')
else:
    print(f'❌ {r[\"msg\"]}')
"
```

## 注意事项
- refresh_token有效期30天，过期需重新走OAuth授权流程
- 环境变量 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 必须已设置
- Token文件路径：`~/.hermes/profiles/main/feishu_user_token.json`
