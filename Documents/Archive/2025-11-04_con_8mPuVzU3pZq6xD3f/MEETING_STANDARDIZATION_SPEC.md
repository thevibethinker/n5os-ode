---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---
# Meeting Standardization - Complete Specification

**Status:** Ready for Review  
**Requirements:** V approved (2025-11-04)

---

## Problem Statement

Two interrelated issues:
1. **Inconsistent folder names** - Mix of formats, hard to grep, not readable
2. **No frontmatter in intelligence files** - Can't track versions, grep by fields, or query metadata programmatically

---

## Solution Design

### Part A: Frontmatter Standard

**Schema:**
```yaml
---
processing_version: 1.0
meeting_date: YYYY-MM-DD
meeting_type: [category]
lead_participant: [name or org]
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
---
```

**Applied to:** All B*.md files (B01, B02, B05, B15, B21, B25, B26, B28, etc.)

**Fields:**
- `processing_version`: Pipeline version that generated this file (semantic versioning)
- `meeting_date`: ISO 8601 date of actual meeting
- `meeting_type`: Category from controlled vocabulary (see below)
- `lead_participant`: Primary external party or "internal" for team meetings
- `created`: Date file was first generated
- `last_edited`: Date file was last modified

**Benefits:**
- Grep by date: `grep "meeting_date: 2025-11" *.md`
- Grep by type: `grep "meeting_type: coaching" *.md`
- Track pipeline versions for debugging
- Metadata queries without parsing full files

### Part B: Folder Naming Standard

**Format:**
```
YYYY-MM-DD_TYPE_participant-or-org
```

**Rules:**
- **Date:** ISO 8601 (`YYYY-MM-DD`)
- **Type:** Single word from controlled vocabulary (lowercase)
- **Participant:** Primary person (firstname-lastname) or organization (lowercase, hyphenated)
- **Delimiters:** Underscore between major fields, hyphen within fields

**Examples:**
```
2025-10-29_coaching_alex-wisdom
2025-11-03_internal_standup
2025-09-12_external_allie-greenlight
2025-11-03_technical_nafisa-n5os-install
2025-09-08_partnership_affiliates-lenders
2025-08-29_sales_tim-he
```

**Benefits:**
- Chronological sort by default
- Grep by type: `ls *_coaching_*`
- Grep by participant: `ls *_alex-*`
- Human readable at a glance
- Machine parseable (predictable structure)

### Part C: Meeting Type Taxonomy

**Controlled Vocabulary:**

Based on analysis of existing meetings:

```
internal      - Team standups, co-founder sync, internal planning
external      - Generic external meetings, intro calls
coaching      - Wisdom Partners, advisory sessions
partnership   - Lender affiliates, business partnerships
sales         - Sales calls, customer meetings
technical     - Implementation sessions, debugging, pair programming
workshop      - Group learning sessions, MBA workshops
```

**Decision Logic:**
1. If all participants are Careerspan team → `internal`
2. If coaching relationship → `coaching`
3. If business partnership discussion → `partnership`
4. If sales/customer → `sales`
5. If technical work session → `technical`
6. If group learning → `workshop`
7. Else → `external`

---

## Implementation Plan

### Phase 1: Frontmatter Retrofitting (Non-Breaking)

**Script:** `add_frontmatter_to_meetings.py`

**Logic:**
1. Scan all meeting folders for B*.md files
2. Check if frontmatter already exists (idempotent)
3. Read B26_metadata.md to extract:
   - meeting_date (from date field)
   - meeting_type (infer from classification/type fields)
   - lead_participant (from participants section)
4. Add frontmatter to top of each file
5. Set created = current date, last_edited = current date

**Safety:**
- Dry-run mode (show what would be added)
- Test on 3 folders first
- Full backup before mass operation
- Idempotent (can run multiple times safely)
- Rollback script (strips frontmatter)

**Test folders:**
```
bdr-rjwf-ehc-transcript-2025-11-03T08-34-24.986Z
2025-09-08_alex-caveny-wisdom-partners_coaching
Daily_team_stand-up-transcript-2025-10-29T14-38-58.996Z
```

### Phase 2: Folder Renaming (Atomic, Reversible)

**Script:** `rename_meeting_folders.py`

**Logic:**
1. Scan all meeting folders
2. For each folder with B26_metadata.md:
   - Extract meeting_date
   - Infer meeting_type (using taxonomy logic)
   - Extract lead_participant
   - Generate new name: `{date}_{type}_{participant}`
3. Show dry-run mapping (old → new)
4. On approval, execute renames atomically
5. Log all renames to rename_log.json for rollback

**Safety:**
- Dry-run mode with full mapping shown
- Test on 3 folders first
- Rename log created for reversal
- Check for name collisions before proceeding
- Skip folders already matching pattern

