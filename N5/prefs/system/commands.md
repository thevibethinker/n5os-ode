# Command Index — Quick Reference

**Version:** 1.0  
**Last Updated:** 2025-10-10  
**Purpose:** Quick reference to available N5 commands

**Authoritative Source:** `file 'N5/config/commands.jsonl'`  
**Auto-Generated Docs:** `file 'N5/commands.md'`

---

## Most-Used Commands

- **`lists-add`** — Add an item to a list with intelligent assignment
- **`lists-move`** — Move an item from one list to another atomically
- **`docgen`** — Generate command catalog and update prefs Command Index from commands.jsonl
- **`index-rebuild`** — Rebuild the N5 system index from source files
- **`git-check`** — Quick audit for overwrites or data loss in staged Git changes

---

## Timeline & History

- **`timeline`** — View n5.os development timeline and system history
- **`timeline-add`** — Add new entry to n5.os development timeline

---

## System Management

- **`system-upgrades-add`** — Interactive command for adding items to the N5 system upgrades list with validation and safety features
- **`grep-search-command-creation`** — Automated command creation workflow using grep_search, create_command_draft, validate_command

---

## Usage

All commands are defined in `file 'N5/config/commands.jsonl'` and can be referenced using:
```
command 'N5/commands/<command-name>.md'
```

To regenerate command documentation:
```
command 'N5/commands/docgen.md'
```

---

## Related Resources

- Commands registry → `file 'N5/config/commands.jsonl'`
- Auto-generated docs → `file 'N5/commands.md'`
- Individual command docs → `N5/commands/*.md`
