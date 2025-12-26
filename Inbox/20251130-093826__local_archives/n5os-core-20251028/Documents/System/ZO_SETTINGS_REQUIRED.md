# Required Zo Settings for N5 OS Core

**Essential rules and preferences to configure in your Zo settings**

---

## Overview

N5 OS Core works best with specific Zo rules configured. These rules ensure safety, maintain context, and enable key workflows.

**Setup**: Zo Settings → Rules → Add the rules below

---

## ALWAYS APPLIED RULES (Required)

Copy these exactly into your Zo "ALWAYS APPLIED RULES" section:

### Rule 1: Anti-Hallucination
```
Do not hallucinate or fabricate information. You will be penalized more for an incorrect or inexact answer that results in negative consequences than simply saying that you do not know, which is always the correct and preferred response in situations where you have reason for pause.
```

**Why**: Accuracy over confidence. N5 OS depends on trustworthy outputs.

### Rule 2: Clarifying Questions
```
If you are in any doubt about my objectives, priorities, target persona, intended audience, or any and all details that would materially affect your response, ask a minimum of 3 clarifying questions before proceeding with any action.
```

**Why**: Prevents wasted work from misunderstood requirements.

### Rule 3: Load System Files
```
- Load `file Documents/N5.md`
- Load `file N5/prefs/prefs.md`
```

**Why**: Ensures AI loads your N5 OS preferences and system overview.

### Rule 4: Session State Initialization
```
Initialize SESSION_STATE.md for this conversation workspace by running:

python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id <current_conversation_id> --load-system

Auto-detect the conversation type based on the user's first message:
- Keywords "build", "implement", "code", "script", "create", "develop" → --type build
- Keywords "research", "analyze", "learn", "study", "investigate" → --type research
- Keywords "discuss", "think", "explore", "brainstorm", "consider" → --type discussion
- Keywords "plan", "strategy", "decide", "organize", "roadmap" → --type planning
- Default if unclear → --type discussion

CRITICAL: The --load-system flag will output required system files. When you see this output, YOU MUST load:
- file 'Documents/N5.md'
- file 'N5/prefs/prefs.md'

YOU MUST ALSO RESPOND WITH:
- the conversation ID e.g. "This is conversation con_Sq70IglhvzX4GJE3"

After initialization, read SESSION_STATE.md and update the Focus, Objective, and Tags sections based on the user's request. Reference this state file throughout the conversation to maintain context and track progress.
```

**Why**: Maintains context across long conversations, enables resume after interruptions.

### Rule 5: Timestamp
```
Include a date and time stamp in ET/EST at the end of each response.
```

**Why**: Track when work was done, helps with debugging timing issues.

---

## CONDITIONAL RULES (Required for Safety & Features)

Copy these into your Zo "CONDITIONAL RULES" section:

### Rule 6: Destructive Actions Safety

**CONDITION**: `Before destructive actions (e.g., deletes/overwrites of individual files or in bulk)`

**RULE**: `Require dry-run preview and explicit confirmation; validate security (e.g., via file 'N5/scripts/n5_safety.py') against risks in file 'N5/lists/detection_rules.md'.`

**Why**: Prevents accidental data loss. Always preview before destroying.

### Rule 7: /gfetch Command

**CONDITION**: `When I provide the command /gfetch`

**RULE**: `Seek and retrieve from Google Drive or Gmail`

**Why**: Quick command for fetching from integrated apps.

*(Note: This requires Google Drive/Gmail integration setup separately)*

### Rule 8: Troubleshooting Protocol

**CONDITION**: `Whenever you are stuck or repeatedly encountering errors`

**RULE**:
```
Troubleshoot in the following way:
Stop directly trying to solve the problem and take a deep breath. Then step outside of the approach you've been using and ask the following kinds of questions:
- Am I missing a vital piece of information?
- Am I executing things in the right order?
- Are there dependencies I haven't considered?
- Am I barking up the wrong tree? (Is this approach fundamentally unsound?)
- Are there relevant problem solving principles I can apply?
- Are there novel angles from which to approach this problem or are there other ways divergent thinking can help me? (raise AI model temperature if needed)
```

**Why**: Prevents AI from spinning wheels. Forces reset and re-evaluation.

### Rule 9: System Operations Check

**CONDITION**: `Before executing system operations (e.g., adding to lists, rebuilding index)`

**RULE**:
```
Check if a registered command exists in file 'N5/config/commands.jsonl' and use it instead of manual operations. Priority: command-first approach.
```

**Why**: Use documented commands instead of ad-hoc operations. Consistency.

### Rule 10: System Building Work

**CONDITION**: `When I request building, refactoring, or modifying significant system components (scripts, workflows, infrastructure, automation)`

**RULE**:
```
Load file 'Knowledge/architectural/architectural_principles.md' FIRST before any design or implementation work. Follow the system design workflow in 'N5/commands/system-design-workflow.md'.
```

**Why**: Ensure system changes follow N5 architectural principles.

---

## Optional but Recommended

### Rule 11: Scheduled Task Protocol

**CONDITION**: `When I request creating, modifying, or reviewing a scheduled task`

**RULE**:
```
Load and follow file 'N5/prefs/operations/scheduled-task-protocol.md' before proceeding. This includes safety requirements, testing checklist, instruction structure, and documentation standards.
```

**Why**: Consistent, safe scheduled task management.

---

## Setup Checklist

- [ ] All "ALWAYS APPLIED RULES" (Rules 1-5) added
- [ ] All "CONDITIONAL RULES" (Rules 6-10) added
- [ ] Optional Rule 11 added (if using scheduled tasks)
- [ ] Tested: Start new conversation, verify session state initializes
- [ ] Tested: Try destructive command, verify dry-run prompt appears

---

## Onboarding Integration

During interactive onboarding (`onboarding.py`), the system will:

1. **Detect** if rules are already configured (by testing behavior)
2. **Prompt** user to add missing rules
3. **Provide** copy-paste text for each rule
4. **Verify** rules work (test session state, test dry-run)
5. **Document** in `user_config/zo_rules_configured.txt`

---

## Troubleshooting

### "Session state not initializing"
**Check**: Rule 4 is added correctly, test by starting new conversation

### "Destructive actions not prompting for confirmation"
**Check**: Rule 6 is added correctly, test by trying to delete a file

### "AI not loading system files"
**Check**: Rules 3 and 4 are added correctly, check conversation start

### "Timestamp not appearing"
**Check**: Rule 5 is added, may need to remind AI once

---

**Version**: 1.0-core  
**Essential**: Rules 1-10  
**Optional**: Rule 11  
**Setup Time**: ~10 minutes

**Note**: These rules are copied from V's production N5 OS and are battle-tested for N5 OS installations.
