# Systematic Debugging

**Iron Law:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

## Four Phases

### 1. Root Cause Investigation
- Read the full error message — every line, every stack frame
- Reproduce the issue reliably (if you can't reproduce, you can't fix)
- Check what changed recently (git log, git diff, deployment history)
- Trace the data flow — where does bad data enter, where does it exit?
- Add strategic logging/print statements to observe the flow

### 2. Pattern Analysis
- Find working examples (same library, same pattern, same framework)
- Compare working vs broken code — what's different?
- Search error messages verbatim (Stack Overflow, GitHub issues, docs)
- Identify the minimal difference that causes the failure

### 3. Hypothesis and Testing
- Form a **single** hypothesis ("I think X causes Y because Z")
- Design a minimal test to confirm or reject the hypothesis
- Change one variable at a time
- If hypothesis is wrong, document what you learned, form new hypothesis
- Never skip to "just try fixing it"

### 4. Implementation
- Write a failing test that reproduces the bug first
- Apply the single fix your hypothesis identified
- Verify the test passes
- Run the full test suite to check for regressions
- **Rule of Three:** 3+ failed fix attempts = stop and question the architecture

## Language-Specific Debugging

### Python
```python
# Inline debugging (Python 3.7+)
breakpoint()  # Drops into pdb at this line

# Command-line debugger
import pdb; pdb.set_trace()  # Legacy style

# Remote debugging
# pip install debugpy
import debugpy; debugpy.listen(5678); debugpy.wait_for_client()
# Then attach VS Code or PyCharm debugger

# Remote debugging over SSH
# pip install remote-pdb
# On remote: remote-pdb -p 4444
# Locally: nc localhost 4444
```

### Node.js
```bash
# Inspector breakpoint (pauses on first line)
node --inspect-brk app.js

# Attach to running process
node inspect -p <pid>

# Chrome DevTools Protocol (CDP)
# Open chrome://inspect in Chrome to attach debugger

# Conditional breakpoints in code
debugger;  // Pauses when --inspect is active
```

### General Tools
- **Interactive REPL/Shell:** Inject code to test assumptions live
- **Logging:** Add structured logs with context (variable values, timestamps)
- **Bisection:** Binary search through commits to find when bug was introduced (`git bisect`)

## The Debugging Mindset

| Instead of... | Do this... |
|---------------|------------|
| "Let me just try changing X" | "What evidence do I have that X is the cause?" |
| "It worked before, must be a library bug" | "What changed? Let me check git log" |
| "I'll add more error handling" | "What's the actual error? Read the full message" |
| "Let me restart and see if it goes away" | "Let me reproduce it reliably first" |
| "This is probably a race condition" | "Let me trace the actual execution order" |

## Red Flags — STOP and Return to Phase 1

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "One more attempt" (after 2+ failures)
- "It's probably a library issue"
- "Let me just add a try/except"
- "I'll fix the root cause later"

**If any of these thoughts arise: STOP. Return to Phase 1 (Root Cause Investigation).**

## Escalation: When to Question Architecture

After 3+ failed fix attempts, the problem may not be a bug — it may be a design flaw:

1. **Is the module doing too much?** (Single Responsibility violation)
2. **Are responsibilities tangled?** (Need dependency injection, event system)
3. **Is the data model wrong?** (Schema doesn't match reality)
4. **Is the abstraction leaking?** (Forcing wrong patterns)
5. **Should this be two systems?** (Coupling that should be separation)

Architecture problems masquerade as bugs. If fixing the bug requires changing 5+ files, you likely have an architecture issue.
