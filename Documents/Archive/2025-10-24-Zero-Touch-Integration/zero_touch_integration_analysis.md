# Zero-Doc → N5 Integration Analysis

## Executive Summary

Zero-Doc introduces 10 core principles that operate at a **higher abstraction level** than current architectural principles. They're productivity philosophy, not implementation rules. Integration strategy:

1. **Create new "Philosophy" layer** above Architectural Principles
2. **Derive system design implications** from Zero-Doc principles
3. **Realign N5 architecture** around flow vs. pools
4. **Extract implementation patterns** for new architectural principles

---

## Principle Mapping: Zero-Doc → Architectural

| Zero-Doc Principle | Current Coverage | Gap | Action |
|--------------------|------------------|-----|--------|
| 1. Context + State Framework | Partial (P8: Minimal Context) | Missing state management philosophy | NEW: P23 - State Management |
| 2. Flow vs. Pools | None | Core metaphor missing | NEW: P24 - Information Flow Design |
| 3. Organization Step Shouldn't Exist | Partial (P7: Idempotence implies automation) | Not explicit | NEW: P25 - Automated Organization |
| 4. Maintenance > Organization | Implied by review systems | Not codified | NEW: P26 - Maintenance-First Design |
| 5. Self-Healing by Design | Strong (P11: Failure Modes, P19: Error Handling) | **COVERED** ✅ | Reference in new philosophy doc |
| 6. Gestalt Evaluation | Partial (P20: Modular Design) | Needs system-level thinking | ENHANCE: P20 + NEW: P27 - System Integration |
| 7. AIR Pattern | None | Core workflow pattern | NEW: P28 - Assess-Intervene-Review |
| 8. Minimal Touch | Partial (automation implied) | Not explicit | NEW: P29 - Human-in-Loop Design |
| 9. SSOT Always | Strong (P2: Single Source of Truth) | **COVERED** ✅ | Reference in philosophy |
| 10. Platform Orchestration | None | System architecture pattern | NEW: P30 - Platform Orchestration |

**Summary**: 2 fully covered, 3 partial, 5 net new → **Add 8 new principles**

---

## N5 Architecture Alignment Analysis

### Current N5 Structure (Flow Analysis)

```
Knowledge/    → POOL (mostly static, rarely flows back out)
Lists/        → FLOW (actionable, moves through states)
Records/      → STAGING (designed to flow → Knowledge/Lists)
  ├─ Company/    POOL risk (meetings pile up)
  ├─ Personal/   POOL risk
  └─ Temporary/  FLOW (7-day auto-delete)
N5/           → META (system managing the system)
```

**Diagnosis**: Records/ is designed for flow, but Company/ and Personal/ subdirs become POOLS in practice.

### Zero-Doc Ideal Structure

```
Intake/       → Everything enters here (AIR: Assess)
Processing/   → Transformations happen (AIR: Intervene)
Output/       → Knowledge OR Actions OR Archive (AIR: Review outcome)
System/       → Operating rules
```

**Key difference**: N5 has category-based dirs (Company/Personal), Zero-Doc has flow-stage dirs (Intake/Processing/Output).

### Recommendation: Hybrid Approach

Keep N5's SSOT categories (Knowledge/Lists) but restructure Records/ to emphasize flow:

```
Records/
  ├─ Intake/           ← Everything enters here first (AIR: Assess)
  │   ├─ voice/        (transcribe automatically)
  │   ├─ web/          (summaries automatically)
  │   ├─ email/        (parse automatically)
  │   └─ raw/          (manual processing)
  │
  ├─ Processing/       ← Active transformation (AIR: Intervene)
  │   ├─ Company/      (work-in-progress for business)
  │   ├─ Personal/     (work-in-progress for personal)
  │   └─ pending/      (needs human decision)
  │
  └─ Temporary/        ← Already correct (7-day retention)
```

**Key wins**:
- Clear flow stages (Intake → Processing → Knowledge/Lists)
- AIR pattern embedded in structure
- Pool detection: anything in Processing/ > 7 days gets flagged
- Company/Personal become processing contexts, not permanent homes

---

## New Architectural Principles (Draft)

### P23: State Management Philosophy

