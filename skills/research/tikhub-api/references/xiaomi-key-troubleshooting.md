# Xiaomi MiMo API Key 故障排查

## 常见错误码

| 错误码 | 含义 | 处理 |
|--------|------|------|
| 401 | Invalid API Key | key 本身无效或被删除 |
| 402 | Insufficient account balance | key 有效但余额不足（充值后重置状态即可） |

## auth.json 凭据池

Hermes 把 API key 存在 `~/.hermes/auth.json` 的 `credential_pool` 里，不是直接从 .env 读取。

```
credential_pool.xiaomi = [
  { source: "env:XIAOMI_API_KEY", last_status: "exhausted", last_error_code: 402 },
  { source: "manual", last_status: "exhausted", last_error_code: 401 }
]
```

### 重置 exhausted 状态

充值后 key 恢复有效，但 Hermes 不会自动重置。手动修复：

```python
import json, os
path = os.path.expanduser('~/.hermes/auth.json')
with open(path) as f: data = json.load(f)
for c in data['credential_pool'].get('xiaomi', []):
    c['last_status'] = 'ok'
    c['last_error_code'] = None
    c['last_error_message'] = None
with open(path, 'w') as f: json.dump(data, f, indent=2)
```

### 删除无效的手动 key

```python
data['credential_pool']['xiaomi'] = [
    c for c in data['credential_pool']['xiaomi']
    if c.get('source') != 'manual'
]
```

### 修复后重启 Gateway

```bash
hermes gateway restart
```

## 注意事项

- .env 里 `XIAOMI_API_KEY=***` 是字面值（不是 masked），实际 key 通过环境变量传入
- 同一个 key 在 Windows 和 Mac 共享，充值后两边都恢复
- 401 错误如果 key 本身有效（env source），可能是手动加的备用 key 报的
- **⚠️ 区分两个 key 的错误码**：env source 的 key 报 402（余额不足），manual source 的 key 报 401（key 本身无效）。用户说"401"时可能是在看 manual key 的错误，实际 env key 是 402。排查时两个都要检查。
