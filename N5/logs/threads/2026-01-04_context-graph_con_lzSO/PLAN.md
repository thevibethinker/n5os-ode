---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.1
type: build_plan
status: in_progress
provenance: con_SCcyCoCBDyPJDc1i
---
# Plan: Context Graph System — Decision Tracing & Cognitive Mirror

**Objective:** Build an edge-based graph layer that captures the provenance, reasoning, and evolution of V's ideas and decisions, enabling pattern detection in his own thinking over time.

**Trigger:** V read Foundation Capital's "Context Graphs" article and recognized alignment with N5's meeting intelligence system. Wants to move from "capturing what happened" to "capturing why it happened and how ideas evolved."

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- All resolved in conversation prior to plan creation -->
- [x] Edge vocabulary: Finalized 6 core types (originated_by, supported_by, challenged_by, hoped_for, concerned_about, influenced_by)
- [x] Confidence tracking: NOT implementing (overkill)
- [x] Idea naming: Auto-generated slugs with V review
- [x] Review queue: `N5/review/edges/`
- [x] Backfill: YES, after forward pipeline proven
- [x] Query interface: Through Zo (natural language), not direct CLI

---

## Alternatives Considered (Nemawashi)

### Alternative A: Pure Graph Database (Neo4j/MemGraph)
**Pros:** Native graph queries, visualization tools, industry standard
**Cons:** Another service to run, overkill for single-user system, learning curve
**Decision:** REJECTED — SQLite is sufficient for V's scale. Can migrate later if needed.

### Alternative B: Extend Existing SQLite Tables
**Pros:** No new database, simpler architecture
**Cons:** Muddies existing schemas, edge queries would be awkward
**Decision:** REJECTED — Clean separation of concerns. Edges deserve their own store.

### Alternative C: JSONL Event Log (Append-Only)
**Pros:** Simple, immutable history, easy backups
**Cons:** No efficient querying, no status updates without rewriting
**Decision:** PARTIALLY ADOPTED — Use JSONL for review queue staging, SQLite for queryable store.

### Selected Approach: New SQLite database (`edges.db`) with JSONL review queue
**Rationale:** Queryable, supports status/lifecycle, clean separation from existing data, review queue provides human-in-the-loop before commit.

---

## Trap Doors Identified 🚨

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Edge vocabulary (6 types) | MEDIUM — Can add types, hard to rename/remove | Start minimal, expand only with evidence |
| Idea slug format | LOW — Referenced everywhere once created | Use `idea:<slug>` prefix, reserve ability to alias |
| SQLite vs graph DB | HIGH — Can migrate | Design schema with graph semantics in mind |
| B33 as extraction point | MEDIUM — Integrated into pipeline | Keep extraction logic modular, can swap source |

---

## Checklist

### Phase 1: Foundation (Database + Core Scripts)
- ☑ Create `N5/data/edges.db` with schema
- ☑ Create `N5/scripts/edge_writer.py` — Insert/update edges
- ☑ Create `N5/scripts/edge_query.py` — Query edges by entity, relation, trace chains
- ☑ Create `N5/scripts/edge_lifecycle.py` — Update status, link outcomes
- ☑ Test: Insert 5 manual edges, query them, trace a chain

### Phase 2: Extraction (B33 Block + Review Queue)
- ☑ Create `Prompts/Blocks/Generate_B33.prompt.md` — Edge extraction prompt
- ☑ Create `N5/review/edges/` directory structure
- ☑ Create `N5/scripts/edge_extractor.py` — Run B33, output to review queue
- ☑ Create `N5/scripts/edge_reviewer.py` — Process review queue, commit approved edges
- ☑ Test: Run on 3 recent meetings, review queue generates correctly

### Phase 3: Pipeline Integration
- ☑ Update `manifest.json` schema to include B33 status
- ☑ Integrate B33 into meeting processing flow (after B08, before archive)
- ☑ Create `N5/scripts/generate_b33_edges.py` — Pipeline-ready B33 generator
- ☑ Create `N5/scripts/meeting_b33_hook.py` — Integration hooks for batch processing
- ☑ Test: Full pipeline on 2 meetings captures edges automatically

