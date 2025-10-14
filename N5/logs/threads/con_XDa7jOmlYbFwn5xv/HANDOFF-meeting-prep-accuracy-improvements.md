# Meeting Prep Digest — Accuracy Improvements Needed

**Thread:** con_XDa7jOmlYbFwn5xv\
**Date:** 2025-10-12\
**Status:** System works but accuracy issues identified\
**Next Thread:** Brainstorm solutions for accuracy problems

---

## System Status

✅ **Core functionality works:**

- Google Calendar API integration
- Gmail API research
- External meeting filtering
- V-OS tag parsing with asterisk activation
- BLUF generation

❌ **Critical accuracy problems identified:**

1. System makes unfounded assumptions
2. Optimizes for "looking sophisticated" over factual accuracy
3. Makes inferences that aren't supported by data

---

## Problem Examples from Testing

### Issue 1: Logan/Ilse Role Confusion

**What happened:** System guessed at coordination responsibilities without knowing actual roles

**Fix applied:** Added team info to `file N5/prefs/operations/careerspan.md` :

- Logan: Co-founder, COO, Marketing and community engagement
- Ilse: CTO, Head of AI Engineering, Technology
- Vrijen: Founder, Hiring, sales, investment

### Issue 2: "First Meeting" Assumption

**What happened:** System saw 2-3 recent Gmail results (Oct 1-2) for Michael Maher and assumed it was first meeting

**The problem:** Gmail API only returns last 3 messages. Could be years of history before that.

**Why it's bad:** System confidently stated "first substantive meeting" without verification

### Issue 3: Strategic Context Invention

**What happened:** System added elaborate strategic context that sounded authoritative but was speculation:

- "Target: Agree on Q4 pilot with 1-2 communities"
- "Focus: understand their needs and constraints to maximize mutual value"
- Detailed prep actions that assumed meeting purposes

**The problem:** These sound smart but are guesses, not facts

---

## Core Principle Violated

**V's Rule:** "You can't be optimizing for looking sophisticated over accuracy. Accuracy should always be of the highest importance unless we're writing stylistically."

**What the system did:** Added polish and elaboration at the expense of factual grounding

**What it should do:** Stick to verifiable facts, be conservative with inferences

---

## Questions for New Thread

### 1. Gmail History Problem

**Current:** Last 3 email interactions only\
**Issue:** Doesn't show full relationship history\
**Question:** How do we avoid "first meeting" assumptions?

**Options to explore:**

- Add explicit "Limited history - only showing last 3 interactions" disclaimer
- Fetch more than 3 emails when possible
- Check for date gaps that suggest earlier history
- Never make statements about "first" anything

### 2. Strategic Context Problem

**Current:** System adds elaborate prep actions and strategic framing\
**Issue:** Sounds authoritative but is speculative\
**Question:** Should we be more conservative?

**Options to explore:**

- Stick to facts only (email content, calendar description, attendee list)
- Flag inferences explicitly ("Based on email tone, this appears to be...")
- Use tag-based actions ONLY, no additional strategic interpretation
- Add confidence levels to statements

### 3. BLUF Generation Problem

**Current:** System creates stakeholder-specific BLUFs with assumed objectives\
**Issue:** May mischaracterize meeting purpose\
**Question:** How specific should BLUFs be?

**Options to explore:**

- Generic BLUFs always, unless calendar description is explicit
- Derive BLUF only from calendar description text
- Use tags for prep actions but keep BLUF neutral
- Let V write BLUFs in calendar, system just surfaces them

### 4. Model Consistency Problem

**Current:** I (Claude) generated test output, but production uses gpt-5-mini\
**Issue:** Quality/interpretation might differ significantly\
**Question:** Should we enforce consistency?

**Options to explore:**

- Test with actual gpt-5-mini model before claiming "works"
- Make Python script primary logic (consistent output regardless of model)
- Write extremely detailed instruction to constrain model behavior
- Use Claude for scheduled task instead of gpt-5-mini

---

## What We Know Works

✅ **Calendar filtering:** 100% accurate (tested with real data Oct 14-15)\
✅ **Gmail API:** Successfully fetches relevant email history\
✅ **V-OS tag parsing:** Correctly identifies tags and checks for asterisk\
✅ **External domain detection:** Correctly excludes @mycareerspan.com, @theapply.ai\
✅ **Daily recurring exclusion:** Correctly removes standup/sync meetings

---

## Test Data Available

**Real calendar data:** October 14-15, 2025

- 7 external meetings identified
- 4 stakeholders researched via Gmail
- No V-OS tags with asterisk (realistic baseline scenario)

**Test outputs generated:**

- `file N5/digests/daily-meeting-prep-2025-10-14-TEST.md`  — Baseline digest
- `file N5/digests/COMPARISON-baseline-vs-enhanced.md`  — Side-by-side comparison (has accuracy issues)

---

## Scheduled Task Configuration

**Generation Task:**

- ID: `05ec355c-4605-4b16-8298-6c1be0c91a95`
- Schedule: Daily at 10:00 AM ET
- Model: `openai:gpt-5-mini-2025-08-07`
- Output: `file N5/digests/daily-meeting-prep-{date}.md` 

**Email Task:**

- ID: `3b5d2d19-b67a-4c80-9ead-0dad451b4540`
- Schedule: Daily at 6:30 AM ET
- Model: `openai:gpt-5-mini-2025-08-07`
- Action: Read digest file and email

---

## Python Script Status

**File:** `file N5/scripts/meeting_prep_digest.py`  (v3.0.0)

**Strengths:**

- Clean logic for tag parsing
- Proper asterisk activation checking
- Good filtering functions

**Problem:**

- Has mock data for standalone use
- Can't be called directly by scheduled task
- Logic isn't being used by production system

**Question:** Should scheduled task call this script? Or is instruction-based approach fine if we fix accuracy?

---

## Priority for New Thread

1. **Solve the assumptions problem** — How to be conservative with limited data
2. **Test with production model** — Does gpt-5-mini behave differently than Claude?
3. **Define accuracy boundaries** — What inferences are acceptable vs. not?
4. **Implement solution** — Whether that's script-based, instruction-refinement, or hybrid

---

## Key Constraint

V is clear: **Accuracy &gt; Sophistication**

The system should produce less elaborate output if that's what it takes to be factually correct. A simple, accurate digest beats an impressive, speculative one.

---

**Files Modified This Thread:**

1. ✅ `file N5/prefs/operations/careerspan.md`  — Added Logan/Ilse team info
2. ✅ `file N5/scripts/meeting_prep_digest.py`  — Asterisk activation logic
3. ✅ Scheduled task instruction — Updated for asterisk respect

**Files for Review:**

- `file N5/digests/COMPARISON-baseline-vs-enhanced.md`  — Has accuracy issues, use as anti-pattern
- `file N5/digests/daily-meeting-prep-2025-10-14-TEST.md`  — Baseline test output

---

**Handoff to new thread for:** Brainstorming accuracy improvements and testing with production model