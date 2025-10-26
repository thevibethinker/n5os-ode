# Phase 2 Workflow: Zo ↔ Howie Collaboration Setup

**Date:** 2025-10-11  
**Status:** Ready to execute  
**Control Model:** V approves all Howie preference changes

---

## Collaboration Model

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│   Zo    │ REQUEST │  Howie  │  ASK    │    V    │
│         ├────────>│         ├────────>│         │
│         │         │         │         │         │
│         │ UPDATE  │         │ CONFIRM │         │
│         │<────────┤         │<────────┤         │
└─────────┘         └─────────┘         └─────────┘
```

**Workflow:**
1. **Zo** requests preference change from Howie
2. **Howie** asks V for confirmation
3. **V** confirms or provides feedback
4. **Howie** updates preferences after V's approval

**Safety:** V maintains control gate on all Howie preference changes

---

## Phase 2 Execution Steps

### Step 1: V Introduces Zo to Howie ✓

**Action:** V sends intro email to Howie explaining collaboration model

**Email Script:** `file 'N5/docs/v-intro-email-zo-howie.txt'`

**What it covers:**
- What Zo does (meeting prep/research)
- What Howie does (scheduling/calendar)
- Collaboration model (request → confirm → update)
- Communication protocol ([ZO→HOWIE], CC V)
- Trust model (V has final say)

---

### Step 2: Zo Sends Request #1 to Howie

**Wait for:** V to send intro email first

**Action:** Zo sends calendar format preference change request

**Email Script:** `file 'N5/docs/zo-to-howie-request-1.txt'`

**Subject:** `[ZO→HOWIE] Preference Change Request #1: Calendar Event Description Format`

**CC:** vrijen@mycareerspan.com

**What it requests:**
- Format calendar descriptions with V-OS tags
- Tag selection guide (LD-INV, LD-HIR, etc.)
- Examples for common scenarios
- When not to use tags

**Expected flow:**
1. Zo sends request to Howie (CC V)
2. Howie reviews and asks V: "Should I implement this?"
3. V confirms
4. Howie updates preferences

---

### Step 3: Test Calendar Format

**After:** Howie confirms implementation

**Action:** V or Zo sends test scheduling request to Howie

**Verify:**
- Calendar event has V-OS tags
- Tags formatted correctly with `*` activation
- Purpose line is clear
- Conference link included

**If issues:** Zo clarifies with Howie (V confirms adjustment)

---

### Step 4: Zo Sends Request #2 to Howie

**After:** Calendar format tested successfully

**Action:** Zo sends auto-notification preference change request

**Email Script:** `file 'N5/docs/zo-to-howie-request-2.txt'`

**Subject:** `[ZO→HOWIE] Preference Change Request #2: Auto-Notify Zo When Meetings Scheduled`

**CC:** vrijen@mycareerspan.com

**What it requests:**
- Auto-send notification to va@zo.computer
- Notification format with person, date, tags, context
- When to notify (new external meetings)
- When not to notify (internal, reschedules)

**Expected flow:**
1. Zo sends request to Howie (CC V)
2. Howie reviews and asks V: "Should I implement this?"
3. V confirms
4. Howie updates preferences

---

### Step 5: Test Auto-Notification

**After:** Howie confirms implementation

**Action:** V or Zo sends test scheduling request to Howie

**Verify:**
- Notification arrives at va@zo.computer
- Subject line format correct: `[HOWIE→ZO] [NOTIFY] Meeting Scheduled: ...`
- All required fields present
- Context summary included
- V is CC'd on notification

**If issues:** Zo clarifies with Howie (V confirms adjustment)

---

### Step 6: Phase 2 Complete ✓

**Success criteria:**
- [x] Howie populates calendar with V-OS tags
- [x] Howie notifies Zo of new meetings
- [x] V receives CC of all Zo ↔ Howie emails
- [x] Test scheduling produces correct output

**Ready for Phase 3:** Zo processes notifications automatically

---

## Communication Protocol

### Subject Line Format

**Zo → Howie:**
```
[ZO→HOWIE] [TYPE] Subject
```

**Howie → Zo:**
```
[HOWIE→ZO] [TYPE] Subject
```

**Types:**
- `[REQUEST]` — Preference change requests
- `[NOTIFY]` — Event notifications
- `[CONFIRM]` — Confirmations
- `[QUERY]` — Questions
- `[UPDATE]` — Status updates

### Email Rules

**Always:**
- CC V at vrijen@mycareerspan.com
- Use bracketed subject headers
- Be clear and specific
- Include examples when relevant

**When requesting changes:**
- Explain WHY it matters
- Provide concrete examples
- State next steps clearly
- Ask Howie to confirm with V

---

## Files Reference

**Email Scripts:**
1. `file 'N5/docs/v-intro-email-zo-howie.txt'` — V introduces Zo to Howie
2. `file 'N5/docs/zo-to-howie-request-1.txt'` — Calendar format request
3. `file 'N5/docs/zo-to-howie-request-2.txt'` — Auto-notification request

**Supporting Documentation:**
- `file 'N5/docs/howie-request-1-calendar-format.txt'` — Detailed calendar format guide
- `file 'N5/docs/howie-request-2-zo-notification.txt'` — Detailed notification guide

**Phase Documentation:**
- `file 'N5/docs/PHASE-1-COMPLETE.md'` — Phase 1 summary
- `file 'N5/docs/howie-zo-implementation-plan.md'` — Full 5-phase plan

---

## What Phase 2 Enables

Once complete, the automated workflow is:

```
1. Person emails Vrijen requesting meeting
2. Howie schedules with V-OS tags in calendar description
3. Howie notifies Zo at va@zo.computer
4. Zo begins immediate research (Phase 3)
5. Zo generates daily prep digest (Phase 1 complete)
6. Vrijen receives full meeting intelligence
```

**Result:** Zero manual work for meeting prep from initial contact to brief delivery.

---

## Safety & Control

### What V Controls
- ✅ All Howie preference changes (V must confirm)
- ✅ Visibility into all Zo ↔ Howie communication (CC'd on everything)
- ✅ Override authority on any request or configuration

### What Zo Controls
- ✅ Meeting prep research and intelligence generation
- ✅ Stakeholder profile management
- ✅ Daily digest format and content

### What Howie Controls
- ✅ Calendar and scheduling logistics
- ✅ Email coordination with external parties
- ✅ Conference link generation

### Separation of Concerns
- **Howie:** Calendar logistics and external coordination
- **Zo:** Research, intelligence, and internal prep
- **V:** Final authority on all system behavior

---

## Phase 3 Preview

After Phase 2 is working, Phase 3 will enable:

1. **Automatic notification processing** — Zo monitors va@zo.computer
2. **Immediate research pipeline** — Triggered by [HOWIE→ZO] emails
3. **Gmail API integration** — Real email interaction history
4. **Progressive brief enhancement** — Research deepens as meeting approaches

**Phase 3 will NOT require Howie preference changes** — it's all on Zo's side.

---

## Timeline

**Phase 2 Estimated Time:** 1-2 hours (including testing)

**Steps:**
1. V sends intro email (5 min)
2. Zo sends Request #1 (immediate)
3. V confirms, Howie updates (5-10 min)
4. Test calendar format (5 min)
5. Zo sends Request #2 (immediate)
6. V confirms, Howie updates (5-10 min)
7. Test auto-notification (5 min)

**Plus:** Any clarification rounds if needed

---

**Status:** Ready to execute  
**Next Action:** V sends intro email to Howie  
**Control Model:** V approves all changes ✓
