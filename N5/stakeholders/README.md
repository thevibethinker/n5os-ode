# Stakeholder Knowledge Reservoir System

**Date:** 2025-10-12  
**Status:** ✅ Core Infrastructure Complete  
**Purpose:** Progressive knowledge accumulation for external stakeholders

---

## System Overview

This system builds and maintains comprehensive profiles for external stakeholders (investors, partners, advisors, etc.) that grow richer over time through:

1. **Auto-detection** — New stakeholders discovered when meetings are scheduled
2. **Email history analysis** — Deep search (up to 500 messages, not just 3)
3. **LLM-based inference** — Organization, role, lead type inferred from available data
4. **Interactive fill-in** — V answers targeted questions when system is uncertain
5. **Incremental updates** — Each new meeting/email adds to profile without overwriting
6. **Safe merge strategies** — Protects manually-crafted insights from automation

---

## How It Works

### Phase 1: Profile Creation (Auto)

**Trigger:** New meeting scheduled with external email

```
1. Calendar event detected with external@company.com
2. System searches Gmail for ALL history (not just 3 messages)
3. LLM analyzes:
   - Email signatures → infer organization & role
   - Thread context → infer relationship origin
   - Domain analysis → suggest lead type
   - Communication patterns → engagement level
4. Profile created with best-effort fields
5. If uncertain → questions flagged for V
```

**Output:** Initial profile in `N5/stakeholders/person-name.md`

---

### Phase 2: V Reviews & Fills Gaps

**Trigger:** V sees questions in meeting prep or weekly digest

**Questions might be:**
- "What lead type best describes [Person]?" (if system confidence <80%)
- "What is [Person]'s role at [Company]?" (if not in email signature)
- "How did you meet [Person]?" (if earliest email unclear)

**V provides answers** → System updates profile with "Verified" status

---

### Phase 3: Progressive Updates (Ongoing)

**Trigger:** New meeting transcript processed

```
1. Meeting transcript ingested
2. LLM extracts:
   - Summary of discussion
   - Key points discussed
   - Action items / outcomes
3. System calls safe_stakeholder_updater.append_interaction()
4. New interaction added to "Interaction History" section
5. Existing content (manual insights) preserved
6. Backup created automatically
```

**Result:** Profile grows richer with each interaction

---

## Directory Structure

```
N5/stakeholders/
├── README.md (this file)
├── _template.md (profile template)
├── index.jsonl (lookup table: email → profile file)
├── person-name-1.md (individual profiles)
├── person-name-2.md
├── ...
├── .backups/ (timestamped backups before each update)
│   ├── person-name-1_20251012_143022.md
│   ├── person-name-1_20251012_150145.md
│   └── ...
├── .pending_updates/ (preview diffs before applying)
│   └── person-name-1_update_preview_20251012_151234.md
└── .update_log.jsonl (audit trail of all updates)
```

---

## Profile Schema

Each profile follows this structure:

```markdown
---
# YAML frontmatter (metadata)
name: "Full Name"
email_primary: "email@domain.com"
organization: "Company Name"
role: "Job Title"
first_contact: "2025-10-10"
last_updated: "2025-10-12"
lead_type: "LD-NET"
status: "active"
---

# Full Name

**Organization:** Company Name
**Role:** Job Title
**Email:** email@domain.com
**Lead Type:** LD-NET (Partner)
**Status:** Active

---

## Tags

### Verified (Last reviewed: 2025-10-12)
- `#stakeholder:partner:collaboration`
- `#relationship:new`
- `#priority:normal`
- `#engagement:needs_followup`
- `#context:hr_tech`

### Tag History
- 2025-10-12: Initial tags added via retroactive analysis

---

## Relationship Context

### How We Met
[Auto-inferred or V-provided]

### Key Objectives
**Their asks:** [What they want from V/Careerspan]
**V's asks:** [What V wants from them]
**Open loops:** [Pending items]

---

## Interaction History

### 2025-10-10: Initial Meeting
**Type:** Meeting
**Summary:** [LLM-generated from transcript]
**Key Points:**
- Point 1
- Point 2
**Outcomes:**
- Action item 1
**Linked artifact:** `file 'N5/records/meetings/...'`

---

### 2025-10-15: Follow-up Meeting
**Type:** Meeting
**Summary:** [Next meeting summary]
...

---

## Product & Mission
[Manual insights - protected from auto-overwrite]

## Founder Motivation & Values
[Manual insights - protected from auto-overwrite]

## Strategic Posture
[Manual insights - protected from auto-overwrite]

---

