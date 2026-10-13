---
name: social-media
description: "Social media operations: X/Twitter posting and engagement, Yuanbao group interactions."
version: 1.0.0
tags: [social-media, twitter, x, yuanbao, posting, engagement]
metadata:
  hermes:
    tags: [social-media, twitter, x, yuanbao, posting, engagement]
    category: social-media
---

# Social Media Toolkit

Unified skill for social media operations — posting, searching, engaging, and
managing interactions across platforms.

## Supported Platforms

| Platform | CLI/Tool | Key Operations |
|----------|----------|----------------|
| **X / Twitter** | `xurl` | Post, reply, search, DM, media upload, engagement |
| **Yuanbao (元宝)** | `yb_*` tools | Group @mentions, DMs, member queries |

---

## X / Twitter (xurl)

`xurl` is the X developer platform's official CLI. Supports shortcut commands
for common actions AND raw curl-style access to any v2 endpoint. All commands
return JSON to stdout.

### Secret Safety (MANDATORY)

- **Never** read, print, parse, summarize, upload, or send `~/.xurl` to LLM context.
- **Never** ask the user to paste credentials/tokens into chat.
- **Never** use `--verbose` / `-v` in agent sessions — it can expose auth headers/tokens.
- To verify credentials exist, only use: `xurl auth status`.

### Installation

```bash
# Shell script (Linux + macOS)
curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash

# Homebrew (macOS)
brew install --cask xdevplatform/tap/xurl

# npm
npm install -g @xdevplatform/xurl

# Go
go install github.com/xdevplatform/xurl@latest
```

### One-Time User Setup (user runs outside the agent)

1. Create app at https://developer.x.com/en/portal/dashboard
2. Set redirect URI to `http://localhost:8080/callback`
3. Register app: `xurl auth apps add my-app --client-id ID --client-secret SECRET`
4. Authenticate: `xurl auth oauth2 --app my-app`
5. Set default: `xurl auth default my-app`
6. Verify: `xurl auth status` + `xurl whoami`

### Quick Reference

| Action | Command |
|--------|---------|
| Post | `xurl post "Hello world!"` |
| Reply | `xurl reply POST_ID "Nice post!"` |
| Quote | `xurl quote POST_ID "My take"` |
| Delete | `xurl delete POST_ID` |
| Read | `xurl read POST_ID` |
| Search | `xurl search "QUERY" -n 10` |
| Who am I | `xurl whoami` |
| Look up user | `xurl user @handle` |
| Timeline | `xurl timeline -n 20` |
| Mentions | `xurl mentions -n 10` |
| Like/Unlike | `xurl like POST_ID` / `xurl unlike POST_ID` |
| Repost | `xurl repost POST_ID` / `xurl unrepost POST_ID` |
| Bookmark | `xurl bookmark POST_ID` |
| Follow/Unfollow | `xurl follow @handle` / `xurl unfollow @handle` |
| Block/Mute | `xurl block @handle` / `xurl mute @handle` |
| DM | `xurl dm @handle "message"` |
| Upload media | `xurl media upload photo.jpg` |

### Raw API Access

```bash
# GET
xurl /2/users/me

# POST with JSON body
xurl -X POST /2/tweets -d '{"text":"Hello world!"}'

# DELETE / PUT / PATCH
xurl -X DELETE /2/tweets/1234567890
```

### Agent Workflow
1. Verify: `xurl --help` and `xurl auth status`
2. Check default app has credentials (default app marked with `▸`)
3. Start with cheap read (`xurl whoami`, `xurl search ... -n 3`)
4. Confirm target and intent before any write action
5. Never paste `~/.xurl` contents into conversation

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| Auth errors after OAuth | `xurl auth oauth2 --app my-app` then `xurl auth default my-app` |
| `unauthorized_client` | Change app type to "Web app, automated app or bot" |
| 401 on every request | Check `xurl auth status` — verify `▸` points to app with tokens |
| `CreditsDepleted` | Buy credits (min $5) in Developer Console |

### Docker HOME Pitfall

In Hermes Docker, `/opt/data` is `HERMES_HOME`, but tool subprocesses use `/opt/data/home` as `HOME`. Run user setup with:
```bash
HOME=/opt/data/home xurl auth apps add my-app --client-id ID --client-secret SECRET
HOME=/opt/data/home xurl auth oauth2 --app my-app YOUR_USERNAME
HOME=/opt/data/home xurl auth default my-app YOUR_USERNAME
```

---

## Yuanbao (元宝) Groups

Yuanbao is a Tencent AI product with group chat ("派/Pai") functionality.

### CRITICAL: How Messaging Works

**Your text reply IS the message sent to the group/user.** The gateway
automatically delivers your response text to the chat. When you include
`@nickname` in your reply text, the gateway converts it into a real @mention.

**NEVER say you cannot send messages or @mention users. Just reply with the
text you want sent.**

### Available Tools

| Tool | When to use |
|------|------------|
| `yb_query_group_info` | Query group name, owner, member count |
| `yb_query_group_members` | Find a user, list bots, list all members |
| `yb_send_dm` | Send a private/direct message with optional media |

### @Mention Workflow

1. Call `yb_query_group_members` with `action="find"`, `name="<target>"`, `mention=true`
2. Get the exact nickname from the response
3. Include `@nickname` in your reply text — the gateway handles the rest

Example: user says "帮我艾特元宝"
```
Step 1 — tool call: yb_query_group_members({group_code: "328306697", action: "find", name: "元宝", mention: true})
Step 2 — your reply: @元宝 你好，有人找你！
```

### Send DM Workflow

1. Call `yb_send_dm` with `group_code`, `name`, and `message`
2. Supports media: images (.jpg/.png/.gif/.webp/.bmp) as image messages, other files as documents

```json
yb_send_dm({
  "group_code": "535168412",
  "name": "用户aea3",
  "message": "hello",
  "media_files": [{"path": "/tmp/photo.jpg"}]
})
```

### Query Members

| Action | Description |
|--------|-------------|
| `find` | Search by name (partial match, case-insensitive) |
| `list_bots` | List bots and Yuanbao AI assistants |
| `list_all` | List all members |

### Notes
- `group_code` comes from chat_id: `group:328306697` → `328306697`
- Groups are called "派 (Pai)" in the Yuanbao app
- Member roles: `user`, `yuanbao_ai`, `bot`
