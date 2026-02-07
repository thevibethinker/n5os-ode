---
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
type: build_plan
status: ready
provenance: con_UWx2xMNELdT6MUle
---

# Plan: Skills.sh Importer for N5 OS

**Objective:** Create a skill that imports skills from skills.sh (and any GitHub-hosted agentskills.io-compliant repo) into the N5 OS Skills/ directory with proper frontmatter transformation.

**Trigger:** V discovered skills.sh ecosystem has 100+ high-value skills that could enhance N5 capabilities.

**Key Design Principle:** Plans are FOR AI execution. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [x] What's the skills.sh skill format? → Same agentskills.io spec as N5 (SKILL.md + scripts/ + references/)
- [x] Where do skills.sh skills live? → GitHub repos (e.g., `vercel-labs/agent-skills`, `anthropics/skills`)
- [x] What N5-specific frontmatter needs adding? → `created`, `last_edited`, `version`, `provenance`, `compatibility`, `metadata.author`
- [x] Should we support bulk import? → Yes, with `--all` flag for repos with multiple skills

---

## Checklist

### Phase 1: Core Implementation
- ☐ Create `Skills/skills-importer/scripts/import_skill.py` CLI
- ☐ Implement GitHub fetching (raw content API)
- ☐ Implement frontmatter transformation (add N5 fields)
- ☐ Implement skill validation
- ☐ Implement installation to `Skills/<name>/`
- ☐ Create `Skills/skills-importer/SKILL.md` documentation
- ☐ Test: Import `anthropics/skills/frontend-design` successfully

---

## Phase 1: Core Implementation

### Affected Files
- `Skills/skills-importer/SKILL.md` - CREATE - Skill documentation
- `Skills/skills-importer/scripts/import_skill.py` - CREATE - Main CLI script
- `Skills/skills-importer/references/format-mapping.md` - CREATE - Format transformation reference

### Changes

**1.1 Core Import Script (`import_skill.py`):**

CLI interface:
```
python3 Skills/skills-importer/scripts/import_skill.py <source> [options]

Arguments:
  source              GitHub reference: owner/repo/skill-name OR owner/repo (with --all)

Options:
  --all               Import all skills from repo
  --list              List available skills in repo (don't import)
  --dry-run           Show what would be imported without doing it
  --force             Overwrite existing skill if present
  --dest <name>       Custom destination slug (default: skill name)
```

Source resolution:
1. Parse `owner/repo/skill-name` format
2. Detect if repo uses `skills/` subdirectory (like vercel-labs/agent-skills)
3. Fetch SKILL.md via raw.githubusercontent.com
4. Fetch supporting files (scripts/, references/, assets/)

Frontmatter transformation:
```yaml
# INPUT (skills.sh format)
---
name: frontend-design
description: Create distinctive frontend interfaces...
license: Complete terms in LICENSE.txt
---

# OUTPUT (N5 format)
---
name: frontend-design
description: Create distinctive frontend interfaces...
compatibility: Imported from skills.sh
metadata:
  author: anthropics (imported)
  source: anthropics/skills/frontend-design
  imported_at: 2026-02-07
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
provenance: skills-importer
---
```

Tool mapping (in SKILL.md body, not automated):
- Skills may reference Claude Code tools; we'll add a note but not auto-transform
- N5 users adapt tool calls manually or Zo handles it at runtime

**1.2 SKILL.md Documentation:**

Document:
- Installation (it's already a skill)
- Usage examples
- Source formats supported
- Transformation rules
- Popular skills to import (curated list from skills.sh leaderboard)

**1.3 Format Mapping Reference:**

Create `references/format-mapping.md` documenting:
- skills.sh → N5 field mapping
- Tool name differences (if any)
- Known incompatibilities

### Unit Tests
- Import `anthropics/skills/frontend-design`: Should create `Skills/frontend-design/SKILL.md` with N5 frontmatter
- Import with `--dry-run`: Should print transformation without writing files
- Import with `--list`: Should enumerate skills in a multi-skill repo
- Import existing skill without `--force`: Should fail gracefully
- Import from `vercel-labs/agent-skills`: Should handle `skills/` subdirectory structure

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Drop | Status |
|------------|------|--------|
| `Skills/skills-importer/scripts/import_skill.py` | D1.1 | ✓ |
| GitHub fetching logic | D1.1 | ✓ |
| Frontmatter transformation | D1.1 | ✓ |
| Validation logic | D1.1 | ✓ |
| File installation | D1.1 | ✓ |
| `Skills/skills-importer/SKILL.md` | D1.2 | ✓ |
| `Skills/skills-importer/references/format-mapping.md` | D1.2 | ✓ |
| Curated import list | D1.2 | ✓ |

### Token Budget Summary

| Drop | Brief (tokens) | Files (tokens) | Total % | Status |
|------|----------------|----------------|---------|--------|
| D1.1 | ~2,500 | ~5,000 | 3.75% | ✓ |
| D1.2 | ~2,000 | ~3,000 | 2.5% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE Drop (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All Drops within 40% token budget
- [x] Wave dependencies are valid (both Drops in W1, no deps)

---

## Drop Briefs

| Wave | Drop | Title | Brief File |
|------|------|-------|------------|
| 1 | D1.1 | Core Import Script | `drops/D1.1-import-script.md` |
| 1 | D1.2 | Skill Documentation | `drops/D1.2-skill-docs.md` |

---

## Success Criteria

1. `python3 Skills/skills-importer/scripts/import_skill.py anthropics/skills/frontend-design` creates a valid N5 skill
2. Imported skill has correct N5 frontmatter (created, version, provenance, metadata.source)
3. `--list` shows available skills in multi-skill repos
4. `--dry-run` shows transformation without writing
5. Skill documentation clearly explains usage and lists high-value skills to import

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| GitHub API rate limiting | Use raw.githubusercontent.com (no auth needed), cache responses |
| Skill references unavailable tools | Document tool mapping, let Zo adapt at runtime |
| Inconsistent skill structures | Validate SKILL.md exists before import, warn on missing scripts/ |
| Name collisions with existing skills | Check `Skills/<name>/` exists, require `--force` to overwrite |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. Consider NOT transforming tool references automatically — let the model adapt at runtime
2. Add a "popularity" field from skills.sh install counts for prioritization

### Incorporated:
- Tool references stay as-is; Zo handles mapping at invocation time (reduces complexity)
- Added `metadata.source` to preserve lineage

### Rejected (with rationale):
- Popularity tracking: Adds API complexity; users can check skills.sh leaderboard directly
