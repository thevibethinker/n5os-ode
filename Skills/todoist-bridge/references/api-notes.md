---
created: 2026-03-15
last_edited: 2026-03-15
version: "1.0"
provenance: n5os-ode-export/D4.2
---

# Todoist API Quick Reference

## API Base

```
https://api.todoist.com/api/v1/
```

The v1 API replaces the deprecated REST v2 API. Use v1 for all new integrations.

## Authentication

Bearer token in every request:

```
Authorization: Bearer <TODOIST_API_TOKEN>
```

Get your token at: https://app.todoist.com/prefs/integrations

## Key Endpoints

| Resource | Method | Endpoint |
|----------|--------|----------|
| List tasks | GET | `/api/v1/tasks` |
| Create task | POST | `/api/v1/tasks` |
| Get task | GET | `/api/v1/tasks/{id}` |
| Close task | POST | `/api/v1/tasks/{id}/close` |
| Filter tasks | GET | `/api/v1/tasks/filter` |
| Completed tasks | GET | `/api/v1/tasks/completed` |
| List projects | GET | `/api/v1/projects` |
| List labels | GET | `/api/v1/labels` |

## Priority Inversion (Important!)

The API and the Todoist UI use **opposite** numbering:

| API Value | API Meaning | UI Display |
|-----------|-------------|------------|
| 1 | Normal priority | p4 (grey) |
| 2 | Medium priority | p3 (blue) |
| 3 | High priority | p2 (orange) |
| 4 | Urgent priority | p1 (red) |

The bridge script passes priority values directly to the API without inversion.
When using `--priority 4`, the task will appear as p1 (urgent/red) in the Todoist UI.

## Rate Limits

- ~450 requests per minute per user token
- HTTP 429 response when exceeded
- `Retry-After` header indicates wait time in seconds
- Strategy: exponential backoff with jitter, max 3 retries

## Idempotency

POST requests support `X-Request-Id` header (UUID) to prevent duplicate task creation.
The bridge generates and logs request IDs for all write operations.

## Date Formats

- **due_string**: Natural language — `"tomorrow"`, `"every Monday"`, `"next Friday"`
- **due_date**: ISO date — `"2026-03-15"`
- **due_datetime**: RFC 3339 — `"2026-03-15T14:00:00Z"`

## Task Create Payload

```json
{
  "content": "Task title",
  "description": "Optional details",
  "project_id": "optional-project-id",
  "priority": 1,
  "due_string": "tomorrow",
  "labels": ["n5os"]
}
```

## Filter Syntax (for sync --filter)

Todoist filter examples:
- `today` — tasks due today
- `overdue` — past-due tasks
- `today | overdue` — both
- `p1` — urgent tasks (UI priority 1 = API priority 4)
- `@n5os` — tasks with the n5os label
- `#ProjectName` — tasks in a specific project

Full reference: https://todoist.com/help/articles/introduction-to-filters-V98wIH

## Common Error Codes

| Code | Meaning | Bridge Handling |
|------|---------|-----------------|
| 200 | Success | Process response |
| 204 | Success (no body) | Used by close/reopen |
| 400 | Bad request | Log error, show message |
| 401 | Unauthorized | Check TODOIST_API_TOKEN |
| 403 | Forbidden | Token lacks permission |
| 404 | Not found | Resource doesn't exist |
| 429 | Rate limited | Retry with backoff |
| 500+ | Server error | Retry with backoff |
