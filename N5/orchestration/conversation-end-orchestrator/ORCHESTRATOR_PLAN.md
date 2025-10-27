# Conversation-End Orchestrator Plan

**Project:** conversation-end-orchestrator  
**Version:** 1.0.0  
**Created:** 2025-10-27 03:33 ET  
**Status:** Planning

---

## Problem

Current `n5_conversation_end.py` combines analysis + execution + UI in one monolithic script with interactive prompts. This creates:

1. **Blocking in automation** - Interactive prompts block scheduled/automated execution
2. **No preview** - Changes happen immediately without review
3. **All-or-nothing** - Can't accept some changes and reject others
4. **Poor UX** - Terminal-based interaction doesn't match Zo's modern UI

---

## Solution: Two-Phase Orchestrated System

### Phase 1: Analysis & Proposal (Worker 1)
**Intelligent, automated, safe**
- Scan conversation workspace
- Classify files (temp/final/deliverable)
- Generate smart title from SESSION_STATE.md + AAR
- Propose file moves with clear destinations
- Create archive structure
- Generate proposal document

### Phase 2: Review & Execution (Worker 2)
**User-controlled, granular, reversible**
- Display proposal in clean format
- Allow selective approval (checkboxes per action)
- Execute only approved actions
- Provide undo/rollback capability
- Update timeline + git + registry

---

## Worker Breakdown

### Worker 1: Analysis Engine
**File:** `WORKER_1_ANALYSIS_ENGINE.md`  
**Time:** 45 min  
**Dependencies:** None

**Deliverables:**
1. `/home/workspace/N5/scripts/conversation_end_analyzer.py`
2. Proposal schema in `/home/workspace/N5/schemas/conversation-end-proposal.schema.json`
3. Test suite

**Responsibilities:**
- File classification (heuristics + size + naming patterns)
- Title generation (from SESSION_STATE + AAR)
- Destination mapping (intelligent routing)
- Conflict detection
- Safety checks

### Worker 2: Proposal Generator
**File:** `WORKER_2_PROPOSAL_GENERATOR.md`  
**Time:** 30 min  
**Dependencies:** Worker 1

**Deliverables:**
1. `/home/workspace/N5/scripts/conversation_end_proposal.py`
2. Human-readable proposal formatter
3. JSON proposal output

**Responsibilities:**
- Generate structured proposal from analysis
- Group actions logically
- Add explanations for each action
- Calculate impacts
- Provide preview commands

### Worker 3: Execution Engine
**File:** `WORKER_3_EXECUTION_ENGINE.md`  
**Time:** 45 min  
**Dependencies:** Worker 2

**Deliverables:**
1. `/home/workspace/N5/scripts/conversation_end_executor.py`
2. Atomic operation handlers
3. Rollback system

**Responsibilities:**
- Execute approved actions atomically
- Dry-run mode
- Transaction log
- Rollback capability
- State verification

### Worker 4: CLI Interface
**File:** `WORKER_4_CLI_INTERFACE.md`  
**Time:** 30 min  
**Dependencies:** Worker 1, 2, 3

**Deliverables:**
1. Updated `n5_conversation_end.py` (orchestrator)
2. Interactive CLI for proposal review
3. Non-interactive mode for automation

**Responsibilities:**
- Call analyzer → generator → executor
- Display proposal with colors/formatting
- Accept user selections
- Handle --auto mode
- Email proposal option (for scheduled tasks)

### Worker 5: Integration & Testing
**File:** `WORKER_5_INTEGRATION.md`  
**Time:** 30 min  
**Dependencies:** All above

**Deliverables:**
1. End-to-end test suite
2. Integration with existing workflow
3. Migration guide
4. Documentation

**Responsibilities:**
- Test full workflow
- Verify P5 (anti-overwrite) compliance
- Test auto mode
- Test email mode
- Document usage

---

## Architecture Principles Applied

**P0 (Rule-of-Two):** Each worker loads max 2 context files  
**P1 (Human-Readable):** All proposals in clear markdown  
**P2 (SSOT):** Proposal JSON is single source of truth  
**P5 (Anti-Overwrite):** Analyzer checks for conflicts, executor verifies  
**P7 (Dry-Run):** Executor always supports dry-run  
**P11 (Failure Modes):** Each worker handles errors gracefully  
**P19 (Error Handling):** Comprehensive try/except with logging  
**P20 (Modular):** Clean separation: analyze → propose → execute  
**P22 (Language Selection):** Python (data processing + LLM corpus)

---

## Workflow Diagram

