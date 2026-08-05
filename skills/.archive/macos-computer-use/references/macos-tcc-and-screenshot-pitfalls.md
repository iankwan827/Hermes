# macOS TCC Dialogs, Screenshots & Quartz Automation Pitfalls

## TCC Permission Dialogs — What Works and What Doesn't

macOS TCC (Transparency, Consent, and Control) dialogs are system-level prompts that appear when apps request access to protected resources (Screen Recording, Accessibility, Files, etc.). They come in several flavors with different programmatic interactability:

### Dialog Types and Clickability

| Dialog Type | Example Text | Clickable via Quartz CGEvent? | Notes |
|---|---|---|---|
| App data access | "python3.11 想访问其他 App 的数据" | ✅ YES (tested) | Standard TCC prompt, responds to Quartz mouse events at button coordinates |
| Screen Recording | "Python 想访问'屏幕录制'" | ❌ NO | Protected system dialog, does not respond to any programmatic click |
| `universalAccessAuthWarn` | Accessibility permission warning | ❌ NO | Persists even after quitting parent app; cannot be dismissed programmatically |
| Screen & System Audio | "允许下面的应用程序录制屏幕" | ❌ NO | Part of System Settings privacy page, not a standalone dialog |

### Methods That FAIL on Protected TCC Dialogs

1. **Quartz CGEvent mouse clicks** — events post successfully but dialog doesn't respond
2. **cliclick** — tool works (can move cursor, report position) but clicks have no effect on TCC dialogs
3. **osascript System Events `click at {x, y}`** — clicks land on wrong element or are swallowed
4. **Keyboard navigation** (Tab + Return, Escape) — dialog ignores keyboard events
5. **AppleScript `click button "允许"`** — cannot locate the button (dialog not accessible via AX tree)

### Why TCC Dialogs Are Protected

- They run in a separate security context managed by `securityd`/`tccd`
- They use a special window layer that doesn't respond to synthesized input events
- This is by design — prevents malware from auto-granting permissions

## Screenshot Methods on macOS

### Working Methods (in order of reliability)

1. **`screencapture -x /path.png`** — The gold standard. Fast, captures all windows, handles Retina. Requires Screen Recording permission.

2. **Quartz `CGDisplayCreateImage(displayID)`** — Captures the **entire display framebuffer** including all windows. Works even when `screencapture` is broken (no TCC Screen Recording permission needed). Returns a CGImage that can be saved via `CGImageDestinationCreateWithURL`. **This is the best fallback when screencapture fails.** Note: may show wallpaper-only on some configs; combine with `CGWindowListCopyWindowInfo` for window positions.

```python
from Quartz import (
    CGMainDisplayID, CGDisplayCreateImage,
    CGImageDestinationCreateWithURL, CGImageDestinationAddImage, CGImageDestinationFinalize
)
import Foundation

image = CGDisplayCreateImage(CGMainDisplayID())
url = Foundation.NSURL.fileURLWithPath_('/tmp/screenshot.png')
dest = CGImageDestinationCreateWithURL(url, 'public.png', 1, None)
CGImageDestinationAddImage(dest, image, None)
CGImageDestinationFinalize(dest)
```

**Requires:** `pip install pyautogui` (installs `pyobjc-framework-quartz` as dependency).

3. **Quartz `CGWindowListCopyWindowInfo`** — NOT a screenshot, but returns accurate window positions/sizes/bounds for all visible windows. Useful for finding dialog coordinates. Always works.

### Broken/Unreliable Methods

- **`mss` Python library** — On macOS, `mss` captures only the wallpaper, not windows. However, `pip install mss` also installs `pyobjc-framework-quartz`, which enables using `CGDisplayCreateImage` (see Working Methods above). So install it for the dependency, not for its own screenshot capability.
- **`pyautogui.screenshot()`** — Also uses screencapture under the hood.
- **`PIL.ImageGrab.grab()`** — Same underlying mechanism.

### ⚠️ CRITICAL: `tccutil reset ScreenCapture` DANGER

Running `tccutil reset ScreenCapture` **removes Screen Recording permission from ALL apps**, including Terminal. This breaks `screencapture` and all screenshot tools. Recovery requires:

1. Open **System Settings → Privacy & Security → Screen Recording**
2. Manually re-enable Terminal (and any other apps that need it)
3. Confirm the system prompt

**Never run `tccutil reset ScreenCapture` unless you can manually re-grant permissions.** If you're trying to fix a TCC issue, this makes it worse.

## Quartz-Based Desktop Automation (When computer_use Tool Is Unavailable)

### Finding Window Positions

```python
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID

windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
for w in windows:
    name = w.get('kCGWindowOwnerName', 'N/A')
    bounds = w.get('kCGWindowBounds', {})
    pid = w.get('kCGWindowOwnerPID', 0)
    # bounds = {X, Y, Width, Height} — actual screen coordinates
```

### Clicking with Quartz CGEvent (works for most UI, NOT TCC dialogs)

```python
import time
from Quartz import (
    CGEventCreateMouseEvent, CGEventPost, kCGHIDEventTap,
    kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGMouseButtonLeft,
    CGEventSetIntegerValueField, kCGMouseEventClickState
)

def quartz_click(x, y):
    for evt_type in [kCGEventLeftMouseDown, kCGEventLeftMouseUp]:
        evt = CGEventCreateMouseEvent(None, evt_type, (x, y), kCGMouseButtonLeft)
        CGEventSetIntegerValueField(evt, kCGMouseEventClickState, 1)
        CGEventPost(kCGHIDEventTap, evt)
        time.sleep(0.05)
```

**Requirements:** Must install `pyobjc-framework-quartz` (comes with `pip install pyautogui`).

### AppleScript for UI Navigation

AppleScript via `osascript` can navigate app UI hierarchies (find buttons, click elements, read text) **but requires Accessibility permission for Terminal**. Without it, you get "osascript不允许辅助访问 (-25211)".

```bash
# Check if Accessibility is granted:
osascript -e 'tell application "System Events" to tell process "Finder" to get name of window 1'
# If this works, Accessibility is granted. If error -25211, it's not.
```

### Chicken-and-Egg Problem

- To grant Accessibility permission, you need to click a system dialog
- To click a system dialog programmatically, you need Accessibility permission
- **Resolution:** User must manually grant Accessibility to Terminal in System Settings → Privacy & Security → Accessibility

## System Settings URL Schemes (macOS Ventura+)

```bash
# Open specific privacy pages:
open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
open "x-apple.systempreferences:com.apple.preference.security?Privacy"
```

## Navigation AppleScript Pattern for System Settings

```applescript
-- Navigate System Settings UI hierarchy:
-- Window → Group → Splitter Group → Group 3 (content) → Group 1 → Scroll Area → Group 1 → Scroll Area → Outline → Row → Cell
-- This is the path to the app list in privacy settings pages.

tell application "System Events"
    tell process "System Settings"
        set win to first window
        -- Drill down: group 1 → splitter group 1 → group 3 → group 1 → scroll area 1 → group 1 → scroll area 1
        set scrollArea to scroll area 1 of group 1 of group 3 of splitter group 1 of group 1 of win
        set innerScroll to scroll area 1 of group 1 of scrollArea
        set allChildren to entire contents of innerScroll
        -- Find checkboxes (toggle permissions on/off)
        repeat with e in allChildren
            if role of e is "AXCheckBox" then
                click e  -- toggles the permission
            end if
        end repeat
    end tell
end tell
```
