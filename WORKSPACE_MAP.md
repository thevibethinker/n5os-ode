---
created: 2026-04-27
last_edited: 2026-05-15
version: 1.3
provenance: con_MgE1jbcMK4s9epeL
---
# Workspace Map

Fast navigation index for `/home/workspace`. Use this file first, then load only the specific docs needed for the current lane.

## Operating Docs

| Need | Start Here |
|---|---|
| Shared workspace contract | `AGENTS.md` |
| Folder placement and root hygiene | `POLICY.md` |
| Maintainer cleanup, git hygiene, ignore/protection, commit cadence | `Documents/System/Maintainer-Playbook.md` |
| Site staging, promotion, and GitHub-per-site protocol | `Documents/System/Sites-System.md` |
| Cross-harness operating contract | `N5/HARNESS_CONTRACT.md` |
| Session-state decision | `N5/SESSION_STATE_POLICY.md` |
| Claude Code adapter | `CLAUDE.md` |
| Codex adapter | `CODEX.md` |
| Workspace identity / tone | `SOUL.md` |

## Core N5 Systems

| System | Key Paths |
|---|---|
| Pulse builds | `N5/builds/`, `Skills/pulse/SKILL.md`, `Skills/pulse/scripts/pulse.py` |
| Build checks | `N5/scripts/build_contract_check.py`, `N5/scripts/mece_validator.py` |
| Close checks | `N5/scripts/close_contract_check.py`, `N5/lib/close/` |
| Cognition / retrieval | `N5/cognition/`, `N5/scripts/n5_load_context.py` |
| Graph / feed architecture | `N5/builds/graph-feed-architecture/`, `N5/data/signal-ledger/` |
| Mind map / positions | `N5/data/positions.db`, `N5/scripts/positions.py`, `N5/scripts/sync_positions_to_entities.py` |
| Meeting ingestion | `Skills/meeting-ingestion/SKILL.md`, `Personal/Meetings/` |
| Tasks bridge | `Skills/google-tasks-bridge/`, `N5/data/taskintake.db` |
| Research routing | `N5/scripts/research_router.py`, `Research/` |

## Workspace Roots

| Directory | Purpose |
|---|---|
| `Articles/` | Saved articles and webpage captures intended for later ingestion or reference |
| `Assets/` | Shared static assets that are not tied to a single site or generated image batch |
| `Build Exports/` | Exportable build packages and backups |
| `Careerspan/` | Careerspan-specific project files and operating material |
| `Databases/` | Canonical data folders and local datasets |
| `Documents/` | Documents, drafts, deliverables, and system references |
| `Images/` | Generated, captured, and reusable image assets |
| `Integrations/` | Integration-specific code, adapters, and service glue |
| `Knowledge/` | Curated knowledge artifacts and content library |
| `Lists/` | Managed list-style databases and list policies |
| `N5/` | N5OS scripts, configs, data, builds, and system docs |
| `Personal/` | Personal files, meetings, CRM, health, and private records |
| `Projects/` | Project folders that are not sites, skills, research, or N5 builds |
| `Prompts/` | Reusable prompt artifacts and prompt contracts |
| `Research/` | Research artifacts and investigations |
| `Scratch/` | Ephemeral workspace scratch |
| `Skills/` | Deployed reusable workflows and local integrations |
| `Sites/` | Canonical website and web app projects |

## Common Commands

```bash
python3 N5/scripts/n5_load_context.py --health
python3 N5/scripts/build_contract_check.py <slug>
python3 Skills/pulse/scripts/pulse.py validate <slug>
python3 Skills/pulse/scripts/pulse.py status <slug>
python3 Skills/pulse/scripts/pulse.py finalize <slug>
python3 N5/scripts/docs_drift_check.py --root /home/workspace
```

## Current Notes

- Use `python3 N5/scripts/docs_drift_check.py --root /home/workspace` for broad reference drift. For this map, verify listed paths and commands directly before relying on them.
- Build-level details stay in `N5/builds/<slug>/`; this map should list stable navigation surfaces, not every finalized build.
- `WORKSPACE_MAP.md` is hand-curated. If it is missing, restore the tracked root file first; do not recreate it from the generic starter template.
