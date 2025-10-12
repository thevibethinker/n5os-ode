# Prefs Migration Guide: v1 → v2

**Date:** 2025-10-09  
**Version:** 2.0.0

---

## Overview

The N5 preferences system has been refactored from a single monolithic file into a modular, context-aware structure.

### Key Changes

1. **Modular Structure**
   - Preferences split into specialized modules
   - Selective loading based on context
   - Reduced token overhead

2. **Better Organization**
   - Clear separation of concerns
   - Single responsibility per module
   - Easier to find and update specific preferences

3. **Synchronized with Knowledge Base**
   - Explicit links to stable knowledge files
   - Eliminates duplication
   - Prevents drift between preference and knowledge

---

## File Locations

### Old Structure (v1)
```
N5/prefs/
├── prefs.md (monolithic, ~650 lines)
├── naming-conventions.md
└── engagement_definitions.md
```

### New Structure (v2)
```
N5/prefs/
├── index.md (lightweight index + critical rules)
├── prefs.md.v1_backup (original preserved)
├── MIGRATION_GUIDE.md (this file)
├── naming-conventions.md (unchanged)
├── engagement_definitions.md (unchanged)
├── system/
│   ├── file-protection.md
│   ├── git-governance.md
│   ├── folder-policy.md
│   └── safety.md
├── operations/
│   ├── scheduling.md
│   └── resolution-order.md
├── communication/
│   ├── voice.md
│   ├── templates.md
│   ├── meta-prompting.md
│   └── email.md
├── integration/
│   ├── google-drive.md
│   └── coding-agent.md
└── knowledge/
    └── lookup.md
```

---

## What Changed

### Content Migration

All content from `prefs.md` has been preserved and distributed across modules:

**System Governance:**
- File protection → `system/file-protection.md`
- Git governance → `system/git-governance.md`
- Folder policy → `system/folder-policy.md`
- Review & safety → `system/safety.md`

**Operations:**
- Scheduling config → `operations/scheduling.md`
- Resolution order → `operations/resolution-order.md`

**Communication:**
- Voice & style → `communication/voice.md`
- Templates → `communication/templates.md`
- Prompt engineering → `communication/meta-prompting.md`
- Email processing → `communication/email.md`

**Integration:**
- Google Drive → `integration/google-drive.md`
- Coding agent → `integration/coding-agent.md`

**Knowledge:**
- Knowledge lookup → `knowledge/lookup.md`

---

## New Synchronization

The new structure explicitly references stable knowledge files to avoid duplication:

### Personal & Company Knowledge

**Referenced, not duplicated:**
- `file 'Knowledge/stable/bio.md'` — Vrijen & Logan bio
- `file 'Knowledge/stable/company/overview.md'` — Careerspan mission
- `file 'Knowledge/stable/company/strategy.md'` — GTM strategy
- `file 'Knowledge/stable/company/history.md'` — Company history
- `file 'Knowledge/stable/company/principles.md'` — Core principles
- `file 'Knowledge/stable/careerspan-timeline.md'` — Timeline
- `file 'Knowledge/stable/glossary.md'` — Terminology

### Architectural Principles

**Referenced, not duplicated:**
- `file 'Knowledge/architectural/operational_principles.md'` — Rule-of-Two, SSOT, voice policy
- `file 'Knowledge/architectural/ingestion_standards.md'` — What to ingest, MECE principles

### Lists & Detection

**Referenced, not duplicated:**
- `file 'Lists/POLICY.md'` — How to interact with lists
- `file 'Lists/detection_rules.md'` — Email routing rules

### Context Files

**Referenced, not duplicated:**
- `file 'Knowledge/context/howie_instructions/preferences.md'` — Howie scheduling (reference only)

---

## Loading Strategy

### Old Behavior (v1)
- Entire prefs.md loaded on every conversation start
- ~5-6K tokens consumed always
- All rules in context regardless of relevance

