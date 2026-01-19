---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_RkSXGwBtKEEudYEP
---

# MECE Worker Framework

**Purpose:** Ensure build orchestrator divides work in a **Mutually Exclusive, Collectively Exhaustive** way while **minimizing worker count**.

**When to Apply:** Every build using the orchestrator-worker pattern (multi-worker builds in `N5/builds/`).

---

## Core Principles

### 1. Mutually Exclusive (No Overlaps)
- **Rule:** No two workers touch the same scope (files, functions, responsibilities)
- **Why:** Overlapping scope causes merge conflicts, duplicate work, and coordination overhead
- **Check:** For each scope item, exactly ONE worker owns it

### 2. Collectively Exhaustive (No Gaps)
- **Rule:** ALL scope items from the plan are covered by exactly one worker
- **Why:** Gaps mean incomplete implementation; discovered late = expensive rework
- **Check:** Every plan deliverable maps to a worker

### 3. Minimum Worker Count
- **Rule:** Combine work where cognitive load permits; don't over-split
- **Why:** More workers = more coordination, more context-switching for V, more threads to manage
- **Heuristic:** If two tasks share >50% of files, consider combining into one worker
- **Anti-pattern:** One worker per file (too granular)

---

## Token Budget Rules

### Context Window Reality

| Advertised Context | System Overhead (~30%) | Usable Context (~70%) |
|--------------------|------------------------|----------------------|
| 200k tokens        | ~60k                   | ~140k                |
| 128k tokens        | ~38k                   | ~90k                 |

### Budget Limits Per Worker

| Metric | Hard Limit | Soft Target | Reasoning |
|--------|-----------|-------------|-----------|
| Brief + Expected File Reads | ≤40% of total context | ≤30% of total context | Leave room for tool outputs, errors, iterations |

### When to Split a Worker

**Split trigger:** If estimated token load > 40% of context window:
1. Identify natural split points (e.g., separate files, distinct responsibilities)
2. Create two workers with explicit boundaries
3. Establish dependency if sequential

### Token Estimation Method

```
Total tokens ≈ (brief_chars / 4) + Σ(file_chars / 4)
```

For files expected to be read/modified:
- Small file (<100 lines): ~500 tokens
- Medium file (100-500 lines): ~2,000 tokens  
- Large file (500+ lines): ~5,000+ tokens

---

## Wave Optimization

### Wave Assignment Rules

| Worker Dependencies | Wave Assignment |
|---------------------|-----------------|
| No dependencies | Wave 1 (can run in parallel) |
| Depends on Wave 1 outputs | Wave 2 |
| Depends on Wave 2 outputs | Wave 3 |

### Minimize Critical Path

**Critical path** = longest chain of dependent workers

**Optimization strategies:**
1. Look for implicit dependencies that can be made explicit in Wave 1
2. Split large dependent workers into independent parts + dependent parts
3. Consider whether dependency is real or just sequencing preference

### Example Wave Structure

```
Good:                           Bad:
Wave 1: W1.1, W1.2, W1.3       Wave 1: W1.1
  ↓        ↓       ↓           Wave 2: W2.1
Wave 2: W2.1 (depends on all)   Wave 3: W3.1
                                Wave 4: W4.1
(3 parallel + 1 sequential)    (4 sequential = slow)
```

---

## Scope Declaration Format

Every worker brief MUST include:

### Frontmatter (YAML)

```yaml
scope:
  files:
    - path/to/file1.py       # Files this worker OWNS
    - path/to/file2.py
  responsibilities:
    - "Database schema changes"  # Non-file scope items
    - "Migration script"
  must_not_touch:
    - path/to/shared.py      # Explicit exclusions
token_estimate:
  brief_tokens: 1500
  file_tokens: 4000
  total_pct: 2.75            # Percentage of context window
```

### Body Structure

