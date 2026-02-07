---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: consulting-zoffice-stack
---

# Zoffice Consultancy Stack - Build Plan

## Overview
Build a multi-Zo consultancy architecture enabling V to offer advisory services to other Zo users. Consists of:
1. **Security Gate** - Client-facing inbound protection (event-triggered)
2. **Archetype Zo (zoputer.zo.computer)** - Clean mirror with curated knowledge
3. **API Communication Layer** - Direct /zo/ask between va.zo.computer ↔ zoputer.zo.computer
4. **Dual-Sided Audit DB** - Immutable communication logging on both ends
5. **Zoffice Workers** - Scheduled persona activations during office hours
6. **Export Pipeline** - Daily curated skill bundles from va → zoputer
7. **Localization Protocol** - Guidelines for client adaptation

## Security Model
- **Inbound (Client → Archetype)**: Event-triggered security gate on every email
- **Internal (va ↔ zoputer)**: Trusted channel, no security overhead
- **Outbound (zoputer → Client)**: Response passes through same gate as inbound
- **Audit**: ALL communications logged to independent DBs on both sides

## Build Streams & Drops

### Stream 1: Foundation (Sequential - prerequisites for others)

**Drop 1.1: Security Gate Validator** [PRIORITY: CRITICAL]
- Create `/zo/ask` prompt for adversarial pattern detection
- Build wrapper script for email pre-processing
- Define risk levels: low (proceed), medium (hold for V), high (quarantine + alert)
- Test against known jailbreak/prompt injection patterns
- Output: `Skills/security-gate/` with validator script and test suite

**Drop 1.2: Dual-Sided Audit System** [PRIORITY: CRITICAL]
- Design schema: timestamp, direction, content_hash, metadata, checksum
- Build va-side audit logger (SQLite DB at `N5/data/consulting_audit.db`)
- Build zoputer-side audit logger (SQLite DB at `N5/data/consulting_audit.db`)
- Create sync verification script (compare hashes, detect discrepancies)
- Output: `Skills/audit-trail/` with logger and verification scripts

**Drop 1.3: API Communication Layer** [PRIORITY: HIGH]
- Create API key exchange protocol between va.zo.computer and zoputer.zo.computer
- Build va-side export client (`N5/scripts/zoputer_client.py`)
- Build zoputer-side ingestion endpoint
- Implement retry logic, timeout handling, failure notification
- Output: `Integrations/zoputer-sync/` with client/endpoint code

---

### Stream 2: Archetype Setup (Parallel after Stream 1 complete)

**Drop 2.1: Archetype Zo Account Setup** [PRIORITY: HIGH]
- Document account creation at zoputer.zo.computer
- Create initial folder structure mirroring va's Level 1 content
- Set up API key storage in [Settings > Developers]
- Output: `Documents/consulting/archetype-setup-guide.md`

**Drop 2.2: Content Classification System** [PRIORITY: HIGH]
- Build scanner that categorizes va's content into tiers:
  - Tier 0: Safe to export (Skills/, Prompts/, Documents/System/)
  - Tier 1: Review required (architecture docs with personal examples)
  - Tier 2: Never export (Personal/, Zo/, anything .n5protected)
- Create manifest generation (`CONSULTING_MANIFEST.json`)
- Output: `Skills/content-classifier/` with scanner and tier definitions

**Drop 2.3: Zoffice Workers Framework** [PRIORITY: MEDIUM]
- Create worker manifest system (persona, schedule, activation conditions)
- Build Librarian worker (daily export orchestrator)
- Build Consultant worker (office hours activation)
- Build Debugger worker (health checks)
- Output: `Skills/zoffice-workers/` with manifests and activation scripts

---

### Stream 3: Export Pipeline (Parallel after Stream 2)

**Drop 3.1: Daily Export Pipeline** [PRIORITY: MEDIUM]
- Build scheduled agent for 9 AM ET skill export
- Implement change detection (only export modified skills)
- Create bundle format: skill metadata + SKILL.md + assets + version
- Add post-export verification (checksum validation)
- Output: `Skills/librarian-export/` with pipeline scripts

**Drop 3.2: Calendly Integration** [PRIORITY: MEDIUM]
- Configure webhook from Calendly (v-at-careerspan) to zoputer
- Build Consultant worker activation on booking
- Create session preparation flow (client context loading)
- Build post-session summary generation
- Output: `Integrations/calendly-zoffice/` with webhook handler

---

### Stream 4: Localization Protocol (Parallel)

**Drop 4.1: Localization Framework** [PRIORITY: MEDIUM]
- Design protocol for adapting archetype patterns to client contexts
- Create decision tree: when to ask V vs. ask client vs. auto-adapt
- Build questionnaire for initial client intake
- Document localization examples (3-5 case studies)
- Output: `Documents/consulting/localization-protocol.md`

**Drop 4.2: Client Onboarding Flow** [PRIORITY: LOW]
- Create welcome email template with expectations
- Build initial assessment questionnaire
- Design "first 30 days" consulting roadmap
- Output: `Documents/consulting/client-onboarding.md`

---

## Dependencies

```
Stream 1 (Foundation)
├── Drop 1.1 (Security Gate) ──┐
├── Drop 1.2 (Audit System) ───┼──→ Stream 2 (Archetype)
└── Drop 1.3 (API Layer) ──────┘

Stream 2 (Archetype)
├── Drop 2.1 (Account Setup) ──┐
├── Drop 2.2 (Classifier) ─────┼──→ Stream 3 (Pipeline)
└── Drop 2.3 (Workers) ────────┘

Stream 3 (Pipeline) & Stream 4 (Localization) → Parallel
```

## Success Criteria

- [ ] Security gate blocks 100% of known adversarial patterns in test suite
- [ ] Audit DB logs every API call with matching hashes on both sides
- [ ] Daily export runs automatically, V receives confirmation SMS
- [ ] Calendly booking triggers Consultant worker activation
- [ ] Client receives helpful response within 5 minutes of first email
- [ ] V can review any communication via audit query in <30 seconds

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API key exposure | HIGH | Store in Settings, never commit to files |
| Export includes PII | HIGH | Classifier + manual review + .n5protected checks |
| Audit DB corruption | MEDIUM | Daily backup + hash verification |
| Client overwhelm | MEDIUM | Clear scope setting in onboarding |
| V notification fatigue | MEDIUM | Batch alerts, digest format |

## Notes for Drops

- All drops must log to audit system
- All drops must respect .n5protected boundaries
- All drops must follow P35-P39 building principles
- Security gate is non-negotiable on all client-facing operations
