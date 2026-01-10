---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
type: build_plan
status: draft
---

# Plan: Resonance System V2

**Objective:** Enhance the Context Graph with five new analysis capabilities: velocity tracking, cross-pollination detection, challenge resolution tracking, idea genealogy, and external validation signals.

**Trigger:** V requested enhancements after reviewing the initial Resonance Report. Priority order: Velocity > Cross-Pollination > Challenge Resolution > Genealogy > External Validation (elevated due to high-signal alignment tracking).

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [x] What's the current data model? → edges.db has entities (189 ideas, 19 people) and edges with relations (originated_by, supported_by, challenged_by, etc.)
- [x] Decay threshold? → Updated to 14 days per V's feedback
- [ ] Should velocity be stored in edges.db or computed on-the-fly? → Recommend: computed, with caching in resonance_index.json
- [ ] For external validation, do we have person credibility scores? → Check CRM for signal quality indicators

---

## Checklist

### Phase 1: Velocity Tracking
- ☐ Add `compute_velocity()` function to pattern_surfacer.py
- ☐ Create weekly mention counts table in resonance_index.json
- ☐ Add velocity metrics to report output
- ☐ Test: Verify acceleration detection on known rising ideas

### Phase 2: Cross-Pollination Detection
- ☐ Add `detect_co_occurrence()` function to pattern_surfacer.py
- ☐ Create co-occurrence matrix for ideas sharing meetings
- ☐ Add "converging ideas" section to report
- ☐ Test: Verify detection of ideas that started separate but now co-occur

### Phase 3: Challenge Resolution Tracking
- ☐ Query edges.db for `challenged_by` edges and their outcomes
- ☐ Add resolution status tracking (pending/resolved/abandoned)
- ☐ Add "under challenge" section with resolution status to report
- ☐ Test: Verify challenge lifecycle visibility

### Phase 4: Idea Genealogy
- ☐ Add `derives_from` relation to edge_types if missing
- ☐ Create `build_genealogy_tree()` function
- ☐ Add ancestry/descendant queries to evolution_tracker.py
- ☐ Test: Verify parent→child idea chains are surfaced

### Phase 5: External Validation Signal
- ☐ Query edges.db for `supported_by` edges where source is external person
- ☐ Join with CRM to get person credibility/influence indicators
- ☐ Weight validations by source credibility
- ☐ Add "external validators" section showing high-signal alignment
- ☐ Test: Verify credibility-weighted validation scores

---

## Phase 0: Schema Versioning (Pre-requisite)

### Affected Files
- `N5/data/resonance_index.json` - UPDATE - add schema_version field
- `N5/scripts/resonance/pattern_surfacer.py` - UPDATE - add version check on load

### Changes

**0.1 Add Schema Version:**
Add `schema_version: "2.0"` to resonance_index.json root. Old format (no version) treated as 1.0.

**0.2 Version Check on Load:**
```python
def load_resonance_index() -> dict:
    """Load index with version migration if needed"""
    data = json.load(...)
    version = data.get('schema_version', '1.0')
    if version == '1.0':
        # Migrate: add empty structures for new features
        data['schema_version'] = '2.0'
        data['velocity'] = {}
        data['co_occurrence'] = {}
        data['external_validations'] = {}
    return data
```

### Unit Tests
- Load old-format index: should auto-migrate to 2.0
- Load new-format index: should preserve existing data

---

## Phase 1: Velocity Tracking

### Affected Files
- `N5/scripts/resonance/pattern_surfacer.py` - UPDATE - add velocity computation
- `N5/data/resonance_index.json` - UPDATE - add weekly_mentions structure

### Changes

**1.1 Weekly Mention Aggregation:**
Add function to group idea mentions by ISO week:
```python
def compute_weekly_mentions(idea_id: str, weeks_back: int = 8) -> list[int]:
    """Returns list of mention counts for last N weeks, oldest first.
    Example: [0, 1, 2, 3, 5, 4, 6, 8] = 8 weeks of counts
    """
```

**1.2 Trend Detection (Simplified):**
Simple week-over-week comparison, no slope math:
```python
def compute_velocity(idea_id: str) -> dict:
    """Returns {
        'weekly_counts': [int, ...],  # last 8 weeks
        'current_week': int,
        'prev_week': int,
        'trend': 'rising' | 'stable' | 'falling'
    }
    
    Trend rules:
    - 'rising': current_week > prev_week
    - 'falling': current_week < prev_week  
    - 'stable': current_week == prev_week
    """
```

**1.3 Report Integration:**
Update `report` command to show "Rising Ideas" section:
- Ideas where trend == 'rising' AND current_week >= 2

