---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_GCktM2iwLZIi5cHK
---

# Deal Intelligence System — Full Design

## Design Principles

1. **LLMs for semantics, Python for plumbing** — Use LLMs to understand intent, extract meaning, detect signals. Use Python/SQL for data operations, syncing, formatting.
2. **Append-only intelligence** — Never overwrite; always append with timestamps. History is valuable.
3. **Bidirectional sync** — Local is fast index, Notion is source of truth for humans. Changes flow both ways.
4. **SMS-first updates** — V can text deal updates from anywhere; Zo parses and propagates.
5. **Proactive but gated** — System detects signals proactively, but V approves before creating new deals.

---

## Data Flow Architecture

```
                                    ┌─────────────────────┐
                                    │      NOTION         │
                                    │  (Source of Truth)  │
                                    │                     │
                                    │  • Acquirer Targets │
                                    │  • Deal Brokers     │
                                    │  • Leadership       │
                                    └──────────┬──────────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                              ▼                ▼                ▼
┌─────────────┐      ┌───────────────┐   ┌──────────┐   ┌─────────────┐
│   MEETING   │      │    EMAIL      │   │   SMS    │   │   KONDO     │
│  B-blocks   │      │  Gmail scan   │   │  "n5     │   │  LinkedIn   │
│  processed  │      │  + backfill   │   │  deal"   │   │  webhook    │
└──────┬──────┘      └───────┬───────┘   └────┬─────┘   └──────┬──────┘
       │                     │                │                │
       └──────────┬──────────┴────────────────┴────────────────┘
                  │
                  ▼
         ┌───────────────────┐
         │   SIGNAL ROUTER   │
         │   (LLM-powered)   │
         │                   │
         │  1. Parse input   │
         │  2. Match to deal │
         │  3. Extract intel │
         │  4. Detect stage  │
         └─────────┬─────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
  ┌───────────┐        ┌─────────────┐
  │  KNOWN    │        │  UNKNOWN    │
  │  DEAL     │        │  (New sig)  │
  └─────┬─────┘        └──────┬──────┘
        │                     │
        ▼                     ▼
  ┌───────────┐        ┌─────────────┐
  │  UPDATE   │        │  SMS V for  │
  │  Local +  │        │  approval   │
  │  Notion   │        │             │
  └───────────┘        └─────────────┘
```

---

## Notion Field Mapping

### Acquirer Targets Database

| Notion Field | Type | Sync Direction | Notes |
|--------------|------|----------------|-------|
| Company | Title | Notion → Local | Primary identifier |
| Deal Temp | Select | Bidirectional | hot/warm/cool/temperate |
| Status | Select | Bidirectional | Stage equivalent |
| Category | Select | Notion → Local | ATS, Staffing, etc. |
| Proximity | Select | Notion → Local | 1st/2nd degree |
| Intelligence Summary | Rich Text | Local → Notion | **Append-only** |
| Last Meeting | Date | Local → Notion | Auto-updated |
| Next Action | Text | Bidirectional | What's next |

### Intelligence Summary Format (Append-Only)

```markdown
---
## [2026-01-18] Meeting with Christine Song

**Stage:** Engaged → Qualified
**Signal:** Expressed interest in partnership structure
**Key Intel:**
- Budget approved for Q1
- Decision maker is CEO (Sarah)
- Timeline: 60 days

**Next:** Send proposal by Friday

---
## [2026-01-15] Email thread: Partnership terms

**Signal:** Responded positively to pricing
**Key Intel:**
- Comfortable with $X range
- Wants pilot program first

---
```

---

## SMS Command Interface

### Syntax

```
n5 deal <deal_name> <update>
```

### Examples

```
n5 deal darwinbox They're ready to move forward, setting up call next week
n5 deal ribbon Christine confirmed budget, need to send proposal
n5 deal aviato Hot lead - founder wants to integrate ASAP
```

### Parsing (LLM-powered)

Input: `n5 deal darwinbox They're ready to move forward, setting up call next week`

