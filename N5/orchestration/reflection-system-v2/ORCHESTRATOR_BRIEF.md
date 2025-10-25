# Reflection System V2 - Orchestrator Brief

**Project:** Reflection Processing System V2  
**Architecture:** Worker-Orchestrator Model  
**Created:** 2025-10-24  
**Status:** Ready to Launch

---

## Mission

Build a Drive-centric, block-based reflection processing system that:
1. Polls Google Drive folder for new reflections (text/audio)
2. Classifies reflections with multi-label taxonomy
3. Generates appropriate blocks based on classification
4. Routes to correct voice profiles (internal/professional/social)
5. Applies style guides per block type
6. Suggests new block types when patterns emerge
7. Maintains idempotency and state tracking

---

## Workers Overview

### Worker 1: Drive Integration & Transcription
**Time:** 45 min | **Dependency:** None | **Parallel:** Yes (with W2)

Deliverables:
- `N5/scripts/reflection_ingest_v2.py`
- `N5/.state/reflection_drive_state.json`
- Drive polling with idempotency
- Auto-transcription for audio

Brief: `file 'N5/orchestration/reflection-system-v2/workers/WORKER_1_drive_integration.md'`

---

### Worker 2: Classification & Block Registry
**Time:** 60 min | **Dependency:** None | **Parallel:** Yes (with W1)

Deliverables:
- `N5/prefs/reflection_block_registry.json` (B50-B99 definitions)
- `N5/scripts/reflection_classifier.py`
- Classification → block mapping
- Update main block registry

Brief: `file 'N5/orchestration/reflection-system-v2/workers/WORKER_2_classification.md'`

---

### Worker 3: Style Guide Generation
**Time:** 90 min | **Dependency:** W2 | **Parallel:** No

Deliverables:
- 13 style guide files in `N5/prefs/communication/style-guides/reflections/`
- Voice extraction + transformation application
- Examples integration from transformation-pairs-library

Brief: `file 'N5/orchestration/reflection-system-v2/workers/WORKER_3_style_guides.md'`

---

### Worker 4: Block Generator with Voice Routing
**Time:** 60 min | **Dependency:** W2, W3 | **Parallel:** No

Deliverables:
- `N5/scripts/reflection_block_generator.py`
- Voice routing: internal/professional/social
- Auto-approve ≤10 blocks, manual >10
- Block output to structured directories

Brief: `file 'N5/orchestration/reflection-system-v2/workers/WORKER_4_block_generator.md'`

---

### Worker 5: Block Suggester & Synthesizer Repurpose
**Time:** 45 min | **Dependency:** W2 | **Parallel:** Yes (with W3, W4)

Deliverables:
- `N5/scripts/reflection_block_suggester.py`
- Analysis of reflection-synthesizer → repurpose plan
- New block type detection algorithm

Brief: `file 'N5/orchestration/reflection-system-v2/workers/WORKER_5_block_suggester.md'`

---

### Worker 6: Main Orchestrator & Integration
**Time:** 60 min | **Dependency:** All workers | **Parallel:** No

Deliverables:
- `N5/scripts/reflection_orchestrator_v2.py`
- `N5/commands/reflection-process-v2.md`
- Integration tests
- Documentation
- Scheduled task setup

Brief: `file 'N5/orchestration/reflection-system-v2/workers/WORKER_6_orchestrator.md'`

---

## Execution Phases

### Phase 1: Foundation (Parallel)
**Launch:** Workers 1 & 2 simultaneously  
**Duration:** 60 minutes (W2 is longest)  
**Gate:** Both complete before Phase 2

---

### Phase 2: Content Generation
**Launch:** Worker 3 (depends on W2)  
**Duration:** 90 minutes  
**Parallel:** Can start W5 during this phase  
**Gate:** W3 complete before W4

---

### Phase 3: Intelligence & Generation
**Launch:** Workers 4 & 5  
**Duration:** 60 minutes (W4 is longest)  
**Dependency:** W4 needs W2+W3, W5 only needs W2  
**Gate:** Both complete before Phase 4

