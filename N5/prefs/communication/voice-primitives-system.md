---
created: 2026-01-11
last_edited: 2026-01-12
version: 1.0
provenance: n5os-ode-export
type: system_spec
status: active
---
# Voice Primitives System (Spec)

## Purpose

Provide your AI writing persona with a curated, expandable repository of reusable voice primitives sourced from your own content (transcripts, social posts, emails), optimized for **your unique writing voice**.

---

## Canonical Locations

- **Database (source of truth):**
  - `N5/data/voice_library.db`

- **Retrieval script:**
  - `N5/scripts/retrieve_primitives.py`

- **Candidate review batches (HITL):**
  - `N5/review/voice/`

- **Build artifacts:**
  - `N5/builds/voice-library/`

---

## Source Policy

**Primary sources:**
1. Social media corpus (posts, comments with commentary) — bulk seeding
2. Meeting transcripts via block extraction — ongoing accumulation

**Source tracking:**
- Each primitive has a `source` field: `social`, `meeting`, `manual`
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
python3 N5/scripts/retrieve_primitives.py --topic "[your topic]" --count 5

# Python
from N5.scripts.retrieve_primitives import get_connection, get_primitives, mark_as_used

conn = get_connection()
primitives = get_primitives(conn, count=5, topic="[your topic]", min_distinctiveness=0.6)
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

**Distribution guidance:**
- High (≥0.9): Your most unique phrases and framings
- Medium (0.6-0.9): Distinctive but more general
- Low (<0.6): Filter out during import — too generic to be useful

**Note:** Socially-seeded primitives may have synthetic scores based on LLM ranking. Meeting-sourced primitives can be scored with detection tools for ground truth.

---

## Integration Points

### 1. Writer Persona Generation
- Retrieve 5-10 relevant primitives before drafting
- Primitives available as context during voice transformation

### 2. AI-Detection Post-Check
- Run detection tools on generated draft
- If AI-fraction is too high: retrieve high-distinctiveness primitives
- Inject into AI-heavy windows and regenerate

### 3. Meeting Intelligence Pipeline
- Extract voice primitives from meeting transcripts
- Flag explicit capture signals ("I'm stealing that")

---

## Database Schema

```sql
CREATE TABLE primitives (
  id TEXT PRIMARY KEY,                          -- e.g., VL-0001
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

## Getting Started

To build your own voice library:

1. **Seed from existing content** — Export your social posts, emails, or transcripts
2. **Extract primitives** — Use LLM to identify distinctive phrases, metaphors, patterns
3. **Score distinctiveness** — Rate each primitive 0.0-1.0
4. **Review and approve** — Human-in-the-loop review of candidates
5. **Integrate with writing** — Use retrieval script to inject into drafts

---

## Related Files

- **Retrieval:** `N5/scripts/retrieve_primitives.py`
- **Extraction:** `N5/scripts/extract_voice_primitives.py`
- **Style Guide:** `N5/prefs/communication/style-guide.md`