### Phase 4: Cognitive Mirror (LLM-Powered Insight Layer)
- ☐ Create `N5/scripts/cognitive_mirror/` directory
- ☐ Create `N5/insights/cognitive_mirror/` output directory
- ☐ Create `N5/scripts/cognitive_mirror/decision_retrospective.py` — "Did what I hoped/feared happen?"
- ☐ Create `N5/scripts/cognitive_mirror/reversal_detector.py` — "Where am I inconsistent?"
- ☐ Create `N5/scripts/cognitive_mirror/influence_map.py` — "Who shapes my thinking?"
- ☐ Create `N5/scripts/cognitive_mirror/originated_vs_adopted.py` — "Do my ideas stick better than others'?"
- ☐ Create `N5/scripts/cognitive_mirror/decay_detector.py` — "What have I abandoned?"
- ☐ Test: Run each on current edge data, outputs are dated Markdown reports

### Phase 5: Backfill
- ☐ Create `N5/scripts/edge_backfill.py` — Process historical meetings
- ☐ Run on Week-of-2025-10-* through Week-of-2025-12-* folders
- ☐ Manual review pass on backfilled edges
- ☐ Test: Query "ideas originated by V in Q4 2025" returns results

---

## Phase 1: Foundation (Database + Core Scripts)

### Affected Files
- `N5/data/edges.db` - CREATE - SQLite database for edge storage
- `N5/data/edges_schema.sql` - CREATE - Schema definition (for reference/recreation)
- `N5/scripts/edge_writer.py` - CREATE - Insert/update edge records
- `N5/scripts/edge_query.py` - CREATE - Query interface for Zo
- `N5/scripts/edge_lifecycle.py` - CREATE - Status transitions, outcome linking
- `N5/lib/edge_types.py` - CREATE - Canonical edge type definitions

### Changes

**1.1 Database Schema (`edges.db`):**

```sql
-- Core edges table
CREATE TABLE edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Source entity
    source_type TEXT NOT NULL,  -- 'person', 'idea', 'decision', 'outcome', 'meeting'
    source_id TEXT NOT NULL,    -- Slug or ID in that domain
    
    -- Relation
    relation TEXT NOT NULL,     -- 'originated_by', 'supported_by', 'challenged_by', 
                                -- 'hoped_for', 'concerned_about', 'influenced_by',
                                -- 'preceded_by', 'led_to', 'depends_on'
    
    -- Target entity
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    
    -- Provenance
    context_meeting_id TEXT,    -- Which meeting surfaced this edge
    evidence TEXT,              -- Quote or summary justifying edge
    extracted_at TEXT NOT NULL, -- ISO timestamp
    
    -- Lifecycle
    status TEXT DEFAULT 'active',  -- 'active', 'superseded', 'reversed', 'decayed', 'invalidated'
    superseded_by INTEGER,         -- FK to edge that replaced this
    outcome_note TEXT,             -- "This worked because..." or "This failed because..."
    reviewed_at TEXT,              -- When V last validated this edge
    
    -- Metadata
    confidence TEXT,               -- Reserved for future (currently unused)
    
    FOREIGN KEY (superseded_by) REFERENCES edges(id)
);

-- Indexes for common queries
CREATE INDEX idx_edges_source ON edges(source_type, source_id);
CREATE INDEX idx_edges_target ON edges(target_type, target_id);
CREATE INDEX idx_edges_relation ON edges(relation);
CREATE INDEX idx_edges_meeting ON edges(context_meeting_id);
CREATE INDEX idx_edges_status ON edges(status);

-- Entity registry (for slug→display name mapping)
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- 'person', 'idea', 'decision', 'outcome'
    entity_id TEXT NOT NULL,    -- Slug
    display_name TEXT,          -- Human-readable name
    created_at TEXT NOT NULL,
    metadata TEXT,              -- JSON blob for type-specific data
    
    UNIQUE(entity_type, entity_id)
);

CREATE INDEX idx_entities_type ON entities(entity_type);
```

**1.2 Edge Type Definitions (`N5/lib/edge_types.py`):**

