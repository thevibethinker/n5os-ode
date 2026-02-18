---
created: 2026-02-11
last_edited: 2026-02-11
version: 1.0
provenance: con_Rne6A1Z70igdePFs
---

# Skills Specification

This document defines the canonical specification for Zo Computer skills, following the [Agent Skills specification](https://agentskills.io/specification) with SkillRL-inspired enhancements for evolutionary management.

## Directory Structure

Skills are packaged under `Skills/<skill-dir>/` with this structure:

```
Skills/<skill-dir>/
├── SKILL.md                # Required: frontmatter + instructions
├── scripts/               # Optional: executable code (Python, TypeScript/Bun, Bash)
├── references/            # Optional: detailed docs, API notes
└── assets/               # Optional: static resources (templates, images, data files)
```

The `skill-dir` must be a slug (lowercase letters/numbers/hyphens) derived from the skill name and must match the `name` field in frontmatter.

## SKILL.md Frontmatter Specification

### Required Fields

```yaml
---
name: skill-name                    # REQUIRED: 1–64 chars, lowercase letters/numbers/hyphens only
description: |                      # REQUIRED: 1–1024 chars, what the skill does and when to use it
  Multi-line description explaining what this skill does
  and when to use it.
---
```

### Standard Fields

```yaml
---
compatibility: Created for Zo Computer    # Platform/environment requirements
metadata:                                # Key-value map for extra metadata
  author: va.zo.computer                 # Skill author
created: 2026-02-11                      # Creation date (YYYY-MM-DD)
last_edited: 2026-02-11                  # Last modification date
version: 1.0                             # Semantic version
provenance: con_XXX                      # Originating conversation or build
allowed-tools:                           # Optional: space-delimited Zo tool names
  - Bash
  - Read
---
```

### SkillRL Evolution Fields (New)

These fields support the evolutionary skill management system:

```yaml
---
# EVOLUTION TRACKING
scope: universal                         # REQUIRED for new skills: universal|domain|task-specific
domain: debugging                        # REQUIRED if scope=domain: debugging|writing|research|building|...
created_from: lesson                     # How skill was created: lesson|pattern|manual
usage_count: 0                          # Auto-incremented when skill is activated
last_used: null                          # ISO timestamp, auto-updated when used
last_refined: 2026-02-11                 # When skill was last updated
refinement_history:                      # Change log for evolution tracking
  - date: 2026-02-11
    source: build:skillrl-integration
    change: Initial creation
---
```

### Scope Definitions

- **universal**: Skills applicable across all domains (e.g., `thread-close`, `systematic-debugging`)
- **domain**: Skills specific to a domain (e.g., `research`, `writing`, `building`)
- **task-specific**: Skills for narrow use cases (e.g., `careerspan-jd-intake`)

### Domain Categories

When `scope: domain`, specify the domain:

- `debugging` - Error diagnosis and troubleshooting
- `writing` - Content creation and communication
- `research` - Information gathering and analysis  
- `building` - Code and system development
- `data` - Data processing and analysis
- `health` - Health and wellness tracking
- `business` - Business operations and deals
- `system` - Infrastructure and maintenance

## Skill Activation Protocol

When Zo activates a skill:

1. **Read `SKILL.md`** — The body content contains instructions
2. **Record usage** — Call `python3 Skills/pulse/scripts/skill_usage.py record <skill-name>` (convention)
3. **Run scripts** — Execute scripts in `scripts/` as directed
4. **Reference docs** — Consult `references/` for detailed documentation
5. **Use assets** — Access static resources in `assets/`

## Evolution Management

Skills are managed by the Evolution Agent (`⇱ Skill Evolution Digest`):

- **Weekly analysis** — Identifies stale, unused, and failing skills
- **Usage tracking** — Monitors activation patterns
- **Refinement suggestions** — Proposes improvements based on debug logs and build lessons
- **Deprecation flow** — Archives stale skills to `Skills/_archived/`

## Validation Rules

### Name Requirements
- 1–64 characters
- Lowercase letters, numbers, hyphens only
- No leading/trailing hyphens
- No consecutive hyphens
- Must match parent directory name

### Description Requirements  
- 1–1024 characters
- Non-empty
- Clearly explain what the skill does and when to use it

### Version Requirements
- Follow semantic versioning (X.Y format minimum)
- Increment when skill content changes

## Migration Notes

- **Existing skills**: SkillRL evolution fields are optional for backward compatibility
- **New skills**: Should include evolution fields from creation
- **Legacy skills**: Will be gradually updated with evolution fields during refinements

## Examples

### Minimal Skill (Legacy Compatible)
```yaml
---
name: example-skill
description: Does something useful when needed.
---
```

### Full SkillRL-Enhanced Skill
```yaml
---
name: advanced-debugging
description: |
  Systematic debugging methodology with 5-phase approach.
  Use when encountering persistent bugs or circular fixes.
scope: universal
created_from: lesson
usage_count: 23
last_used: 2026-02-10T14:30:00Z
last_refined: 2026-02-11
refinement_history:
  - date: 2026-02-11
    source: build:skillrl-integration
    change: Added circular pattern detection
  - date: 2026-02-06
    source: con_xyz123
    change: Initial creation from debug lessons
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
created: 2026-02-06
last_edited: 2026-02-11
version: 1.1
provenance: con_xyz123
---
```

## References

- [Agent Skills Specification](https://agentskills.io/specification)
- [SkillRL Paper](https://arxiv.org/abs/2402.03310)
- Evolution Agent: `⇱ Skill Evolution Digest` scheduled agent