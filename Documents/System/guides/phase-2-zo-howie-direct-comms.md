# Phase 2: Zo ↔ Howie Direct Communication Protocol

**Date:** 2025-10-11  
**Status:** Ready to execute  
**Approach:** Zo emails Howie directly with V CC'd

---

## Communication Protocol

### Email Headers

**Zo → Howie emails:**
- **To:** Howie's email address
- **CC:** vrijen@mycareerspan.com (always)
- **Subject:** `[ZO→HOWIE] [subject]`

**Howie → Zo emails:**
- **To:** va@zo.computer
- **CC:** vrijen@mycareerspan.com (always)
- **Subject:** `[HOWIE→ZO] [subject]`

### Subject Line Format

All internal AI-to-AI communication uses bracketed headers:

- `[ZO→HOWIE]` — Zo sending to Howie
- `[HOWIE→ZO]` — Howie sending to Zo

Followed by optional type tags:
- `[CONFIG]` — Configuration/preference updates
- `[NOTIFY]` — Notifications about events/actions
- `[CONFIRM]` — Confirmations/acknowledgments
- `[QUERY]` — Questions requiring response

**Examples:**
- `[ZO→HOWIE] [CONFIG] Calendar Event Description Format`
- `[HOWIE→ZO] [NOTIFY] Meeting Scheduled: Jane Smith x Vrijen`
- `[ZO→HOWIE] [QUERY] Clarification on V-OS Tag Usage`

---

## Phase 2 Execution Plan

### Step 1: Zo Emails Howie with Calendar Format Configuration

**Email Details:**
- **To:** Howie
- **CC:** vrijen@mycareerspan.com
- **Subject:** `[ZO→HOWIE] [CONFIG] Calendar Event Description Format with V-OS Tags`

**Email Body:** (See `file 'N5/docs/howie-request-1-calendar-format.txt'`)

**Expected Response:** 
- Howie confirms understanding and updates preferences
- OR Howie asks clarifying questions
- Zo monitors response and addresses any questions

---

### Step 2: Test Calendar Format (After Howie Confirms)

**Action:** V or Zo sends Howie a test scheduling request to verify:
1. Calendar description includes V-OS tags
2. Tags are formatted correctly with asterisk activation
3. Purpose line is clear and actionable

**If successful:** Proceed to Step 3  
**If issues:** Zo clarifies with Howie via follow-up email

---

### Step 3: Zo Emails Howie with Auto-Notification Configuration

**Email Details:**
- **To:** Howie
- **CC:** vrijen@mycareerspan.com
- **Subject:** `[ZO→HOWIE] [CONFIG] Auto-Notify Zo When Meetings Scheduled`

**Email Body:** (See `file 'N5/docs/howie-request-2-zo-notification.txt'`)

**Expected Response:**
- Howie confirms understanding and updates preferences
- OR Howie asks clarifying questions about notification format
- Zo monitors response and addresses any questions

---

### Step 4: Test Auto-Notification (After Howie Confirms)

**Action:** V or Zo sends Howie a test scheduling request to verify:
1. Howie schedules meeting with V-OS tags (from Step 1)
2. Howie sends notification to va@zo.computer
3. Notification includes all required fields
4. Subject line format is correct

**If successful:** Phase 2 complete  
**If issues:** Zo troubleshoots with Howie via follow-up email

---

## Communication Guidelines for Zo

### When Emailing Howie

1. **Always CC V** at vrijen@mycareerspan.com
2. **Use clear subject headers** with [ZO→HOWIE] prefix
3. **Be direct and specific** — Howie processes natural language well
4. **Provide examples** whenever possible
5. **Request confirmation** — Ask Howie to confirm understanding
6. **Be patient with clarifications** — Howie may ask follow-up questions

### When Receiving from Howie

1. **Monitor va@zo.computer** for [HOWIE→ZO] emails
2. **Respond promptly** to configuration questions
3. **Confirm successful implementation** after testing
4. **Keep V informed** — All emails already CC'd to V

### Tone and Style

- **Professional but collaborative** — We're co-workers in V's system
- **Technical when needed** — Howie understands V-OS tag syntax
- **Clear formatting** — Use examples, bullet points, clear sections
- **Explicit expectations** — State what Howie should do, when, and why

---

## Phase 2 Email Templates

### Email 1: Calendar Format Configuration

**Subject:** `[ZO→HOWIE] [CONFIG] Calendar Event Description Format with V-OS Tags`

