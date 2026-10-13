# Pre-Commit Code Verification

**Core principle:** No agent should verify its own work.

## Steps

### 1. Get the diff
```bash
git diff --cached          # staged changes
git diff HEAD~1..HEAD      # last commit
git diff main...HEAD       # branch diff
```
If no staged changes, run `git add -p` for selective staging.

### 2. Static security scan
Run on the diff output:
- **Secrets**: API keys, tokens, passwords, connection strings (regex scan)
- **Injection**: unsanitized user input reaching `exec()`, `eval()`, `subprocess`, `os.system`, template engines
- **Deserialization**: `pickle.loads`, `yaml.load` (unsafe), `marshal.loads`, `JSON.parse` on untrusted input
- **SQL injection**: string concatenation in queries, f-strings in SQL, missing parameterization
- **Path traversal**: unsanitized `open()`, `os.path.join` with user input
- **Hardcoded credentials**: default passwords, test-only secrets left in production code

### 3. Baseline tests and linting
```bash
# Run existing tests first to establish baseline
pytest --tb=short          # Python
npm test                   # Node.js
go test ./...              # Go
cargo test                 # Rust

# Lint
ruff check .               # Python
eslint .                   # JavaScript/TypeScript
golangci-lint run          # Go
```
**Rule**: If tests fail before your changes, that's pre-existing — document it but don't block.

### 4. Self-review checklist
Before delegating to the independent reviewer:
- [ ] No debug prints, commented-out code, or TODO/FIXME without ticket references
- [ ] No hardcoded values that should be configurable
- [ ] Error handling is present and non-empty
- [ ] No function exceeds 50 lines (suggest extraction)
- [ ] No duplicate logic (DRY)
- [ ] Variable/function names are descriptive
- [ ] No unused imports or variables
- [ ] Changes match the task scope (no scope creep)

### 5. Independent reviewer subagent
Use `delegate_task` to create a reviewer subagent. The reviewer receives:
- The full diff
- Task context (what was requested)
- The codebase structure

**Reviewer prompt template:**
```
You are an independent code reviewer. Review this diff critically.

Diff:
<diff here>

Context: <task description>

Check for:
1. Bugs and logic errors
2. Security vulnerabilities
3. Performance issues
4. Test coverage gaps
5. Code style and consistency
6. Edge cases not handled

Output: List of issues with severity (critical/high/medium/low) and suggested fixes.
```

### 6. Evaluate results
- **0 critical/high issues**: Proceed to commit
- **1+ critical issues**: Fix before committing
- **3+ medium issues**: Fix before committing
- **All low**: Document and proceed (or fix if time permits)

### 7. Auto-fix loop (max 2 cycles)
```
Reviewer finds issues → Agent fixes → Re-run reviewer → 
  Still issues? → Fix again → Re-run reviewer → 
    Still issues? → STOP, escalate to human with summary
```
**Never** auto-fix more than 2 cycles. If issues persist, the problem likely needs human judgment.

### 8. Commit with [verified] prefix
```bash
git commit -m "[verified] <description>

- Security scan: passed
- Tests: X passed, Y skipped
- Review: 0 critical, 0 high, Z medium
- Auto-fix cycles: N

Reviewed-by: independent-agent"
```

---

## Parallel 3-Agent Cleanup

When refactoring or optimizing existing code, delegate three parallel reviewers:

### Reviewer 1: Code Reuse
- Duplicate code detection
- Existing utility functions or libraries that could replace custom code
- DRY violations across the codebase
- Opportunities to extract common patterns

### Reviewer 2: Code Quality
- Naming conventions and readability
- Function complexity (cyclomatic complexity, nesting depth)
- Type safety and error handling
- Documentation gaps
- Dead code and unreachable branches

### Reviewer 3: Efficiency
- Unnecessary allocations or data copies
- N+1 queries or O(n²) loops where O(n) is possible
- Missing caching opportunities
- Resource leaks (unclosed files/connections)
- Algorithmic improvements

**Merge strategy**: After all three reviewers complete, consolidate findings, deduplicate, and prioritize by severity. Present unified list to the implementing agent for batch fixes.