**Collision handling:**
If two meetings same date/type/participant, append numeric suffix:
```
2025-11-03_coaching_alex-wisdom
2025-11-03_coaching_alex-wisdom-02
```

### Phase 3: Pipeline Integration

**Location:** `N5/services/meeting-intelligence/`

**Changes:**
1. Modify block generator to include frontmatter in template
2. Extract metadata fields from B26 generation context
3. Set processing_version from config
4. Generate frontmatter for all blocks

**Hook for renaming:**
Add final step to meeting processing pipeline:
```python
# After B26_metadata.md complete
rename_folder_to_standard(meeting_folder, metadata)
```

**Backwards compatible:**
- Works with or without frontmatter
- Doesn't break if folder already renamed
- Graceful degradation if metadata incomplete

---

## Testing Strategy

### Phase 1 Testing:
1. **Dry-run on 3 folders** - Verify frontmatter format, field population
2. **Execute on 3 folders** - Verify files still readable, no corruption
3. **Grep tests** - Verify greppability of frontmatter fields
4. **Full rollout** - Apply to all meeting folders
5. **Validation** - Check random sample for correctness

### Phase 2 Testing:
1. **Dry-run on all folders** - Review mapping, check for collisions
2. **Execute on 3 folders** - Verify rename successful, contents intact
3. **Grep tests** - Verify new names are greppable as expected
4. **Full rollout** - Rename all folders
5. **Validation** - Verify no broken references, files accessible

### Phase 3 Testing:
1. **Test new meeting processing** - Verify frontmatter generated
2. **Test folder auto-rename** - Verify new meetings get standard names
3. **End-to-end test** - Process meeting from Inbox → final folder
4. **Backwards compat** - Verify old meetings still work

---

## Rollback Procedures

### Phase 1 Rollback:
```bash
python3 remove_frontmatter.py --all
```
Strips YAML frontmatter from all B*.md files using rename log.

### Phase 2 Rollback:
```bash
python3 rename_meeting_folders.py --rollback rename_log.json
```
Reverses all renames using stored mapping.

### Phase 3 Rollback:
Git revert pipeline changes, restart service.

---

## Maintenance

### Adding New Meeting Types:
1. Add to taxonomy list in this document
2. Update inference logic in scripts
3. Update pipeline config
4. Document decision criteria

### Versioning:
- Increment `processing_version` when pipeline changes significantly
- Allows filtering meetings by generation method
- Helps debug issues in older processed meetings

---

## Examples: Before → After

### Folder Names:
```
Before: Alex x Vrijen - Wisdom Partners Coaching-transcript-2025-08-27T18-03-03.024Z
After:  2025-08-27_coaching_alex-wisdom

Before: Acquisition War Room-transcript-2025-11-03T19-48-05.399Z
After:  2025-11-03_internal_acquisition-war-room

Before: bdr-rjwf-ehc-transcript-2025-11-03T08-34-24.986Z
After:  2025-11-03_technical_nafisa-n5os-install

Before: Daily_team_stand-up-transcript-2025-10-29T14-38-58.996Z
After:  2025-10-29_internal_standup
```

### Frontmatter Example:
```markdown
---
processing_version: 1.0
meeting_date: 2025-11-03
meeting_type: technical
lead_participant: nafisa
created: 2025-11-04
last_edited: 2025-11-04
---
# Meeting Metadata and Context

## Basic Information
[rest of file...]
```

---

## Trap Door Decision

**Format Commitment:**
- Folder: `YYYY-MM-DD_TYPE_participant`
- Frontmatter: 6 fields (version, date, type, participant, created, edited)
- Taxonomy: 7 categories (internal, external, coaching, partnership, sales, technical, workshop)

**Rationale:**
- Machine-optimized (predictable structure, easy parsing)
- Human-readable (clear at a glance)
- Greppable (by any dimension)
- Simple (minimal fields, stable taxonomy)
- Derivable from metadata (no manual categorization)

**Risk:** ~20-30 existing folders renamed, all files gain frontmatter
**Mitigation:** Full testing, dry-run review, rollback procedures, audit logs

---

## Questions for V

1. **Taxonomy:** Do these 7 categories cover your meeting types? Any to add/change?
2. **Participant naming:** For organizations, use full name or abbreviation? (e.g., "wisdom-partners" vs "wisdom")
3. **Internal meetings:** Use specific descriptor (e.g., "standup", "war-room") or generic "internal"?
4. **Frontmatter fields:** Any additional fields you want tracked? (e.g., location, duration, platform?)
5. **Optional blocks tuning:** Want to address this now or separate effort?

---

**READY TO BUILD ONCE APPROVED**
