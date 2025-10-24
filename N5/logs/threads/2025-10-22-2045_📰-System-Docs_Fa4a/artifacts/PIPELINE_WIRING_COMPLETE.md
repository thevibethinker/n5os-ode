# Pipeline Wiring Complete
**Date:** 2025-10-22  
**Thread:** con_6eNkFTCmluuGFa4a  
**Status:** ✅ Complete

---

## Summary

Resumed work on Candidate Intake Processor and successfully wired it into the Pipeline Orchestrator CLI.

## What Was Delivered

### 1. Pipeline Orchestrator (`pipeline/run.py`)
- End-to-end orchestration: intake → parse → score → dossier
- `--from-inbox` flag to run candidate intake first
- `--dry-run` support throughout
- Per-candidate isolation with continue-on-error
- JSON summary output with detailed step results
- Pipeline run log written to `jobs/<job>/pipeline_run.json`

### 2. Documentation
- `file 'ZoATS/pipeline/README.md'` - Complete usage guide and output structure
- `file 'ZoATS/workers/pipeline_cli.md'` - Updated spec (Status: Complete)
- `file 'ZoATS/docs/ROADMAP.md'` - Split architecture and dossier evolution
- `file 'ZoATS/WORKERS_PLAN.md'` - Updated with Candidate Intake Processor + Gmail Intake (Week 2)

### 3. Integration Verified
- Tested dry-run mode: intake + parser working correctly
- Tested with existing smoke-test job candidates
- Graceful handling of missing workers (scorer, dossier not yet implemented)
- Status tracking: complete / partial_complete / parser_failed / scorer_failed / dossier_failed / error

## Test Results

### Dry-run Test (--from-inbox)
```
[pipeline] starting for job: smoke-test
[stage] running candidate intake
[pipeline] discovered 2 candidate(s)
[pipeline] processing alice-johnson-st001-2025-10-22
  ✓ parser: success
  ⊘ scorer: not_implemented
  ⊘ dossier: not_implemented
  → status: partial_complete
[pipeline] processing smoke-test-john-doe-20251022-nxbh27
  ✗ parser: failed (invalid PDF)
  → status: parser_failed
[pipeline] complete: 0/2 fully processed, 1 partial, 1 failed
```

## Architecture Decisions Confirmed

1. **Split Architecture** (from earlier course correction)
   - Gmail Intake Worker (Week 2) → inbox_drop/ → Candidate Intake Processor → jobs/<job>/candidates/
   - Pipeline remains source-agnostic

2. **Candidate Dossier Evolution**
   - `interactions.md` initialized by Candidate Intake Processor
   - Grows chronologically with emails, calls, notes, decisions
   - Becomes comprehensive candidate history

## Files Delivered

**Core Implementation:**
- `file 'ZoATS/pipeline/run.py'` (165 lines, executable)
- `file 'ZoATS/pipeline/README.md'`

**Documentation Updates:**
- `file 'ZoATS/workers/pipeline_cli.md'` (Status: Complete)
- `file 'ZoATS/docs/ROADMAP.md'` (Gmail Intake + Dossier Evolution)
- `file 'ZoATS/WORKERS_PLAN.md'` (Architecture split)

**Supporting:**
- `file 'ZoATS/workers/gmail_intake.md'` (Week 2 spec stub)
- `file 'ZoATS/workers/email_intake.md'` (Deprecation notice)

## Integration Points

- Test Harness can call: `python pipeline/run.py --job demo --from-inbox --dry-run`
- Parser already working (from previous build)
- Scorer/Dossier: Stubs ready, pipeline will call when implemented
- Output structure supports future UI consumption

## Next Steps for ZoATS

1. Implement Scoring Engine (`workers/scoring/main.py`)
2. Implement Dossier Generator (`workers/dossier/main.py`)
3. Create Test Harness with fixtures (`tests/smoke.py`)
4. End-to-end smoke test with demo job
5. (Week 2) Build Gmail Intake Worker

## Verification Commands

```bash
# Dry-run with intake
python pipeline/run.py --job smoke-test --from-inbox --dry-run

# Process existing candidates
python pipeline/run.py --job smoke-test --dry-run

# Real run
python pipeline/run.py --job smoke-test --from-inbox
```

---

**Status:** Pipeline orchestration complete and tested. Ready for downstream worker integration (Scorer, Dossier).

**References:**
- Candidate Intake spec: `file 'ZoATS/workers/candidate_intake.md'`
- Candidate Intake implementation: `file 'ZoATS/workers/candidate_intake/main.py'`
- Pipeline orchestrator: `file 'ZoATS/pipeline/run.py'`
- Workers plan: `file 'ZoATS/WORKERS_PLAN.md'`
