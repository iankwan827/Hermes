# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.

**Iron Law:** NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST

## Red-Green-Refactor Cycle
1. RED: Write failing test (one behavior per test, clear name)
2. Verify RED: Run test, confirm it fails for expected reason
3. GREEN: Write simplest code to pass (cheating OK)
4. Verify GREEN: Run test, confirm pass, run full suite
5. REFACTOR: Clean up while tests stay green

## Common Rationalizations
- "Too simple to test" → Simple code breaks
- "I'll test after" → Tests passing immediately prove nothing
- "TDD will slow me down" → TDD faster than debugging
- "Deleting X hours is wasteful" → Sunk cost fallacy

## Verification Checklist
- Every new function has a test
- Watched each test fail before implementing
- Wrote minimal code to pass
- All tests pass, output pristine