---

### Phase 4: Integration
**Launch:** Worker 6  
**Duration:** 60 minutes  
**Gate:** All previous workers complete

---

## Total Timeline

**Optimized (with parallelization):** ~4.5 hours
- Phase 1: 60 min (W1 + W2 parallel)
- Phase 2: 90 min (W3 + W5 parallel for first 45 min)
- Phase 3: 60 min (W4 after W3 completes)
- Phase 4: 60 min (W6 integration)

**Sequential (if needed):** ~6.5 hours

---

## Success Criteria

System complete when:
- [ ] Drive folder polls with idempotency
- [ ] Audio transcription works
- [ ] Multi-label classification functional
- [ ] 13 style guides created
- [ ] Block generation with voice routing works
- [ ] Auto/manual approval logic correct
- [ ] Block suggester detects patterns
- [ ] Reflection-synthesizer fate decided
- [ ] Integration tests pass
- [ ] Documentation complete
- [ ] Scheduled task configured

---

## Key Design Decisions

### Drive Folder ID
`16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV`

### Block Numbering
B50-B99 (meetings 1-49, reflections 50-99, room to expand)

### Voice Routing
- **B50-B59 (Internal):** `voice.md`
- **B60-B79 (Professional):** `voice.md`
- **B80-B89 (Social):** `social-media-voice.md`
- **B90-B99 (Meta):** Context-dependent

### Approval Logic
- ≤10 blocks: Auto-generate all
- >10 blocks: Prompt V for selection

### Polling Frequency
**PENDING V's DECISION:** Hourly vs 4x daily

### Idempotency
State tracking via `N5/.state/reflection_drive_state.json`

### Polling Offset
7-minute offset (e.g., `:07` past hour) to avoid crash windows

---

## Architectural Principles Applied

- **P0 (Rule-of-Two):** Max 2 config files loaded per operation
- **P1 (Human-Readable):** All configs in JSON/Markdown
- **P2 (SSOT):** Single registry for block definitions
- **P5 (Anti-Overwrite):** Idempotency prevents re-processing
- **P7 (Dry-Run):** All scripts support `--dry-run`
- **P8 (Minimal Context):** Load only what's needed
- **P11 (Failure Modes):** Graceful degradation on errors
- **P15 (Complete Before Claiming):** Verify before marking done
- **P18 (Verify State):** Check file exists before state update
- **P19 (Error Handling):** Comprehensive error handling
- **P20 (Modular):** Clear component boundaries
- **P21 (Document Assumptions):** Classification rationale included
- **P22 (Language Selection):** Python for all scripts (LLM corpus advantage)

---

## Next Steps

1. **V confirms polling frequency** (hourly vs 4x daily)
2. **Launch Phase 1:** Start Workers 1 & 2 in parallel
3. **Monitor:** Check briefs, verify progress
4. **Launch subsequent phases** as dependencies complete
5. **Integration testing:** Worker 6 validates end-to-end
6. **Deployment:** Configure scheduled task

---

## Worker Brief Index

- file 'N5/orchestration/reflection-system-v2/workers/WORKER_1_drive_integration.md'
- file 'N5/orchestration/reflection-system-v2/workers/WORKER_2_classification.md'
- file 'N5/orchestration/reflection-system-v2/workers/WORKER_3_style_guides.md' (to be created)
- file 'N5/orchestration/reflection-system-v2/workers/WORKER_4_block_generator.md' (to be created)
- file 'N5/orchestration/reflection-system-v2/workers/WORKER_5_block_suggester.md' (to be created)
- file 'N5/orchestration/reflection-system-v2/workers/WORKER_6_orchestrator.md' (to be created)

---

## System Architecture Reference

Main plan: file 'N5/orchestration/reflection-system-v2/REFLECTION_SYSTEM_V2_PLAN.md'

---

**Status:** Awaiting V's polling frequency decision, then ready to launch Phase 1  
**Created:** 2025-10-24 18:10 ET
