---
created: 2025-11-04
last_edited: 2025-11-04
version: 2.0
---
# Meeting Folder Naming + Frontmatter Standard - SPECIFICATION v2

**Status:** Pending V approval on format choice  
**Authority:** V approved trap door decision (pending format selection)

---

## Problem Statement

1. **Folder names:** Inconsistent, hard to grep, not human-readable
2. **Files lack frontmatter:** Can't grep by metadata, no version tracking, no standardized fields

---

## Solution Part 1: Frontmatter Standard

### Requirement
**All meeting intelligence files (B01, B02, B05, etc.) MUST include YAML frontmatter**

### Standard Frontmatter Fields

```yaml
---
meeting_date: YYYY-MM-DD
created: YYYY-MM-DD
version: X.Y
processing_version: 2.1.0
meeting_type: category
participants:
  - Name or Org
  - Name or Org
lead_participant: Primary Person or Org
status: complete|partial|pending
---
```

### Field Specifications

**Required fields:**
- `meeting_date`: Date meeting occurred (ISO 8601: YYYY-MM-DD)
- `created`: Date this file was generated
- `version`: File version (starts at 1.0, increments on regeneration)
- `processing_version`: Intelligence pipeline version that generated this
- `meeting_type`: Category from taxonomy (see below)
- `participants`: List of key people/orgs in meeting
- `lead_participant`: Primary stakeholder (used in folder naming)
- `status`: `complete` (full processing) | `partial` (some blocks) | `pending` (queued)

**Optional fields:**
- `tags`: List of relevant tags for grep (e.g., [`sales`, `urgent`, `followup`])
- `priority`: `high|medium|low` (for follow-up tracking)
- `next_meeting`: Date of scheduled follow-up if applicable
- `related_meetings`: Links to related meeting folders

### Example Frontmatter

```yaml
---
meeting_date: 2025-10-29
created: 2025-10-29
version: 1.0
processing_version: 2.1.0
meeting_type: coaching
participants:
  - Alex Caveny
  - Vrijen Attawar
lead_participant: Alex Caveny
status: complete
tags: [wisdom-partners, coaching, strategy]
---
```

### Benefits

✅ **Greppable by any field:**
```bash
# Find all coaching meetings
grep -r "meeting_type: coaching" Personal/Meetings/

# Find meetings with specific participant
grep -r "lead_participant: Alex" Personal/Meetings/

# Find high priority meetings
grep -r "priority: high" Personal/Meetings/

# Find all v2.1.0 processed meetings
grep -r "processing_version: 2.1.0" Personal/Meetings/
```

✅ **Version tracking:** Know which pipeline version generated each file
✅ **Status tracking:** Know completion state at a glance
✅ **Scriptable:** Easy to parse with Python/scripts for analysis
✅ **Standard:** Consistent across all meeting intelligence

---

## Solution Part 2: Folder Naming Standard

### Your Requirements
1. **Date** - Chronological sort (YYYY-MM-DD)
2. **Type** - Internal/external OR specific category
3. **Lead participant or org** - Chief stakeholder
4. **Machine-optimized** - Easy to grep/parse
5. **Human-readable** - Know what it is at a glance

### Meeting Type Categories

**Primary taxonomy (choose one per meeting):**

| Category | Description | Examples |
|----------|-------------|----------|
| `internal` | Team meetings, planning, strategy sessions | Team planning, co-founder sync |
| `coaching` | 1-1 coaching or advisory sessions | Wisdom Partners, exec coaching |
| `sales` | Sales calls, demos, discovery | Prospect calls, product demos |
| `external` | General external stakeholder meetings | Partner intros, exploratory calls |
| `standup` | Daily team standups, quick syncs | Daily standup, weekly check-in |
| `partnership` | Partnership discussions, negotiations | Affiliate partnerships, integrations |
| `workshop` | Group learning, training, workshops | AI MBA, team training |
| `advisory` | Board meetings, advisor check-ins | Board updates, advisor sessions |
| `research` | User research, customer discovery | User interviews, feedback sessions |

**Do you want to add, remove, or modify any categories?**

### Naming Format Options

I've created 3 options that balance your requirements. Pick the one you prefer:

---

#### **Option A: TYPE-first (Machine Optimized)**
**Format:** `YYYY-MM-DD_TYPE_lead-participant_context`

**Examples:**
```
2025-10-29_coaching_alex-caveny_wisdom-partners
2025-11-03_internal_sunday-standup
2025-09-12_external_allie-cialeo_greenlight-intro
2025-09-04_workshop_ai-agent-mba
2025-11-03_internal_acquisition-strategy
2025-10-28_coaching_rochel-1on1
```

**Pros:**
- Type is immediate and prominent
- Easy to grep by category: `ls -d *_coaching_*`
- Machine-optimized for filtering
- Consistent structure

**Cons:**
- Type might feel redundant when context is obvious
- Slightly less human-readable

---

#### **Option B: Participant-first (Human Readable)**
**Format:** `YYYY-MM-DD_lead-participant_context_TYPE`

