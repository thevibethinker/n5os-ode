---
created: 2026-05-15
last_edited: 2026-05-15
version: 1.0
provenance: con_H7bSTDBcsH0gBtFG
---

# N5OS Environment — Claude Code Adapter

**Owner:** V (Vrijen Attawar)
**System:** N5OS on Zo Computer
**Fast map:** `WORKSPACE_MAP.md` · **Canonical contract:** `AGENTS.md` · **Shared harness contract:** `N5/HARNESS_CONTRACT.md` · **Session-state policy:** `N5/SESSION_STATE_POLICY.md` · **Placement authority:** `POLICY.md`

This file contains Claude Code-specific mechanics only. For workspace navigation, start with `WORKSPACE_MAP.md`. For workspace governance, precedence, build invariants, and operating defaults, follow `AGENTS.md`. For session-state decisions, follow `N5/SESSION_STATE_POLICY.md`. For folder placement rules, follow `POLICY.md`.

---

## MCP Bridge

Claude Code has access to three N5OS MCP tools:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `n5_protect_check` | Warns before destructive ops on protected paths | Before delete/move on `N5/`, `Sites/`, `Personal/`, `Prompts/`, `Knowledge/` |
| `n5_log_bio` | Logs significant milestones to V's bio timeline | Major life/career events, not routine task completions |
| `n5_close_conversation` | Logs session to N5OS alongside Zo conversations | At session close via `/n5-close` or the Stop hook |

These tools warn but do not block. You decide whether to proceed based on context.

---

## Session Lifecycle

- **Session context:** `.claude/session-context.md` tracks progress, decisions, and loaded context modules for this Claude Code session.
- **Session close:** Use `/n5-close` to log the session to N5OS.
- **Auto-logging:** The `Stop` hook automatically logs sessions on exit.
- **Conversation-local state:** Use the conversation workspace `SESSION_STATE.md` when the current lane or workflow requires it per `N5/SESSION_STATE_POLICY.md`.

---

## On-Demand Context Loading

For non-trivial work, load shared docs in this order:

1. `WORKSPACE_MAP.md`
2. `AGENTS.md`
3. `N5/HARNESS_CONTRACT.md`
4. `N5/SESSION_STATE_POLICY.md`
5. Specialized protocol docs only as needed

Then use `/load-context <context>` only when deeper domain-specific preferences are needed.

Available context bundles:

| Context | Use For |
|---------|---------|
| `system_ops` | System admin, file operations, git work |
| `content_generation` | Writing, documents, social posts |
| `crm_operations` | Contact management, stakeholder tracking |
| `code_work` | Code modifications, multi-file changes |
| `scheduling` | Scheduled tasks, calendar ops |
| `research` | Deep research, stakeholder analysis |
| `build` | Implementation, refactoring, engineering |
| `full` | Load all modules (**use sparingly**) |

Or load a specific file: `/load-context file 'N5/prefs/path/to/module.md'`

Default state: only core principles and safety rules are loaded. Load additional context as tasks require it.

---

## System Architecture (Quick Reference)

N5OS is organized as a layered system:

```
N5/
├── prefs/       # Architectural principles + operational protocols
├── scripts/     # Python automation scripts
├── config/      # Centralized configuration (ports, webhooks, integrations)
├── data/        # Runtime state, databases, caches
├── builds/      # Project workspaces
├── commands/    # Executable recipes for AI execution
└── logs/        # Thread exports, system logs

Sites/           # Production websites (protected)
Personal/        # Personal data and records (protected)
Skills/          # Deployed skill definitions with SKILL.md docs
Knowledge/       # Curated knowledge artifacts
```

---

## Protected Paths

Before delete/move operations on these directories, use `n5_protect_check`:

| Path | Protection Level |
|------|-----------------|
| `N5/` | High — system infrastructure |
| `Sites/` | High — production websites |
| `Personal/` | High — personal data |
| `N5/prefs/**/*.md` | Manual-edit only |
| `Prompts/` | Medium |
| `Knowledge/**/*.md` | Medium |

---

## Configuration Quick Reference

**Port Registry:** `N5/config/PORT_REGISTRY.md` is the SSOT for port allocation.
CLI: `python N5/scripts/port_registry.py check/next/list/sync`

**Commands Registry:** `N5/config/commands.jsonl` — search before creating new commands.

**Drive Integration:** `N5/config/drive_locations.yaml` — Google Drive folder ID mapping.

---

## Key Protocol Pointers

These are not rules to memorize — search for them when the task requires specialized guidance.

| Domain | File |
|--------|------|
| Think-Plan-Execute | `N5/prefs/operations/planning_prompt.md` |
| Recipe execution | `N5/prefs/operations/recipe-execution-guide.md` |
| Task routing | `N5/prefs/protocols/task_routing_protocol.md` |
| File creation | `N5/prefs/operations/file-creation-protocol.md` |
| Artifact placement | `N5/prefs/operations/artifact-placement.md` |
| File protection | `N5/prefs/system/file-protection.md` |
| Folder policy | `N5/prefs/system/folder-policy.md` |
| Scheduled tasks | `N5/prefs/operations/scheduled-task-protocol.md` |
| Digest creation | `N5/prefs/operations/digest-creation-protocol.md` |
| Conversation close | `N5/prefs/operations/conversation-end-v5.md` |
| Thread closure triggers | `N5/prefs/operations/thread-closure-triggers.md` |
| Conversation init | `N5/prefs/operations/conversation-initialization.md` |
| Backpressure | `N5/prefs/operations/backpressure-protocol.md` |
| Refactoring | `N5/prefs/operations/refactoring-protocol.md` |
| Debug logging | `N5/prefs/operations/debug-logging-auto-behavior.md` |

---

## What This Adapter Provides

1. **Protection warnings** via `n5_protect_check` MCP tool
2. **Session continuity** via `.claude/session-context.md`
3. **N5OS logging** via `n5_close_conversation` MCP tool
4. **Bio event logging** via `n5_log_bio` MCP tool

## What This Adapter Does NOT Do

- Override your planning capabilities or judgment
- Block any operations (MCP tools warn only)
- Require specific workflows (protocols are guidance, not mandates)
- Load all context by default (you control what's loaded per P08)
- Replace `WORKSPACE_MAP.md`, `AGENTS.md`, `N5/HARNESS_CONTRACT.md`, or `N5/SESSION_STATE_POLICY.md`

---

**Last Updated:** 2026-04-06
**Fast Map:** `WORKSPACE_MAP.md`
**Canonical Contract:** `AGENTS.md`
**Shared Harness Contract:** `N5/HARNESS_CONTRACT.md`
**Session-State Policy:** `N5/SESSION_STATE_POLICY.md`
**Placement Authority:** `POLICY.md`
**Full Preferences:** N5/prefs/ (load on-demand per P08)
