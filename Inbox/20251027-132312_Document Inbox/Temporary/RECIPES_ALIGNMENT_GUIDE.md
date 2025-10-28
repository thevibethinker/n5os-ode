# N5 + Zo Recipes: Alignment Guide
**Date:** 2025-10-27  
**Version:** 1.0

---

## Executive Summary

Zo's native **Recipes** feature is now the standard for user-facing workflows. This document clarifies how N5's architecture aligns with Zo's recipes paradigm and provides migration guidance.

---

## Three-Layer Architecture

### Layer 1: Recipes (User Workflows)
**Location:** `/home/workspace/Recipes/`  
**Purpose:** Reusable procedures invocable via slash command  
**Audience:** V and AI, user-facing  
**Format:** Markdown with YAML frontmatter

**Characteristics:**
- Natural language instructions
- Slash-invocable (type `/` in Zo chat)
- Can reference files, tools, other recipes, and N5 commands
- Living documentation that AI executes
- Portable across Zo users

**Examples:**
- `/analyze-meeting` - Process meeting notes
- `/export-thread` - Export conversation with AAR
- `/create-tally-survey` - Generate Tally forms
- `/process-to-knowledge` - Records → Knowledge pipeline

### Layer 2: N5 Commands (System Automation)
**Location:** `/home/workspace/N5/config/commands.jsonl`  
**Purpose:** Formal system operations with structured I/O  
**Audience:** System-level automation  
**Format:** JSONL registry + markdown docs

**Characteristics:**
- Well-defined interfaces (args, scripts, outputs)
- Scripted operations with validation
- Registered in commands.jsonl
- Called by recipes, scheduled tasks, or directly
- Can be triggered via natural language (Incantum)

**Examples:**
- `conversation-end` - Formal end-of-conversation workflow
- `lists-add` - Add item to list with validation
- `knowledge-ingest` - Structured knowledge ingestion
- `docgen` - Generate system documentation

### Layer 3: N5 Scripts (Implementation)
**Location:** `/home/workspace/N5/scripts/`  
**Purpose:** Python/shell implementations  
**Audience:** Automation layer  
**Format:** Executable code

**Characteristics:**
- Logging, error handling, dry-run support
- Called by commands or directly
- State verification, validation
- Follow architectural principles (P0-P22)

---

## How They Work Together

### Pattern 1: Recipe → Command → Script
```
User types: /export-thread
↓
Recipe loads: Recipes/Export Thread.md
↓
Recipe instructs: "Run the thread-export command"
↓
Command executes: N5/config/commands.jsonl (thread-export)
↓
Script runs: N5/scripts/n5_thread_export.py
↓
Output: Thread exported to N5/logs/threads/
```

### Pattern 2: Recipe → Direct AI Work
```
User types: /analyze-meeting
↓
Recipe loads: Recipes/Analyze Meeting.md
↓
Recipe instructs: "Load meeting-processing-blocks.json, ask user which blocks to apply"
↓
AI executes: Direct file manipulation, no script needed
↓
Output: Analysis blocks as markdown files
```

### Pattern 3: Recipe → Multiple Commands
```
User types: /process-to-knowledge
↓
Recipe loads: Recipes/Process to Knowledge.md
↓
Recipe instructs: "Classify content, run knowledge-add, verify"
↓
Commands execute: Multiple N5 commands in sequence
↓
Output: Records → Knowledge with metadata
```

---

## Decision Matrix: Recipe vs Command vs Script

### Use a Recipe When:
- ✅ User-facing workflow (discovery via `/` command)
- ✅ Natural language instructions sufficient
- ✅ Need flexibility for AI interpretation
- ✅ Workflow may vary based on context
- ✅ Want to share with other Zo users

### Use a Command When:
- ✅ System operation with structured I/O
- ✅ Needs validation and error handling
- ✅ Called by multiple recipes or scheduled tasks
- ✅ Requires state tracking or logging
- ✅ Part of N5 OS (not user workflow)

### Use a Script When:
- ✅ Implementing a command
- ✅ Complex logic not suitable for shell
- ✅ Needs testing and dry-run
- ✅ Reusable component for multiple commands

---

## Migration Strategy

