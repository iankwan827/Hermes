---
name: github-operations
description: "Complete GitHub workflow: authentication, PR lifecycle, issue management, repo operations, code review, and codebase analysis. Unified entry point for all GitHub tasks."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, Issues, Code-Review, Authentication, Git, CI/CD, Repositories]
    related_skills: [codebase-inspection]
---

# GitHub Operations

Complete guide for working with GitHub. Every section shows the `gh` CLI path first, then the `git` + `curl` fallback for machines without `gh`.

## Prerequisites

- Authenticated with GitHub (see **Authentication** section below)
- Inside a git repository with a GitHub remote (for repo-specific operations)

---

## 1. Authentication

### Detection Flow

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**Decision tree:**
1. If `gh auth status` shows authenticated → use `gh` for everything
2. If `gh` is installed but not authenticated → use `gh auth` method
3. If `gh` is not installed → use git-only method (no sudo needed)

### Method 1: Git-Only Authentication

**Option A: HTTPS with Personal Access Token (Recommended)**

Go to https://github.com/settings/tokens → Generate new token (classic):
- Scopes: `repo`, `workflow`, `read:org`
- Expiration: 90 days

```bash
git config --global credential.helper store
git ls-remote https://github.com/<username>/<any-repo>.git
# Enter username + paste token as password
```

**Option B: SSH Key Authentication**

```bash
ssh-keygen -t ed25519 -C "email@example.com" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub  # Add to https://github.com/settings/keys
ssh -T git@github.com  # Verify
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

### Method 2: gh CLI Authentication

```bash
gh auth login  # Interactive browser login
echo "<TOKEN>" | gh auth login --with-token  # Token-based (headless)
gh auth setup-git  # Set up git credentials through gh
```

### Auth Detection Helper (for scripts)

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH_METHOD=gh
elif [ -n "$GITHUB_TOKEN" ]; then
  AUTH_METHOD=curl
elif [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
  AUTH_METHOD=curl
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  AUTH_METHOD=curl
else
  AUTH_METHOD=none
fi
```

### Extracting Owner/Repo from Git Remote

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password | Use personal access token as password, or switch to SSH |
| `remote: Permission denied` | Token may lack `repo` scope |
| `fatal: Authentication failed` | Run `git credential reject` then re-authenticate |
| SSH port 22 refused | Add `Host github.com` with `Port 443` and `Hostname ssh.github.com` to `~/.ssh/config` |

---

## 2. Pull Request Workflow

### Branch Creation

```bash
git fetch origin
git checkout main && git pull origin main
git checkout -b feat/add-user-authentication
```

Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`, `ci/`

### Making Commits (Conventional Commits)

```
type(scope): short description

feat, fix, refactor, docs, test, ci, chore, perf
```

```bash
git add src/auth.py tests/test_auth.py
git commit -m "feat: add JWT-based user authentication"
```

### Pushing and Creating a PR

```bash
git push -u origin HEAD

# With gh:
gh pr create --title "feat: add JWT auth" --body "## Summary\n...\n\nCloses #42"

