---
name: zoffice-workers
description: Worker manifest and runner utilities that let zoputer activate personas (Librarian, Consultant, Debugger) based on schedule or Calendly triggers while logging every activation to the audit system.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0"
  created: "2026-02-06"
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_GwlFHPrBi5KsNm1X
---

# Zoffice Workers

## Purpose

This system stitches together worker manifests, scheduler/webhook handlers, and the manager script so that `zoputer.zo.computer` can activate personas and orchestrate scheduled consulting support just like V does on `va`. Every activation writes to the dual-sided audit log.

## Utilities

```bash
# List configured workers
python3 N5/scripts/zoffice_worker.py list

# Activate a worker (prints persona instructions and logs the activation)
python3 N5/scripts/zoffice_worker.py activate librarian

# Check worker states
python3 N5/scripts/zoffice_worker.py status

# Deactivate everyone
python3 N5/scripts/zoffice_worker.py deactivate-all
```

## Worker Catalog

- **Librarian** – Persona `1bb66f53-9e2a-4152-9b18-75c2ee2c25a3`, scheduled daily at 9 AM ET to run Drop 3.1 exports.
- **Consultant** – Triggered by Calendly webhooks, sets persona to `Teacher`, runs briefing, and remains available during the call window.
- **Debugger** – Weekly Sunday 10 AM ET health check run, persona `Debugger`.
