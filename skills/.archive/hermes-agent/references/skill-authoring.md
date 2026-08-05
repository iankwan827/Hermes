# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo:** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `/home/bb/hermes-agent/skills/` (use `patch` for small edits, `write_file` for rewrites)

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape:

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` are NOT enforced by the validator, but every peer has them.

## Size Limits

- Description: ≤ 1024 chars (enforced).
- Full SKILL.md: ≤ 100,000 chars (enforced as `MAX_SKILL_CONTENT_CHARS`, ~36k tokens).
- Peer skills in `software-development/` sit at **8-14k chars**. Aim for that range. If pushing past 20k, split into `references/*.md` and reference them from SKILL.md.

## Peer-Matched Structure

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables
- Code blocks with exact commands
- Hermes-specific recipes

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications
```

## Directory Placement

```
skills/<category>/<skill-name>/SKILL.md
```

Pick the closest existing category. Don't invent new top-level categories casually.

## Workflow

1. Survey peers in the target category
2. Check validator constraints in `tools/skill_manager_tool.py`
3. Draft with `write_file`
4. Validate locally (check frontmatter, name length, description length, total size)
5. Git add + commit

## Editing Existing In-Repo Skills

- **Small fix:** `skill_manage(action='patch')` works fine
- **Major rewrite:** `write_file` the whole SKILL.md
- **Supporting files:** `write_file` to `references/`, `templates/`, or `scripts/`

## Common Pitfalls

1. **Using `skill_manage(action='create')` for in-repo.** It writes to `~/.hermes/skills/`, not the repo. Use `write_file`.
2. **Leading whitespace before `---`.** Validator checks `content.startswith("---")`.
3. **Description too generic.** Start with "Use when ..." and describe trigger class.
4. **Writing a skill that duplicates a peer.** Survey first. Prefer extending over creating.
5. **Expecting current session to see new skill.** It won't — loader is cached at session start.
