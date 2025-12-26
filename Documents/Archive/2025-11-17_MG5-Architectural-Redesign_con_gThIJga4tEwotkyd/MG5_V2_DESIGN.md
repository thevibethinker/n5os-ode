---
created: 2025-11-17
last_edited: 2025-11-17
version: 1
---
# MG-5 v2.0: Follow-Up Email Generation (LLM-First Architecture)

**This is conversation con_gThIJga4tEwotkyd**

## Design Principles

### Division of Labor (Core Principle)
```
Python Scripts = MECHANICS (file operations, validation, data structures)
LLM (Zo) = SEMANTICS (understanding, judgment, content generation)
```

**Previous Architecture (WRONG):**
```
Task → Python Script (tries to do everything) → Email
```

**New Architecture (RIGHT):**
```
Task → Python (find meetings) → LLM (semantic analysis per meeting) → Python (save files, update manifest)
```

---

## Task Instruction Design

### High-Level Flow

**STEP 1: Python finds [M] meetings (Mechanics)**
- Scan `/home/workspace/Personal/Meetings/Inbox` for folders with `[M]` tag
- Return list of meeting paths

**STEP 2: LLM analyzes EACH meeting semantically (Semantics)**
For each meeting:
1. Read transcript and all intelligence blocks
2. Make semantic judgment: "Does this meeting need a follow-up email?"
3. If YES → Generate personalized follow-up email content
4. If NO → Classify reason (n/a, internal-only, no-action-needed, etc.)

**STEP 3: Python saves output (Mechanics)**
- Save email to `follow_up_email.md` in meeting folder
- Update `manifest.json` with `system_states.follow_up_email.status = "complete"` or "n/a"
- Update `completed_at` timestamp

---

## Detailed Task Instruction

```markdown
Generate follow-up emails for meetings in [M] state using LLM-first semantic analysis.

**STEP 1: Find [M] meetings using Python (Mechanics)**

Run Python to find all meetings:
```bash
find /home/workspace/Personal/Meetings/Inbox -maxdepth 1 -type d -name "*[M]" | sort
```

Store results in array for processing.

**STEP 2: For EACH meeting, perform LLM semantic analysis (I do this)**

For each meeting path:

2a. **Load meeting context:**
- Read `transcript.md`
- Read `manifest.json` to understand meeting metadata
- Read all intelligence blocks (B01, B02, B05, etc.)
- Read B08_FOLLOW_UP_CONVERSATIONS.md if it exists (gives explicit follow-up guidance)

2b. **Semantic judgment - Does this meeting need a follow-up email?**

Consider:
- Is this an external meeting with someone outside Careerspan?
- Were commitments made that need confirmation?
- Were action items assigned that need follow-up?
- Was information requested or promised?
- Is this a partnership/sales/strategic conversation requiring next steps?

**Internal-only meetings (V + Careerspan team only) → typically N/A**
**External meetings (V + external stakeholders) → typically YES**

If NO follow-up needed:
- Classify reason: "internal_only", "no_action_needed", "casual_conversation", etc.
- Skip to Step 3 with status = "n/a"

If YES follow-up needed → Proceed to 2c

2c. **Generate follow-up email content:**

Use V's communication style:
- Warm, personal, professional
- Reference specific conversation moments
- Confirm commitments clearly
- Provide clear next steps
- Include relevant context/links if helpful

Structure:
```
Subject: [Descriptive, specific subject]

[Opening - personal connection to conversation]

[Body - key points, commitments, next steps]

[Closing - clear call to action or timeline]

Best,
V
```

Save content to variable for Step 3.

**STEP 3: Python saves files and updates manifest (Mechanics)**

For each meeting processed:

3a. If email was generated:
```bash
# Save email
cat > "$MEETING_PATH/follow_up_email.md" << 'EOF'
[email content]
EOF

# Update manifest
python3 << 'PYTHON'
import json
from pathlib import Path
from datetime import datetime, timezone

