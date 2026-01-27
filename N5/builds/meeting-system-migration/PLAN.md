---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
type: build_plan
status: ready
provenance: con_Tq9eOqW4T0rTnKvb
---

# Plan: Meeting System Migration + Agent Audit

**Objective:** Migrate MG-1 through MG-6 meeting agents to a single unified agent using the meeting-ingestion skill, add archive functionality, and audit all scheduled agents for consolidation opportunities.

**Trigger:** V requested full migration to skill-based meeting system and broader agent streamlining audit.

---

## Open Questions

All resolved:
- [x] Drop MG-4 (Warm Intros)? → Yes, delete
- [x] Fold archive into skill? → Yes, add `meeting-ingestion archive`
- [x] Broader agent audit? → Yes, but report-only (no changes)

---

## Checklist

### Stream 1: Audit (Parallel)
- ☐ D1.1: Full agent audit (report-only)
- ☐ D1.2: Meeting prompt audit (deletion manifest)

### Stream 2: Skill Enhancement
- ☐ D2.1: Add archive command to meeting-ingestion skill
- ☐ Test: `meeting_cli.py archive --dry-run`

### Stream 3: Agent Migration
- ☐ D3.1: Delete 7 old agents, create unified agent
- ☐ Verify: New agent in list, old agents gone

### Stream 4: Cleanup
- ☐ D4.1: Delete deprecated prompts, update references
- ☐ Verify: No broken references, skill status works

---

## Stream 1: Audit (Parallel)

### D1.1: Full Agent Audit
- **Scope**: All 35+ scheduled agents
- **Output**: Categorization, consolidation opportunities, deletion candidates
- **Artifact**: `artifacts/agent-audit-report.md`

### D1.2: Meeting Prompt Audit
- **Scope**: All meeting-related prompts
- **Output**: Deletion manifest (DELETE, KEEP, ARCHIVE categories)
- **Artifact**: `artifacts/prompt-deletion-manifest.md`

---

## Stream 2: Skill Enhancement

### D2.1: Add Archive Command
**Affected Files:**
- `Skills/meeting-ingestion/scripts/archive.py` - CREATE
- `Skills/meeting-ingestion/scripts/meeting_cli.py` - UPDATE
- `Skills/meeting-ingestion/SKILL.md` - UPDATE

**Logic (from Weekly Meeting Org agent):**
1. Scan for meetings with manifest.json status="complete"
2. Calculate target folder: `Personal/Meetings/Week-of-YYYY-MM-DD/`
3. Move meeting folder to target

---

## Stream 3: Agent Migration

### D3.1: Delete + Create Agents

**DELETE (7 agents):**
| ID Prefix | Title | Reason |
|-----------|-------|--------|
| 0c53b7ba | MG-1 Manifest | Replaced by skill |
| 0a08e6a8 | MG-2 Blocks | Replaced by skill |
| 5579f899 | MG-3 Blurb | Disabled, obsolete |
| ce6995b8 | MG-4 Warm Intro | V said drop |
| c7d010d5 | MG-5 Follow-up | Disabled, obsolete |
| f339ca26 | MG-6 State | Replaced by skill |
| 9b813d5c | Weekly Org v2 | Replaced by archive |

**CREATE (1 agent):**
- Title: `📋 Meeting Pipeline (Unified)`
- Schedule: 4x daily (6am, 11am, 3pm, 7pm ET)
- Uses: `meeting_cli.py pull && process && archive && status`

---

## Stream 4: Cleanup

### D4.1: Final Cleanup
**Affected Files (DELETE):**
- `Prompts/Meeting Manifest Generation.prompt.md`
- `Prompts/Meeting Block Generation.prompt.md`
- `Prompts/Meeting Warm Intro Generation.prompt.md`
- `Prompts/Meeting State Transition.prompt.md`
- `Prompts/Meeting Follow-Up Generation.prompt.md`
- `Prompts/Meeting Blurb Generation.prompt.md`
- `Prompts/Meeting_Block_Selector.prompt.md`
- Plus any from D1.2 audit

**Affected Files (UPDATE):**
- `Skills/meeting-ingestion/references/legacy_prompts.md`

---

## Success Criteria

1. ✅ Agent count reduced by 6 (7 deleted, 1 created)
2. ✅ `meeting_cli.py archive` works
3. ✅ Unified agent runs successfully
4. ✅ No broken references to deleted prompts
5. ✅ Agent audit report delivered

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Wrong agent deleted | Verify by title before delete |
| Archive logic incorrect | Test with --dry-run first |
| Missing prompt dependency | D1.2 audit identifies all deps |

---

## MECE Validation

| Scope Item | Drop | Status |
|------------|------|--------|
| Agent audit | D1.1 | ✓ |
| Prompt audit | D1.2 | ✓ |
| archive.py | D2.1 | ✓ |
| meeting_cli.py update | D2.1 | ✓ |
| SKILL.md update | D2.1 | ✓ |
| Delete old agents | D3.1 | ✓ |
| Create new agent | D3.1 | ✓ |
| Delete prompts | D4.1 | ✓ |
| Update legacy_prompts.md | D4.1 | ✓ |

No overlaps. All items assigned.
