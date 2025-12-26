---
created: 2025-12-07
last_edited: 2025-12-11
version: 1.1
capability_id: positions-system
name: Positions System
category: internal
status: active
---

# Positions System
```yaml
# Zone 2: Capability metadata (machine-readable)
capability_id: positions-system
name: Positions System
category: internal
status: active
confidence: high
last_verified: 2025-12-11
tags:
- knowledge-synthesis
- positions
- worldview
entry_points:
- type: script
  id: N5/scripts/positions.py
- type: prompt
  id: Prompts/Close Conversation Type B.prompt.md
owner: V
change_type: update
capability_file: N5/capabilities/internal/positions-system.md
description: 'Updated to v1.1. Added essential CLI commands (audit, update, delete,
  export, suggest-connections), structured evidence support, and automatic bidirectional
  connection management. Improved integration with Type B workflow.

  '
associated_files:
- N5/data/positions.db
- N5/capabilities/internal/positions-system.md
```



## Summary

Knowledge-tier system for capturing, storing, and semantically searching V's worldview positions — compound insights, beliefs, and conclusions that emerge from conversations and experience.

## What It Does

- Stores **thick, compound insights** (not atomic facts) organized by domain
- Uses **OpenAI embeddings** for semantic similarity search
- Enables **overlap detection** before adding new positions (extend vs. create)
- Tracks **evidence, components, and cross-position connections**
- Integrates with **Type B Conversation End** for knowledge consolidation
- **Audits** positions for completeness (evidence, connections, components)

## Entry Points

| Entry Point | Type | Description |
|-------------|------|-------------|
| `python3 N5/scripts/positions.py` | CLI | Primary interface for all operations |
| `@Close Conversation Type B` | Prompt | Extracts positions from conversations |

## CLI Commands

```bash
# List all positions
python3 /home/workspace/N5/scripts/positions.py list

# List all domains
python3 /home/workspace/N5/scripts/positions.py list --domains

# Get a specific position
python3 /home/workspace/N5/scripts/positions.py get <position-id>

# Audit for incomplete positions (missing evidence, connections, etc.)
python3 /home/workspace/N5/scripts/positions.py audit

# Check for semantic overlap before adding
python3 /home/workspace/N5/scripts/positions.py check-overlap "Your insight text" --threshold 0.4

# Search positions semantically
python3 /home/workspace/N5/scripts/positions.py search "query" --threshold 0.4

# Suggest connections for a position
python3 /home/workspace/N5/scripts/positions.py suggest-connections <position-id>

# Add a new position (with evidence and components)
python3 /home/workspace/N5/scripts/positions.py add \
  --domain "domain-name" \
  --title "Position Title" \
  --insight "The compound insight text..." \
  --component "First sub-claim" \
  --component "Second sub-claim" \
  --evidence "content_library:item-id" \
  --evidence "meeting:folder-name" \
  --stability emerging \
  --confidence 3 \
  --source-conversation "con_XXX"

# Extend an existing position
python3 /home/workspace/N5/scripts/positions.py extend <position-id> \
  --add-component "New sub-claim" \
  --add-evidence "meeting:folder-name" \
  --add-connection "other-position-id:relationship" \
  --source-conversation "con_XXX"

# Update core fields of a position
python3 /home/workspace/N5/scripts/positions.py update <position-id> \
  --title "New Title" \
  --insight "Updated insight text (will re-embed)" \
  --domain "new-domain" \
  --stability stable \
  --confidence 4

# Delete a position (with confirmation)
python3 /home/workspace/N5/scripts/positions.py delete <position-id>

# Delete without confirmation (use with caution)
python3 /home/workspace/N5/scripts/positions.py delete <position-id> --force

# Export a position to markdown (prints to stdout)
python3 /home/workspace/N5/scripts/positions.py export <position-id>

# Export a position to markdown file
python3 /home/workspace/N5/scripts/positions.py export <position-id> -o /path/to/output.md
```

## Evidence Format

Evidence must be prefixed with a type:

| Type | Format | Example |
|------|--------|---------|
| Content Library | `content_library:<id>` | `content_library:hiring-signal-collapse-worldview` |
| Meeting | `meeting:<folder>` | `meeting:2025-10-10_hamoon-ekhtiari-futurefit` |
| URL | `url:<url>` | `url:https://example.com/article` |
| File | `file:<path>` | `file:Documents/Strategy/analysis.md` |
| Conversation | `conversation:<id>` | `conversation:con_abc123` |
| Article | `article:<id>` | `article:why-ai-changes-hiring` |

## Connection Types

| Relationship | Meaning |
|--------------|---------|
| `supports` | This position provides evidence for the other |
| `extends` | This position builds on the other |
| `contradicts` | This position conflicts with the other |
| `prerequisite` | The other must be true for this to hold |
| `implies` | If this is true, the other follows |
| `related` | General thematic connection |

## Associated Files

| File | Purpose |
|------|---------|
| `N5/scripts/positions.py` | Core CLI and library |
| `N5/data/positions.db` | SQLite database with embeddings |
| `Prompts/Close Conversation Type B.prompt.md` | Knowledge consolidation workflow |

## Database Schema

```sql
CREATE TABLE positions (
    id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    title TEXT NOT NULL,
    insight TEXT NOT NULL,
    components TEXT DEFAULT '[]',      -- JSON array of sub-claims
    evidence TEXT DEFAULT '[]',        -- JSON array of evidence pointers
    connections TEXT DEFAULT '[]',     -- JSON array of cross-references
    stability TEXT DEFAULT 'emerging', -- emerging|stable|canonical
    confidence INTEGER DEFAULT 3,      -- 1-5
    source_conversations TEXT DEFAULT '[]',
    embedding BLOB,                    -- 1536-dim float32 vector
    created_at TEXT,
    updated_at TEXT
);
```

## Workflow: Type B Conversation End

1. **Audit** — Check current state with `audit` command
2. **Catalog Evidence** — List all evidence items from conversation FIRST
3. **Extract** — Identify position candidates (conclusions, beliefs, frameworks)
4. **Check** — `check-overlap` for each candidate (threshold 0.4)
5. **Decide** — Extend existing (if overlap ≥0.5) or create new
6. **Execute** — Run `add` or `extend` commands WITH evidence
7. **Connect** — Run `suggest-connections` and add connections
8. **Verify** — Run `audit` to confirm completeness
9. **Output** — Summary of changes + evidence cataloged

## Design Principles

- **Thick units** — Positions are compound insights, not atomic claims
- **SQLite as source of truth** — No separate markdown position papers needed
- **Semantic search** — OpenAI `text-embedding-3-small` for overlap detection
- **Manual trigger** — Type B is invoked explicitly, not automatic
- **Extensible** — Positions grow via `extend` as evidence/components accumulate
- **Evidence required** — Every position must have at least one evidence pointer
- **Connections matter** — Positions should be linked when semantically related

## Source Conversations

- `con_0CASX5AGlViD01uu` — Initial build (2025-12-07)
- `con_mQJFva6ivyp81A4n` — v1.1 fixes: evidence format, audit command, suggest-connections (2025-12-11)



