---
created: 2026-01-05
last_edited: 2026-01-05
version: 1.0
type: build_plan
status: draft
provenance: con_g5Oyb9PO2QM1LTaC
---

# Plan: Edge Pipeline Fixes: Import, Meeting ID, and Commit Flow

**Objective:** Fix three blocking bugs in the edge backfill pipeline so it correctly tracks which meetings have been processed and allows the pipeline to run without PYTHONPATH hacks.

**Trigger:** Debugger analysis revealed 124 meetings show `already_processed: 0` despite 155 edges existing. Root causes: import error, meeting ID inconsistency, and batch-name-as-meeting-id commit pattern.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- All resolved during investigation -->
- [x] Where is meeting_id generated? → `edge_backfill.py:108` `meeting_to_id()`
- [x] Where is it passed during commit? → `edge_reviewer.py` passes `meeting_id` → `edge_writer.py` → `context_meeting_id` column
- [x] Why `already_processed: 0`? → IDs include `[m]`/`[p]` suffixes; existing edges have batch names not meeting IDs

---

## Checklist

### Phase 1: Fix Import Errors
- ☐ Add `sys.path.insert(0, "/home/workspace")` to `edge_backfill.py`
- ☐ Add `sys.path.insert(0, "/home/workspace")` to `b32_position_extractor.py`
- ☐ Move N5 imports below sys.path fix in both files
- ☐ Test: `python3 N5/scripts/edge_backfill.py scan --period Q4-2025` runs without ModuleNotFoundError

### Phase 2: Fix Meeting ID Format
- ☐ Update `meeting_to_id()` to strip `_[M]`, `_[P]`, `_[C]` suffixes before generating ID
- ☐ Test: `meeting_to_id(Path("2025-12-26_Careerspan-demo_[P]"))` returns `mtg_2025-12-26-careerspan-demo` (no `[p]`)

### Phase 3: Verify Commit Flow (No Code Change Expected)
- ☐ Trace: confirm `edge_reviewer.py approve` passes per-edge meeting_id to `edge_writer.add_edge()`
- ☐ Document: existing edges with batch names are historical; new commits will use correct meeting_id
- ☐ Test: create mock edge commit and verify `context_meeting_id` is actual meeting ID

---

## Phase 1: Fix Import Errors

### Affected Files
- `N5/scripts/edge_backfill.py` - UPDATE - add sys.path fix at top
- `N5/scripts/b32_position_extractor.py` - UPDATE - add sys.path fix at top

### Changes

**1.1 Add sys.path fix to edge_backfill.py:**

Current (line 2):
```python
#!/usr/bin/env python3
from N5.lib.paths import N5_ROOT, N5_DATA_DIR
```

Change to:
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/workspace")
from N5.lib.paths import N5_ROOT, N5_DATA_DIR
```

**1.2 Add sys.path fix to b32_position_extractor.py:**

Current (line 32):
```python
from N5.lib.paths import N5_DATA_DIR, N5_ROOT, MEETINGS_DIR
```

Change to (insert at line 32, before the N5 import):
```python
import sys
sys.path.insert(0, "/home/workspace")
from N5.lib.paths import N5_DATA_DIR, N5_ROOT, MEETINGS_DIR
```

Note: `sys` is already imported at line 30, so just add the `sys.path.insert` line.

### Unit Tests
- `cd /home/workspace && python3 N5/scripts/edge_backfill.py scan --period Q4-2025 2>&1 | head -5`: Should show JSON output, NOT ModuleNotFoundError
- `cd /home/workspace && python3 N5/scripts/b32_position_extractor.py stats 2>&1`: Should show stats, NOT ModuleNotFoundError

---

## Phase 2: Fix Meeting ID Format

### Affected Files
- `N5/scripts/edge_backfill.py` - UPDATE - modify `meeting_to_id()` function

### Changes

**2.1 Update meeting_to_id() to strip state suffixes:**

Current (lines 108-117):
```python
def meeting_to_id(meeting_path: Path) -> str:
    """Generate consistent meeting ID from path."""
    # e.g., "mtg_2025-12-15_david-x-careerspan"
    name = meeting_path.name.lower()
    # Clean up name
    name = name.replace(" ", "-").replace("_", "-")
    # Truncate if too long
    if len(name) > 60:
        name = name[:60]
    return f"mtg_{name}"
```

Change to:
```python
def meeting_to_id(meeting_path: Path) -> str:
    """Generate consistent meeting ID from path.
    
    Strips state markers ([M], [P], [C]) to ensure stable IDs across
    meeting lifecycle transitions.
    """
    import re
    name = meeting_path.name
    # Strip state suffixes: _[M], _[P], _[C] (case-insensitive)
    name = re.sub(r'_\[[MPC]\]$', '', name, flags=re.IGNORECASE)
    # Normalize: lowercase, replace spaces/underscores with hyphens
    name = name.lower().replace(" ", "-").replace("_", "-")
    # Truncate if too long
    if len(name) > 60:
        name = name[:60]
    return f"mtg_{name}"
