---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.4
type: build_plan
status: complete
provenance: con_ctpO4tmxumzIn8RP
---
# Plan: Resonance Reservoir — Distinguishing Pattern from Novelty

**Objective:** Build a "Semantic Memory" layer that allows the Context Graph system to distinguish between V's established mental models (his "toolbox") and genuinely novel ideas—preventing repetitive extraction while surfacing true intellectual edge.

**Trigger:** V observed that meeting-by-meeting extraction treats every idea as novel, even when it's the 15th time he's mentioned "meaning-level intelligence." This creates noise and obscures what's actually new in his thinking.

**Key Insight:** The goal isn't to *suppress* recurring patterns—it's to *classify* them differently. A "Cornerstone" that appears in 20 meetings is valuable metadata about V's intellectual identity. A "Spark" that appears once is a candidate for exploration.

---

## Core Concepts

### The Resonance Hierarchy

| Level | Name | Frequency | Treatment |
|-------|------|-----------|-----------|
| **L0** | Cornerstone | 10+ meetings | V's foundational beliefs. Don't re-extract; reference as context. |
| **L1** | Active Thesis | 4-9 meetings | Ideas V is currently developing. Track evolution, not repetition. |
| **L2** | Recurring Tool | 2-3 meetings | Frameworks V reaches for. Note when applied to new domains. |
| **L3** | Spark | 1 meeting | Novel idea. Extract fully, flag for attention. |

### The Three Functions

1. **Pattern Surfacing** — Periodically analyze `edges.db` to identify what's moved up the hierarchy.
2. **Contextual Priming** — Feed the extractor a "What V Already Knows" context so it can distinguish novelty.
3. **Evolution Tracking** — When a Cornerstone *does* appear, check if there's a pivot, refinement, or challenge.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RESONANCE RESERVOIR                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   edges.db   │───▶│   Pattern    │───▶│  Resonance   │       │
│  │ (raw edges)  │    │  Surfacer    │    │   Index      │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                 │                │
│                                                 ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  New Meeting │───▶│  Contextual  │───▶│     B33      │       │
│  │  (for B33)   │    │   Primer     │    │  Extractor   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                 │                │
│                                                 ▼                │
│                                          ┌──────────────┐       │
│                                          │  Evolution   │       │
│                                          │   Tracker    │       │
│                                          └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Structures

**Resonance Index** (`N5/data/resonance_index.json`):
```json
{
  "generated_at": "2026-01-09T16:30:00Z",
  "cornerstones": [
    {
      "idea_slug": "meaning-level-intelligence",
      "label": "Meaning-Level Intelligence",
      "frequency": 23,
      "first_seen": "2025-10-15",
      "last_seen": "2026-01-09",
      "sample_contexts": ["hiring", "AI assistants", "search"]
    }
  ],
  "active_theses": [...],
  "recurring_tools": [...],
  "recent_sparks": [...]
}
```

**Evolution Log** (`N5/data/evolution_log.jsonl`):
```jsonl
{"date": "2026-01-09", "idea": "meaning-level-intelligence", "event": "domain_expansion", "from": "hiring", "to": "personal productivity", "meeting_id": "mtg_2026-01-09_xyz"}
{"date": "2026-01-08", "idea": "information-overload-scam", "event": "challenged", "by": "david-spiegel", "meeting_id": "mtg_2026-01-08_abc"}
```

---

## Open Questions

- [x] Where does Resonance Index live? → `N5/data/resonance_index.json`
- [x] How often to regenerate? → Daily (via scheduled agent) + on-demand
- [x] What's the threshold for each level? → L0: 10+, L1: 4-9, L2: 2-3, L3: 1
- [ ] Should "person" entities also have resonance levels? → **Defer to Phase 2**
- [ ] Should we track "idea combinations" (e.g., "meaning-level + hiring")? → **Defer to Phase 2**

---

## Phase Checklist

### Phase 1: Pattern Surfacing Engine
- [x] Create `N5/scripts/resonance/` directory structure
- [x] Create `N5/scripts/resonance/pattern_surfacer.py`
  - Query `edges.db` for idea frequency counts
  - Classify ideas into L0/L1/L2/L3 based on thresholds
  - Generate `resonance_index.json`
  - Output human-readable summary for review
- [x] Create `N5/data/resonance_index.json` (initial generation)
- [x] Test: Run on current edges.db, validate classification
  - Result: 255 total ideas (0 L0, 3 L1, 38 L2, 214 L3)
  - First report saved to `N5/insights/resonance/2026-01-09_resonance_report.md`

### Phase 2: Contextual Primer for Extraction
- [x] Create `N5/scripts/resonance/contextual_primer.py`
  - Read `resonance_index.json`
  - Generate a "Context Block" for B33 extraction prompts
  - Format: "V's Established Framework" section listing Cornerstones + Active Theses
- [x] Update `edge_backfill.py` to call primer before generating extraction prompt
  - Added `HAS_PRIMER` flag and `generate_context_block()` integration
  - Primer automatically injected into batch prompts