### Unit Tests
- Create test fixtures with known weekly patterns
- Idea with [1, 2, 3, 4] counts → trend = 'rising'
- Idea with [4, 3, 2, 1] counts → trend = 'falling'
- Idea with [2, 2, 2, 2] counts → trend = 'stable'

---

## Phase 2: Cross-Pollination Detection

### Affected Files
- `N5/scripts/resonance/pattern_surfacer.py` - UPDATE - add co-occurrence detection
- `N5/data/resonance_index.json` - UPDATE - add co_occurrence structure

### Changes

**2.1 Co-occurrence Matrix:**
Build matrix of idea pairs that appear in same meetings:
```python
def build_co_occurrence_matrix(min_shared_meetings: int = 2) -> dict:
    """Returns {(idea_a, idea_b): {
        'shared_meetings': [meeting_ids],
        'first_co_occurrence': date,
        'recent_co_occurrence': date
    }}"""
```

**2.2 Convergence Detection:**
Identify idea pairs that were separate (no co-occurrence) in first 4 weeks but now co-occur:
```python
def detect_convergence() -> list:
    """Returns list of newly converging idea pairs"""
```

**2.3 Report Integration:**
Add "Converging Ideas" section showing pairs that are starting to appear together.

### Unit Tests
- Create test meeting referencing two previously separate ideas, run detection
- Verify convergence section appears in report with the new pair

---

## Phase 3: Challenge Resolution Tracking

### Affected Files
- `N5/scripts/resonance/evolution_tracker.py` - UPDATE - add challenge lifecycle queries
- `N5/scripts/resonance/pattern_surfacer.py` - UPDATE - include challenge status in report

### Changes

**3.1 Challenge Status Query:**
```python
def get_challenge_status(idea_id: str) -> list:
    """Returns list of {
        'challenger': person_id,
        'challenger_name': str,
        'challenged_at': date,
        'meeting_id': str,
        'evidence': str,  # the challenge quote
        'status': 'pending' | 'resolved' | 'abandoned',
        'resolution': str | None  # how it was resolved
    }"""
```

**3.2 Resolution Detection:**
A challenge is "resolved" if a subsequent edge shows:
- V `supported_by` the challenger on the same idea (they came around)
- The idea has `superseded_by` status (V abandoned it)
- An explicit resolution edge exists

**3.3 Report Integration:**
Enhance "Under Challenge" section to show:
- Challenger identity
- Days since challenge
- Resolution status

### Unit Tests
- Query `moneyball-for-hiring` challenge: should show challenger and pending status
- Create test resolution edge, verify status updates

---

## Phase 4: Idea Genealogy

### Affected Files
- `N5/scripts/resonance/evolution_tracker.py` - UPDATE - add genealogy functions
- `N5/data/edges.db` - UPDATE - add `derives_from` edge type if missing

### Changes

**4.1 Edge Type Setup:**
```sql
INSERT OR IGNORE INTO edge_types (relation, category, description, inverse_relation)
VALUES ('derives_from', 'chain', 'This idea evolved from or builds upon another idea', 'spawned');
```

**4.2 Genealogy Tree Builder:**
```python
def build_genealogy(idea_id: str) -> dict:
    """Returns {
        'ancestors': [list of parent ideas, oldest first],
        'descendants': [list of child ideas],
        'siblings': [ideas sharing same parent]
    }"""
```

**4.3 Report Integration:**
For ideas with genealogy, show lineage in report:
- "Evolved from: {parent_idea}"
- "Spawned: {child_ideas}"

### Unit Tests
- Create test idea with `derives_from` edge to existing idea
- Verify genealogy tree shows correct ancestry

---

## Phase 5: External Validation Signal

### Affected Files
- `N5/scripts/resonance/pattern_surfacer.py` - UPDATE - add external validation scoring
- `N5/scripts/resonance/evolution_tracker.py` - UPDATE - add credibility weighting
- `N5/data/resonance_index.json` - UPDATE - add external_validations structure

### Changes

**5.1 External Supporter Query:**
```python
def get_external_validations(idea_id: str) -> list:
    """Returns list of {
        'person_id': str,
        'person_name': str,
        'meeting_id': str,
        'validated_at': date,
        'evidence': str,  # quote of support
        'credibility_score': float  # from CRM if available
    }"""
```

**5.2 Credibility Integration:**
Join with CRM (people.db or markdown profiles) to get:
- Role/title (founder, investor, executive = higher weight)
- Relationship strength
- Domain expertise match

```python
def compute_credibility_score(person_id: str, idea_domain: str) -> float:
    """Returns 0.0-1.0 credibility score based on person's relevance to idea domain"""
```

**5.3 Weighted Validation Score:**
```python
def compute_validation_strength(idea_id: str) -> dict:
    """Returns {
        'total_validations': int,
        'weighted_score': float,  # sum of credibility-weighted validations
        'top_validators': [top 3 by credibility],
        'signal_quality': 'high' | 'medium' | 'low'
    }"""
```

