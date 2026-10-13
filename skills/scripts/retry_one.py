import os, sys, json, base64, urllib.request

env_path = os.path.expanduser('~/AppData/Local/hermes/.env')
api_key = ''
with open(env_path) as f:
    for line in f:
        if line.strip().startswith('XIAOMI_API_KEY'):
            api_key = line.strip().split('=', 1)[1]
            break

img_path = 'D:/hermes-agent/imge/5b6321f2af13af67df737ec0fb44dafb.png'
out_path = 'D:/hermes-agent/imge/docs/5b6321f2af13af67df737ec0fb44dafb.md'

with open(img_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

data_url = f'data:image/png;base64,{b64}'
messages = [{'role': 'user', 'content': [
    {'type': 'text', 'text': '提取所有文字保持排版'},
    {'type': 'image_url', 'image_url': {'url': data_url}},
]}]

headers = {'Authorization': f'Bearer {api_key}', 'api-key': api_key, 'Content-Type': 'application/json'}
payload = {'model': 'mimo-v2.5', 'messages': messages, 'max_tokens': 8000, 'temperature': 0.1}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request('https://token-plan-cn.xiaomimimo.com/v1/chat/completions', data=data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        text = result['choices'][0]['message']['content']
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'OK: {len(text)} chars')
except Exception as e:
    print(f'FAIL: {e}')
