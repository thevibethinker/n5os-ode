---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---
# Meeting Folder Naming Standard - SPECIFICATION

**Status:** Ready for Implementation  
**Authority:** V approved trap door decision

---

## Problem Statement

Meeting folders have inconsistent naming:
- Mix of formats: date-first, name-first, transcript IDs, timestamps
- Hard to grep systematically
- Not human-readable at glance
- No consistent structure for filtering

**Current mess:**
```
Alex_x_Vrijen_-_Wisdom_Partners_Coaching-transcript-2025-10-29T17-58-28.439Z/
bdr-rjwf-ehc-transcript-2025-11-03T08-34-24.986Z/
2025-09-12_greenlight-allie-paul_external/
Vs_Zo_pitch_GRANOLA/
AI Agent MBA 101 (What businesses will look like with A-transcript-2025-09-04T17-25-02.164Z/
```

---

## Solution: Standardized 4-Field Format

### Format
```
YYYY-MM-DD_participants_context_category
```

### Field Specifications

**1. Date (YYYY-MM-DD)**
- ISO 8601 format
- Enables chronological sorting
- Extracted from: B26_metadata.md `date` field or folder name

**2. Participants (lowercase-hyphenated)**
- Key people or organization names
- Max 2-3 participants for clarity
- Internal: first names (alex-vrijen)
- External: first-last or company (allie-cialeo, greenlight-fund)
- Extracted from: B26_metadata.md `participants` or meeting title

**3. Context (1-3-words-lowercase-hyphenated)**
- Brief meeting purpose/topic
- Examples: wisdom-partners, acquisition-strategy, user-research
- Extracted from: Meeting title or B15_insights.md summary

**4. Category (single-word-lowercase)**
- Standardized taxonomy:
  - `internal` - Team meetings, standups, planning
  - `external` - Customer, partner, prospect meetings
  - `coaching` - 1-1 coaching sessions
  - `sales` - Sales calls, discovery, demos
  - `partnership` - Partnership discussions
  - `workshop` - Group learning, training
  - `standup` - Daily team standups
  - `advisory` - Board/advisor meetings
  - `research` - User research, interviews
- Extracted from: B26_metadata.md `meeting_type` or inferred

### Examples

**Before → After:**
```
Alex_x_Vrijen_-_Wisdom_Partners_Coaching-transcript-2025-10-29T17-58-28.439Z/
  → 2025-10-29_alex-vrijen_wisdom-partners_coaching/

bdr-rjwf-ehc-transcript-2025-11-03T08-34-24.986Z/
  → 2025-11-03_sunday-morning-standup_internal/

2025-09-12_greenlight-allie-paul_external/
  → 2025-09-12_allie-paul_greenlight-intro_external/

Vs_Zo_pitch_GRANOLA/
  → 2025-[DATE]_v-pitch_zo-demo_sales/

AI Agent MBA 101 (What businesses will look like with A-transcript-2025-09-04T17-25-02.164Z/
  → 2025-09-04_ai-agent-mba_workshop_external/
```

---

## Implementation Design

### Phase 1: Renaming Script
**File:** `N5/scripts/meeting_renamer.py`

**Logic:**
1. Scan `/home/workspace/Personal/Meetings/` for folders with meetings
2. For each folder:
   - Read `B26_metadata.md` if exists
   - Extract: date, participants, context
   - Infer category from meeting_type or participants
   - Generate new name using format
   - Validate new name (no conflicts, valid chars)
   - Prompt confirmation if ambiguous
3. Rename folder
4. Log all changes to `RENAME_LOG.jsonl`

**Dry-run mode:** Default behavior shows proposed renames, requires `--execute` flag

**Safety:**
- Never overwrites existing folder
- Auto-versions on conflict (`_v2`, `_v3`)
- Logs original → new mapping
- Preserves all folder contents

### Phase 2: Integration with Pipeline
**Hook:** After B26_metadata.md generation

**Location:** `N5/services/meeting-intelligence/generate_intelligence.py`

**Logic:**
- After metadata generated successfully
- Extract naming fields from metadata
- Generate standardized folder name
- If different from current name:
  - Rename folder atomically
  - Update any references (conversation workspace, logs)
  - Log rename event

### Phase 3: Backfill Existing Folders
**Command:** `python3 N5/scripts/meeting_renamer.py --backfill --dry-run`

**Process:**
1. Scan all existing meeting folders
2. Generate proposed names
3. Show V for review (dry-run output)
4. V confirms: `--execute`
5. Batch rename with progress tracking

---

## Success Criteria

✅ All meeting folders follow YYYY-MM-DD_participants_context_category format
✅ Script runs in dry-run mode by default (no accidental renames)
✅ New meetings auto-rename after metadata generation
✅ Can grep by date: `ls -d 2025-11-*`
✅ Can grep by participant: `ls -d *alex-vrijen*`
✅ Can grep by category: `ls -d *_coaching/`
✅ Human-readable at glance
✅ No timestamp cruft in folder names
✅ Zero collision/conflict errors
✅ Complete rename log for auditing

---

## Edge Cases

**No metadata file:**
- Fall back to parsing existing folder name
- Extract date from transcript ID or folder name
- Prompt for missing fields if unclear

**Ambiguous participants:**
- Max 3 participants in name
- If >3, use primary + "team" (e.g., `vrijen-team`)
- Or use organization name (e.g., `greenlight-team`)

**Name collision:**
- Auto-append `_v2`, `_v3` etc.
- Log collision for V review

**Special characters:**
- Strip or convert: spaces→hyphens, parentheses→remove
- Allow: letters, numbers, hyphens, underscores
- Lowercase everything

**Unknown category:**
- Default to `external` if has external participants
- Default to `internal` if all internal
- Prompt V if truly ambiguous

---

## Grep Examples (Post-Implementation)

```bash
# All meetings in November 2025
ls -d /home/workspace/Personal/Meetings/2025-11-*

# All coaching sessions
ls -d /home/workspace/Personal/Meetings/*_coaching/

# All meetings with Alex
ls -d /home/workspace/Personal/Meetings/*alex*

# All external meetings
ls -d /home/workspace/Personal/Meetings/*_external/

# Meetings in date range
ls -d /home/workspace/Personal/Meetings/2025-10-{20..31}*

# Sales meetings in October
ls -d /home/workspace/Personal/Meetings/2025-10-*_sales/
```

---

## Non-Goals

❌ Renaming files within folders (only folder names)
❌ Changing meeting intelligence filenames (B01, B02, etc.)
❌ Modifying transcript filenames in Inbox
❌ Retroactive categorization (use existing metadata/context)

---

## Implementation Priority

1. **Phase 1:** Build renaming script with dry-run (2-3 hours)
2. **Phase 2:** Test on 5-10 folders manually (30 min)
3. **Phase 3:** Backfill all existing folders (1 hour)
4. **Phase 4:** Integrate into pipeline (1 hour)

**Total estimate:** 4-5 hours end-to-end

---

## Trap Door Decision: Approved

**Decision:** Use `YYYY-MM-DD_participants_context_category` format
**Rationale:** 
- Chronological sort
- Greppable by all dimensions
- Human readable
- Simple (4 fields, consistent delimiters)
- Metadata contains all needed info

**Risk:** Mass rename of ~20-30 existing folders
**Mitigation:** Dry-run review, complete audit log, atomic renames

**Approved by:** V (2025-11-04)

---

**READY TO BUILD**
