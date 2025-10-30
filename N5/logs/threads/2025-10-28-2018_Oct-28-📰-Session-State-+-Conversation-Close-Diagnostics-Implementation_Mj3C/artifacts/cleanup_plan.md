# Commands.jsonl Cleanup Plan

## Strategy

Update active system documentation, leave historical files intact.

### Files to Update

**Core N5 Docs:**
- N5/README.md
- N5/PROTECTION_QUICK_REF.md
- N5/IMPLEMENTATION_SUMMARY.md
- N5/MAINTENANCE_SYSTEM.md
- N5/config/README.md
- N5/scripts/README.md

**Prefs (Already updated prefs.md):**
- N5/prefs/operations/conversation-end.md
- N5/prefs/operations/digest-creation-protocol.md
- N5/prefs/operations/incantum-protocol.md
- N5/prefs/operations/thread-closure-triggers.md
- N5/prefs/system/architecture-enforcement.md
- N5/prefs/system/command-triggering.md
- N5/prefs/system/commands.md
- N5/prefs/system/file-protection.md
- N5/prefs/system/git-governance.md
- N5/prefs/system/safety.md

**Recipes:**
- Recipes/Add Digest.md
- Recipes/Docgen.md
- Recipes/File Protector.md
- Recipes/Function Import System.md
- Recipes/Git Check.md
- Recipes/Prompt Import.md
- Recipes/Search Commands.md

**Key System Docs:**
- Lists/README.md
- Knowledge/architectural/principles/core.md
- Knowledge/architectural/principles/safety.md

### Files to Leave (Historical):**
- Documents/Archive/
- N5/logs/threads/
- Inbox/
- Records/
- N5/backups/
- Deliverables/
- Trash/

## Approach

Replace references with one of:
1. "DEPRECATED - See recipe-execution-guide.md"
2. "Recipes now self-executing - see Recipes/"
3. Remove reference entirely if it's in a list
