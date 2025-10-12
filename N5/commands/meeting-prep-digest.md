# `meeting-prep-digest`

Generate daily meeting intelligence digest with attendee research and email context.

**Version:** 3.0.0 (N5OS Tag Support)  
**Updated:** 2025-10-11

---

## Usage

```bash
# Generate digest for today
meeting-prep-digest

# Generate for specific date
meeting-prep-digest --date 2025-10-12

# Preview without saving
meeting-prep-digest --dry-run
```

---

## Description

Automated daily meeting prep that scans your calendar, filters for **external stakeholder meetings only**, researches attendees, and surfaces relevant context in a streamlined BLUF (Bottom Line Up Front) format.

**What it does:**

1. **Calendar Scan** — Fetches today's meetings from Google Calendar
2. **Smart Filtering** — External stakeholders only; excludes internal/buffer/postponed events
3. **N5OS Tag Recognition** — Reads N5OS tags from calendar descriptions (`[LD-INV]`, `[!!]`, etc.)
4. **Last 3 Interactions** — Pulls most recent Gmail threads with each stakeholder
5. **Profile Check** — References existing stakeholder profiles from past meetings
6. **Calendar Context** — Extracts meeting purpose and context from description
7. **BLUF Format** — Bottom Line Up Front summaries for quick action
8. **Smart Prep Actions** — Context-aware suggestions based on N5OS tags

**Exclusions:**
- All-internal meetings (only @mycareerspan.com or @theapply.ai)
- `[OFF]` (postponed) and `[TERM]` (inactive) meetings
- `[DW]` (deep work) blocks and "Meeting Buffer" events
- Daily recurring meetings ("Daily standup", "Daily sync", etc.)
- Declined meetings
- All-day events

**New in v3.0.0:**
- ✅ **N5OS Tag Support** — Harmonized with Howie's N5OS tag system
- ✅ **Binary Priority** — Critical (`!!` or `[LD-INV]`) vs non-critical
- ✅ **Accommodation Awareness** — Prep actions adapt to `[A-0]`, `[A-1]`, `[A-2]`
- ✅ **Stakeholder-Specific BLUFs** — Different formats for investors, hiring, partners
- ✅ **Coordination Notes** — Auto-surfaces `[LOG]` and `[ILS]` tags
- ✅ **Weekend Indicators** — Highlights `[WEP]` and `[WEX]` meetings
- ✅ **Status Filtering** — Skips `[OFF]` and `[TERM]` meetings

---

## N5OS Tag Support

The digest recognizes and processes N5OS tags from calendar event descriptions.

### Supported Tag Categories

#### Lead/Stakeholder Types (`{CATG}`)
```
[LD-INV]  — Investor/VC (auto-sets CRITICAL priority)
[LD-HIR]  — Job seeker (recruiting/hiring)
[LD-COM]  — Community partner
[LD-NET]  — Business partner
[LD-GEN]  — General prospect
```

#### Timing (`{TWIN}`)
```
[!!]   — CRITICAL/Urgent (protect time block)
[D5]   — Schedule within 5 days
[D5+]  — Schedule 5+ days out
[D10]  — Schedule 10+ days out
```

#### Status (`{POST}`)
```
[OFF]  — Postponed (skipped in digest)
[AWA]  — Awaiting response
[TERM] — Terminated/Inactive (skipped in digest)
```

#### Coordination (`{CORD}`)
```
[LOG]  — Coordinate with Logan
[ILS]  — Coordinate with Ilse
```

#### Accommodation Level (`{MISC}`)
```
[A-0]  — Minimal (clear requirements)
[A-1]  — Baseline (standard flexibility)
[A-2]  — Full (understand their needs)
```

#### Weekend (`{WKND}`)
```
[WEX]  — Weekend exception (allowed)
[WEP]  — Weekend preferred
```

#### Priority Preferences (`{GPT}`)
```
[GPT-I]  — Prioritize internal meetings
[GPT-E]  — Prioritize external meetings
[GPT-F]  — Prioritize founder meetings
```

**Tag Activation:** Asterisk `*` at END of tag block activates tags.

**Example Calendar Description:**
```
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

---
Please send pitch deck in advance to vrijen@mycareerspan.com.
```

