---
description: 'Command: check-state-session'
tool: true
tags:
- state-session
- tracking
- status
---
# check-state-session

Read and display current SESSION_STATE.md.

## Usage

```bash
# Check current conversation state
/check-state-session

# Check specific conversation
/check-state-session --convo-id con_XXX
```

## What It Shows

### All Conversation Types
- Conversation ID and timestamps
- Type, mode, and focus
- Current status and objective
- Success criteria checklist
- Progress tracking
- Key insights and decisions
- Open questions
- Outputs created
- Tags

### Build Conversations (Additional)
- Current phase (design/implementation/testing/deployment)
- Architectural decisions log
- Files being modified with status
- Test checklist
- Rollback plan
- Principle violations

### Research Conversations (Additional)
- Research questions
- Sources consulted
- Findings and conclusions
- Knowledge gaps

## Output Format

Displays full SESSION_STATE.md content formatted as markdown with:
- Metadata header
- Sectioned information
- Checklists for tracking
- Timestamps for audit trail

## Use Cases

- **Mid-conversation check-in**: See what's been accomplished
- **Context refresh**: Reload objectives after interruption
- **Handoff preparation**: Review state before switching contexts
- **Quality gate**: Verify completeness before marking done

## Related Commands

- file 'N5/commands/init-state-session.md' - Initialize state
- file 'N5/commands/update-state-session.md' - Update state fields
- file 'Documents/System/SESSION_STATE_SYSTEM.md' - Full documentation
