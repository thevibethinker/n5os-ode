# Command Index — Quick Reference

**Version:** 1.0\
**Last Updated:** 2025-10-10\
**Purpose:** Quick reference to available N5 commands

**Authoritative Source:** `file N5/config/commands.jsonl` \
**Auto-Generated Docs:** `file N5/commands.md` 

---

## Most-Used Commands

- `lists-add` — Add an item to a list with intelligent assignment
- `lists-move` — Move an item from one list to another atomically
- `docgen` — Generate command catalog and update prefs Command Index from commands.jsonl
- `index-rebuild` — Rebuild the N5 system index from source files
- `git-check` — Quick audit for overwrites or data loss in staged Git changes
- `thread-export` — Export conversation thread to structured AAR format

---

## ⚠️ Command-First Approach

**CRITICAL POLICY:** Always check `file N5/config/commands.jsonl`  BEFORE performing any system operation manually.

### Enforcement Rules

1. **Check before acting:** Search commands.jsonl for relevant commands before writing scripts or manual operations
2. **Use registered commands:** If a command exists, use it via `command N5/commands/<name>.md` 
3. **Never bypass:** Do not replicate command functionality manually
4. **Suggest improvements:** If command doesn't fit needs, propose enhancement rather than bypassing

### Specific Violations to Prevent

**❌ Thread Exports:**

- NEVER create manual markdown exports in workspace root
- NEVER create ad-hoc export directories (`/home/workspace/ExportedThreads/`, `/home/workspace/Exports/`)
- ALWAYS use `command N5/commands/thread-export.md` 
- ALL thread exports MUST go to `N5/logs/threads/`

**✓ Correct Pattern:**

```markdown
User: "Export this thread"
AI: Uses command 'N5/commands/thread-export.md'
Result: Structured export in N5/logs/threads/YYYY-MM-DD-HHMM_title_suffix/
```

**❌ Wrong Pattern:**

```markdown
User: "Export this thread"
AI: Creates /home/workspace/ExportedThreads/thread-summary.md
Result: SSOT violation, directory proliferation
```

### Why This Matters

- **P2 (SSOT):** Single canonical location prevents confusion
- **P8 (Minimal Context):** Eliminates need to check multiple locations
- **P20 (Modular):** Commands encapsulate system operations properly
- **Consistency:** Naming conventions, structure, and format enforced
- **Maintainability:** Changes to export format update once, apply everywhere

---

## Timeline & History

- `timeline` — View n5.os development timeline and system history
- `timeline-add` — Add new entry to n5.os development timeline

---

## System Management

- `system-upgrades-add` — Interactive command for adding items to the N5 system upgrades list with validation and safety features
- `grep-search-command-creation` — Automated command creation workflow using grep_search, create_command_draft, validate_command

---

## Usage

All commands are defined in `file N5/config/commands.jsonl`  and can be referenced using:

```markdown
```

`command N5/commands/<command-name>.md` 

To regenerate command documentation:

```markdown
```

`command N5/commands/docgen.md` 

---

## Related Resources

- Commands registry → `file N5/config/commands.jsonl` 
- Auto-generated docs → `file N5/commands.md` 
- Individual command docs → `file N5/commands/*.md` 