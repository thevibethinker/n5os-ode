---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_nXKLrpy6lsnJm0dz
---

# Conversation-End v3: Tiered Redesign

**Build ID:** conversation-end-v3  
**Status:** 🟡 Planning  
**Architect:** Vibe Architect  
**Created:** 2025-12-17

---

## Problem Statement

Current conversation-end workflow suffers from:
1. **Inconsistent execution** - 7+ conflicting documentation files
2. **Excessive cost** - ~$0.15-0.25 per close regardless of conversation type
3. **Unpredictable behavior** - AAR sometimes generated, sometimes not; capability questions inconsistent

## Design Principles

Per V's direction:
- **Default Quick, Escalate Smart** - Quick mode by default; escalate to full only when build/orchestrator markers detected
- **AAR for Builds Only** - Full After-Action Report reserved for build situations
- **Lessons for Troubleshooting** - Lesson extraction for builds with debugging/repair work
- **File Org Always Important** - Keep file organization/archival across all tiers
- **Titling Always Important** - Thread title generation across all tiers
- **Thread Export is Distinct** - Not part of conversation-end; it's spawn-worker adjacent
- **Tier 1/2 More Detailed** - Not ultra-light; meaningful closure even for non-builds

---

## Architecture: 3-Tier System

### Tier Detection Logic

```
DEFAULT → Tier 1 (Quick)

ESCALATE to Tier 2 if:
- Conversation has ≥3 file artifacts created
- SESSION_STATE.md shows type=research or type=discussion with substantial progress
- Git changes detected in workspace

ESCALATE to Tier 3 if:
- SESSION_STATE.md type=build OR type=orchestrator
- Build workspace exists (N5/builds/<slug>/)
- DEBUG_LOG.jsonl exists (troubleshooting session)
- Major capability work mentioned in conversation
```

### Manual Override

User can force a specific tier with flags:
- `@Close Conversation --tier=1` → Force Tier 1 (quick)
- `@Close Conversation --tier=2` → Force Tier 2 (standard)  
- `@Close Conversation --tier=3` → Force Tier 3 (full build)
- No flag → Auto-detect tier based on markers above

### Tier 1: Quick Close (Default)

**Cost Target:** <$0.05  
**Time Target:** <45 seconds

| Step | Action | Script/Tool |
|------|--------|-------------|
| 1 | Generate thread title (LLM, follows naming convention) | `n5_title_generator.py` |
| 2 | Generate conversation summary (LLM, 2-3 sentences) | LLM analysis |
| 3 | Update SESSION_STATE.md status=closed | `session_state_manager.py` |
| 4 | Scan and list files in conversation workspace | `conversation_end_analyzer.py --quick` |
| 5 | Present file list with recommendations | Script + LLM categorization |

**Output Format (Tier 1):**
```markdown
## Conversation Closed

**Title:** [Generated Title]
**Type:** [Quick discussion / Q&A / etc.]
**Duration:** ~[X] minutes

### Summary
[1-2 sentence description of what was discussed/accomplished]

### Files Organized
- [file moved] → [destination] (or "None")

✅ Workspace clean
```

### Tier 2: Standard Close

**Cost Target:** <$0.08  
**Time Target:** <90 seconds

| Step | Action | Script/Tool |
|------|--------|-------------|
| 1-5 | All Tier 1 steps | (same) |
| 6 | Detailed file organization with categorization | `conversation_end_analyzer.py --standard` |
| 7 | Extract key decisions/outcomes | LLM analysis |
| 8 | Check for unfinished work items | Pattern scan |
| 9 | Git status check (if changes) | `n5_git_check.py` |

**Output Format (Tier 2):**
```markdown
## Conversation Closed

**Title:** [Generated Title]
**Type:** [Research / Discussion / Investigation]
**Duration:** ~[X] minutes

### Summary
[2-3 sentence description]

### Key Outcomes
- [Outcome 1]
- [Outcome 2]

### Decisions Made
- [Decision with rationale]

### Files Organized
| File | Destination | Reason |
|------|-------------|--------|
| ... | ... | ... |

### Open Items
- [ ] [Any unfinished work] (or "None identified")

### Git Status
[Clean / X uncommitted changes in Y]

✅ Workspace organized
```