```

### Unit Tests
- Test with [M] suffix: `meeting_to_id(Path("2025-12-26_Zo-demo-planning-brainstorm_[M]"))` → `mtg_2025-12-26-zo-demo-planning-brainstorm`
- Test with [P] suffix: `meeting_to_id(Path("2025-12-26_Careerspan-demo_[P]"))` → `mtg_2025-12-26-careerspan-demo`
- Test without suffix: `meeting_to_id(Path("2025-12-15_David-x-Careerspan"))` → `mtg_2025-12-15-david-x-careerspan`
- Full pipeline test: `python3 N5/scripts/edge_backfill.py scan --period Q4-2025 2>&1 | grep meeting_id | head -3` → No `[m]` or `[p]` in IDs

---

## Phase 3: Verify Commit Flow

### Affected Files
- None (verification only)

### Changes

**3.1 Trace commit flow (read-only verification):**

Verify the data flow is correct by inspection:
1. `edge_reviewer.py` line 306: `commit_from_jsonl(jsonl_content, meeting_id)` takes meeting_id
2. `edge_reviewer.py` line 362: passes `meeting=meeting_id` to `add_edge()`
3. `edge_writer.py` line 137-140: INSERT uses `meeting` param as `context_meeting_id`

The flow is correct. Problem is upstream: when batches are committed, the `meeting_id` passed is the batch name (e.g., `batch_2026-01-04_recent`), not the per-edge meeting ID.

**3.2 Root cause of batch-name-as-meeting-id:**

Looking at `edge_reviewer.py` line 128:
```python
meeting_id = metadata.get("meeting_id", "unknown")
```

The batch file's metadata block has the batch name, not per-edge meeting IDs. Each edge line in the JSONL should have its own `meeting_id` field.

**3.3 Decision: Leave historical data, fix going forward:**

- Existing 155 edges with batch names: leave as-is (they have provenance via batch name)
- New edge extraction: ensure each edge line includes `meeting_id` field from source meeting
- Modify `edge_reviewer.py` to prefer per-edge `meeting_id` over batch metadata

**3.4 Small fix to edge_reviewer.py commit logic:**

In `commit_from_jsonl()`, change to use per-edge meeting_id if present:

Current pattern (line 358-362):
```python
add_result = add_edge(
    source=source_ref,
    relation=edge["relation"],
    target=target_ref,
    meeting=meeting_id,  # Uses batch-level meeting_id
    evidence=edge.get("evidence", "")
)
```

Change to:
```python
# Prefer per-edge meeting_id, fall back to batch-level
edge_meeting_id = edge.get("meeting_id", meeting_id)
add_result = add_edge(
    source=source_ref,
    relation=edge["relation"],
    target=target_ref,
    meeting=edge_meeting_id,
    evidence=edge.get("evidence", "")
)
```

### Affected Files (Updated)
- `N5/scripts/edge_reviewer.py` - UPDATE - prefer per-edge meeting_id in commit flow

### Unit Tests
- Create test JSONL with per-edge `meeting_id`, commit, verify `context_meeting_id` in DB matches
- `sqlite3 N5/data/edges.db "SELECT context_meeting_id FROM edges ORDER BY id DESC LIMIT 1"` → Should be actual meeting ID

---

## Success Criteria

1. `python3 N5/scripts/edge_backfill.py scan --period Q4-2025` runs without PYTHONPATH workaround
2. `python3 N5/scripts/b32_position_extractor.py stats` runs without PYTHONPATH workaround
3. All meeting IDs in scan output have NO `[m]`/`[p]`/`[c]` suffixes
4. New edge commits store actual meeting ID in `context_meeting_id`, not batch name
5. `already_processed` count increases when meetings are re-scanned after edge commit

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Historical edges have batch names, not meeting IDs | Acceptable: they retain provenance via batch name; only affects `already_processed` count for ~15 unique batches |
| Regex may not catch all state suffix patterns | Pattern `_\[[MPC]\]$` covers known cases; add to test suite |
| Per-edge meeting_id missing from existing batches | Fallback to batch-level meeting_id preserves current behavior |

---

## Alternatives Considered (Nemawashi)

### Alternative 1: Migrate historical edges to correct meeting_id
- **Pro:** Clean data, `already_processed` accurate for all historical
- **Con:** Risky migration, may break provenance, 8+ hours work
- **Decision:** REJECTED — cost outweighs benefit; forward-fix is sufficient

### Alternative 2: Use PYTHONPATH in all invocations instead of fixing scripts
- **Pro:** Zero code change
- **Con:** Fragile, every caller must remember, agents/prompts may forget
- **Decision:** REJECTED — fix at source is more robust

### Alternative 3: Create wrapper scripts that set PYTHONPATH
- **Pro:** Doesn't modify existing scripts
- **Con:** Adds indirection, two files to maintain
- **Decision:** REJECTED — direct fix is simpler

**Selected approach:** Fix scripts directly (sys.path), fix meeting_to_id(), fix commit flow to prefer per-edge meeting_id.

---

## Trap Doors

None identified. All changes are:
- Additive (sys.path insert)
- Behavior-preserving with enhancement (meeting_to_id strips suffix)
- Backward-compatible (per-edge meeting_id is opt-in, falls back to current behavior)

---

## Level Upper Review

*Skipping for this build — straightforward bug fixes with clear root causes. No architectural decisions or divergent thinking needed.*

---

## Handoff

**When approved:** Route to Builder with:
- Plan file: `file 'N5/builds/edge-pipeline-fixes/PLAN.md'`
- Start at: Phase 1
- Context: All investigation complete, code locations identified, changes specified


