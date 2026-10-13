---
name: kanban
description: "Hermes Kanban multi-agent workflow: orchestrator decomposition playbook + worker pitfalls and patterns. Complete guide for routing, executing, and recovering kanban tasks."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, workflow, collaboration, routing]
    related_skills: []
---

# Kanban — Multi-Agent Workflow

Complete guide for Hermes Kanban: the orchestrator decomposition playbook and the worker execution patterns. The core worker lifecycle (6 steps: orient → work → heartbeat → block/complete) is auto-injected into every kanban worker via `KANBAN_GUIDANCE`. This skill is the deeper detail for both roles.

---

## Part 1: Orchestrator — Decomposition Playbook

### When to Use the Board (vs. just doing the work)

Create Kanban tasks when:
1. **Multiple specialists are needed** — research + analysis + writing = three profiles
2. **Work should survive a crash or restart** — long-running, recurring, or important
3. **User might want to interject** — human-in-the-loop at any step
4. **Multiple subtasks can run in parallel** — fan-out for speed
5. **Review/iteration is expected** — reviewer profile loops on drafter output
6. **Audit trail matters** — board rows persist in SQLite forever

If none apply (small one-shot task) — use `delegate_task` or answer directly.

### Profiles Are User-Configured

There is **no default specialist roster**. Before fanning out:

```bash
hermes profile list  # Discover available profiles
```

Cache the result. The dispatcher silently fails to spawn unknown assignees.

### The Anti-Temptation Rules

- **Do not execute the work yourself.** Route, don't execute.
- **For any concrete task, create a Kanban task and assign it.** Every time.
- **Split multi-lane requests before creating cards.** One card per lane.
- **Run independent lanes in parallel.** Link only true data dependencies.
- **Never create dependent work as independent ready cards.** Use `parents=[...]`.
- **If no specialist fits, ask the user.** Don't invent profile names.

### Decomposition Playbook

**Step 1 — Understand the goal.** Ask clarifying questions if ambiguous.

**Step 2 — Sketch the task graph.** Before creating anything, draft the graph:

```python
# Example: "Research Postgres migration"
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="<researcher-profile>",
    body="Compare infrastructure costs over 3-year window.",
)
t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="<researcher-profile>",
    body="Compare query latency and throughput at expected volume.",
)
t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="<analyst-profile>",
    body="Read T1 + T2 findings. Produce 1-page recommendation.",
    parents=[t1, t2],  # Gates promotion until T1+T2 done
)
t4 = kanban_create(
    title="draft decision memo",
    assignee="<writer-profile>",
    body="Turn recommendation into CTO memo.",
    parents=[t3],
)
```

**Step 3 — Create tasks and link.** Parent-first order. Children created with unfinished parents start in `todo` and auto-promote to `ready` when all parents complete.

**Step 4 — Complete your own task** (if spawned as orchestrator):

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 research lanes parallel, 1 synthesis, 1 prose",
    metadata={"task_graph": {"T1": {"assignee": "researcher", "parents": []}, ...}},
)
```

**Step 5 — Report back** in plain prose, naming actual profiles.

### Common Patterns

- **Fan-out + fan-in:** N research cards → 1 synthesis card
- **Parallel implementation + validation:** implementer + researcher in parallel → reviewer
- **Pipeline with gates:** planner → implementer → reviewer (each depends on previous)
- **Same-profile queue:** N tasks, same profile, no dependencies (serialized)
- **Human-in-the-loop:** Any task can `kanban_block()` to wait for input

---

## Part 2: Worker — Pitfalls and Patterns

### Workspace Handling

| Kind | What | How to Work |
|------|------|-------------|
| `scratch` | Fresh tmp dir | Read/write freely; GC'd on archive |
| `dir:<path>` | Shared persistent dir | Other runs will read what you write |
| `worktree` | Git worktree | Run `git worktree add` if `.git` missing; commit here |

### Tenant Isolation

If `$HERMES_TENANT` is set, prefix memory entries: `business-a: Acme is our biggest customer`

### Good Summary + Metadata Shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, 14 tests pass",
    metadata={"changed_files": ["rate_limiter.py"], "tests_run": 14, "tests_passed": 14},
)
```

**Task needing review:**
```python
kanban_comment(body="review-required handoff:\n" + json.dumps(metadata, indent=2))
kanban_block(reason="review-required: rate limiter shipped, needs eyes before merging")
```

**Research task:**
```python
kanban_complete(
    summary="3 libraries reviewed; vLLM wins on throughput",
    metadata={"recommendation": "vLLM", "benchmarks": {"vllm": 1.0, "sglang": 0.87}},
)
```

### Claiming Cards You Created

Only list IDs from successful `kanban_create` returns. Phantom IDs block completion.

```python
c1 = kanban_create(title="fix SQL injection", assignee="security-worker")
kanban_complete(summary="Done", created_cards=[c1["task_id"]])  # ✅
kanban_complete(summary="Done", created_cards=["t_hallucinated"])  # ❌ blocks
```

### Block Reasons That Get Answered Fast

Bad: `"stuck"` — no context.  
Good: one sentence naming the specific decision needed.

```python
kanban_comment(body="Full context: I have user IPs but NATs cause false positives.")
kanban_block(reason="Rate limit key choice: IP (NAT-unsafe) or user_id (requires auth)?")
```

### Heartbeats

Good: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`  
Bad: `"still working"`, empty notes, sub-second intervals

### Retry Scenarios

Check `kanban_show` for prior runs:
- `timed_out` → chunk the work
- `crashed` → reduce memory
- `spawn_failed` → profile config issue, ask human
- `reclaimed` → task was archived, check status
- `blocked` → check unblock comment in thread

### Do NOT

- Call `delegate_task` as substitute for `kanban_create` (different lifetimes)
- Call `clarify` (you're headless — use `kanban_block` instead)
- Modify files outside `$HERMES_KANBAN_WORKSPACE`
- Create follow-up tasks assigned to yourself
- Complete a task you didn't actually finish

---

## Part 3: Recovery — Stuck Workers

When a worker crashes/hallucinates/get blocked:

1. **Reclaim** (`hermes kanban reclaim <id>`) — abort and reset to `ready`
2. **Reassign** (`hermes kanban reassign <id> <profile> --reclaim`) — switch profile
3. **Change model** — edit profile config, then reclaim to retry

Hallucination warnings appear when:
- `created_cards` contains IDs not created by the worker's profile
- Free-form summary references `t_<hex>` IDs that don't resolve

---

## CLI Fallback

| Tool | CLI |
|------|-----|
| `kanban_show` | `hermes kanban show <id> --json` |
| `kanban_complete` | `hermes kanban complete <id> --summary "..."` |
| `kanban_block` | `hermes kanban block <id> "reason"` |
| `kanban_create` | `hermes kanban create "title" --assignee <profile>` |

Use tools from inside agents; CLI for humans at the terminal.

## Pitfalls

1. **Inventing profile names** — dispatcher silently drops unknown assignees
2. **Bundling independent lanes** — one user sentence ≠ one card
3. **Over-linking from wording** — "finally check X" may still be parallel
4. **Forgetting dependency links** — use `parents=` not prose references
5. **Argument order** — `kanban_link(parent_id, child_id)` — parent first
6. **Task state can change between dispatch and startup** — always `kanban_show` first
7. **Workspace may have stale artifacts** — read comment thread for context
