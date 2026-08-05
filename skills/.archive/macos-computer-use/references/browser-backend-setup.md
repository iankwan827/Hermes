## Browser Backend Setup & Troubleshooting (macOS)

## Quick Diagnosis

When `browser_navigate` fails with connection errors:

1. **Check if camofox is the configured backend:**
   ```bash
   grep CAMOFOX_URL ~/.hermes/profiles/main/.env
   ```
   If `CAMOFOX_URL=http://localhost:9377` is set but camofox isn't running, all browser ops will 502.

2. **Fix: switch to local agent-browser backend:**
   ```bash
   # Comment out CAMOFOX_URL in .env
   sed -i '' 's|^CAMOFOX_URL=|# CAMOFOX_URL=|' ~/.hermes/profiles/main/.env
   
   # Set cloud_provider to local
   hermes config set browser.cloud_provider local
   
   # MUST /reset to reload .env — changes don't take effect mid-session
   ```

3. **If agent-browser launches wrong browser (e.g. Edge instead of Chrome):**
   ```bash
   cat ~/.agent-browser/config.json
   # Fix executablePath to correct Chrome path:
   # /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
   ```

## Dynamic CDP Port Mismatch

The most common cause of browser tool failure: Hermes expects CDP on a specific port, but agent-browser's Chrome listens on a **dynamic port** that changes every restart.

### Root Cause
agent-browser launches Chrome with `--remote-debugging-port=0` (OS-assigned) by default. Each restart gets a new port. The `cdp_url` in Hermes config becomes stale immediately.

### Fix: Pin the Port (Permanent Solution)

**Step 1 — Configure agent-browser to always use port 9333:**
```bash
cat > ~/.agent-browser/config.json << 'EOF'
{
  "executablePath": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "headed": false,
  "args": "--remote-debugging-port=9333"
}
EOF
```

**Step 2 — Set Hermes to always point to 9333:**
```bash
hermes config set browser.cdp_url http://localhost:9333
```

**Step 3 — Restart gateway from OUTSIDE hermes:**
```bash
hermes gateway restart
```

After this, both sides are pinned to 9333 and never need changing again.

### ⚠️ Pitfall: Chrome Killed on Gateway Restart

When `hermes gateway restart` runs, **Chrome gets killed too** (even if launched independently). The CDP port goes dead. After every gateway restart, you MUST relaunch Chrome:

```bash
# CORRECT: Use direct binary launch (NOT open -a!)
pkill -9 -f Chrome 2>/dev/null; sleep 2
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9333 \
  --user-data-dir=/tmp/hermes-chrome-profile &
```

Then verify:
```bash
sleep 5 && curl -s http://localhost:9333/json/version
```

**⚠️ CRITICAL: Do NOT use `open -a` — it doesn't reliably pass `--remote-debugging-port`!**
- `open -a "Google Chrome" --args --remote-debugging-port=9333` → port 9333 never comes up
- Direct binary launch → port 9333 works reliably
- This was verified in production: `open -a` leaves Chrome running but port 9333 shows nothing in `lsof`

**Quick restart workflow (copy-paste):**
```bash
pkill -9 -f Chrome 2>/dev/null; sleep 2
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9333 \
  --user-data-dir=/tmp/hermes-chrome-profile &
sleep 5 && curl -s http://localhost:9333/json/version | head -3
```

### ⚠️ Pitfall: User Data Dir Causes Binding Failure

