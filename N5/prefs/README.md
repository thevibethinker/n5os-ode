# N5 Preferences System v2.0

**Date:** 2025-10-09  
**Status:** Complete

---

## Quick Start

### For AI/LLM Loading

**Primary entry point:**
```
Load: file 'N5/prefs/prefs.md'
```

This lightweight index (~1-2K tokens) contains:
- Critical always-load rules
- Module directory
- Context-aware loading guide

### For Humans

**Navigate by topic:**
- **System operations** → `system/` folder
- **Communication style** → `communication/` folder
- **Tool integrations** → `integration/` folder
- **Knowledge management** → `knowledge/` folder
- **Operational config** → `operations/` folder

---

## Structure Overview

```
N5/prefs/
├── prefs.md                      ← Start here
├── README.md                     ← This file
├── naming-conventions.md         
├── engagement_definitions.md     
├── system/                       ← System governance
│   ├── file-protection.md
│   ├── git-governance.md
│   ├── folder-policy.md
│   └── safety.md
├── operations/                   ← Operational config
│   ├── scheduling.md
│   └── resolution-order.md
├── communication/                ← Communication & voice
│   ├── voice.md
│   ├── templates.md
│   ├── meta-prompting.md
│   └── email.md
├── integration/                  ← Tool integrations
│   ├── google-drive.md
│   └── coding-agent.md
├── knowledge/                    ← Knowledge management
│   └── lookup.md
└── Archive/                      ← Historical documentation
    ├── README.md
    ├── MIGRATION_GUIDE.md
    └── OPTIMIZATION_SUMMARY.md
```

---

## Key Features

### 1. Modular Architecture
Each module has single responsibility, making it easy to find and update specific preferences without affecting others.

### 2. Selective Loading
Load only what's needed for the current context:
- Base: prefs.md (~1-2K tokens)
- Add modules as needed (~1K each)
- 60-70% reduction in token overhead vs. monolithic

### 3. Synchronized with Knowledge Base
Preferences **reference** stable knowledge files instead of duplicating content:
- `Knowledge/stable/` — Bio, company info, timeline, glossary
- `Knowledge/architectural/` — Operational principles, ingestion standards
- `Lists/` — List policies, detection rules

### 4. Clear Precedence Hierarchy
Conflicts resolved through explicit precedence order (see `operations/resolution-order.md`):
1. User's direct instruction (highest)
2. Folder POLICY.md
3. Critical safety rules
4. Specialized modules
5. Global defaults (lowest)

---

## Context-Aware Loading Guide

| Context | Load These Modules |
|---------|-------------------|
| **System operations** | `system/file-protection`, `system/git-governance`, `system/safety` |
| **Knowledge ingestion** | `Knowledge/architectural/operational_principles`, `Knowledge/architectural/ingestion_standards`, `knowledge/lookup` |
| **Communication tasks** | `communication/voice`, `communication/templates` |
| **Strategic work** | `Knowledge/stable/company/strategy`, `Knowledge/stable/glossary`, `Knowledge/stable/careerspan-timeline` |
| **List operations** | `Lists/POLICY.md` |

---

## Critical Always-Load Rules

These rules apply universally (from `prefs.md`):

### Safety
- Never schedule without explicit consent
- Always support `--dry-run`
- Require explicit approval for side-effect actions
- Always ask where to create new files

### Folder Policy Principle
Folder-specific POLICY.md files take precedence over global preferences. Always check for POLICY.md before folder operations.

---

## Synchronized Knowledge Files

Preferences reference (not duplicate) these stable knowledge files:

### Personal & Company
- `file 'Knowledge/stable/bio.md'` — V & Logan biographical info
- `file 'Knowledge/stable/company/overview.md'` — Careerspan mission & product
- `file 'Knowledge/stable/company/strategy.md'` — GTM strategy, positioning
- `file 'Knowledge/stable/company/history.md'` — Company founding story
- `file 'Knowledge/stable/company/principles.md'` — Core values & philosophy
- `file 'Knowledge/stable/careerspan-timeline.md'` — Historical timeline
- `file 'Knowledge/stable/glossary.md'` — Careerspan terminology

### Architectural

- `file 'Knowledge/architectural/ingestion_standards.md'` — What to ingest, MECE principles

### Lists & Policies
- `file 'Lists/POLICY.md'` — How to interact with lists
- `file 'Lists/detection_rules.md'` — Email routing patterns

### Context
- `file 'Knowledge/context/howie_instructions/preferences.md'` — Howie scheduling (reference)

---

## Benefits Over v1

### Token Efficiency
- **Old:** ~5-6K tokens every conversation
- **New:** ~1-2K base + selective modules
- **Savings:** 60-70% reduction

### Maintainability
- **Old:** Edit 650-line monolithic file carefully
- **New:** Edit specific 100-200 line module
- **Benefit:** Easier updates without side effects

### Discoverability
- **Old:** Search through entire monolith
- **New:** Navigate directly to relevant module
- **Benefit:** Faster to find and update

### Synchronization
- **Old:** Duplicate info between prefs and knowledge
- **New:** Reference stable knowledge, no duplication
- **Benefit:** Single source of truth, no drift

---

## Migration from v1

If you're coming from the old monolithic system:

### What Changed
- **Entry point:**
  - Old: `Load file 'N5/prefs/prefs.md'` (650-line monolith)
  - New: `Load file 'N5/prefs/prefs.md'` (284-line index)

**Original file preserved in Git history**

**Historical migration details:** See `file 'N5/prefs/Archive/MIGRATION_GUIDE.md'`

**All content preserved:** Every rule from v1 is in v2, just reorganized

**Rollback available:** Copy v1_backup to prefs.md if needed

```bash
# View the v3 entry point
cat N5/prefs/prefs.md

# If needed, restore historical versions from Git:
git log --all --full-history -- N5/prefs/prefs.md
```

---

## Next Steps for System Update

1. **Update system prompt reference:**
   - Old: `Load file 'N5/prefs/prefs.md'`
   - New: `Load file 'N5/prefs/prefs.md'`

2. **Add new modules to Git tracking:**
   ```bash
   git add N5/prefs/system/*.md
   git add N5/prefs/operations/*.md
   git add N5/prefs/communication/*.md
   git add N5/prefs/integration/*.md
   git add N5/prefs/knowledge/*.md
   git add N5/prefs/prefs.md
   git add N5/prefs/README.md
   git add N5/prefs/MIGRATION_GUIDE.md
   ```

3. **Update N5.md** to reflect new prefs structure

4. **Test loading behavior** in new conversations

---

## Support

Questions or issues with the new structure?
1. Check `file 'N5/prefs/Archive/MIGRATION_GUIDE.md'` for historical context
2. Verify content mapping between versions
3. Test specific module loading
4. Raise issue with Zo team if needed

---

## Version History

### v2.0.0 — 2025-10-09
- **Breaking change:** Refactored monolithic prefs into modular structure
- Created 11 specialized preference modules
- Synchronized with 15+ stable knowledge files
- Added context-aware loading guide
- Reduced token overhead by 60-70%
- Preserved all v1 content across modules

### v1.1 — 2025-09-20
- Added military time override
- Added safeguard note for file editing
- Consolidated from previous versions

---

**For the full structure visualization and token comparison, see the structure summary output above or contact for details.**
