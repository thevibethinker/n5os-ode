# N5OS Lite File System Standard

**Version:** 1.0  
**Purpose:** Standard directory layout for N5OS Lite environments  
**Status:** Recommended structure for new installations

---

## Overview

N5OS Lite uses a consistent, purpose-driven directory structure. Each directory has a specific role in the system architecture.

## Standard Layout

```
workspace/
├── N5/                      # System core (protected)
│   ├── prefs/               # Preferences and protocols
│   │   ├── principles/      # Architectural principles (P01-P37)
│   │   ├── operations/      # Operational prompts
│   │   ├── strategic/       # Strategic frameworks
│   │   └── system/          # System documentation
│   ├── scripts/             # System utilities
│   ├── data/                # System databases
│   └── lists/               # System lists (if using)
│
├── Prompts/                 # Reusable AI workflows
│   ├── planning_prompt.md
│   ├── thinking_prompt.md
│   └── *.md                 # Custom prompts
│
├── Lists/                   # Knowledge base (JSONL)
│   ├── tools.jsonl
│   ├── resources.jsonl
│   └── *.jsonl
│
├── Knowledge/               # Long-term documentation
│   ├── architectural/       # System designs
│   ├── technical/           # Technical docs
│   └── domain/              # Domain knowledge
│
├── Personal/                # User-specific content
│   ├── Meetings/            # Meeting records
│   ├── Journal/             # Personal notes
│   └── Planning/            # Personal planning
│
├── Inbox/                   # Temporary staging
│   └── (transient files)
│
├── Documents/               # Working documents
├── Images/                  # Generated/working images
├── Records/                 # Permanent records
└── Archive/                 # Completed/obsolete

```

## Directory Purposes

### System Core: N5/

**Purpose:** Core system files, preferences, and protocols  
**Protection:** Should be marked as protected  
**Modification:** Carefully managed, version controlled

**Contents:**
- `prefs/` - System preferences, principles, protocols
- `scripts/` - Utility scripts for system operations
- `data/` - System databases (executables, indexes)
- `lists/` - Optional system-level lists

**When to edit:**
- Adding new principles
- Creating new system prompts
- Updating protocols
- Installing new utilities

**Never:**
- Delete without backup
- Bulk operations without review
- Move to different location

### Prompts/

**Purpose:** Reusable AI workflow templates  
**File Format:** Markdown with YAML frontmatter  
**Invocation:** Tell AI to load/execute by name

**Structure:**
```markdown
---
tool: true
description: Brief description
tags: [tag1, tag2]
---

# Prompt Name

Instructions...
```

**Organization:**
- Flat structure (no subdirectories for simplicity)
- Descriptive filenames: `add-to-list.md`, `close-conversation.md`
- Use frontmatter tags for categorization

### Lists/

**Purpose:** Structured knowledge base using JSONL format  
**File Format:** `.jsonl` (JSON Lines - one JSON object per line)  
**Single Source of Truth:** Lists are canonical data sources

**Structure:**
```jsonl
{"name": "Item Name", "slug": "item-name", "type": "category", "description": "...", "tags": ["tag1"], "created": "2025-01-01"}
```

**Common lists:**
- `tools.jsonl` - Tools and prompts inventory
- `resources.jsonl` - References and learning materials
- `contacts.jsonl` - Professional contacts
- `ideas.jsonl` - Ideas and possibilities

**Maintenance:**
- Use `add-to-list.md` prompt for additions
- Use `query-list.md` prompt for searches
- Validate with `scripts/validate_list.py`
- Never manually sort (preserve chronological order)

### Knowledge/

**Purpose:** Long-term documentation and reference material  
**Organization:** By type and domain

**Subdirectories:**
- `architectural/` - System designs, ADRs, technical decisions
- `technical/` - Technical documentation, guides
- `domain/` - Domain-specific knowledge
- `processes/` - Standard operating procedures

**File formats:**
- Markdown primary format
- Diagrams as embedded images or separate files
- Link between documents liberally

### Personal/

**Purpose:** User-specific content not suitable for Knowledge/  
**Privacy:** May contain PII, keep separate from shared content

**Subdirectories:**
- `Meetings/` - Meeting notes and follow-ups
- `Journal/` - Personal reflections
- `Planning/` - Personal goals and plans

### Inbox/

**Purpose:** Temporary staging for incoming content  
**Lifetime:** Short-term only (hours to days)  
**Maintenance:** Regular cleanup

**Usage patterns:**
- Download files → Process → Move to destination
- Capture quick notes → Elaborate → File appropriately
- Staging during workflows → Archive when complete

**Cleanup:**
- Review weekly
- Archive or delete items >1 week old
- Empty completely once monthly

### Documents/, Images/, Records/

**Documents/** - Active working documents  
**Images/** - Generated images, diagrams, screenshots  
**Records/** - Permanent records that need preservation

### Archive/

**Purpose:** Completed or obsolete content  
**When to archive:**
- Projects completed
- Content superseded by newer versions
- No longer actively referenced

**Organization:**
- By year: `Archive/2025/`
- By project: `Archive/project-name/`
- Maintain structure from original location

## Protection System

### Marking Directories as Protected

Create `.protected` file in directory:

```json
{
  "protected": true,
  "reason": "System core files",
  "created": "2025-11-03T00:00:00Z",
  "created_by": "system"
}
```

### Protected by Default

- `N5/` - System core
- `N5/prefs/` - Preferences
- `.git/` - Version control

### Checking Protection

```bash
python3 N5/scripts/file_guard.py check /path/to/directory
```

## Navigation Tips

### For AI

When working with files:
1. **Check current directory** structure before operations
2. **Use standard paths** (N5/, Prompts/, Lists/, etc.)
3. **Verify protection** before destructive operations
4. **Maintain organization** - files in correct directories

### For Users

- **Start here:** `README.md` in workspace root
- **Find prompts:** Browse `Prompts/` directory
- **Search lists:** Use `query-list.md` prompt
- **System docs:** Check `N5/prefs/system/`

## Migration

### From Existing System

1. **Audit current structure** - What exists?
2. **Map to standard** - Where should things go?
3. **Create directories** - Set up standard layout
4. **Move incrementally** - Don't break working systems
5. **Update references** - Fix broken links
6. **Test thoroughly** - Verify nothing broken

### From Scratch

1. Run `setup.sh` to create structure
2. Add `.protected` to `N5/`
3. Create initial lists in `Lists/`
4. Import prompts to `Prompts/`
5. Configure personas

## Principles Applied

- **P2 (SSOT):** Each type of content has one canonical location
- **P13 (Naming):** Consistent, descriptive naming
- **P20 (Modular):** Organized by purpose and lifetime
- **P5 (Safety):** Protection system prevents accidents

---

## Quick Reference

| Content Type | Location | Lifetime | Protection |
|--------------|----------|----------|------------|
| System core | `N5/` | Permanent | Protected |
| Prompts | `Prompts/` | Permanent | Standard |
| Lists | `Lists/` | Permanent | Standard |
| Knowledge | `Knowledge/` | Long-term | Standard |
| Active work | `Documents/` | Active | Standard |
| Temporary | `Inbox/` | Short-term | Standard |
| Completed | `Archive/` | Long-term | Standard |

---

**Last Updated:** 2025-11-03  
**Maintained By:** N5OS Lite Core Team