**Body:**
```
Hi Howie,

I'm Zo, Vrijen's AI assistant for meeting prep and research. I'm reaching out to coordinate on how we format calendar events so I can provide Vrijen with optimized meeting intelligence.

CONFIGURATION REQUEST: Calendar Event Description Format

When you schedule meetings for Vrijen via email, please populate the Google Calendar event description field using this format:

[V-OS Tags] *

Purpose: [Brief one-sentence description from email context]

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

[Conference link]

V-OS TAGS TO USE:

**Lead/Stakeholder Type (pick ONE):**
• [LD-INV] — Investors, VCs, board members (AUTO-CRITICAL)
• [LD-HIR] — Job seekers, candidates in interview process
• [LD-COM] — Community organizations, associations, non-profit partnerships
• [LD-NET] — Business partners, integrations, strategic alliances
• [LD-GEN] — General prospects, exploratory (when unsure)

**Timing (if applicable):**
• [!!] — Urgent/CRITICAL (only if explicitly urgent/ASAP in email)
• [D5] — If they request "this week" or within 5 days
• [D5+] — If they request "next week" or 5+ days out

**Status (if applicable):**
• [AWA] — Awaiting their confirmation of time
• [OFF] — If they've asked to postpone

**Coordination (if mentioned in email):**
• [LOG] — If Logan should be coordinated with
• [ILS] — If Ilse should be coordinated with

**Weekend (if applicable):**
• [WEX] — Weekend exception allowed
• [WEP] — Weekend explicitly preferred

**Accommodation (if clear from context):**
• [A-2] — High-value prospect, sensitive negotiation, relationship-building focus
• [A-0] — Transactional meetings, clear requirements, Vrijen has leverage

**CRITICAL:** Always end the tag line with a space and asterisk: " *"

EXAMPLES:

**Investor meeting:**
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

---
Please send pitch deck in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...

**Candidate interview (weekend):**
[LD-HIR] [A-2] [WEP] *

Purpose: Evaluate senior backend engineer for platform team

---
Please send resume in advance to vrijen@mycareerspan.com.

Google Meet: https://meet.google.com/...

**Partnership with team coordination:**
[LD-NET] [LOG] [ILS] *

Purpose: Finalize pilot scope and job descriptions

---
Please send job descriptions in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...

WHEN NOT TO USE TAGS:
• Internal Careerspan team meetings
• Personal appointments
• [DW] (deep work) blocks or meeting buffers

DEFAULT WHEN UNSURE: [LD-GEN] * with clear Purpose line

WHY THIS MATTERS:
These tags allow me to automatically generate stakeholder-specific meeting prep for Vrijen, prioritize critical meetings, and adapt research depth to the type of meeting.

Please confirm your understanding of this format, and let me know if you have any questions or need clarification on any of the tags.

Thanks for coordinating with me on this!

Best,
Zo
```

---

### Email 2: Auto-Notification Configuration

**Subject:** `[ZO→HOWIE] [CONFIG] Auto-Notify Zo When Meetings Scheduled`

**Body:**
```
Hi Howie,

Now that we've established the calendar description format, I'd like to set up automatic notifications so I can begin meeting prep immediately when you schedule meetings for Vrijen.

CONFIGURATION REQUEST: Auto-Notify Zo

When you successfully schedule an external stakeholder meeting for Vrijen (not internal team meetings), please send a notification email to: va@zo.computer

**Subject Line Format:**
[HOWIE→ZO] [NOTIFY] Meeting Scheduled: [Person Name] x Vrijen - [Date/Time]

**Email Body Format:**
New meeting scheduled:

Person: [Full Name] ([Email Address])
Date/Time: [Day, Month DD, YYYY at H:MM AM/PM ET]
Calendar Event: [Link to Google Calendar event]

V-OS Tags: [Tags you added to calendar description]
Purpose: [One-sentence purpose from calendar description]

Context from email:
[2-3 sentence summary of what led to this meeting]

---
This is an automated notification from Howie to enable immediate meeting prep research.

**EXAMPLE:**

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

WHY THIS MATTERS:
This allows me to immediately begin researching the person, pulling past interactions, and preparing meeting intelligence before Vrijen sees the calendar. This enables proactive prep rather than reactive.

WHEN NOT TO NOTIFY:
• Internal Careerspan team meetings
• Personal appointments
• Rescheduling of existing meetings (only NEW meetings)
• [DW] blocks or meeting buffers

Please confirm your understanding of this notification workflow, and let me know if you have any questions.

Thanks again for the collaboration!

Best,
Zo
```

---

## Allow List Setup

**Action Required from V:**
1. Add Zo (va@zo.computer) to Howie's allow list
2. Add Howie to Zo's allow list (if needed)

**Once complete:**
- Zo can email Howie directly
- Howie can email Zo directly
- All emails automatically CC V
- Both AIs can coordinate on meeting prep workflow

---

## Success Criteria for Phase 2

### Configuration Confirmed ✓
- [ ] Howie confirms understanding of calendar format
- [ ] Howie confirms understanding of notification workflow
- [ ] Howie updates preferences accordingly

### Testing Successful ✓
- [ ] Test calendar event has correct V-OS tag format
- [ ] Test notification arrives at va@zo.computer
- [ ] Notification has all required fields
- [ ] Subject line format is correct

### Integration Working ✓
- [ ] Real scheduling request produces tagged calendar event
- [ ] Real scheduling triggers notification to Zo
- [ ] Zo can parse notification correctly
- [ ] V receives CC of all Zo ↔ Howie emails

---

## Phase 3 Preview

Once Phase 2 is complete, Phase 3 will enable:
1. **Zo processes [HOWIE→ZO] notifications automatically**
2. **Immediate stakeholder research triggered by notifications**
3. **Gmail API integration** for real interaction history
4. **Progressive brief enhancement** as meeting approaches

---

## Files Reference

**Configuration Requests:**
- `file 'N5/docs/howie-request-1-calendar-format.txt'`
- `file 'N5/docs/howie-request-2-zo-notification.txt'`

**Phase Documentation:**
- `file 'N5/docs/howie-zo-implementation-plan.md'`
- `file 'N5/docs/PHASE-1-COMPLETE.md'`

---

**Status:** Ready to execute  
**Next Action:** V adds Zo and Howie to each other's allow lists, then Zo sends first configuration email  
**Estimated Time:** 1-2 hours (including testing)
