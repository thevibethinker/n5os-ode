# Calendar Event Tagging System — User Guide

**Version:** 2.0.0 (V-OS Integration)  
**Date:** 2025-10-11  
**Status:** Active — Harmonized with Howie

---

## Overview

The meeting prep digest uses **V-OS tags** (square bracket format) in calendar event descriptions to automatically classify and prioritize meetings. This system is shared with Howie, your email scheduling assistant, creating a unified tagging language across both AI systems.

**Key Benefit:** One tag system to learn, used by both Howie (scheduling) and Zo (meeting prep).

---

## Quick Reference

### Lead/Stakeholder Types

| Tag | Who | Meeting Type | Priority |
|-----|-----|--------------|----------|
| `[LD-INV]` | Investors, VCs | Discovery | CRITICAL ⚠️ |
| `[LD-HIR]` | Job seekers | Discovery | Normal |
| `[LD-COM]` | Community partners | Partnership | Normal |
| `[LD-NET]` | Business partners | Discovery | Normal |
| `[LD-GEN]` | General prospects | Discovery | Normal |

### Timing

| Tag | Meaning |
|-----|---------|
| `[!!]` | CRITICAL/Urgent — protect time block ⚠️ |
| `[D5]` | Schedule within 5 days |
| `[D5+]` | Schedule 5+ days out |
| `[D10]` | Schedule 10+ days out |

### Status

| Tag | Meaning | Digest Behavior |
|-----|---------|-----------------|
| `[OFF]` | Postponed | Skipped |
| `[AWA]` | Awaiting response | Included |
| `[TERM]` | Terminated/Inactive | Skipped |

### Coordination

| Tag | Meaning |
|-----|---------|
| `[LOG]` | Coordinate with Logan |
| `[ILS]` | Coordinate with Ilse |

### Accommodation Level

| Tag | Meaning | Prep Focus |
|-----|---------|------------|
| `[A-0]` | Minimal | Clear requirements, 1-2 options |
| `[A-1]` | Baseline | Standard flexibility |
| `[A-2]` | Full | Understand their needs, 3+ options |

### Weekend

| Tag | Meaning |
|-----|---------|
| `[WEX]` | Weekend exception (allowed) |
| `[WEP]` | Weekend preferred |

### Priority Preferences

| Tag | Meaning |
|-----|---------|
| `[GPT-I]` | Prioritize internal meetings |
| `[GPT-E]` | Prioritize external meetings |
| `[GPT-F]` | Prioritize founder meetings |

---

## Tag Syntax

### Basic Format

```
[TAG1] [TAG2] [TAG3] *

Purpose: Brief description of meeting

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.
```

**Important:** The asterisk `*` at the end of the tag block **activates** the tags. Without it, tags are informational only.

### Example Calendar Descriptions

#### Example 1: Investor Meeting (Critical)
```
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline and requirements

---
Please send pitch deck in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...
```

**Result:**
- 🔴 **CRITICAL priority** (auto-set by [LD-INV])
- BLUF: "Investor meeting: discuss series a funding timeline..."
- Prep action: "⚠️ CRITICAL: Protect this time block — do not reschedule"

---

#### Example 2: Hiring Discussion with Full Accommodation
```
[LD-HIR] [A-2] [WEP] *

Purpose: Evaluate senior engineering candidate

---
Please send resume in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...
```

**Result:**
- BLUF: "Hiring discussion: evaluate fit — Focus: understand their needs and constraints"
- Prep action: "Prepare 3+ options showing flexibility"
- Note: "☀️ Weekend meeting — likely high engagement from their side"

---

#### Example 3: Partnership with Team Coordination
```
[LD-NET] [LOG] [ILS] *

Purpose: Finalize pilot job descriptions and sourcing workflow

---
Please send job descriptions in advance to vrijen@mycareerspan.com.

Google Meet: https://meet.google.com/...
```

**Result:**
- BLUF: "Partnership discussion: finalize pilot job descriptions..."
- Note: "Coordinate with Logan on scheduling and agenda"
- Note: "Coordinate with Ilse on scheduling and agenda"

---

#### Example 4: Urgent Meeting (Non-Investor)
```
[!!] [LD-NET] *

Purpose: Critical partnership decision needed today

---
Google Meet: https://meet.google.com/...
```

**Result:**
- 🔴 **CRITICAL priority** (set by [!!])
- Prep action: "⚠️ CRITICAL: Protect this time block — do not reschedule"

---

#### Example 5: Postponed Meeting
```
[LD-COM] [OFF]

Purpose: Community partnership discussion — postponed to next month
```

**Result:**
- ⏸️ **Skipped in digest** (not actionable this week)

---

## How Howie Populates These Tags

When you schedule a meeting via email with Howie, it:

1. **Analyzes the email thread** for context clues
2. **Selects appropriate V-OS tags** based on:
   - Who you're meeting (investor, candidate, partner)
   - Urgency signals in email ("ASAP", "urgent", "this week")
   - Your scheduling preferences
3. **Populates calendar description** with tags + context
4. **Activates tags** with asterisk `*` when confident

You can always **manually adjust tags** in Google Calendar if Howie gets it wrong.

---

## How Tags Affect Your Meeting Prep Digest

### 1. Filtering

The daily meeting prep digest:
- ✅ Includes meetings with **external attendees** and V-OS tags
- ❌ Excludes `[OFF]` (postponed) and `[TERM]` (inactive) meetings
- ❌ Excludes `[DW]` (deep work) blocks and "Meeting Buffer" events
- ❌ Excludes daily recurring meetings (e.g., "Daily standup")

