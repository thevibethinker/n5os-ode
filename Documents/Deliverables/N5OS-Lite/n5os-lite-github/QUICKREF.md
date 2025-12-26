# N5OS Lite Quick Reference Card

**Version:** 1.2.2  
**Purpose:** Common commands and workflows at a glance

---

## 🚀 Daily Workflows

### Start Your Day
```
1. "Load planning prompt" - Set framework for building
2. "Check session state" - Resume where you left off
3. "Query my lists" - Review tools/ideas/knowledge
```

### End Your Day
```
1. "Review my work" - Validate what was built
2. "Close conversation" - Archive and summarize
3. "Export thread" - Save important conversations
```

---

## 📋 List Management

| Task | Natural Language | Script |
|------|-----------------|--------|
| Add | "Add X to my tools list" | `n5_lists_add.py` |
| Find | "Find Python in lists" | `n5_lists_find.py` |
| Validate | "Check list health" | `validate_list.py` |

---

## 🧠 Knowledge Management

| Task | Natural Language | Script |
|------|-----------------|--------|
| Ingest | "Ingest this knowledge" | `n5_knowledge_ingest.py` |
| Find | "Search knowledge for X" | `n5_knowledge_find.py` |

---

## 👥 Persona Switching

```
"Switch to Builder" → Execution mode
"Switch to Strategist" → Analysis mode
"Switch to Architect" → Design mode
"Switch back to Operator" → Default mode
```

---

## 🏗️ Build Workflows

### Simple Build
```
1. Load planning prompt
2. Think → Plan → Execute
3. Review work
4. Close conversation
```

### Complex Build (Parallel)
```
1. Load orchestrator protocol
2. Spawn Worker 1 (backend)
3. Spawn Worker 2 (frontend)
4. Spawn Worker 3 (tests)
5. Integrate results
```

---

## 🔍 Common Commands

### File Operations
```
"Protect this directory" → file_guard.py
"Check if protected" → n5_protect.py
"Show dry-run" → All scripts support --dry-run
```

### State Management
```
"Init session state" → session_state_manager.py init
"Update state" → session_state_manager.py update
"Check state" → session_state_manager.py check
```

### Documentation
```
"Generate docs" → n5_docgen.py
"Rebuild index" → index_rebuild.py
```

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Check scripts/ directory has all .py files |
| "Permission denied" | chmod +x scripts/*.py |
| "Directory not found" | Run bootstrap.sh first |
| "Invalid JSON" | Run validate_list.py |
| "Schema mismatch" | Check ASSUMPTIONS.md |

---

## 🎯 Principles Quick Ref

| ID | Name | When To Apply |
|----|------|---------------|
| P1 | Human-Readable First | Creating outputs |
| P2 | Single Source of Truth | Storing facts |
| P7 | Dry-Run by Default | Destructive ops |
| P15 | Complete Before Claiming | Progress reports |
| P21 | Document Assumptions | Building systems |
| P36 | Orchestration Pattern | Complex builds |

---

## 📁 Directory Structure

```
workspace/
├── .n5os/
│   ├── lists/        # Canonical list storage
│   ├── personas/     # Persona definitions
│   └── config/       # System configuration
├── Prompts/          # Reusable workflows
├── Knowledge/        # Long-term knowledge
├── Documents/        # Active work
├── Lists/            # Legacy (symlink to .n5os/lists)
└── Inbox/            # Temporary staging
```

---

## 🔗 Essential Files

- `QUICKSTART.md` - 15-minute tutorial
- `INSTALLATION.md` - Setup guide
- `ASSUMPTIONS.md` - Dependencies & assumptions
- `ARCHITECTURE.md` - System design
- `TROUBLESHOOTING.md` - Common issues

---

**Print this page. Keep it handy. Reference often.**

*Quick Reference v1.2.2 | 2025-11-03*
