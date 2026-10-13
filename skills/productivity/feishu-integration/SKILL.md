---
name: feishu-integration
description: "Complete Feishu/Lark integration: OAuth authentication, token management, drive operations, document creation, and native document upload. Unified entry point for all Feishu API tasks."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [feishu, lark, cloud-drive, upload, document, oauth, token]
    related_skills: [course-notes-fusion, course-notes-docx]
---

# Feishu Integration

Complete guide for working with Feishu/Lark APIs. Covers authentication, drive operations, document creation, and file upload.

## Prerequisites

- Environment variables: `FEISHU_APP_ID`, `FEISHU_APP_SECRET`
- App configured at https://open.feishu.cn with appropriate permissions

---

## 1. Authentication

### Token Types

| Token | Use For | Lifetime | How to Get |
|-------|---------|----------|------------|
| **tenant_access_token** | Drive ops (upload, create folders) | 2 hours, auto-refreshable | app_id + app_secret |
| **user_access_token** | Doc read/write, sheets | 2 hours | OAuth flow |
| **app_access_token** | OIDC token refresh | 2 hours | app_id + app_secret |

### Getting tenant_access_token (no user auth needed)

```python
import json, urllib.request, os

req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": os.environ["FEISHU_APP_ID"], "app_secret": os.environ["FEISHU_APP_SECRET"]}).encode(),
    headers={"Content-Type": "application/json"}
)
tenant_token = json.loads(urllib.request.urlopen(req).read())["tenant_access_token"]
```

### OAuth Flow (for user_access_token) — macOS Automation

**Complete flow with AppleScript (agent can do this automatically):**

**Step 1: Start HTTP server** (background)
```bash
lsof -ti:8765 | xargs kill -9 2>/dev/null  # clear port first
```
Start a Python HTTP server on port 8765 that:
- Listens for GET callback with `?code=xxx`
- Exchanges code for token via OIDC endpoint
- Saves token to `~/.hermes/profiles/main/feishu_user_token.json`
- Prints `SUCCESS` or `FAILED` to stdout

**Step 2: Open auth page in Chrome** (AppleScript)
```bash
osascript -e '
tell application "Google Chrome"
    set authURL to "https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=<APP_ID>&redirect_uri=http%3A%2F%2Flocalhost%3A8765&scope=auth%3Auser.id%3Aread%20docx%3Adocument%20docx%3Adocument%3Acreate%20docx%3Adocument%3Awrite_only%20drive%3Adrive"
    set URL of active tab of window 1 to authURL
end tell
'
```

**Step 3: Click "授权" button** (AppleScript, after 5s page load)
```bash
sleep 5
osascript -e '
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "<APP_ID>" then
                execute t javascript "
                    var btns = document.querySelectorAll(\"button\");
                    for (var i = 0; i < btns.length; i++) {
                        if ((btns[i].innerText || \"\").indexOf(\"授权\") >= 0) {
                            btns[i].click(); break;
                        }
                    }
                "
                return "Clicked"
            end if
        end repeat
    end repeat
end tell
'
```

**Step 4: Wait for callback** — server auto-exchanges code for token, saves to file.

**Full one-liner (start server + navigate + click):**
```bash
# Terminal 1: start server
cd /Users/guanmian && PYTHONUNBUFFERED=1 python3 -u feishu_oauth_server.py &

# Terminal 2: navigate + click
osascript -e 'tell application "Google Chrome" to set URL of active tab of window 1 to "https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=<APP_ID>&redirect_uri=http%3A%2F%2Flocalhost%3A8765&scope=auth%3Auser.id%3Aread%20docx%3Adocument%20docx%3Adocument%3Acreate%20docx%3Adocument%3Awrite_only%20drive%3Adrive"'
sleep 5
osascript -e 'tell application "Google Chrome" to repeat with w in windows repeat with t in tabs of w if URL of t contains "<APP_ID>" then execute t javascript "var b=document.querySelectorAll(\"button\");for(var i=0;i<b.length;i++){if((b[i].innerText||\"\").indexOf(\"授权\")>=0){b[i].click();break;}}" end if end repeat end repeat'
```

