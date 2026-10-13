---
name: llm-provider-fix
description: "LLM provider 报错诊断与修复。触发词：401、402、Invalid API Key、欠费、余额不足、provider报错、key失效、token过期、飞书报错、模型调用失败。自动定位 credential_pool 状态、重置 exhausted key、清理无效 key、重启 gateway。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [llm, provider, billing, auth, credential-pool, debug]
---

# LLM Provider 报错诊断与修复

当用户报告 LLM 调用报错（401/402/403）、飞书/通道回复失败、模型调不通时，按以下流程排查。

## 快速诊断（3步定位）

### Step 1: 看日志确定错误类型

```bash
tail -50 ~/.hermes/profiles/main/logs/gateway.error.log | grep -i "401\|402\|403\|invalid.*key\|exhausted\|insufficient"
```

常见错误码：
| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 401 | Invalid API Key | key 无效或已被撤销，需更换 |
| 402 | Insufficient account balance | 账户欠费，需充值 |
| 403 | Permission denied | key 权限不足，检查 scope |
| SSL/Connection | 网络问题 | 检查代理/防火墙 |

### Step 2: 查 credential_pool 状态

```bash
cat ~/.hermes/profiles/main/auth.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
cp = d.get('credential_pool', {})
for provider, entries in cp.items():
    for e in entries:
        label = e.get('label','?')
        status = e.get('last_status','?')
        err = e.get('last_error_code','')
        msg = e.get('last_error_message','')[:50]
        print(f'  {provider}/{label}: status={status} err={err} msg={msg}')
"
```

关注：
- status=exhausted 的 key → 被标记耗尽，需要重置或更换
- 所有 key 都 exhausted → "no available entries" → 通道完全不可用

### Step 3: 确认 key 本身是否有效

```bash
# 替换为实际的环境变量名和 base_url
export $(grep "^XIAOMI_API_KEY=" ~/.hermes/.env | xargs)
python3 -c "
import urllib.request, os
key = os.environ.get('XIAOMI_API_KEY','')
req = urllib.request.Request('https://api.xiaomimimo.com/v1/models', headers={'Authorization': f'Bearer {key}'})
try:
    r = urllib.request.urlopen(req)
    print(f'OK (status={r.status})')
except urllib.error.HTTPError as e:
    print(f'FAIL: {e.code} {e.read().decode()[:200]}')
"
```

如果 key 本身能通但 credential_pool 报 exhausted → 欠费后充值的典型表现，重置即可。

## 修复操作

### 情况 A: 欠费充值后恢复（最常见）

credential_pool 还记着 exhausted 状态，需要手动重置：

```bash
cat ~/.hermes/profiles/main/auth.json | python3 -c "
import sys, json, time
d = json.load(sys.stdin)
cp = d.get('credential_pool', {})
for provider, entries in cp.items():
    for e in entries:
        if e.get('last_status') == 'exhausted' and e.get('last_error_code') in [402, 401]:
            e['last_status'] = 'ok'
            e['last_status_at'] = None
            e['last_error_code'] = None
            e['last_error_reason'] = None
            e['last_error_message'] = None
            e['last_error_reset_at'] = time.time()
            print(f'Reset {provider}/{e[\"label\"]} -> ok')
with open('$HOME/.hermes/profiles/main/auth.json', 'w') as f:
    json.dump(d, f, indent=2)
"
```

然后重启 gateway：
```bash
hermes gateway restart
```

### 情况 B: key 真的失效了

1. 获取新 key
2. 更新环境变量（`.env` 文件）
3. 从 credential_pool 删除旧 key 或重置状态
4. 重启 gateway

删除旧 key：
```bash
cat ~/.hermes/profiles/main/auth.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
cp = d.get('credential_pool', {})
# 按 provider 和 label 过滤
target_provider = 'xiaomi'  # 改为实际 provider
target_label = 'api-key-2'  # 改为要删的 label
if target_provider in cp:
    cp[target_provider] = [e for e in cp[target_provider] if e.get('label') != target_label]
with open('$HOME/.hermes/profiles/main/auth.json', 'w') as f:
    json.dump(d, f, indent=2)
print('Done')
"
```

### 情况 C: 多个 key 轮换（credential pool）

如果配置了多个 key 做容错，确保至少有一个是有效的。查看所有 key 状态：
```bash
cat ~/.hermes/profiles/main/auth.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
for provider, entries in d.get('credential_pool', {}).items():
    for e in entries:
        print(f'{provider}/{e[\"label\"]}: {e[\"last_status\"]} (err={e.get(\"last_error_code\",\"-\")})')
"
```

## 常见陷阱

1. **充值后不重启** — credential_pool 状态缓存在内存中，必须 `hermes gateway restart` 才生效
2. **auth.json 里的 key ≠ .env 里的 key** — auth.json 的 credential_pool 可能有手动添加的 key（source="manual"），和 .env 里的环境变量 key 是两个东西
3. **402 ≠ 401** — 402 是欠费（充值就行），401 是 key 无效（要换 key）
4. **只有飞书报错但 CLI 正常** — CLI session 可能在报错前就建立了连接，不受 credential_pool 影响；飞书通道每次新消息都走 credential_pool 取 key
5. **"no available entries"** — 所有 key 都 exhausted，不是没有 key，而是全被标记耗尽了

## 验证修复

重启后发测试消息确认：
```bash
# 查看 gateway 是否正常连接
cat ~/.hermes/profiles/main/gateway_state.json | python3 -m json.tool | grep -A3 "state"
```

飞书通道状态应为 `"state": "connected"`，无 error_code。