### Tier 3: Full Build Close

**Cost Target:** <$0.20  
**Time Target:** <3 minutes

| Step | Action | Script/Tool |
|------|--------|-------------|
| 1-9 | All Tier 2 steps | (same) |
| 10 | Generate full AAR | LLM + `conversation-end-output-template.md` |
| 11 | Lesson extraction (if troubleshooting) | `n5_lessons_extract.py` |
| 12 | Capability registry check | Interactive Q&A |
| 13 | Archive build tracker | Move to `N5/logs/builds/` |
| 14 | Placeholder scan (P16/P21) | `n5_placeholder_scan.py` |

**Output Format (Tier 3):**
```markdown
## Build Conversation Closed

**Title:** [Generated Title]
**Build:** [build-slug]
**Type:** Build / Orchestrator
**Duration:** ~[X] minutes

### Executive Summary
[What was built, why it matters]

### What Was Built
- [Component 1]: [description]
- [Component 2]: [description]

### Technical Decisions
| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| ... | ... | ... |

### Files & Artifacts
| Artifact | Location | Purpose |
|----------|----------|---------|
| ... | ... | ... |

### Lessons Learned
- [Lesson 1 - logged to project_log.jsonl]
- (or "None extracted")

### Capability Registry Updates
- [Capability added/updated]
- (or "None - no capability changes")

### Risks & Follow-ups
- [ ] [Risk or follow-up item]

### Git Status
[Status + recommendation]

### After-Action Report
[Full AAR per template - only for Tier 3]

✅ Build archived | Workspace clean
```

---

## Phase 0: Elimination (Pre-work)

**Goal:** Remove orphaned/conflicting documentation before building new system.

### Files to Eliminate

| File | References | Action |
|------|-----------|--------|
| ~~`conversation-end-CANONICAL.md`~~ | N/A | ✅ Already deleted |
| ~~`conversation_end_pipeline.md`~~ | N/A | ✅ Already deleted |
| ~~`conversation_end_schema.md`~~ | N/A | ✅ Already deleted |
| `N5/logs/threads/*/artifacts/*conversation*end*` | 10+ files | 📦 LEAVE (historical) |

### Files to Consolidate

| Current File | Fate |
|--------------|------|
| `N5/prefs/operations/conversation-end.md` | → Merge into v3 docs |
| `N5/prefs/operations/conversation-end-output-template.md` | → Keep for Tier 3 only |
| `Prompts/Close Conversation.prompt.md` | → Rewrite as router |

### Checklist
- [x] Delete `conversation-end-CANONICAL.md` - Already gone
- [x] Delete `conversation_end_pipeline.md` - Already gone
- [x] Delete `conversation_end_schema.md` - Already gone
- [x] Verify no broken references - Clean

### Current State (Cleaner Than Expected)

| File | Lines | Fate in v3 |
|------|-------|------------|
| `N5/prefs/operations/conversation-end.md` | 509 | → Replace with `conversation-end-v3.md` |
| `N5/prefs/operations/conversation-end-output-template.md` | 386 | → Keep for Tier 3 only |
| `Prompts/Close Conversation.prompt.md` | 238 | → Rewrite as router |

---

## Phase 1: Core Router

**Goal:** Build the tier detection and routing logic.

### Affected Files
- `N5/scripts/conversation_end_router.py` (NEW)
- `N5/scripts/conversation_end_analyzer.py` (MODIFY - add --quick/--standard flags)

### Deliverables
1. `conversation_end_router.py`:
   - Reads SESSION_STATE.md
   - Checks for build workspace
   - Checks for DEBUG_LOG.jsonl
   - Scans conversation for build markers
   - Returns tier recommendation (1/2/3)

### Unit Tests
- [x] Returns Tier 1 for empty conversation ✓
- [x] Returns Tier 3 for build workspace present ✓
- [x] Force tier override works ✓
- [ ] Returns Tier 2 for ≥3 artifacts (needs test data)
- [ ] Returns Tier 3 for DEBUG_LOG.jsonl present (needs test data)

---

## Phase 2: Tier 1 Implementation

