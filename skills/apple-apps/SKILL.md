---
name: apple-apps
description: "macOS Apple app integrations: Notes, Reminders, Find My, iMessage — all via CLI tools."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Apple, macOS, Notes, Reminders, FindMy, iMessage, CLI, productivity]
---

# Apple Apps — macOS CLI Integrations

Umbrella skill for interacting with Apple's built-in macOS applications from the terminal. Each sub-skill covers one app, its CLI tool, prerequisites, and common workflows.

## Sub-skills

| App | CLI Tool | Install | Use Case |
|-----|----------|---------|----------|
| **Notes** | `memo` | `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo` | Create, search, edit Apple Notes. Cross-device iCloud sync. |
| **Reminders** | `remindctl` | `brew install steipete/tap/remindctl` | Add, list, complete tasks. Due dates sync to iPhone/iPad. |
| **Find My** | AppleScript + screenshot | Built-in (no CLI) | Track AirTags, devices, items via FindMy.app UI automation. |
| **iMessage** | `imsg` | `brew install steipete/tap/imsg` | Send/receive iMessages/SMS. Read conversation history. |

## Quick Reference

### Apple Notes (`memo`)
```bash
memo notes                        # List all notes
memo notes -f "Folder Name"       # Filter by folder
memo notes -s "query"             # Search notes (fuzzy)
memo notes -a "Note Title"        # Quick add with title
memo notes -e                     # Interactive edit
memo notes -m                     # Move note to folder
memo notes -ex                    # Export to HTML/Markdown
```
**Limitations:** Cannot edit notes with images/attachments. macOS only.

### Apple Reminders (`remindctl`)
```bash
remindctl today                   # Today's reminders
remindctl week                    # This week
remindctl overdue                 # Past due
remindctl add --title "Task" --due tomorrow
remindctl add --title "Meeting" --due "2026-02-15 09:00" --alarm "2026-02-15 08:30"
remindctl complete 1 2 3          # Complete by ID
remindctl today --json            # JSON output
```
**Key distinction:** `--due` = reminder due date; `--alarm` = notification trigger time.

### Find My (AppleScript + screenshot)
```bash
osascript -e 'tell application "FindMy" to activate'
sleep 3
screencapture -w -o /tmp/findmy.png
# Then: vision_analyze(image_url="/tmp/findmy.png", question="What devices are shown and their locations?")
```
**Critical:** FindMy has no CLI. AirTags only update while the app is in the foreground. Use `peekaboo` for better UI automation if available.

### iMessage (`imsg`)
```bash
imsg chats --limit 10 --json                     # List chats
imsg history --chat-id 1 --limit 20 --json       # View history
imsg send --to "+14155551212" --text "Hello!"     # Send text
imsg send --to "+14155551212" --text "Hi" --file /path/to/image.jpg  # With attachment
imsg watch --chat-id 1 --attachments              # Watch for new messages
```
**Safety:** Always confirm recipient and message content before sending.

## Rules

1. **Clarify intent:** When user says "remind me", clarify: Apple Reminders (syncs to phone) vs agent cronjob alert.
2. **Cross-device sync:** Apple Notes and Reminders sync via iCloud — prefer them when the user needs phone access.
3. **Obsidian distinction:** Use the `obsidian` skill for Markdown-native knowledge management, not Apple Notes.
4. **Privacy:** Only track devices/items the user owns via Find My.
5. **No secrets:** Never type passwords, API keys, or credit card numbers via any of these tools.