**See full documentation:** `file 'N5/docs/calendar-tagging-system.md'`

---

## How Tags Affect Output

### Priority & Protection

**Critical meetings** (`!!` or `[LD-INV]`):
- BLUF includes stakeholder type
- First prep action: "⚠️ CRITICAL: Protect this time block — do not reschedule"

**Non-critical meetings** (everything else):
- Standard prep actions
- No special protection warning

### BLUF Adaptation

| Tag | BLUF Format |
|-----|-------------|
| `[LD-INV]` | "Investor meeting: [topic] with [name]" |
| `[LD-HIR]` | "Hiring discussion: evaluate fit for [name]" |
| `[LD-COM]` | "Community partnership: explore collaboration with [name]" |
| `[LD-NET]` | "Partnership discussion: [topic] with [name]" |
| Discovery type | "Discovery: understand needs and fit for [name]" |

**Accommodation focus:**
- `[A-2]` adds: "— Focus: understand their needs and constraints"
- `[A-0]` adds: "— Focus: establish clear value and requirements"

### Prep Actions

| Tag/Combo | Prep Action |
|-----------|-------------|
| `[!!]` or `[LD-INV]` | "⚠️ CRITICAL: Protect this time block" |
| `[A-2]` | "Prepare 3+ options showing flexibility" |
| `[A-0]` | "Prepare 1-2 clear options with non-negotiables" |
| Discovery type | "Prepare 3 questions to qualify fit" |
| Partnership type | "Prepare partnership framework and value proposition" |
| Default | "Review last interaction and prepare 1-2 specific asks" |

**Always includes:** "Set explicit outcome: what decision or next step do you need?"

### Coordination & Weekend Notes

| Tag | Note in Digest |
|-----|----------------|
| `[LOG]` | "**Note:** Coordinate with Logan on scheduling and agenda" |
| `[ILS]` | "**Note:** Coordinate with Ilse on scheduling and agenda" |
| `[WEP]` | "**Note:** ☀️ Weekend meeting — likely high engagement from their side" |
| `[WEX]` | "**Note:** Weekend availability confirmed" |

---

## Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--date` | str | today | Target date (YYYY-MM-DD or "today") |
| `--dry-run` | flag | False | Preview without generating file |

---

## What Gets Generated

**Output File:** `N5/digests/daily-meeting-prep-YYYY-MM-DD.md`

**Content Structure:**

### 1. Table of Contents (Chronological)
- Meeting count summary
- Chronological list with times and attendee counts
- External stakeholders only

### 2. Per-Meeting Section (BLUF Format)
```markdown
## [TIME] — [TITLE] (stakeholder · type · CRITICAL)

**BLUF:** [Context-aware one-sentence objective]

**Last 3 interactions:**
- [Date] — [Context from Gmail]
- [Date] — [Context from Gmail]
- [Date] — [Context from Gmail]

**Calendar context:** [Purpose from event description]

**Past notes:** `file 'path/to/stakeholder-profile.md'`

**Prep actions:**
1. [Context-aware action based on N5OS tags]
2. [Context-aware action based on N5OS tags]
3. Set explicit outcome: what decision or next step do you need?

**Note:** [Coordination or weekend notes from N5OS tags]

---
```

---

## Examples

### Example 1: Investor Meeting with Critical Priority

**Calendar Event:**
```
Title: Series A Discussion - Acme Ventures
Time: 2:00 PM - 3:00 PM
Description:
[LD-INV] [D5+] *

Purpose: Discuss funding timeline and terms

---
Please send pitch deck in advance to vrijen@mycareerspan.com.
```

**Digest Output:**
```markdown
## 14:00 — Series A Discussion - Acme Ventures (investor · discovery · CRITICAL)

**BLUF:** Investor meeting: series a discussion with Jane Smith

**Last 3 interactions:**
- 2025-10-08 — Sent updated pitch deck, discussed timeline
- 2025-09-20 — Initial intro call, strong interest in ed-tech
- 2025-09-05 — Warm intro via mutual connection

**Calendar context:** Discuss funding timeline and terms

**Past notes:** `file 'N5/records/meetings/2025-09-20-acme-ventures/stakeholder-profile.md'`

**Prep actions:**
1. ⚠️ CRITICAL: Protect this time block — do not reschedule
2. Prepare 3 questions to qualify fit
3. Set explicit outcome: what decision or next step do you need?

---
```