**Statement**: Every system component must maintain and expose its current state. State should be queryable, auditable, and recoverable.

**Rationale**: Zero-Doc Principle 1 (Context + State). You can't maintain context without knowing state.

**Implementation**:
- Every workflow logs: current stage, pending items, last update
- State files use standard format (JSONL or SQLite)
- `state-check` command shows system-wide state
- No "black box" processes—everything exposable

**Example**:
```bash
$ n5 state-check
Records/Intake: 3 items awaiting triage (2 auto, 1 manual)
Records/Processing/Company: 5 items > 3 days old [POOL WARNING]
Lists: 12 active, 3 stale (>30d no update)
Knowledge: Last ingest 2 days ago
```

---

### P24: Information Flow Design

**Statement**: Design systems for information flow, not information storage. Every category should have defined entry, transformation, and exit paths.

**Rationale**: Zero-Doc Principle 2 (Flow vs. Pools). Pools = graveyards.

**Implementation**:
- Map flow for each info type (articles, meetings, ideas, emails)
- Define max residence time per stage (e.g., Intake: 24hr, Processing: 7d)
- Alert when information pools beyond expected time
- Regular flow audits to identify new pools

**Anti-pattern**: Folders that accumulate indefinitely without exit path.

**Example**:
```
Article saved → Intake/ (auto-summarize) → Processing/ (weekly review) 
  → Knowledge/ (if valuable) OR Archive/ (if not)
Max time: 24hr → 7d → permanent
```

---

### P25: Automated Organization Philosophy

**Statement**: Organization should emerge from use, not require manual intervention. Design systems where categorization and routing happen automatically with human review for exceptions.

