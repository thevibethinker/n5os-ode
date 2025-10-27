# Worker 6 Deployment Brief

**Date:** 2025-10-26 21:54 ET  
**Status:** Ready to Deploy  
**Prerequisites:** ✅ All Met (Workers 1-5 Complete)

---

## Mission

Build end-to-end orchestrator that coordinates all workers + create scheduled task for automatic polling.

---

## Context from Workers 1-5

### ✅ What's Complete (4,524 lines of production code)

**Worker 1:** `reflection_ingest_v2.py` (344 lines)
- Drive folder polling
- Audio transcription
- State tracking

**Worker 2:** `reflection_classifier.py` (342 lines)
- Multi-label classification
- Block type mapping
- Confidence scoring

**Worker 3:** Style guides (2,472 lines)
- 11 block types (B50-B99)
- Voice routing rules
- Templates and examples

**Worker 4:** `reflection_block_generator.py` (488 lines)
- Multi-block content generation
- Voice profile application
- Auto-approve logic

**Worker 5:** Pattern detection + Synthesizer V2 (878 lines)
- `reflection_block_suggester.py` (407 lines)
- `reflection_synthesizer_v2.py` (471 lines)
- B90/B91 cross-reflection synthesis

---

## Worker 6 Deliverables

### 1. Main Orchestrator Script
**File:** `N5/scripts/reflection_orchestrator.py`

**Purpose:** Coordinate end-to-end reflection processing pipeline

**Flow:**
```
1. Ingest (Worker 1) → Pull from Drive + transcribe
2. Classify (Worker 2) → Multi-label classification
3. Generate (Worker 4) → Create blocks from transcript
4. Suggest (Worker 5) → Pattern detection (periodic)
5. Synthesize (Worker 5) → B90/B91 generation (weekly)
6. Registry Update → Track all processed reflections
```

**CLI:**
```bash
python3 reflection_orchestrator.py \
  --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
  --run-suggester \
  --run-synthesizer \
  [--dry-run]

# Or via command shortcut
n5 reflect process
```

### 2. Scheduled Task
**Integration:** N5 scheduled tasks system

**Frequency Options:**
- Hourly: `7 */1 * * *`
- 4x daily: `7 */6 * * *`
- **Recommended:** 4x daily (at :07, 6:07, 12:07, 18:07)

**Task Command:**
```bash
python3 /home/workspace/N5/scripts/reflection_orchestrator.py \
  --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
  --run-suggester weekly \
  --run-synthesizer weekly
```

### 3. Command Integration
**File:** Add to `N5/config/commands.jsonl`

**Command:** `reflect process`
**Alias:** `rp`
**Description:** "Process reflection queue (ingest + classify + generate blocks)"

### 4. Registry System
**File:** `N5/records/reflections/registry/reflections.jsonl`

**Schema:**
```json
{
  "id": "2025-10-24_pricing-strategy",
  "date_iso": "2025-10-24T14:30:00Z",
  "source_file": "2025-10-24_pricing-strategy.m4a",
  "transcript_path": "incoming/2025-10-24_pricing-strategy.m4a.transcript.jsonl",
  "classification": {
    "primary": ["B71", "B73"],
    "confidence": 0.85
  },
  "blocks_generated": ["B71", "B73"],
  "output_directory": "outputs/2025-10-24/pricing-strategy/",
  "status": "approved",
  "processed_at_iso": "2025-10-24T14:35:00Z"
}
```

---

## Implementation Plan

### Phase 1: Orchestrator Script (60 min)

**Step 1:** Create orchestrator skeleton
```python
#!/usr/bin/env python3
import subprocess, logging, json
from pathlib import Path
from datetime import datetime

def run_worker(script: str, args: list, dry_run: bool = False):
    """Execute worker script with error handling"""
    
def ingest_reflections(folder_id: str, dry_run: bool = False):
    """Worker 1: Ingest from Drive"""
    
def classify_reflections(dry_run: bool = False):
    """Worker 2: Classify new transcripts"""
    
def generate_blocks(dry_run: bool = False):
    """Worker 4: Generate block content"""
    
def suggest_blocks(dry_run: bool = False):
    """Worker 5: Pattern detection"""
    
def synthesize_compound(dry_run: bool = False):
    """Worker 5: B90/B91 synthesis"""
    
def update_registry(processed: list, dry_run: bool = False):
    """Update reflection registry"""
```

