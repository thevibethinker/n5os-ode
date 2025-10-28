# Commands → Recipes Migration Plan
**Date:** 2025-10-27  
**Conversation:** con_uVnpAD6W1XKczbee

---

## Overview

Migrating N5's custom `/Commands` folder to align with Zo's native `/Recipes` feature. The recipes system is Zo's official way to create reusable, slash-invocable workflows.

---

## Key Differences: Commands vs. Recipes

### Commands (Old, N5-specific)
- Custom N5 directory (`/home/workspace/Commands/`)
- User-created convention, not native to Zo
- Required manual routing/parsing
- Mixed with N5 system commands (`N5/config/commands.jsonl`)

### Recipes (New, Zo-native)
- Official Zo feature (`/home/workspace/Recipes/`)
- Slash (/) invocable in chat input
- Markdown files with YAML frontmatter
- Native UI integration
- Can reference files, tools, other recipes
- Standard structure: frontmatter + instructions

---

## Migration Strategy

### Phase 1: Transfer Files (COMPLETE)
✅ Move all `.md` files from Commands/ to Recipes/
✅ Preserve YAML frontmatter structure
✅ Maintain all content intact

### Phase 2: System Realignment (IN PROGRESS)
- Update N5 documentation to reference Recipes/ instead of Commands/
- Update prefs to use recipes paradigm
- Update any scripts that reference Commands/ directory
- Create recipe discovery/management workflows

### Phase 3: Validation
- Test each recipe invocation via slash command
- Verify all file references work
- Ensure N5 command registry (commands.jsonl) integration still works
- Document new workflows

---

## Files to Migrate

### From Commands/
1. ✅ Analyze Meeting.md
2. ✅ Build Review.md
3. ✅ Close Conversation.md
4. ✅ Emoji Legend.md
5. ✅ Export Thread.md
6. ✅ Process to Knowledge.md
7. ✅ Quick Classify.md
8. ✅ Resume.md (already exists in Recipes/)
9. ✅ Safety Check.md
10. ✅ Session Review.md
11. ✅ spawn-worker.md

### Already in Recipes/
- Create Tally Survey.md
- Resume.md (duplicate, will merge)

---

## System Files to Update

### Documentation
- [ ] `Documents/N5.md` - Update references to Commands/ → Recipes/
- [ ] `N5/prefs/prefs.md` - Update command-first workflow to include recipes
- [ ] `N5/commands.md` - Clarify distinction between recipes and system commands

### Scripts
- [ ] Search for hardcoded `/Commands/` paths in N5/scripts/
- [ ] Update any discovery or indexing logic

### Config
- [ ] Review `N5/config/commands.jsonl` - System commands stay here
- [ ] Document relationship: Recipes = user workflows, commands.jsonl = system operations

---

## Post-Migration Architecture

```
/home/workspace/
├── Recipes/                    # USER WORKFLOWS (slash-invocable)
│   ├── Analyze Meeting.md      # Process meetings
│   ├── Export Thread.md        # Thread export
│   ├── Create Tally Survey.md  # Tally integration
│   └── ...                     # All user-facing workflows
│
├── N5/
│   ├── config/
│   │   └── commands.jsonl      # SYSTEM COMMANDS (registered automation)
│   ├── commands/               # COMMAND DOCUMENTATION
│   │   ├── conversation-end.md
│   │   ├── thread-export.md
│   │   └── ...
│   └── scripts/                # AUTOMATION SCRIPTS
│       ├── n5_conversation_end.py
│       └── ...
```

### Conceptual Model

**Recipes = User-Facing Workflows**
- Slash-invocable in chat
- Natural language instructions
- Can reference N5 commands, scripts, or work directly
- Living documentation that AI executes

**Commands = System Automation**
- Formal registry (commands.jsonl)
- Scripted operations with structured I/O
- Called by recipes or triggered automatically
- Well-defined interfaces

**Relationship:**
- Recipes can call commands: "Run the `conversation-end` command"
- Commands can be wrapped in recipes for easier discovery
- Recipes provide human context, commands provide automation

---

## Zo Recipes Feature: What We Know

From system prompts and context:

### Structure
```yaml
---
description: |
  Multi-line description of what this recipe does
tags:
  - tag1
  - tag2
---
# Recipe Title

Instructions in markdown...
Can reference `file 'path/to/file'`
Can reference `tool tool_name`
Can reference other recipes
```

### Invocation
- Type `/` in chat to see all recipes
- Recipes auto-complete by name
- AI reads recipe and executes instructions

### Features
- YAML frontmatter (description, tags)
- Markdown body with instructions
- Can reference files, tools, other recipes
- Native to Zo (not N5-specific)

---

## Key Realignments

### 1. Discovery
**Before:** Manual search of Commands/  
**After:** Type `/` to discover recipes

### 2. Execution
**Before:** Tell AI "use the command for X"  
**After:** Type `/recipe-name` or reference in natural language

### 3. Organization
**Before:** Mixed user workflows + system commands in Commands/  
**After:** Clear separation - Recipes/ for workflows, N5/config/commands.jsonl for system

### 4. Documentation
**Before:** Commands lived in N5 namespace  
**After:** Recipes are workspace-level, N5 commands stay in N5/

---

## Benefits of Migration

1. **Native Integration:** Leverage Zo's built-in recipe system
2. **Better Discovery:** Slash command auto-complete
3. **Clearer Architecture:** Recipes (user) vs Commands (system)
4. **Portable:** Recipes can be shared across Zo users
5. **Future-Proof:** Aligned with Zo's roadmap (marketplace, sharing)

---

## Risk Mitigation

- ✅ No data loss: Commands/ folder remains (can archive later)
- ✅ Backward compatibility: N5 commands.jsonl unchanged
- ✅ Incremental: Can migrate one recipe at a time
- ✅ Reversible: Can move files back if needed

---

## Next Steps

1. ✅ Complete file migration
2. ⏳ Update system documentation
3. ⏳ Test each recipe invocation
4. ⏳ Update prefs and workflows
5. ⏳ Archive Commands/ folder
6. ⏳ Create recipes discovery workflow

---

## Open Questions for V

1. Keep Commands/ as archive or delete after validation?
2. Should Resume.md merge content or keep separate?
3. Any recipes that should stay N5-internal only?
4. Want to create recipe for "discover all recipes"?

---

**Status:** Phase 1 Complete, Phase 2 In Progress  
**Next Action:** Transfer all files, then update documentation