## Quick Reference

**Contact Preferences:** [Learned over time]
**Timezone:** [Inferred or stated]
**LinkedIn:** [URL]
**Company Website:** [URL]
```

---

## Key Features

### 1. No 3-Message Limit
- Gmail API supports up to 500 results per query
- Can paginate for thousands more
- System searches full history on profile creation
- Date filters enable progressive search (e.g., "last 90 days" for updates)

### 2. Safe Updates (No Overwrites)
- **Append-only interaction history** — New meetings add entries, never replace
- **Tag addition only** — Tags can be added but never auto-removed
- **Section merge strategies** — Enrichment without overwriting manual content
- **Automatic backups** — Every update creates timestamped backup
- **Dry-run preview** — Review changes before applying

### 3. Cumulative Knowledge
- Each meeting transcript adds to profile
- Over time, you have:
  - Complete interaction history
  - Evolution of relationship
  - All meeting notes linked
  - Strategic insights accumulated
- Meeting prep becomes: "Load profile + recent updates" (fast & accurate)

### 4. Tag Taxonomy Integration
- Uses hashtag format internally (`#stakeholder:investor`)
- Translates to Howie brackets (`[LD-INV]`) for calendar
- Supports rich tagging:
  - Stakeholder types (investor, advisor, partner, etc.)
  - Relationship status (new, warm, active, cold)
  - Priority levels (critical, high, normal, low)
  - Engagement behavior (responsive, slow, needs_followup)
  - Industry context (hr_tech, venture_capital, saas, etc.)