# With curl:
BRANCH=$(git branch --show-current)
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{\"title\":\"feat: add JWT auth\",\"head\":\"$BRANCH\",\"base\":\"main\"}"
```

### Monitoring CI Status

```bash
gh pr checks          # One-shot
gh pr checks --watch  # Poll until complete

# With curl:
SHA=$(git rev-parse HEAD)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status
```

### Auto-Fix CI Failures Loop

1. Check CI status → identify failures
2. Read failure logs → understand the error
3. Fix with `patch`/`write_file` → `git add . && git commit -m "fix: ..." && git push`
4. Wait for CI → re-check (up to 3 attempts, then ask user)

### Merging

```bash
gh pr merge --squash --delete-branch  # With gh

# With curl:
curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d '{"merge_method":"squash"}'
```

---

## 3. Code Review

### Reviewing Local Changes (Pre-Push)

```bash
git diff main...HEAD --stat   # Big picture
git diff main...HEAD          # Full diff

# Check for issues:
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME"
git diff main...HEAD | grep -in "password\|secret\|api_key"
```

### Review Output Format

```
## Code Review Summary

### Critical
- **file:line** — Issue description

### Warnings
- **file:line** — Issue description

### Suggestions
- **file:line** — Improvement suggestion

### Looks Good
- Positive observations
```

### Review Checklist

- **Correctness:** Edge cases, error paths, does it do what it claims?
- **Security:** Hardcoded secrets, input validation, SQL injection, XSS
- **Quality:** Naming, DRY, single responsibility, unnecessary complexity
- **Testing:** New paths tested? Happy + error cases covered?
- **Performance:** N+1 queries, unnecessary loops, blocking in async

### Reviewing a PR on GitHub

```bash
gh pr view 123
gh pr diff 123
gh pr checkout 123  # Check out locally for full review

# Leave comments:
gh pr comment 123 --body "Looks good, a few suggestions."
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
```

### Inline Review Comments

```bash
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')
gh api repos/$OWNER/$REPO/pulls/123/comments --method POST \
  -f body="Simplify with list comprehension." \
  -f path="src/auth/login.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 -f side="RIGHT"
```

---

## 4. Issue Management

### Viewing Issues

```bash
gh issue list --state open --label "bug"
gh issue view 42
gh issue list --search "authentication error" --state all
```

### Creating Issues

```bash
gh issue create --title "Login redirect bug" --body "## Steps to Reproduce\n1. ...\n2. ..." --label "bug,backend"
```

### Managing Issues

```bash
gh issue edit 42 --add-label "priority:high"
gh issue edit 42 --add-assignee @me
gh issue comment 42 --body "Investigating..."
gh issue close 42
gh issue reopen 42
```

### Issue Triage Workflow

1. List untriaged: `gh issue list --label "needs-triage"`
2. Read and categorize each issue
3. Apply labels and priority
4. Assign if owner is clear
5. Comment with triage notes

---

## 5. Repository Management

### Cloning and Creating

```bash
gh repo clone owner/repo-name
gh repo create my-new-project --public --clone
gh repo create my-org/my-project --private --description "A tool" --license MIT --clone
gh repo create my-project --source . --public --push  # From existing dir
```

### Forking and Syncing

```bash
gh repo fork owner/repo-name --clone
gh repo sync $USER/repo-name  # Keep fork in sync
```

### Settings and Configuration

```bash
gh repo edit --description "Updated" --visibility public
gh repo edit --enable-auto-merge
gh repo edit --add-topic "machine-learning,python"
```

### Branch Protection

```bash
curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{"required_status_checks":{"strict":true,"contexts":["ci/test"]},"required_pull_request_reviews":{"required_approving_review_count":1}}'
```

### Secrets Management

```bash
gh secret set API_KEY --body "value"
gh secret list
gh secret delete API_KEY
```

### Releases

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release list
gh release download v1.0.0 --dir ./downloads
```

### GitHub Actions

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID> --failed
gh workflow run ci.yml --ref main
```

### Gists

```bash
gh gist create script.py --public --desc "Useful script"
gh gist list
```

---

## 6. Codebase Inspection

Analyze repositories for lines of code, language breakdown, and code-vs-comment ratios using `pygount`.

### Prerequisites

```bash
pip install pygount
```

### Basic Summary

```bash
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build" \
  /path/to/repo
```

**Always use `--folders-to-skip`** — without it, pygount crawls everything and may hang.

### Filter by Language

```bash
pygount --suffix=py --format=summary .
```

### Interpretation

- `__empty__` = empty files
- `__binary__` = images, compiled files
- `__generated__` = auto-generated files
- Markdown shows 0 code lines (all content is "comments") — this is expected

---

## Quick Reference

| Action | gh | curl endpoint |
|--------|-----|--------------|
| List PRs | `gh pr list` | `GET /repos/{o}/{r}/pulls` |
| Create PR | `gh pr create ...` | `POST /repos/{o}/{r}/pulls` |
| Review PR | `gh pr review N --approve` | `POST /repos/{o}/{r}/pulls/N/reviews` |
| List issues | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| Create issue | `gh issue create ...` | `POST /repos/{o}/{r}/issues` |
| Clone repo | `gh repo clone o/r` | `git clone` |
| Create repo | `gh repo create name` | `POST /user/repos` |
| Fork repo | `gh repo fork o/r` | `POST /repos/o/r/forks` |
| Create release | `gh release create v1.0` | `POST /repos/o/r/releases` |
| List workflows | `gh workflow list` | `GET /repos/o/r/actions/workflows` |
| Set secret | `gh secret set KEY` | `PUT /repos/o/r/actions/secrets/KEY` |

## Pitfalls

1. **GitHub disabled password auth** — always use personal access tokens or SSH
2. **Token scope matters** — `repo` for full access, `workflow` for Actions
3. **curl + markdown `***`** — shell interprets `***` as glob; write scripts to files when authorization headers contain special chars
4. **PRs show in /issues** — filter with `'pull_request' not in i` when using the issues API
5. **Multiple accounts** — use SSH with different keys per host alias in `~/.ssh/config`

## References

- `references/github-api-cheatsheet.md` — API endpoints quick reference
- `references/ci-troubleshooting.md` — CI failure diagnosis patterns
- `references/conventional-commits.md` — Commit message format guide
- `templates/pr-body-bugfix.md` — PR body template for bug fixes
- `templates/pr-body-feature.md` — PR body template for features
- `templates/bug-report.md` — Issue template for bugs
- `templates/feature-request.md` — Issue template for feature requests
- `scripts/gh-env.sh` — Auth detection and env setup script
