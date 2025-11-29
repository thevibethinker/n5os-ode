---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# ZoBridge Service v1 – ParentZo ↔ ChildZo Bridge

```yaml
capability_id: zobridge-service-v1
name: "ZoBridge Service – ParentZo ↔ ChildZo Collaboration Bridge"
category: internal
status: experimental
confidence: medium
last_verified: 2025-11-29
tags:
  - zobridge
  - messaging
  - services
  - bootstrap
entry_points:
  - type: script
    id: "N5/services/zobridge/server.ts"
  - type: script
    id: "N5/services/zobridge/zobridge_processor.py"
  - type: script
    id: "N5/services/zobridge/bootstrap_sender.py"
  - type: script
    id: "N5/services/zobridge/bootstrap_monitor.py"
owner: "V"
```

## What This Does

The ZoBridge service provides a structured communication channel between **ParentZo** (this system) and **ChildZo** (a demonstrator Zo computer). It exposes HTTP endpoints, processes ZoBridge messages, persists them to a SQLite database, and coordinates bootstrap sequences (e.g. building N5 OS on ChildZo).

It is the runtime counterpart to the **ZoBridge Parent‑Child Link integration capability**, focusing specifically on the local services, databases, and monitoring scripts that make the protocol work.

## How to Use It

### Service lifecycle

The service is managed as a Zo user service (Bun + TypeScript + Hono). Typical actions:

- Service entrypoint: `file 'N5/services/zobridge/server.ts'` (TypeScript HTTP server).
- Processor: `file 'N5/services/zobridge/zobridge_processor.py'` (Python worker that consumes messages from DB/audit and executes workflows).

To inspect or restart the service, use [Services](/system#services) in Zo and look for the ZoBridge service record.

### Bootstrap utilities

From `/home/workspace`:

```bash
# Bootstrap sender – sends a sequence of bootstrap messages to ChildZo
python3 N5/services/zobridge/bootstrap_sender.py --help

# Bootstrap monitor – summarizes status of long-running bootstrap threads
python3 N5/services/zobridge/bootstrap_monitor.py

# Deployment sender – send deployment manifest
python3 N5/scripts/n5_deployment_sender.py --help
```

These tools use the ZoBridge schema and config files to emit well‑formed messages and to track milestones such as `msg_100` (ZoBridge deployed) and bootstrap progress.

## Associated Files & Assets

### Service code & configuration

- `file 'N5/services/zobridge/server.ts'` – Bun/Hono HTTP service implementation.
- `file 'N5/services/zobridge/relay.ts'` / `poller.ts` – Parent→Child relay and poller logic.
- `file 'N5/services/zobridge/zobridge_processor.py'` – Python processor that reads messages and coordinates actions.
- `file 'N5/services/zobridge/bootstrap_sender.py'` – Sends bootstrap messages to ChildZo.
- `file 'N5/services/zobridge/bootstrap_monitor.py'` – Tracks bootstrap milestones and summarizes progress.
- `file 'N5/services/zobridge/health_monitor.py'` – Periodic health checks and status reporting.
- `file 'N5/services/zobridge/zobridge_audit.jsonl'` – Service‑side audit log.
- `file 'N5/services/zobridge/HEALTH_STATUS.md'` – Human‑readable health report.
- `file 'N5/services/zobridge/AUDIT_REPORT.md'` – Detailed audit and issue list.
- `file 'N5/services/zobridge/package.json'` – Node/Bun project metadata.

### Shared schema & data

- `file 'N5/schemas/zobridge.schema.json'` – Message JSON schema.
- `file 'N5/data/zobridge.db'` – ZoBridge message store (threads, messages, state).
- `file 'N5/data/zobridge_audit.jsonl'` – Additional audit trail of inbound/outbound events.

### Documentation

- `file 'N5/services/zobridge/README.md'` – Protocol and system overview.
- `file 'N5/ZOBRIDGE_FULL_AUDIT_2025-10-20.md'` – Full system audit; current known issues and message statistics.
- `file 'Documents/zobridge_bootstrap_status.md'`, `file 'Documents/zobridge_next_steps.md'`, etc. – High‑level status docs.
- `file 'Inbox/20251029-131651_Deliverables/ZOBRIDGE_CHILDZO_INSTALL_GUIDE.md'` – ChildZo installation instructions.

## Workflow

### High-level protocol flow

```mermaid
flowchart TD
  A[ParentZo systems
  - N5 OS
  - scripts/workflows] --> B[ZoBridge Processor
  - prepare ZoBridgeMessage JSON]

  B --> C[ZoBridge Service (server.ts)
  - HTTP API
  - store to zobridge.db]

  C --> D[Transport
  - HTTP
  - file-based exchange]

  D --> E[ChildZo ZoBridge Service
  - receive + process]

  E --> F[ChildZo Response
  - status, results]

  F --> G[ParentZo Processor
  - update state
  - write to audit
  - optionally trigger next actions]
```

### Bootstrap pattern

1. ParentZo uses `bootstrap_sender.py` to send a series of numbered messages (`msg_001`, `msg_100`, etc.) describing work to be done on ChildZo (e.g. installing N5 OS components).
2. ZoBridge service transmits messages (initially via file copy, then via HTTP endpoints) and logs all events to `zobridge.db` and audit JSONL.
3. `bootstrap_monitor.py` and the various audit reports summarize how many messages succeeded, which failed, and which are pending.
4. When both services are healthy and response authentication is fixed, ParentZo and ChildZo can collaborate on multi‑step builds.

## Notes / Gotchas

- **Authentication issues remain.** The full audit notes that while 54/56 Parent→Child messages succeeded, Child→Parent responses were blocked by authentication mismatches; treat the system as **partially operational** until those corrections are fully deployed.
- **Two capabilities:** This file documents the **internal service**; the separate **ZoBridge Parent‑Child Link** integration capability covers how AI workflows invoke the protocol.
- **Service footprint:** The ZoBridge service directory under `N5/services/zobridge/` is relatively heavy; cleanup or migration must be treated as a high‑risk operation and coordinated with audit docs.
- **Transport modes:** Some older docs reference purely file‑based exchange (V manually shuttling JSON files); the HTTP service is the current direction but assumes both ParentZo and ChildZo have active ZoBridge services.

