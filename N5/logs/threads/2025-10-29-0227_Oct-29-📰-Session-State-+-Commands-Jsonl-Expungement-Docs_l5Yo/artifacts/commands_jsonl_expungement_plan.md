# commands.jsonl Expungement Plan

**Created:** 2025-10-28 22:22 ET  
**Conversation:** con_V0uhNqJjr6osl5Yo  
**Objective:** Systematically remove ALL references to `commands.jsonl` from N5 system

---

## Findings

### Active System Files (CRITICAL - Must Fix)
1. **Documents/N5.md** - Main OS doc, has deprecation note but still references
2. **N5/prefs/prefs.md** - Critical preferences file, command-first rule references it
3. **Documents/System/personas/vibe_operator_persona.md** - Currently loaded persona
4. **Documents/System/personas/vibe_builder_persona.md** - Sister persona

### Active Recipes (11 files)
- Recipes/Search Commands.md
- Recipes/Add Digest.md
- Recipes/Docgen.md
- Recipes/Linkedin Post Generate.md
- Recipes/Prompt Import.md
- Recipes/File Protector.md
- Recipes/Function Import System.md
- Recipes/Git Check.md

### Active Python Scripts (20 files)
Core scripts that reference commands.jsonl:
- N5/scripts/n5_search_commands.py
- N5/scripts/n5_docgen.py
- N5/scripts/n5_index_rebuild.py
- N5/scripts/n5_index_update.py
- N5/scripts/n5_safety.py
- N5/scripts/n5_git_audit.py
- N5/scripts/n5_incantum.py
- N5/scripts/n5_schedule_wrapper.py
- N5/scripts/n5_import_prompt.py
- N5/scripts/file_protector.py
- N5/scripts/file_backup.py
- N5/scripts/bulletin_generator.py
- N5/scripts/sync_to_main.py
- N5/scripts/incantum_parser.py
- N5/scripts/author_command/* (4 files)
- N5/scripts/maintenance/* (2 files)

### System Docs & Guides (50+ files)
Various documentation, guides, principles that mention commands.jsonl

### Bootstrap/Deployment Artifacts
- N5_OS_Core_Artifacts/
- N5_Artifacts_For_Download/
- .n5_bootstrap_server/

### Archived Material (Excluded from cleanup)
- Documents/Archive/
- Inbox/
- N5/logs/threads/

---

## Replacement Strategy

### Pattern Replacements

**For documentation/guides:**
- `N5/config/commands.jsonl` → `Recipes/recipes.jsonl` (context: "recipe index")
- `commands.jsonl` → `recipes.jsonl` (when referring to index)
- References to "command registry" → "recipe registry"
- "Registered commands" → "Available recipes"

**For scripts:**
- Variable names: `COMMANDS_FILE` → `RECIPES_INDEX`
- File path: `N5/config/commands.jsonl` → `Recipes/recipes.jsonl`
- Comments: "commands.jsonl" → "recipes.jsonl (recipe index)"

**For personas/prefs:**
- "Check commands.jsonl" → "Check Recipes/ for available recipes"
- "Command-first" → "Recipe-first" (with appropriate context)

**Special cases:**
- Scripts that truly need command functionality → Mark for deprecation or refactor
- Historical documentation → Add deprecation banner, don't modify content
- Bootstrap artifacts → Update or mark as outdated

---

## Execution Plan

### Phase 1: Critical System Files (Do First)
1. Documents/N5.md
2. N5/prefs/prefs.md  
3. Documents/System/personas/vibe_operator_persona.md
4. Documents/System/personas/vibe_builder_persona.md

### Phase 2: Active Recipes (11 files)
Update all recipe references systematically

### Phase 3: Active Scripts (20 files)
Update script references, mark deprecated scripts

### Phase 4: System Documentation (50+ files)
Systematic replacement in guides, principles, system docs

### Phase 5: Bootstrap Artifacts
Update or add deprecation warnings

### Phase 6: Verification
- Grep entire workspace (excluding Archives/Inbox)
- Verify no active references remain
- Log to squawk if any issues encountered

---

## Risk Mitigation

1. **Git commit before starting** (capture current state)
2. **Process in phases** (critical files first)
3. **Test after each phase** (verify system still works)
4. **Squawk log any issues** (track problems for later review)
5. **Skip archives** (historical preservation)

---

## Success Criteria

✅ Zero active references in:
- Critical system files (N5.md, prefs.md, personas)
- Active recipes
- Active scripts
- Active documentation

✅ All references updated to:
- recipes.jsonl (for recipe index)
- Recipe-first workflows
- Clear deprecation notices where needed

✅ System verified functional after changes

---

**Ready to execute.**
