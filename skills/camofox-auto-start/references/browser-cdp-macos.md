# macOS Chrome CDP Setup Reference

## Working Configuration (2026-07-03 verified)

### Chrome Launch Command
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check
```

### Hermes Config
```bash
hermes config set browser.cdp_url "ws://127.0.0.1:9222"
```

Config path: `~/.hermes/profiles/main/config.yaml` (sets `browser.cdp_url`)

### Verification
```bash
curl -s http://127.0.0.1:9222/json/version
```
Expected response includes `"Browser": "Chrome/149.0.7827.200"` (or similar version).

## How CDP Connection Works

1. `browser.cdp_url` tells Hermes where to find the CDP WebSocket endpoint
2. The browser tool resolves this via `_resolve_cdp_endpoint()` in `browser_cdp_tool.py`
3. Precedence: `BROWSER_CDP_URL` env var > `browser.cdp_url` in config.yaml
4. Once configured, all `browser_navigate`, `browser_click`, etc. route through this connection

## Why Safari Doesn't Work

Safari uses WebKit's Web Inspector protocol, not Chrome DevTools Protocol (CDP).
Hermes browser tools only support CDP, which means Chromium-family browsers:
- Google Chrome ✅
- Brave ✅
- Microsoft Edge ✅
- Chromium ✅
- Safari ❌ (WebKit, different protocol)
- Firefox ❌ (uses own remote debugging protocol, unless via Camofox)

## Platform Toolset Note

After `hermes tools enable browser`, the toolset is enabled but needs:
1. A running browser backend (CDP or cloud)
2. The CDP URL configured (for local mode)
3. Gateway restart or `/reset` for config changes to take effect

The `hermes status --all` output shows browser status:
- `Browserbase ✗` = no cloud credentials
- `Browser Use ✗` = no cloud credentials
- These are cloud providers; local CDP doesn't show here
