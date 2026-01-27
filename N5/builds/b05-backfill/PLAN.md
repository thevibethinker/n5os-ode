---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
type: build_plan
status: approved
provenance: con_BTFIhYsxr3P3CzaR
---

# Plan: B05 Consolidation & Semantic Backfill

**Objective:** Consolidate B05 prompts, re-process last week's meeting transcripts with new decomposition spec, semantically extract V's action items with urgency signals and deduplication, present single batch checklist for approval, bulk import approved items.

**Trigger:** V wiped task database because previous backfill (D1.2) generated fake "Prepare for X" garbage. Real tasks come from meeting action items with explicit commitments.

**Key Design Principle:** LLM semantic reasoning over regex/Python for all extraction. One interactive approval pass, not incremental review.

---

## Open Questions

- [x] How far back? → Last week (34 B05 blocks modified in last 7 days)
- [x] Skip any meetings? → No exclusions specified
- [x] Domain focus? → All domains

---

## Checklist

### Phase 1: B05 Prompt Consolidation
- ☐ Archive old Generate_B05.prompt.md  
- ☐ Move new prompt to Prompts/Blocks/Generate_B05.prompt.md
- ☐ Verify naming/structure fits block system

### Phase 2: Semantic Extraction & Processing
- ☐ Identify last week's meeting transcripts
- ☐ Re-run B05 generation through new prompt (LLM calls)
- ☐ Extract V's action items with urgency signals
- ☐ Deduplicate semantically across meetings
- ☐ Stage all items for review

### Phase 3: Interactive Review & Import
- ☐ Present batch checklist to V
- ☐ V ticks approved items
- ☐ Bulk import ticked items
- ☐ Discard unticked items

---

## Phase 1: B05 Prompt Consolidation

### Affected Files
- `Prompts/Blocks/Generate_B05.prompt.md` - UPDATE (replace with new spec)
- `Prompts/Generate_B05_Action_Items.prompt.md` - DELETE (after merge)

### Changes

**1.1 Replace old B05 prompt:**
The new prompt at `Prompts/Generate_B05_Action_Items.prompt.md` has the decomposition metadata we need (priority, first_step, estimate, domain, project, milestones). Replace the old table-based prompt entirely.

**1.2 Verify block system compliance:**
- Filename: `Generate_B05.prompt.md` ✓
- Location: `Prompts/Blocks/` ✓
- YAML frontmatter with block_id: B05

### Unit Tests
- `ls Prompts/Blocks/Generate_B05.prompt.md` exists
- `grep "decomposition" Prompts/Blocks/Generate_B05.prompt.md` returns results
- Old file `Prompts/Generate_B05_Action_Items.prompt.md` deleted

---

## Phase 2: Semantic Extraction & Processing

### Affected Files
- `Personal/Meetings/Week-of-2026-01-19/*/B05_ACTION_ITEMS.md` - REGENERATE
- `Personal/Meetings/Week-of-2026-01-12/*/B05_ACTION_ITEMS.md` - REGENERATE (if in 7-day window)
- `/home/.z/workspaces/con_BTFIhYsxr3P3CzaR/extracted_items.json` - CREATE (temp)

### Changes

**2.1 Identify transcripts to reprocess:**
Find all meetings from last 7 days with transcripts:
```bash
find /home/workspace/Personal/Meetings/Week-of-2026-01-* -name "B01_TRANSCRIPT.md" -mtime -7
```

**2.2 Re-run B05 generation (LLM semantic):**
For each transcript:
1. Read transcript content
2. Call `/zo/ask` with new B05 prompt
3. Write regenerated B05_ACTION_ITEMS.md

**2.3 Extract V's items with urgency signals (LLM semantic):**
For each regenerated B05:
1. Read block content
2. Call `/zo/ask` with extraction prompt that:
   - Filters to V's items only (Owner: Vrijen/V)
   - Detects urgency signals:
     - Multiple mentions across meetings
     - "Someone reminded V" patterns
     - Explicit deadlines
     - External commitments
3. Output structured JSON per item

**2.4 Deduplicate semantically (LLM):**
1. Collect all extracted items
2. Call `/zo/ask` with deduplication prompt:
   - Group semantically similar items
   - Merge across meetings (preserve sources)
   - Keep highest urgency signal

**2.5 Stage all items:**
Use `python3 Skills/task-system/scripts/stage.py add` for each deduplicated item

### Unit Tests
- At least 1 regenerated B05 has new format (milestones, priority fields)
- `stage.py list` shows staged items
- No regex in extraction code

---

## Phase 3: Interactive Review & Import

### Affected Files
- `/home/.z/workspaces/con_BTFIhYsxr3P3CzaR/review_checklist.md` - CREATE

### Changes

**3.1 Present batch checklist:**
Generate markdown checklist with all staged items:
```markdown
## Task Backfill Review

Check items to approve, leave unchecked to discard.

- [ ] **Task title** | Priority: X | Est: Ymin | Source: meeting-name
  - First step: ...
  - Context: ...
```

**3.2 Process V's selections:**
- Parse checked items
- `stage.py promote` for each checked item
- `stage.py dismiss` for each unchecked item

### Unit Tests
- All promoted tasks appear in `task.py list`
- No staged items remain after review

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Drop | Status |
|------------|------|--------|
| B05 prompt consolidation | D1.1 | ✓ |
| Transcript identification | D1.2 | ✓ |
| B05 regeneration (LLM) | D1.2 | ✓ |
| V's item extraction (LLM) | D1.2 | ✓ |
| Urgency signal detection (LLM) | D1.2 | ✓ |
| Deduplication (LLM) | D1.2 | ✓ |
| Staging items | D1.2 | ✓ |
| Checklist presentation | D2.1 (manual) | ✓ |
| V's approval collection | D2.1 (manual) | ✓ |
| Bulk import | D2.1 (manual) | ✓ |

### Token Budget Summary

| Drop | Brief (tokens) | Files (tokens) | Total % | Status |
|------|----------------|----------------|---------|--------|
| D1.1 | ~1,500 | ~3,000 | 2% | ✓ |
| D1.2 | ~3,000 | ~15,000 | 9% | ✓ |
| D2.1 | ~1,000 | ~2,000 | 1.5% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE Drop (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All Drops within 40% token budget
- [x] Stream dependencies valid (D2.1 depends on D1.1, D1.2)

---

## Drop Briefs

| Stream | Drop | Title | Mode |
|--------|------|-------|------|
| 1 | D1.1 | B05 Prompt Consolidation | auto |
| 1 | D1.2 | Semantic Extraction Pipeline | auto |
| 2 | D2.1 | Interactive Review & Import | manual (this thread) |

---

## Success Criteria

1. Single B05 prompt at `Prompts/Blocks/Generate_B05.prompt.md` with decomposition spec
2. All extraction uses LLM semantic reasoning (no regex for item parsing)
3. V reviews single batch checklist, ticks approvals
4. Only approved items in task system
5. Zero staged items remaining after review

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Too many items overwhelms V | Group by domain/project in checklist |
| LLM hallucination creates fake tasks | Only extract explicit commitments from B05 blocks |
| Deduplication over-merges distinct items | Preserve source meeting references, let V untick if wrong |

---

## Trap Doors

⚠️ **Irreversible**: Once V approves and imports, tasks are in production database. 
Mitigation: Batch review means V sees everything before commit.

---

## Alternatives Considered

1. **Staged daily review** — Rejected: V explicitly wants single batch approval
2. **Regex extraction** — Rejected: V mandated semantic LLM reasoning
3. **Incremental import** — Rejected: Bulk import after full approval

