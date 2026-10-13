---
name: coding-agents
description: "Delegate coding tasks to external autonomous coding CLIs (Claude Code, Codex, OpenCode). Unified orchestration guide for all coding agent integrations."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Codex, OpenCode, Autonomous, Refactoring, Code-Review, Delegation]
    related_skills: [claude-code, codex, opencode]
---

# Coding Agents

Delegate coding tasks to external autonomous coding CLIs. This skill covers the shared orchestration patterns; see each agent's detailed guide for CLI-specific flags and features.

## Supported Agents

| Agent | Install | Auth | PTY Required | One-Shot Mode |
|-------|---------|------|-------------|---------------|
| **Claude Code** | `npm i -g @anthropic-ai/claude-code` | OAuth or `ANTHROPIC_API_KEY` | Interactive: yes; Print: no | `claude -p "task"` |
| **Codex** | `npm i -g @openai/codex` | OAuth or `OPENAI_API_KEY` | Yes (TUI) | `codex exec "task"` |
| **OpenCode** | `npm i -g opencode-ai` or `brew install anomalyco/tap/opencode` | `opencode auth login` | Interactive: yes; Run: no | `opencode run "task"` |

## When to Use

- User explicitly asks to use a specific coding agent
- Task needs an autonomous coding agent (feature build, refactor, PR review)
- Long-running coding session with progress checks
- Parallel task execution in isolated workdirs/worktrees

## Shared Orchestration Patterns

### One-Shot (Preferred for most tasks)

```bash
# Claude Code
terminal(command="claude -p 'Add error handling to src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/project", timeout=120)

# Codex
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="/project", pty=true)

# OpenCode
terminal(command="opencode run 'Add retry logic to API calls'", workdir="/project")
```

### Interactive (Background + PTY)

For multi-turn iterative work:

```bash
# Start in background with PTY
terminal(command="<agent>", workdir="/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send follow-up
process(action="submit", session_id="<id>", data="Now add tests")

# Exit
process(action="kill", session_id="<id>")
```

### Parallel Execution

Use separate worktrees to avoid collisions:

```bash
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="/project")

# Launch agents in parallel
terminal(command="claude -p 'Fix issue #78' --allowedTools 'Read,Edit' --max-turns 10", workdir="/tmp/issue-78", background=true)
terminal(command="claude -p 'Fix issue #99' --allowedTools 'Read,Edit' --max-turns 10", workdir="/tmp/issue-99", background=true)

process(action="list")
```

### PR Review Pattern

```bash
# Clone to temp dir for safe review
REVIEW=$(mktemp -d)
git clone https://github.com/user/repo.git $REVIEW
cd $REVIEW && gh pr checkout 42

# Claude Code
claude -p 'Review PR #42 thoroughly' --from-pr 42 --max-turns 10

# Codex
codex exec 'Review this PR vs main. Report bugs and security risks.'

# OpenCode
opencode pr 42
```

## Agent Selection Guide

| Task | Recommended Agent | Why |
|------|------------------|-----|
| Feature build (complex) | Claude Code (opus) | Best multi-step reasoning |
| Bug fix (focused) | Claude Code (sonnet) or Codex | Fast, reliable |
| PR review | Claude Code | Built-in PR review from number |
| Batch issue fixing | Codex | Fast parallel execution with worktrees |
| Provider-agnostic | OpenCode | Works with any provider |
| Cost-sensitive | OpenCode (--model openrouter/...) | Use cheaper models |

## Common Pitfalls

1. **All agents require git repos** — Codex refuses to run outside one; others strongly prefer it
2. **PTY for interactive mode** — Codex and OpenCode TUIs hang without `pty=true`
3. **Clean up worktrees** — `git worktree remove /tmp/issue-78` after completion
4. **Monitor, don't poll** — use `process(action="poll")` not blind sleep loops
5. **Report outcomes** — summarize files changed, tests passed, remaining risks
6. **`/exit` not valid in OpenCode** — use Ctrl+C or `process(action="kill")`
7. **Claude trust dialog** — first launch in a new directory requires Enter to accept; permissions dialog requires Down+Enter
8. **Session resumption** — Claude requires same directory; Codex/OpenCode use session IDs

## References

- `references/claude-code-flags.md` — Complete Claude Code CLI flags reference
- `references/codex-workflows.md` — Codex-specific workflows and patterns
- `references/opencode-tui.md` — OpenCode TUI keybindings and session management