---

### Example 2: Hiring Discussion with Full Accommodation

**Calendar Event:**
```
Title: Engineering Candidate - Alex Chen
Time: 10:00 AM - 11:00 AM
Description:
[LD-HIR] [A-2] [WEP] *

Purpose: Evaluate senior backend engineer for platform team

---
Please send resume in advance to vrijen@mycareerspan.com.
```

**Digest Output:**
```markdown
## 10:00 — Engineering Candidate - Alex Chen (job_seeker · discovery)

**BLUF:** Hiring discussion: evaluate fit for Alex Chen — Focus: understand their needs and constraints

**Last 3 interactions:**
- 2025-10-10 — Confirmed interview, shared engineering challenges
- 2025-10-05 — Applied via LinkedIn, strong Python/FastAPI background
- (No third interaction found)

**Calendar context:** Evaluate senior backend engineer for platform team

**Prep actions:**
1. Prepare 3+ options showing flexibility
2. Set explicit outcome: what decision or next step do you need?

**Note:** ☀️ Weekend meeting — likely high engagement from their side

---
```

---

### Example 3: Partnership with Coordination

**Calendar Event:**
```
Title: Pilot Kickoff - University Career Center
Time: 3:00 PM - 4:00 PM
Description:
[LD-COM] [LOG] [ILS] *

Purpose: Finalize pilot scope and timeline

---
Please send job descriptions in advance to vrijen@mycareerspan.com.
```

**Digest Output:**
```markdown
## 15:00 — Pilot Kickoff - University Career Center (community · partnership)

**BLUF:** Community partnership: explore collaboration with Maria Rodriguez

**Last 3 interactions:**
- 2025-10-07 — Sent pilot proposal, discussed job description needs
- 2025-09-25 — Discovery call, strong fit for career center partnership
- 2025-09-10 — Intro via NACE conference connection

**Calendar context:** Finalize pilot scope and timeline

**Prep actions:**
1. Prepare partnership framework and value proposition
2. Set explicit outcome: what decision or next step do you need?

**Note:** Coordinate with Logan on scheduling and agenda
**Note:** Coordinate with Ilse on scheduling and agenda

---
```

---

## Testing

### Unit Tests
```bash
# Test N5OS tag extraction
python3 /home/.z/workspaces/con_Qqg3HjE36MRpwyYi/test_vos_tags.py
```

### Integration Test
```bash
# Dry-run with current calendar
meeting-prep-digest --dry-run

# Expected behavior:
# - External meetings only
# - N5OS tags extracted and processed
# - Critical meetings flagged
# - Prep actions adapted to tags
# - Coordination notes included
```

---

## Troubleshooting

### Issue: Tags not recognized
**Solution:** 
1. Verify asterisk `*` at end of tag block
2. Check square bracket format: `[LD-INV]` not `LD-INV`
3. Run dry-run to test: `meeting-prep-digest --dry-run`

### Issue: Meeting not in digest
**Check if meeting:**
- Has only internal attendees (@mycareerspan.com)
- Tagged with `[OFF]` or `[TERM]`
- Daily recurring pattern ("Daily standup")
- Title contains `[DW]` or "buffer"

### Issue: Wrong prep actions
**Solution:**
1. Verify which N5OS tags are active
2. Check stakeholder type mapping
3. Adjust tags in calendar description
4. Re-run digest

---

## Related Commands

- `command 'meeting-research'` — Deep research on single stakeholder
- `command 'stakeholder-profile'` — Generate/update stakeholder profile
- `command 'follow-up'` — Generate follow-up email after meeting

---

## Technical Reference

**Script:** `file 'N5/scripts/meeting_prep_digest.py'`  
**Complete Documentation:** `file 'N5/docs/calendar-tagging-system-COMPLETE.md'`  
**User Guide:** `file 'N5/docs/calendar-tagging-system.md'`  
**Implementation Plan:** `file 'N5/docs/howie-zo-implementation-plan.md'`

---

**Version:** 3.0.0 (N5OS Tag Support)  
**Last Updated:** 2025-10-11  
**Status:** Active — Phase 1 Complete
