---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_LtMXlYe5vtBsMym1
---

# PLAN: Broker Detection & Sync in Deal Intelligence

## Open Questions

1. **Schema enrichment**: Should we add a `broker_info` section to B37 YAML frontmatter, or keep it in the markdown body only?
   - **Decision**: Frontmatter for machine-readable, body for human-readable
2. **Retroactive processing**: Should we scan existing B37s for brokers?
   - **Decision**: Yes, create a one-time backfill script
3. **Broker confidence threshold**: What confidence level triggers auto-creation vs. manual review?
   - **Decision**: ≥80% auto-create, <80% queue for review

## Context

**Problem**: Deal intelligence (B37) doesn't detect or flag when a meeting attendee is acting as a broker (someone who can introduce Careerspan to potential acquirers/partners, without being the target themselves).

**Example**: Ray from the 2026-01-15 meeting — he's not a deal target, but he has M&A experience and offered to intro V to potential acquirers.

**Existing Infrastructure**:
- `deal_contacts` table in SQLite with `contact_type = 'broker'` support
- Notion "Deal Brokers" database (`2ec5c3d6-a5db-8007-a821-000bf97dee8b`)
- `notion_field_mapping.json` already has `deal_brokers` config
- `notion_deal_sync.py` handles bidirectional sync (but not yet for brokers specifically)

## Alternatives Considered (Nemawashi)

### Alternative A: Inline in meeting_deal_intel.py
**Approach**: Add broker detection directly into `extract_deal_intel()` and `generate_b37_block()`
- **Pros**: Single file change, tight coupling to B37 generation
- **Cons**: Bloats meeting_deal_intel.py, mixes concerns

### Alternative B: Separate broker_detector.py module ✅ RECOMMENDED
**Approach**: Create dedicated module that:
1. Takes transcript/B-blocks as input
2. Returns broker candidates with confidence scores
3. Called from meeting_deal_intel.py after B37 generation
- **Pros**: Clean separation, reusable, testable
- **Cons**: One more file to maintain

### Alternative C: Post-processing agent
**Approach**: Scheduled agent scans B37s for broker patterns
- **Pros**: Non-blocking, can use LLM for nuanced detection
- **Cons**: Latency, adds complexity, duplicates work

**Decision**: Alternative B — clean, single-responsibility module

## Injection Point

```
Meeting Pipeline Flow:
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  B36_DEAL_ROUTING│ ──▶ │ meeting_deal_intel│ ──▶ │   B37_DEAL_INTEL │
│  (classification)│     │   (extraction)    │     │   (output)       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                  │
                                  ▼ NEW
                         ┌──────────────────┐     ┌──────────────────┐
                         │ broker_detector  │ ──▶ │ B38_BROKER_INTEL │
                         │   (detection)    │     │   (optional)     │
                         └──────────────────┘     └──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ deal_contacts DB │
                         │ + Notion sync    │
                         └──────────────────┘
```

## Checklist

### Phase 1: Broker Detection Module
- [x] Create `N5/scripts/broker_detector.py`
- [x] Implement heuristic detection (keywords, patterns)
- [x] Implement confidence scoring
- [x] Add name extraction from meeting folder/title
- [x] CLI for testing

### Phase 2: Integration with meeting_deal_intel.py
- [x] Import broker_detector module
- [x] Call detection in generate_b37_block()
- [x] Embed broker section in B37 output

### Phase 3: Database Persistence
- [x] Add broker columns to deal_contacts table (broker_confidence, broker_signals, network_access, source_meeting)
- [x] Implement persist_broker_to_db()
- [x] Auto-persist ≥80% confidence brokers

### Phase 4: Notion Sync
- [x] Implement queue_broker_notion_sync() using notion_outbox table
- [ ] Extend notion_deal_sync.py to handle broker_intel entity type
- [ ] Test Notion Deal Brokers database sync

## Status

**Current Phase**: 4 (Notion Sync - partial)
**Progress**: 11/13 (85%)
**Blocker**: Need to extend notion_deal_sync.py to handle new entity type

## Phase 1: Broker Detection Module

### Affected Files
- `N5/scripts/broker_detector.py` (NEW)

### Changes

Create `broker_detector.py` with:

```python
@dataclass
class BrokerCandidate:
    name: str
    company: str
    confidence: int  # 0-100
    signals: List[str]  # what triggered detection
    context: str  # relevant quote
    source_block: str  # B01, B03, transcript
    
def detect_brokers(
    transcript: str,
    b01_content: Optional[str],
    b03_content: Optional[str],
    existing_brokers: List[str]  # to dedupe
) -> List[BrokerCandidate]:
    """
    Detect broker patterns in meeting content.
    
    Broker signals:
    - Offers to make introductions ("I know someone...", "Send me your stuff")
    - Has relevant network ("connected to...", "knows people at...")
    - Advisory role without being the deal target
    - M&A/acquisition experience mentioned
    - Not the primary meeting subject but facilitating deals
    """
```