- [x] Update `Generate_B33.prompt.md` with new instructions:
  - Added `<!-- INJECT_CONTEXT -->` marker
  - Added "Resonance-Aware Extraction" section
  - Added `evolves` relation type with `evolution_type` field
  - Added hierarchy rules (L0-L3) and extraction guidance
- [x] Test: Verified batch prompt now includes full contextual primer
  - Successfully injects Active Theses (3) and Recurring Tools (20) into extraction prompt

### Phase 3: Evolution Tracking
- [x] Create `N5/scripts/resonance/evolution_tracker.py`
  - Compare new edges against Resonance Index
  - Detect: domain_expansion, refinement, challenge, abandonment
  - Append to `evolution_log.jsonl`
  - Commands: analyze, check, history, report
- [x] Add `evolution_type` field to edge schema (optional field)
  - Added column to edges table via ALTER TABLE
- [x] Update `edge_writer.py` to accept evolution metadata
  - Added evolution_type parameter with validation
- [x] Update `edge_types.py` to include 'evolves' relation
  - Added EVOLUTION category and 'evolves' EdgeType
- [x] Test: Manually create evolution event, verify logging
  - Tested with sample edges: detected domain_expansion and challenge
  - Evolution log created at `N5/data/evolution_log.jsonl`
  - Report generation working

### Phase 4: Surfacing to V (The Mirror)
- [~] Create `N5/scripts/resonance/weekly_resonance_report.py` — **Skipped per V's preference** (no more weekly digests)
- [x] Create `N5/insights/resonance/` output directory — Created in Phase 1
- [~] Add to Morning Digest (optional section when notable movement) — **Skipped per V's preference**
- [x] Create standalone prompt: `@Resonance Report`
  - Created at `Prompts/Resonance Report.prompt.md`
  - Marked as `rotation_eligible: true` for Prompt of the Day system
- [x] Create Prompt of the Day rotation config
  - Created at `N5/config/prompt_rotation.json`
  - Categories: self-reflection, system-health, knowledge-management
  - Resonance Report added to self-reflection (weekly frequency)
- [~] Test: Generate first weekly report — **Skipped** (ad-hoc use via prompt instead)

### Phase 5: Integration & Automation
- [x] Update scheduled backfill agent to use contextual primer
  - Updated agent `13199a59` with LIFO + Resonance-Aware extraction
  - Removed "self-destruct" date (now perpetual)
  - Agent now regenerates resonance index before each run
- [x] Add resonance index regeneration to daily maintenance
  - Created `N5/scripts/resonance/daily_maintenance.py`
  - Commands: regenerate, status
  - Tested: Successfully regenerates index and saves daily reports
- [x] Add evolution tracking to edge commit pipeline
  - Updated `edge_reviewer.py` to call `evolution_tracker.analyze_edges_for_evolution` on commit
  - Evolution events automatically logged to `N5/data/evolution_log.jsonl`
- [x] Documentation: Context Graph docs updated with Resonance system
  - PLAN.md serves as living documentation
  - Prompt rotation config at `N5/config/prompt_rotation.json`

---

## Build Complete ✅

**Completed:** 2026-01-09
**Total Phases:** 5/5 (100%)
**All artifacts created and tested.**

---

## Trap Doors Identified 🚨

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Frequency thresholds (10/4/2/1) | HIGH — Just config values | Start conservative, tune based on V's feedback |
| Single resonance_index.json | MEDIUM — Could split by category | Keep simple; if needed, add `category` field |
| Evolution types vocabulary | MEDIUM — Can add, hard to rename | Start with 4: domain_expansion, refinement, challenge, abandonment |
| Daily regeneration cadence | HIGH — Trivial to change | Default daily; can switch to on-demand if costly |

---

## Success Criteria

1. **No Duplicate Noise**: Running B33 on 10 meetings doesn't surface "meaning-level intelligence" 10 times.
2. **Novelty Detection**: Genuine sparks are flagged and easy to find.
3. **Evolution Awareness**: When a Cornerstone *is* mentioned, we capture *what changed*.
4. **V Can Query**: V can ask "What are my active theses right now?" and get a clean answer.
5. **Automated Maintenance**: The system runs without manual intervention after initial setup.

---

## Estimated Effort

| Phase | Complexity | Estimated Time |
|-------|------------|----------------|
| Phase 1 | Low | 30 min |
| Phase 2 | Medium | 45 min |
| Phase 3 | Medium | 30 min |
| Phase 4 | Low | 30 min |
| Phase 5 | Low | 20 min |
| **Total** | | **~2.5 hours** |

---

## Dependencies

- **Existing**: `edges.db`, `edge_writer.py`, `edge_backfill.py`, `Generate_B33.prompt.md`
- **No new external dependencies**
- **LLM calls**: Only in Phase 2 (contextual primer generation) and Phase 4 (report generation)

---

## Next Action

**Phase 1 is ready for execution.** 

On V's approval, I will:
1. Create the `N5/scripts/resonance/` directory
2. Build `pattern_surfacer.py`
3. Generate the initial `resonance_index.json` from current `edges.db`
4. Present the first "Resonance Report" showing V's current intellectual hierarchy






