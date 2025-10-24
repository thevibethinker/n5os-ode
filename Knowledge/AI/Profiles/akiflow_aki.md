---
name: Akiflow Aki
aka: [Aki]
owner: V
status: active
last_reviewed: 2025-10-22
---
# Profile: Akiflow Aki

## Purpose
Personal assistant inside Akiflow for tasks, calendar, planning; accepts email to create tasks/events.

## Channels
- In-app chat (desktop/web/mobile)
- WhatsApp (manual use)
- Email intake (unique address per user) → creates tasks/events; no guaranteed email replies
  - **Confirmed allowlisted sender:** va@zo.computer
  - **CC rule:** If >3 back-and-forths with Aki or stuck in loop, auto-CC attawar.v@gmail.com
- Automations/Workflows (time-based)
- Integrations: Zapier, IFTTT (read/write actions)

## Auth & Setup
- Toggle Aki: Settings → AI Center
- Copy unique Aki email and add allowed sender addresses in AI Center (Your Aki email + Enabled addresses)
- Ensure sender we use via Zo is allowlisted

## Core Capabilities
- Create/Edit: tasks (title, when, duration, recurrence, description, deadline, priority, project, tags [assign existing]) [^1]
- Create/Edit: events (primary calendars; guests; auto call link; previews) [^1]
- Read/Plan: check schedule, move tasks/time slots; overdue handling [^1]
- Automations: time-based reminders and workflows (results in-app; not WhatsApp) [^1]
- Search web, guide support (beta) [^1]

## Read Access (Programmatic)
- No documented email responses; agenda queries are in-app.
- IFTTT offers queries like “List Tasks for a Date” (read) and actions like “Create Task” (write). Useable via IFTTT → Webhooks bridge. [^2]

## I/O Specs
- Email to Aki (task/event creation): natural language; include fields inline.
- Suggested format (works well with NL parser):
  Subject: [N5] <Actionable Title> | <When>
  Body:
  - When: Tue 3:30 pm ET
  - Duration: 25m
  - Priority: High
  - Project: <existing>
  - Tags: tag1, tag2
  - Notes: context + source link

## Limits & Caveats
- Cannot create Projects/Tags; can assign existing ones [^1]
- Cannot create recurring events (can edit single instances) [^1]
- Automations are time-based only today [^1]
- Email intake is designed for capture; multi-task in one email not documented — test and validate

## Playbooks

### P1: Warm Intro Pack
```bash
python3 N5/scripts/akiflow_push.py \
  --tasks Documents/System/akiflow/example_warm_intro.json \
  --batch
```
Creates 3-task sequence: draft (15m) → send (5m) → follow-up in 7 days (10m).
Project: Networking | Tags: warm_intro, draft/send/follow_up

### P2: Meeting → Action Items
Post-meeting: extract 3-5 action items → format JSON → push batch.
Projects: Operations, Product, Personnel (context-dependent)

### P3: Daily Planning Handoff
V sends tasks → Zo formats with smart defaults → batch push.
Intelligent duration/priority inference from V's context.

### Projects Reference (V's actual structure)
Personal, VA-ZO Content, LifeOps, Learning, Networking,
Careerspan, Operations, Product, Growth, Personnel,
Finance & Legal, Careerspan Content

### Template: Batch Tasks Email (experimental)
Subject: [N5] Batch tasks | Tomorrow

Body:
- Task: Draft recap for <Meeting X>
  When: Tomorrow 9:30am ET
  Duration: 20m
  Priority: Normal
  Project: Careerspan
  Tags: meeting, recap
  Notes: file 'Records/Company/Meetings/<YYYY-MM-DD-Meeting-X>.md'

- Task: Send warm intro <A> → <B>
  When: Tomorrow 10:00am ET
  Duration: 15m
  Priority: High
  Project: Networking
  Tags: warm_intro
  Notes: context + emails

## Testing
- T1 Email one task → confirm appears correctly
- T2 Email two tasks in one email → measure parsing success (acceptance criteria: 2 distinct tasks created)
- T3 Event creation with guest(s) → confirm preview in app and created event
- T4 IFTTT query “List Tasks for a Date” via webhook → verify pull of agenda

## References
- Aki overview and capabilities [^1]
- IFTTT Akiflow Create Task [^2]
- IFTTT Akiflow List Tasks for a Date [^3]
- Akiflow Integrations overview [^4]

## Change Log
- 2025-10-22: Initial profile created; confirmed va@zo.computer allowlisted; added CC rule

[^1]: https://how-to-use-guide.akiflow.com/aki-akiflow-ai-bot-beta
[^2]: https://ifttt.com/akiflow/actions/create_task
[^3]: https://ifttt.com/akiflow/queries/task_for_date
[^4]: https://how-to-use-guide.akiflow.com/integrations
