# P23: Recipe Execution

**Category:** System Design  
**Status:** Active  
**Created:** 2025-10-28

---

## Principle

**Recipes are executable instructions, not documentation.**

When a user invokes a recipe, the AI must execute the commands in the "Execution" section, not merely describe what would happen.

---

## Core Rule

**Recipe markdown files must contain explicit execution instructions.**

A recipe without an "Execution" section is documentation-only and will result in the AI summarizing instead of acting.

---

## Pattern

```markdown
---
description: |
  What the recipe does (shown in slash menu)
tags:
  - categorization
  - tags
---
# Recipe Name

Brief overview of what this recipe accomplishes.

## Execution

**Run the primary command:**

\`\`\`bash
python3 /home/workspace/N5/scripts/script_name.py \\
  --flag value \\
  --convo-id <current_conversation_id>
\`\`\`

**Dry-run mode (preview only):**

\`\`\`bash
python3 /home/workspace/N5/scripts/script_name.py \\
  --dry-run \\
  --convo-id <current_conversation_id>
\`\`\`

**Parameters:**
- `--flag`: Description
- `--convo-id`: Current conversation ID (auto-detect from workspace)

## What This Does

[Detailed description of all phases/steps]

## When to Use

[Use cases and triggers]

## What You Get

✅ Expected output 1
✅ Expected output 2  
✅ Expected output 3

## Full Documentation

`file 'N5/prefs/operations/protocol-name.md'`

---

**Related:**
- Other related recipes
```

---

## Anti-Patterns

### ❌ Documentation-Only Recipe

**Wrong:**
```markdown
# Close Conversation

Runs conversation end workflow.

See `file 'N5/prefs/operations/conversation-end.md'` for details.
```

**Problem:** No execution section → AI reads recipe as documentation → Generates summary of what SHOULD happen → Nothing actually happens

**Result:** User gets text summary instead of actual execution

### ❌ Vague Instructions

**Wrong:**
```markdown
## Execution

Run the conversation end script with appropriate flags.
```

**Problem:** Not explicit enough → AI must guess what to run → May improvise or skip

### ❌ Missing Parameters

**Wrong:**
```markdown
## Execution

\`\`\`bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py
\`\`\`
```

**Problem:** Missing `--auto` and `--convo-id` flags → Script will prompt for input → Fails in automated context

---

## Correct Pattern

### ✅ Self-Executing Recipe

**Correct:**
```markdown
## Execution

**Run the conversation end-step:**

\`\`\`bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py \\
  --auto \\
  --convo-id <current_conversation_id>
\`\`\`

**Parameters:**
- `--auto`: Non-interactive mode (auto-approve all prompts)
- `--convo-id`: Current conversation ID (detect from workspace path)
```

**Why it works:**
- Explicit command with all required flags
- Clear parameter documentation
- AI knows exactly what to execute
- No ambiguity or guessing

---

## Migration from Commands.jsonl

### Old System (Deprecated 2025-10-28)

**Architecture:**
```
Recipe markdown (documentation) +  commands.jsonl (execution registry)
          ↓
User invokes recipe
          ↓
AI checks commands.jsonl
          ↓
Finds trigger → Executes command
```

**Problems:**
1. Two places to maintain
2. Hidden execution logic
3. Recipe and registry can diverge
4. Extra complexity layer

### New System (Current)

**Architecture:**
```
Recipe markdown (documentation + execution)
          ↓
User invokes recipe
          ↓
AI reads Execution section
          ↓
Executes commands directly
```

**Benefits:**
1. Single source of truth (P2)
2. Transparent to user
3. Cannot diverge
4. Simpler architecture

---

## Implementation

### Recipe Author Checklist

When creating or updating a recipe:

- [ ] Include YAML frontmatter with description and tags
- [ ] Add "Execution" section with explicit bash commands
- [ ] Include all required flags and parameters
- [ ] Document what each parameter does
- [ ] Provide dry-run option if applicable
- [ ] Test the command manually before committing
- [ ] Update recipes.jsonl index (auto-generated)