### Detection Heuristics

**High-confidence signals (30 pts each)**:
- "send me your stuff" / "I'll send this to..."
- "I know someone who..." / "let me intro you to..."
- "I have a contact at..."
- Explicit offer to broker/facilitate

**Medium-confidence signals (20 pts each)**:
- M&A/acquisition experience mentioned
- Connected to relevant companies
- Advisory relationship established
- Previous deal-making experience

**Low-confidence signals (10 pts each)**:
- General network mentions
- Industry connections
- Non-specific "I can help"

**Threshold**: ≥60 confidence = broker candidate

### Unit Tests
```python
def test_ray_meeting():
    """Ray should be detected as broker with high confidence."""
    result = detect_brokers(ray_transcript, ray_b01, ray_b03, [])
    assert len(result) == 1
    assert result[0].name == "Ray"
    assert result[0].confidence >= 80
    assert "send me your stuff" in result[0].signals
```

## Phase 2: B37 Integration

### Affected Files
- `N5/scripts/meeting_deal_intel.py` (MODIFY)

### Changes

1. Import broker_detector
2. After `extract_deal_intel()`, call `detect_brokers()`
3. Add results to `DealIntel` dataclass (new field: `broker_candidates`)
4. Modify `generate_b37_block()` to include broker section

**B37 Frontmatter Addition**:
```yaml
brokers_detected:
  - name: Ray
    company: Hearth
    confidence: 85
    notion_synced: false
```

**B37 Body Addition**:
```markdown
## Broker Intelligence

### Ray (Hearth) — Confidence: 85%
- **Signals**: "Send me your stuff", M&A experience, offered intro
- **Context**: "There's at least one other potential [acquirer]"
- **Action**: ✅ Added to Deal Brokers pipeline
```

## Phase 3: Local DB Persistence

### Affected Files
- `N5/scripts/meeting_deal_intel.py` (MODIFY)

### Changes

Add function `persist_brokers()`:
```python
def persist_brokers(brokers: List[BrokerCandidate], meeting_folder: str, dry_run: bool) -> None:
    """Upsert broker candidates to deal_contacts table."""
    for broker in brokers:
        if broker.confidence < 80:
            # Queue for manual review
            queue_broker_review(broker)
            continue
        
        # Upsert to deal_contacts
        upsert_deal_contact(
            contact_type="broker",
            pipeline="careerspan",
            full_name=broker.name,
            company=broker.company,
            angle_strategy=broker.context,
            source_system="meeting_deal_intel",
            source_id=meeting_folder
        )
        
        # Queue Notion sync
        queue_notion_sync_contact(broker)
```

## Phase 4: Notion Sync

### Affected Files
- `N5/scripts/notion_deal_sync.py` (MODIFY)
- `N5/config/notion_field_mapping.json` (VERIFY)

### Changes

1. Add `sync_brokers()` function to notion_deal_sync.py
2. Use existing `deal_brokers` config from mapping
3. Handle create vs. update (by name match)

**Notion API call** (via Pipedream):
```python
# Create new broker
use_app_notion(
    tool_name="notion-create-page-from-database",
    configured_props={
        "parentDataSource": "2ec5c3d6-a5db-8007-a821-000bf97dee8b",
        "properties": {
            "Contact": broker.name,
            "Current Org": broker.company,
            "Angle / Strategy": broker.context
        }
    }
)
```

## Success Criteria

1. ✅ Ray detected as broker in the 2026-01-15 meeting with confidence ≥80%
2. ✅ B37 includes "Broker Intelligence" section
3. ✅ Broker appears in `deal_contacts` table
4. ✅ Broker synced to Notion "Deal Brokers" database
5. ✅ Existing B37s can be backfilled (CLI command)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positives (detecting non-brokers) | Medium | Confidence threshold + manual review queue |
| Missing existing brokers (false negatives) | Low | Can manually add; backfill catches some |
| Notion sync conflicts | Medium | Check for existing by name before create |
| Schema drift between local and Notion | Low | Use mapping config, not hardcoded fields |

## Trap Doors

⚠️ **B37 schema change** — Adding `brokers_detected` to frontmatter affects all existing B37 parsing. 
- **Mitigation**: Make field optional, handle missing gracefully

## Estimated Effort

- Phase 1: 45 min (new module)
- Phase 2: 30 min (integration)
- Phase 3: 20 min (DB persistence)
- Phase 4: 30 min (Notion sync)
- **Total**: ~2 hours

## Single Worker Build

This is a focused enough scope that it can be done in a single conversation rather than multi-worker orchestration. No MECE validation needed.