**Examples:**
```
2025-10-29_alex-caveny_wisdom-partners_coaching
2025-11-03_sunday-standup_internal
2025-09-12_allie-cialeo_greenlight-intro_external
2025-09-04_ai-agent-mba_workshop
2025-11-03_acquisition-strategy_internal
2025-10-28_rochel_1on1_coaching
```

**Pros:**
- Most human-readable
- Lead participant prominent (who you met with)
- Natural flow: date → who → what → type
- Context-rich

**Cons:**
- Type at end, slightly harder to grep by category
- Can still grep: `ls -d *_coaching` works fine

---

#### **Option C: Hybrid (Balanced)**
**Format:** `YYYY-MM-DD_TYPE_lead-participant`

**Examples:**
```
2025-10-29_coaching_alex-caveny
2025-11-03_internal_sunday-standup
2025-09-12_external_allie-cialeo
2025-09-04_workshop_ai-agent-mba
2025-11-03_internal_acquisition-strategy
2025-10-28_coaching_rochel
```

**Pros:**
- Concise, clean
- Type prominent for grepping
- Lead participant clear
- Machine-optimized

**Cons:**
- Loses rich context in folder name
- Need to open folder to see full context
- Some meetings might need context to disambiguate

---

### **My Recommendation: Option B (Participant-first)**

**Why:**
- Most human-readable while still machine-greppable
- You work with people, not categories—seeing "alex-caveny" first is more intuitive
- Context preserved (wisdom-partners tells you more than just "coaching")
- Category at end still easy to grep: `ls -d *_coaching`
- Balances your "machine optimized but very readable" goal best

**What do you prefer? A, B, or C?**

---

## Implementation Plan

### Phase 1: Add Frontmatter to Intelligence Generator
**File:** `N5/services/meeting-intelligence/generate_intelligence.py`

**Changes:**
1. Define frontmatter template
2. Extract fields from metadata/conversation
3. Prepend frontmatter to all generated blocks (B01, B02, etc.)
4. Ensure consistent formatting

**Timeline:** 1-2 hours

### Phase 2: Build Renaming Script
**File:** `N5/scripts/meeting_renamer.py`

**Logic:**
1. Read B26_metadata.md (contains all needed info)
2. Extract: meeting_date, meeting_type, lead_participant
3. Generate folder name using chosen format (A, B, or C)
4. Dry-run by default, show proposed changes
5. Execute with `--execute` flag

**Timeline:** 2-3 hours

### Phase 3: Backfill Existing Meetings
**Process:**
1. Add frontmatter to existing intelligence files
2. Rename folders using new standard
3. Log all changes
4. V reviews and approves

**Timeline:** 1-2 hours

### Phase 4: Integrate into Pipeline
**Hook:** After metadata generation (B26_metadata.md complete)

**Auto-actions:**
1. Add frontmatter to all generated blocks
2. Rename folder to standard format
3. Log rename event

**Timeline:** 1 hour

---

## Optional Block Generation Optimization

**Current state:** Blocks generating consistently ✅

**Requested improvement:** Make optional block selection more "open-minded"

**Implementation:**
- Review current block selection logic in `generate_intelligence.py`
- Adjust thresholds/prompts to be less conservative
- Test on a few meetings to ensure quality maintained
- V provides feedback on whether more blocks are useful vs. noisy

**Timeline:** 30 minutes tuning + testing

---

## Success Criteria

✅ All meeting intelligence files have standardized frontmatter
✅ All meeting folders follow chosen naming convention
✅ Can grep by any frontmatter field
✅ Can grep folders by date/type/participant
✅ Human-readable at glance
✅ Machine-parseable for automation
✅ Version tracking functional
✅ Processing pipeline auto-applies standards to new meetings
✅ Complete audit log of all changes

---

## Grep Examples (Post-Implementation)

**Using frontmatter:**
```bash
# All coaching meetings
grep -rl "meeting_type: coaching" Personal/Meetings/

# Meetings with Alex Caveny
grep -rl "Alex Caveny" Personal/Meetings/*/B26_metadata.md

# All v2.1.0 processed meetings
grep -rl "processing_version: 2.1.0" Personal/Meetings/

# High priority meetings
grep -rl "priority: high" Personal/Meetings/
```

**Using folder names (assuming Option B):**
```bash
# All coaching meetings
ls -d Personal/Meetings/*_coaching/

# All meetings with Alex
ls -d Personal/Meetings/*alex*

# October coaching meetings
ls -d Personal/Meetings/2025-10-*_coaching/

# All external meetings
ls -d Personal/Meetings/*_external/
```

---

## Decisions Needed from V

1. **Categories:** Approve the 9 categories, or add/remove/modify?
2. **Naming format:** Choose A, B, or C (I recommend B)
3. **Optional frontmatter fields:** Any others you want standardized?
4. **Optional block tuning:** Proceed with making selection more open-minded?

Once decided, I'll implement in ~5-6 hours total.

---

**READY FOR V DECISIONS**
