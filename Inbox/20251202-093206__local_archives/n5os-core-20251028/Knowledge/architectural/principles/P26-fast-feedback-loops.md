# P26: Fast Feedback Loops

**Category:** Development Practice  
**Priority:** High  
**Related:** P24 (Simulation), P7 (Dry-Run)

---

## Principle

**Minimize time between action and feedback. Fast loops enable rapid iteration and learning.**

The faster you can test an idea, the faster you can learn if it works. Optimize for iteration speed, not perfection.

---

## Pattern

### Ideal Feedback Loop

```
Idea → Test → Result → Learn
└────────── <5 seconds ──────┘
```

**Goal:** Keep the loop under 5 seconds when possible.

---

## Examples

### Development

**Slow loop (expensive):**
```bash
# Edit code → Save → Deploy → Wait → Test → Debug
# Time: 2-5 minutes per iteration
```

**Fast loop (cheap):**
```bash
# Edit code → Save → Run locally → See result
# Time: 2-5 seconds per iteration
```

**Impact:** 60x faster feedback = 60x more iterations = 60x faster learning

### Testing

**Slow:**
```python
# Test entire system
python -m pytest tests/  # 45 seconds
```

**Fast:**
```python
# Test one function
python -m pytest tests/test_specific.py::test_function  # 0.5 seconds
```

### Debugging

**Slow:**
```python
# Add print → Run → Wait → Check output
print(f"Debug: {variable}")
```

**Fast:**
```python
# Use REPL or debugger
>>> variable
{'key': 'value'}
```

---

## Implementation Strategies

### 1. Dry-Run Everything
```python
# Instant feedback without side effects
./script.py --dry-run  # Shows what would happen
```

### 2. Local Before Remote
```bash
# Test locally first
sqlite3 local.db "SELECT COUNT(*) FROM users"  # Instant

# Then remote
psql -h prod "SELECT COUNT(*) FROM users"  # 2 seconds
```

### 3. Small Batches
```python
# Bad: Process everything
process_all_records()  # 10 minutes to see if it works

# Good: Process one first
process_record(records[0])  # 1 second to see if it works
```

### 4. Fast Tests
```python
# Unit tests: milliseconds
def test_parse():
    assert parse("input") == "output"

# Integration tests: seconds
# E2E tests: minutes (run less frequently)
```

---

## Benefits

1. **Learn faster:** More iterations = more learning
2. **Catch errors early:** Fail fast, fix fast
3. **Build confidence:** Immediate validation
4. **Maintain flow:** No context switching while waiting

---

## Common Mistakes

❌ Optimizing for production before local works
❌ Running full test suite for every change
❌ Deploying to test environment for simple checks
❌ Building complex setup before proving concept

**Fix:** Start simple, add complexity only when needed.

---

## Application

**Before building:**
- Can I test this idea in < 5 seconds?
- Do I need the full system to validate this?
- Can I use a REPL, dry-run, or sample data?

**During development:**
- Test the smallest unit first
- Use dry-runs liberally
- Keep sample data handy
- Defer integration until units work

**While debugging:**
- Isolate the failing component
- Test it in isolation
- Fix, verify, then reintegrate

---

## Related Principles

- **P24 (Simulation):** Dry-runs enable instant feedback
- **P7 (Dry-Run):** Preview changes without consequences
- **P25 (Code Is Free):** Fast loops cost nothing, slow loops cost time

---

**Pattern:** Action → Feedback → Learn → Repeat

**Goal:** Keep the loop under 5 seconds