```python
"""Canonical edge type definitions for context graph."""

# Core reasoning edges
EDGE_TYPES = {
    # Provenance - who originated/supported/challenged
    "originated_by": {
        "description": "Who first voiced this idea",
        "source_types": ["idea", "decision"],
        "target_types": ["person"],
        "inverse": "originated"
    },
    "supported_by": {
        "description": "Who endorsed after hearing",
        "source_types": ["idea", "decision"],
        "target_types": ["person"],
        "inverse": "supports"
    },
    "challenged_by": {
        "description": "Who pushed back or raised concerns",
        "source_types": ["idea", "decision"],
        "target_types": ["person"],
        "inverse": "challenged"
    },
    
    # Reasoning - hoped for / concerned about
    "hoped_for": {
        "description": "Expected positive outcome",
        "source_types": ["idea", "decision"],
        "target_types": ["outcome"],
        "inverse": "motivated"
    },
    "concerned_about": {
        "description": "Feared risk or downside",
        "source_types": ["idea", "decision"],
        "target_types": ["outcome"],
        "inverse": "warned_against"
    },
    
    # Influence - shaped thinking on topic
    "influenced_by": {
        "description": "Who shaped thinking on this",
        "source_types": ["person", "idea"],
        "target_types": ["person"],
        "inverse": "influenced"
    },
    
    # Chains - logical dependencies
    "preceded_by": {
        "description": "This decision followed from a prior one",
        "source_types": ["decision"],
        "target_types": ["decision"],
        "inverse": "led_to"
    },
    "depends_on": {
        "description": "Logical dependency",
        "source_types": ["idea", "decision"],
        "target_types": ["idea", "decision"],
        "inverse": "enables"
    },
    "led_to": {
        "description": "Resulted in this outcome",
        "source_types": ["decision"],
        "target_types": ["outcome"],
        "inverse": "resulted_from"
    }
}

# Status values
EDGE_STATUSES = [
    "active",       # Currently valid
    "superseded",   # Replaced by newer edge
    "reversed",     # Explicitly overturned
    "decayed",      # Never acted on, effectively dead
    "invalidated"   # Outcome proved this wrong
]

# Entity type prefixes for ID generation
ENTITY_PREFIXES = {
    "person": "person:",
    "idea": "idea:",
    "decision": "decision:",
    "outcome": "outcome:",
    "meeting": "mtg:"
}
```

**1.3 Edge Writer (`N5/scripts/edge_writer.py`):**

Core operations:
- `add_edge(source_type, source_id, relation, target_type, target_id, context_meeting_id, evidence)` → Returns edge ID
- `ensure_entity(entity_type, entity_id, display_name)` → Creates entity if not exists
- `bulk_add_edges(edges_list)` → Batch insert from review queue
- `get_or_create_idea_slug(idea_description)` → Auto-generates slug like `idea:context-graph-adoption`

CLI interface:
```bash
# Add single edge
python3 edge_writer.py add \
    --source "idea:context-graph" \
    --relation "originated_by" \
    --target "person:animesh-koratana" \
    --meeting "mtg_2026-01-04" \
    --evidence "Animesh's article introduced the concept"

# Register entity
python3 edge_writer.py entity \
    --type "idea" \
    --id "context-graph" \
    --name "Context Graph System for N5"
```

**1.4 Edge Query (`N5/scripts/edge_query.py`):**

Core operations:
- `find_edges(source=None, target=None, relation=None, status="active")` → Filter edges
- `trace_provenance(entity_type, entity_id, depth=3)` → Trace back through `originated_by`, `preceded_by`
- `trace_outcomes(entity_type, entity_id)` → Find `hoped_for`, `concerned_about` and their validation status
- `find_by_person(person_id, relation=None)` → All edges involving a person
- `find_by_meeting(meeting_id)` → All edges from a meeting

CLI interface:
```bash
# Where did this idea come from?
python3 edge_query.py trace --entity "idea:context-graph"

# Who has influenced my thinking?
python3 edge_query.py find --relation "influenced_by" --source-type "person" --source-id "vrijen"

# What edges came from this meeting?
python3 edge_query.py meeting --id "mtg_2026-01-04"
```

Output format (JSON for Zo to parse):
```json
{
  "query": "trace idea:context-graph",
  "results": [
    {
      "edge_id": 1,
      "source": "idea:context-graph",
      "relation": "originated_by",
      "target": "person:animesh-koratana",
      "meeting": "mtg_2026-01-04",
      "evidence": "...",
      "status": "active"
    }
  ],
  "trace_depth": 2,
  "chain": ["idea:context-graph", "originated_by", "person:animesh-koratana"]
}
```

**1.5 Edge Lifecycle (`N5/scripts/edge_lifecycle.py`):**

Core operations:
- `supersede(old_edge_id, new_edge_id)` → Mark old as superseded, link to replacement
- `reverse(edge_id, reason)` → Mark as reversed with note
- `decay(edge_id)` → Mark as decayed (stale)
- `link_outcome(edge_id, outcome_note, validated=True)` → Record outcome for `hoped_for`/`concerned_about`
- `find_stale_edges(days=90)` → Find edges not reviewed in N days

### Unit Tests

