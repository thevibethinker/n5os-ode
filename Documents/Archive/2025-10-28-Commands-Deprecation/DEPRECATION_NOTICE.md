# Commands.jsonl Deprecation Notice

**Date:** 2025-10-28  
**Status:** DEPRECATED & REMOVED  
**Replaced By:** Recipe execution model

---

## What Changed

**Removed:**
- `N5/config/commands.jsonl` - Command execution registry
- Automatic command lookup/execution based on trigger words

**Added:**
- `N5/prefs/operations/recipe-execution-guide.md` - How recipes work
- Explicit execution instructions in recipe markdown files

---

## Why This Change

### Previous System (Commands.jsonl)

**Architecture:**
```
User invokes command
    ↓
AI checks commands.jsonl registry
    ↓
Finds matching trigger
    ↓
Executes associated command
    ↓
Reports result
```

**Problems:**
1. **Hidden execution** - User couldn't see what would run
2. **Two places to update** - Recipe markdown + commands.jsonl
3. **Complexity** - Extra layer between intent and execution
4. **Non-technical barrier** - Users had to understand registry format
5. **Sync issues** - Recipe and registry could diverge

### New System (Recipe Markdown)

**Architecture:**
```
User invokes recipe
    ↓
AI reads recipe markdown
    ↓
Executes bash commands in "Execution" section
    ↓
Reports result
```

**Benefits:**
1. **Transparent** - User sees exactly what will run
2. **Single source** - One file to update
3. **Simple** - Direct path from intent to execution
4. **User-friendly** - Plain English + bash commands
5. **Always in sync** - Can't diverge

---

## Migration Path

### For Recipe Authors

**Before:**
1. Create recipe markdown
2. Add entry to commands.jsonl with trigger + command
3. User invokes → AI checks registry → executes

**After:**
1. Create recipe markdown with "Execution" section
2. Include explicit bash commands
3. User invokes → AI reads recipe → executes

**Example:**

**Old Recipe** (required commands.jsonl entry):
```markdown
# Close Conversation

Runs conversation end workflow.

See `file 'N5/prefs/operations/conversation-end.md'` for details.
```

**commands.jsonl entry:**
```json
{
  "trigger": "close-conversation",
  "command": "python3 /home/workspace/N5/scripts/n5_conversation_end.py --auto --convo-id {convo_id}"
}
```

**New Recipe** (self-contained):
```markdown
# Close Conversation

Runs conversation end workflow.

## Execution

\`\`\`bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py \\
  --auto \\
  --convo-id <current_conversation_id>
\`\`\`

## What This Does

[Full description...]
```

### For AI System

**Before:**
1. Check if command exists in `commands.jsonl`
2. Parse command template
3. Substitute variables
4. Execute

**After:**
1. Read recipe markdown
2. Find "Execution" section
3. Execute bash commands directly

---

## Affected Files

### Removed
- `N5/config/commands.jsonl` → Moved to Archive

### Updated
- `Documents/N5.md` - Updated commands section
- `N5/prefs/prefs.md` - Removed commands.jsonl references
- `Recipes/Close Conversation.md` - Added Execution section

### Created
- `N5/prefs/operations/recipe-execution-guide.md` - Complete guide
- `Documents/Archive/2025-10-28-Commands-Deprecation/` - This archive

---

## Backwards Compatibility

**None.** This is a breaking change.

**References to commands.jsonl in:**
- Documentation - Being updated
- Scripts - May need updates (if they read commands.jsonl)
- Old recipes - Need Execution sections added

---

## Action Items

For system maintainers:

- [x] Create recipe-execution-guide.md
- [x] Remove commands.jsonl
- [x] Update N5.md
- [x] Update prefs.md
- [x] Update Close Conversation recipe
- [ ] Audit all recipes for Execution sections
- [ ] Update any scripts that read commands.jsonl
- [ ] Search/replace references in documentation

---

## Related Documentation

- `file 'N5/prefs/operations/recipe-execution-guide.md'` - How recipes work now
- `file 'Recipes/recipes.jsonl'` - Recipe index (metadata only)
- `file 'Documents/N5.md'` - Updated system overview

---

## Questions?

Reference file `file 'N5/prefs/operations/recipe-execution-guide.md'` for complete details on the new system.

---

*Archived commands.jsonl:* `file '/home/workspace/Documents/Archive/2025-10-28-Commands-Deprecation/commands.jsonl.deprecated'`