```markdown
## MECE Declaration

**SCOPE:** [Summary of owned scope]

**MUST DO:**
1. [Specific action with exact details]
2. [Another specific action]
...

**MUST NOT DO:**
- [Forbidden action + why]
- [Another boundary]
...

**EXPECTED OUTPUT:**
- [Exact deliverable with success criteria]
- [Verification method]
```

---

## Gap Check Protocol

### Before Launching Workers

1. **List all scope items** from the plan (files, responsibilities, deliverables)
2. **Map each item** to a worker
3. **Validate:**
   - Items with 0 workers → **GAP** (must assign or justify exclusion)
   - Items with 2+ workers → **OVERLAP** (must clarify ownership)
   - Items with 1 worker → **VALID**

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `api/routes.py` | W1.1 | ✓ |
| `api/models.py` | W1.2 | ✓ |
| `api/utils.py` | W1.1, W1.2 | ⚠️ OVERLAP |
| `api/tests/` | (none) | ⚠️ GAP |

---

## Validation

### Run Before Launching Workers

```bash
python3 N5/scripts/mece_validator.py <build_slug>
```

### Validator Outputs

- **PASS**: All scope items have exactly one owner
- **WARN**: Advisory issues (token estimates high, etc.)
- **FAIL**: Overlaps or gaps detected

### Fix Before Proceeding

If validation fails:
1. Reassign overlapping scope to single owner
2. Assign orphaned scope to appropriate worker (or create new worker)
3. Re-run validator
4. Document resolution in plan

---

## Integration with Orchestrator Protocol

This framework extends `N5/prefs/operations/orchestrator-protocol.md`:

**Add to Orchestrator Setup Phase:**
> Before creating worker briefs, complete MECE validation:
> 1. Define scope items from plan
> 2. Assign each to exactly one worker
> 3. Run `python3 N5/scripts/mece_validator.py <slug>`
> 4. Fix any overlaps/gaps before proceeding

**Add to Worker Brief Template:**
> Include MECE Declaration section (scope, must do, must not do, expected output)

---

## Examples

### Good MECE Division

**Build:** API refactor (3 domains)

| Worker | Scope | Token Est. |
|--------|-------|-----------|
| W1.1 | `auth/` directory (all files) | 25% |
| W1.2 | `users/` directory (all files) | 30% |
| W1.3 | `billing/` directory (all files) | 28% |

✓ Clear boundaries (directory-based)
✓ No overlaps
✓ Complete coverage
✓ Can run in parallel (Wave 1)

### Bad Division (Overlaps)

| Worker | Scope | Problem |
|--------|-------|---------|
| W1.1 | "Refactor auth" | Vague scope |
| W1.2 | "Update user endpoints" | May touch auth |
| W1.3 | "Fix security issues" | Definitely touches auth |

⚠️ "auth", "user endpoints", and "security" likely overlap

### Bad Division (Gaps)

| Worker | Scope | Problem |
|--------|-------|---------|
| W1.1 | `api/v1/` | Covered |
| W1.2 | `api/v2/` | Covered |
| (none) | `api/shared/` | **GAP** - who owns shared utilities? |

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| One worker per file | Too granular; coordination overhead | Group by domain/responsibility |
| Vague scope ("refactor X") | Leads to overlap interpretations | Explicit file list + must_not_touch |
| Unstated shared files | Both workers modify, merge conflicts | Explicitly assign to one; other reads only |
| No token estimates | Workers run out of context mid-task | Estimate before assigning |
| Dependencies unclear | Wave assignment impossible | Explicit `depends_on` in frontmatter |

---

## Quick Reference

**Architect checklist before worker handoff:**
- [ ] All scope items from plan listed
- [ ] Each item assigned to exactly ONE worker
- [ ] `must_not_touch` explicit for shared resources
- [ ] Token estimates within 40% budget
- [ ] Waves assigned based on dependencies
- [ ] `python3 N5/scripts/mece_validator.py <slug>` passes