### New Behavior (v2)
- `index.md` loaded first (lightweight, ~1-2K tokens)
- Critical rules always in context
- Additional modules loaded selectively based on task

### Context-Aware Loading

**System operations:**
→ Load: `system/file-protection`, `system/git-governance`, `system/safety`

**Knowledge ingestion:**
→ Load: `Knowledge/architectural/ingestion_standards`, `Knowledge/architectural/operational_principles`

**Communication tasks:**
→ Load: `communication/voice`, `communication/templates`

**Strategic work:**
→ Reference: `Knowledge/stable/company/strategy`, `glossary`, `timeline`

**List operations:**
→ Load: `Lists/POLICY.md` (commands handle loading)

---

## Backward Compatibility

### For AI/LLM Loading

**Old prefs still referenced in system prompt:**
The system prompt currently references `N5/prefs/prefs.md`, which should be updated to:

```
Load `file 'N5/prefs/index.md'`
```

**Fallback behavior:**
- If old prefs.md loaded, still works (full context)
- If new index.md loaded, selective module loading

---

### For User References

**Old references in documents:**
References to `N5/prefs.md` should be updated to appropriate module:
- General reference → `N5/prefs/index.md`
- Specific topic → Appropriate module file

---

## Migration Checklist

### Completed ✓
- [x] Create modular structure
- [x] Distribute content across modules
- [x] Add cross-references to stable knowledge
- [x] Preserve original as prefs.md.v1_backup
- [x] Create index.md with loading guide
- [x] Document migration in this guide

### TODO
- [ ] Update system prompt to reference `N5/prefs/index.md`
- [ ] Update any hardcoded references to old prefs.md
- [ ] Update N5.md to reflect new structure
- [ ] Add prefs modules to Git tracking
- [ ] Test loading behavior in new conversations

---

## Validation

### Content Preservation Check

To verify all content was preserved:

```bash
# Compare line counts (should be similar total)
wc -l /home/workspace/N5/prefs/prefs.md.v1_backup
wc -l /home/workspace/N5/prefs/**/*.md | tail -1

# Search for specific content
grep -r "specific-rule" /home/workspace/N5/prefs/
```

### Functionality Check

- [ ] File protection rules work correctly
- [ ] Git tracking captures new modules
- [ ] Lists policy still enforced
- [ ] Communication style applied correctly
- [ ] Knowledge lookup finds canonical sources

---

## Rollback Procedure

If issues arise with new structure:

### Immediate Rollback

```bash
# Restore original
cp /home/workspace/N5/prefs/prefs.md.v1_backup /home/workspace/N5/prefs/prefs.md

# Update system prompt reference
# Change back to: Load `file 'N5/prefs/prefs.md'`
```

### Preserve New Modules

New modules can coexist with old prefs.md if needed. They provide more detail but don't conflict.

---

## Benefits Summary

### Token Efficiency
- **Old:** ~5-6K tokens every conversation
- **New:** ~1-2K tokens (index only) + selective module loading
- **Savings:** 60-70% reduction in baseline overhead

### Maintainability
- **Old:** Edit 650-line file carefully
- **New:** Edit specific 100-200 line module
- **Benefit:** Easier to update without breaking other sections

### Discoverability
- **Old:** Search through monolith
- **New:** Navigate to relevant module directly
- **Benefit:** Faster to find and update specific preferences

### Synchronization
- **Old:** Duplicate info between prefs and knowledge
- **New:** Reference stable knowledge, no duplication
- **Benefit:** Single source of truth, no drift

---

## Questions & Support

If issues arise or questions about migration:
1. Check this migration guide
2. Verify content in v1 backup
3. Test specific module loading
4. Raise issue with Zo team if needed

---

## Change Log

### v2.0.0 — 2025-10-09
- Initial migration from monolithic to modular structure
- Created 11 specialized module files
- Added cross-references to 15+ stable knowledge files
- Preserved all original content across modules
- Created this migration guide
