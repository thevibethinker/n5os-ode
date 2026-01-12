---
created: 2025-11-17
last_edited: 2026-01-12
version: 3.3
title: Follow-Up Email Generator v3.3
description: Generate follow-up emails for meetings using manifest status and semantic classification
tags: [workflow, email, meetings, automation, semantic-analysis]
tool: true
---

# Follow-Up Email Generator v3.3

**Purpose:** Generate follow-up emails for meetings using semantic classification  
**Key Principle:** Scripts = Mechanics | LLM = Semantics | Never confuse the two

**v3.3 Change:** Added Voice Injection Layer integration (auto-applies V's linguistic primitives).

**v3.2 Change:** Now uses manifest.json status instead of `_[P]` folder suffix.
The pipeline is: `intelligence_generated` → MG-5 → `processed` (ready for archival)

---

## Execution Protocol

### STEP 1: Find Meetings Ready for Follow-Up (Mechanical, then select ONE)

```bash
# Find meetings with intelligence_generated/mg2_completed status that lack FOLLOW_UP_EMAIL.md
python3 /home/workspace/N5/scripts/find_meetings_for_follow_up.py --oldest --json
```

**Selection Rule:** The script returns the oldest meeting in Inbox with:
- Status = `intelligence_generated` or `mg2_completed`
- No existing `FOLLOW_UP_EMAIL.md`

To include Week-of folders (for backfill):
```bash
python3 /home/workspace/N5/scripts/find_meetings_for_follow_up.py --oldest --include-week-of --json
```

> MG-5 is *single-email-per-run*. Do **not** batch across multiple meetings in one invocation.

Let `TARGET_MEETING` be the folder path returned by the script.

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

### STEP 2.5: Voice Injection Layer (Automatic) ⭐ NEW in v3.3

**Purpose:** Auto-inject V's distinctive linguistic patterns before generation. Fully automatic — no human review.

**Implementation:**
```python
from N5.scripts.voice_layer import VoiceContext, inject_voice

# Build context from meeting classification
ctx = VoiceContext(
    content_type="email",
    platform="email",
    purpose="follow-up",
    topic_domains=extracted_from_B06_or_B26,  # e.g., ["hiring", "partnership", "career"]
)

# Auto-inject (happens before generation)
enhanced_prompt = inject_voice(generation_prompt, ctx)
```

**What happens automatically:**
1. Layer retrieves 3 relevant primitives from `voice_library.db`
2. Primitives injected as context into generation prompt
3. LLM weaves patterns naturally — never forced
4. Usage tracked to prevent repetition across emails

**Domain Extraction:**
- From B06_BUSINESS_CONTEXT: industry, sector, discussion topics
- From B26_METADATA: meeting type, stakeholder context
- Inferred from B01 content analysis

**Note:** This step runs automatically as part of the generation process. No manual intervention required.

---

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

## Directness Validation (2026-01)

**After generating email, scan for hedging anti-patterns:**

| Kill | Example | Fix |
|------|---------|-----|
| `just wanted to` | "Just wanted to follow up..." | "Following up on..." |
| `I think maybe` | "I think maybe we could..." | "We should..." |
| `if you have time` | "If you have time to review..." | "Please review by [date]" |
| `no rush` | "No rush on this..." | Name actual timeline or omit |
| `feel free to` | "Feel free to reach out..." | "Let me know..." |
| `does that make sense?` | "Does that make sense?" | Assume it does |

**Directness target:** 0.7-0.8 for follow-up emails.

**Reference:** `file 'N5/prefs/communication/style-guides/hedging-antipatterns.md'`

---

## Quality Gates

**Before classification:**
- [ ] Used find_meetings_for_follow_up.py to select TARGET_MEETING
- [ ] Loaded actual meeting content (not just B25)
- [ ] Understood who attended
- [ ] Understood meeting type
- [ ] Judging semantically, not pattern-matching
- [ ] Exactly one TARGET_MEETING chosen using oldest-ready rule

**Before generation:**
- [ ] Switched to Vibe Writer
- [ ] Following v2.0 email generation protocol
- [ ] Loading real intelligence blocks
- [ ] Applying voice transformation
- [ ] Manifest follow_up_email set to `in_progress`

**After generation (DIRECTNESS CHECK):**
- [ ] No hedging qualifiers (just, maybe, kind of)
- [ ] Asks are explicit, not buried
- [ ] Timelines named when relevant
- [ ] No permission-seeking phrases
- [ ] Scanned against hedging-antipatterns.md

**Before reporting:**
- [ ] TARGET_MEETING classified with reasoning
- [ ] Email (if any) scored
- [ ] Directness validation passed
- [ ] Honest progress reported for this one meeting

---

*v3.3 | 2026-01-12 | Added Voice Injection Layer integration (auto-applies V's linguistic primitives).*

*v3.2 | 2025-12-26 | Changed to manifest-based status detection (no more [P] suffix requirement)*