- **Test 1:** Create edge, query by source → Returns edge
- **Test 2:** Create chain (A → B → C), trace from C → Returns full chain
- **Test 3:** Supersede edge, query with status="active" → Old edge not returned
- **Test 4:** Create `hoped_for` edge, link outcome → Outcome retrievable
- **Test 5:** Bulk insert 10 edges → All inserted, queryable

---

## Phase 2: Extraction (B33 Block + Review Queue)

### Affected Files
- `Prompts/Blocks/Generate_B33.prompt.md` - CREATE - Edge extraction prompt
- `N5/review/edges/` - CREATE - Directory for review queue
- `N5/scripts/edge_extractor.py` - CREATE - Run extraction, output to queue
- `N5/scripts/edge_reviewer.py` - CREATE - Process queue, commit edges

### Changes

**2.1 B33 Prompt (`Generate_B33.prompt.md`):**

System prompt that extracts edges from transcript. Key sections:
- Input: Transcript + metadata + existing CRM people
- Output: JSONL of candidate edges
- Instructions: 
  - Identify ideas/decisions discussed
  - Track who originated vs supported vs challenged
  - Capture reasoning (hoped_for, concerned_about)
  - Note influence relationships
  - Generate stable slugs for ideas
  - Quote evidence from transcript

Output format (one JSON object per line):
```jsonl
{"source_type": "idea", "source_id": "context-graph-adoption", "source_display": "Adopting context graph architecture for N5", "relation": "originated_by", "target_type": "person", "target_id": "animesh-koratana", "evidence": "Animesh's article 'Context Graphs: AI's Trillion Dollar Opportunity' introduced this concept"}
{"source_type": "idea", "source_id": "context-graph-adoption", "relation": "supported_by", "target_type": "person", "target_id": "vrijen", "evidence": "V said 'This resonates with what I'm trying to build'"}
{"source_type": "idea", "source_id": "context-graph-adoption", "relation": "hoped_for", "target_type": "outcome", "target_id": "cognitive-mirror-capability", "target_display": "Ability to see patterns in my own thinking", "evidence": "V wants to track 'what originated from me vs what I adopted'"}
```

**2.2 Review Queue Structure:**

```
N5/review/edges/
├── pending/
│   └── 2026-01-04_mtg-animesh.jsonl     # Extracted, awaiting review
├── approved/
│   └── 2026-01-04_mtg-animesh.jsonl     # Reviewed, ready to commit
├── rejected/
│   └── (moved here if rejected)
└── committed/
    └── (moved here after commit to edges.db)
```

**2.3 Edge Extractor (`edge_extractor.py`):**

- Loads transcript and metadata
- Queries CRM for known people (to match names→slugs)
- Runs B33 prompt via LLM
- Parses JSONL output
- Checks for contradictions with existing edges (flags conflicts)
- Writes to `pending/` queue

**2.4 Edge Reviewer (`edge_reviewer.py`):**

- Lists pending files
- For each: display edges, ask for batch approval
- Move approved → `approved/`
- Call `edge_writer.bulk_add_edges()` on approved
- Move committed → `committed/`

### Unit Tests

- **Test 1:** Run extractor on sample transcript → JSONL generated in pending/
- **Test 2:** JSONL has valid schema (required fields present)
- **Test 3:** Approve and commit → Edges appear in `edges.db`
- **Test 4:** Conflict detection → Flags edge that contradicts existing

---

## Phase 3: Pipeline Integration

### Affected Files
- `N5/scripts/meeting_manifest_generator.py` - UPDATE - Add B33 to block list
- `N5/scripts/edge_extractor.py` - UPDATE - Integrate with meeting pipeline
- `Prompts/Meeting Intelligence Generator.prompt.md` - UPDATE - Include B33

### Changes

**3.1 Manifest Schema Update:**

Add B33 to blocks_selected in manifest.json:
```json
{
  "block_id": "B33",
  "block_name": "DECISION_EDGES",
  "priority": 2,
  "status": "pending",
  "category": "cognitive",
  "reason": "Extracts provenance and reasoning edges for context graph"
}
```

**3.2 Pipeline Position:**

B33 runs AFTER B08 (Stakeholder Intelligence) because:
- Needs CRM person slugs from B08 enrichment
- Runs before archive transition
- Generates to review queue (not inline in meeting folder)

**3.3 Contradiction Detection:**

When extracting, check:
```python
# For each candidate edge
existing = edge_query.find_edges(
    source_type=candidate['source_type'],
    source_id=candidate['source_id'],
    relation=candidate['relation'],
    status='active'
)
if existing and existing[0]['target_id'] != candidate['target_id']:
    candidate['conflict'] = True
    candidate['conflicts_with'] = existing[0]['id']
```

