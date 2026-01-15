---
created: 2026-01-13
last_edited: 2026-01-14
version: 1.1
provenance: con_WDVrJL9R2FhuBypw
type: design_spec
status: proposed
---

# Voice Library Categorization Spec

**Author:** Architect (Worker from Learning Profile System build)  
**Objective:** Design a categorization schema for V's Voice Library that supports scalable phrase capture from conversation-end hooks.

---

## Executive Summary

This spec proposes a **function-based categorization** system derived from V's actual linguistic patterns. Categories emerge from *how phrases function in discourse* rather than abstract taxonomies. The schema integrates with the existing `voice_library.db` infrastructure and supports automated capture via conversation-close hooks.

---

## Analysis: What Emerged from the Data

### Source Material Examined

| Source | Records | Key Observations |
|--------|---------|------------------|
| `paragraph-chunks.jsonl` | 150 | 5 post types, position tracking (opening/closing) |
| `voice-primitives-system.md` | 419 approved | 6 primitive types, 4 domains |
| Existing transformation system | — | Platform-aware, transformation pairs approach |

### Distinctive Patterns Observed in V's Voice

From corpus analysis, V's most distinctive linguistic moves:

1. **Contrarian Reframes** — "This just in: Anthropic is telling job applicants not to use AI... Let me play that back..."
2. **Devastating Analogies** — "swapping keywords like an overpaid thesaurus"
3. **System Indictments** — "resumes are fundamentally terrible. They're one-dimensional representations..."
4. **Rally Cries** — "So until we overthrow the yoke of resume tyranny altogether..."
5. **Pattern Interrupts** — Action-asterisk openings: "*Pastes in a job description*"
6. **Warm Authority Pivots** — "I can attest to the immense quality..." + specific evidence
7. **Em-Dash Pivots** — Sharp turns mid-sentence with tonal shift

---

## Proposed Category Schema

### Design Principle: Function Over Form

Categories answer: **"What job does this phrase do in V's discourse?"**

Not: "What part of speech is this?" or "What topic does it cover?"

### Primary Categories (Mutually Exclusive)

| Category ID | Name | Function | Example |
|-------------|------|----------|---------|
| `OPEN` | **Openers** | Hooks attention, establishes frame | "A dozen Future of Work founders walk into a Zoom room…" |
| `PIVOT` | **Pivots** | Shifts direction, creates tension | "Here's the thing —" / "But let me be blunt:" |
| `FRAME` | **Frames** | Recontextualizes, names patterns | "The ChatGPT Resume Clone Army" |
| `STRIKE` | **Strikes** | Devastating precision; quotable truths | "one-dimensional representations of complex, nuanced careers" |
| `RALLY` | **Rallies** | Calls to action, invokes shared mission | "overthrow the yoke of resume tyranny" |
| `CLOSE` | **Closers** | Lands the point, exits with resonance | "It's as simple as that." |
| `BRIDGE` | **Bridges** | Transitions, connects ideas | "That's why..." / "Which brings me to..." |

### Secondary Tags (Non-Exclusive, Additive)

Applied as `tags_json` array alongside primary category:

| Tag | Meaning | Retrieval Use |
|-----|---------|---------------|
| `analogy` | Contains A→B comparison | Inject when explaining complex concepts |
| `metaphor` | Figurative language | Add color to dry content |
| `contrarian` | Challenges conventional wisdom | Thought leadership, hot takes |
| `warm` | Demonstrates care/connection | Relationship-building comms |
| `technical` | Domain-specific precision | B2B, expert audiences |
| `humor` | Wit, wordplay, irony | X posts, casual contexts |
| `self-aware` | Meta-commentary, self-deprecation | Authenticity signals |

### Domain Tags (Existing, Preserved)

Retain current domain taxonomy for topical retrieval:
- `career`, `tech`, `communication`, `recruiting`, `hiring`, `ai`, `consulting`

---

## Integration with Existing System

### Database Schema Extension

```sql
-- Add to existing primitives table
ALTER TABLE primitives ADD COLUMN category TEXT DEFAULT NULL;
-- Values: OPEN, PIVOT, FRAME, STRIKE, RALLY, CLOSE, BRIDGE

ALTER TABLE primitives ADD COLUMN tags_json TEXT DEFAULT '[]';
-- JSON array: ["analogy", "contrarian", "warm"]

-- Preserve existing columns:
-- primitive_type (signature_phrase, metaphor, analogy, syntactic_pattern, conceptual_frame, rhetorical_device)
-- domains_json (career, tech, etc.)
```

