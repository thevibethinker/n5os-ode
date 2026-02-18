---
created: 2026-02-11
last_edited: 2026-02-11
version: 1.0
provenance: con_qwBKVmsu7qZOk7DW
name: learning-logger
description: |
  Log learnings from zoputer's client interactions to a dedicated branch for va review.
  Commits structured markdown files with metadata, respects autonomy config permissions,
  and pushes to GitHub substrate for review workflow integration.
compatibility: Created for Zo Computer - Zoputer Consultancy Stack
metadata:
  author: va.zo.computer
  build: zoputer-autonomy-v2
  drop: D4.2
---

# Learning Logger

Provides a CLI for zoputer to log learnings discovered during client interactions. Learnings are committed to the `zoputer/learnings` branch for va review before potential merge.

## Purpose

When zoputer discovers something worth remembering from client interactions (preferences, domain knowledge, workflow improvements, mistakes to avoid), this skill:

1. Creates a structured markdown file with metadata
2. Validates write permission against autonomy config
3. Commits to the `zoputer/learnings` branch
4. Pushes to GitHub substrate for va review

## Usage

```bash
# Log a client preference
python3 Skills/learning-logger/scripts/log_learning.py \
  --learning "Client X prefers async communication over meetings" \
  --source "con_abc123" \
  --category "client-preferences"

# Log domain knowledge
python3 Skills/learning-logger/scripts/log_learning.py \
  --learning "Healthcare RFPs require HIPAA compliance section" \
  --source "con_def456" \
  --category "domain-knowledge"

# Dry run to see what would be created
python3 Skills/learning-logger/scripts/log_learning.py \
  --learning "Test learning" \
  --source "test" \
  --category "workflow-improvements" \
  --dry-run

# List recent learnings
python3 Skills/learning-logger/scripts/log_learning.py --list

# Show help
python3 Skills/learning-logger/scripts/log_learning.py --help
```

## Categories

| Category | Purpose |
|----------|---------|
| `client-preferences` | How clients like to work, communication styles, timing preferences |
| `domain-knowledge` | Industry-specific or technical learnings from engagements |
| `workflow-improvements` | Better ways to accomplish tasks discovered through practice |
| `mistakes-to-avoid` | What not to do - lessons from errors or near-misses |

## Output Format

Each learning creates a markdown file in `Learnings/<category>/`:

```markdown
---
created: 2026-02-11
source: con_abc123
category: client-preferences
logged_by: zoputer
status: pending_review
---

# Learning

Client X prefers async communication over meetings
```

## Integration

- **Autonomy Config**: Reads from `N5/config/zoputer_autonomy.yaml` to validate write permissions
- **Git Substrate Sync**: Uses similar git patterns for commit and push
- **Review Workflow**: Pushes to `zoputer/learnings` branch; GitHub Actions (D4.3) notifies va

## Branch Strategy

- Learnings push to `zoputer/learnings` branch (not main)
- va reviews via GitHub PR or direct inspection
- Approved learnings can be merged or elevated to Knowledge/
