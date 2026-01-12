---
created: 2026-01-11
last_edited: 2026-01-12
version: 1.0
provenance: con_TBnwuolXxSkp5t1D
type: system_spec
status: active
---
# Voice Primitives System (Spec)

## Purpose

Provide Vibe Writer with a curated, expandable repository of reusable voice primitives sourced primarily from transcripts and LinkedIn corpus, optimized for **V's writing voice**.

---

## Canonical Locations

- **Database (source of truth):**
  - `N5/data/voice_library.db`
  
- **Retrieval script:**
  - `N5/scripts/retrieve_primitives.py`

- **Candidate review batches (HITL):**
  - `N5/review/voice/`

- **Build artifacts:**
  - `N5/builds/voice-library-v2/`

---

## Source Policy

**Primary sources:**
1. LinkedIn corpus (comments, posts with commentary) — bulk seeding
2. Meeting transcripts via B35 block extraction — ongoing accumulation

**Source tracking:**
- Each primitive has a `source` field: `linkedin`, `meeting`, `manual`
- Sources table links primitives to specific files

---

## Retrieval Contract

### Default Parameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Count | 5-10 primitives | Per 1,000-2,000 word piece |
| Min distinctiveness | ≥ 0.6 | Only distinctive primitives |
| Throttle window | 24 hours | Same primitive can't repeat too soon |
| Max same domain | 3 | Diversity enforcement |

### Usage
```bash
# CLI
python3 N5/scripts/retrieve_primitives.py --topic "hiring" --count 5

# Python
from N5.scripts.retrieve_primitives import get_connection, get_primitives, mark_as_used

conn = get_connection()
primitives = get_primitives(conn, count=5, topic="hiring", min_distinctiveness=0.6)
mark_as_used(conn, [p["id"] for p in primitives])
conn.close()
```

### Primitive Types
| Type | Usage Guidance |
|------|----------------|
| `signature_phrase` | Use verbatim or near-verbatim |
| `metaphor` | Adapt to context; preserve core comparison |
| `analogy` | Adapt to context; preserve structural relationship |
| `syntactic_pattern` | Mirror structure with new content |
| `conceptual_frame` | Adopt the framing lens |
| `rhetorical_device` | Apply the technique |

### Injection Guidelines
- **1-3 primitives per 500 words** (don't over-inject)
- Primitives are *raw material*, not mandatory inclusions
- Signature phrases can drop in verbatim
- Metaphors/analogies should be adapted to fit context
- Never force a primitive if it doesn't fit

---

## Throttle Logic

**Goal:** Prevent overuse of distinctive phrases.

**Implementation:**
- `last_used_at` timestamp updated on each retrieval
- `use_count` increments on each retrieval
- Retrieval excludes primitives used within `THROTTLE_HOURS` (default: 24)

**Override:** Use `--no-throttle` flag when you explicitly want to reuse.

---

## Distinctiveness Scoring

**Score range:** 0.0 (generic/AI-like) to 1.0 (distinctive/human-like)

**Distribution (current library):**
- High (≥0.9): 139 primitives
- Medium (0.6-0.9): 280 primitives
- Low (<0.6): 0 primitives (filtered out during import)

**Note:** LinkedIn-seeded primitives have synthetic scores based on LLM ranking. Future meeting-sourced primitives can be scored with Pangram for ground truth.

---

## Integration Points

### 1. Vibe Writer Generation
- Step 2.5 in `Prompts/Generate With Voice.prompt.md`
- Retrieves 5-10 relevant primitives before drafting
- Primitives available as context during voice transformation

### 2. Pangram Post-Check (Phase 3.4)
- Run Pangram on generated draft
- If `fraction_ai > 0.5`: retrieve high-distinctiveness primitives
- Inject into AI-heavy windows and regenerate

### 3. Meeting Intelligence Pipeline
- B35 block (`Prompts/Blocks/Generate_B35.prompt.md`)
- Extracts voice primitives from meeting transcripts
- Flags explicit capture signals ("I'm stealing that")

---

## Database Schema

```sql
CREATE TABLE primitives (
  id TEXT PRIMARY KEY,                          -- e.g., VL-LI-0001
  exact_text TEXT NOT NULL,                     -- The actual phrase
  primitive_type TEXT NOT NULL,                 -- phrase|analogy|metaphor|etc
  distinctiveness_score REAL DEFAULT NULL,      -- 0.0-1.0
  novelty_flagged INTEGER DEFAULT 0,            -- 1 if capture signal
  domains_json TEXT DEFAULT '[]',               -- JSON array of domain tags
  use_count INTEGER DEFAULT 0,                  -- Times used in generation
  last_used_at TEXT DEFAULT NULL,               -- ISO timestamp
  status TEXT DEFAULT 'candidate',              -- candidate|approved|rejected
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  notes TEXT DEFAULT NULL
);

CREATE TABLE sources (
  id TEXT PRIMARY KEY,
  primitive_id TEXT NOT NULL,
  source_path TEXT NOT NULL,
  source_type TEXT DEFAULT 'transcript',
  -- ... additional tracking fields
);
```

---

## Current State

| Metric | Value |
|--------|-------|
| Total approved primitives | 419 |
| Primary source | LinkedIn corpus |
| Top domains | career (166), tech (114), communication (103), recruiting (93) |
| Retrieval script | Active |
| Vibe Writer integration | Active |
| Pangram post-check | Not yet implemented |

---

## Related Files

- **Plan:** `N5/builds/voice-library-v2/PLAN.md`
- **Status:** `N5/builds/voice-library-v2/STATUS.md`
- **Retrieval:** `N5/scripts/retrieve_primitives.py`
- **Extraction:** `N5/scripts/extract_voice_primitives.py`
- **B35 Block:** `Prompts/Blocks/Generate_B35.prompt.md`