### Migration Path

1. **Existing 419 primitives:** Run bulk classification via LLM prompt
2. **New captures:** Classify at ingestion time via B35 or conversation-close hook
3. **Backward compatible:** Old queries still work; new queries can filter by category

### Retrieval Contract Extension

```python
# Extended retrieval signature
def get_primitives(
    conn,
    count: int = 5,
    topic: str = None,           # Existing: domain match
    category: str = None,        # NEW: OPEN, PIVOT, etc.
    tags: list[str] = None,      # NEW: ["analogy", "contrarian"]
    min_distinctiveness: float = 0.6,
    exclude_ids: list[str] = None
) -> list[dict]:
    ...
```

### Use Cases by Category

| Generation Context | Primary Category | Tags |
|-------------------|------------------|------|
| LinkedIn opening | `OPEN` | — |
| Email pivot to ask | `PIVOT` | `warm` |
| X hot take | `STRIKE` | `contrarian`, `humor` |
| Follow-up close | `CLOSE` | `warm` |
| Explaining AI to non-tech | `FRAME` | `analogy` |
| CTA in marketing copy | `RALLY` | — |

---

## File Structure Recommendation

### Current State (Preserve)

```
Knowledge/voice-library/
├── README.md
├── voice-primitives.md
├── corpus-analysis-report.md
├── paragraph-chunks.jsonl
└── primitives/                  # Empty, unused
```

### Proposed Structure (Extend)

```
Knowledge/voice-library/
├── README.md                    # Update with new schema
├── voice-primitives.md          # Preserve
├── corpus-analysis-report.md    # Preserve
├── paragraph-chunks.jsonl       # Preserve (source corpus)
│
├── by-category/                 # NEW: Human-readable exports
│   ├── openers.md
│   ├── pivots.md
│   ├── frames.md
│   ├── strikes.md
│   ├── rallies.md
│   ├── closers.md
│   └── bridges.md
│
└── capture-log.jsonl            # NEW: Raw captures before HITL
```

**Note:** `by-category/` files are **read-only exports** from `voice_library.db`. Database remains source of truth.

---

## Capture Format for Conversation-Close Hook

### Input: Raw Capture Signal

When conversation-close detects a distinctive phrase:

```json
{
  "text": "The ChatGPT Resume Clone Army",
  "source_type": "conversation",
  "source_id": "con_WDVrJL9R2FhuBypw",
  "context_before": "...you've unwittingly enlisted yourself in",
  "context_after": "- and martyred your job prospects",
  "capture_signal": "distinctive_framing",
  "timestamp": "2026-01-13T21:30:00Z"
}
```

### Processing Pipeline

1. **Capture** → Write to `capture-log.jsonl` (unclassified)
2. **Auto-classify** → LLM assigns `category` + `tags` + `distinctiveness_score`
3. **HITL gate** → If `distinctiveness_score >= 0.8`, auto-approve; else queue for review
4. **Ingest** → Insert to `voice_library.db` with status `approved` or `candidate`

### Classification Prompt Template

```
Classify this phrase for V's voice library:

TEXT: "{text}"
CONTEXT: {context_before} [TEXT] {context_after}

1. PRIMARY CATEGORY (exactly one):
   OPEN (hooks attention), PIVOT (shifts direction), FRAME (recontextualizes),
   STRIKE (quotable truth), RALLY (call to action), CLOSE (lands point), BRIDGE (transitions)

2. TAGS (zero or more):
   analogy, metaphor, contrarian, warm, technical, humor, self-aware

3. DOMAINS (zero or more):
   career, tech, communication, recruiting, hiring, ai, consulting

4. DISTINCTIVENESS (0.0-1.0):
   How unique to V vs. generic/anyone could say this?

Output JSON:
{"category": "...", "tags": [...], "domains": [...], "distinctiveness": 0.X}
```

---

## Quality Gates

### Auto-Approve Threshold

| Condition | Action |
|-----------|--------|
| `distinctiveness >= 0.8` | Auto-approve to `voice_library.db` |
| `0.6 <= distinctiveness < 0.8` | Queue to `N5/review/voice/` for HITL |
| `distinctiveness < 0.6` | Reject (too generic) |