**Step 2:** Implement each worker wrapper
- Call subprocess with proper args
- Capture output and errors
- Log progress
- Handle failures gracefully

**Step 3:** Implement registry tracking
- Load existing registry
- Add new entries
- Update statuses
- Append to JSONL

**Step 4:** Add CLI interface
- `--folder-id` (required)
- `--run-suggester` (optional, default: skip)
- `--run-synthesizer` (optional, default: skip)
- `--dry-run` (optional)

### Phase 2: Scheduled Task (30 min)

**Step 1:** Create scheduled task
```bash
python3 /home/workspace/N5/scripts/create_scheduled_task.py \
  --rrule "FREQ=DAILY;BYHOUR=7,13,19,1;BYMINUTE=7" \
  --instruction "Run reflection processing pipeline: ingest from Drive, classify, generate blocks. Use reflection_orchestrator.py with folder ID 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV" \
  --delivery-method none
```

**Step 2:** Test scheduled task
- Verify cron schedule
- Check task appears in list
- Dry-run execution

### Phase 3: Command Integration (15 min)

**Step 1:** Add to commands.jsonl
```json
{
  "command": "reflect process",
  "alias": "rp",
  "description": "Process reflection queue",
  "script": "reflection_orchestrator.py",
  "args": "--folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV"
}
```

**Step 2:** Test command
```bash
n5 reflect process --dry-run
```

### Phase 4: Integration Testing (30 min)

**Test 1: End-to-End Pipeline**
```bash
python3 reflection_orchestrator.py \
  --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
  --dry-run
  
# Expected:
# 1. Ingest: Pull from Drive
# 2. Classify: Process transcripts
# 3. Generate: Create blocks
# 4. Registry: Update tracking
```

**Test 2: Suggester Integration**
```bash
python3 reflection_orchestrator.py \
  --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
  --run-suggester \
  --dry-run
  
# Expected: Pattern detection runs after generation
```

**Test 3: Synthesizer Integration**
```bash
python3 reflection_orchestrator.py \
  --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
  --run-synthesizer \
  --dry-run
  
# Expected: B90/B91 generation runs at end
```

**Test 4: Scheduled Task**
```bash
# Manually trigger scheduled task
python3 /home/workspace/N5/scripts/trigger_task.py --task-id <reflection_task_id>

# Expected: Full pipeline executes automatically
```

---

## Architecture Decisions

### Error Handling Strategy

**Per-Worker Failures:**
- Log error with context
- Continue to next worker
- Flag reflection as "failed" in registry
- Don't crash entire pipeline