### Unit Tests

- **Test 1:** Process new meeting → B33 status appears in manifest
- **Test 2:** Edges appear in review queue after meeting processing
- **Test 3:** Conflicting edge is flagged in JSONL output

---

## Phase 4: Cognitive Mirror (LLM-Powered Insight Layer)

### Affected Files
- `N5/scripts/cognitive_mirror/` - CREATE directory
- `N5/insights/cognitive_mirror/` - CREATE output directory
- `N5/scripts/cognitive_mirror/decision_retrospective.py` - CREATE
- `N5/scripts/cognitive_mirror/reversal_detector.py` - CREATE
- `N5/scripts/cognitive_mirror/influence_map.py` - CREATE
- `N5/scripts/cognitive_mirror/originated_vs_adopted.py` - CREATE
- `N5/scripts/cognitive_mirror/decay_detector.py` - CREATE

### Design Principles

1. **LLM-powered, not regex** — Each script queries edges.db for raw data, then passes to LLM with a well-crafted prompt for semantic reasoning
2. **Archival outputs** — Each run produces a dated Markdown report in `N5/insights/cognitive_mirror/YYYY-MM-DD_<script-name>.md`
3. **Uses `/zo/ask` API** — Scripts call the Zo API for LLM reasoning, keeping prompts versioned in the script

### Changes

**4.1 Decision Retrospective (`decision_retrospective.py`):**

Purpose: "Did what I hoped for / feared actually happen?"

Process:
1. Query all `hoped_for` and `concerned_about` edges older than 90 days
2. Check which have linked outcomes vs. still open
3. Pass to LLM with prompt: "Given these predictions V made 90+ days ago, identify which need closure. For those with outcomes, assess accuracy. Surface patterns in prediction quality."

Output: Dated report with sections:
- Predictions needing closure (no outcome linked)
- Predictions validated (outcome matches hope/concern)
- Predictions invalidated (outcome contradicts)
- Pattern observations (e.g., "You're overly optimistic about timeline estimates")

```bash
python3 decision_retrospective.py --since 2025-10-01 --output N5/insights/cognitive_mirror/
```

**4.2 Reversal Detector (`reversal_detector.py`):**

Purpose: "Where am I inconsistent, and is that good or bad?"

Process:
1. Query all `superseded` and `reversed` edges
2. Group by semantic topic (LLM clusters similar ideas)
3. Pass to LLM with prompt: "Analyze these reversals. Which represent healthy evolution vs. indecision? Are there domains where V flip-flops repeatedly?"

Output: Dated report with sections:
- Healthy pivots (clear reasoning, new information)
- Concerning patterns (repeated back-and-forth)
- Domain analysis (where thinking is most/least stable)

```bash
python3 reversal_detector.py --output N5/insights/cognitive_mirror/
```

**4.3 Influence Map (`influence_map.py`):**

Purpose: "Who shapes my thinking, and in what domains?"

Process:
1. Query all `originated_by` and `influenced_by` edges with person targets
2. Join with meeting context to understand domains
3. Pass to LLM with prompt: "Map V's intellectual influences. Who originated ideas that stuck? Who challenges effectively? Are there echo chambers?"

Output: Dated report with sections:
- Top influencers by idea adoption rate
- Domain breakdown (who influences product vs. GTM vs. personal)
- Echo chamber risk assessment
- Underutilized perspectives

```bash
python3 influence_map.py --output N5/insights/cognitive_mirror/
```

**4.4 Originated vs Adopted (`originated_vs_adopted.py`):**

Purpose: "Do my ideas stick better than others'?"

Process:
1. Query ideas by originator (V vs. others)
2. Track lifecycle: active → superseded/reversed/validated
3. Pass to LLM with prompt: "Compare V's originated ideas vs. adopted ideas. Which have better outcomes? What does this say about ideation vs. curation strengths?"

Output: Dated report with sections:
- Originated idea survival rate
- Adopted idea survival rate
- Quality comparison by domain
- Strategic implications

```bash
python3 originated_vs_adopted.py --output N5/insights/cognitive_mirror/
```

**4.5 Decay Detector (`decay_detector.py`):**

Purpose: "What have I abandoned without deciding to?"

Process:
1. Query `active` edges not touched in 90+ days
2. Find commitments without follow-up edges
3. Pass to LLM with prompt: "These ideas/decisions appear abandoned but never explicitly closed. Which deserve revival? Which should be formally archived? What patterns exist in what V abandons?"