manifest_path = Path("$MEETING_PATH/manifest.json")
manifest = json.loads(manifest_path.read_text())

# Update system_states
if "system_states" not in manifest:
    manifest["system_states"] = {}
    
manifest["system_states"]["follow_up_email"] = {
    "status": "complete",
    "completed_at": datetime.now(timezone.utc).isoformat(),
    "last_updated_by": "MG-5_v2"
}

# Also set ready_for_state_transition if all systems complete
if all([
    manifest["system_states"].get("intelligence_blocks", {}).get("status") == "complete",
    manifest["system_states"].get("warm_intro", {}).get("status") in ["complete", "n/a"],
    manifest["system_states"].get("follow_up_email", {}).get("status") in ["complete", "n/a"]
]):
    if "ready_for_state_transition" not in manifest:
        manifest["ready_for_state_transition"] = {}
    manifest["ready_for_state_transition"]["status"] = True
    manifest["ready_for_state_transition"]["blocking_systems"] = []
    
manifest_path.write_text(json.dumps(manifest, indent=2))
PYTHON
```

3b. If no email needed (n/a):
```bash
# Update manifest only
python3 << 'PYTHON'
import json
from pathlib import Path
from datetime import datetime, timezone

manifest_path = Path("$MEETING_PATH/manifest.json")
manifest = json.loads(manifest_path.read_text())

if "system_states" not in manifest:
    manifest["system_states"] = {}
    
manifest["system_states"]["follow_up_email"] = {
    "status": "n/a",
    "reason": "[classification from Step 2b]",
    "completed_at": datetime.now(timezone.utc).isoformat(),
    "last_updated_by": "MG-5_v2"
}

# Check if ready for transition
if all([
    manifest["system_states"].get("intelligence_blocks", {}).get("status") == "complete",
    manifest["system_states"].get("warm_intro", {}).get("status") in ["complete", "n/a"],
    manifest["system_states"].get("follow_up_email", {}).get("status") in ["complete", "n/a"]
]):
    if "ready_for_state_transition" not in manifest:
        manifest["ready_for_state_transition"] = {}
    manifest["ready_for_state_transition"]["status"] = True
    manifest["ready_for_state_transition"]["blocking_systems"] = []

manifest_path.write_text(json.dumps(manifest, indent=2))
PYTHON
```

**STEP 4: Summary report**

After processing all meetings, report:
- Total [M] meetings found: X
- Follow-up emails generated: Y
- Marked as n/a: Z
- Summary of each meeting processed

---

**Division of Labor Enforced:**
- Python = Finding files, saving files, updating JSON
- LLM (me) = Reading context, making judgments, generating content

This is the correct architecture.
```

---

## Why This Design Works

### Addresses Root Cause
1. **LLM does semantic work:** Understanding meeting context, making judgment calls about follow-up necessity
2. **Python does mechanics:** File operations, JSON updates, validation
3. **Clear separation:** No Python trying to analyze conversation dynamics

### Handles Edge Cases
1. **Internal meetings:** LLM can semantically distinguish internal vs external
2. **No-action meetings:** LLM can judge "this was just informational"
3. **Complex meetings:** LLM can read multiple blocks and synthesize
4. **Personalization:** LLM generates content in V's voice

### Scalable Pattern
This same architecture should apply to:
- MG-2 (Intelligence Blocks): LLM verifies completion status
- MG-4 (Warm Intros): LLM analyzes if intro is valuable
- Any future meeting pipeline task

---

## Implementation Path

1. **Create new scheduled task** with this instruction
2. **Test with 2-3 sample meetings** manually first
3. **Let run on schedule** (every 4 hours suggested)
4. **Compare results** with old MG-5 before deprecating
5. **Once validated, deprecate old task**

---

## Ready for Builder

Design complete. Ready to:
1. Create scheduled task with this instruction
2. Test execution
3. Compare with old system

---

*2025-11-17 22:08:12 ET*

