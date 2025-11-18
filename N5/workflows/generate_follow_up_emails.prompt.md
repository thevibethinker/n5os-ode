---
created: 2025-11-17
last_edited: 2025-11-17
version: 3.0
title: Follow-Up Email Generator v3.0
description: Generate follow-up emails for meetings in [P] state using semantic classification
tags: [workflow, email, meetings, automation, semantic-analysis]
tool: true
---

# Follow-Up Email Generator v3.0

**Purpose:** Generate follow-up emails for meetings using semantic classification  
**Key Principle:** Scripts = Mechanics | LLM = Semantics | Never confuse the two

---

## Execution Protocol

### STEP 1: Find [P] Meetings (Mechanical)

```bash
find /home/workspace/Personal/Meetings/Inbox -type d -name "*[P]"
```

### STEP 2: Classify Each Meeting (Semantic - LLM Does This)

For each [P] meeting:

1. **Load raw data using script:**
   ```bash
   python3 /home/workspace/N5/scripts/follow_up_email_classifier.py "<meeting_folder>"
   ```

2. **LLM reads and understands:**
   - B26: Meeting metadata (participants, type, context)
   - B02: Commitments/deliverables (internal vs external)
   - B08: Stakeholder intelligence (external parties involved)
   - B01: Detailed recap (meeting substance)

3. **LLM makes semantic judgment:**
   - **Who attended?** External stakeholders or internal-only?
   - **Meeting type?** Client meeting, coaching, planning, standup?
   - **Deliverables?** To external parties, to internal team, or none?
   - **Context understanding?** What was this meeting actually about?

4. **Classification Decision:**

```yaml
DEFINITELY_YES:
  - External stakeholders present AND has deliverables
  - Coaching/advisory session with external party
  - Client presentation or workshop
  - Event with external attendees
  
PROBABLY_YES:
  - External stakeholders present (even without explicit deliverables)
  - Follow-up conversations needed (from B08)
  
PROBABLY_NO:
  - Internal-only with only internal deliverables
  - Planning session (no external parties)
  
DEFINITELY_NO:
  - Daily standup or quick sync
  - Internal-only meeting with no deliverables
  - FOLLOW_UP_EMAIL.md already exists
  
SKIP:
  - Missing critical intelligence blocks (B26, B02)
  - Incomplete meeting processing
```

5. **Document reasoning:**
```json
{
  "meeting": "folder_name",
  "needs_follow_up_email": true/false,
  "reason": "Clear explanation of why",
  "participants": ["list of people"],
  "participant_types": "external/internal/mixed",
  "meeting_type": "coaching/client/planning/standup/etc",
  "deliverables": "external/internal/none",
  "confidence": "high/medium/low"
}
```

### STEP 3: Generate Emails (Semantic - Vibe Writer)

For each meeting where `needs_follow_up_email: true`:

1. **Switch to Vibe Writer persona**
2. **Execute Follow-Up Email Generator v2.0:**
   - PHASE 1: Harvest (extract from B25, B02, B26, B01)
   - PHASE 2: Voice transformation (V's authentic style)
   - PHASE 3: Structure (greeting, context, deliverables, next steps)
   - PHASE 4: Quality validation (≥90/100 score)
3. **Save as FOLLOW_UP_EMAIL.md in meeting folder**

### STEP 4: Report Completion

```markdown
## Follow-Up Email Generation Report

**Meetings Scanned:** X
**Classified as needing emails:** Y
**Emails generated:** Z
**Skipped (already exist):** W

### Classification Decisions:
1. [Meeting Name]
   - Decision: YES/NO
   - Reason: [explanation]
   - Confidence: high/medium/low

### Emails Generated:
1. [Meeting Name] - Score: X/100
2. [Meeting Name] - Score: Y/100
```

---

## Critical Rules

**✓ DO:**
- Read actual meeting content (B26, B02, B08, B01)
- Make semantic judgment based on understanding
- Document reasoning for each classification
- Use Vibe Writer for actual email generation
- Track all deliverables (internal + external), note type

**✗ DON'T:**
- Trust mechanical pattern matching (grep "Follow-Up Email Needed")
- Use stub/backfilled B25 files for classification
- Skip reading meeting context
- Assume internal-only meetings never need follow-ups
- Generate emails without semantic understanding

---

## Anti-Patterns to Avoid

**P0.1 Violation:** Using scripts for semantic analysis  
**P15 Violation:** Claiming "done" without processing all meetings  
**P19 Violation:** Silently failing when intelligence blocks missing

---

## Quality Gates

**Before classification:**
- [ ] Loaded actual meeting content (not just B25)
- [ ] Understood who attended
- [ ] Understood meeting type
- [ ] Judging semantically, not pattern-matching

**Before generation:**
- [ ] Switched to Vibe Writer
- [ ] Following v2.0 email generation protocol
- [ ] Loading real intelligence blocks
- [ ] Applying voice transformation

**Before reporting:**
- [ ] All meetings classified with reasoning
- [ ] All emails scored
- [ ] Honest progress reported (X/Y done)

---

*v3.0 | 2025-11-17 | Semantic-First Architecture*

