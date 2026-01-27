# N5 Operating System

**Version:** 5.0  
**Status:** Production Active

---

## Quick Start

**System Documentation:** `file 'Documents/N5.md'`  
**Preferences:** `file 'N5/prefs/prefs.md'`  
**Architectural Principles:** `file 'Knowledge/architectural/architectural_principles.md'`

---

## Structure

```
N5/
├── commands/          Command workflows (meeting-process, etc.)
├── scripts/           Python automation scripts
├── prefs/             System preferences and protocols
├── config/            Configuration files
├── lists/             Action tracking (todos, lessons, etc..)
├── logs/              Thread exports and system logs
├── records/           Meeting records and processing outputs
├── Skills/            Automated workflow skills (meeting-ingestion, pulse, etc.)
└── System Documentation/  Quick reference guides
```

---

## Key Systems

- **Meeting Intelligence:** `command 'meeting-process'`
- **Thread Management:** `command 'thread-export'`
- **Meeting Ingestion:** `skill 'meeting-ingestion'` - Automated transcript processing from Google Drive
- **Build Orchestration:** `skill 'pulse'` - Automated parallel build execution system
- **Git Safety:** `python3 N5/scripts/n5_git_check.py`
- **Recipes System:** See `file 'N5/prefs/operations/recipe-execution-guide.md'`

---

## Documentation

- **Full System Tour:** `file 'Documents/N5.md'`
- **Architecture:** `file 'Knowledge/architectural/architectural_principles.md'`
- **System Docs:** `file 'Documents/System/README.md'` (guides, architecture, personas)
- **Skills:** `file 'Skills/'` (automated workflow capabilities)

---

**For detailed information, start with:** `file 'Documents/N5.md'`
