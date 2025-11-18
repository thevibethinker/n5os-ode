---
created: 2025-11-16
last_edited: 2025-11-16
version: 2
---
# Meeting Intelligence Communications Architecture v2

**Updated:** 2025-11-16 14:08 EST  
**Replaces:** Original unified block system  
**Key Change:** Separation of intelligence extraction from communications generation

---

## Architecture Overview

### The Split

**Problem:** B14 and B25 were doing two incompatible jobs:
- **Intelligence extraction** (meeting-specific facts) 
- **Communications generation** (Careerspan-aware messaging)

**Solution:** Two separate pipelines with different models and context.

```
MEETING TRANSCRIPT
       ↓
┌──────────────────────────────────────┐
│  PIPELINE 1: INTELLIGENCE            │
│  Model: Standard (efficient)         │
│  Context: Transcript only            │
│  Output: B01-B31 blocks              │
│  State: [M] → [P]                    │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  PIPELINE 2: COMMUNICATIONS          │
│  Model: Powerful (Opus/GPT-4/o1)     │
│  Context: Transcript + Blocks +      │
│           Knowledge/current/         │
│  Output: Emails + Blurbs             │
│  State: [P] → [R]                    │
└──────────────────────────────────────┘
       ↓
  READY FOR DEPLOYMENT
```

---

## Pipeline 1: Intelligence Extraction

### What Changed

**B14 (BLURBS_REQUESTED) - Simplified:**
- **Purpose:** Track what blurbs were requested (intelligence only)
- **Format:** Simple list/table
- **Length:** 100-200 words
- **NO blurb generation** (moved to Pipeline 2)

**B25 (DELIVERABLE_CONTENT_MAP) - Simplified:**
- **Purpose:** Map promised resources/deliverables
- **Format:** Simple table (Item | Promised By | Due | Status)
- **Length:** 100-200 words
- **NO email generation** (moved to Pipeline 2)

### Process Flow

1. Meeting folder created with transcript
2. Block selector runs → generates manifest.json → `[M]` state
3. Block generator runs → generates all B01-B31 blocks → `[P]` state
4. **Trigger Pipeline 2** if B14 or B25 exists

### Unchanged Blocks

All other blocks (B01, B02, B08, B21, B26, B27, B31, etc.) remain exactly as they were. They operate on transcript-only context and generate meeting intelligence.

---

## Pipeline 2: Communications Generation

### New Agent: Communications Generator

**Trigger:**
- Folder reaches `[P]` state (all intelligence blocks complete)
- AND (B14 exists OR B25 exists)

