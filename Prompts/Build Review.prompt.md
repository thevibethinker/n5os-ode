---
description: |
  Orchestrate a multi-worker build project.
  
  The LLM defines the build plan with workers, dependencies, and context.
  The script handles tracking, status, and generating spawn commands.
  
  **Initialize:** Define plan as JSON, then init
  **Track:** Check status, get ready workers, mark complete
  **Spawn:** Generate spawn commands with full context
tool: true
tags:
  - build
  - orchestration
  - workers
  - parallel
---

# Build Orchestrator

## Workflow

### 1. Define Your Build Plan (LLM Does This)

Create a JSON plan with:
- Project name and objective
- Workers with dependencies
- Key decisions and relevant files

```json
{
  "name": "Authentication System",
  "description": "Implement OAuth2 + SSO for N5 services",
  "objective": "Secure, user-friendly authentication with provider flexibility",
  "key_decisions": [
    "SQLite for credential storage",
    "JWT for sessions",
    "Support Google, GitHub, custom OIDC"
  ],
  "relevant_files": [
    "N5/services/auth/README.md",
    "N5/schemas/auth.sql"
  ],
  "workers": [
    {
      "id": "worker_schema",
      "component": "database_schema",
      "description": "Create SQLite schema for users, sessions, providers",
      "dependencies": [],
      "estimated_hours": 2
    },
    {
      "id": "worker_oauth",
      "component": "oauth_flow",
      "description": "Implement OAuth2 authorization code flow",
      "dependencies": ["worker_schema"],
      "estimated_hours": 4
    },
    {
      "id": "worker_jwt",
      "component": "jwt_sessions",
      "description": "JWT token generation and validation",
      "dependencies": ["worker_schema"],
      "estimated_hours": 3
    },
    {
      "id": "worker_providers",
      "component": "provider_config",
      "description": "Google, GitHub, custom OIDC provider support",
      "dependencies": ["worker_oauth"],
      "estimated_hours": 3
    }
  ]
}
```

### 2. Initialize the Project

```bash
# Save plan to file first, or use inline
python3 N5/scripts/build_orchestrator_v2.py init \
    --project auth-system \
    --plan-file /path/to/plan.json
```

### 3. Check What's Ready

```bash
python3 N5/scripts/build_orchestrator_v2.py ready --project auth-system
```

Returns workers whose dependencies are met.

### 4. Spawn Workers

```bash
# Get spawn command for a ready worker
python3 N5/scripts/build_orchestrator_v2.py spawn-cmd \
    --project auth-system \
    --worker worker_schema \
    --parent con_XXXXX
```

This generates a `spawn_worker_v2.py` command with full context.

### 5. Mark Complete

When a worker finishes:

```bash
python3 N5/scripts/build_orchestrator_v2.py complete \
    --project auth-system \
    --worker worker_schema \
    --output "N5/services/auth/schema.sql"
```

### 6. Check Overall Status

```bash
python3 N5/scripts/build_orchestrator_v2.py status --project auth-system
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `init --project X --plan-file Y` | Start new project |
| `status --project X` | Show all workers and status |
| `ready --project X` | Show workers ready to spawn |
| `complete --project X --worker Y` | Mark worker done |
| `spawn-cmd --project X --worker Y --parent Z` | Get spawn command |
| `list` | List all projects |

## Project Data

Projects are stored in `N5/orchestration/{project}/`:
- `plan.json` - Full plan with worker status
- `README.md` - Auto-generated overview

## Tips

1. **Start with ready workers** - Check `ready` to see what can be parallelized
2. **Update frequently** - Mark workers complete so dependent workers become ready
3. **The LLM drives everything** - Plan definition, spawning decisions, context
4. **Script just tracks** - No AI in the script, just state management

