# Zo Capabilities Index

## What Zo Is
Personal cloud computer with built-in AI. Full Linux server (100GB), always-on. Accessible via web, desktop, SMS, email (handle@zo.computer). AI has root access and all connected services.

## Primitives

**Rules** — Persistent behavioral instructions (optional condition + instruction). Always-applied or conditional. For: preferences, formatting, routing, guardrails.

**Personas** — Switchable AI personalities with custom prompts. Default handles routing; specialists handle depth. For: specialized thinking (writer, strategist, coder, tutor).

**Scheduled Agents** — AI tasks on cron (RRULE). Delivery: email, SMS, or silent. Full tool access (web, files, integrations, messages). For: monitoring, reports, reminders, automation.

**Skills** — Packaged workflows: Skills/name/SKILL.md + scripts/ + references/ + assets/. Installable or custom-built. For: repeatable multi-step procedures, custom integrations.

## Surfaces

**zo.space** — Instant-deploy personal site (handle.zo.space). Pages (React/Tailwind, private default) and APIs (Hono, always public). For: dashboards, webhooks, widgets, landing pages, tools.

**Sites** — Full web apps with build system (Hono+Bun+SQLite, custom domains). For: complex multi-page apps.

**Datasets** — Structured data: source → ingest → DuckDB. Query with SQL, visualize in zo.space. For: analytics, tracking, metrics.

## Integrations
Gmail, Google Calendar, Google Drive, Notion, Airtable, Stripe, Linear, Dropbox, Spotify. Multiple accounts per service. Custom: build as Skills with API scripts.

## Channels
SMS (send/receive, agents can text), Email (handle@zo.computer inbound, send_email_to_user outbound), Browser (persistent authenticated sessions).

## Architectural Patterns

**Email→Process→Output**: Agent monitors inbox for tagged emails → extract → process → deliver to Drive/Airtable/email.

**Dataset+Agent+Dashboard**: Agent refreshes dataset on schedule → zo.space page visualizes → always-current view.

**Webhook→Process→Notify**: zo.space API receives events → process → SMS/email notification.

## Prompt Harness
```
[CONTEXT: who they are, what they need]
[TASK: specific objective]
[CONSTRAINTS: boundaries, requirements]
[GATE: "Before executing, ask me about: X, Y, Z"]
[DONE: what the output looks like]
```

## Key Prompting Patterns
- Clarification gate: "Ask me N questions before responding"
- Staged builds: plan first, execute in pieces, verify each stage
- Specific > vague: give examples of desired output, define "done"
- File mentions: reference workspace files with @filename for context
- Start small: build v1, then upgrade (don't over-engineer day 1)