**Context Loaded:**
1. Full meeting transcript
2. B14 (if exists) - what blurbs were requested
3. B25 (if exists) - what deliverables were promised
4. **Knowledge/current/** - all documents in this folder
5. B08 (stakeholder intelligence) - for personalization

**Model:**
- **Recommended:** Claude Opus (best for nuanced communications)
- **Alternative:** GPT-4 or o1-preview
- **Why powerful:** Needs to balance Careerspan context, stakeholder resonance, V's voice

**Outputs Generated:**

**1. FOLLOW_UP_EMAIL.md** (if B25 exists)
- Send-ready follow-up email draft
- Incorporates:
  - Deliverables from B25
  - Stakeholder resonance from B08
  - Current Careerspan positioning from Knowledge/current/
  - V's communication style
  - v11 email system (Flesch-Kincaid, warmth dials, etc.)

**2. BLURBS_GENERATED.md** (if B14 exists)
- All requested blurbs/descriptions/one-pagers
- Copy-paste ready
- Incorporates:
  - What was requested (from B14)
  - Who requested it and why
  - Current Careerspan positioning from Knowledge/current/
  - Appropriate format/length for each request

**State Transition:**
- After successful generation: `[P]` → `[R]` (Ready for deployment)
- Folder is now ready to move to final destination

---

## Knowledge/current/ Folder

### Purpose

Single source of truth for communications context. V manually maintains this with the most up-to-date Careerspan information.

### What Lives Here

- Current positioning documents
- Recent value props
- Active initiatives
- Recent wins/traction
- Messaging guidelines
- Template examples (successful emails/blurbs)

### Why This Works

**Before:** Communications generator had to search entire Knowledge folder (overwhelming, may miss key context).

**After:** Communications generator ALWAYS loads Knowledge/current/ (guaranteed up-to-date, V controls exactly what's referenced).

### Usage

V drops any document here that should inform outbound communications. No organization needed - just dump relevant docs here.

---

## State Machine

### Updated Folder States

```
[no suffix] → Raw meeting (transcript only)
     ↓
    [M] → Manifest created, blocks selected
     ↓
    [P] → Processing complete (all intelligence blocks done)
     ↓
    [R] → Ready for deployment (communications generated, if applicable)
     ↓
  (Move to final destination)
```

### State Definitions

- **[no suffix]:** Raw transcript, awaiting block selection
- **[M]:** Manifest exists, intelligence blocks being generated
- **[P]:** All intelligence complete, may need communications
- **[R]:** All communications complete (or none needed), ready to file

### Transition Logic

**[no suffix] → [M]:**
- Block selector analyzes transcript
- Generates manifest.json
- Renames folder

**[M] → [P]:**
- All blocks in manifest generated
- Validates all blocks present
- Renames folder
- **Checks:** Does B14 or B25 exist?
  - If YES: Trigger communications generator
  - If NO: Move directly to [R]

**[P] → [R]:**
- Communications generator completes (if triggered)
- Generates FOLLOW_UP_EMAIL.md and/or BLURBS_GENERATED.md
- Renames folder
- Ready for final filing

**[R] → Final:**
- Move to Inbox or final destination
- System complete

---

## Implementation Files

### New Files Created

1. **`file 'Knowledge/current/README.md'`**
   - Documentation for context folder
   - Usage guidelines

2. **`file 'Documents/B14-Definition-v2.md'`**
   - Simplified B14 (intelligence-only)
   - To replace existing B14 guidance

3. **`file 'Documents/B25-Definition-v2.md'`**
   - Simplified B25 (intelligence-only)
   - To replace existing B25 guidance

4. **`file 'Prompts/communications-generator.prompt.md'`**
   - New dedicated agent for Pipeline 2
   - Generates emails and blurbs

5. **`file 'Documents/Communications-Architecture-v2.md'`** (this file)
   - Architecture documentation
   - Reference for system design

### Files To Update (Next Step)

1. **`file 'N5/prefs/block_type_registry.json'`**
   - Replace B14 guidance with v2
   - Replace B25 guidance with v2

2. **`file 'Prompts/meeting-block-generator.prompt.md'`**
   - Update to use new B14/B25 definitions
   - Add [P] → communications trigger logic

3. **`file 'N5/scripts/meeting_state_manager.py'`** (if exists)
   - Add [R] state support
   - Add communications trigger logic

---

## Comparison: Before vs After

### B14 (BLURBS_REQUESTED)

**Before:**
- Track what was requested (intelligence)
- Generate actual blurbs (communications)
- Context: Transcript only
- Output: 150-300 words mixed purpose

**After:**
- Track what was requested (intelligence only)
- Context: Transcript only
- Output: 100-200 words, simple list
- **Blurb generation** → Communications Generator with Knowledge/current/

### B25 (DELIVERABLE_CONTENT_MAP)

**Before:**
- Track deliverables promised (intelligence)
- Generate follow-up email draft (communications)
- Context: Transcript only
- Output: 300-700 words mixed purpose

**After:**
- Track deliverables promised (intelligence only)
- Context: Transcript only
- Output: 100-200 words, simple table
- **Email generation** → Communications Generator with Knowledge/current/

### Why This Is Better

**1. Separation of Concerns:**
- Intelligence = extract meeting facts (fast, efficient model)
- Communications = craft messaging (powerful model, rich context)

**2. Right Context for Right Job:**
- Intelligence blocks don't need Careerspan positioning
- Communications NEED Careerspan positioning
- No context pollution

**3. Model Economics:**
- Don't load Knowledge/current/ for 19 intelligence blocks
- Only load for 2 communications artifacts
- More efficient token usage

**4. Quality Improvement:**
- Communications get dedicated attention
- Full Careerspan context available
- No competing priorities

---

## Next Steps

### Phase 1: Foundation (Immediate)
- [x] Create Knowledge/current/ folder
- [x] Create architecture documentation
- [ ] Create B14 v2 definition
- [ ] Create B25 v2 definition
- [ ] Create communications-generator.prompt.md

### Phase 2: Integration (Next Session)
- [ ] Update block_type_registry.json with v2 definitions
- [ ] Update meeting-block-generator.prompt.md
- [ ] Add [R] state support to state management
- [ ] Create communications trigger logic

### Phase 3: Testing (After Integration)
- [ ] Test on 2-3 recent meetings
- [ ] Validate B14 v2 output (intelligence-only)
- [ ] Validate B25 v2 output (intelligence-only)
- [ ] Validate communications generator output
- [ ] Validate [P] → [R] state transitions

### Phase 4: Production (After Testing)
- [ ] Migrate all [P] folders to new system
- [ ] Document for scheduled agent
- [ ] Update any manual workflows

---

## Questions Answered

**Q: Should B27 (KEY_MESSAGING) move to communications pipeline?**  
**A:** No. B27 generates strategic talking points FROM the meeting (intelligence extraction). It doesn't generate outbound communications. Stays in Pipeline 1.

**Q: What if communications generation fails?**  
**A:** Folder stays in [P] state. Retry logic attempts 3x. After 3 failures, flag for manual review but don't block intelligence availability.

**Q: Can folder move to [R] without communications?**  
**A:** Yes. If B14 and B25 don't exist, folder moves directly from [P] to [R]. Communications pipeline is optional.

**Q: What if V wants to regenerate communications?**  
**A:** Delete FOLLOW_UP_EMAIL.md and/or BLURBS_GENERATED.md, then manually trigger communications generator. Or: revert folder from [R] to [P] state to trigger automatic regeneration.

---

**This is conversation con_MMUy9beXziOyCQC5**

*Generated: 2025-11-16 14:08 EST*