**Critical Failures:**
- Drive connection fails → abort (nothing to process)
- Registry corruption → abort (can't track state)

**Recoverable Failures:**
- Single transcript fails classification → skip, continue
- Single block generation fails → log, continue
- Synthesizer fails → log, continue (not critical)

### Registry Design

**Why JSONL:**
- Append-only (no overwrites)
- One reflection per line
- Easy to parse
- Git-friendly

**What to Track:**
- Source file info
- Classification results
- Blocks generated
- Approval status
- Timestamps

### Suggester/Synthesizer Frequency

**Suggester:**
- Weekly is sufficient
- Requires ≥3 examples to suggest
- Won't be useful on every run

**Synthesizer:**
- Weekly for B90/B91
- Requires multiple reflections
- Cross-reflection synthesis takes time

**Implementation:**
- CLI flags: `--run-suggester`, `--run-synthesizer`
- Scheduled task: Only pass these flags weekly
- Default: Skip both (focus on individual processing)

---

## Integration Points

### Input Dependencies (All Met)
✅ Worker 1: Drive ingestion  
✅ Worker 2: Classification  
✅ Worker 3: Style guides  
✅ Worker 4: Block generation  
✅ Worker 5: Pattern detection + Synthesizer

### Output Products
- **Orchestrator:** Coordinates all workers
- **Scheduled Task:** Automatic execution
- **Command:** `n5 reflect process`
- **Registry:** Complete audit trail
- **Documentation:** User guide

---

## File Structure

```
N5/
├── scripts/
│   ├── reflection_orchestrator.py          # NEW: Main orchestrator
│   ├── reflection_ingest_v2.py             # Worker 1
│   ├── reflection_classifier.py            # Worker 2
│   ├── reflection_block_generator.py       # Worker 4
│   ├── reflection_block_suggester.py       # Worker 5
│   └── reflection_synthesizer_v2.py        # Worker 5
│
├── records/reflections/
│   ├── incoming/                           # Transcripts
│   ├── outputs/                            # Generated blocks
│   ├── suggestions/                        # Block suggestions
│   └── registry/
│       └── reflections.jsonl               # NEW: Registry
│
├── config/
│   └── commands.jsonl                      # NEW: Add reflect command
│
└── prefs/
    ├── reflection_block_registry.json      # Block definitions
    └── communication/style-guides/reflections/  # Style guides
```

---

## Testing Strategy

### Unit Tests
- Test each orchestrator function independently
- Mock worker scripts
- Verify error handling

### Integration Tests
- End-to-end pipeline (dry-run)
- Registry updates correctly
- State tracking works
- Command integration works

### Production Readiness
- Run on real reflection
- Verify output quality
- Check registry accuracy
- Monitor scheduled task

---

## Success Criteria

Worker 6 is complete when:

1. ✅ Orchestrator coordinates Workers 1-5
2. ✅ Registry tracks all reflections
3. ✅ Scheduled task created and working
4. ✅ Command integration complete
5. ✅ Error handling robust
6. ✅ Dry-run support throughout
7. ✅ End-to-end test passes
8. ✅ Documentation complete

---

## Principles to Follow

- **P7 (Dry-Run):** Full dry-run support
- **P11 (Failure Modes):** Graceful degradation
- **P15 (Complete Before Claiming):** All tests pass
- **P18 (Verify State):** Registry validates correctly
- **P19 (Error Handling):** Per-worker error isolation
- **P20 (Modular):** Clean worker separation

---

## Post-Deployment Checklist

### Immediate
- [ ] Run end-to-end pipeline (dry-run)
- [ ] Verify registry created correctly
- [ ] Test scheduled task
- [ ] Confirm command works

### Before Production
- [ ] Set polling frequency (recommend 4x daily)
- [ ] Generate more classifications (run Worker 2 on all transcripts)
- [ ] Test with real reflection upload
- [ ] Monitor first few automatic runs

### Documentation
- [ ] Update N5 README with reflection system
- [ ] Create user guide for uploading reflections
- [ ] Document output review workflow
- [ ] Add troubleshooting section

---

## Estimated Timeline

**Phase 1:** Orchestrator Script - 60 minutes  
**Phase 2:** Scheduled Task - 30 minutes  
**Phase 3:** Command Integration - 15 minutes  
**Phase 4:** Integration Testing - 30 minutes  
**Documentation:** 15 minutes

**Total:** ~2.5 hours

---

## Outstanding Items from Previous Workers

### From Worker 4
- `count_blocks_generated()` is placeholder
- Can implement here in orchestrator

### From Worker 5
- `get_next_block_id()` hardcoded to 74
- Should read from registry dynamically
- Fix in orchestrator

### Synthesizer Consolidation
- V2 is separate file from legacy
- Decision: Keep both for now
- Can deprecate legacy after production validation

---

## Risk Assessment

**Overall Risk:** ✅ LOW

**Workers 1-5:** All validated and working  
**Architecture:** Sound orchestration pattern  
**Dependencies:** All met  
**Blockers:** None

**Confidence Level:** High - ready for final integration

---

## Next Steps

1. **Build orchestrator script** (~60 min)
2. **Create scheduled task** (~30 min)
3. **Integrate command** (~15 min)
4. **End-to-end testing** (~30 min)
5. **Production deployment**

---

**Status:** Ready to Deploy  
**Risk:** Low  
**Dependencies:** All Met  
**Timeline:** 2.5 hours to completion

**Deploy when ready!**

**2025-10-26 21:54 ET**
