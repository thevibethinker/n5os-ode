# Complete Meeting Processing Chain Analysis

**Date:** 2025-11-17  
**Purpose:** Debug entire meeting lifecycle from webhook to archive

---

## The Complete Chain

```
FIREFLIES WEBHOOK
    ↓
TRANSCRIPT PROCESSOR (fireflies-poller service)
    ↓
RAW FOLDER (no suffix)
    ↓
MG-1: MANIFEST GENERATOR (hourly)
    ↓
[M] FOLDER (manifest created)
    ↓
MG-2: BLOCK GENERATOR (every 30min)
    ↓
[M] → [P] (all blocks complete)
    ↓
MG-5: FOLLOW-UP EMAIL (every 30min, optional)
    ↓
[P] FOLDER (ready for archive)
    ↓
MG-7: ARCHIVE (4x daily at 1, 13, 17, 21)
    ↓
ARCHIVED (in Archive/YYYY-QX/)
```

---

## Step-by-Step Analysis

### STEP 1: Fireflies Webhook → Raw Folder

**Service:** `fireflies-poller` (port 8421)  
**Frequency:** Every 2 minutes  
**Code:** `N5/services/fireflies_webhook/transcript_processor.py`

**Process:**
1. Poll `fireflies_webhooks` table for `status='pending'`
2. Fetch transcript from Fireflies API
3. Create folder: `YYYY-MM-DD_participant-names`
4. Save: `transcript.jsonl`, `metadata.json`
5. Mark webhook as `processed`

**Folder State:** Raw (no suffix)

**Potential Issues:**
- [ ] Duplicate webhook delivery?
- [ ] Folder naming collisions?
- [ ] Missing transcript data?

---

### STEP 2: Raw Folder → [M] Folder (Manifest Generation)

**Task:** MG-1 (ID: 3ae08209-5c17-405a-bdfd-bd997d38d649)  
**Frequency:** Hourly at 0, 15, 16, 17, 18, 19, 20, 21, 22, 23  
**Prompt:** `Prompts/meeting-block-selector.prompt.md`

**Process:**
1. Find folders: No suffix, no manifest.json, has transcript.md
2. Load transcript
3. Analyze and select blocks (mandatory + semantic)
4. Generate manifest.json
5. **RENAME:** `mv "$folder" "${folder}_[M]"`

**Folder State:** [M] (manifest ready for block generation)

**Potential Issues:**
- [x] FIXED: Was creating new folders instead of renaming
- [ ] Block selection logic correct?
- [ ] Idempotency check working?

---

### STEP 3: [M] Folder → Block Generation

**Task:** MG-2 (Meeting Intelligence Block Generation)  
**Frequency:** Every 30 minutes  
**Prompt:** `Prompts/meeting-block-generator.prompt.md`

**Process:**
1. Find folders with `_[M]` suffix
2. Check manifest for `status="pending"` blocks
3. Generate ONE block per run
4. Update manifest with `status="completed"`
5. If all complete: Rename [M] → [P]

**Folder State:** 
- Stays [M] while blocks generating
- Becomes [P] when all complete

**Potential Issues:**
- [x] FIXED: Bash escaping bug in rename command
- [ ] Block generation quality?
- [ ] Handles missing/incomplete blocks?

---

### STEP 4: [P] Folder → Communications (Optional)

**Task:** MG-5 (Follow-Up Email Generation)  
**Frequency:** Every 30 minutes  
**Prompt:** TBD

**Process:**
1. Find folders with `_[P]` suffix
2. Check if follow-up email needed
3. Generate FOLLOW_UP_EMAIL.md
4. Folder stays [P]

**Folder State:** [P] (ready for archive)

**Potential Issues:**
- [ ] When does it run?
- [ ] Multiple emails generated?

---

### STEP 5: [P] Folder → Archive

**Task:** MG-7 (Meeting Archive Automation)  
**Frequency:** 4x daily at 1:00, 13:00, 17:00, 21:00 UTC  
**Code:** `N5/scripts/meeting_pipeline/archive_completed_meetings.py`

**Process:**
1. Find folders with `_[P]` suffix
2. Determine quarter (Q1-Q4) from date
3. Remove `_[P]` suffix from folder name
4. **MOVE:** to `Archive/YYYY-QX/meeting-name/`
5. Log action

**Folder State:** Archived (no suffix)

**Potential Issues:**
- [ ] Suffix removal only handles _[P], not _[M]?
- [ ] Quarter calculation correct?
- [ ] Handles missing Archive dirs?

---

## Current Known Issues

### ✅ FIXED
1. **MG-1 Duplication:** Creating new folders instead of renaming
2. **Bash Escaping:** [M] not escaped in parameter expansion

### ⚠️ TO INVESTIGATE
1. **Archive suffix logic:** Only removes `_[P]`, what about `_[M]`?
2. **Block generator frequency:** Is 30min optimal?
3. **Idempotency:** Are all steps truly idempotent?
4. **Error handling:** What happens on failures?
5. **State recovery:** Can chain resume after crash?

---

## Testing Plan

1. **End-to-end test:** Create mock raw folder, watch full chain
2. **State validation:** Verify each transition correct
3. **Error injection:** Test failure scenarios
4. **Race conditions:** Check concurrent processing
5. **Idempotency:** Run tasks multiple times on same folder

---

**Next Steps:** Systematic investigation of each component

