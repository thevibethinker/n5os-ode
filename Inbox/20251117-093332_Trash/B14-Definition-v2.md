---
created: 2025-11-16
last_edited: 2025-11-16
version: 2
---
# B14: BLURBS_REQUESTED (v2 - Intelligence Only)

**Block ID:** B14  
**Name:** BLURBS_REQUESTED  
**Type:** CONDITIONAL (intelligence extraction)  
**Priority:** Generate when blurbs/descriptions/materials are explicitly requested  
**Length:** 100-200 words

---

## Purpose

**Intelligence extraction ONLY.** Track what blurbs, descriptions, one-pagers, or materials were explicitly requested during the meeting, by whom, and for what purpose.

**NOTE:** This block does NOT generate the actual blurbs. Blurb generation happens in Pipeline 2 (Communications Generator) with full Careerspan context from Knowledge/current/.

---

## When To Generate

**Required when:**
- Other party explicitly asks for: blurbs, descriptions, one-pagers, executive summaries, pitch materials, or similar
- Promise made to send written materials about Careerspan
- Specific request for "something I can share with [person/team]"

**NOT required when:**
- Only verbal introductions discussed (use B07 instead)
- General "let's stay in touch" (use B25 instead)
- No specific written materials requested

---

## Structure

### Simple List Format

```markdown
# B14: BLURBS_REQUESTED

## Requested Materials

1. **[Type of Material]**
   - **Requested by:** [Name/Role]
   - **Purpose:** [What they want to do with it]
   - **Target audience:** [Who will read it]
   - **Deadline:** [If specified]
   - **Key focus:** [What to emphasize]

2. **[Type of Material]**
   - **Requested by:** [Name/Role]
   - **Purpose:** [What they want to do with it]
   - **Target audience:** [Who will read it]
   - **Deadline:** [If specified]
   - **Key focus:** [What to emphasize]

[Repeat for each request]
```

---

## Field Definitions

**Type of Material:**
- Be specific: "One-pager about Careerspan for investors", "2-sentence blurb for intro email", "Executive summary for board deck"
- Use exact language from meeting if possible

**Requested by:**
- Name and role of person requesting
- E.g., "Sarah Chen, VP Partnerships"

**Purpose:**
- Why they want this material
- E.g., "To brief her CEO before intro call", "To include in investor deck", "To forward to portfolio company"

**Target audience:**
- Who will ultimately read/see this
- E.g., "C-level executives at enterprise companies", "Seed-stage founders", "HR tech investors"

**Deadline:**
- If explicitly mentioned, note it
- If not mentioned, write "Not specified"

**Key focus:**
- What specific aspects to emphasize
- E.g., "Focus on enterprise scalability", "Emphasize founder experience", "Highlight recent traction"

---

## Example Output

```markdown
# B14: BLURBS_REQUESTED

## Requested Materials

1. **One-pager about Careerspan for investor intro**
   - **Requested by:** Michael Torres, Partner at Sequoia
   - **Purpose:** To share with Roelof Botha before warm intro call
   - **Target audience:** Top-tier VC partner evaluating consumer/career tech
   - **Deadline:** By Friday (Nov 22)
   - **Key focus:** Emphasize founder track record + early traction + market timing

2. **2-3 sentence blurb for LinkedIn intro post**
   - **Requested by:** Jennifer Wu, CMO at Lattice
   - **Purpose:** To tag Careerspan when she shares post about career development trends
   - **Target audience:** Her 15K followers (mostly HR/talent leaders)
   - **Deadline:** Not specified (she's drafting post this week)
   - **Key focus:** Keep conversational, emphasize practical value for working professionals
```

---

## What NOT To Include

**Do NOT include:**
- The actual generated blurbs (that's Pipeline 2)
- Email text or follow-up content (that's B25/Pipeline 2)
- Your speculation about what blurbs should say
- Warm intro details (that's B07)

**This block is pure intelligence extraction.** It answers: "What written materials were requested and why?" The Communications Generator will handle creation.

---

## Validation Checklist

Before marking complete, verify:
- [ ] Each request has all 5 fields filled
- [ ] Type of material is specific and actionable
- [ ] Purpose explains why they want it
- [ ] Target audience is clear
- [ ] No actual blurb content included (intelligence only)
- [ ] Length is 100-200 words

---

## Relationship to Other Blocks

**Triggers Pipeline 2:**
- When B14 exists → Communications Generator creates BLURBS_GENERATED.md
- State transition: [P] → [R] after blurbs generated

**Related Blocks:**
- **B07 (WARM_INTRO_BIDIRECTIONAL):** For verbal introductions
- **B25 (DELIVERABLE_CONTENT_MAP):** For non-blurb deliverables
- **B27 (KEY_MESSAGING):** For strategic talking points (not external materials)

---

## Migration Notes

**Changed from v1:**
- **Removed:** Blurb generation (moved to Communications Generator)
- **Simplified:** Now pure intelligence extraction
- **Reduced:** Target length from 150-300 to 100-200 words
- **Added:** Explicit note that actual generation happens in Pipeline 2

**Why the change:**
- Blurb generation needs Careerspan context from Knowledge/current/
- Separates fact extraction (fast, efficient) from content creation (powerful model, rich context)
- Improves quality by giving communications dedicated focus

---

**Version:** 2.0 (Intelligence-Only)  
**Date:** 2025-11-16  
**Replaces:** B14 v1 (mixed intelligence + generation)

*Part of Communications Architecture v2*

