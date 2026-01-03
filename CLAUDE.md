@.claude/session-context.md

# N5OS Environment — Claude Code Integration

This project operates within V's N5OS environment on Zo Computer. This file informs you about conventions — it does not override your planning capabilities.

## Environment Context

**Owner:** V (Vrijen Attawar)  
**System:** N5OS on Zo Computer  
**Integration:** MCP bridge provides `n5_protect_check`, `n5_log_bio`, `n5_close_conversation` tools

## Protected Paths

Before delete/move operations on these directories, check with `n5_protect_check`:

| Path | Protection Reason |
|------|-------------------|
| `N5/` | System scripts and services |
| `Sites/` | Production websites |
| `Personal/` | Personal data and records |

**The tool warns but doesn't block.** You decide whether to proceed.

## Build Conventions

When creating major new systems or features:

- **Build workspace**: `N5/builds/<slug>/` with `PLAN.md` and `STATUS.md`
- **Scripts**: New scripts go in `N5/scripts/`
- **Integrations**: External tool integrations go in `Integrations/<service>/`

These are conventions, not requirements. Use your judgment.

## Session Lifecycle

- **Session context**: `.claude/session-context.md` tracks progress and decisions
- **Session close**: `/n5-close` logs the session to N5OS
- **Auto-logging**: The `Stop` hook automatically logs sessions

## Naming Conventions

- Scripts: `snake_case.py` or `kebab-case.ts`
- Directories: `kebab-case/`
- Build slugs: `descriptive-slug-name`

## What This Integration Provides

1. **Protection warnings** before destructive operations
2. **Session continuity** via session-context.md
3. **N5OS logging** so sessions are tracked alongside Zo conversations

## What This Integration Does NOT Do

- Override your planning methodology
- Block any operations
- Require specific workflows

**Your planning capabilities remain intact.** This integration just keeps you informed about the environment.

