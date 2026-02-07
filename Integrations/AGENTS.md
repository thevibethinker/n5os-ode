---
created: 2026-02-02
last_edited: 2026-02-06
version: 1.1
provenance: con_NLOu2MVInIYnuwuf
---

# Integrations Directory

External service integrations and automated pipelines. Each subdirectory is a self-contained integration with its own `AGENTS.md`.

## Active Integrations

### careerspan-pipeline/
**Status:** Live — heartbeat active, schema complete
**Purpose:** CorridorX × Careerspan talent matching automation
**Entry:** `python3 scripts/pipeline_orchestrator.py [scan|process|status]`
**Heartbeat:** Every 2 hours, 9am-9pm ET
**Docs:** See `careerspan-pipeline/AGENTS.md` for full context

### careerspan-webhook/
**Status:** Running
**Purpose:** Receives Careerspan Intelligence Briefs when candidates complete Stories
**URL:** `https://careerspan-webhook-va.zocomputer.io/webhook`
**Port:** 8850
**Docs:** See `careerspan-webhook/AGENTS.md`

### calendly-zoffice/
**Status:** Built (enable on zoputer)
**Purpose:** Calendly webhooks → schedule Consultant worker activation/deactivation
**Endpoint:** `POST /api/calendly/webhook`
**Port:** 8851 (default)
**Entry:**
- Webhook server: `python3 scripts/webhook_handler.py serve --port 8851`
- Job runner: `python3 scripts/session_prep.py tick`
**Docs:** See `calendly-zoffice/AGENTS.md`

---

## Directory Convention

```
Integrations/
├── AGENTS.md              ← This file (index)
└── <integration-name>/
    ├── AGENTS.md          ← Integration-specific memory
    ├── config.yaml        ← Configuration
    ├── scripts/           ← Entry points
    └── ...
```

When creating new integrations:
1. Create subdirectory with slug name
2. Add `AGENTS.md` with operational context
3. Add entry to this index