---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---
# Meeting Standardization - Ready to Execute

**Status:** Built and tested, ready for V approval  
**Date:** 2025-11-04 11:48 ET

---

## What Was Built

### ✅ Complete System
1. **Taxonomy schema** - Hierarchical (internal/external + subtypes)
2. **Inference engine** - Reads B26 Stakeholder Classification
3. **Frontmatter generator** - Adds version/type/date metadata to all B*.md files
4. **Folder renamer** - Atomic, logged, reversible
5. **Bulk processor** - Handles all meetings with dry-run

### New Taxonomy (Approved by V)

**External subtypes:**
- coaching
- partnership
- sales
- workshop
- discovery
- ai-consulting ← NEW
- career-advising ← NEW
- general

**Internal subtypes:**
- standup
- technical
- planning
- cofounder
- general

### Folder Naming Format (Option B - Approved)
```
YYYY-MM-DD_lead-participant_context_subtype
```

**Examples from dry-run:**
```
2025-09-12_greenlight_talent-quality-filte_sales
2025-10-09_advisorycoaching_founder-burnout-reco_coaching
2025-09-02_ld-net_gpt-exp-go-to-market_partnership
```

### Frontmatter Added to All B*.md Files
```yaml
---
processing_version: 2.0
meeting_date: 2025-09-12
meeting_type: external
meeting_subtype: sales
created: 2025-11-04
last_edited: 2025-11-04
---
```

---

## Current State

**Total meeting folders:** 21

**Ready to standardize (NEW B26 format):** 5
- 2025-08-27_unknown_external
- 2025-09-12_greenlight-allie-paul_external  
- 2025-09-12_unknown_external
- 2025-10-09_Alex-Caveny_advisory-coaching
- Aniket x Vrijen Attawar-transcript-2025-09-02T16-59-20.052Z

**Will skip (old B26 format or missing):** 16
- These will be handled when their B26 files are regenerated with new format

---

## Safety Features

✅ **Atomic operations** - Each folder processed independently  
✅ **Dry-run tested** - Full preview before execution  
✅ **Collision detection** - Won't overwrite existing folders  
✅ **Complete logging** - All renames logged to rename_log.jsonl  
✅ **Reversible** - Log contains old→new mapping for rollback  
✅ **Old format protection** - Won't touch meetings without new B26 format

---

## Next Steps

**Option 1: Execute on 5 ready meetings**
```bash
python3 /home/workspace/N5/scripts/standardize_all_meetings.py --execute
```

**Option 2: Test on single meeting first**
```bash
# Add frontmatter
python3 /home/workspace/N5/scripts/add_frontmatter_to_meeting.py \
  "/home/workspace/Personal/Meetings/2025-09-12_greenlight-allie-paul_external"

# Rename folder
python3 /home/workspace/N5/scripts/rename_meeting_folder.py \
  "/home/workspace/Personal/Meetings/2025-09-12_greenlight-allie-paul_external"
```

---

## Integration with Pipeline

**After this works:** Add to meeting intelligence workflow
- Hook: After B26 generation completes
- Actions:
  1. Infer taxonomy from new B26
  2. Add frontmatter to all B*.md files
  3. Rename folder to standard format
  4. Log rename for tracking

**Location:** `N5/services/meeting-intelligence/finalize_meeting.py`

---

**READY TO EXECUTE**
