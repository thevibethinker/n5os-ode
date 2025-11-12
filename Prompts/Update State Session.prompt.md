---
description: 'Command: update-state-session'
tool: true
tags:
- state-session
- tracking
- update
---
# update-state-session

Update fields in SESSION_STATE.md for current conversation.

## Usage

```bash
# Update single field
/update-state-session --field status --value active
/update-state-session --field phase --value implementation
/update-state-session --field focus --value "Refactoring N5 core"

# Update objective
/update-state-session --field objective --value "Complete session state system"

# Update progress
/update-state-session --field progress --value "73%"
```

## Common Fields

### Metadata
- `status`: active | paused | complete | blocked
- `focus`: What this conversation is specifically about
- `objective`: What we're trying to accomplish

### Build-Specific
- `phase`: design | implementation | testing | deployment | complete
- `progress`: Percentage complete (e.g., "42%")

### Tracking
- `mode`: Specific mode within conversation type
- `tags`: Add tags for categorization

## What It Does

1. Locates SESSION_STATE.md for current conversation
2. Updates specified field with new value
3. Updates "Last Updated" timestamp
4. Validates field exists in template

## Examples

```bash
# Mark build as in testing phase
/update-state-session --field phase --value testing

# Change status to blocked
/update-state-session --field status --value blocked

# Update objective mid-conversation
/update-state-session --field objective --value "Add state-session commands to N5"
```

## Related Commands

- file 'N5/commands/init-state-session.md' - Initialize state
- file 'N5/commands/check-state-session.md' - Read current state
- file 'Documents/System/SESSION_STATE_SYSTEM.md' - Full documentation