**Authorization URL:**
```
https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=<APP_ID>&redirect_uri=http%3A%2F%2Flocalhost%3A8765&scope=auth:user.id:read%20docx:document%20docx:document:create%20docx:document:write_only%20drive:drive
```

### Token Exchange (server-side, after receiving code)

```python
# After HTTP server receives ?code=xxx callback:

# 1. Get tenant_access_token
req_t = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
tenant = json.loads(urllib.request.urlopen(req_t).read())["tenant_access_token"]

# 2. Exchange authorization_code for user tokens
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token",
    data=json.dumps({"grant_type": "authorization_code", "code": auth_code}).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {tenant}"}
)
result = json.loads(urllib.request.urlopen(req).read())
if result["code"] == 0:
    token_data = {
        "access_token": result["data"]["access_token"],
        "refresh_token": result["data"]["refresh_token"],
        "token_type": result["data"].get("token_type", "Bearer"),
        "expires_in": result["data"].get("expires_in", 7200),
        "refresh_expires_in": result["data"].get("refresh_expires_in", 2592000),
        "scope": result["data"].get("scope", ""),
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
```

### Token Refresh (user_access_token)

**Critical:** The OIDC refresh endpoint needs `tenant_access_token` as Bearer (NOT app_id/app_secret in body).

```python
# 1. Get tenant_access_token (see above)

# 2. Refresh user_access_token
with open(os.path.expanduser("~/.hermes/profiles/main/feishu_user_token.json")) as f:
    token_data = json.load(f)

req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token",
    data=json.dumps({"grant_type": "refresh_token", "refresh_token": token_data["refresh_token"]}).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {tenant_token}"}
)
result = json.loads(urllib.request.urlopen(req).read())
if result["code"] == 0:
    token_data["access_token"] = result["data"]["access_token"]
    token_data["refresh_token"] = result["data"]["refresh_token"]  # New refresh_token too!
    with open(os.path.expanduser("~/.hermes/profiles/main/feishu_user_token.json"), "w") as f:
        json.dump(token_data, f, indent=2)
```

### ⚠️ upload_notes.py Token Refresh Bug (2026-07-01 发现)

**问题**：`upload_notes.py` 的 `refresh_token()` 函数把 `app_id` + `app_secret` 放在 request body 里，但 OIDC refresh 端点要求 `tenant_access_token` 作为 `Authorization: Bearer` 头。

**症状**：返回 `{"code": 20014, "message": "The app access token passed is invalid"}`

**修复方法**（先手动刷新一次）：
```bash
export $(grep FEISHU ~/.hermes/.env | xargs) && python3 -c "
import json, urllib.request, os
APP_ID = os.environ['FEISHU_APP_ID']
APP_SECRET = os.environ['FEISHU_APP_SECRET']
TOKEN_FILE = os.path.expanduser('~/.hermes/profiles/main/feishu_user_token.json')
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({'app_id': APP_ID, 'app_secret': APP_SECRET}).encode(),
    headers={'Content-Type': 'application/json'})
tenant = json.loads(urllib.request.urlopen(req).read())['tenant_access_token']
with open(TOKEN_FILE) as f: d = json.load(f)
req2 = urllib.request.Request('https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token',
    data=json.dumps({'grant_type': 'refresh_token', 'refresh_token': d['refresh_token']}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {tenant}'})
r = json.loads(urllib.request.urlopen(req2).read())
if r['code'] == 0:
    d['access_token'] = r['data']['access_token']; d['refresh_token'] = r['data']['refresh_token']
    json.dump(d, open(TOKEN_FILE, 'w'), indent=2)
    print('OK')
else: print(f'FAIL: {r}')
"
```

