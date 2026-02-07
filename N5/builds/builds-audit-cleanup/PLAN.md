---
created: 2026-01-31
last_edited: 2026-01-31
version: 1.0
provenance: con_Hu4WkuDzfHlguK3L
---

# Build Plan: builds-audit-cleanup

## Purpose

Systematically audit all builds in `N5/builds/`, identify what's stale/incomplete/superseded, extract learnings worth preserving, and clean up the build directory.

## Context

- **111 builds** flagged as incomplete (most have no meta.json)
- **30 builds** have no git activity since 2025 (stale)
- **8 builds** marked "active" but may be complete or abandoned
- Meeting-related builds may be superseded by `meeting-ingestion` skill
- Careerspan builds need assessment for what to keep vs archive

## Streams

### Stream 1: Assessment (Parallel)

| Drop | Title | Description |
|------|-------|-------------|
| D1.1 | Audit Active Builds | Check the 8 "active" builds, determine true status, fix meta.json |
| D1.2 | Extract 2025 Learnings | Review 30 stale builds, extract any valuable learnings/patterns |
| D1.3 | Meeting Builds Audit | Which meeting-* builds are superseded by `meeting-ingestion` skill? |

### Stream 2: Cleanup (After S1)

| Drop | Title | Description | Depends On |
|------|-------|-------------|------------|
| D2.1 | Archive Stale Builds | Move confirmed stale builds to `N5/builds/_archive/` | D1.1, D1.2 |
| D2.2 | Document Decomposer Endpoint | Spec for webhook endpoint when Careerspan pushes data | Independent |

## Success Criteria

- [ ] All 8 "active" builds have accurate status in meta.json
- [ ] Learnings extracted from valuable 2025 builds before archival
- [ ] Clear verdict on meeting-* build status (keep/archive)
- [ ] Stale builds moved to _archive (recoverable)
- [ ] Decomposer endpoint requirements documented

## Data

### Active Builds to Audit (D1.1)

```
task-system-wiring
gamma-survey-dashboard
b05-backfill-extended
workos-integration
personal-site-v1
n5os-ode-v2
store-v2
meeting-ingestion-skill
```

### 2025 Stale Builds (D1.2)

```
architectural-redesign-v2 (2025-11-02)
mode-system-cleanup (2025-11-02)
orchestrator-enhancements-v1 (2025-11-03)
cognition-layer-v1 (2025-12-26)
cost-guard (2025-12-26)
google-flights-refactor (2025-12-26)
istrategies-recon (2025-12-26)
lists-markdown-view-enhancement (2025-12-26)
lists-storage-standards (2025-12-26)
semantic-cleanup-v1 (2025-12-26)
architectural-redesign-v1 (2025-12-28)
capability-registry-v1 (2025-12-28)
con_O6Yh7sdM0GUavX0N (2025-12-28)
con_wmTTLgn0WG4i79O4 (2025-12-28)
crm-v3-enrichment (2025-12-28)
crm-v3-unified (2025-12-28)
email-allowlist (2025-12-28)
eric-zo-demo-intel (2025-12-28)
example-build (2025-12-28)
knowledge-realignment-v1 (2025-12-28)
llm-extraction-integration (2025-12-28)
media-documents-system (2025-12-28)
meeting-intel-gen-vrijen-miami (2025-12-28)
meeting-intelligence-davit-shadunts (2025-12-28)
meeting-intelligence-gen-con_4bCmrQsySGzDYwci (2025-12-28)
meeting-intelligence-gen-con_aWbhQiGMBR2dM7HM (2025-12-28)
meeting-pipeline-v2-BUILD (2025-12-28)
smart-event-detector (2025-12-28)
wheres-v-revamp (2025-12-28)
zorg-due-diligence (2025-12-28)
```

### Meeting Builds to Assess (D1.3)

```
MG-2
meeting-ingestion-skill
meeting-intel-gen-vrijen-miami
meeting-intelligence-davit-shadunts
meeting-intelligence-gen-con_4bCmrQsySGzDYwci
meeting-intelligence-gen-con_aWbhQiGMBR2dM7HM
meeting-pipeline-v2-BUILD
mg2-intelligence-gen
mg2-careerspan-2025-12-16
mg2-ilyamycareerspancom-duplicate
mg2-hydrogen-quarantine
unified-meeting-intake
```

---

## Checklist

### Stream 1: Assessment
- [ ] D1.1: Audit active builds
- [ ] D1.2: Extract 2025 learnings
- [ ] D1.3: Meeting builds audit

### Stream 2: Cleanup
- [ ] D2.1: Archive stale builds
- [ ] D2.2: Document decomposer endpoint