```
┌─────────────────────────────────────────────┐
│ User triggers conversation-end              │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ WORKER 1: Analysis Engine                   │
│ • Scan workspace                            │
│ • Classify files                            │
│ • Detect patterns                           │
│ • Generate title                            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ WORKER 2: Proposal Generator                │
│ • Structure analysis results                │
│ • Format human-readable                     │
│ • Add explanations                          │
│ • Generate JSON proposal                    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ WORKER 4: CLI Interface (orchestrator)      │
│ • Display proposal                          │
│ • Accept user input                         │
│ • Handle --auto / --email modes             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ WORKER 3: Execution Engine                  │
│ • Execute approved actions                  │
│ • Log transactions                          │
│ • Verify state                              │
│ • Support rollback                          │
└─────────────────────────────────────────────┘
```

---

## File Organization

```
N5/orchestration/conversation-end-orchestrator/
├── ORCHESTRATOR_PLAN.md (this file)
├── ORCHESTRATOR_MONITOR.md
├── WORKER_1_ANALYSIS_ENGINE.md
├── WORKER_2_PROPOSAL_GENERATOR.md
├── WORKER_3_EXECUTION_ENGINE.md
├── WORKER_4_CLI_INTERFACE.md
├── WORKER_5_INTEGRATION.md
└── conversation-end-design.md

N5/scripts/
├── conversation_end_analyzer.py (W1)
├── conversation_end_proposal.py (W2)
├── conversation_end_executor.py (W3)
└── n5_conversation_end.py (W4, updated orchestrator)

N5/schemas/
└── conversation-end-proposal.schema.json (W1)
```

---

## Deployment Sequence

### Sequential
1. Worker 1 (Analysis Engine) - foundational
2. Worker 2 (Proposal Generator) - depends on W1 schema
3. Worker 3 (Execution Engine) - depends on W2 proposal format

### Parallel (after W1-3)
4. Worker 4 (CLI) + Worker 5 (Integration) can run in parallel

### Total Time
~3 hours (45 + 30 + 45 + 30 + 30 = 180 min)

---

## Success Criteria

- [ ] Analyzer correctly classifies files (95%+ accuracy on test set)
- [ ] Title generation uses SESSION_STATE when available
- [ ] Proposal is human-readable and actionable
- [ ] User can selectively approve/reject actions
- [ ] Executor handles all file operations atomically
- [ ] --auto mode works for scheduled tasks
- [ ] --email mode generates proposal for remote approval
- [ ] Dry-run mode works end-to-end
- [ ] Rollback capability functions correctly
- [ ] Fresh conversation test passes (P12)
- [ ] No regressions in existing conversation-end functionality

---

## Usage Examples

### Interactive Mode
```bash
python3 N5/scripts/n5_conversation_end.py
# Shows proposal, asks for approval
# User can check/uncheck specific actions
# Executes only approved actions
```

### Auto Mode (Scheduled)
```bash
python3 N5/scripts/n5_conversation_end.py --auto
# Uses intelligent defaults
# Executes immediately
# Logs all actions
```

### Email Approval Mode
```bash
python3 N5/scripts/n5_conversation_end.py --email
# Generates proposal
# Emails to V
# Waits for reply with selections
# Executes approved actions
```

### Dry-Run
```bash
python3 N5/scripts/n5_conversation_end.py --dry-run
# Shows what would happen
# Doesn't execute anything
# Validates all paths
```

---

## Integration Points

**Existing Systems:**
- SESSION_STATE.md (read for context)
- Conversation registry (update on close)
- Timeline automation (log closure event)
- Git integration (commit option)
- Archive promotion (trigger if conditions met)

**New Capabilities:**
- Email-based approval for scheduled tasks
- Granular action selection
- Rollback capability
- Better title generation
- Conflict detection

---

## Risk Mitigation

**Risk:** File classification errors  
**Mitigation:** Conservative defaults, user review, dry-run

**Risk:** Loss of existing functionality  
**Mitigation:** Keep old script as fallback, comprehensive testing

**Risk:** Performance degradation  
**Mitigation:** Lazy evaluation, caching, parallel where possible

**Risk:** User confusion with new UX  
**Mitigation:** Clear documentation, examples, help text

---

## Future Enhancements

**Phase 2 (post-MVP):**
- Web UI for proposal review (replace CLI)
- ML-based file classification
- Learning from user selections
- Suggest archive structure from past conversations
- Integration with conversation search

---

**Status:** Ready for worker deployment  
**Next Step:** Create worker briefs  
**Orchestrator:** con_O4rpz6MPrQXLbOlX  
**Created:** 2025-10-27 03:33 ET