### Already Migrated ✅
All files from `/Commands/` → `/Recipes/`

### Updated ✅
- `Documents/N5.md` - Added Recipes section
- `file 'MIGRATION_PLAN.md'` - Detailed plan

### Next Steps
1. **Update Prefs** - Add recipe discovery to command-first workflow
2. **Test Invocation** - Verify each recipe works via slash command
3. **Update Scripts** - Search for hardcoded `/Commands/` paths
4. **Archive Commands/** - Move to Documents/Archive/ after validation
5. **Document Patterns** - Create examples of recipe + command patterns

---

## Recipe Design Best Practices

### Structure Template
```yaml
---
description: |
  Clear, concise description of what this recipe does.
  Multi-line is fine.
tags:
  - primary-category
  - secondary-category
---
# Recipe Title

## What This Does
Brief explanation of purpose and use cases.

## Usage
How to invoke and what to expect.

## Instructions
Step-by-step guidance for AI:

1. **Step 1:** Load required files/context
2. **Step 2:** Ask clarifying questions if needed
3. **Step 3:** Execute workflow
4. **Step 4:** Verify and report results

## Scripts/Commands Referenced
- `command 'conversation-end'` - For structured operations
- `file 'N5/scripts/script.py'` - For direct script calls
- `file 'Knowledge/reference.md'` - For context

## Output
What the user should expect as result.
```

### Design Principles

**P1: Human-Readable Instructions**
- Write for both V and AI
- Clear intent, not just commands
- Explain the "why" not just "how"

**P2: Reference, Don't Duplicate**
- Use `file 'path'` mentions for context
- Use `command 'name'` for N5 operations
- Don't copy/paste content into recipes

**P8: Minimal Context**
- Load only what's needed for this workflow
- Use Rule-of-Two (max 2 files loaded)
- Reference others by path only

**P15: Complete Before Claiming**
- Define success criteria explicitly
- Include verification steps
- State expected outputs

**P21: Document Assumptions**
- What files must exist?
- What state is required?
- What are the prerequisites?

---

## Recipe Discovery Workflow

### For Users (V)
1. Type `/` in Zo chat
2. See autocomplete list of all recipes
3. Select recipe or continue typing to filter
4. AI loads and executes recipe

### For AI (You)
When V references a workflow:
1. Check if recipe exists: `ls /home/workspace/Recipes/*.md`
2. If exists, load recipe: `file 'Recipes/recipe-name.md'`
3. If not, check for command: `file 'N5/config/commands.jsonl'`
4. If neither, ask V or improvise

### Creating New Recipes
When V says "create a recipe for X":
1. Ask 3+ clarifying questions
2. Define scope and success criteria
3. Check for existing commands/scripts to reference
4. Write recipe with proper frontmatter
5. Save to `/home/workspace/Recipes/`
6. Test invocation

---

## Zo Recipes: Native Features

### What Zo Provides
- Slash command autocomplete
- YAML frontmatter parsing
- Tag-based organization
- File/tool/recipe reference syntax
- Native UI integration

### What N5 Adds
- Command registry integration
- Structured system operations
- Scripted automation
- Architectural principles
- Quality gates and validation

### Synergy
Recipes provide **discoverability** and **user interface**.  
N5 provides **automation** and **system operations**.  
Together: **Human-readable workflows backed by robust automation**.

---

## Examples: Before and After

### Example 1: Meeting Analysis

**Before (Commands/):**
```
V: "Use the meeting analysis command"
AI: Searches for Commands/Analyze Meeting.md
AI: Reads file, follows instructions
```

**After (Recipes/):**
```
V: Types "/analyze" [autocomplete shows "Analyze Meeting"]
V: Selects recipe
AI: Loads Recipes/Analyze Meeting.md
AI: Follows instructions
```

**Benefit:** Native discovery, no need to remember exact name

### Example 2: Thread Export

**Before:**
```
V: "Export this thread"
AI: Searches N5 prefs for "export thread"
AI: Finds thread-export command
AI: Runs command
```

**After:**
```
V: Types "/export" [autocomplete shows "Export Thread"]
V: Selects recipe
AI: Loads recipe, which references thread-export command
AI: Runs command via recipe
```

**Benefit:** Recipe provides context + instructions, command provides automation

### Example 3: New Workflow

**Before:**
```
V: "I want a workflow for processing customer emails"
AI: "Should I create a command for this?"
V: "Sure, whatever works"
AI: Creates Commands/Process Customer Emails.md
AI: No native discovery method
```

**After:**
```
V: "I want a workflow for processing customer emails"
AI: "I'll create a recipe. What should it do?"
[3+ clarifying questions]
AI: Creates Recipes/Process Customer Emails.md
AI: Recipe now discoverable via "/" in all conversations
V: Can share recipe with others via export
```

**Benefit:** Portable, discoverable, aligned with Zo ecosystem

---

## Ecosystem Implications

### For V's Careerspan Work
Recipes can be **packaged and distributed**:
- VC deal flow recipe → Share with VC community
- Student productivity recipe → Share at universities
- Solutions architect model → Monetize via Zo marketplace

### For N5 Evolution
- Recipes = User-facing interface
- Commands = System-level automation
- Scripts = Implementation layer
- **All three layers complement each other**

### For Zo Partnership
- V builds vertical-specific recipes
- Recipes reference N5 commands (portable)
- Zo users install recipes + underlying N5 components
- Revenue share model becomes feasible

---

## Testing Checklist

### Recipe Validation
- [ ] YAML frontmatter valid (description, tags)
- [ ] Instructions clear and actionable
- [ ] File/command references correct
- [ ] Can be invoked via slash command
- [ ] AI can execute successfully
- [ ] Success criteria defined

### System Integration
- [ ] Recipe → Command flow works
- [ ] Command → Script flow works
- [ ] Logging and error handling present
- [ ] Dry-run mode available (if applicable)
- [ ] State verification after execution

### Documentation
- [ ] N5.md updated
- [ ] Prefs.md references recipes
- [ ] Migration plan complete
- [ ] Examples documented
- [ ] Best practices defined

---

## Frequently Asked Questions

### Q: Should I convert all N5 commands to recipes?
**A:** No. Keep commands for system operations. Create recipes for user workflows that call commands.

### Q: Can recipes call other recipes?
**A:** Yes! Use natural language: "Follow the Export Thread recipe first, then..."

### Q: What if a recipe needs structured data?
**A:** Reference an N5 command that handles structured I/O. Recipe provides context, command provides structure.

### Q: Can I share recipes with other Zo users?
**A:** Yes, that's the point! Recipes are portable. If they reference N5 commands, include those in the package.

### Q: What happens to the Commands/ folder?
**A:** Archive it to `Documents/Archive/2025-10-27-Commands-Backup/` after validation. No data loss.

### Q: How do I create a new recipe?
**A:** Ask AI (me!) to create one. I'll ask clarifying questions, write it with proper structure, save to Recipes/.

---

## Next Actions

### Immediate
- [x] Migrate all files from Commands/ to Recipes/
- [x] Update Documents/N5.md
- [x] Create alignment documentation
- [ ] Test each recipe via slash command
- [ ] Update prefs.md command-first workflow

### Short-term (this week)
- [ ] Archive Commands/ folder
- [ ] Update any scripts referencing Commands/
- [ ] Create recipe discovery workflow
- [ ] Document recipe + command patterns

### Medium-term (this month)
- [ ] Create 5-10 new recipes for common workflows
- [ ] Package VC recipe for external distribution
- [ ] Build recipe template for future creations
- [ ] Update Vibe Builder persona with recipes guidance

---

## Resources

### Files
- `file 'Documents/N5.md'` - N5 OS overview
- `file 'N5/prefs/prefs.md'` - Preferences index
- `file 'N5/config/commands.jsonl'` - Command registry
- `file '/home/.z/workspaces/con_uVnpAD6W1XKczbee/MIGRATION_PLAN.md'` - Migration details

### Recipes Currently Available
```bash
ls /home/workspace/Recipes/*.md
```

### Commands Currently Registered
```bash
cat /home/workspace/N5/config/commands.jsonl | jq -r '.command'
```

---

**Status:** Migration Complete, System Aligned  
**Last Updated:** 2025-10-27 00:27 ET  
**Version:** 1.0
