# Zero-Touch Analysis: File Storage & Flow

Generated: 2025-10-24T15:25:00Z  
Context: Applying Zero-Touch manifesto principles to N5 file storage architecture

---

## Current State: Pools vs Flows

### POOLS (where files rot) ❌
1. **Root directory** - 17 loose files (resumes, logs) sitting with no flow
2. **Notes/** - Generic catch-all, no onward flow to Careerspan/Personal
3. **Document Inbox/Temporary** - IF used as permanent storage (currently unclear)
4. **Backups, Exports, Under Construction** - Accumulation without flow or TTL
5. **.n5_backups, .n5-ats-backups, .migration_backups** - Multiple backup pools

### FLOWS (where files move) ✓
1. **Records/Temporary → Knowledge/Lists** - Work-in-progress → permanent
2. **Documents/Archive** - Terminal state with clear semantics
3. **N5/logs/** - System logs flow here (when routing works correctly)

**Problem**: System has NO ACTIVE ROUTING. Files land at root by default, then sit forever.

---

## Zero-Touch Principles Applied to File Storage

### Principle: "Organization Step Shouldn't Exist"

**Current Reality**: Every file uploaded/created requires manual filing decision  
**Zero-Touch Goal**: Files auto-route based on type/context/origin

**Implementation**:
```
File enters system
  ↓
Assess: What is it? (resume/log/meeting-note/article/image/code)
  ↓
Intervene: Route to canonical location via anchors.json
  ↓
Review: Surface in daily digest for confirmation
```

### Principle: "Flow vs Pools"

**Temporary Storage Decision** (V's question):

**Option A: Document Inbox/Temporary as FLOW** ✓ RECOMMENDED
- Purpose: Triage/staging for items requiring human classification
- TTL: 7 days max, then auto-archive or delete
- Flow: Upload → Inbox/Temporary → [Human: categorize] → Final destination
- Self-healing: Weekly digest shows stale items (>7 days)

**Option B: Records/Temporary as SCRATCH** ✓ KEEP FOR DIFFERENT PURPOSE
- Purpose: Ephemeral working files (script outputs, temp conversions, downloads)
- TTL: 24-48 hours, aggressive auto-cleanup
- Flow: Create → Use → Delete (never promoted to permanent storage)
- Self-healing: Nightly cleanup of files >48hrs old

**Verdict**: BOTH, but with distinct semantics:
- `Document Inbox/Temporary/` = Human triage queue (flow channel)
- `Records/Temporary/` = Machine scratch space (ephemeral pool with TTL)

### Principle: "Maintenance > Organization"

**Anti-Pattern**: "Organize everything once, then maintain"  
**Zero-Touch Pattern**: "Build self-maintaining flows, review exceptions"

**File maintenance rhythms**:
- **Nightly**: Detect misplaced files (root sprawl, wrong folders)
- **Daily**: Review queue of files needing classification (Inbox/Temporary)
- **Weekly**: Hygiene report (duplicates, stale files, broken flows)
- **Monthly**: Flow evaluation (what's pooling? what needs new channels?)

### Principle: "Self-Healing by Design"

**File system should detect and flag**:
1. Files at root (except whitelisted: README, .gitignore, etc)
2. Files >7 days in Document Inbox/Temporary
3. Files >48hrs in Records/Temporary  
4. Duplicate basenames in different locations
5. Case-variant folder siblings (Projects vs projects)
6. Empty files
7. Orphaned SESSION_STATE.md in user workspace

**Implementation**: `N5/scripts/file_hygiene_detector.py` (runs nightly via cron or scheduled task)

### Principle: "AIR Pattern (Assess → Intervene → Review)"

**Resume upload example**:
```
1. ASSESS
   - File type: .pdf
   - Content scan: "resume", "experience", name patterns
   - Classification: RESUME
   
2. INTERVENE
   - Extract candidate name from content
   - Route: Documents/Resumes/{Name}_{Date}.pdf
   - Log: file_flow_log.jsonl (timestamp, classification, destination)
   
3. REVIEW
   - Daily digest: "10 resumes auto-filed today. Review?"
   - V spot-checks, confirms or corrects
   - System learns from corrections
```

**Log file example**:
```
1. ASSESS
   - File type: .log
   - Origin: N5 bootstrap script (detected via filename pattern)
   - Classification: SYSTEM_LOG
   
2. INTERVENE
   - Route: N5/logs/{script_name}_{timestamp}.log
   - Rotate if >100MB
   
3. REVIEW
   - Weekly: "12 logs generated. Any errors flagged?"
```

---

## Meeting Notes Architecture

**V's context**: Careerspan meetings + other business (Zo Consultancy?) + personal

**Current state**: Generic `Notes/` at root (POOL)

**Zero-Touch structure**: Context-specific flows

```
Careerspan/Meetings/
  ├── 2025-10-24_ClientName_TopicSlug.md
  └── index.md (auto-generated list)

Personal/Meetings/
  ├── 2025-10-24_PersonName_TopicSlug.md
  └── index.md

Zo Consultancy/Meetings/  (if separate business)
  ├── 2025-10-24_ClientName_TopicSlug.md
  └── index.md
```

**Flow**:
1. Meeting happens → AI transcribes
2. ASSESS: Detect attendees, keywords → classify business context
3. INTERVENE: Route to appropriate Meetings/ folder with standard naming
4. REVIEW: V confirms classification in daily digest

**Eliminate**: `Notes/` root folder (migrate contents, delete folder)

---

## Anti-Patterns → Enforcement Mechanisms

| Anti-Pattern | Root Cause | Zero-Touch Fix |
|--------------|------------|--------------|
| AP-001: Root file sprawl | No default routing | File Flow Router (assess all new files at root) |
| AP-002: System artifacts at root | Scripts write to CWD | Path Guard (scripts MUST use canonical paths) |
| AP-003: Case-variant siblings | No normalization | Path Guard (reject case-ambiguous mkdir) |
| AP-004: Conversation leakage | Archival copies everything | Boundary Rule (never copy SESSION_STATE to user workspace) |
| AP-005: Generic catch-all folders | No context routing | Eliminate generic folders; force context-specific |
| AP-006: Top-level sprawl | Unconstrained mkdir | Path Guard (whitelist top-level; reject others) |

---

## Modular Architecture (Self-Contained Flows)

**V's requirement**: Discrete modules, self-contained except for command intersection

**Zero-Touch alignment**: "Platform Orchestration" - best-in-class components with intelligent routing

### Module Structure
```
N5/modules/
  ├── resume-flow/
  │   ├── assess.py       # Detect resume files
  │   ├── intervene.py    # Route to Documents/Resumes/
  │   ├── review.py       # Generate digest
  │   ├── schema.json     # Flow contract
  │   └── README.md       # Module purpose
  │
  ├── meeting-flow/
  │   ├── assess.py       # Classify meeting context
  │   ├── intervene.py    # Route to appropriate Meetings/
  │   ├── review.py       # Generate digest
  │   └── schema.json
  │
  ├── log-flow/
  │   ├── assess.py       # Detect system logs
  │   ├── intervene.py    # Route to N5/logs/
  │   ├── review.py       # Flag errors
  │   └── schema.json
  │
  └── file-hygiene/
      ├── detect.py       # Nightly violation scan
      ├── report.py       # Weekly hygiene report
      └── schema.json
```

**Command layer (orchestration)**:
```
N5/commands/file-flow.md
  - Calls resume-flow, meeting-flow, log-flow modules
  - Coordinates AIR pattern across modules
  - Aggregates review queues into single digest
```

**Intersection points**:
- `anchors.json` - Canonical paths (SSOT for routing)
- `commands.jsonl` - Registered commands that trigger flows
- `file_flow_log.jsonl` - Audit trail of all routing decisions
- Review queues (consolidated by command layer)

---

## Revised Cleanup Plan (Zero-Touch Edition)

### Phase 1: Immediate (Demo Prep)
1. **Eliminate root pools**: Move resumes/logs to canonical locations
2. **Kill generic catch-all**: Migrate Notes/* to context-specific Meetings/
3. **Consolidate case-variants**: projects → Projects (single canonical)
4. **Archive legacy**: Exports → N5/exports/legacy_2025-10-24

### Phase 2: Flow Infrastructure (Post-Demo)
1. **Build File Flow Router** (`N5/scripts/file_flow_router.py`)
   - Scans root directory every 5 minutes
   - Assesses files via type/content/origin
   - Routes to canonical locations
   - Logs decisions to file_flow_log.jsonl
   
2. **Build Path Guard** (`N5/scripts/path_guard.py`)
   - Pre-flight check before mkdir/touch operations
   - Validates against anchors.json
   - Rejects non-canonical paths
   - Prompts for clarification if ambiguous
   
3. **Build Hygiene Detector** (`N5/scripts/file_hygiene_detector.py`)
   - Nightly scan for anti-patterns
   - Generates violations.json
   - Surfaces in daily review queue

### Phase 3: Modular Flows (Week 2+)
1. Build resume-flow module (highest volume)
2. Build meeting-flow module (highest context value)
3. Build log-flow module (system maintenance)
4. Add article-capture, idea-capture flows as needed

### Phase 4: Review Rhythms (Week 3+)
1. Daily digest: file_flow_router decisions + hygiene violations
2. Weekly report: flow health, pool detection, routing accuracy
3. Monthly evaluation: flow redesign, new channels, module performance

---

## Success Metrics (Zero-Touch Applied)

**Flow health**:
- Files at root <3 at any time (whitelisted only)
- Average time from capture to canonical location <5 minutes
- Manual filing operations per week <10 (down from ~50+)

**Context quality**:
- Meeting notes retrievable by context (business/person) in <30 seconds
- Resumes findable by name in <10 seconds
- Zero "where did I put that?" moments

**System trust**:
- V stops checking if files landed correctly (system reliability >95%)
- Review time <5min daily, <30min weekly
- Cognitive load drops (subjective but measurable via reflection)

---

## Recommendation Summary

**For V's immediate questions**:

1. **Temporary folders**: Keep BOTH with distinct purposes
   - `Document Inbox/Temporary` = Human triage flow (7-day TTL)
   - `Records/Temporary` = Machine scratch (48-hour TTL)

2. **Meeting notes**: Context-specific, not generic
   - Careerspan/Meetings, Personal/Meetings, [Other Business]/Meetings
   - Eliminate Notes/ root folder

3. **Projects**: Single canonical `Projects/` (capital P)
   - Migrate projects/* → Projects/*
   - Delete empty projects/ folder

4. **Modular architecture**: Align with Zero-Touch platform orchestration
   - Self-contained flow modules in N5/modules/
   - Command layer as orchestrator
   - Anchors.json as routing SSOT

**Next steps**: Execute Phase 1 cleanup, then build Flow Infrastructure (Phase 2)

---

*Principles applied: Flow vs Pools, AIR Pattern, Self-Healing, Organization Step Shouldn't Exist, Minimal Touch*
