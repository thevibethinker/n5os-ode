---
created: 2025-12-10
last_edited: 2025-12-10
version: 1.0
---

# Reasoning Pattern: LLM-First Script Design

## Pattern Name
LLM-First Script Design

## Context
When building scripts that work with LLM-driven workflows (worker spawning, build orchestration, content generation, etc.)

## Problem
Scripts that try to extract semantic meaning from files using regex patterns fail when:
- Field names don't match exactly
- Values are placeholders (TBD, N/A)
- The richest context is in unexpected fields
- File formats change

**Anti-pattern example:**
```python
# BAD: Regex trying to understand context
pattern = r"^\*\*Focus:\*\*\s*(.+)$"
match = re.search(pattern, content)
focus = match.group(1) if match else "Not specified"
```

## Solution

**Invert the responsibility:**

| What | Who Handles | Why |
|------|-------------|-----|
| Understanding context | LLM | Semantic understanding is what LLMs do |
| Deciding what to do | LLM | Judgment requires understanding |
| Providing structured input | LLM | LLM knows what matters |
| File I/O | Script | Mechanical, deterministic |
| Timestamps/IDs | Script | Mechanical, deterministic |
| Database updates | Script | Mechanical, deterministic |

**Good pattern:**
```python
# GOOD: Script accepts context from LLM as structured JSON
parser.add_argument('--context', help='JSON context from LLM')

def main(args):
    context = json.loads(args.context)
    # Script just handles mechanics with LLM-provided semantics
    write_file(context['instruction'], context['parent_focus'], ...)
```

## Implementation

1. **Add `--context` JSON argument** to accept LLM-provided context
2. **Keep legacy mode** as fallback (parse files if no context provided)
3. **Improve legacy parsing** to try multiple field names, filter placeholders
4. **Add `--generate-ids` mode** to return IDs for LLM to use manually

## Examples

### spawn_worker.py v2
```bash
# LLM provides full context
python3 spawn_worker.py --parent con_XXX --context '{
    "instruction": "Build OAuth module",
    "parent_focus": "Authentication system",
    "parent_status": "Database complete"
}'
```

### build_orchestrator_v2.py
```bash
# LLM provides build plan
python3 build_orchestrator_v2.py init --project "auth" --plan '{
    "workers": [...],
    "key_decisions": [...]
}'
```

## Applicability

Use this pattern when:
- Script needs context that an LLM already has
- Script currently uses regex to parse semantic content
- Script output quality depends on understanding context
- Multiple LLMs might call the script (different conversations)

Don't use when:
- Script operates purely on mechanical data (file sizes, timestamps)
- Context is truly deterministic (git status, file existence)
- No LLM is involved in the workflow

## Related Patterns

- **Mechanics vs Semantics Split**: Scripts handle mechanics, LLMs handle semantics
- **JSON Contract**: Structured JSON as the interface between LLM and script
- **Graceful Degradation**: Fallback to file parsing when no context provided

