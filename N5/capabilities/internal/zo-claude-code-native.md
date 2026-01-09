---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_JS1OqPU9pbYCCCjI
---

# Zo Claude Code Native

```yaml
# Zone 2: Capability metadata (machine-readable)
capability_id: zo-claude-code-native
name: Zo Claude Code Native
category: internal
status: active
confidence: high
last_verified: '2026-01-09'
tags: [integration, engineering, workflow, automation]
owner: V
purpose: |
  Integrates Claude Code as a native tool within N5OS, providing environment awareness, session continuity, and unified logging.
components:
  - Integrations/claude-code/n5_mcp_bridge.ts
  - N5/scripts/close_convo_bridge.py
  - ~/.claude/hooks/session-start.py
  - ~/.claude/hooks/pre-tool-use.py
  - ~/.claude/hooks/pre-stop.py
  - /home/workspace/CLAUDE.md
  - N5/builds/zo-claude-code-native/PLAN.md
operational_behavior: |
  Automates environment initialization via lifecycle hooks, enforces N5OS protection rules during tool use, and syncs session logs to the Zo conversation history upon termination.
interfaces:
  - Command: claude (cli)
  - Slash Command: /n5-close
  - Slash Command: /n5-status
  - File: /home/workspace/CLAUDE.md
quality_metrics: |
  100% hook firing reliability, zero bypasses of protected path warnings, and verified session log ingestion into N5OS.
```

## What This Does

Zo Claude Code Native transforms the standalone Claude Code CLI into a context-aware participant in the N5OS ecosystem. It enhances Claude Code's superior engineering planning with V's specific environmental constraints, such as protected paths and N5OS conventions, ensuring that external terminal-based AI work remains visible and logged within the main Zo conversation system. This capability ensures that terminal sessions are not "dark" to the rest of the OS, maintaining a unified source of truth for all build activities.

## How to Use It

### Triggering the Environment
Simply run the standard Claude Code command in the terminal:
```bash
claude
```
The `session-start.py` hook will automatically initialize the `session-context.md` file and inform Claude of the N5OS environment.

### Integrated Commands
While inside a Claude Code session, you can use N5-specific slash commands:
- `/n5-status`: Verifies the state of the MCP bridge and environment sync.
- `/n5-close`: Gracefully terminates the session and triggers the `pre-stop.py` hook to log the session to N5OS.

### Environment Awareness
Claude Code is automatically informed of workspace rules via the `CLAUDE.md` file at the root. If Claude attempts to modify a protected path, the `pre-tool-use.py` hook will intercept the action and provide a warning based on N5OS safety protocols.

## Associated Files & Assets

- file 'Integrations/claude-code/n5_mcp_bridge.ts': The MCP server bridging N5 tools to Claude.
- file 'N5/scripts/close_convo_bridge.py': Python utility for syncing terminal logs to Zo API.
- file 'home/workspace/CLAUDE.md': The primary conventions file Claude reads for workspace behavior.
- file '~/.claude/hooks/': Directory containing lifecycle scripts (`session-start.py`, `pre-tool-use.py`, `pre-stop.py`).
- file '~/.claude/settings.json': Configuration mapping hooks to the Claude Code lifecycle.

## Workflow

```mermaid
flowchart TD
  A[User runs 'claude'] --> B[session-start.py hook]
  B --> C[Initialize session-context.md]
  C --> D[Active Engineering Session]
  D --> E{Tool Use?}
  E -- Yes --> F[pre-tool-use.py hook]
  F --> G[Check .n5protected]
  G -- Safe --> H[Execute Tool]
  G -- Protected --> I[Warn / Block]
  D --> J[/n5-close or Exit]
  J --> K[pre-stop.py hook]
  K --> L[close_convo_bridge.py]
  L --> M[Log synced to N5OS / Zo API]
```

## Notes / Gotchas

- **Path Protection**: The `pre-tool-use.py` hook relies on the presence of `.n5protected` files. Ensure critical system directories are marked accordingly.
- **Async Logging**: Session logging via `close_convo_bridge.py` operates in an async mode to prevent terminal hang on exit; logs may take a few moments to appear in the Zo chat history.
- **CLAUDE.md Maintenance**: This file is a "living" document. While it informs Claude of conventions, it should not be used to override Claude's internal planning logic, which is preserved as per the "Inform, don't override" philosophy.
- **Hook Permissions**: Ensure all scripts in `~/.claude/hooks/` are executable (`chmod +x`).

03:57:00 ET/EST