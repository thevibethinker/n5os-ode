---
created: 2025-11-17
last_edited: 2025-11-25
version: 3.1
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

### STEP 1: Find [P] Meetings (Mechanical, then select ONE)

```bash
find /home/workspace/Personal/Meetings/Inbox -type d -name "*[P]"
```

From this list, **select exactly one meeting per MG-5 run**:

- Candidate set: folders in `Personal/Meetings/Inbox` with suffix `_[P]` where:
  - `FOLLOW_UP_EMAIL.md` does **not** exist in the meeting folder **OR**
  - `manifest.json.system_states.follow_up_email.status` != `complete`.
- **Selection rule:** choose the **oldest** such meeting (by meeting date in folder name or filesystem mtime).

> MG-5 is *single-email-per-run*. Do **not** batch across multiple meetings in one invocation.

Let `TARGET_MEETING` be the single folder you selected.

### STEP 2: Classify Selected Meeting (Semantic - LLM Does This)

For **TARGET_MEETING** only:

1. **Load raw data using script:**
   ```bash
   python3 /home/workspace/N5/scripts/follow_up_email_classifier.py "<TARGET_MEETING>"
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
  - FOLLOW_UP_EMAIL.md already exists **and** manifest follow_up_email.status = complete
  
SKIP:
  - Missing critical intelligence blocks (B26, B02)
  - Incomplete meeting processing
```

5. **Document reasoning for TARGET_MEETING only:**
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

### STEP 3: Generate Email for TARGET_MEETING (Semantic - Vibe Writer)

If `needs_follow_up_email: true` for **TARGET_MEETING**:

1. **Set manifest state to in_progress (Mechanical):**
   ```bash
   # If an older FOLLOW_UP_EMAIL.md exists, rename to FOLLOW_UP_EMAIL_v0.md first
   python3 /home/workspace/N5/scripts/manifest_state_updater.py "<TARGET_MEETING>" follow_up_email in_progress \
     --output-file FOLLOW_UP_EMAIL_v0.md --task-name MG-5
   ```
   - If no prior file exists, you may omit `--output-file` or use `FOLLOW_UP_EMAIL.md`.

2. **Switch to Vibe Writer persona**

3. **Execute Follow-Up Email Generator v2.0 for TARGET_MEETING only:**
   - PHASE 1: Harvest (extract from B25, B02, B26, B01)
   - PHASE 2: Voice transformation (V's authentic style)
   - PHASE 3: Structure (greeting, context, deliverables, next steps)
   - PHASE 4: Quality validation (≥90/100 score)

4. **Save as FOLLOW_UP_EMAIL.md in TARGET_MEETING folder**

5. **Set manifest state to complete (Mechanical):**
   ```bash
   python3 /home/workspace/N5/scripts/manifest_state_updater.py "<TARGET_MEETING>" follow_up_email complete \
     --output-file FOLLOW_UP_EMAIL.md --task-name MG-5
   ```

### STEP 4: Report Completion (Single-Meeting Scope)

```markdown
## Follow-Up Email Generation Report

**Meetings Considered This Run:** 1  
**Classified as needing email:** 1/0  
**Emails generated this run:** 1/0

### Classification Decision (This Run):
- [Meeting Name]
  - Decision: YES/NO
  - Reason: [explanation]
  - Confidence: high/medium/low

### Email Generated (if any):
- [Meeting Name] - Score: X/100
```

---

## Critical Rules

**✓ DO:**
- Read actual meeting content (B26, B02, B08, B01) for **one** TARGET_MEETING per run
- Make semantic judgment based on understanding
- Document reasoning for the single selected meeting
- Use Vibe Writer for actual email generation
- Track all deliverables (internal + external), note type
- Use `manifest_state_updater.py` to mark `follow_up_email` as `in_progress` → `complete`

**✗ DON'T:**
- Batch multiple meetings in a single MG-5 run
- Trust mechanical pattern matching (grep "Follow-Up Email Needed")
- Use stub/backfilled B25 files for classification
- Skip reading meeting context
- Assume internal-only meetings never need follow-ups
- Generate emails without semantic understanding

---

## Anti-Patterns to Avoid

**P0.1 Violation:** Using scripts for semantic analysis  
**P15 Violation:** Claiming "done" without processing the **single selected** meeting  
**P19 Violation:** Silently failing when intelligence blocks missing

---

## Quality Gates

**Before classification:**
- [ ] Loaded actual meeting content (not just B25)
- [ ] Understood who attended
- [ ] Understood meeting type
- [ ] Judging semantically, not pattern-matching
- [ ] Exactly one TARGET_MEETING chosen using oldest-[P]-without-followup rule

**Before generation:**
- [ ] Switched to Vibe Writer
- [ ] Following v2.0 email generation protocol
- [ ] Loading real intelligence blocks
- [ ] Applying voice transformation
- [ ] Manifest follow_up_email set to `in_progress`

**Before reporting:**
- [ ] TARGET_MEETING classified with reasoning
- [ ] Email (if any) scored
- [ ] Honest progress reported for this one meeting

---

*v3.1 | 2025-11-25 | Switched MG-5 to single-email-per-run with explicit selection + manifest bookkeeping*



