---
created: 2025-12-05
last_edited: 2025-12-05
version: 1.0
status: spec
---

# Positions System Specification

## Overview

A knowledge-tier system for storing V's worldview as compound insights, organized by domain, with full connection tracking and artifact cataloging.

## Architecture Decision

**SQLite as source of truth.** Position papers are generated views.

## Storage

**Location:** `Personal/Knowledge/Positions/positions.db`

**Generated views:** `Personal/Knowledge/Positions/papers/` (markdown exports per domain)

---

## Schema

```sql
-- Core positions table
CREATE TABLE positions (
    id TEXT PRIMARY KEY,                    -- e.g., 'hiring-signal-collapse-v1'
    domain TEXT NOT NULL,                   -- e.g., 'hiring-market', 'ai-systems', 'careerspan', 'productivity'
    title TEXT NOT NULL,                    -- Short title
    insight TEXT NOT NULL,                  -- Rich multi-paragraph description (the thick unit)
    components TEXT,                        -- JSON: array of sub-claims/points that make up this insight
    stability TEXT DEFAULT 'emerging',      -- 'emerging' | 'tested' | 'durable'
    confidence INTEGER DEFAULT 3,           -- 1-5 scale
    formed_date TEXT,                       -- When first articulated
    last_refined TEXT,                      -- Last modification
    source_conversations TEXT,              -- JSON: array of conversation IDs where this was developed
    supersedes TEXT,                        -- JSON: array of position IDs this replaces/evolves
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Connections between positions
CREATE TABLE position_connections (
    from_position TEXT NOT NULL,
    to_position TEXT NOT NULL,
    connection_type TEXT NOT NULL,          -- 'supports', 'contradicts', 'extends', 'prerequisite', 'implies'
    notes TEXT,                             -- Optional explanation
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (from_position, to_position),
    FOREIGN KEY (from_position) REFERENCES positions(id),
    FOREIGN KEY (to_position) REFERENCES positions(id)
);

-- Evidence and artifacts linked to positions
CREATE TABLE position_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id TEXT NOT NULL,
    evidence_type TEXT NOT NULL,            -- 'content_library', 'meeting', 'article', 'url', 'file', 'conversation'
    reference_id TEXT,                      -- ID in source system (content library ID, meeting folder, etc.)
    reference_path TEXT,                    -- File path if applicable
    reference_url TEXT,                     -- URL if applicable
    snippet TEXT,                           -- Relevant excerpt/quote
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(id)
);

-- Knowledge units used/shared in conversations (for Type B extraction)
CREATE TABLE conversation_knowledge_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    item_type TEXT NOT NULL,                -- 'link', 'file', 'artifact', 'content_library', 'meeting', 'position'
    item_reference TEXT NOT NULL,           -- Path, URL, or ID
    item_title TEXT,                        -- Human-readable title
    usage_context TEXT,                     -- 'cited', 'created', 'referenced', 'shared'
    extracted_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Full-text search
CREATE VIRTUAL TABLE positions_fts USING fts5(
    title, 
    insight, 
    components,
    content='positions',
    content_rowid='rowid'
);

-- Indexes
CREATE INDEX idx_positions_domain ON positions(domain);
CREATE INDEX idx_positions_stability ON positions(stability);
CREATE INDEX idx_evidence_position ON position_evidence(position_id);
CREATE INDEX idx_knowledge_log_convo ON conversation_knowledge_log(conversation_id);
```

---

## Domains (Initial Set)

| Domain | Description |
|--------|-------------|
| `hiring-market` | Labor market dynamics, recruiting, job seeking |
| `ai-systems` | AI capabilities, limitations, integration patterns |
| `careerspan` | Product strategy, positioning, competitive landscape |
| `productivity` | Personal systems, knowledge work, time management |
| `coaching` | Career coaching philosophy, methods |
| `founder-life` | Entrepreneurship, startup dynamics |

*Domains are extensible—new ones created as needed.*

---

## Type B Conversation-End Workflow

### Trigger
Manual: "Consolidate knowledge" / "Extract positions" / "Type B close"