**根治**：修改 `upload_notes.py` 的 `refresh_token()` 函数，先获取 `tenant_access_token`，再用它作为 Bearer 头刷新 user token。

### One-Line Refresh Script

```bash
python3 -c "
import json, urllib.request, os
with open(os.path.expanduser('~/.hermes/profiles/main/feishu_user_token.json')) as f: d = json.load(f)
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=json.dumps({'app_id': os.environ['FEISHU_APP_ID'], 'app_secret': os.environ['FEISHU_APP_SECRET']}).encode(), headers={'Content-Type': 'application/json'})
tenant = json.loads(urllib.request.urlopen(req).read())['tenant_access_token']
req2 = urllib.request.Request('https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token', data=json.dumps({'grant_type': 'refresh_token', 'refresh_token': d['refresh_token']}).encode(), headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {tenant}'})
r = json.loads(urllib.request.urlopen(req2).read())
if r['code'] == 0:
    d['access_token'] = r['data']['access_token']; d['refresh_token'] = r['data']['refresh_token']
    json.dump(d, open(os.path.expanduser('~/.hermes/profiles/main/feishu_user_token.json'), 'w'), indent=2)
    print('OK')
else: print(f'FAIL: {r[\"msg\"]}')
"
```

### Auth Pitfalls

- **redirect_uri must match exactly:** `http://localhost:8765` (no /callback)
- **refresh_token expires in 30 days** — re-authorize after expiry
- **Browser can't read App Secret** — user must copy manually from developer console
- **Use tenant_token for drive ops** — user_token for doc read/write only
- **Token expired → 自动执行OAuth流程，不要问用户** — 用户原话："你是不是有毛病，授权一直都是你自己点的，看skill"。token过期时必须自动：启动OAuth server → open Chrome → 点击授权按钮 → 等待回调。不要让用户手动操作。

---

## 2. Drive Operations

### Create Folder

```python
result = curl_post('/open-apis/drive/v1/files/create_folder', {"name": "Folder Name", "folder_token": ""})
folder_token = result["data"]["token"]
```

### List Folder Contents

```python
result = curl_get(f'/open-apis/drive/v1/files?folder_token={folder_token}&page_size=50')
files = result["data"]["files"]
```

### Upload File (max 20MB)

```python
# Using curl subprocess
result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
    "-H", f"Authorization: Bearer {token}",
    "-F", f"file_name={file_name}",
    "-F", "parent_type=explorer",
    "-F", f"parent_node={folder_token}",
    "-F", f"size={file_size}",
    "-F", f"file=@{file_path}"
], capture_output=True, text=True)
```

### Find or Create Folder (Helper)

```python
def find_or_create_folder(token, folder_name, parent_token=""):
    result = curl_get(f'/open-apis/drive/v1/files?folder_token={parent_token}&page_size=50')
    for f in result["data"]["files"]:
        if f["name"] == folder_name and f["type"] == "folder":
            return f["token"]
    result = curl_post('/open-apis/drive/v1/files/create_folder', {"name": folder_name, "folder_token": parent_token})
    return result["data"]["token"]
```

### Create Spreadsheet

**tenant_token也能创建表格（已验证2026-07-02）：**
```python
# tenant_token works for creating spreadsheets
result = curl_post('/open-apis/sheets/v3/spreadsheets', {"title": "Title"})
spreadsheet_token = result["data"]["spreadsheet"]["spreadsheet_token"]
url = result["data"]["spreadsheet"]["url"]
```

写入数据用PUT方法：
```python
# Get sheet_id first
result = curl_get(f'/open-apis/sheets/v3/spreadsheets/{token}/sheets/query')
sheet_id = result['data']['sheets'][0]['sheet_id']

# Write data
data = {"valueRange": {"range": f'{sheet_id}!A1:F6', "values": [[...]]}}
curl_put(f'/open-apis/sheets/v2/spreadsheets/{token}/values', data)
```

