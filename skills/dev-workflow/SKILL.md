---
name: dev-workflow
description: "Complete software development methodology: plan (spike), test (TDD), debug (systematic root cause), verify (pre-commit review). One skill for the full dev lifecycle."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [development, workflow, tdd, debugging, code-review, spike, methodology, quality]
    related_skills: [hermes-agent, github-operations]
---

# Dev Workflow: Complete Software Development Methodology

A unified entry point for the full software development lifecycle. This skill orchestrates four complementary practices — each has its own detailed skill for deep dives, but this umbrella tells you **when to load which** and **how they connect**.

## The Lifecycle

```
Explore → Plan → Test → Build → Debug → Review → Ship
  spike   plan    TDD    impl   debug   review   commit
```

| Phase | Practice | Detailed Skill | When |
|-------|----------|---------------|------|
| **Explore** | Spike | `spike` | Validating feasibility before committing to an approach |
| **Plan** | Architecture | `plan` (protected) | Structured implementation planning |
| **Test** | TDD | `test-driven-development` | Writing tests before code (RED-GREEN-REFACTOR) |
| **Build** | Implementation | — | Writing the actual code |
| **Debug** | Systematic debugging | `systematic-debugging` | Finding root cause before fixing |
| **Review** | Code review | `requesting-code-review` | Pre-commit verification pipeline |
| **Ship** | Commit | — | Clean, verified commits |

## When to Load Which Skill

### When to use (see `references/spike.md` for full guide):
- The user wants to **try something before committing** to a real build
- "Is this even possible?", "compare A vs B", "quick prototype"
- You need to validate an approach, not implement it
- **Don't use for production work** — use `plan` + TDD instead

### When to use (see `references/test-driven-development.md` for full guide):
- Writing **new features**, **bug fixes**, or **refactoring**
- The user says "implement", "build", "add", "fix"
- You need tests to prove your code works
- **Always use this** unless the user explicitly says to skip TDD

### When to use (see `references/systematic-debugging.md` for full guide):
- A test is failing and you don't know why
- Something is broken in production
- You've tried multiple fixes and none worked
- Performance problems, build failures, integration issues
- **Never guess** — always find root cause first

### When to use (see `references/requesting-code-review.md` for full guide):
- After implementing a feature (2+ file edits in a git repo)
- The user says "commit", "push", "ship", "done", "verify"
- After completing each task in a multi-task workflow
- **Skip for** documentation-only changes, pure config tweaks

## How They Connect

### TDD + Debugging (the core loop)
When a test fails during TDD:
1. **Don't fix the code** — first understand WHY it fails (see `references/systematic-debugging.md` Phase 1)
2. Find the root cause
3. THEN implement the minimal fix (TDD GREEN phase)
4. Verify the test passes

### Debugging + Code Review (the verification loop)
After debugging and fixing:
1. Write a regression test (TDD RED-GREEN)
2. Load `requesting-code-review` to verify the fix (see `references/requesting-code-review.md`)
3. The independent reviewer catches what you missed

### Spike → TDD (the exploration-to-implementation handoff)
After a spike validates an approach (see `references/spike.md`):
1. **Throw away the spike code** — it was disposable
2. Write tests for the validated approach (TDD)
3. Implement from tests, not from spike code

### Code Review + TDD (the quality gate)
After implementing with TDD:
1. Load `requesting-code-review` (see `references/requesting-code-review.md`)
2. The reviewer checks: tests exist? Tests pass? No regressions?
3. If issues found → auto-fix loop → re-verify

## Quick Reference: The Iron Laws

| Skill | Iron Law |
|-------|----------|
| **TDD** | NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST |
| **Debugging** | NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST |
| **Code Review** | NO COMMIT WITHOUT INDEPENDENT VERIFICATION |
| **Spike** | SPIKE CODE IS DISPOSABLE — THROW IT AWAY |

## Common Rationalizations (Don't Fall for These)

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "Skip debugging, just try fixing" | Random fixes waste 2-3 hours. Systematic takes 15-30 min. |
| "I'll review my own code" | Fresh eyes find what you miss. Always use independent reviewer. |
| "Spike code works, I'll clean it up" | Spike code is disposable. Rewrite with TDD. |
| "Tests after achieve the same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "Emergency, no time for process" | Systematic is FASTER than thrashing under pressure. |

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Skip the test, I'll manually verify"
- "Code before test, I'll add tests later"
- "One more fix attempt" (after 2+ failures)
- "I'll review my own changes"

**ALL of these mean: Stop. Load the appropriate skill. Follow the process.**

## Integration with Other Skills

- **`hermes-agent`**: For Hermes-specific development (tools, plugins, CLI)
- **`github-operations`**: For PR lifecycle, branch management, CI/CD
- **`plan`** (protected): For structured implementation planning before TDD

## Reference Files

Detailed methodology for each practice lives in this skill's `references/` directory:
- `references/test-driven-development.md` — RED-GREEN-REFACTOR cycle, test patterns, anti-patterns
- `references/systematic-debugging.md` — 4-phase root cause analysis, language-specific debuggers
- `references/requesting-code-review.md` — Pre-commit verification pipeline, security scan, auto-fix
- `references/spike.md` — Throwaway experiments, comparison spikes, verdict format
