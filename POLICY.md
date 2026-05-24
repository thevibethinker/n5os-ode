---
created: 2026-03-17
last_edited: 2026-05-17
version: 1.1
provenance: con_6I6xr87oFVC6mYyl
---

# Root Workspace Policy

## Allowed Top-Level Directories

Only these directories belong at workspace root. Anything else is misplaced.

| Directory | Purpose |
|-----------|---------|
| `Articles/` | Saved web articles |
| `Assets/` | Shared media assets |
| `Build Exports/` | Exportable build packages (n5os-ode) |
| `Careerspan/` | Careerspan business files |
| `Databases/` | Structured datasets (DuckDB, SQLite) |
| `Documents/` | Documents, drafts, deliverables |
| `Images/` | Generated/stored images |
| `Integrations/` | External service integrations |
| `Knowledge/` | Curated knowledge artifacts |
| `Lists/` | Managed list databases |
| `N5/` | N5OS system (scripts, config, data, builds) |
| `Personal/` | Personal files, health, CRM, meetings |
| `Projects/` | Standalone project workspaces |
| `Prompts/` | Recipe/prompt definitions |
| `Research/` | Research artifacts and investigations |
| `Scratch/` | Ephemeral scratch work (auto-cleaned) |
| `Services/` | Managed service notes and service-local material |
| `Sites/` | Production websites |
| `Skills/` | Deployed skill definitions |
| `Trash/` | Deleted items |
| `Zo/` | Zo identity and journal |
| `ZoATS/` | ZoATS project material |
| `Zoffice/` | Virtual office platform |

## Allowed Top-Level Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Workspace-level agent memory |
| `CLAUDE.md` | Claude Code integration config |
| `CODEX.md` | Codex integration config |
| `HEARTBEAT.md` | Workspace heartbeat/status anchor |
| `IDENTITY.md` | Workspace identity anchor |
| `LICENSE` | Repository license |
| `POLICY.md` | This file |
| `README.md` | Repository readme |
| `SESSION_STATE.md` | Active session tracking |
| `SOUL.md` | Zo personality/identity anchor |
| `TOOLS.md` | Workspace tool index |
| `USER.md` | User profile anchor |
| `WORKSPACE_MAP.md` | Fast navigation index |
| `.n5protected` | Protection marker |
| `.gitignore` | Git ignore rules |
| `.gitmodules` | Git submodule config |

## Rules

1. **No loose files at root.** Scripts → `N5/scripts/`. Data → appropriate domain folder. Personal docs → `Personal/Documents/`.
2. **No new top-level directories** without explicit permission from V.
3. **No temp/working files at root.** Use `Scratch/` for ephemeral work.
4. **Conversation artifacts stay in conversation workspaces** (`/home/.z/workspaces/`), not at root.
5. **Resumes and candidate files** → `Personal/` or project-specific folders, never root.
6. **Meeting block files** (B##_*.md) → meeting processing pipeline, never root.

## Enforcement

The `workspace_audit.py` script runs periodically to detect violations and report them.
