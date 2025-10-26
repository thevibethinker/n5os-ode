# Howie Phase 2 Preference Updates

**Date:** 2025-10-11  
**Goal:** Enable Howie to populate V-OS tags and notify Zo of scheduled meetings  
**Approach:** Submit 2 focused requests to Howie

---

## Request 1: Calendar Event Description Format with V-OS Tags

### When This Applies
When scheduling ANY meeting for Vrijen via email.

### What to Do
Populate the Google Calendar event description field with this exact format:

```
[V-OS Tags] *

Purpose: [Brief one-sentence description from email context]

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

[Conference link]
[Rescheduling link if requested]
```

### V-OS Tags to Use

**Lead/Stakeholder Type (pick ONE):**
- `[LD-INV]` — Investors, VCs, board members from investor firms (AUTO-CRITICAL)
- `[LD-HIR]` — Job seekers, candidates in interview process
- `[LD-COM]` — Community organizations, associations, non-profit partnerships
- `[LD-NET]` — Business partners, integrations, strategic alliances
- `[LD-GEN]` — General prospects, cold outbound, exploratory (when unsure)

**Timing (pick ONE if applicable):**
- `[!!]` — Urgent/CRITICAL (only if explicitly stated as urgent, time-sensitive, or ASAP)
- `[D5]` — If they request "this week" or "within 5 days"
- `[D5+]` — If they request "next week" or 5+ days out
- `[D10]` — If they request "in a couple weeks" or 10+ days out

**Status (only if applicable):**
- `[AWA]` — If you're awaiting their confirmation of time
- `[OFF]` — If they've asked to postpone/reschedule to later date

**Coordination (only if mentioned in email):**
- `[LOG]` — If Logan should be coordinated with
- `[ILS]` — If Ilse should be coordinated with

**Weekend (only if applicable):**
- `[WEX]` — If they've agreed to weekend but it's an exception
- `[WEP]` — If they explicitly prefer weekend meetings

**Accommodation Level (pick ONE if clear from context):**
- `[A-2]` — High-value prospects, sensitive negotiations, relationship-building focus
- `[A-1]` — Standard meetings (default, can omit)
- `[A-0]` — Transactional meetings, when Vrijen has leverage, clear requirements

**CRITICAL:** Always end the tag line with a space and asterisk: ` *`

### Examples

**Example 1: Investor Meeting**
```
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline and terms

---
Please send pitch deck in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...
```

**Example 2: Candidate Interview (Weekend)**
```
[LD-HIR] [A-2] [WEP] *

Purpose: Evaluate senior backend engineer for platform team

---
Please send resume in advance to vrijen@mycareerspan.com.

Google Meet: https://meet.google.com/...
```

**Example 3: Partnership with Coordination**
```
[LD-NET] [LOG] [ILS] *

Purpose: Finalize pilot scope and job descriptions

---
Please send job descriptions in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...
```

**Example 4: Urgent Community Meeting**
```
[!!] [LD-COM] *

Purpose: Critical partnership decision for Q1 launch

---
Google Meet: https://meet.google.com/...
```

### When NOT to Use Tags
- Internal meetings (Careerspan team only)
- Personal appointments
- Blocks marked as `[DW]` (deep work)
- Meeting buffers

### Default When Unsure
If you're uncertain which stakeholder type, use `[LD-GEN] *` with a clear Purpose line.

---

## Request 2: Auto-Notify Zo When Meetings Scheduled

### When This Applies
Immediately after successfully scheduling ANY external stakeholder meeting for Vrijen (not internal team meetings).

### What to Do
Send a notification email to: **va@zo.computer**

**Subject Line Format:**
```
[HOWIE→ZO] [NOTIFY] Meeting Scheduled: [Person Name] x Vrijen - [Date/Time]
```

**Email Body Format:**
```
New meeting scheduled:

Person: [Full Name] ([Email Address])
Date/Time: [Day, Month DD, YYYY at H:MM AM/PM ET]
Calendar Event: [Link to Google Calendar event]

V-OS Tags: [Tags you added to calendar]
Purpose: [One-sentence purpose from calendar description]

Context from email:
[2-3 sentence summary of what led to this meeting]

---
This is an automated notification from Howie to enable immediate meeting prep research.
```

**Example Notification:**
```
Subject: [HOWIE→ZO] [NOTIFY] Meeting Scheduled: Jane Smith x Vrijen - Oct 15, 2025 2:00 PM

New meeting scheduled:

Person: Jane Smith (jane@acmeventures.com)
Date/Time: Wednesday, October 15, 2025 at 2:00 PM ET
Calendar Event: [Google Calendar link]

V-OS Tags: [LD-INV] [D5+] *
Purpose: Discuss Series A funding timeline and terms

Context from email:
Jane replied to the intro from Mike, expressed strong interest in Careerspan's traction in the ed-tech space. She requested a meeting to discuss funding timeline and what terms structure might look like for Series A.

---
This is an automated notification from Howie to enable immediate meeting prep research.
```

### Why This Matters
This allows Zo to immediately begin:
1. Researching the person and their organization
2. Pulling past email interactions
3. Checking for existing stakeholder profiles
4. Preparing meeting intelligence before Vrijen sees the calendar

### When NOT to Notify
- Internal Careerspan team meetings
- Personal appointments
- Rescheduling of existing meetings (only NEW meetings)
- Meetings marked with `[DW]` or "buffer"

---

## How to Submit These Requests

### Recommended Approach
1. Submit **Request 1 (Calendar Format)** first
2. Wait for Howie's confirmation and any clarifying questions
3. Then submit **Request 2 (Auto-Notify)** once calendar format is working
4. Test with a mock scheduling scenario

### Testing After Implementation
After Howie confirms these changes:
1. Send Howie a test email asking to schedule a mock meeting
2. Verify calendar description has V-OS tags with asterisk
3. Verify Zo receives notification at va@zo.computer
4. Check that Zo can parse the notification correctly

---

## What This Enables

Once implemented, the workflow becomes:
1. **Person emails** requesting meeting with Vrijen
2. **Howie schedules** and populates calendar with V-OS tags
3. **Howie notifies Zo** at va@zo.computer
4. **Zo immediately begins research** (Phase 3)
5. **Vrijen gets daily digest** with full prep (existing Phase 1)

This creates a **fully automated meeting intelligence pipeline** from first contact to prep delivery.

---

## Future Phase 3 (Not Included in These Requests)

After Phase 2 is working, we'll enable:
- Zo processing [HOWIE→ZO] notifications automatically
- Immediate stakeholder research triggered by notifications
- Real-time Gmail integration for interaction history
- Progressive brief enhancement as meeting approaches

---

**Status:** Ready to submit to Howie  
**Priority:** High (enables full Howie-Zo integration)  
**Dependencies:** Phase 1 complete ✓
