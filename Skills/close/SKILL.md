---
name: close
description: |
  Universal close skill. Just say "close" and it auto-routes to the right close skill
  (thread-close, drop-close, or build-close) based on SESSION_STATE context.
compatibility: Created for Zo Computer
metadata:
  author: n5os-ode
---

# Close — Universal Router

A single entry point for closing any conversation context. Instead of remembering which close skill to invoke, just say "close" and this skill determines the correct one automatically.

## How It Works

The router reads `SESSION_STATE.md` from the current conversation workspace and inspects the active context to determine which close skill applies:

### Routing Logic

1. **Drop context detected** (`drop_id` present in session state) → **drop-close**
   - The conversation is a Pulse worker executing a Drop. Close writes a structured deposit JSON for the orchestrator.

2. **Build context detected** (`build_slug` present, no `drop_id`) → **build-close**
   - The conversation is a build-level orchestration session. Close aggregates deposits, synthesizes decisions and learnings, and generates the build AAR.

3. **No build/drop context** → **thread-close**
   - A normal interactive conversation. Close summarizes progress, lists artifacts, and finalizes session state.

### Fallback

If `SESSION_STATE.md` is missing or unreadable, the router defaults to **thread-close** since that's the safest and most common case.

## Usage

```bash
python3 Skills/close/scripts/router.py --convo-id <conversation_id>
```

### Flags

| Flag | Description |
|------|-------------|
| `--convo-id` | Conversation ID (used to locate the workspace) |
| `--dry-run` | Print which close skill would be invoked without executing anything |

## Script

- `scripts/router.py` — Reads session state context and prints the target close skill.
