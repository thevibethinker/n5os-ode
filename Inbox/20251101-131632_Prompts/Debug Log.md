---
description: |
  Log problem→hypothesis→outcome cycles during debugging to track attempts and detect circular patterns.
  Use when debugging complex issues to maintain situational awareness.
tags:
  - debugging
  - logging
  - build
  - problem-solving
tool: true
---

# Debug Log

Track debugging attempts to detect circular patterns and maintain situational awareness.

## When to Use

- Complex debugging sessions with multiple attempts
- Build threads where solutions aren't obvious
- After 2-3 failed attempts at fixing an issue
- When you feel like you're going in circles

## Usage

### Log a Debug Attempt

```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id <current_conversation_id> \
  --component "component/file name" \
  --problem "Description of the problem" \
  --hypothesis "What you think will fix it" \
  --actions "Action taken 1" "Action taken 2" \
  --outcome success|failure|partial \
  --notes "Additional context or learnings"
```

### View Recent Attempts

```bash
python3 /home/workspace/N5/scripts/debug_logger.py recent \
  --convo-id <current_conversation_id> \
  --n 5 \
  --format display
```

### Check for Circular Patterns

```bash
python3 /home/workspace/N5/scripts/debug_logger.py patterns \
  --convo-id <current_conversation_id> \
  --window 10 \
  --threshold 3
```

## Example

```bash
# After trying to fix a rate limit issue
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id con_ABC123 \
  --component "api_client.py" \
  --problem "Rate limit 429 errors on API calls" \
  --hypothesis "Add exponential backoff will reduce rate limit hits" \
  --actions "Added backoff decorator" "Set intervals to 5s, 15s, 45s" \
  --outcome success \
  --notes "Worked after implementing proper retry logic"
```

## Integration with Operator Persona

The Vibe Operator persona will:
- Auto-check patterns after 3+ failures
- Suggest loading Debugger mode if circular pattern detected
- Review recent attempts when stuck

## Log Location

Logs are stored in the conversation workspace:
`/home/.z/workspaces/con_<conversation_id>/DEBUG_LOG.jsonl`

## Pattern Detection

Automatically detects when:
- Same component has 3+ similar problems
- Problems have >70% text similarity OR >60% keyword overlap
- Issues occur within last 10 attempts

When detected, suggests:
- Different approach
- Loading Debugger mode with planning prompt
- Asking V for guidance
