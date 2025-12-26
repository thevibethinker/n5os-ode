---
created: 2025-12-06
last_edited: 2025-12-06
version: 1
worker_id: positions-core
depends_on: 
---
# Worker Assignment: Positions Core System

## Mission

Build the core positions system: SQLite database + CLI + semantic search via OpenAI embeddings.

## Context

V wants a knowledge-tier system for storing compound insights/beliefs/worldview positions. This is the foundational layer that Type B conversation-end will call.

**Full spec:** `/home/.z/workspaces/con_0CASX5AGlViD01uu/positions-system-spec-v2.md`

## Deliverables

### 1. Database (`N5/data/positions.db`)

```sql
CREATE TABLE positions (
    id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    title TEXT NOT NULL,
    insight TEXT NOT NULL,
    components TEXT,                        -- JSON array
    evidence TEXT,                          -- JSON array
    connections TEXT,                       -- JSON array: [{target_id, relationship}]
    stability TEXT DEFAULT 'emerging',      -- emerging | stable | canonical
    confidence INTEGER DEFAULT 3,
    formed_date TEXT,
    last_refined TEXT,
    source_conversations TEXT,              -- JSON array
    supersedes TEXT,                        -- JSON array
    embedding BLOB,                         -- 1536-dim float32
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_domain ON positions(domain);
CREATE INDEX idx_stability ON positions(stability);
```

### 2. Script (`N5/scripts/positions.py`)

**Required functions:**
- `embed(text: str) -> bytes` — OpenAI API call
- `cosine_similarity(a: bytes, b: bytes) -> float`
- `find_similar(insight: str, threshold: float = 0.75) -> list[dict]`
- `add_position(...)` — Insert with embedding
- `extend_position(id, ...)` — Update existing, refresh embedding
- `get_position(id)` — Retrieve
- `list_positions(domain=None)` — List all or by domain
- `check_overlap(insight: str)` — Used by Type B

**CLI interface:**
```bash
python3 positions.py add --domain X --title Y --insight "..."
python3 positions.py search "query text"
python3 positions.py list [--domain X]
python3 positions.py get <id>
python3 positions.py extend <id> --add-component "..." --add-evidence "..."
python3 positions.py check-overlap "insight text"
```

### 3. Seed Data

Extract positions from this conversation and add them as initial data:
- Domain: `hiring-market`
- The "hiring signal collapse" worldview

Reference: `/home/.z/workspaces/con_0CASX5AGlViD01uu/worldview-synthesis-hiring-signal-collapse.md`

## Success Criteria

| Test | Expected |
|------|----------|
| `add` then `get` | Returns same data |
| Add 3 positions, `search` for one | Correct one ranked highest |
| `check-overlap` on near-duplicate | Returns match above threshold |
| `check-overlap` on distinct | Returns no match |
| `extend` existing | Single row updated, not duplicated |

## Flexibility

- Schema fields adjustable if needed
- Similarity threshold (0.75) can be tuned
- CLI details flexible
- Error handling approach is your call

## Environment

- OpenAI SDK already installed (`openai 1.107.2`)
- Use `text-embedding-3-small` model
- Store embeddings as BLOB (1536 floats × 4 bytes = 6144 bytes per embedding)

## On Completion

1. Verify all success criteria pass
2. Document any deviations from spec
3. Report: "Worker positions-core complete. Ready for Worker 2 (Type B)."

---

*Open this file in a new conversation to begin work.*

