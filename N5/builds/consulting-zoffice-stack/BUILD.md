---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: consulting-zoffice-stack
---

# BUILD: Zoffice Consultancy Stack

## Quick Reference
- **Build ID:** consulting-zoffice-stack
- **Type:** Multi-component infrastructure build
- **Streams:** 4 (Foundation → Archetype → Pipeline → Localization)
- **Total Drops:** 11
- **Estimated Duration:** 2-3 weeks

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT'S ZO (Theirs)                        │
│                    (Inquiries → Security Gate)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ Email (monitored, secured)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              ZOPUTER.ZO.COMPUTER (Archetype Zo)               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │   Security  │  │   Zoffice    │  │     Consultant      │   │
│  │    Gate     │  │   Workers    │  │ (Office Hours only) │   │
│  │(event-based)│  │(scheduled)   │  │                     │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           DUAL-SIDED AUDIT DATABASE                    │   │
│  │  (Immutable log, independently maintained on both ends) │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │ API (/zo/ask)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              VA.ZO.COMPUTER (Source of Truth)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │   Content   │  │   Daily      │  │   Dual-Sided        │   │
│  │  Classifier │  │   Export     │  │   Audit Database    │   │
│  │             │  │   Pipeline   │  │                     │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Stream Flow

### Stream 1: Foundation (Sequential)
**Drops:** D1.1 → D1.2 → D1.3
**Purpose:** Security gate, audit system, API layer
**Critical Path:** Yes

### Stream 2: Archetype (After Stream 1)
**Drops:** D2.1 (manual) → D2.2, D2.3 (parallel)
**Purpose:** Set up zoputer account, content classification, worker framework
**Critical Path:** Yes

### Stream 3: Pipeline (After Stream 2)
**Drops:** D3.1, D3.2 (parallel)
**Purpose:** Daily export automation, Calendly integration
**Critical Path:** No

### Stream 4: Localization (Parallel)
**Drops:** D4.1 (manual), D4.2
**Purpose:** Adaptation protocol, client onboarding
**Critical Path:** No

## Worker Briefs

All drops are in `workers/`:
- `D1.1-security-gate.md`
- `D1.2-audit-system.md`
- `D1.3-api-layer.md`
- `D2.1-archetype-setup.md`
- `D2.2-content-classifier.md`
- `D2.3-zoffice-workers.md`
- `D3.1-export-pipeline.md`
- `D3.2-calendly-integration.md`
- `D4.1-localization-framework.md`
- `D4.2-client-onboarding.md`

## Manual Steps Required

### From V:
1. **D2.1:** Create zoputer.zo.computer account
2. **D2.1:** Set up API keys in both environments
3. **D4.1:** Collaborate on localization philosophy

## Success Criteria

- [ ] Security gate blocks 100% of adversarial patterns in test suite
- [ ] Audit DB logs every API call with matching hashes
- [ ] Daily export runs automatically with SMS confirmation
- [ ] zoputer responds to client emails within 5 minutes
- [ ] Calendly integration triggers Consultant worker
- [ ] Localization protocol documented and V-approved

## Commands

```bash
# Check build status
python3 Skills/pulse/scripts/pulse.py status consulting-zoffice-stack

# Start build
python3 Skills/pulse/scripts/pulse.py start consulting-zoffice-stack

# Verify audit sync
python3 N5/scripts/audit_verify.py --since "2026-02-06"

# Manual export test
python3 Skills/librarian-export/scripts/daily_export.py --dry-run
```

## Contacts
- **Build Owner:** V
- **Technical Lead:** Zo (Vibe Operator → Architect → Builder)
- **Security Review:** V