When launching Chrome with `--user-data-dir="$HOME/Library/Application Support/Google/Chrome"` (the user's real profile), Chrome may **fail to bind the debugging port** even though the process is running. Symptoms:
- `ps aux` shows Chrome with `--remote-debugging-port=9333`
- But `lsof -i :9333` shows nothing, `curl localhost:9333` fails
- Chrome helpers (GPU, renderer, utility) all start normally

**Cause:** macOS profile lock (`SingletonLock`) or Chrome's internal state prevents the debug port from binding when reusing an existing profile with remote debugging.

**Workaround:** Use a temporary user-data-dir for headless debugging:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new --remote-debugging-port=9333 \
  --user-data-dir=/tmp/chrome-debug \
  --no-first-run --no-default-browser-check
```
This works reliably. The tradeoff: no login sessions from the user's real Chrome.

**For login-required flows (OAuth, etc.):** The user must either:
1. Scan QR code in the headless Chrome, or
2. Manually upload/drag the file to the target service

### Diagnosis Commands
```bash
# Find actual Chrome CDP port
lsof -i -P | grep LISTEN | grep -E "(agent-browser|Google Chrome)"

# Test CDP connectivity
curl -s http://localhost:<port>/json/version

# Check Chrome process arguments
ps aux | grep "Google Chrome" | grep -v Helper | grep -v grep
```

### Alternative: Use agent-browser CLI directly
If browser tools keep failing, agent-browser CLI works independently:
```bash
agent-browser open https://www.baidu.com
agent-browser snapshot
agent-browser click <ref>
```

## Key Pitfall: .env Changes Need /reset

Environment variables from `.env` are loaded at session start. Changing `.env` mid-session has **no effect** until `/reset` or a new session. This applies to CAMOFOX_URL, BROWSER_CDP_URL, and all other env-based config.

## Key Pitfall: Config Changes Need Gateway Restart

`browser.cdp_url` changes via `hermes config set` require restarting the gateway from **outside** the running hermes session. Running `hermes gateway restart` from inside hermes is blocked to prevent restart loops.

## Fallback: AppleScript Content Extraction from Chrome

When browser tools fail (CDP connection refused, port mismatch, etc.) but Chrome is running normally, use AppleScript to extract page content directly. This is NOT remote control — it reads the current tab's text without manipulating the browser.

**Prerequisites:** Chrome → View → Developer → ✓ Allow JavaScript from AppleEvents

**Find and extract from a specific tab:**
```bash
osascript -e '
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "TARGET_URL_FRAGMENT" then
                set pageText to execute t javascript "document.body.innerText"
                return pageText
            end if
        end repeat
    end repeat
end tell
'
```

**List all open tabs:**
```bash
osascript -e '
tell application "Google Chrome"
    set tabList to {}
    repeat with w in windows
        repeat with t in tabs of w
            set end of tabList to URL of t & " | " & title of t
        end repeat
    end repeat
    return tabList
end tell
'
```

**Save extracted content to file:**
```bash
osascript -e '...' > /tmp/extracted.txt
```

**Pitfalls:**
- Must enable "Allow JavaScript from AppleEvents" in Chrome Developer menu first
- AppleScript `execute t javascript` only works when Chrome has focus or the permission is granted
- For long pages, the output may be truncated — use `> /tmp/file.txt` to capture fully
- This reads `document.body.innerText` (plain text), not HTML — tables come as tab-separated text

## Backend Priority Order

The browser tool resolves backends in this order:
1. `BROWSER_CDP_URL` env var (live override from `/browser connect`)
2. `browser.cdp_url` in config.yaml
3. `CAMOFOX_URL` env var → routes through camofox REST API
4. `browser.cloud_provider` setting → `local` = agent-browser, or cloud provider
5. Default: local agent-browser

## Setup from Scratch (no camofox)

```bash
# 1. Install agent-browser
npm install -g agent-browser

# 2. Download Chromium
agent-browser install

# 3. Verify correct browser in config
cat ~/.agent-browser/config.json
# Should point to Chrome, not Edge or other browsers

# 4. Pin the CDP port (see "Fix: Pin the Port" above)

# 5. Ensure .env has no CAMOFOX_URL (commented out)
# 6. Ensure config.yaml has browser.cloud_provider: local
hermes config set browser.cloud_provider local

# 7. Set fixed CDP URL
hermes config set browser.cdp_url http://localhost:9333

# 8. Restart gateway
hermes gateway restart

# 9. Test
agent-browser open https://www.baidu.com
```