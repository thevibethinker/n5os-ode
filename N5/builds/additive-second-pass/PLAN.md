---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.1
type: build_plan
status: in_progress
provenance: con_ctpO4tmxumzIn8RP
---
# Plan: Additive Second Pass — Broader Idea Extraction

**Objective:** Re-scan meetings that were processed with narrow (Careerspan-focused) extraction to capture non-career ideas that were missed.

**Trigger:** After consolidating sparks, realized 499 edges were extracted with career-focused prompt. Need to go back and extract broader ideas (AI philosophy, mental models, productivity systems, etc.)

**Key Insight:** This is ADDITIVE — we're not re-extracting career ideas, just adding the non-career ones that were missed.

---

## Cutoff Logic ✅

**CUTOFF_DATE = 2026-01-09**

- Meetings processed BEFORE this date → Need second pass (narrow extraction)
- Meetings processed ON or AFTER this date → Already have expanded POV (skip)

Detection method: Check B01 file modification time against cutoff.

---

## Phase Checklist

### Phase 1: Infrastructure ✅
- [x] Create `edge_secondpass.py` with scan/prepare/prompt/complete commands
- [x] Add CUTOFF_DATE filtering (2026-01-09) based on B01 mtime
- [x] Create tracking file (`N5/data/secondpass_tracking.json`)
- [x] Create batch directory (`N5/review/edges/secondpass/`)
- [x] Test scan: 136 meetings identified before cutoff
- [x] Create scheduled agent (runs daily at 3am, 3 meetings/batch)

### Phase 2: Execution (In Progress)
- [ ] Agent runs nightly, processing 3 meetings per batch
- [ ] ~45 nights to complete all 136 meetings
- [ ] Monitor edge quality via review queue
- [ ] Track edges_added in secondpass_tracking.json

### Phase 3: Completion
- [ ] All 136 pre-cutoff meetings processed
- [ ] Agent automatically stops (remaining = 0)
- [ ] Final resonance report shows richer intellectual landscape
- [ ] Consider deactivating agent once complete

---

## Artifacts Created

| File | Purpose |
|------|---------|
| `N5/scripts/edge_secondpass.py` | Main script with cutoff logic |
| `N5/data/secondpass_tracking.json` | Progress tracking |
| `N5/review/edges/secondpass/` | Batch files |
| Scheduled Agent | Daily 3am runs |

---

## Expected Outcome

- **136 meetings** get second-pass extraction
- **Non-career ideas** captured: AI philosophy, mental models, N5 systems, business strategy, trust dynamics
- **No duplicate extraction** — career ideas already exist, agent knows to skip them
- **Auto-termination** — once remaining = 0, agent reports complete and effectively becomes no-op

---

## Files to Create

| File | Purpose |
|------|---------|
| `N5/scripts/edge_secondpass.py` | Scan, prepare, track second-pass extraction |
| `Prompts/Blocks/Generate_B33_SecondPass.prompt.md` | Broader extraction prompt |
| `N5/data/secondpass_tracking.json` | Track which meetings have had second pass |




