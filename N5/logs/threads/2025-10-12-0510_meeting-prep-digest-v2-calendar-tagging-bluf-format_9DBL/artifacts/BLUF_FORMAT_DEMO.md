# Daily Meeting Prep Digest — BLUF Format Demo

**Date:** 2025-10-12  
**Generated:** 2025-10-11 12:28 EDT  
**Status:** DRY RUN (No files saved, no emails sent)

---

## Overview

This demonstrates the new **BLUF (Bottom Line Up Front)** format for the daily meeting prep digest v2.0.0.

---

## Key Features

### 1. **Chronological Table of Contents**
- Meetings listed earliest to latest
- Quick scan format with time and attendee count
- External stakeholders only

### 2. **BLUF Format Per Meeting**
- **BLUF:** One-sentence objective (what the meeting achieves)
- **Last 3 interactions:** Brief context from Gmail history
- **Calendar context:** Extracted from event description
- **Past notes:** Links to stakeholder profiles (if available)
- **Prep actions:** 1-3 specific, actionable items

### 3. **Tag-Based Intelligence**
- Tags parsed from calendar description: `#stakeholder:TYPE #type:TYPE #priority:LEVEL`
- BLUF tailored to meeting type
- Prep actions customized based on tags

### 4. **Streamlined & Actionable**
- No extraneous information
- Focus on last 3 interactions
- Specific prep actions
- Calendar protection warnings

---

## Sample Output

## Today's External Stakeholder Meetings

**Total:** 1 meeting(s)

1. **09:00** — Aniket Partnership Follow-up (1 external)

---

## 09:00 — Aniket Partnership Follow-up (#partner type:follow-up)

**BLUF:** Follow-up: advance partnership/relationship with Aniket

**Last 3 interactions:**
- 2025-10-08 — Confirmed interest in pilot, requested job descriptions
- 2025-09-15 — Initial intro, discussed recruiting challenges
- 2025-09-02 — Shared product demo, explored use cases

**Calendar context:** Discuss pilot job descriptions and next steps for sourcing workflow. Need job descriptions by EOW to start candidate search.

**Past notes:** `file 'N5/records/meetings/2025-09-02_aniket-x-vrijen-attawar/founder_profile_summary.md'`

**Prep actions:**
1. ⚠️ Protect this time block — reschedule conflicts
2. Review last interaction and prepare 1-2 specific asks
3. Set explicit outcome: what decision or next step do you need?

---

---

## Format Breakdown

### Table of Contents
```markdown
## Today's External Stakeholder Meetings

**Total:** [N] meeting(s)

1. **[TIME]** — [TITLE] ([X] external)
2. **[TIME]** — [TITLE] ([X] external)
```

**Purpose:** Quick scan of the day's external engagements

---

### Meeting Section Header

```markdown
## [TIME] — [TITLE] (#tags)
```

