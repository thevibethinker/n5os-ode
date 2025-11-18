---
created: 2025-11-16
last_edited: 2025-11-16
version: 2
---
# B25: DELIVERABLE_CONTENT_MAP (v2 - Intelligence Only)

**Block ID:** B25  
**Name:** DELIVERABLE_CONTENT_MAP  
**Type:** REQUIRED (intelligence extraction)  
**Priority:** Generate for every meeting  
**Length:** 100-200 words

---

## Purpose

**Intelligence extraction ONLY.** Map what deliverables, resources, or materials were promised during the meeting, by whom, and when.

**NOTE:** This block does NOT generate the follow-up email. Email generation happens in Pipeline 2 (Communications Generator) with full Careerspan context from Knowledge/current/.

---

## When To Generate

**Always generate** for every meeting. Even if no deliverables were promised, note that explicitly.

---

## Structure

### Simple Table Format

```markdown
# B25: DELIVERABLE_CONTENT_MAP

## Deliverables Promised

| Item | Promised By | To Whom | Due Date | Status | Notes |
|------|-------------|---------|----------|--------|-------|
| [What] | [V or Other Party] | [Recipient] | [Date/Timeline] | [Pending/Complete] | [Context] |
| [What] | [V or Other Party] | [Recipient] | [Date/Timeline] | [Pending/Complete] | [Context] |

## Follow-Up Email Needed?

[YES/NO] - If yes, Communications Generator will create FOLLOW_UP_EMAIL.md
```

---

## Field Definitions

**Item:**
- Specific deliverable, resource, or material
- E.g., "Intro to Sarah Chen", "Deck with traction metrics", "Calendar link", "Pilot pricing proposal"

**Promised By:**
- Who committed to delivering this
- Options: "V", "Other Party Name", "Mutual"

**To Whom:**
- Who will receive this
- Name or role

**Due Date:**
- Specific date if mentioned
- Or timeline: "This week", "Before next meeting", "ASAP"
- Or "No deadline specified"

**Status:**
- **Pending:** Not yet delivered
- **Complete:** Already sent/done
- **Blocked:** Waiting on something

**Notes:**
- Brief context or dependencies
- E.g., "Waiting for Q4 numbers", "Depends on legal review", "Intro to be made via email"

---

## Example Output

```markdown
# B25: DELIVERABLE_CONTENT_MAP

## Deliverables Promised

| Item | Promised By | To Whom | Due Date | Status | Notes |
|------|-------------|---------|----------|--------|-------|
| Warm intro to Bennett Lee (Product Lead) | V | Jennifer Wu | By Friday (Nov 22) | Pending | For marketplace integration discussion |
| Send deck with enterprise case studies | V | Michael Torres | This week | Pending | He'll forward to Roelof |
| Share Q3 retention metrics | V | Michael Torres | ASAP | Blocked | Waiting on finalized numbers from analytics team |
| Calendar link for follow-up call | Jennifer Wu | V | During call | Complete | Link shared via Zoom chat |
| Connect with portfolio company CFO | Michael Torres | V | Next 2 weeks | Pending | CFO interested in career pathing for finance team |

## Follow-Up Email Needed?

YES - V has 3 pending deliverables to send. Communications Generator will create send-ready email.
```

---

## Example (No Deliverables)

```markdown
# B25: DELIVERABLE_CONTENT_MAP

## Deliverables Promised

| Item | Promised By | To Whom | Due Date | Status | Notes |
|------|-------------|---------|----------|--------|-------|
| None | - | - | - | - | Pure discovery call, no commitments made |

## Follow-Up Email Needed?

NO - No deliverables to send. Standard "nice to meet you" email can be sent manually if desired.
```

---

## What NOT To Include

**Do NOT include:**
- The actual follow-up email text (that's Pipeline 2)
- Detailed email content or structure
- Blurb generation details (that's B14)
- Your opinion on what to say in the email

**This block is pure intelligence extraction.** It answers: "What did we promise to deliver?" The Communications Generator will handle email creation.

---

## Validation Checklist

Before marking complete, verify:
- [ ] Table has all promised deliverables (or explicitly notes "None")
- [ ] Each row has all 6 fields filled
- [ ] Status is accurate (Pending/Complete/Blocked)
- [ ] Follow-up email flag is clearly YES or NO
- [ ] No email content included (intelligence only)
- [ ] Length is 100-200 words

---

## Relationship to Other Blocks

**Triggers Pipeline 2:**
- When B25 exists AND "Follow-Up Email Needed = YES" → Communications Generator creates FOLLOW_UP_EMAIL.md
- State transition: [P] → [R] after email generated

**Related Blocks:**
- **B02 (COMMITMENTS_CONTEXTUAL):** Internal action items (B25 is external deliverables)
- **B07 (WARM_INTRO_BIDIRECTIONAL):** Specific to introductions
- **B14 (BLURBS_REQUESTED):** Specific to blurbs/materials

**Key Difference:**
- **B02:** What V needs to DO (tasks, decisions, internal)
- **B25:** What V needs to SEND (deliverables, resources, external)

---

## Migration Notes

**Changed from v1:**
- **Removed:** Follow-up email generation (moved to Communications Generator)
- **Simplified:** Now pure deliverables tracking
- **Reduced:** Target length from 300-700 to 100-200 words
- **Changed format:** Table-only (no email section)
- **Added:** "Follow-Up Email Needed?" flag to trigger Pipeline 2

**Why the change:**
- Email generation needs Careerspan context from Knowledge/current/
- Email needs stakeholder intelligence from B08 for personalization
- Separates fact extraction (fast, efficient) from content creation (powerful model, rich context)
- Improves email quality by giving it dedicated focus

---

**Version:** 2.0 (Intelligence-Only)  
**Date:** 2025-11-16  
**Replaces:** B25 v1 (mixed intelligence + email generation)

*Part of Communications Architecture v2*