LLM extracts:
```json
{
  "deal_query": "darwinbox",
  "pipeline": "careerspan",  // inferred from deal match
  "update_text": "They're ready to move forward, setting up call next week",
  "signals": {
    "stage_change": "qualified → negotiating",
    "sentiment": "positive",
    "next_action": "set up call next week"
  }
}
```

### Response Flow

1. V texts: `n5 deal darwinbox They're ready to move forward`
2. Zo matches to `cs-acq-darwinbox` (Darwinbox, careerspan pipeline)
3. Zo updates:
   - `deals.db` — stage, last_touched, add activity log
   - Notion — append to Intelligence Summary
4. Zo texts back: `✓ Updated Darwinbox (careerspan) — stage: negotiating. Notion synced.`

---

## LLM Usage Points

| Component | LLM Task | Why Not Regex |
|-----------|----------|---------------|
| Signal Detection | Identify deal-relevant content in meetings/emails | Semantic understanding needed |
| Deal Matching | Fuzzy match "darwinbox" to "Darwinbox" | Handle typos, aliases, partial names |
| Stage Inference | "ready to move forward" → negotiating | Context-dependent interpretation |
| Intel Extraction | Pull key facts from unstructured text | Summarization + classification |
| New Deal Detection | "This person seems like a broker" | Intent + role classification |

### LLM Prompts (Examples)

**Deal Match Prompt:**
```
Given the user input "{query}" and these deals:
{deal_list}

Which deal is the user referring to? Consider:
- Exact matches
- Partial company name matches  
- Contact name matches
- Common abbreviations

Return: deal_id or "no_match"
```

**Signal Extraction Prompt:**
```
Extract deal intelligence from this update:
"{update_text}"

Return JSON:
{
  "stage_signal": "none|positive|negative|stage_change",
  "inferred_stage": "identified|researched|outreach|engaged|qualified|negotiating|closed_won|closed_lost|null",
  "key_facts": ["fact1", "fact2"],
  "next_action": "string or null",
  "sentiment": "positive|neutral|negative"
}
```

---

## Incremental Progress Tracking

### Stage Progression

```
identified → researched → outreach → engaged → qualified → negotiating → closed_won
                                                                      ↘ closed_lost
```

### Auto-Stage Detection Rules

| Signal | Stage Inference |
|--------|-----------------|
| "sent first email" | → outreach |
| "they responded" | → engaged |
| "confirmed interest" | → qualified |
| "discussing terms/pricing" | → negotiating |
| "deal signed/closed" | → closed_won |
| "they passed/declined" | → closed_lost |

### Momentum Tracking

```python
# In deal_activities table
- meetings_last_30_days: int
- emails_last_30_days: int  
- days_since_last_touch: int
- momentum: "accelerating" | "steady" | "stalling" | "cold"
```

---

## Worker Split

### Worker 1: Signal Router Core
- `deal_signal_router.py` — main orchestrator
- LLM-powered deal matching
- LLM-powered signal extraction
- Route to appropriate handler

### Worker 2: Meeting Integration  
- `B37_DEAL_INTEL.md` block generation
- Hook into meeting processing pipeline
- Extract intel from B01, B08, B13, B25

### Worker 3: Notion Sync
- Bidirectional sync logic
- Append-only intelligence field
- Field mapping + formatting
- Conflict resolution (Notion wins for manual edits)

### Worker 4: SMS Interface
- Parse "n5 deal" commands
- Integration with existing SMS handler
- Response formatting
- Error handling

### Worker 5: Email Scanner
- Daily Gmail scan for deal signals
- Historical backfill (last 90 days)
- Thread association

### Worker 6: Proactive Sensing
- New deal detection
- SMS approval flow
- Auto-create after approval

---

## Open Questions Resolved

| Question | Decision |
|----------|----------|
| LLM vs regex? | **LLM** for all semantic tasks |
| Notion field for intel? | **Intelligence Summary** (rich text, append-only) |
| SMS syntax? | `n5 deal <name> <update>` |
| Stage auto-update? | **Yes**, with LLM inference |
| New deal approval? | **SMS confirmation required** |