**Elements:**
- **Time:** 24-hour format (HH:MM)
- **Title:** Meeting title from calendar
- **Tags:** Parsed from description (#stakeholder:TYPE #type:TYPE)

**Example:**
```markdown
## 09:00 — Aniket Partnership Follow-up (#partner type:follow-up)
```

---

### BLUF (Bottom Line Up Front)

```markdown
**BLUF:** [One-sentence objective]
```

**Purpose:** Immediately understand what this meeting should accomplish

**BLUF Types by Tag:**
- `#type:decision` → "Decision meeting: determine next steps for [topic]"
- `#type:discovery` → "Discovery: understand needs and fit for [stakeholder]"
- `#type:follow-up` → "Follow-up: advance partnership/relationship with [stakeholder]"
- `#type:coaching` → "Coaching: [topic] with [coach name]"
- `#type:sales` → "Sales: demonstrate value and address objections for [prospect]"
- Default → "Connect with [stakeholder] to [topic]"

**Example:**
```markdown
**BLUF:** Follow-up: advance partnership/relationship with Aniket
```

---

### Last 3 Interactions

```markdown
**Last 3 interactions:**
- [DATE] — [Brief context]
- [DATE] — [Brief context]
- [DATE] — [Brief context]
```

**Purpose:** Quick reminder of recent conversation history

**Data Source:** Gmail search `from:{email} OR to:{email}` (most recent 3)

**Format:** Date + brief 1-line summary of email thread

**Example:**
```markdown
**Last 3 interactions:**
- 2025-10-08 — Confirmed interest in pilot, requested job descriptions
- 2025-09-15 — Initial intro, discussed recruiting challenges
- 2025-09-02 — Shared product demo, explored use cases
```

---

### Calendar Context

```markdown
**Calendar context:** [Text from event description]
```

**Purpose:** Surface any context you added to the calendar event

**Data Source:** Calendar event description (non-tag text)

**Length:** First ~200 characters of substantive text

**Example:**
```markdown
**Calendar context:** Discuss pilot job descriptions and next steps for sourcing workflow. Need job descriptions by EOW to start candidate search.
```

---

### Past Notes

```markdown
**Past notes:** `file 'path/to/stakeholder-profile.md'`
```

**Purpose:** Link to existing stakeholder profiles or meeting notes

**Search Locations:**
- `N5/records/meetings/{folder}/stakeholder-profile.md`
- `N5/records/meetings/{folder}/INTELLIGENCE/stakeholder-profile.md`
- `N5/records/meetings/{folder}/founder_profile_summary.md`

**Matching Logic:** Email local part or name slug

**Example:**
```markdown
**Past notes:** `file 'N5/records/meetings/2025-09-02_aniket-x-vrijen-attawar/founder_profile_summary.md'`
```

---

### Prep Actions

```markdown
**Prep actions:**
1. [Specific action]
2. [Specific action]
3. [Specific action]
```

**Purpose:** Concrete, actionable prep steps

**Tag-Based Logic:**

**Priority Protection:**
```markdown
#priority:high OR #priority:protect
→ 1. ⚠️ Protect this time block — reschedule conflicts
```

**Type-Specific Actions:**
```markdown
#type:decision
→ 2. Prepare 1-page decision brief with recommendation

#type:discovery
→ 2. Prepare 3 questions to qualify fit

#type:follow-up (or default)
→ 2. Review last interaction and prepare 1-2 specific asks
```

**Always Included:**
```markdown
3. Set explicit outcome: what decision or next step do you need?
```

**Example:**
```markdown
**Prep actions:**
1. ⚠️ Protect this time block — reschedule conflicts
2. Review last interaction and prepare 1-2 specific asks
3. Set explicit outcome: what decision or next step do you need?
```

---

## What's Excluded

### Internal Meetings
```
Title: Ayush Jain and Vrijen Attawar
Attendees: ayush@mycareerspan.com, vrijen@mycareerspan.com
```
**Result:** Not included (all internal domains)

### Daily Recurring Meetings
```
Title: Daily Team Standup
Attendees: vrijen@mycareerspan.com, logan@theapply.ai
```
**Result:** Not included (matches daily pattern)

---

## Comparison: Old vs New Format

### Old Format (v1.0.1)

```markdown
## Meetings (today)

1) Ayush Jain and Vrijen Attawar
- Time: 2025-10-11 12:30–13:15 (America/New_York)
- Location: Google Meet (meet.google.com/oyv-ubnx-eva)
- Organizer: vrijen@mycareerspan.com
- Attendees: ayush@mycareerspan.com (accepted), vrijen@mycareerspan.com (organizer)
- Description notes: Calendly-managed booking; "Friends & Family Link for Vrijen" referenced; reschedule/cancel links present in description.
- Event link: https://www.google.com/calendar/event?eid=...

---

## Attendee research — ayush@mycareerspan.com
Source: recent Gmail history (10 messages found referencing Ayush + calendar invites).
- Interaction pattern: frequent calendar invites and acceptances; participant in team stand-ups and recurring check-ins.
- Recent email context: multiple accepted invites for one-off check-ins and recurring stand-ups; one thread flagged a suspicious external email that Ayush forwarded for verification.
- Internal role/context: appears to act on design/meeting coordination; uses both ayush@mycareerspan.com and a personal address (design.ayush@gmail.com) in some headers.

Caveat: public web search returned multiple people named "Ayush Jain"; internal email evidence is the authoritative source for this attendee.

---

## Suggested prep (practical)
- Confirm agenda (1–3 bullets) by replying now: "Confirming agenda + any files you'd like reviewed." Include deadline to share materials (e.g., 2 hours before meeting).
- Send 1–2 priority items in advance: current draft link, specific screenshots, or the decision you want from Ayush.
- Verify Calendly/reschedule links and Meet link are correct; pin dial-in phone number as backup.
- Set explicit timebox: 40 minutes (start/end markers) and owner for next steps.

---

## Strategic framing & goals
- Primary objective: finalize the "Friends & Family Link" deliverable and confirm next steps for implementation.
- Secondary objective: identify any blockers Ayush needs (assets, approvals, timelines).
- Triage approach: (1) Outcome, (2) Gaps, (3) Decisions required.
```

**Issues:**
- ❌ Includes internal meetings (Ayush)
- ❌ Verbose, lots of metadata
- ❌ Repeats email/calendar details
- ❌ No bottom-line-up-front summary
- ❌ Mixed strategic and tactical advice
- ❌ No chronological TOC

---

### New Format (v2.0.0)

```markdown
## Today's External Stakeholder Meetings

**Total:** 1 meeting(s)

1. **09:00** — Aniket Partnership Follow-up (1 external)

---

## 09:00 — Aniket Partnership Follow-up (#partner type:follow-up)

**BLUF:** Follow-up: advance partnership/relationship with Aniket

**Last 3 interactions:**
- 2025-10-08 — Confirmed interest in pilot, requested job descriptions
- 2025-09-15 — Initial intro, discussed recruiting challenges
- 2025-09-02 — Shared product demo, explored use cases

**Calendar context:** Discuss pilot job descriptions and next steps for sourcing workflow.

**Past notes:** `file 'N5/records/meetings/2025-09-02_aniket-x-vrijen-attawar/founder_profile_summary.md'`

**Prep actions:**
1. ⚠️ Protect this time block — reschedule conflicts
2. Review last interaction and prepare 1-2 specific asks
3. Set explicit outcome: what decision or next step do you need?
```

**Improvements:**
- ✅ External stakeholders only
- ✅ BLUF upfront (instant clarity)
- ✅ Streamlined (1/4 the length)
- ✅ Actionable (specific prep actions)
- ✅ Chronological TOC
- ✅ Tag-based intelligence
- ✅ Links to past notes
- ✅ Focus on last 3 interactions

---

## Tag System Integration

### Calendar Event Setup

**Add to event description:**
```
#stakeholder:partner #type:follow-up #priority:high

Discuss pilot job descriptions and next steps for sourcing workflow.
Need job descriptions by EOW to start candidate search.
```

### Tag Effects

**Stakeholder Type:**
- Influences research priority
- Appears in section header
- Could influence Gmail search keywords (future)

**Meeting Type:**
- Determines BLUF wording
- Customizes prep actions
- Sets context for research

**Priority Level:**
- Adds calendar protection warning
- Could trigger calendar operations (future)

---

## When You See This Digest

**Morning Email (6:30 AM ET):**
- Receive full digest in inbox
- Review external meetings for the day
- Read BLUF summaries
- Check prep actions
- Click into past notes if needed

**Time to Process:** ~2-3 minutes for quick scan, 5-10 minutes for deep prep

---

## Next Steps

1. **Start tagging calendar events** with `#stakeholder:TYPE #type:TYPE #priority:LEVEL`
2. **Receive tomorrow's digest** (2025-10-12) using new format
3. **Provide feedback** on:
   - BLUF clarity
   - Prep action usefulness
   - Tag taxonomy (especially priority levels)
   - Format conciseness
4. **Harmonize tag system** per `file 'N5/docs/calendar-tagging-system-COMPLETE.md'`

---

**This format is live and will be used starting tomorrow (Oct 12) at 6:30 AM ET.**