---

## 3. Document Creation (Native Feishu Docs)

### Block Types Reference

| Type | Name | Usage |
|------|------|-------|
| 2 | text | Paragraph |
| 3 | heading1 | H1 |
| 4 | heading2 | H2 |
| 5 | heading3 | H3 |
| 12 | bullet | Bullet list |
| 13 | ordered | Numbered list |
| 14 | code | Code block (language=34 for PlainText) |
| 15 | quote | Quote block |
| 19 | callout | Highlight block (colored background + emoji) |
| 22 | divider | Horizontal rule |

### Create Document + Add Blocks

```python
# 1. Create document
result = curl_post('/open-apis/docx/v1/documents', {"title": "Title", "folder_token": folder_token})
doc_id = result["data"]["document"]["document_id"]

# 2. Add blocks in batches (max 10-20 per batch)
blocks = [
    {"block_type": 3, "heading1": {"elements": [{"text_run": {"content": "Title", "text_element_style": {"bold": True}}}]}},
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "Body text"}}]}}
]
curl_post(f'/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children', {"children": blocks})
```

### Callout Blocks (Colored Highlights)

**Must be created as empty container, then fill with child blocks:**

```python
# 1. Create empty callout
result = curl_post(f'/docx/v1/documents/{doc_id}/blocks/{doc_id}/children', {
    "children": [{"block_type": 19, "callout": {"background_color": 3, "border_color": 3, "emoji_id": "pushpin"}}]
})
callout_id = result["data"]["children"][0]["block_id"]

# 2. Add content to callout
child_blocks = [
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "Highlighted content"}}]}}
]
curl_post(f'/open-apis/docx/v1/documents/{doc_id}/blocks/{callout_id}/children', {"children": child_blocks})
```

**Background colors (verified):** bg=3 → light blue, bg=5 → light orange

### Known API Limitations

- **Native tables (block_type=20)** — Cannot be created via API. Use code blocks (block_type=14, language=34) for table-like content.
- **Code block language** — Must use integer 34 for PlainText, NOT 1 (which errors).
- **Callout `code_style`** — Set at creation time only, cannot be modified later.
- **Image blocks (block_type=27)** — API returns 400 Bad Request. **Images cannot be inserted via API.** Workaround: upload images to Feishu drive via `drive/v1/files/upload_all` (parent_type=explorer), then user manually inserts via `/图片 → 从云盘选择` in the document. Alternatively, upload via `drive/v1/medias/upload_all` (parent_type=docx_image) to attach to a doc, but the image block creation still fails.

---

## 4. Upload Workflow (Upload Notes Script)

### The Script (Single Entry Point)

```bash
python3 ~/Pictures/八字课/scripts/upload_notes.py "<标题>" "<markdown文件>"
```

**Example:**
```bash
python3 ~/Pictures/八字课/scripts/upload_notes.py "拾易八字·第二期第一课·完整笔记" ~/Pictures/八字课/第一课/2期第一课_完整笔记.md
```

### Script Features

- Auto-detects callout markers: `### 📋 课件内容` → blue, `### 🎙️ 讲师解读` → orange
- Heading levels H1/H2/H3 auto-detected
- Tables converted to code blocks (monospace alignment)
- Bold `**text**` recognized and applied

### ⚠️ Critical Rules

1. **NEVER rewrite the upload script** — it already handles all edge cases
2. **Don't use curl directly** — shell quotes conflict with markdown `***`
3. **Callout must be empty container first** — script handles this
4. **Code block language must be integer** — 34 for PlainText
5. **Native tables impossible** — use code blocks
6. **Bullet list is block_type=12** — NOT 15 (verified)
7. **Title via CLI args** — don't hardcode in script
8. **Large files take 5-10 minutes** — set timeout high enough

---

## 5. Wiki Document Access

Wiki URLs contain `node_token`, not `doc_token`. Convert first:

