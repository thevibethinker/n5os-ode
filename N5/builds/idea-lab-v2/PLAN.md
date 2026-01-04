# Plan: Idea Lab v2.0 - Triage & Dynamic Modality

## Open Questions
- None. Requirements clear.

## Checklist
- [x] Phase 1: Initialize Triage List & Schema ☑
- [x] Phase 2: Implement "Modality Monitor" Logic in Prompt ☑
- [x] Phase 3: Update Lab Orchestrator Prompt (Budget & Fluidity) ☑
- [x] Phase 4: Final Validation & Structural Audit ☑
- [x] Phase 5: Add Raw Dump Mode ☑
- [x] Phase 6: Lazy Folder Creation ☑
- [x] Phase 7: Session Logging & Archive State ☑

## Phase 1: Initialize Triage List
- **Affected Files:** `file 'Lists/idea-triage.jsonl'`
- **Changes:** Create empty file. Define schema in `file 'Lists/schemas/idea-triage.schema.json'` (if applicable, otherwise append-only JSONL).
- **Unit Tests:** `test -f Lists/idea-triage.jsonl`

## Phase 2: Dynamic Modality Logic
- **Affected Files:** `file 'Prompts/Idea Lab.prompt.md'`
- **Changes:** 
  - Explicitly define "Modality Monitor" persona as a sub-routine.
  - Add "Fluid Modality" instructions: switch midstream if returns diminish.
  - Add 15-minute strict budget instruction.
- **Unit Tests:** Verify instructions present in file.

## Phase 3: Lab Orchestrator Updates
- **Affected Files:** `file 'Prompts/Idea Lab.prompt.md'`
- **Changes:** Integrate "Add to triage" action using `lists-add` to the new triage file.
- **Unit Tests:** Verify `lists-add` target is updated.

## Phase 5: Add Raw Dump Mode
- **Affected Files:** `file 'Prompts/Idea Lab.prompt.md'`
- **Changes:**
  - Add "Raw Dump" as fourth modality option
  - V word-vomits for up to 15 minutes without structure
  - AI synthesizes patterns, themes, contradictions AFTER
  - Output: structured synthesis + extracted threads
- **Unit Tests:**
  - [ ] Prompt contains "Raw Dump" mode description
  - [ ] Synthesis step explicitly documented

## Phase 6: Lazy Folder Creation
- **Affected Files:** `file 'N5/scripts/promote_to_lab.py'`, `file 'Prompts/Idea Lab.prompt.md'`
- **Changes:**
  - Triage = add to idea-triage.jsonl (NO folder creation)
  - Folder creation ONLY when entering Lab session
  - New script: `start_lab_session.py` creates folder on-demand
- **Unit Tests:**
  - [ ] promote_to_lab.py no longer creates folders
  - [ ] start_lab_session.py creates folder structure
  - [ ] Prompt reflects lazy creation workflow

## Phase 7: Session Logging & Archive State
- **Affected Files:** `file 'N5/scripts/start_lab_session.py'`, exploration README templates
- **Changes:**
  - Each session logged with timestamp in exploration README
  - Add `status` field: active | paused | archived
  - Archive = exploration complete, learnings crystallized
- **Unit Tests:**
  - [ ] Session log format defined
  - [ ] Status field present in exploration README
  - [ ] Archive criteria documented

## Success Criteria
- [x] Triage list exists and is usable.
- [x] Prompt explicitly manages a 15-minute budget.
- [x] Prompt explicitly allows modality switching and monitors for diminishing returns.
- [x] Manual promotion process is preserved.

## Validation Report (2026-01-04) - FINAL

### Phase 1-4 Tests (Previously Passing)
- ✓ Triage list exists
- ✓ 15-minute budget present  
- ✓ Monitor sub-routine present
- ✓ Triage list target correct

### Phase 5 Tests
- ✓ Raw Dump mode present in prompt
- ✓ Synthesis step documented

### Phase 6 Tests
- ✓ promote_to_lab.py compiles
- ✓ start_lab_session.py compiles
- ✓ promote_to_lab.py no longer creates folders
- ✓ Prompt references start_lab_session.py

### Phase 7 Tests
- ✓ Status field in exploration README (active | paused | archived)
- ✓ Session logging function present (--log)
- ✓ Archive function present (--archive)
- ✓ Help output shows all CLI options

**BUILD COMPLETE: 7/7 phases (100%)**




