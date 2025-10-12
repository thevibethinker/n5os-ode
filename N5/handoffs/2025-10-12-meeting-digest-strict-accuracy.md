# Thread Handoff: Meeting Digest Strict Accuracy Implementation

**From Thread:** con_JK1EcL1HMPhV6m8H  
**Date:** 2025-10-12  
**Status:** Ready for dry-run testing  
**Next Thread:** Test digest generation with real calendar data

---

## Summary: What Was Accomplished

### 1. ✅ Updated Architectural Principles
**File:** `file 'Knowledge/architectural/operational_principles.md'`

**Change:** Added Section 0.1 — "LLM-First for Analysis and Synthesis"

**Purpose:** Establish system-wide principle that LLM reasoning should be default for analysis, synthesis, and problem-solving. Scripts/templates are for technical execution only.

**Key rule:** "If the task involves understanding, evaluating, or synthesizing information, use LLM capabilities directly rather than creating fill-in-the-blank frameworks."

---

### 2. ✅ Updated Scheduled Task with Strict Accuracy Rules
**Task ID:** `05ec355c-4605-4b16-8298-6c1be0c91a95`  
**Schedule:** Daily at 10:00 AM ET  
**Model:** openai:gpt-5-mini-2025-08-07

**Critical Change:** Rewrote instruction to enforce strict accuracy constraints:

#### Accuracy Rules Implemented:
1. **No relationship status claims** — Never say "first meeting" when Gmail only returns 3 messages
2. **No invented objectives** — Quote calendar description verbatim or state "No meeting objective documented"
3. **No generic prep actions** — Only context-specific guidance; if no context, state "Clarify objective"
4. **No tone interpretation** — Direct quotes only, never characterize as "enthusiastic" or "interested"
5. **Explicit data limitations** — Always flag Gmail 3-message limit

#### V-OS Tags Handling:
- **Asterisk activation is Howie-only** — Zo ignores asterisk, always processes V-OS tags when present
- Tags provide stakeholder type (LD-INV, LD-COM, etc.), timing (D5, D10), coordination (LOG, ILS)

---

### 3. ❌ Script NOT Yet Updated (Pending)
**File:** `file 'N5/scripts/meeting_prep_digest.py'` (v3.0.0)

**Known Issues:**
1. Still has asterisk activation logic (lines checking `tags['active']`)
2. Generates generic prep actions when tags inactive
3. BLUF generation may not follow strict accuracy rules

**Why Not Critical Yet:**
- Scheduled task uses LLM instruction-based generation, not script
- Script is for standalone/testing use only
- Once we validate LLM approach works, we'll align script or deprecate it

---

## Problem Statement (Context)

Meeting prep digest system was generating **sophisticated-sounding but speculative output**:
- Claimed "first meeting" when only seeing 2-3 Gmail results
- Invented strategic objectives not stated in calendar
- Added generic prep advice that could apply to any meeting
- Interpreted tone ("enthusiastic", "interested") from minimal data

**V's Core Principle Violated:** "Accuracy over sophistication. Simple and correct beats elaborate and wrong."

---

## Solution Implemented

### Strict Accuracy Mode for gpt-5-mini

**Five Inviolable Rules:**

1. **Gmail Limitation Transparency**
   - ❌ "This appears to be first meeting"
   - ✅ "Email history: 2 messages found (Oct 1-2). Last 3 interactions (max returned by API). Earlier history may exist."

2. **Calendar-Only BLUFs**
   - ❌ "Discuss partnership progress and next steps" (invented)
   - ✅ "No meeting objective documented in calendar" OR quote description verbatim

3. **Context-Specific Prep Only**
   - ❌ "Review last interaction and prepare 1-2 specific asks" (generic template)
   - ✅ "Email mentions 'Q4 pilot communities' - prepare response" OR "Clarify meeting objective (not documented)"

4. **No Tone Interpretation**
   - ❌ "Fei is engaged and enthusiastic"
   - ✅ "Fei wrote: 'awesome ! Look forward'" (direct quote only)

5. **Explicit Gaps**
   - Always include "What's documented" vs "What's unclear" sections
   - Flag missing data: "No stakeholder profile found", "Meeting purpose not stated"

---

## V-OS Tag System (Reference)

**Tag Categories:**
- **Lead types:** [LD-INV] investor, [LD-HIR] hiring, [LD-COM] community, [LD-NET] networking, [LD-GEN] general
- **Timing:** [!!] urgent, [D5] within 5 days, [D10] within 10 days
- **Coordination:** [LOG] Logan coordinates, [ILS] Ilse coordinates
- **Status:** [OFF] postponed, [AWA] awaiting, [TERM] inactive

**Asterisk Rule for Zo:**
- **Ignore asterisk entirely** — that's a Howie activation signal
- **Always process V-OS tags when present** in calendar description

---

## Test Data Available

**Real calendar data:** October 14-15, 2025
- 7 external meetings
- 4 stakeholders researched via Gmail
- Mix of meetings with/without V-OS tags

**Test outputs (from previous thread):**
- `file 'N5/digests/daily-meeting-prep-2025-10-14-TEST.md'` — Baseline (has accuracy issues)
- `file 'N5/digests/COMPARISON-baseline-vs-enhanced.md'` — Empty file

---

## Next Steps for New Thread

### 1. Run Dry-Run Test
Generate digest for tomorrow's calendar (or use Oct 14-15 test date) to validate strict accuracy mode.

**Command for testing:**
```
Generate meeting prep digest for [date] using the updated strict accuracy instruction. 
Review output against the 5 inviolable rules.
```

### 2. Check Output Quality
Verify each meeting section has:
- ✅ No "first meeting" claims
- ✅ BLUF derived from calendar or explicitly states absence
- ✅ Context-specific prep OR "clarify objective" statement
- ✅ Direct quotes only, no tone interpretation
- ✅ Gmail limitations flagged

### 3. If Output is Good
- Mark system as production-ready
- Next scheduled run: Tomorrow 10:00 AM ET
- Monitor for accuracy over first few days

### 4. If Output Still Has Issues
- Consider moving to hybrid approach (script handles data, LLM does minimal synthesis)
- Or use Claude for scheduled task instead of gpt-5-mini
- Or add even more constraint/examples to instruction

---

## Files Modified This Thread

1. ✅ `Knowledge/architectural/operational_principles.md` — Added LLM-First principle
2. ✅ Scheduled task `05ec355c-4605-4b16-8298-6c1be0c91a95` — Updated instruction to strict accuracy mode
3. ⏳ `N5/scripts/meeting_prep_digest.py` — Needs alignment (not blocking)

---

## Key Constraint for All Future Work

**V's Rule:** "Accuracy over sophistication. Simple and correct beats elaborate and wrong."

Any digest generation must prioritize:
1. Factual correctness over impressive-sounding synthesis
2. Explicit gap-flagging over gap-filling with speculation
3. Conservative interpretation over confident inference

---

## Team Context Added

**File:** `file 'N5/prefs/operations/careerspan.md'`

Confirmed team roles for V-OS tag coordination:
- **Logan:** Co-founder, COO — Marketing and community engagement
- **Ilse:** CTO, Head of AI Engineering — Technology
- **Vrijen (V):** Founder — Hiring, sales, investment

When [LOG] tag appears → Logan coordinates  
When [ILS] tag appears → Ilse coordinates

---

**Handoff complete. Ready for dry-run test in new thread.**