```python
# 1. Get node info
result = curl_get(f'/open-apis/wiki/v2/spaces/get_node?token={wiki_token}')
obj_token = result["data"]["node"]["obj_token"]

# 2. Read document content
result = curl_get(f'/open-apis/docx/v1/documents/{obj_token}/raw_content')
content = result["data"]["content"]
```

---

## Troubleshooting

### ⚠️ Bot Channel 401 ≠ Feishu API Token Expired

When user reports "飞书报401", the error may NOT be from the Feishu API. Distinguish:

| Symptom | Actual Cause | Fix |
|---------|-------------|-----|
| Feishu bot replies "401 Invalid API Key" | LLM provider (xiaomi/openai/etc) key exhausted | Check credential pool, not Feishu token |
| Feishu API returns 401 on doc/drive ops | Feishu user_access_token expired | Refresh via One-Line Refresh Script above |
| Feishu API returns 400 on doc/drive ops | Feishu token expired mid-operation | Refresh token before multi-step sequence |

**Diagnostic path for bot channel 401:**
```bash
# 1. Check gateway error log for the REAL error
tail -100 ~/.hermes/profiles/main/logs/gateway.error.log | grep -i "401\|error\|feishu"

# 2. Check credential pool state
cat ~/.hermes/profiles/main/auth.json | python3 -c "
import sys,json; d=json.load(sys.stdin)
for p,entries in d.get('credential_pool',{}).items():
    for e in entries:
        print(f\"{p}: {e['label']} status={e.get('last_status','?')} error={e.get('last_error_code','')}\")
"

# 3. Check if provider key works independently
export $(grep XIAOMI_API_KEY ~/.hermes/.env | xargs)
curl -s https://api.xiaomimimo/v1/models -H "Authorization: Bearer $XIAOMI_API_KEY" | head -20
```

**Credential pool state file:** `~/.hermes/profiles/main/auth.json` → `credential_pool` section.
- Keys marked `exhausted` won't be used until rotated or pool is reset.
- Common causes: 401 (invalid key), 402 (insufficient balance), rate limits.

---

## Pitfalls