**Rationale**: Zero-Doc Principle 3 (Organization Step Shouldn't Exist).

**Implementation**:
- AI-driven initial routing based on content analysis
- Folder structure reflects flow stages, not manual categories
- Human review only for edge cases or quality control
- System learns from review corrections

**Key metric**: % of items flowing without manual routing decisions.

**Example**: Voice note → Auto-transcribe → Auto-categorize → Route to Processing/Company → Flag for weekly review → User confirms → Moves to Knowledge.

---

### P26: Maintenance-First Design

**Statement**: Design for continuous maintenance, not one-time organization. Systems should include regular review rhythms and health checks built in.

**Rationale**: Zero-Doc Principle 4 (Maintenance > Organization).

**Implementation**:
- Daily/Weekly/Monthly review schedules baked into system
- Automated health checks (pool detection, stale items, orphaned files)
- Review generates actionable reports, not just status
- Maintenance commands are first-class citizens

**Pattern**:
```bash
# Daily (automated)
n5 health-check --daily

# Weekly (human-in-loop)
n5 review --weekly

# Monthly (system evaluation)
n5 audit --full
```

---

### P27: System Integration Patterns

**Statement**: Optimize for system-wide effectiveness, not individual component excellence. Evaluate changes by their impact on the entire information flow, not isolated metrics.

**Rationale**: Zero-Doc Principle 6 (Gestalt Evaluation).

**Implementation**:
- Before adding tools: map how they integrate with existing flows
- Track cross-system metrics (end-to-end processing time, not per-stage)
- Integration points are documented and versioned
- Regular "flow mapping" exercises to see whole system

**Questions to ask**:
- Does this improve flow or create a pool?
- Does this reduce cognitive load or just shift it?
- How does this interact with 3+ other components?

---

### P28: Assess-Intervene-Review Pattern (AIR)

**Statement**: Every information intake should follow the AIR pattern: Assess (categorize/route), Intervene (transform/act), Review (confirm/correct). Automate Assess and Intervene, human-control Review.

**Rationale**: Zero-Doc Principle 7 (AIR Pattern).

**Implementation**:
- **Assess**: AI determines category, urgency, relationships
- **Intervene**: Automated transformations (summarize, extract, route)
- **Review**: Human confirms AI decisions, system learns from corrections

**Structure**:
```python
def air_pattern(item):
    # Assess
    assessment = ai.categorize(item)
    
    # Intervene
    transformed = ai.transform(item, assessment)
    route_to = determine_destination(assessment)
    move(transformed, route_to)
    
    # Review (human-in-loop)
    flag_for_review(transformed, confidence=assessment.confidence)
```

**Key insight**: Not everything needs Review. High-confidence Assess + Intervene can auto-complete.

---

### P29: Human-in-Loop Design

**Statement**: Humans should be approvers and exception handlers, not operators. Design workflows where AI handles routine operations and humans provide judgment on edge cases.

**Rationale**: Zero-Doc Principle 8 (Minimal Touch).

**Implementation**:
- Default: AI does the work
- Human intervention: Only when confidence < threshold OR user request
- Review queues surface decisions needing judgment
- System tracks which decisions humans override (learning signal)

**Pattern**:
```
95% of items: AI Assess → AI Intervene → Auto-complete
4% of items: AI Assess → AI Intervene → Human Review → Complete
1% of items: AI Assess → Human Intervene → Human Review → Complete
```

**Metric**: Track "touch rate" - goal is <10% items requiring human routing decisions.

---

### P30: Platform Orchestration

**Statement**: Use best-in-class tools for specific jobs, orchestrated by intelligent routing. Avoid all-in-one solutions. Prefer interoperable components with centralized coordination.

**Rationale**: Zero-Doc Principle 10 (Platform Orchestration).

**Implementation**:
- Each tool has one primary job (git=sync, sqlite=structured, markdown=text)
- N5 is the orchestrator (knows routes, rules, transformations)
- Standard interfaces between components (file-based, APIs)
- New tools integrate via adapters, not replacements

**Architecture**:
```
N5 (orchestrator)
  ├─ Zo (compute + AI)
  ├─ Git (sync + version control)
  ├─ SQLite (structured queries)
  ├─ Markdown (portable text)
  └─ [future tool] (new capability)
```

**Anti-pattern**: "All-in-one" tools that do everything poorly. Notion is great until you need to script it. Obsidian is great until you need structured data.

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
1. **Create philosophy doc**: `Knowledge/architectural/zero_doc_philosophy.md` (link existing manifesto)
2. **Add 8 new principles**: P23-P30 to architectural principles
3. **Update principle index**: Reference Zero-Doc philosophy layer

### Phase 2: Structural Changes (Week 3-4)
1. **Restructure Records/**: Intake → Processing → (Knowledge/Lists)
2. **Implement pool detection**: Script to flag items pooling in Processing/
3. **Add state-check command**: System-wide state visibility
4. **Document flow maps**: For each info type (articles, meetings, etc.)

### Phase 3: AIR Implementation (Week 5-8)
1. **Build AIR framework**: Core pattern for all intakes
2. **Implement 3 AIR loops**: Articles, Meetings, Voice notes
3. **Create review queues**: Weekly review of flagged items
4. **Add confidence scoring**: Track when human override needed

### Phase 4: Optimization (Week 9-12)
1. **Track metrics**: Touch rate, pool warnings, flow bottlenecks
2. **Iterate on routing**: Improve AI categorization based on corrections
3. **Add self-healing**: Automated checks for common failures
4. **Document patterns**: What worked, what didn't

---

## Open Questions

1. **Records/ restructure impact**: Current threads and workflows reference Company/Personal directly. Migration path?

2. **AIR confidence thresholds**: What % confidence triggers human review? Start conservative (>80%) or aggressive (>95%)?

3. **Review cadence**: Daily/Weekly/Monthly split - what goes in each?

4. **Metrics dashboard**: Should we build visual state/flow monitoring, or keep CLI?

5. **Backwards compatibility**: Keep old structure + add new, or full migration?

---

## Success Criteria

Zero-Doc integration successful when:

1. ✅ All 10 Zero-Doc principles mapped to architectural principles or philosophy
2. ✅ N5 structure reflects flow stages, not just categories
3. ✅ Pool warnings implemented and triggering correctly
4. ✅ At least 3 AIR loops operational
5. ✅ System state is queryable at any time
6. ✅ Touch rate < 15% (85% of items flow without manual routing)
7. ✅ Weekly reviews surface <50 items (cognitive load manageable)
8. ✅ New info types can be added by defining flow, not creating folders

---

**Next Step**: Get V's input on clarifying questions, then proceed with implementation.