# WORKER_N: [Task Name]

**Project:** [project-name]  
**Worker ID:** WN  
**Created:** YYYY-MM-DD  
**Estimated Duration:** XX minutes

---

## Mission

[One clear sentence: What is this worker building/doing?]

---

## Context

[Background information the worker needs to understand the task]

**Why this matters:**
- Reason 1
- Reason 2

**How it fits:**
- Part of larger [system/feature]
- Connects to [other components]

---

## Deliverables

1. **`/path/to/file1.py`** - Description of file 1
2. **`/path/to/file2.md`** - Description of file 2
3. **`/path/to/file3.json`** - Description of file 3

---

## Success Criteria

- [ ] All deliverables exist at specified paths
- [ ] Code follows N5OS Lite principles (P1, P2, P15, P16)
- [ ] Tests pass (if applicable)
- [ ] Documentation complete
- [ ] No TODOs or stubs in production code
- [ ] Validation script runs successfully

---

## Implementation Guide

### Step 1: [First Major Step]

[Detailed instructions for step 1]

```python
# Example code if helpful
def example():
    pass
```

### Step 2: [Second Major Step]

[Detailed instructions for step 2]

### Step 3: Testing & Validation

Run validation:
```bash
python3 path/to/validation_script.py
```

Expected output:
```
✓ All checks passed
```

---

## Dependencies

**Requires (must complete first):**
- Worker X: [What it provides]
- File: `/path/from/previous/worker`

**Provides (for downstream workers):**
- Output files for Worker Y
- Schema for Worker Z

---

## Technical Specifications

**Language/Framework:** Python 3.x  
**Key Libraries:** [list]  
**Coding Standards:** Follow PEP 8  

**Architecture Notes:**
- Use [pattern/approach]
- Avoid [anti-pattern]
- Reference [existing similar code]

---

## Related Principles

- **P15: Complete Before Claiming** - Verify all success criteria before marking done
- **P2: Single Source of Truth** - Don't duplicate data/logic
- **P16: Accuracy Over Sophistication** - Correct > impressive
- **P19: Error Handling** - Handle failures gracefully

---

## Validation Checklist

Before marking complete:

- [ ] All files created at correct paths
- [ ] No placeholder/stub code (`TODO`, `FIXME`, `pass`, `NotImplementedError`)
- [ ] Imports resolve correctly
- [ ] Functions have docstrings
- [ ] Tests written and passing
- [ ] Follows principles listed above
- [ ] No obvious bugs or errors
- [ ] Ready for integration

---

## Notes & Constraints

[Any additional context, constraints, or important notes]

---

## Contact/Questions

If blocked or unclear:
1. Check [reference documentation]
2. Review [similar implementation]
3. Note blocker in worker conversation

---

*This is Worker N of M in the [Project Name] build*  
*Orchestrator: [conversation ID]*
