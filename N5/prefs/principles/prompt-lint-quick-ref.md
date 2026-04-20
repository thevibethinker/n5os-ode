---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_fLt3MnecLZ4NGDs0
---

# Prompt Lint Quick Reference

One-page reference for writing high-leverage Drop briefs and prompts.

## Do's and Don'ts

| Do ✅ | Don't ❌ |
|--------|----------|
| `"Create X"` | `"Try to create X"` |
| `"Implement function F"` | `"If possible, implement F"` |
| `"Optimize until < 1s"` | `"Optimize the code"` |
| `"Improve accuracy by 10%"` | `"Improve the accuracy"` |
| `"List all: X, Y, Z"` | `"List: X, Y, etc."` |
| `"Run within 5 minutes"` | `"Run quickly"` |
| `"Accuracy must exceed 95%"` | `"Make it accurate"` |
| `"Use active voice"` | `"Was improved by X"` |
| `"Must validate inputs"` | `"Should validate inputs"` |
| `"Complete by Friday 5pm"` | `"Complete soon"` |

## Brief Structure (Required Sections)

```markdown
## Objective
[Single sentence, what success looks like]

## Context
[Why this matters, what came before, dependencies]

## Requirements
1. [Specific task 1]
2. [Specific task 2]
...

## Success Criteria
- [ ] [Verifiable outcome 1]
- [ ] [Verifiable outcome 2]
...

## Constraints
- [What NOT to do, boundaries]
```

## Common Anti-Patterns

### "Try to" → Permits Failure
```
❌ Try to optimize the database query
✅ Optimize the database query
✅ Optimize the database query, or escalate if blocked
```

### "If possible" → Permits Skipping
```
❌ Cache the result if possible
✅ Cache the result if response time > 100ms
✅ Cache the result (always)
```

### "Improve X" → No Target
```
❌ Improve error handling
✅ Improve error handling by adding specific exceptions
✅ Improve error handling until user gets actionable feedback
```

### "Optimize" → No Criteria
```
❌ Optimize the algorithm
✅ Optimize the algorithm until runtime < 1 second
✅ Optimize for memory usage (< 50MB)
```

### Vague Quantities
```
❌ Check some of the files
✅ Check all .json files in the directory

❌ Run a few tests
✅ Run all 12 unit tests
```

### Vague Timing
```
❌ Respond quickly
✅ Respond within 200ms

❌ Complete soon
✅ Complete within 24 hours
```

### Passive Voice
```
❌ The file was updated by the script
✅ The script updated the file

❌ Error handling was improved
✅ Improved error handling
```

## Lint Score Thresholds

| Score | Status | Action |
|--------|--------|--------|
| 90+ | 🟢 Ready | No action needed |
| 70-89 | 🟡 Acceptable | Consider fixes |
| 50-69 | 🟠 Needs Attention | Fix high-severity issues |
| < 50 | 🔴 Rewrite | Rewrite recommended |

## Running the Linter

```bash
# Lint a single file
python3 N5/scripts/prompt_lint.py file path/to/brief.md

# Lint all briefs in a build
python3 N5/scripts/prompt_lint.py build watts-principles

# Get JSON output
python3 N5/scripts/prompt_lint.py file brief.md --format json
```

## Pre-Build Gate

Pulse runs `prompt_lint.py` on all Drop briefs before starting a build:
- Score < 70 → **BLOCKED** (high-severity issues must be fixed)
- Score 70-89 → **WARNINGS** shown, build proceeds
- Score ≥ 90 → No issues detected

## Remember: 100x Leverage

Every word in a prompt is executed by potentially hundreds of agents.
- A vague "try to" becomes hundreds of failed attempts
- A clear "X" becomes hundreds of successful executions

Invest time in your prompts. It pays dividends at scale.
