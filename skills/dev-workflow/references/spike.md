# Spike

Throwaway experiments to validate an idea before build.

## When to use
- User wants to try something before committing to a real build
- "Is this even possible?", "compare A vs B", "quick prototype"
- Validating feasibility, not implementing

## When NOT to use
- Answer is knowable from docs — just research
- Work is production path — use `plan` + TDD instead
- Idea already validated — jump to implementation

## Core method

```
decompose → research → build → verdict
   ↑__________________________________________↓
                  iterate on findings
```

### 1. Decompose
Break the user's idea into 2-5 independent feasibility questions. Each question is one spike. Order by risk — the hardest question runs first.

| # | Spike | Validates (Given/When/Then) | Risk |
|---|-------|----------------------------|------|
| 001 | websocket-streaming | Given a WS connection, when LLM streams tokens, then client receives chunks < 100ms | High |

### 2. Research (per spike)
1. Brief it: 2-3 sentences on what, why, key risk
2. Surface competing approaches if there's real choice
3. Pick one. State why.

### 3. Build
One directory per spike. Standalone. Bias toward something interactive.

```
spikes/
├── 001-websocket-streaming/
│   ├── README.md
│   └── main.py
├── 002a-pdf-parse-pdfjs/
│   ├── README.md
│   └── parse.js
└── 002b-pdf-parse-camelot/
    ├── README.md
    └── parse.py
```

**Depth over speed.** Never declare "it works" after one happy-path run. Test edge cases.

### 4. Verdict
Each spike's README.md closes with:

```markdown
## Verdict: VALIDATED | PARTIAL | INVALIDATED

### What worked
- ...

### What didn't
- ...

### Surprises
- ...

### Recommendation for the real build
- ...
```

**VALIDATED** = core question answered yes, with evidence.
**PARTIAL** = works under constraints X, Y, Z — document them.
**INVALIDATED** = doesn't work. This is a successful spike.

## Comparison spikes

When two approaches answer the same question (002a / 002b), build them back to back, then do a head-to-head comparison:

```markdown
## Head-to-head: pdfjs vs camelot

| Dimension | pdfjs (002a) | camelot (002b) |
|-----------|--------------|----------------|
| Extraction quality | 9/10 | 7/10 |
| Setup complexity | npm install | pip + ghostscript |
| Perf on 100-page PDF | 3s | 18s |

**Winner:** pdfjs for our use case.
```

## Key rule
**Spike code is disposable.** Throw it away after the verdict. A spike that takes 2 days to "clean up for production" was a bad spike. Rewrite with TDD.