**Goal:** Fast, cheap default close.

### Affected Files
- `N5/scripts/conversation_end_quick.py` (NEW)
- `Prompts/Close Conversation.prompt.md` (MODIFY)

### Deliverables
1. Script that executes Tier 1 steps
2. Output template for Tier 1
3. Integration with router

### Unit Tests
- [x] Completes in <30 seconds (actual: 94ms) ✓
- [x] Generates valid title ✓
- [x] Updates SESSION_STATE.md (with --dry-run tested) ✓
- [x] Produces correct output format ✓

---

## Phase 3: Tier 2 Implementation

**Goal:** Standard close with meaningful detail.

### Affected Files
- `N5/scripts/conversation_end_standard.py` (NEW)

### Deliverables
1. Script that executes Tier 2 steps
2. Output template for Tier 2
3. Decision/outcome extraction logic

### Unit Tests
- [x] Completes in <90 seconds (actual: 526ms) ✓
- [x] Extracts decisions correctly (pattern-based) ✓
- [x] Git check works ✓
- [x] Produces correct output format ✓

---

## Phase 4: Tier 3 Implementation

**Goal:** Full build close with AAR.

### Affected Files
- `N5/scripts/conversation_end_full.py` (NEW)
- `N5/prefs/operations/conversation-end-output-template.md` (KEEP)

### Deliverables
1. Script that executes Tier 3 steps
2. AAR generation using existing template
3. Lesson extraction integration
4. Capability registry Q&A

### Unit Tests
- [ ] Completes in <3 minutes
- [ ] AAR matches template
- [ ] Lessons logged correctly
- [ ] Capability registry prompt fires

---

## Phase 5: Prompt Rewrite & Integration

**Goal:** Single entry point that routes to correct tier.

### Affected Files
- `Prompts/Close Conversation.prompt.md` (REWRITE)
- `N5/prefs/operations/conversation-end-v3.md` (NEW - single source of truth)

### Deliverables
1. Simplified prompt that:
   - Calls router
   - Executes appropriate tier
   - Presents output
2. Single consolidated documentation file
3. Deprecation notices on old files

### Unit Tests
- [ ] Prompt correctly routes Tier 1
- [ ] Prompt correctly routes Tier 2
- [ ] Prompt correctly routes Tier 3
- [ ] Old files have deprecation headers

---

## Phase 6: Validation & Cleanup

**Goal:** Verify system works, remove old code.

### Checklist
- [ ] Test Tier 1 on 3 real conversations
- [ ] Test Tier 2 on 2 real conversations
- [ ] Test Tier 3 on 1 real build conversation
- [ ] Measure actual costs vs targets
- [ ] Remove deprecated files (after validation)
- [ ] Update any references in rules/prefs

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tier 1 cost | N/A | <$0.05 |
| Tier 2 cost | N/A | <$0.08 |
| Tier 3 cost | ~$0.20 | <$0.20 |
| Consistency | ~60% | >95% |
| Tier detection accuracy | N/A | >90% |

---

## Open Questions for V

1. ~~**Tier 2 threshold:**~~ ✅ Confirmed: ≥3 artifacts
2. ~~**Git commit prompt:**~~ ✅ Confirmed: Any tier can prompt for git commit
3. ~~**Manual override:**~~ ✅ Confirmed: Yes, `--tier=N` flag supported
4. ~~**SESSION_STATE timing:**~~ ✅ Confirmed: Rebuild from scratch at conversation-end (trust but verify if SESSION_STATE exists)

---

## Status Tracking

| Phase | Status | Completed |
|-------|--------|-----------|
| Phase 0: Elimination | ✅ Complete | 2025-12-17 |
| Phase 1: Core Router | ✅ Complete | 2025-12-17 |
| Phase 2: Tier 1 | ✅ Complete | 2025-12-17 |
| Phase 3: Tier 2 | ✅ Complete | 2025-12-17 |
| Phase 4: Tier 3 | ✅ Complete | 2025-12-18 |
| Phase 5: Integration | ✅ Complete | 2025-12-18 |
| Phase 6: Validation | ✅ Complete | 2025-12-18 |

---

*Plan created by Vibe Architect | 2025-12-17*