### 2. Priority & Protection

**Critical meetings** (do not reschedule):
- `[!!]` tag
- `[LD-INV]` tag (investors auto-critical)

**Normal meetings** (flexible):
- Everything else

### 3. BLUF Generation (Bottom Line Up Front)

Tags automatically generate contextual meeting summaries:

| Tag | BLUF Format |
|-----|-------------|
| `[LD-INV]` | "Investor meeting: [topic] with [name]" |
| `[LD-HIR]` | "Hiring discussion: evaluate fit for [name]" |
| `[LD-COM]` | "Community partnership: explore collaboration with [name]" |
| `[LD-NET]` | "Partnership discussion: [topic] with [name]" |

**Accommodation adds focus:**
- `[A-2]` → "— Focus: understand their needs and constraints"
- `[A-0]` → "— Focus: establish clear value and requirements"

### 4. Prep Actions

Tags generate smart prep suggestions:

| Tag/Combo | Prep Action |
|-----------|-------------|
| `[!!]` or `[LD-INV]` | "⚠️ CRITICAL: Protect this time block" |
| `[A-2]` | "Prepare 3+ options showing flexibility" |
| `[A-0]` | "Prepare 1-2 clear options with non-negotiables" |
| Discovery type | "Prepare 3 questions to qualify fit" |
| Partnership type | "Prepare partnership framework and value proposition" |

**Plus always:** "Set explicit outcome: what decision or next step do you need?"

### 5. Coordination Notes

| Tag | Note |
|-----|------|
| `[LOG]` | "Coordinate with Logan on scheduling and agenda" |
| `[ILS]` | "Coordinate with Ilse on scheduling and agenda" |

### 6. Weekend Notes

| Tag | Note |
|-----|------|
| `[WEP]` | "☀️ Weekend meeting — likely high engagement from their side" |
| `[WEX]` | "Weekend availability confirmed" |

---

## When to Use Which Tags

### Use `[LD-INV]` for:
- Current investors
- Prospective VCs during fundraising
- Board members from investor firms
- **Auto-sets CRITICAL priority**

### Use `[LD-HIR]` for:
- Job seekers you're evaluating
- Candidates in interview process
- Talent discussions

### Use `[LD-COM]` for:
- Community organizations (NACE, career centers)
- Industry associations
- Non-profit partnerships

### Use `[LD-NET]` for:
- Business partners (integrations, referral partners)
- Strategic alliances
- Platform partnerships

### Use `[LD-GEN]` for:
- General prospects (haven't qualified yet)
- Cold outbound meetings
- Exploratory discussions

### Use `[!!]` for:
- Urgent non-investor meetings
- Time-sensitive decisions
- Crisis situations

### Use `[A-2]` (full accommodation) for:
- High-value prospects
- Sensitive negotiations
- When relationship-building is key

### Use `[A-0]` (minimal accommodation) for:
- Transactional meetings
- When you have leverage
- Clear requirements, take-it-or-leave-it

---

## Migration from Old System

**Old format (DEPRECATED):** `#stakeholder:investor #type:discovery #priority:high`  
**New format:** `[LD-INV] *`

The old hashtag format is still recognized during transition, but:
- V-OS tags take precedence if both present
- Use V-OS tags for all new meetings
- Old format will be removed in 2026

**Quick translation:**
- `#stakeholder:investor` → `[LD-INV]`
- `#stakeholder:job_seeker` → `[LD-HIR]`
- `#stakeholder:community` → `[LD-COM]`
- `#stakeholder:partner` → `[LD-NET]`
- `#priority:high` or `#priority:protect` → `[!!]`

---

## Tips & Best Practices

### 1. Let Howie Handle It
Most of the time, Howie will auto-populate tags correctly. Only manually adjust if needed.

### 2. Always Activate with `*`
Tags won't affect digest behavior without the asterisk at the end of the tag block.

### 3. Combine Tags Strategically
```
[LD-INV] [!!] [LOG] *  ← Critical investor meeting, coordinate with Logan
[LD-HIR] [A-2] [WEP] *  ← Hiring with full accommodation, weekend OK
```

### 4. Use Status Tags to Clean Up Calendar
- Postponed meeting? Add `[OFF]` → Removed from digest
- Inactive prospect? Add `[TERM]` → Removed from digest

### 5. Coordination Tags for Team Sync
Use `[LOG]` or `[ILS]` when Logan or Ilse need to be looped in on prep/agenda.

---

## Troubleshooting

### Tags Not Working?
1. Check for asterisk `*` at end of tag block
2. Verify tags are in square brackets: `[LD-INV]` not `LD-INV`
3. Run test: `python3 /home/workspace/N5/scripts/meeting_prep_digest.py --dry-run`

### Meeting Not in Digest?
Check if meeting is:
- All-internal (only @mycareerspan.com attendees)
- Tagged with `[OFF]` or `[TERM]`
- Daily recurring pattern
- Title contains `[DW]` or "buffer"

### Wrong BLUF or Prep Actions?
1. Check which tags are active
2. Verify stakeholder type matches intent
3. Adjust tags in calendar description
4. Re-run digest

---

## Reference Documents

**Complete Technical Reference:** `file 'N5/docs/calendar-tagging-system-COMPLETE.md'`  
**Implementation Plan:** `file 'N5/docs/howie-zo-implementation-plan.md'`  
**Command Reference:** `file 'N5/commands/meeting-prep-digest.md'`

---

**Last Updated:** 2025-10-11  
**Version:** 2.0.0 (V-OS Integration)  
**Questions?** Message in Zo or email va@zo.computer
