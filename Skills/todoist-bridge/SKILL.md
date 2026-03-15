---
name: todoist-bridge
description: >
  Unidirectional bridge between your task management system (Todoist) and your
  operating system. Syncs tasks for daily briefings, pushes new tasks from
  commitments and meeting action items. Read+create only — never modifies or
  deletes existing Todoist tasks.
compatibility: Created for Zo Computer
metadata:
  author: n5os
  version: "1.0"
---

# Todoist Bridge

Read-only sync and task creation bridge for Todoist integration.

## What It Does

- **Pulls** active tasks from Todoist into a local cache for briefings and analytics
- **Pushes** new tasks to Todoist from commitments, meeting actions, or manual entry
- **Generates** daily task briefings grouped by project and priority
- Labels all bridge-created tasks with `@n5os` for easy filtering

## Safety Constraints

- **Never edits** existing Todoist tasks
- **Never deletes** Todoist tasks
- All write operations support `--dry-run`
- Unidirectional: your Todoist stays under your manual control

## Setup

### 1. Get Your API Token

1. Go to [Todoist Integrations](https://app.todoist.com/prefs/integrations)
2. Scroll to "Developer" and copy your **API token**

### 2. Store the Token

Add `TODOIST_API_TOKEN` as an environment variable / secret in your system.

On Zo Computer: [Settings > Advanced](/?t=settings&s=advanced), add it under Secrets.

### 3. Test Connection

```bash
python3 Skills/todoist-bridge/scripts/todoist_bridge.py status
```

You should see your connection status and project list.

## Usage

### Pull tasks from Todoist

```bash
python3 Skills/todoist-bridge/scripts/todoist_bridge.py sync
python3 Skills/todoist-bridge/scripts/todoist_bridge.py sync --project "Work"
```

### Create a task

```bash
python3 Skills/todoist-bridge/scripts/todoist_bridge.py push "Review quarterly report" \
  --due "next Friday" --priority 3
```

### Create a task (dry run)

```bash
python3 Skills/todoist-bridge/scripts/todoist_bridge.py push "Send follow-up" --dry-run
```

### Daily briefing

```bash
python3 Skills/todoist-bridge/scripts/todoist_bridge.py briefing
python3 Skills/todoist-bridge/scripts/todoist_bridge.py briefing --format json
```

### Check connection and sync status

```bash
python3 Skills/todoist-bridge/scripts/todoist_bridge.py status
```

### List projects

```bash
python3 Skills/todoist-bridge/scripts/todoist_bridge.py projects --refresh
```

### Show completed tasks

```bash
python3 Skills/todoist-bridge/scripts/todoist_bridge.py completed --since 2026-03-10
```

## Commands Reference

| Command | Description | Dry-run |
|---------|-------------|---------|
| `sync` | Pull active tasks into local cache | Yes |
| `push` | Create a new task in Todoist | Yes |
| `status` | Show connection health and sync state | — |
| `briefing` | Generate daily task briefing | — |
| `projects` | List Todoist projects | — |
| `completed` | Show recently completed tasks | — |

## Priority Mapping

The CLI uses the same numbering as the Todoist API (which is inverted from the UI):

| CLI Flag | Meaning | Todoist UI |
|----------|---------|------------|
| `--priority 1` | Normal | p4 |
| `--priority 2` | Medium | p3 |
| `--priority 3` | High | p2 |
| `--priority 4` | Urgent | p1 |

## Local State

Sync state is stored at the path configured via `--state-file` (default:
`Skills/todoist-bridge/state/sync_state.json`). This file contains:

- Cached active tasks (for offline briefings)
- Project ID-to-name mapping
- Audit trail of bridge-created tasks
- Last sync timestamp

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TODOIST_API_TOKEN` | Yes | Personal API token from Todoist settings |

## Dependencies

- Python 3.10+
- `requests` (standard on most systems)
- No additional packages required
