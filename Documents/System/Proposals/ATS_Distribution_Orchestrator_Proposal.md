# Proposal: N5 Hiring ATS - Distribution + Orchestrator

Status: Draft for review  
Owner: V (Solutions Architect)  
Date: 2025-10-22

---

## 0) Context

This proposal packages a complete, self-setup Hiring ATS for Zo using the Git + Submodule distribution pattern, and references the existing orchestrator thread for coordination across modules.

- Reference thread: `ORCHESTRATOR_APPROVAL_2025-10-22.md` (parent orchestrator thread)
- System workflow: `file 'N5/commands/system-design-workflow.md'`

---

## 1) Objective

Deliver a portable, privacy-preserving Hiring ATS that installs in minutes and supports:
- Candidate pipeline management (Lists)
- Interview intelligence and automation (Meetings + Howie)
- Candidate profiles (CRM/Stakeholders)
- Email workflows (offers, rejections, follow-ups)
- Task tracking and orchestrated next steps

Success criteria:
- Installable via one command on a vanilla Zo
- Users control updates and can roll back
- Works without Gmail/Drive (optional integrations)
- Full pipeline ready Day 1; interview automation by Week 1

---

## 2) Scope

### v1.0 (Launch Package)
**Bar:** Self-setup hiring ATS core functionality

**Included:**
- ✅ Infrastructure & Safety (10 scripts)
- ✅ Lists System - Pipeline Management (17 scripts)
- ✅ CRM/Stakeholder - Minimal Profile Fields (7 scripts)
- ✅ Follow-up Tracking (6 scripts)
- ✅ Search & Query (8 scripts)
- ✅ Background Processing (7 scripts)
- ✅ Zo System Integration (5 scripts)
- ✅ Compatibility Scanner (1 script)

**Deferred to v1.1+:**
- 🔜 Interview Processing (HIGH PRIORITY - meetings, Howie, intelligence extraction)
- 🔜 Email Templates & Mailing (templates, sending, validation)
- 🔜 Document Generation (offers, rejections)
- 🔜 Advanced Profile Fields

**Total v1.0:** ~61 scripts (down from ~106)

**Rationale:**
- v1.0 = Core pipeline + candidate tracking + automation
- Interview intelligence is powerful but complex → separate release
- Email templates add significant testing surface → later
- Allows faster launch with focused feature set

---

## 3) Architecture

### Components
- n5-core (submodule): scripts/, schemas/, templates/, docs/
- config/ (user private): pipeline.json, email templates, candidate_fields.json
- logs/ (runtime)

### Data Flow
1. Meeting happens → transcript appears (manual drop or detector)
2. Meeting processors generate blocks (assessment, next steps)
3. Orchestrator updates candidate profile + pipeline stage
4. Email drafts generated (offer/rejection/follow-up)
5. Follow-ups queued and digested

### Orchestrator
- Trigger points: new transcript, stage change, approval event
- Implements: idempotence, dry-run, error handling, logging
- References: `file 'ORCHESTRATOR_APPROVAL_2025-10-22.md'`

---

## 4) File Structure

```
/home/workspace/N5/
├── n5_core/                       # submodule
│   ├── scripts/01_infrastructure
│   ├── scripts/02_lists
│   ├── scripts/03_meetings
│   ├── scripts/04_crm
│   ├── scripts/05_email
│   ├── scripts/06_followups
│   ├── scripts/07_docgen
│   ├── scripts/08_search
│   ├── scripts/09_automation
│   └── scripts/10_integrations
├── config/
│   ├── hiring_pipeline.json
│   ├── email_templates/
│   └── candidate_fields.json
└── logs/
```

---

## 5) Risks & Mitigations

- Breaking changes in core → Semantic versioning + migration scripts
- User edits in core → Privacy fence + warnings + checks
- Transcript formats vary → Normalization layer + tests
- Email send failures → Retry + queued outbox + manual review path

---

## 6) Testing Plan

- Dry-run mode for orchestrator
- Golden-path tests on demonstrator Zo
- Error-path tests: missing transcript, malformed list entries, CRM conflicts
- State verification: lists updated, profiles updated, drafts generated

---

## 7) Rollout Plan

1. Create n5-core repo (developer-setup.sh)
2. Package modules (per selection doc)
3. Write docs: QUICKSTART_HIRING_ATS.md, PIPELINE_SETUP.md
4. Install on demonstrator Zo; validate
5. Pilot with 1–2 external Zo users
6. Iterate, tag v1.0.0, publish

---

## 8) Open Questions

- Finalize minimal set of meeting processors for v1
- Required candidate fields for profiles
- Email templates bundle (offer, rejection variants)

---

## 9) Approval

- [ ] Architecture approved (link decision)
- [ ] Implementation green light
- [ ] Pilot candidates identified

---

## Appendices

- System design workflow: `file 'N5/commands/system-design-workflow.md'`
- Component selection: `file 'Documents/System/Proposals/N5_HIRING_ATS_COMPONENTS.md'`
- Distribution pattern summary: `file '/home/.z/workspaces/con_W1mgxuDoKE4Jui2Y/DISTRIBUTION_PATTERN_SUMMARY.md'`
