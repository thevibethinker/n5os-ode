---
description: Explicitly route task requests to Akiflow via Aki email interface.
tags: []
tool: true
---
---
name: aki
version: 1.0
status: active
created: 2025-10-22
aliases: [aki-add, akiflow, @aki]
---
# Command: aki

## Purpose
Explicitly route task requests to Akiflow via Aki email interface.

## Syntax

### Basic
```
aki: <task description>
```

### With Context
```
aki: <task description>
--project <project_name>
--priority <High|Normal|Low>
--when <time_description>
--duration <duration>
```

### Multi-task
```
aki: 
- <task 1>
- <task 2>
- <task 3>
```

## Examples

### Single Task
```
aki: Review McKinsey proposal by Friday 2pm
```

### Warm Intro
```
aki: Connect Sarah Chen (Product) with Marcus Rodriguez (Recruiting). 
Both expanding teams Q1 2026. Draft by tomorrow 10am.
```

### Multiple Tasks
```
aki:
- Draft recap for Leadership Team Sync (tomorrow 9:30am, 20m)
- Send warm intro Sarah → Marcus (tomorrow 10am, 15m)  
- Review candidate pipeline for SWE role (tomorrow 11am, 30m)
```

### With Metadata
```
aki: Prepare Q4 board deck
--project Operations
--priority High
--when Next Monday 2pm
--duration 2h
```

## Behavior

### 1. Detection
When V types "aki:" or "aki-add" or "@aki", route request to Akiflow automation.

### 2. Processing
- Extract task(s) from description
- Infer metadata (project, priority, timing, duration)
- Apply defaults from taxonomy
- Format per Aki's expected schema

### 3. Execution
- Call Zo API to structure tasks
- Send formatted email to Aki via va@zo.computer
- Confirm tasks sent

### 4. Confirmation
```
✓ Sent to Akiflow:
  - Draft intro: Sarah Chen → Marcus Rodriguez (Tomorrow 10am, 15m, Networking)
  - Send intro: Sarah Chen → Marcus Rodriguez (Tomorrow 11am, 5m, Networking)
  - Follow-up: Sarah Chen ↔ Marcus Rodriguez (Oct 30 2pm, 10m, Networking)
```

## Flags (Optional)

- `--dry-run` - Preview tasks without sending
- `--batch` - Force batch mode (default: auto-detect)
- `--project <name>` - Override project detection
- `--priority <level>` - Override priority detection
- `--when <time>` - Override time detection
- `--duration <time>` - Override duration detection

## Default Behavior

**Without "aki:" prefix:**
- Auto-detection via task routing protocol
- HIGH confidence → auto-route
- MEDIUM confidence → ask confirmation
- LOW confidence → respond in chat

**With "aki:" prefix:**
- Always route to Akiflow
- No confirmation needed
- Explicit user intent

## Integration

**Routing Protocol:** file 'N5/prefs/protocols/task_routing_protocol.md'
**Akiflow Profile:** file 'Knowledge/AI/Profiles/akiflow_aki.md'
**Project Taxonomy:** file 'Documents/System/akiflow/project_taxonomy.md'

## Implementation

```python
# Pseudo-code
if message.startswith(("aki:", "aki-add", "@aki")):
    content = extract_content_after_prefix(message)
    tasks = zo_api.extract_tasks(content)
    gmail.send_to_aki(tasks, batch=True)
    confirm_sent(tasks)
```

## Error Handling

- **No tasks detected:** Ask for clarification
- **Ambiguous timing:** Use defaults + ask
- **Unknown project:** Use "Operations" + notify
- **Gmail failure:** Retry once, then report error

## Change Log
- 2025-10-22: Created v1.0 - Explicit command prefix for Akiflow routing
