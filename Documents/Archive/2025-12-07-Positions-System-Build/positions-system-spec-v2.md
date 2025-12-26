---
created: 2025-12-06
last_edited: 2025-12-06
version: 2.0
status: spec-for-build
---

# Positions System Specification v2

## 1. Overview

A knowledge-tier system for storing V's compound insights, beliefs, and worldview positions with semantic search for overlap detection.

## 2. Architecture Decisions (Locked)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Source of truth | SQLite (`positions.db`) | Queryable, fits existing patterns |
| Position papers | **Dropped** | Semantic search sufficient |
| Embeddings | OpenAI `text-embedding-3-small` | Already installed, simple, cheap |
| Knowledge unit storage | **None** | Just summarized in Type B output |
| Type B conversation-end | Separate minimal worker | Calls existing functionality only |

## 3. What Gets Built

### Worker 1: Positions Core System

**Scope:** Database + CLI + semantic search

**Database Schema:**
```sql
-- positions.db

CREATE TABLE positions (
    id TEXT PRIMARY KEY,                    -- e.g., "hiring-signal-collapse"
    domain TEXT NOT NULL,                   -- e.g., "hiring-market", "ai-career", "product"
    title TEXT NOT NULL,                    -- Human-readable title
    insight TEXT NOT NULL,                  -- The compound insight (can be multi-paragraph)
    components TEXT,                        -- JSON array of sub-claims/parts
    evidence TEXT,                          -- JSON array of evidence pointers
    connections TEXT,                       -- JSON array: [{target_id, relationship}]
    stability TEXT DEFAULT 'emerging',      -- emerging | stable | canonical
    confidence INTEGER DEFAULT 3,           -- 1-5 scale
    formed_date TEXT,                       -- When V first articulated this
    last_refined TEXT,                      -- Last time it was extended/refined
    source_conversations TEXT,              -- JSON array of conversation IDs
    supersedes TEXT,                        -- JSON array of position IDs this replaces
    embedding BLOB,                         -- 1536-dim float32 vector
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_domain ON positions(domain);
CREATE INDEX idx_stability ON positions(stability);
```

**CLI Commands:**
```bash
# Add a new position
python3 positions.py add \
  --domain "hiring-market" \
  --title "Hiring Signal Collapse" \
  --insight "The inbound hiring channel is structurally broken..." \
  --stability canonical \
  --source-conversation con_0CASX5AGlViD01uu

# Search semantically
python3 positions.py search "AI making resumes worthless"
# Returns: top N similar positions with similarity scores

# Search by domain
python3 positions.py list --domain "hiring-market"

# Get specific position
python3 positions.py get hiring-signal-collapse

# Extend existing position
python3 positions.py extend hiring-signal-collapse \
  --add-component "New sub-claim" \
  --add-evidence "content-library:xyz" \
  --source-conversation con_ABC123

# Check for overlap (used by Type B)
python3 positions.py check-overlap "Some insight text"
# Returns: similar positions above threshold, or "no overlap"
```

**Core Functions:**
```python
def embed(text: str) -> bytes:
    """Generate embedding via OpenAI API"""

def cosine_similarity(a: bytes, b: bytes) -> float:
    """Compare two embeddings"""

def find_similar(insight: str, threshold: float = 0.75) -> list[dict]:
    """Find positions similar to given insight"""

def add_position(...) -> str:
    """Add new position, generate embedding, return ID"""

def extend_position(id: str, ...) -> None:
    """Add components/evidence to existing position, update embedding"""
```

**Flexibility for Builder:**
- Schema fields can be adjusted if implementation reveals issues
- Threshold for "similar enough to extend" can be tuned
- CLI interface details are flexible

---

### Worker 2: Type B Conversation-End

**Scope:** Minimal protocol that calls Worker 1's functionality

**Depends on:** Worker 1 must be complete first

**What it does:**
1. Receive conversation ID (or current conversation context)
2. Identify insight candidates from conversation (LLM extraction)
3. For each candidate:
   - Call `positions.py check-overlap`
   - If overlap found: call `positions.py extend`
   - If no overlap: call `positions.py add`
4. Collect all artifacts/links/files referenced in conversation
5. Output summary:
   ```
   ## Positions Updated
   - [extended] hiring-signal-collapse: Added component about...
   - [new] careerspan-coaching-mechanism: Created with...
   
   ## Knowledge Units Referenced
   - file: Knowledge/content-library/hiring-signal-collapse-worldview.md
   - url: https://example.com/article
   - artifact: worldview-synthesis-hiring-signal-collapse.md
   ```

**Implementation:** Single prompt file that:
- Uses LLM to extract insights
- Calls `positions.py` commands
- Formats output

**Flexibility for Builder:**
- Insight extraction prompt can be refined
- Output format is flexible
- Can be a prompt file or a script, builder's choice

---

## 4. Success Rubric

| Criterion | Target | How to Verify |
|-----------|--------|---------------|
| **Positions can be stored** | Add works, persists to DB | `add` then `get` returns same data |
| **Semantic search works** | Similar insights found | Add 3 positions, search finds correct one |
| **Overlap detection works** | Threshold correctly separates extend vs new | Test with near-duplicate and distinct insights |
| **Extend works** | Existing position updated, not duplicated | Extend, verify single row with new components |
| **Type B extracts correctly** | Insights pulled from conversation | Run on test conversation, verify extraction |
| **Type B routes correctly** | Extend vs new decision accurate | Run with overlap and without, verify behavior |
| **Output is useful** | V can see what happened | Summary clearly shows actions taken |

---

## 5. What's NOT in Scope

- Position papers / markdown exports (dropped)
- Knowledge unit persistence (just summarized)
- Automatic Type B triggering (manual only)
- Connection graph visualization
- Cross-domain relationship inference

---

## 6. Open Questions for Builder

1. **Embedding dimension:** Using 1536 (text-embedding-3-small). Confirm this works with BLOB storage.
2. **Similarity threshold:** Start with 0.75, may need tuning.
3. **Insight extraction prompt:** Builder designs this based on conversation structure.
4. **Error handling:** What if OpenAI API fails mid-operation?

---

## 7. File Locations

```
N5/
├── data/
│   └── positions.db              # The database
├── scripts/
│   └── positions.py              # CLI and library
└── prefs/
    └── positions/
        └── domains.json          # Optional: domain taxonomy
        
Prompts/
└── Type B Conversation End.prompt.md   # Or could be a script
```

---

*Spec ready for worker deployment.*