### Deduplication

Before insert, check:
```sql
SELECT id FROM primitives 
WHERE exact_text = ? 
   OR similarity(exact_text, ?) > 0.9;
```

If match found: skip or merge (update `use_count`, don't duplicate).

---

## Implementation Phases

### Phase 1: Schema + Migration (This Spec)
- Add `category`, `tags_json` columns
- Bulk-classify existing 419 primitives
- Update `retrieve_primitives.py` with new filters

### Phase 2: Conversation-Close Integration
- Hook into Close Conversation workflow
- Write captures to `capture-log.jsonl`
- Auto-classify with LLM

### Phase 3: HITL Review Flow
- Generate review batches from candidates
- Integrate with existing `N5/review/voice/` workflow

### Phase 4: Smart Retrieval
- Context-aware primitive selection during generation
- Category matching based on generation position (opening → `OPEN`, closing → `CLOSE`)

---

## Decisions (Resolved)

1. **Category granularity:** ✅ 7 categories confirmed sufficient. Validated that any formal structure (question, statement) can serve any function — categories are functional, not formal.

2. **Auto-approve threshold:** ✅ 0.8 distinctiveness confirmed for auto-approve.

3. **Source priority:** ✅ Conversation captures weighted **lower** than LinkedIn corpus:
   - LinkedIn corpus primitives: `source_weight = 1.0` (proven in public, polished)
   - Conversation captures: `source_weight = 0.75` (raw, context-dependent)

4. **Decay policy:** ✅ Implement decay for unused primitives (see below)

---

## Decay Policy Design

### Rationale

Primitives that are repeatedly retrieved but never selected for generation are likely poor fits. Decay prevents stale/weak primitives from cluttering retrieval results.

### Tracking Fields

```sql
ALTER TABLE primitives ADD COLUMN retrieval_count INTEGER DEFAULT 0;
ALTER TABLE primitives ADD COLUMN selection_count INTEGER DEFAULT 0;
ALTER TABLE primitives ADD COLUMN last_retrieved_at TEXT DEFAULT NULL;
ALTER TABLE primitives ADD COLUMN last_selected_at TEXT DEFAULT NULL;
```

### Decay Formula

```python
def effective_score(primitive: dict) -> float:
    base = primitive['distinctiveness']
    source_weight = 1.0 if primitive['source_type'] == 'linkedin' else 0.75
    
    # Decay based on retrieval-without-selection ratio
    retrievals = primitive.get('retrieval_count', 0)
    selections = primitive.get('selection_count', 0)
    
    if retrievals == 0:
        decay_factor = 1.0  # New primitive, no penalty
    elif selections == 0 and retrievals >= 5:
        decay_factor = 0.5  # Retrieved 5+ times, never selected → heavy penalty
    else:
        # Ratio-based decay: selection_rate approaching 0 → decay approaching 0.5
        selection_rate = selections / retrievals
        decay_factor = 0.5 + (0.5 * selection_rate)  # Range: 0.5 to 1.0
    
    return base * source_weight * decay_factor
```

### Decay Thresholds

| Condition | Decay Factor | Meaning |
|-----------|--------------|----------|
| New (0 retrievals) | 1.0 | Full weight |
| High selection rate (>50%) | 0.75–1.0 | Healthy |
| Low selection rate (10-50%) | 0.55–0.75 | Declining |
| Very low selection rate (<10%) | 0.5–0.55 | At risk |
| Never selected after 5+ retrievals | 0.5 | Minimum floor |

### Resurrection Path

If a decayed primitive is manually selected (via HITL or direct use), reset:
```python
if manually_selected:
    primitive['selection_count'] += 1
    primitive['last_selected_at'] = now()
    # Decay factor recalculates on next retrieval
```

### Archival Policy

Primitives with `effective_score < 0.3` after 20+ retrievals → move to `status = 'archived'` (excluded from retrieval, preserved for audit).

---

## Related Files

| Purpose | Location |
|---------|----------|
| Existing primitives system | `file 'N5/prefs/communication/voice-primitives-system.md'` |
| Voice transformation system | `file 'N5/prefs/communication/voice-transformation-system.md'` |
| Retrieval script | `file 'N5/scripts/retrieve_primitives.py'` |
| Review queue | `file 'N5/review/voice/'` |
| Parent build plan | `file 'N5/builds/learning-profile-system/PLAN.md'` |