### AI Behavior

When user invokes a recipe:

1. **Read recipe markdown** - Parse YAML frontmatter and body
2. **Find Execution section** - Locate bash commands or step-by-step instructions
3. **Execute commands** - Run using `run_bash_command` tool
4. **Monitor and report** - Track progress, report results
5. **Never just summarize** - Always execute unless dry-run

---

## Examples

### System Recipe (Conversation Close)

**File:** `Recipes/Close Conversation.md`

**Execution section:**
```bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py \\
  --auto \\
  --convo-id <current_conversation_id>
```

**Result:** Full AAR with INDEX.md, RESUME.md, artifacts folder, etc.

### Content Recipe (Meeting Analysis)

**File:** `Recipes/Analyze Meeting.md`

**Execution section:**
```markdown
1. Ask which meeting to analyze (provide path)
2. Load `file N5/config/meeting-processing-blocks.json`
3. Ask which processing blocks to apply
4. Run: `python3 N5/scripts/meeting_processor.py <path> <blocks>`
```

**Result:** Individual .md files for each block in meeting directory

### Cleanup Recipe (Cleanup Root)

**File:** `Recipes/Cleanup Root.md`

**Execution section:**
```bash
python3 /home/workspace/N5/scripts/cleanup_workspace_root.py --dry-run
python3 /home/workspace/N5/scripts/cleanup_workspace_root.py
```

**Result:** Workspace root cleaned of conversation artifacts

---

## System Impact

### Files Affected

**Created:**
- `N5/prefs/operations/recipe-execution-guide.md` - Complete guide
- `Knowledge/architectural/principles/P23-recipe-execution.md` - This principle

**Deprecated:**
- `N5/config/commands.jsonl` - Archived 2025-10-28
- Moved to: `Documents/Archive/2025-10-28-Commands-Deprecation/`

**Updated:**
- `Documents/N5.md` - Commands section updated
- `N5/prefs/prefs.md` - Removed commands.jsonl references
- `Recipes/Close Conversation.md` - Added Execution section

### Documentation

**Primary:**
- `file 'N5/prefs/operations/recipe-execution-guide.md'` - Complete guide

**Archive:**
- `file 'Documents/Archive/2025-10-28-Commands-Deprecation/DEPRECATION_NOTICE.md'` - Migration guide

---

## Trade-offs

### Advantages
1. **Simplicity** - One file instead of two
2. **Transparency** - User sees what will run
3. **Maintainability** - Cannot get out of sync
4. **Self-documenting** - Code + docs in same place

### Disadvantages
1. **Verbosity** - Bash commands in markdown
2. **No validation** - No schema for execution section (yet)
3. **Learning curve** - Recipe authors must understand bash

**Verdict:** Advantages far outweigh disadvantages. The old system's hidden execution was a larger problem than verbosity in recipe files.

---

## Related Principles

- **P1 (Human-Readable)** - Execution section makes recipes transparent
- **P2 (SSOT)** - One file, not recipe + registry
- **P8 (Minimal Context)** - Self-contained recipes reduce lookups
- **P15 (Complete Before Claiming)** - Recipe must execute to completion
- **P21 (Document Assumptions)** - Parameters documented in recipe

---

## References

- `file 'N5/prefs/operations/recipe-execution-guide.md'` - Full guide
- `file 'Recipes/recipes.jsonl'` - Recipe index (272 recipes)
- `file 'Documents/Archive/2025-10-28-Commands-Deprecation/DEPRECATION_NOTICE.md'` - Migration path

---

## Version History

- **v1.0** (2025-10-28) - Initial principle created after conversation close fix
  - Formalized recipe execution model
  - Deprecated commands.jsonl
  - Updated Close Conversation recipe
  - Created comprehensive documentation

---

**Key Insight:** Recipes are for humans AND AI. Make execution explicit.
