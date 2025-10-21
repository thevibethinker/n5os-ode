# N5 Naming Conventions (SSOT)

**Version:** 2.0.0  
**Date:** 2025-10-16  
**Purpose:** Single source of truth for ALL naming conventions across N5 OS

---

## Overview

This document defines naming standards for:
- **Thread titles** (conversation exports)
- **Scheduled tasks** (automated operations)
- **Files** (documents, scripts, data)
- **Folders** (directory organization)
- **Execution records** (AAR archives, logs)

**Central References:**
- Emoji meanings: `file 'N5/config/emoji-legend.json'` (machine-readable)
- Emoji documentation: `file 'N5/prefs/emoji-legend.md'` (auto-generated)
- Thread titling details: `file 'N5/prefs/operations/thread-titling.md'`

---

## Universal Principles

1. **Human-Readable**: Descriptive names > cryptic abbreviations
2. **Greppable**: Use consistent patterns for searchability
3. **Emoji-Prefixed**: Use centralized emoji legend for status/category
4. **Date-Aware**: Include dates where chronology matters
5. **Noun-First**: Lead with subject, not action (see thread
[truncated]
Operational tasks (background, automated)

**Format:**
```
{emoji} {Action} {Subject}
```

**Examples:**
- `📰 Daily Meeting Prep Digest` (digest generation)
- `💾 Gdrive Meeting Pull` (data collection)
- `🔧 Weekly List Health Check` (maintenance)
- `📊 Monthly System Audit` (analytics)
- `🚨 Critical Error Alert` (monitoring)

**Emoji Selection:**
- Use centralized legend: `file 'N5/config/emoji-legend.json'`
- Common task emojis: 📰 💾 🔧 📊 🚨 📝 🎯 ⚡

**Guidelines:**
- Action verb + clear subject
- No frequency in title unless ambiguous (RRULE defines timing)
- Consistent with thread naming principles

**Reference:** `file 'N5/prefs/operations/scheduled-task-protocol.md'`

---

## File Naming

### General Files

**Format:** `kebab-case-with-hyphens.ext`

**Examples:**
- `naming-conventions.md` ✅
- `emoji-legend.json` ✅
- `naming_conventions.md` ❌ (use hyphens, not underscores)
- `NamingConventions.md` ❌ (use lowercase)

**Date-Prefixed Files:**
```
YYYY-MM-DD-{descriptive-name}.ext
```

**Examples:**
- `2025-10-16-meeting-notes.md`
- `2025-10-16-system-audit.json`

### Script Naming

**Format:** `n5_{module}_{action}.py`

**Examples:**
- `n5_thread_export.py` (thread module, export action)
- `n5_emoji_legend_sync.py` (emoji module, sync action)
- `n5_title_generator.py` (title module, generator action)

### Data Files

**Format:** `{type}-{date}.{ext}`

**Examples:**
- `daily-meeting-prep-2025-10-16.md` (digest)
- `system-audit-2025-10.json` (audit)
- `backup-2025-10-16-1430.tar.gz` (backup with time)

---

## Folder Naming

### Top-Level Directories

**Format:** Title Case (no dates, permanent structure)

**Examples:**
- `Knowledge/` - Permanent knowledge base
- `Lists/` - Action items and trackers
- `Records/` - Temporal staging area
- `Documents/` - Final documentation
- `N5/` - System OS files

### Archive Directories

**Format:** `YYYY-MM-DD-HHmm_{title}_{suffix}`

**Examples:**
- `2025-10-16-0633_Thread-Titling-System_lTIs`
- `2025-10-14-1430_CRM-Refactoring-1_xY3z`

**Components:**
- Date+time: `YYYY-MM-DD-HHmm` (sortable)
- Title: `Kebab-Case-Title` (readable)
- Suffix: `{4-char-thread-id}` (uniqueness)

---

## Execution Records

**Format:** `exec_{descriptive_name}_{timestamp}`

**Examples:**
- `exec_hello_world_test_20250920_073731`
- `exec_system_backup_20251016_140000`

**Guidelines:**
- Prefix: `exec_` (greppable)
- Description: Underscore-separated words (grep-friendly)
- Timestamp: `YYYYMMDD_HHMMSS` (sortable, no colons)

---

## Emoji Usage (Centralized)

**Single Source of Truth:** `file 'N5/config/emoji-legend.json'`

**Common Context Mappings:**

| Context | Primary Emojis | Usage |
|---------|----------------|-------|
| **Threads** | ✅ 🚧 🔗 ❌ 📰 | Status and linkage |
| **Tasks** | 📰 💾 🔧 📊 🚨 | Operation type |
| **Files** | 📝 📊 🎯 💡 🔒 | Content category |
| **Status** | ✅ 🚧 ❌ ⏸️ 🔄 | Completion state |

**Auto-Selection Priority:**
1. Explicit failures (❌, 🐛) - Highest
2. In-progress work (🚧) - High
3. Linked sequences (🔗) - Medium-high
4. Content category (📰, 🎯, etc.) - Medium
5. Completed work (✅) - Default

**Full Legend:** See `file 'N5/prefs/emoji-legend.md'` (25 emojis with detection rules)

---

## Cross-Reference Matrix

| Naming Type | Format | Emoji Source | Length Constraint | Example |
|-------------|--------|--------------|-------------------|---------|
| Thread Title | `MMM DD \| {emoji} {Title}` | Centralized | ~30 chars | `Oct 16 \| ✅ Thread Titling System` |
| Scheduled Task | `{emoji} {Action} {Subject}` | Centralized | ~40 chars | `📰 Daily Meeting Prep Digest` |
| File | `kebab-case.ext` | N/A | No limit | `naming-conventions.md` |
| Archive Dir | `YYYY-MM-DD-HHmm_{Title}_{ID}` | N/A | No limit | `2025-10-16-0633_Title_lTIs` |

---

## Validation Rules

**Threads:**
- ✅ Must include date prefix: `MMM DD |`
- ✅ Must use centralized emoji
- ✅ Must be noun-first
- ✅ Should fit in ~30 chars for UI

**Scheduled Tasks:**
- ✅ Must use centralized emoji
- ✅ Must have clear action verb
- ✅ Should not duplicate frequency (in RRULE)
- ✅ Should match operation type

**Files:**
- ✅ Must use kebab-case (except scripts with underscores)
- ✅ Must be lowercase
- ✅ Should include date if temporal
- ✅ Should be descriptive, not cryptic

---

## Sync & Maintenance

**Auto-Generated Docs:**
```bash
# Regenerate emoji legend docs
python3 N5/scripts/n5_emoji_legend_sync.py

# Output: N5/prefs/emoji-legend.md
```

**Review Schedule:**
- **Weekly:** Check for naming convention violations
- **Monthly:** Review emoji usage patterns, add new emojis if needed
- **Quarterly:** Audit all naming for consistency

---

## Version History

**2.0.0** (2025-10-16)
- Complete rewrite as centralized SSOT
- Added thread and scheduled task naming
- Integrated centralized emoji legend
- Added cross-reference matrix
- Comprehensive examples and validation rules

**1.0.0** (2025-09-20)
- Initial naming conventions for executions and files

---

## Related Documentation

- `file 'N5/config/emoji-legend.json'` - Emoji SSOT (machine-readable)
- `file 'N5/prefs/emoji-legend.md'` - Emoji documentation (auto-generated)
- `file 'N5/prefs/operations/thread-titling.md'` - Thread title details
- `file 'N5/prefs/operations/scheduled-task-protocol.md'` - Task protocol
- `file 'Knowledge/architectural/architectural_principles.md'` - System principles

---

*This document is the authoritative source for all N5 naming conventions.*