Output: Dated report with sections:
- Candidates for revival (still relevant)
- Candidates for formal closure (implicitly dead)
- Abandonment patterns (what types of ideas decay)
- Recommendations

```bash
python3 decay_detector.py --output N5/insights/cognitive_mirror/
```

### Shared Infrastructure

Each script will use a common pattern:
```python
# cognitive_mirror/_base.py
def query_edges(sql: str) -> list[dict]
def ask_zo(prompt: str, context: str) -> str
def write_report(script_name: str, content: str) -> Path
```

### Unit Tests

- **Test 1:** decision_retrospective on current 95 edges → produces coherent report
- **Test 2:** influence_map correctly identifies top 3 people by edge count
- **Test 3:** All scripts handle empty result sets gracefully
- **Test 4:** Reports are created with correct date format and location

---

## Phase 5: Backfill

### Affected Files
- `N5/scripts/edge_backfill.py` - CREATE

### Changes

**5.1 Backfill Script:**

- Scans `Personal/Meetings/Week-of-*` folders
- Skips meetings without transcripts
- Runs B33 extraction on each
- Outputs to review queue (batched by week)
- Provides progress: "Processing Week-of-2025-10-27... 4/12 meetings"

**5.2 Execution Plan:**

1. Run on Oct 2025 meetings first (small batch, recent memory)
2. V reviews and approves
3. Run on Nov 2025
4. Run on Dec 2025
5. Final review pass

### Unit Tests

- **Test 1:** Backfill 1 week → Queue populated correctly
- **Test 2:** Skip already-processed meetings (idempotent)

---

## Success Criteria

1. **Queryable:** Zo can answer "Where did this idea come from?" by tracing edges
2. **Integrated:** New meetings automatically generate edge candidates
3. **Lifecycle:** Edges can be superseded, reversed, linked to outcomes
4. **Insightful:** Monthly/quarterly analysis surfaces non-obvious patterns
5. **Backfilled:** Q4 2025 meetings have edges extracted and reviewed
6. **Maintainable:** V can review and approve edges in <5 min per meeting batch

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Edge extraction quality varies | Start with manual review; tune B33 prompt based on errors |
| Too many edges per meeting (noise) | B33 prompt emphasizes selectivity; review queue filters |
| Slug collisions (two ideas get same slug) | Include meeting date in slug; entity registry enforces uniqueness |
| Analysis outputs are unhelpful | Start with simple counts; iterate based on V's feedback |
| Backfill takes too long | Batch by week; parallelize extraction; async review |
| Schema changes needed later | SQLite migrations are simple; keep schema versioned |

---

## Estimated Effort

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1: Foundation | 2-3 hours | None |
| Phase 2: Extraction | 2-3 hours | Phase 1 |
| Phase 3: Integration | 1-2 hours | Phase 2 |
| Phase 4: Analysis | 2-3 hours | Phase 1 (can parallel with 2-3) |
| Phase 5: Backfill | 1 hour setup + V review time | Phase 2 |

**Total build time:** ~10 hours of Zo work + V review cycles

---

## Level Upper Review

### Counterintuitive Suggestions to Consider:

1. **Skip the review queue entirely?** Trust B33 extraction and commit directly, fix errors later. (Faster iteration, risk of noise)

2. **Start with backfill, not forward pipeline?** Historical data is richer; lets you tune B33 before live integration.

3. **Don't build analysis layer yet?** Get edges flowing first; analysis can come months later when there's enough data.

4. **Use existing B08 (Stakeholder Intelligence) instead of new B33?** B08 already captures people + context; extend it rather than new block.

### Architect's Response:

- **Review queue:** KEEP. V explicitly wants human-in-loop. Noise risk is real.
- **Backfill first:** CONSIDER. Could seed with 10-20 manual edges first to test query/lifecycle before extraction.
- **Delay analysis:** ACCEPT. Phase 4 can be deferred until Q2 when there's 3+ months of edges.
- **Extend B08:** REJECT. B08 is person-focused; B33 is idea/decision-focused. Different concerns.

---

## Handoff Notes

**For Builder:**
- Start with Phase 1
- Schema is the trap door — get V's sign-off on schema before creating DB
- `edge_query.py` output format matters — Zo will parse it
- Test with manual edges before building extraction

**For V:**
- Review queue will need your attention ~weekly during initial rollout
- Analysis outputs are hypotheses — tell me which are useful
- Backfill is optional but valuable; schedule time for review batches






