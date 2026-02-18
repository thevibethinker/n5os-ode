---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
type: drop_brief
build_slug: n5os-bootstrap
drop_id: D1
wave: 1
status: pending
---

# D1: Payload Curation

**Build:** n5os-bootstrap
**Wave:** 1 (no dependencies)
**Title:** [n5os-bootstrap] D1: Payload Curation

---

## Objective

Curate and package all N5OS philosophy and infrastructure content into the payload directory structure. This is the "seed" content that will be installed on target instances.

---

## Scope

### Files to Create

```
Skills/n5os-bootstrap/
├── payload/
│   ├── principles/           # P0-P39
│   │   ├── architectural_principles.md
│   │   ├── P24-simulation-over-doing.md
│   │   ├── P25-code-is-free.md
│   │   ├── P26-fast-feedback-loops.md
│   │   ├── P27-nemawashi-mode.md
│   │   ├── P28-plans-as-code-dna.md
│   │   ├── P29-focus-plus-parallel.md
│   │   ├── P30-maintain-feel-for-code.md
│   │   ├── P31-own-the-planning-process.md
│   │   ├── P32-simple-over-easy.md
│   │   ├── P33-old-tricks-still-work.md
│   │   ├── P34-secrets-management.md
│   │   └── P35-P39_building_fundamentals.md
│   │
│   ├── safety/
│   │   ├── safety.md
│   │   ├── file-protection.md
│   │   ├── folder-policy.md
│   │   └── safety-rules.md
│   │
│   ├── operations/
│   │   ├── planning_prompt.md
│   │   ├── conversation-end-v5.md
│   │   ├── conversation-initialization.md
│   │   ├── debug-logging-auto-behavior.md
│   │   ├── recipe-execution-guide.md
│   │   └── scheduled-task-protocol.md
│   │
│   ├── personas/
│   │   ├── INDEX.md
│   │   ├── vibe_architect_persona.md
│   │   ├── vibe_builder_persona.md
│   │   ├── vibe_debugger_persona.md
│   │   ├── vibe_researcher_persona.md
│   │   ├── vibe_strategist_persona.md
│   │   ├── vibe_teacher_persona.md
│   │   └── vibe_writer_persona.md
│   │
│   ├── workflows/
│   │   ├── debugger_workflow.md
│   │   ├── strategist_workflow.md
│   │   ├── teacher_workflow.md
│   │   ├── writer_workflow.md
│   │   └── researcher_workflow.md
│   │
│   ├── voice/
│   │   └── anti-patterns.md
│   │
│   └── state/
│       └── SESSION_STATE.template.md
```

### Source Files

| Payload | Source Location |
|---------|-----------------|
| principles/ | `Personal/Knowledge/Architecture/principles/` |
| safety/ | `N5/prefs/system/` |
| operations/ | `N5/prefs/operations/` |
| personas/ | `Documents/System/personas/` |
| workflows/ | `N5/prefs/workflows/` |
| voice/ | Synthesize from N5/data/voice_library.db |
| state/ | Create from `.claude/session-context.md` pattern |

### Must NOT Touch

- `Skills/n5os-bootstrap/scripts/` (D2's scope)
- `Skills/n5os-bootstrap/config/` (D3's scope)
- `Skills/n5os-bootstrap/templates/` (D3's scope)
- `Skills/n5os-bootstrap/SKILL.md` (D5's scope)

---

## MUST DO

1. **Create directory structure** under `Skills/n5os-bootstrap/payload/`

2. **Copy principles:**
   - All files from `Personal/Knowledge/Architecture/principles/`
   - Include the index (architectural_principles.md) and all P24-P39 files

3. **Copy safety protocols:**
   - safety.md, file-protection.md, folder-policy.md, safety-rules.md
   - Remove any va-specific paths (make generic with `{{WORKSPACE}}` placeholders)

4. **Copy operational protocols:**
   - planning_prompt.md
   - conversation-end-v5.md  
   - conversation-initialization.md
   - debug-logging-auto-behavior.md
   - recipe-execution-guide.md
   - scheduled-task-protocol.md

5. **Copy persona definitions:**
   - All vibe_*_persona.md files (7 personas + INDEX)
   - Remove persona IDs (those are va-specific UUIDs)

6. **Copy workflows:**
   - All 5 workflow files from N5/prefs/workflows/

7. **Create voice anti-patterns:**
   - Export key anti-patterns from voice_library.db
   - Include: corporate speak patterns, filler patterns, over-hedging
   - Create clean markdown doc

8. **Create state template:**
   - Generic SESSION_STATE.md template
   - Include placeholders for instance config

9. **Sanitize all files:**
   - Replace hardcoded paths with `{{WORKSPACE}}` where appropriate
   - Remove va-specific UUIDs, handles, or personal references
   - Keep content generic but functional

---

## MUST NOT DO

- Do NOT create scripts (install.py, etc.) — that's D2
- Do NOT create config files — that's D3
- Do NOT create Jinja2 templates — that's D3
- Do NOT modify SKILL.md — that's D5
- Do NOT include nutritionist/trainer personas (va-only)
- Do NOT include personal data or PII

---

## Expected Output

### Deposit Structure

```yaml
drop_id: D1
status: complete
files_created:
  - Skills/n5os-bootstrap/payload/principles/*.md (13 files)
  - Skills/n5os-bootstrap/payload/safety/*.md (4 files)
  - Skills/n5os-bootstrap/payload/operations/*.md (6 files)
  - Skills/n5os-bootstrap/payload/personas/*.md (8 files)
  - Skills/n5os-bootstrap/payload/workflows/*.md (5 files)
  - Skills/n5os-bootstrap/payload/voice/anti-patterns.md (1 file)
  - Skills/n5os-bootstrap/payload/state/SESSION_STATE.template.md (1 file)
total_files: 38
sanitization_notes:
  - Removed persona UUIDs
  - Replaced /home/workspace paths with {{WORKSPACE}}
  - Excluded va-only personas (nutritionist, trainer)
```

### Verification Commands

```bash
# Count payload files
find Skills/n5os-bootstrap/payload -name "*.md" | wc -l
# Should be ~38

# Check no hardcoded paths remain
grep -r "/home/workspace" Skills/n5os-bootstrap/payload/ | grep -v "{{WORKSPACE}}"
# Should return nothing

# Check no persona UUIDs
grep -r "[0-9a-f]\{8\}-[0-9a-f]\{4\}" Skills/n5os-bootstrap/payload/personas/
# Should return nothing
```

---

## Context Files to Read

Before starting, read these to understand the content:

1. `file 'Personal/Knowledge/Architecture/principles/architectural_principles.md'` — Principles overview
2. `file 'N5/prefs/system/safety.md'` — Safety protocol structure
3. `file 'Documents/System/personas/INDEX.md'` — Persona system overview
4. `file '.claude/session-context.md'` — State tracking pattern

---

## Build Lesson Ledger

Check ledger at start: `python3 Skills/pulse/scripts/pulse_learnings.py read n5os-bootstrap`

Log lessons during work when you discover something other drops should know.