### Process

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: CATALOG KNOWLEDGE UNITS                           │
│                                                             │
│  Scan conversation for:                                     │
│  - URLs shared/cited                                        │
│  - Files created/referenced                                 │
│  - Content library items used                               │
│  - Meetings referenced                                      │
│  - Artifacts produced                                       │
│                                                             │
│  → Insert into conversation_knowledge_log                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: EXTRACT INSIGHT CANDIDATES                        │
│                                                             │
│  Identify compound insights articulated:                    │
│  - Conclusions reached                                      │
│  - Beliefs refined                                          │
│  - Frameworks developed                                     │
│  - "Resilient truths" stated                                │
│                                                             │
│  For each candidate, identify:                              │
│  - Core thesis                                              │
│  - Supporting sub-claims (components)                       │
│  - Relevant domain(s)                                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: CHECK FOR OVERLAP                                 │
│                                                             │
│  For each candidate:                                        │
│  1. Query positions_fts for semantic overlap                │
│  2. Load top matches from relevant domain(s)                │
│  3. Compare:                                                │
│     - HIGH overlap → EXTEND existing position               │
│     - PARTIAL overlap → LINK as related                     │
│     - NO overlap → CREATE new position                      │
│     - CONTRADICTION → FLAG for review                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: WRITE & CONNECT                                   │
│                                                             │
│  For NEW positions:                                         │
│  - Insert into positions table                              │
│  - Link evidence from Phase 1 catalog                       │
│  - Create connections to related positions                  │
│                                                             │
│  For EXTENDED positions:                                    │
│  - Update insight text                                      │
│  - Append to components if new sub-claims                   │
│  - Add this conversation to source_conversations            │
│  - Update last_refined timestamp                            │
│                                                             │
│  For ALL affected positions:                                │
│  - Scan for new cross-connections                           │
│  - Update position_connections table                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: REPORT                                            │
│                                                             │
│  Output summary:                                            │
│  - Knowledge units cataloged: N                             │
│  - Positions created: X                                     │
│  - Positions extended: Y                                    │
│  - Connections added: Z                                     │
│  - Contradictions flagged: W                                │
│                                                             │
│  Optionally regenerate affected position papers             │
└─────────────────────────────────────────────────────────────┘
```

---

## On Embeddings

**For MVP: Full-text search (FTS5) is sufficient.**

FTS5 handles keyword and phrase matching well. The "check for overlap" step can work with:
1. FTS5 query for similar terms
2. LLM judgment call on top N matches ("Is this new insight substantially covered by existing position X?")

**Embeddings can be added later** if FTS5 proves insufficient for semantic similarity. Would require:
- Adding an `embedding BLOB` column to positions
- Using sentence-transformers or OpenAI embeddings
- Vector similarity search (sqlite-vss extension or separate index)

Not needed for v1.

---

## CLI Interface (Planned)

```bash
# Add a position manually
python3 positions.py add --domain hiring-market --title "..." --insight "..."

# Search positions
python3 positions.py search "AI job applications"

# Export domain as position paper
python3 positions.py export --domain hiring-market --output papers/hiring-market.md

# Run Type B extraction on a conversation
python3 positions.py extract --conversation con_XXXXX

# View connections for a position
python3 positions.py connections --id hiring-signal-collapse-v1

# List all positions in a domain
python3 positions.py list --domain careerspan
```

---

## Example Position Entry

```json
{
  "id": "hiring-signal-collapse-v1",
  "domain": "hiring-market",
  "title": "The Hiring Signal Collapse",
  "insight": "Inbound hiring is broken at a fundamental, structural level—not due to process inefficiency but due to signal collapse. AI has made generating application content essentially free, while detection remains biologically constrained. This creates an asymmetry that cannot be solved by better filtering. The channel itself is compromised.\n\nThe real problem isn't even personalization—it's that people don't know themselves well enough to personalize meaningfully. AI lets candidates skip the self-knowledge work entirely while producing output that appears equivalent.",
  "components": [
    "AI makes generating tailored content ~free (supply side)",
    "Humans cannot reliably detect AI-generated content (demand side)", 
    "ATS and ML evaluate strings—zero marginal cost inputs",
    "Recruiters have biological processing limits (~100 resumes/day)",
    "Self-knowledge is the actual missing ingredient, not personalization technique",
    "Many employers only post jobs for legal compliance, not actual inbound hiring"
  ],
  "stability": "tested",
  "confidence": 4,
  "formed_date": "2025-12-05",
  "last_refined": "2025-12-05",
  "source_conversations": ["con_0CASX5AGlViD01uu"],
  "supersedes": ["tailored-applications-work-2024"]
}
```

---

## Files to Create

1. `Personal/Knowledge/Positions/positions.db` — SQLite database
2. `Personal/Knowledge/Positions/README.md` — System documentation
3. `N5/scripts/positions.py` — CLI and library
4. `Prompts/Consolidate Knowledge.prompt.md` — Type B conversation-end prompt

---

## Open Questions

1. **Domain taxonomy**: Start with 6 domains listed, or let them emerge organically?
2. **Stability transitions**: Manual promotion, or automatic based on citation count?
3. **Contradiction handling**: Flag only, or require resolution before proceeding?

---

*Spec ready for build. Route to Builder thread when ready to implement.*