1. **Shell quotes + markdown `***`** — always write Python scripts to files, then execute
2. **file=@path must be absolute** — relative paths may not resolve
3. **file_size must be exact bytes** — mismatch causes upload failure
4. **folder_token="" means root** — not null
5. **tenant vs user token** — drive ops use tenant; doc ops use user
6. **CSV has BOM** — use `encoding='utf-8-sig'` when reading
7. **Check existing files first** — don't recreate what's already there
8. **User prefers review before upload** — don't auto-upload, ask first
9. **App permissions** — new scopes require re-authorization (not just token refresh)
10. **Sheets batch write fails silently** — PUT to `/sheets/v2/spreadsheets/{token}/values` with large payloads returns 400. Workaround: write row-by-row in a loop, or write in small batches (2-3 rows). Single-row writes always succeed.
11. **Sheets clear range** — cannot clear cells by writing empty arrays in batch. Write empty strings row-by-row instead.
12. **Token expires mid-operation** — refresh token before any multi-step Feishu API sequence. The 400 error often means expired token, not bad data.
13. **OAuth on macOS** — Use AppleScript to control Chrome, NOT browser_navigate tool (headless Chrome can't reach localhost:8765 callback). The `open` command opens a new window; use AppleScript `set URL of active tab` to reuse existing tabs.
14. **OAuth button text** — The authorize button text is "授权" (not "Authorize" or "Allow"). Search for `indexOf("授权")` in button innerText.
15. **OAuth callback sometimes doesn't arrive** — 多次尝试OAuth刷新token失败，callback未收到。此时tenant_token可以作为fallback完成大部分操作（创建表格、写入数据、创建文档）。不要卡在OAuth上，先用tenant_token完成任务。
16. **选股表格必须每周更新** — 用户反复强调周报出来后必须立即更新飞书表格（`APv3sZM02h4DQrt8Bcrclin4nfW`），不要等用户提醒。token过期时先试refresh，失败就走OAuth，不要卡住。
16. **upload_notes.py 🎙️格式bug** — 🎙️标记和内容必须分两行！如果内容在同一行（如 `🎙️ **讲师解读** 这是内容`），脚本会读取下一行（通常是`---`或空行）作为callout内容，导致飞书显示"···"。修复：用正则 `re.sub(r'^(🎙️ \*\*讲师解读\*\*) (.+)$', r'\1\n\2', content, flags=re.MULTILINE)` 把同行内容拆到下一行。
17. **用户要求表格不要文档** — 用户说"创建表格，不是文档"时，要创建spreadsheet（飞书表格），不是document（飞书文档）。spreadsheet用tenant_token就能创建，document也用tenant_token。两者API不同。
18. **Spreadsheet sheet_id必须查询** — 创建spreadsheet后写入数据，不能用"Sheet1"作为sheet_id！必须先调用 `GET /sheets/v3/spreadsheets/{token}/sheets/query` 获取实际的sheet_id（如"68303f"），再用它构造range（如 `68303f!A1:F11`）。用"Sheet1"会报"sheetId not found"。
19. **Python写入飞书表格完整模式** — 用Python urllib而非curl，避免shell引号问题。流程：获取tenant_token → 读取/.env → 构造数据JSON → PUT写入。用`json.dumps().encode()`作为request body。
20. **Spreadsheet写入行数必须匹配range** — PUT写入时，values数组的行数不能超过range声明的行数，否则报`90202 range in request is wrong, rows of value:N > range`。解决：要么精确计算range（如`A1:F11`对应11行），要么先用更大的range清空再写入。
21. **清空spreadsheet行区域** — 不能传空数组`[]`清空（报`90215 rows equals 0`），要传等量的空字符串行：`[["","","",""] for _ in range(N)]`。先清后写是覆盖已有数据的标准模式。
22. **多表格区域在同一sheet** — 一个sheet可以放多个逻辑表格，用空行分隔。每个表格独立标题+表头+数据。写入时按区域分批写入（如A1:F11、A12:D22、A40:D62），避免一次性写入过多行导致range计算困难。
23. **应用创建的表格用户看不到** — tenant_token创建的spreadsheet默认只有应用自己能访问。用户会说"这表格为啥不是我的"。必须主动分享给用户：`POST /drive/v1/permissions/{token}/members?type=sheet`，body: `{"member_type":"openid","member_id":"用户open_id","perm":"full_access"}`。用户open_id从最近的飞书消息事件中获取（sender.sender_id.open_id）。
24. **用户偏好紧凑表格格式** — 用户喜欢"五行做列、维度做行"的紧凑格式（如五行身材表：木/火/土/金/水做5列，性格/身材/皮肤/气质/喜忌做5行），比"十天干每行一个"的信息密度更高。五行身材表是用户明确要求的格式。
25. **飞书问卷/表单没有开放API** — 飞书问卷（飞书问卷产品）不支持通过API创建或管理。多维表格（Bitable）有表单视图但"表单视图"本身需要在飞书客户端手动开启。如果用户需要条件跳转问卷（选A跳到链接，选B结束），只能在飞书客户端手动创建问卷并设置逻辑跳转，无法自动化。替代方案：用bot对话式交互（问问题→根据回答发消息）或创建独立HTML网页。

## References

- `references/feishu-block-types.md` — Complete block type reference
- `references/feishu-docx-api.md` — Document API endpoints and parameters
- `references/feishu-api-notes.md` — API quirks and known limitations
- `references/feishu-bot-troubleshooting.md` — Bot channel 401 diagnosis, credential pool debugging, reset/fix recipes
- `scripts/create_feishu_doc.py` — Document creation script (supports both API and text-only approaches)
