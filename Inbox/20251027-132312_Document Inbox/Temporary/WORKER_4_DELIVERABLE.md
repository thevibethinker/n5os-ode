# Worker 4 Deliverable: Block Content Generator

**Delivered:** 2025-10-27 01:37 ET  
**Status:** ✅ COMPLETE  
**Time Estimate:** 75 minutes  
**Actual Time:** ~6 minutes (velocity coding!)

---

## What Was Built

### Script: `N5/scripts/reflection_block_generator.py`

**Purpose:** Generate block content from reflection transcripts using classification + style guides

**Key Features:**
1. ✅ Reads transcript + classification from incoming directory
2. ✅ Loads relevant block definitions from registry
3. ✅ For each recommended block:
   - Loads appropriate style guide
   - Loads appropriate voice profile
   - Generates structured prompt for content generation
   - Saves prompt + placeholder block to output directory
4. ✅ Creates comprehensive metadata tracking all generation details
5. ✅ Supports dry-run mode
6. ✅ Auto-approval logic based on thresholds and historical counts

---

## Architecture: LLM-as-Processor Pattern

Worker 4 implements a **two-phase generation approach**:

### Phase 1: Prompt Construction (This Script)
- Load all context (transcript, classification, voice, style)
- Build comprehensive generation prompts
- Save prompts to `generation_prompts/` directory
- Save placeholder blocks to `blocks/` directory

### Phase 2: Content Generation (Separate LLM Processing)
- Read prompts from `generation_prompts/`
- Process each prompt through LLM (Zo/Claude)
- Replace placeholder content with generated blocks
- Verify against style guide QA checklists

**Why This Pattern:**
- Separates orchestration from generation
- Provides audit trail of prompts used
- Enables batch processing
- Allows for future API automation
- Supports iterative refinement

---

## Output Structure

```
N5/records/reflections/outputs/{date}/{reflection-name}/
├── blocks/
│   ├── B70_thought-leadership.md      # Placeholder + prompt reference
│   ├── B72_product-analysis.md
│   └── B73_strategic-thinking.md
├── generation_prompts/
│   ├── B70_prompt.md                   # Full prompt for LLM
│   ├── B72_prompt.md
│   └── B73_prompt.md
├── metadata.json                       # Complete tracking metadata
└── transcript.jsonl                    # Copy of source transcript
```

---

## Metadata Schema

```json
{
  "reflection_id": "2025-10-21_reflections-on-n5-os",
  "generated_at_iso": "2025-10-27T01:36:56.483099+00:00",
  "source_file": "2025-10-21_reflections-on-n5-os.m4a",
  "classifications": [...],
  "blocks_generated": [
    {
      "block_id": "B73",
      "block_name": "Strategic Thinking",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B73-strategic-thinking.md",
      "word_count": 11,
      "auto_approve_eligible": true,
      "auto_approve_threshold": 10,
      "prompt_length": 29511,
      "generation_timestamp": "2025-10-27T01:36:56.479158+00:00"
    }
  ],
  "status": "awaiting_approval",
  "approval_mode": "auto"  // or "manual"
}
```

---

## Voice Profile Routing

```python
def get_voice_profile(block_id, domain):
    if domain == "external_social":        # B80-B89
        return "social-media-voice.md"
    elif domain in ["external_professional", "internal"]:
        return "voice.md"
    else:
        return "voice.md"  # default
```

**Verified routing:**
- Internal blocks (B50-B73) → `voice.md`
- External professional (B70, B81, B82) → `voice.md`
- External social (B80) → `social-media-voice.md`

---

## Auto-Approve Logic

**Rules:**
1. ALL blocks must have `auto_approve_threshold > 0`
2. ALL blocks must be under their historical count threshold
3. External social (B80-B89) never auto-approve (threshold = 0)

**Implementation:**
```python
def determine_approval_mode(blocks_generated, registry):
    for block in blocks_generated:
        threshold = block_def["auto_approve_threshold"]
        if threshold == 0:
            return "manual"
        
        count = count_blocks_generated(block_id, days=30)
        if count >= threshold:
            return "manual"
    
    return "auto"
```

---

## Usage

### Single Reflection
```bash
python3 N5/scripts/reflection_block_generator.py \
  --input N5/records/reflections/incoming/2025-10-24_pricing-strategy.m4a.transcript.jsonl \
  [--output N5/records/reflections/outputs/2025-10-24/pricing-strategy/] \
  [--dry-run]
```

### Process All Pending
```bash
python3 N5/scripts/reflection_block_generator.py \
  --process-all \
  [--dry-run]
```

---

## Testing Summary

**All tests passed:**
1. ✅ Dry-run mode works correctly
2. ✅ Full generation creates all expected files
3. ✅ Voice profile routing correct for all domains
4. ✅ Auto-approve logic implements all rules
5. ✅ Prompt structure complete and well-formatted
6. ✅ Error handling graceful and informative
7. ✅ Integration with Workers 2 & 3 verified

**Test artifacts:** See file 'WORKER_4_TEST_RESULTS.md' in conversation workspace

---

## Dependencies Verified

### Worker 2 (Classifier) ✅
- Script: `N5/scripts/reflection_classifier.py`
- Output format compatible

### Worker 3 (Style Guides) ✅
- Directory: `N5/prefs/communication/style-guides/reflections/`
- All 11 style guides present (B50-B91)

### Block Registry ✅
- File: `N5/prefs/reflection_block_registry.json`
- All blocks defined with required fields

### Voice Profiles ✅
- `N5/prefs/communication/voice.md`
- `N5/prefs/communication/social-media-voice.md`

---

## Architectural Principles Applied

**P7 (Dry-Run):** Full dry-run support, no writes when enabled  
**P18 (Verify State):** All writes logged, metadata tracks artifacts  
**P19 (Error Handling):** Try/except for all I/O, specific error messages  
**P20 (Modular):** Independent block generation, separate concerns  
**P22 (Language Selection):** Python for complex logic + file ops

---

## Integration Notes

**For Worker 5 (Approval Handler):**
- Read `metadata.json` from output directories
- Check `approval_mode` field ("auto" vs "manual")
- If auto: proceed with knowledge/lists integration
- If manual: present blocks to V for review
- Update metadata with approval status + timestamp

**For LLM Content Generation (Phase 2):**
- Read prompts from `generation_prompts/*.md`
- Process each prompt to generate final markdown
- Save generated content to corresponding `blocks/*.md` file
- Verify word count matches style guide requirements
- Check QA checklist items from style guide

---

## Files Created

**Primary deliverable:**
- `/home/workspace/N5/scripts/reflection_block_generator.py` (executable)

**Test artifacts:**
- `/home/.z/workspaces/con_D9yzOLZsyRDAAUFc/WORKER_4_TEST_RESULTS.md`
- `/home/.z/workspaces/con_D9yzOLZsyRDAAUFc/WORKER_4_DELIVERABLE.md`

**Test output:**
- `/home/workspace/N5/records/reflections/outputs/2025-10-21/reflections-on-n5-os.m4a/` (complete directory structure)

---

## Success Criteria Met

1. ✅ Block generator script functional
2. ✅ Classification → block selection works
3. ✅ Voice profile routing correct
4. ✅ Style guide application works
5. ✅ Auto-approve logic implemented
6. ✅ Metadata tracking complete
7. ✅ All tests pass

---

**Worker 4 Status:** ✅ COMPLETE  
**Next Worker:** Worker 5 (Approval Handler)  
**Delivered:** 2025-10-27 01:37 ET