### 5. Deep Research Integration
- Auto-triggers for high-priority contacts (investors, strategic partners)
- Fetches LinkedIn profiles (authenticated via Zo's browser)
- Web search for company/person background
- Due diligence dossiers via `command 'deep-research-due-diligence'`
- Cached to avoid redundant lookups

---

## Integration Points

### A. Meeting Prep Digest
**When:** Daily at 10 AM ET (or on-demand)

```
For each external meeting tomorrow:
1. Load stakeholder profile
2. Fetch recent emails (last 30-90 days)
3. Generate prep digest:
   - Profile context (how we met, objectives)
   - Recent interactions summary
   - Suggested talking points
   - Open loops to close
```

**Before (without profiles):**
- Start from scratch each time
- Re-search email history
- No cumulative knowledge
- Generic prep advice

**After (with profiles):**
- Rich context immediately available
- Know relationship history
- Specific talking points
- Track open loops across meetings

---

### B. Meeting Transcript Ingestion
**When:** After transcript processed

```
1. Extract key info from transcript
2. Call update_profile_from_transcript()
3. New interaction appended to profile
4. Index updated with last_interaction date
5. Backup created automatically
```

**Result:** Profile grows richer automatically after each meeting

---

### C. Weekly Stakeholder Review
**When:** Sunday 6 PM ET (automated)

```
1. Scan emails for new external contacts (last 7 days)
2. Discover stakeholders not yet in system
3. Analyze email patterns for tag suggestions
4. Generate digest with:
   - New contacts to add
   - Suggested tags (with confidence scores)
   - Profiles needing update
5. Send to V for review
6. Apply V's approved changes
```

**V's workflow:**
- Review ~10 min/week
- Approve/edit suggested tags
- Answer clarifying questions
- System applies updates safely

---

## Scripts & Tools

### Core Implementation
- **`stakeholder_manager.py`** — Profile creation, indexing, basic updates
- **`safe_stakeholder_updater.py`** — Protected update operations with backups
- **`auto_create_stakeholder_profiles.py`** — Calendar scan → auto profile creation

### Supporting Tools
- **Tag taxonomy:** `N5/docs/TAG-TAXONOMY-MASTER.md`
- **Tag mapping:** `N5/config/tag_mapping.json`
- **Deep research:** `N5/commands/deep-research-due-diligence.md`
- **CRM integration:** `N5/scripts/crm_query.py` (SQLite database)

---

## Usage Examples

### Create Profile for New Stakeholder
```python
from stakeholder_manager import create_profile_file

profile = create_profile_file(
    email="person@company.com",
    name="Person Name",
    organization="Company Inc",
    role="VP of Partnerships",
    lead_type="LD-NET",  # Partner
    relationship_context="Met through mutual connection at conference",
    interaction_summary="Initial email about collaboration opportunity",
    first_contact_date="2025-10-10"
)
```

---

### Update Profile After Meeting
```python
from stakeholder_manager import update_profile_from_transcript

update_profile_from_transcript(
    email="person@company.com",
    meeting_date="2025-10-15",
    meeting_title="Follow-up: Partnership Discussion",
    transcript_summary="Discussed specific integration use cases",
    key_points=[
        "Agreed on embedded widget approach",
        "Reviewed technical requirements",
        "Discussed timeline: Q1 2026"
    ],
    outcomes=[
        "V to send technical spec by Oct 20",
        "Person to review internally and respond by Oct 27"
    ],
    linked_artifact="N5/records/meetings/2025-10-15_person-company/meeting_note.md",
    dry_run=False  # Set True to preview
)
```

---

### Add Tag Safely
```python
from safe_stakeholder_updater import add_tag_safely

add_tag_safely(
    profile_path=Path("N5/stakeholders/person-company.md"),
    tag="#stakeholder:advisor",
    tag_category="Verified",
    verification_source="Confirmed via Oct 15 meeting",
    dry_run=False
)
```

---

### Preview Batch Updates
```python
from safe_stakeholder_updater import preview_update

operations = [
    {
        'type': 'append_interaction',
        'params': {
            'interaction_date': '2025-10-15',
            'interaction_title': 'Follow-up Meeting',
            'summary': 'Discussed next steps',
            'key_points': ['Key point 1', 'Key point 2'],
            'outcomes': ['Action 1', 'Action 2']
        }
    },
    {
        'type': 'add_tag',
        'params': {
            'tag': '#priority:high',
            'tag_category': 'Verified',
            'verification_source': 'Strategic importance confirmed'
        }
    }
]

preview_path = preview_update(
    profile_path=Path("N5/stakeholders/person-company.md"),
    update_operations=operations
)

# Review: N5/stakeholders/.pending_updates/person-company_update_preview_*.md
```

---

## Safeguards Summary

### ✅ Protected Operations
- Append interactions (never overwrite)
- Add tags (never remove)
- Enrich sections (merge strategies)
- Automatic backups before every change
- Preview/dry-run mode for all operations
- Audit logging of all updates

### ❌ Prohibited Operations
- Replace existing sections
- Remove tags automatically
- Delete interaction entries
- Modify without backup
- Updates without conflict detection

**See:** `file 'N5/docs/stakeholder-profile-update-safeguards.md'` for complete protection details

---

## Benefits

### Before This System
- ❌ Cold start for every meeting prep
- ❌ Re-process email history each time
- ❌ No memory between interactions
- ❌ Risk of losing context
- ❌ Generic prep advice

### After This System
- ✅ Rich context immediately available
- ✅ One-time email history processing
- ✅ Cumulative knowledge over time
- ✅ Protected manual insights
- ✅ Specific, contextual prep

### Scalability
- **Week 1:** 5 profiles, basic info
- **Week 4:** 20 profiles, interaction histories building
- **Week 12:** 50+ profiles, rich relationship context
- **Week 26:** 100+ profiles, strategic intelligence asset

---

## Next Steps

### Immediate (This Week)
1. ✅ Core infrastructure complete
2. ⏳ Test with existing stakeholders (Hamoon, Alex)
3. ⏳ Integrate with meeting prep digest
4. ⏳ Deploy calendar scan for auto-creation

### Short Term (Next 2 Weeks)
1. Add LinkedIn enrichment (authenticated via view_webpage)
2. Implement weekly review digest
3. Test with 10-20 real stakeholders
4. Refine LLM inference prompts based on accuracy

### Medium Term (Month 1-2)
1. Build stakeholder query interface (search by tags, company, etc.)
2. Add relationship scoring (interaction frequency, recency, quality)
3. Smart prompts ("Haven't heard from X in 90 days — follow up?")
4. CRM integration (sync with SQLite database)

### Long Term (Month 3+)
1. Howie context API (Howie queries stakeholder intelligence)
2. Automated due diligence triggers for investors
3. Pattern analysis across stakeholders (e.g., common objections from VCs)
4. Strategic insights dashboard

---

## Related Documentation

- **Safeguards:** `file 'N5/docs/stakeholder-profile-update-safeguards.md'`
- **Tag taxonomy:** `file 'N5/docs/TAG-TAXONOMY-MASTER.md'`
- **Tagging system:** `file 'N5/docs/STAKEHOLDER-TAGGING-COMPLETE.md'`
- **Deep research:** `file 'N5/commands/deep-research-due-diligence.md'`
- **Meeting prep:** `file 'N5/commands/meeting-prep-digest.md'`

---

**System Ready:** October 12, 2025  
**First Production Use:** Week of October 14, 2025  
**Owner:** V + Zo**