**5.4 Report Integration:**
Add "External Validation" section:
- Ideas with high-credibility external support
- Who validated and their relevance

### Unit Tests
- Query idea with known `supported_by` edges from external people
- Verify credibility weighting applies correctly
- Test with person who has CRM profile vs. one without

---

## Success Criteria

1. `python3 pattern_surfacer.py report` shows all five new sections (Velocity, Convergence, Challenge Status, Genealogy, External Validation)
2. Velocity correctly identifies accelerating vs. decaying ideas over week-over-week comparison
3. Cross-pollination detects at least one converging idea pair from existing data
4. Challenge resolution shows `moneyball-for-hiring` with accurate challenger and status
5. External validation weights by credibility, surfacing high-signal validators

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| CRM data sparse for credibility scoring | Fallback to equal weighting; log missing credibility for later enrichment |
| Performance with large idea set | Cache velocity/co-occurrence in resonance_index.json; compute incrementally |
| Genealogy edges don't exist yet | Phase 4 creates the edge type; genealogy builds over time as V makes connections |
| Challenge resolution ambiguous | Default to 'pending' unless explicit resolution evidence exists |

---

## Alternatives Considered (Nemawashi)

### Alternative 1: Store all metrics in edges.db
**Rejected:** Would complect the edge graph with computed metrics. Better to keep edges.db as source of truth and resonance_index.json as derived analytics.

### Alternative 2: Real-time computation only (no caching)
**Rejected:** Too slow for report generation. Caching in resonance_index.json with daily refresh is the right balance.

### Alternative 3: Build as separate microservice
**Rejected:** Overengineering. These are analytical queries on existing data; Python scripts with JSON caching is appropriate.

---

## Trap Doors Identified

1. **Edge type additions** (Phase 4 `derives_from`): Adding new edge types is low-risk and reversible.
2. **Schema changes**: None required—all features use existing edges.db schema.
3. **CRM integration** (Phase 5): Read-only queries; no risk to CRM data.

**Verdict:** No irreversible decisions. All phases can be built incrementally and rolled back if needed.

---

## Level Upper Review

### Counterintuitive Suggestions Received:

**1. Opposite approach — Single synthetic "Resonance Score":**
Instead of five metrics, combine into one score per idea. Like a credit score for intellectual momentum.
→ **Rejected**: V explicitly wants visibility into separate signals (velocity, cross-pollination, validation). A synthetic score hides what he's trying to understand. Candidate for v3.

**2. Scale risk — O(n²) co-occurrence at 10x ideas:**
At 1,890 ideas, co-occurrence matrix = 3.5M comparisons. Genealogy traversal also expensive.
→ **Incorporated**: Add incremental computation note to Phase 2. Consider computing on meeting-process, not report-generate.

**3. Laziest solution for Velocity:**
Skip acceleration math. Weekly counts + simple trend indicator sufficient for v1.
→ **Incorporated**: Simplify Phase 1. Weekly sparkline + 'rising'/'stable'/'falling' based on week-over-week comparison. No slopes.

**4. Laziest solution for External Validation:**
Skip credibility scoring. Just list validators by name/date. V knows who matters.
→ **Incorporated**: Phase 5 v1 = list validators only. Credibility weighting deferred to v2.

**5. Senior engineer criticism — No migration plan:**
What happens to existing resonance_index.json?
→ **Incorporated**: Add schema_version field. Graceful deprecation of old format.

**6. Senior engineer criticism — Hand-wavy tests:**
"Query known idea" isn't a real test. Need synthetic fixtures.
→ **Noted**: Builder should create test fixtures in Phase 1 before proceeding.

**7. Assumption challenge — Ideas may not be discrete:**
Many "ideas" are facets of same concept. Genealogy helps but may need clustering.
→ **Incorporated**: Add "potential duplicate" warning when genealogy + co-occurrence suggest overlap.

**8. Assumption challenge — External validation can be negative:**
Someone supporting an idea V is moving away from = anchor, not validation.
→ **Deferred**: v1 treats all supported_by as positive. Track "anchor" pattern for v2.

### Incorporated into Plan:
- Phase 0 added: Schema versioning for resonance_index.json
- Phase 1 simplified: No acceleration math, just weekly counts + trend
- Phase 2 note: Incremental computation on meeting-process
- Phase 4 addition: Potential duplicate warning
- Phase 5 simplified: Validator list only, credibility scoring deferred

### Rejected (with rationale):
- Single Resonance Score: V wants signal visibility, not synthesis (v3 candidate)
- Negative validation tracking: Interesting but adds complexity before v1 validates basic approach



