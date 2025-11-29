# Warm Intro Drafts — 2025-11-22

**Generated:** 2025-11-22 23:35:39 EST  
**Scope:** Last 30 days of [M] meetings  
**Status:** DRAFTS ONLY - Manual send required

---

## Summary

- **Meetings scanned:** 11 [M] meetings from last 30 days
- **Meetings with B07_WARM_INTRO_BIDIRECTIONAL blocks:** 0
- **Intro signals detected:** 0
- **Email pairs generated:** 0
- **New this run:** 0 (no intro signals found)

---

## Findings

### System Architecture Issue

The scheduled task expected meetings to have **B07_WARM_INTRO_BIDIRECTIONAL.md** blocks containing explicit warm introduction requests. However, the current meeting processing system generates different blocks:

**Actual blocks in meetings:**
- B01_DETAILED_RECAP.md
- B03_STAKEHOLDER_INTELLIGENCE.md (not B08)
- B05_ACTION_ITEMS.md
- B06_BUSINESS_CONTEXT.md
- B07_TONE_AND_CONTEXT.md (different from expected)
- B14_BLURBS_REQUESTED.md
- B21_KEY_MOMENTS.md
- B25_DELIVERABLES.md
- B26_MEETING_METADATA.md

**Expected blocks (per workflow instruction):**
- B07_WARM_INTRO_BIDIRECTIONAL.md ← **Missing from all meetings**
- B08_STAKEHOLDER_INTELLIGENCE.md (exists as B03 instead)
- B02_COMMITMENTS.md ← **Only found in archived meetings**

### Meetings Scanned (Last 30 Days)

1. **2025-11-21:** Konrad Kucharski x Vrijen Attawar [M] - external
2. **2025-11-21:** Team standup [M] - external  
3. **2025-11-21:** Internal team meeting [M] - external
4. **2025-11-20:** Multiple team/client meetings [M] - external
5. **2025-11-19:** NYC Founders Club dinner networking [M] - external
6. **2025-11-19:** Multiple client calls [M] - external/external_candidate

Total: 11 meetings scanned, 0 with B07_WARM_INTRO_BIDIRECTIONAL blocks

---

## Root Cause Analysis

### The B07 Block Mismatch

**Problem:** The workflow assumes meetings are processed with a B07_WARM_INTRO_BIDIRECTIONAL.md block that explicitly captures introduction requests during the meeting. This block does not exist in the current meeting intelligence generation system.

**Current state:**
- Meetings have B07_TONE_AND_CONTEXT.md instead
- No explicit warm intro tracking block
- Intro signals may exist implicitly in B01_DETAILED_RECAP or B05_ACTION_ITEMS but not structured

**What's needed:**
1. **Add B07_WARM_INTRO_BIDIRECTIONAL block to meeting processing**
   - Should extract intro signals during meeting intelligence generation
   - Format: Person A wants intro to Person B, context, status (pending/completed)
   
2. **OR: Semantic extraction from existing blocks**
   - Read B01_DETAILED_RECAP and B05_ACTION_ITEMS semantically
   - Identify mentions of: "intro", "connect", "introduce me to"
   - Extract structured data: requester → target, context, connector

### Example: Konrad Meeting

**Meeting:** 2025-11-21_Konrad_Kucharski_x_Vrijen_Attawar_[M]

**B05_ACTION_ITEMS.md contains:**
- Send follow-up email
- Draft integration plan
- Investigate webhooks

**No warm intro signals** were explicitly captured, though implicit networking opportunities might exist (Konrad's network, his company's ecosystem).

---

## Recommendations

### Short-term: Semantic Extraction Approach

Since B07_WARM_INTRO_BIDIRECTIONAL doesn't exist, modify this scheduled task to:

1. **Scan existing blocks semantically:**
   - Read B01_DETAILED_RECAP for intro mentions
   - Check B05_ACTION_ITEMS for "intro", "connect", "introduction"
   - Look for patterns: "Can you connect me to X", "I'd love an intro to Y"

2. **Generate intro drafts from implicit signals**
   - Even without structured B07 block
   - LLM-based extraction from meeting context

### Long-term: Add B07 Block to Meeting Processing

**Recommended change to meeting intelligence generation:**

Add a B07_WARM_INTRO_BIDIRECTIONAL.md block that captures:

```markdown
# Warm Introduction Signals

## Requested Introductions

### [Person A] → [Person B]
**Requester:** [Name]  
**Target:** [Name, Company, Role]  
**Connector:** [Who can make intro]  
**Context:** [Why this intro, what was discussed]  
**Status:** Pending | In Progress | Completed  
**Thrust:** Sales/Partnership | Info-Seeking | Network Access  
**Priority:** High | Medium | Low

[Repeat for each intro signal detected]

## Offered Introductions

### V → [Person C]
**Offerer:** [Who offered to make intro]  
**Target:** [Name, Company, Role]  
**Context:** [Why this would be valuable]  
**Status:** Pending | In Progress | Completed

---

**Notes:** 
- Capture both directions: intros V needs AND intros others offered to V
- Track status to avoid duplicate follow-ups
- Include enough context for email generation later
```

---

## Statistics

- **Most common intro type:** N/A (no intros detected)
- **Average intros per meeting:** 0.0
- **Meetings with no intros:** 11/11 (100%)
- **Meetings with B07_WARM_INTRO_BIDIRECTIONAL:** 0/11 (0%)

---

## Next Steps

1. **Decide on approach:**
   - **Option A:** Add B07_WARM_INTRO_BIDIRECTIONAL to meeting processing (architectural change)
   - **Option B:** Modify this scheduled task to semantically extract from existing blocks
   - **Option C:** Manually review meetings and add B07 blocks retroactively

2. **Test semantic extraction** on a sample meeting to see if implicit intro signals can be reliably detected

3. **Update scheduled task** once approach is decided

---

**REMINDER: All emails are DRAFTS. Review and send manually.**

---

## Technical Notes

**Workflow assumptions that failed:**
- ✗ B07_WARM_INTRO_BIDIRECTIONAL.md exists
- ✗ B08_STAKEHOLDER_INTELLIGENCE.md naming (exists as B03)
- ✗ B02_COMMITMENTS.md exists (missing from recent meetings)

**What actually exists:**
- ✓ B01_DETAILED_RECAP.md (rich meeting context)
- ✓ B03_STAKEHOLDER_INTELLIGENCE.md (not B08)
- ✓ B05_ACTION_ITEMS.md (may contain intro signals)
- ✓ manifest.json (meeting metadata)

**File locations checked:**
- `/home/workspace/Personal/Meetings/Inbox/*[M]*`
- 11 meeting folders scanned
- 0 B07_WARM_INTRO_BIDIRECTIONAL.md files found

**References:**
- file 'Prompts/warm-intro-generator.prompt.md' — Email generation template (loaded successfully)
- Meeting intelligence blocks — B01, B03, B05 (different structure than expected)

