# N5OS Lite Naming Conventions

**Version:** 1.0  
**Purpose:** Consistent naming standards for files, folders, and tasks  
**Status:** Standard for all N5OS Lite installations

---

## Universal Principles

1. **Human-Readable** - Descriptive names > cryptic abbreviations
2. **Greppable** - Use consistent patterns for searchability  
3. **Lowercase** - All filenames lowercase (except specific conventions)
4. **Date-Aware** - Include dates where chronology matters
5. **Noun-First** - Lead with subject, not action

---

## File Naming

### General Files

**Format:** `kebab-case-with-hyphens.ext`

**Examples:**
```
✅ planning-prompt.md
✅ file-guard.py
✅ principles-index.yaml

❌ planning_prompt.md (use hyphens, not underscores)
❌ PlanningPrompt.md (use lowercase)
❌ pp.md (too cryptic)
```

### Date-Prefixed Files

**Format:** `YYYY-MM-DD-descriptive-name.ext`

**When to use:**
- Meeting notes
- Status reports
- Dated logs
- Time-bound documents

**Examples:**
```
2025-11-03-meeting-notes.md
2025-11-03-system-audit.json
2025-11-weekly-review.md
```

### Scripts

**Format:** `action_target.py` or `module_action.py`

**Examples:**
```
file_guard.py
validate_list.py  
knowledge_ingest.py
conversation_export.py
```

**Note:** Scripts use underscores (Python convention), other files use hyphens

---

## Folder Naming

### Top-Level Directories

**Format:** Title Case, no dates (permanent structure)

**Standard Structure:**
```
workspace/
├── Prompts/         # Reusable workflows
├── Lists/           # Structured data (JSONL)
├── Knowledge/       # Long-term reference
├── Documents/       # Final docs
├── Personal/        # User-specific
├── Inbox/           # Temporary staging
├── Archive/         # Completed work
└── N5/              # System files
```

**Guidelines:**
- Descriptive and clear
- Singular or plural based on contents
- No version numbers in directory names
- No dates unless archive

### Project Directories

**Format:** `kebab-case-project-name/`

**Examples:**
```
n5os-lite/
website-redesign/
api-integration/
```

### Archive Directories

**Format:** `YYYY-MM-DD-title/` or `YYYY-MM/`

**Examples:**
```
2025-11-03-meeting-analysis/
2025-11/
Archive/2025/Q4/
```

---

## Scheduled Task Naming

**Format:** `{emoji} {Action} {Subject}`

**Examples:**
```
📰 Daily Meeting Digest
🔧 Weekly List Health Check
📊 Monthly System Audit
💾 Hourly Backup
🚨 Critical Error Alert
```

**Common Emojis:**
- 📰 - Information/digest
- 🔧 - Maintenance
- 📊 - Analytics/reporting
- 💾 - Data operations
- 🚨 - Alerts/monitoring
- 📝 - Documentation
- 🎯 - Goals/objectives
- ⚡ - Quick operations

**Guidelines:**
- Action verb + clear subject
- No frequency in title (defined in RRULE)
- Consistent with file naming principles
- Easy to scan in task list

---

## List Files (JSONL)

**Format:** `category-name.jsonl`

**Examples:**
```
tools.jsonl
contacts.jsonl
ideas.jsonl
meetings.jsonl
action-items.jsonl
```

**Guidelines:**
- Plural nouns preferred
- Hyphenated multi-word names
- Always `.jsonl` extension
- Companion `.md` file auto-generated

---

## Knowledge Files

**Format:** `topic-or-entity.md`

**Examples:**
```
Knowledge/people/john-smith.md
Knowledge/technical/api-documentation.md
Knowledge/strategic/q4-2025-plan.md
```

**Guidelines:**
- Entity-based naming for people/companies
- Topic-based for concepts/systems
- Lowercase with hyphens
- Descriptive enough to grep

---

## Principle Files

**Format:** `P##_short-slug.yaml`

**Examples:**
```
P01_human_readable_first.yaml
P15_complete_before_claiming.yaml
P36_orchestration_pattern.yaml
```

**Guidelines:**
- Sequential numbering (P01, P02, ...)
- Underscore after number
- Slug matches principle name (abbreviated)
- Always YAML format

---

## Persona Files

**Format:** `persona-name.yaml`

**Examples:**
```
operator.yaml
builder.yaml
strategist.yaml
architect.yaml
```

**Guidelines:**
- Single-word names preferred
- Role-based naming
- Always YAML format
- Lowercase

---

## Prompt Files

**Format:** `action-target.md` or `verb-noun.md`

**Examples:**
```
close-conversation.md
add-to-list.md
knowledge-ingest.md
generate-documentation.md
```

**Guidelines:**
- Action verb first
- Clear target/object
- Hyphenated
- Always markdown

---

## Version Numbering

**Format:** `v{major}.{minor}.{patch}`

**Examples:**
```
v1.0.0 - Initial release
v1.1.0 - Minor feature addition
v1.1.1 - Bug fix
v2.0.0 - Major breaking change
```

**When to Version:**
- Major systems
- Public packages
- Shared workflows
- Not individual documents

---

## Special Cases

### Temporary Files

**Prefix:** `.tmp-` or place in `Inbox/`

**Examples:**
```
.tmp-download.json
Inbox/temp-processing.md
```

### Protected Directories

**Marker:** `.protected` file inside directory

**Contains:**
```json
{
  "protected": true,
  "reason": "System files",
  "created": "2025-11-03T00:00:00Z"
}
```

### Hidden Files

**Prefix:** `.` (dot)

**Use sparingly:**
```
.gitignore
.protected
.env
```

---

## Anti-Patterns

**Avoid:**
```
❌ file_v2_final_FINAL.md (versioning in filename)
❌ temp123.txt (meaningless names)
❌ MyFile.TXT (mixed case)
❌ untitled-1.md (default names)
❌ new-folder/ (non-descriptive)
❌ backup_copy_2.md (manual versioning)
```

**Instead:**
```
✅ project-report.md
✅ analysis-results.json
✅ meeting-notes.md
✅ Use git for versioning
✅ project-analysis/
✅ Use proper file naming from start
```

---

## Validation

**Check Names:**
- [ ] Lowercase (except Title Case directories)
- [ ] Descriptive and meaningful
- [ ] Hyphenated (files) or underscored (scripts)
- [ ] No version numbers in names
- [ ] Follows format conventions
- [ ] Greppable and searchable

---

## Related

- System: `filesystem_standard.md` - Directory structure
- System: `preferences_system.md` - Pref organization
- Principles: P13 (if exists) - Naming and placement

---

**Consistent naming = easier navigation, better searchability, reduced cognitive load.**

*Last Updated: 2025-11-03*
