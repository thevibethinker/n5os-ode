---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---
# Meeting Standardization - IMPLEMENTATION COMPLETE ✅

**Date:** 2025-11-04 12:10 ET  
**Status:** Fully integrated into pipeline  
**Approach:** LLM-based semantic understanding (not mechanical regex)

---

## What Was Built

### 1. Hierarchical Taxonomy ✅
**Location:** `N5/schemas/meeting_taxonomy.yaml`

```
internal/
  - standup, technical, planning, cofounder, general
  
external/
  - coaching, partnership, sales, workshop, discovery
  - ai-consulting, career-advising, general
```

### 2. Standardization Module ✅
**Location:** `N5/scripts/meeting_pipeline/standardize_meeting.py`

**Responsibilities:**
- Add frontmatter to all B*.md files
- Use Zo (LLM) to generate semantic folder names
- Rename folder to standard format
- Log all changes

**Key functions:**
- `standardize_meeting(meeting_id)` - Main entry point
- `add_frontmatter(meeting_folder)` - Add YAML frontmatter
- `generate_standard_name()` - LLM-based naming
- `validate_folder_name()` - Format validation

### 3. Pipeline Integration ✅
**Location:** `N5/scripts/meeting_pipeline/response_handler.py`

**Integration point:** `finalize_meeting()` function  
**Trigger:** After B26_metadata.md generation completes  
**Behavior:** Non-blocking (warnings only, doesn't fail pipeline)

```python
def finalize_meeting(meeting_id, response_data):
    # ... update database ...
    
    # Standardize folder (add frontmatter + rename)
    try:
        standardize_success = standardize_meeting(meeting_id)
        if not standardize_success:
            logger.warning(f"Could not standardize folder")
    except Exception as e:
        logger.warning(f"Standardization error: {e}")
```

### 4. Prompt Documentation ✅
**Location:** `Prompts/standardize_meeting_folder.md`

- Registered as tool (`tool: true`)
- Comprehensive examples (good vs bad)
- Clear extraction rules
- Validation checklist
- Can be invoked: `@standardize_meeting_folder`

---

## Format Specification

### Standard Format
```
YYYY-MM-DD_lead-participant_context_subtype
```

### Field Rules

**1. Date:** ISO 8601 (YYYY-MM-DD)  
**2. Lead Participant:**
- External: Actual company/person name (e.g., `greenlight`, `alex-caveny`)
- Internal: Descriptor (e.g., `team`, `cofounder`)
- ❌ NEVER CRM codes (`ld-net`, `gpt-exp`)

**3. Context:** 2-4 words describing meeting essence
- Semantic, not mechanical
- No truncation
- Examples: `recruiting-discovery`, `founder-burnout`

**4. Subtype:** Pick from taxonomy
- Must match one of 13 defined subtypes

---

## How It Works

### Automatic (Pipeline)
1. Meeting intelligence generates → B01, B02, ..., B26
2. Response handler completes → Calls `standardize_meeting()`
3. Standardization:
   - Adds frontmatter to all B*.md files
   - Calls Zo CLI with B26 content + prompt
   - Zo returns semantic folder name
   - Validates format
   - Renames folder
   - Logs to `rename_log.jsonl`

### Manual (Single Meeting)
```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/standardize_meeting.py <meeting_id>
```

### Via Prompt
```
@standardize_meeting_folder <meeting-folder-path>
```

---

## Testing Results

### Initial Test (5 meetings):
```
✅ 2025-08-27_community-partner_referral-networks_partnership
✅ 2025-09-02_aniket_recruiting-collab_partnership
✅ 2025-09-12_greenlight_recruiting-discovery_sales
✅ 2025-09-12_greenlight_talent-screening_sales
✅ 2025-10-09_alex-caveny_founder-burnout_coaching
```

**Result:** Clean, semantic, greppable names  
**Method:** LLM-based (not regex)

---

## Key Design Decisions

### Why LLM-based? (Not regex)
1. **Semantic understanding** - Reads and comprehends meeting content
2. **Actual names** - Extracts real participants, not CRM codes
3. **Context extraction** - Picks meaningful themes, not mechanical text
4. **Flexible** - Adapts to B26 format variations
5. **Maintainable** - Prompt can be refined without code changes

### Why Non-blocking Integration?
- Pipeline continues even if standardization fails
- Old/missing B26 files don't break processing
- Can be retrofitted to old meetings later

### Why Frontmatter?
- Version tracking
- Machine-readable metadata
- grep-friendly (can search by version, date, block_id)
- Foundation for future enhancements

---

## Files Changed/Created

### New Files:
1. `N5/schemas/meeting_taxonomy.yaml` - Hierarchical taxonomy
2. `N5/scripts/meeting_pipeline/standardize_meeting.py` - Core module
3. `Prompts/standardize_meeting_folder.md` - Documentation/prompt

### Modified Files:
1. `N5/scripts/meeting_pipeline/response_handler.py` - Added integration

### Log Files:
1. `Personal/Meetings/rename_log.jsonl` - Tracks all renames

---

## Benefits

### For Grepping:
```bash
# All sales meetings
ls -d Personal/Meetings/*_sales

# All Alex Caveny sessions
ls -d Personal/Meetings/*alex-caveny*

# September 2025 meetings
ls -d Personal/Meetings/2025-09-*

# All partnerships
ls -d Personal/Meetings/*_partnership
```

### For Organization:
- Chronological (date-first)
- Categorized (subtype suffix)
- Searchable (semantic names)
- Scannable (human-readable)

### For Automation:
- Standard frontmatter enables batch operations
- Version tracking supports migrations
- Taxonomy supports analytics

---

## Next Steps

### Phase 2 (Optional):
1. **Regenerate old B26s** - Update 16 meetings with old format
2. **Re-run standardization** - Apply to newly updated meetings
3. **Analytics dashboard** - Visualize meeting distribution by type/subtype

### Monitoring:
- Check `rename_log.jsonl` for patterns
- Review any warnings in pipeline logs
- Verify new meetings get standardized automatically

---

## Rollback Plan

If issues arise:

1. **Disable:** Comment out standardization call in `response_handler.py`
2. **Revert names:** Use `rename_log.jsonl` to reverse renames:
```bash
cat Personal/Meetings/rename_log.jsonl | jq -r '[.new, .old] | @tsv' | while read new old; do
  mv "Personal/Meetings/$new" "Personal/Meetings/$old"
done
```
3. **Remove frontmatter:** Script to strip frontmatter if needed

---

**✅ SYSTEM READY FOR PRODUCTION**

All new meetings will be automatically standardized after B26 generation.
Zero disruption to existing pipeline.
LLM-based semantic naming ensures quality.
