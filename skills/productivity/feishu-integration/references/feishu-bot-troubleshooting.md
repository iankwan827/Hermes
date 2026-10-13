# Feishu Bot Channel Troubleshooting

## Error: "Invalid API Key" on Feishu bot replies

The error `HTTP 401: Invalid API Key` in Feishu bot responses almost always means the **LLM provider** key is exhausted, NOT the Feishu API.

### Root Cause: Credential Pool Exhaustion

Hermes manages API keys via a credential pool stored in:
```
~/.hermes/profiles/main/auth.json → credential_pool
```

Each provider has a list of keys. When a key gets 401/402, it's marked `exhausted` and the pool rotates to the next. When ALL keys for a provider are exhausted → "no available entries" → every request fails.

### Real Error in Logs

The error message shown to the user is misleading (it shows the LLM error wrapped in Feishu formatting). The actual error is in:

```bash
# Gateway error log — shows the LLM provider error
tail -200 ~/.hermes/profiles/main/logs/gateway.error.log | grep -i "401\|error\|provider"

# Agent log — shows credential pool rotation
tail -200 ~/.hermes/profiles/main/logs/agent.log | grep -i "credential\|exhausted\|rotat"
```

Key log lines:
```
agent.credential_pool: marking XIAOMI_API_KEY exhausted (status=401), rotating
agent.credential_pool: no available entries (all exhausted or empty)
agent.conversation_loop: Non-retryable client error: Error code: 401
```

### Diagnosis Steps

1. **Check credential pool state:**
```bash
python3 -c "
import json
with open('/Users/guanmian/.hermes/profiles/main/auth.json') as f:
    d = json.load(f)
for provider, entries in d.get('credential_pool', {}).items():
    for e in entries:
        print(f\"{provider}: {e['label']} status={e.get('last_status','?')} code={e.get('last_error_code','')} msg={e.get('last_error_message','')}\")
"
```

2. **Test the key independently (bypasses pool):**
```bash
# For xiaomi
export $(grep XIAOMI_API_KEY ~/.hermes/.env | xargs)
python3 -c "
import urllib.request, json, os
key = os.environ['XIAOMI_API_KEY']
req = urllib.request.Request('https://api.xiaomimimo.com/v1/models', headers={'Authorization': f'Bearer {key}'})
try:
    r = urllib.request.urlopen(req)
    print(f'OK: {r.status}')
except urllib.error.HTTPError as e:
    print(f'FAIL: {e.code} {e.read().decode()[:200]}')
"
```

3. **Check .env key vs pool key match:**
```bash
# What's in .env
grep XIAOMI_API_KEY ~/.hermes/.env
# What's in pool
python3 -c "import json; d=json.load(open('...auth.json')); print([e['secret_fingerprint'] for e in d['credential_pool'].get('xiaomi',[])])"
```

### Common Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| 401 | Invalid API Key | Check key is correct, not expired |
| 402 | Insufficient account balance | Top up account at provider dashboard |
| 429 | Rate limit | Wait or use different key |
| 500 | Provider server error | Retry, usually transient |

### Fix: Reset Credential Pool

If a key is valid but stuck as exhausted:

```bash
# Option 1: Restart the gateway (clears pool state)
hermes gateway restart

# Option 2: Edit auth.json directly (set status back to ok)
python3 -c "
import json
path = '/Users/guanmian/.hermes/profiles/main/auth.json'
with open(path) as f: d = json.load(f)
for provider in d.get('credential_pool', {}):
    for entry in d['credential_pool'][provider]:
        if entry.get('last_status') == 'exhausted':
            entry['last_status'] = 'ok'
            entry['last_error_code'] = None
            entry['last_error_message'] = None
            print(f'Reset: {provider}/{entry[\"label\"]}')
with open(path, 'w') as f:
    json.dump(d, f, indent=2)
print('Done')
"
```

### Fix: Add New Key to Pool

If the old key is genuinely dead:

```bash
hermes auth add-key --provider xiaomi --key "sk-newkey..."
```

Or edit `auth.json` → `credential_pool` → `xiaomi` array.
