---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_GCktM2iwLZIi5cHK
---

# Build Plan: Deal-Aware Meeting Intelligence System

## Summary

Extend the meeting processing pipeline to automatically detect deal-related meetings and push intelligence back to Notion. When V meets with someone connected to a deal (broker, leadership target, or acquirer contact), the system captures deal-specific intel and updates the corresponding Notion database.

## Open Questions

1. ~~How do we match attendees to deals?~~ → Use B03 stakeholder intel + fuzzy match against deals.db + leadership cache
2. ~~What triggers the intel extraction?~~ → After B36_DEAL_ROUTING.json is generated, create B37_DEAL_INTEL.md
3. ~~What fields in Notion should be updated?~~ → "Notes" field appended with timestamped meeting intel
4. ~~Should brokers be tracked in deals.db?~~ → Yes, added as `deal_broker` (11 records)
5. ~~Should leadership be tracked in deals.db?~~ → Yes, added as `leadership_target` (21 records)
6. **Email sensing trigger**: Which emails? All inbound? Only CC'd? Only from/to deal contacts?
7. **New deal threshold**: What confidence level for auto-creating vs. flagging for review?
8. **Kondo integration**: Do we have webhook access to LinkedIn messages via Kondo?

## Checklist

### Phase 1: Deal Matching Infrastructure
- [ ] Add `deal_broker` type to deals.db schema
- [ ] Sync Deal Brokers from Notion to deals.db (12 contacts)
- [ ] Create `deal_matcher.py` — unified matching against all deal types
- [ ] Add leadership targets to deals.db as `leadership_target` type (21 people)
- [ ] Unit test: match "Christine Song" → Ribbon leadership + cs-acq-ribbon

### Phase 2: Meeting Intel Block (B37)
- [ ] Create `meeting_deal_intel.py` — generates B37_DEAL_INTEL.md
- [ ] Hook into deal_meeting_router.py (after B36 generated → trigger B37)
- [ ] B37 extracts: deal context, key intel, relationship to deal, suggested next actions
- [ ] Unit test: process real meeting folder with known deal contact

### Phase 3: Notion Push
- [ ] Create `notion_deal_push.py` — pushes B37 content to Notion
- [ ] Map deal_type → Notion database (acquirer→Acquirers, broker→Brokers, leadership→Leadership)
- [ ] Append formatted intel to appropriate Notion field
- [ ] Unit test: push sample intel to test record in Notion

### Phase 4: Integration & Scheduling
- [ ] Integrate into deal_meeting_router.py workflow
- [ ] Update scheduled agent to include Notion push step
- [ ] Add dry-run mode for testing
- [ ] End-to-end test with recent meeting

## Phases

### Phase 1: Deal Matching Infrastructure

**Affected Files:**
- `N5/data/deals.db` — add deal_broker and leadership_target types
- `N5/scripts/deal_sync_external.py` — sync brokers and leadership
- `N5/scripts/deal_matcher.py` — NEW: unified matching service
- `N5/cache/deal_sync/` — existing cache files

**Changes:**
1. Create `deal_matcher.py`:
   ```python
   class DealMatcher:
       def match_person(self, name: str, company: str = None) -> List[DealMatch]
       def match_company(self, company: str) -> List[DealMatch]
       def match_meeting(self, meeting_path: Path) -> List[DealMatch]
   ```
2. Extend `deal_sync_external.py`:
   - Add `sync_deal_brokers()` function
   - Add `sync_leadership_targets()` function
3. Populate deals.db with brokers (12) and leadership (21)

**Unit Tests:**
- `test_match_person("Christine Song")` → returns Ribbon leadership match
- `test_match_person("Jennifer Ives")` → returns deal_broker match
- `test_match_company("Darwinbox")` → returns acquirer match

### Phase 2: Meeting Intel Block (B37)

**Affected Files:**
- `N5/scripts/meeting_deal_intel.py` — NEW: generates B37
- `N5/scripts/deal_meeting_router.py` — add hook for B37 generation
- `N5/prompts/deal_intel_prompt.md` — NEW: prompt template

**Changes:**
1. Create `meeting_deal_intel.py`:
   - Input: meeting folder path + DealMatch results
   - Reads: B01 (recap), B03 (stakeholders), B13 (risks), B25 (deliverables)
   - Outputs: B37_DEAL_INTEL.md with structured intel per matched deal
2. B37 format:
   ```markdown
   ---
   deal_matches:
     - deal_id: cs-acq-ribbon
       deal_type: careerspan_acquirer
       match_type: leadership_contact
       matched_person: Christine Song
       confidence: 0.95
   ---
   
   ## Deal Intel: Ribbon (Christine Song)
   
   ### Meeting Context
   [What was discussed relevant to the deal]
   
   ### Key Intelligence
   [Extracted insights for deal progression]
   
   ### Relationship Status
   [Current state of the relationship]
   
   ### Suggested Next Actions
   [Recommendations based on meeting content]
   ```

**Unit Tests:**
- Generate B37 for real meeting with Christine Song → valid YAML + content
- Generate B37 for broker meeting → different format for broker type

### Phase 3: Notion Push

**Affected Files:**
- `N5/scripts/notion_deal_push.py` — NEW: pushes intel to Notion
- `N5/config/notion_field_mapping.json` — NEW: field ID mappings

**Changes:**
1. Create `notion_deal_push.py`:
   - Input: B37_DEAL_INTEL.md file
   - Parses YAML frontmatter for deal matches
   - Routes to correct Notion database based on deal_type
   - Appends formatted intel to Notes/Intel field
2. Notion field mapping:
   ```json
   {
     "careerspan_acquirer": {
       "database_id": "3a2d606f-99fb-4ecf-9f92-374d324f7247",
       "intel_field": "Notes"
     },
     "deal_broker": {
       "database_id": "2ec5c3d6-a5db-8007-a821-000bf97dee8b",
       "intel_field": "Blurb"
     },
     "leadership_target": {
       "database_id": "2438ec09-5208-45d5-88b3-2d761099da9a",
       "intel_field": "Notes / thesis"
     }
   }
   ```
3. Append format:
   ```
   ---
   ## [2026-01-18] Meeting: Christine Song Sync
   
   ### Key Intel
   [Extracted content from B37]
   
   ### Next Steps
   [Action items]
   ```

**Unit Tests:**
- Push sample intel to test Notion page → verify field updated
- Push to non-existent deal → graceful error handling

### Phase 4: Integration & Scheduling

**Affected Files:**
- `N5/scripts/deal_meeting_router.py` — integrate B37 + Notion push
- Scheduled agent instruction — add Notion push step

**Changes:**
1. Extend `deal_meeting_router.py`:
   - After B36 generated → call `meeting_deal_intel.py`
   - After B37 generated → call `notion_deal_push.py`
   - Add `--skip-notion-push` flag for dry runs
2. Update scheduled agent:
   - Ensure Notion push runs after meeting routing

**Unit Tests:**
- End-to-end: process meeting → B36 → B37 → Notion updated
- Dry-run mode: no Notion changes

### Phase 5: Proactive Deal Sensing (Multi-Channel)

**Goal:** Detect potential deals from emails and flag/create new deals automatically.

**Affected Files:**
- `N5/scripts/email_deal_sensor.py` — NEW: scans emails for deal signals
- `N5/scripts/deal_signal_detector.py` — NEW: shared signal detection logic
- `N5/data/deals.db` — add `deal_signals` table for flagged potentials
- `N5/review/deals/` — HITL review queue for uncertain matches

**Changes:**

1. **Email Integration Hook** (via Gmail app):
   - Scheduled scan of recent emails (last 24h)
   - Priority: emails with deal contacts in To/CC/From
   - Secondary: emails mentioning company names from deals.db
   - Tertiary: emails with deal keywords (acquisition, partnership, intro, etc.)

2. **Signal Detection Logic** (`deal_signal_detector.py`):
   ```python
   class DealSignalDetector:
       def detect_signals(self, text: str, participants: List[str]) -> DealSignal:
           # Returns: matched_deals, potential_new_deals, confidence, signal_type
       
       def classify_signal(self, signal: DealSignal) -> Action:
           # HIGH confidence (>0.9) + existing deal → auto-link + update intel
           # HIGH confidence (>0.9) + new deal → auto-create in deals.db
           # MEDIUM confidence (0.7-0.9) → flag for HITL review
           # LOW confidence (<0.7) → log only, no action
   ```

3. **New Deal Auto-Creation**:
   - When email/meeting mentions company NOT in deals.db
   - AND contains deal signals (intro, partnership, acquisition language)
   - AND confidence > 0.85
   - → Create as `stage: prospect` with `source: email_sensed` or `meeting_sensed`

4. **HITL Review Queue**:
   - Uncertain matches staged to `N5/review/deals/YYYY-MM-DD_deal-signals.md`
   - Format: signal source, matched text, suggested deal, confidence, [APPROVE/REJECT]

5. **Kondo/LinkedIn Integration** (future):
   - If Kondo webhook available: process LinkedIn messages same as email
   - If not: manual trigger via `deal_signal_detector.py --source linkedin --file <export>`

**Unit Tests:**
- Email with known deal contact → auto-link
- Email mentioning new company + "partnership" → flag for review
- Email with no signals → no action

### Phase 6: Email-to-Deal Workflow (Gmail Integration)

**Affected Files:**
- Scheduled agent — add email scan step
- `N5/scripts/gmail_deal_scan.py` — NEW: orchestrates email scanning

**Changes:**

1. **Scheduled Email Scan** (daily or twice-daily):
   ```
   1. Fetch emails from last 24h via Gmail API
   2. For each email:
      a. Extract participants (From, To, CC)
      b. Run deal_signal_detector.detect_signals()
      c. If matched existing deal → log activity to deals.db
      d. If potential new deal → apply confidence threshold
      e. If above threshold → create/flag accordingly
   3. Push intel to Notion for matched deals
   4. Generate HITL review file for uncertain matches
   ```

2. **Email Thread Tracking**:
   - Track email thread IDs linked to deals
   - Subsequent emails in thread auto-link to same deal

**Unit Tests:**
- Scan test inbox with planted deal emails → correct detection
- Thread continuation → links to same deal

## Success Criteria

1. **Match accuracy**: 95%+ of deal-related meetings correctly identified
2. **Intel quality**: B37 extracts actionable, deal-specific intel (not generic recap)
3. **Notion sync**: Updates appear in Notion within 6 hours of meeting processing
4. **No duplicates**: Same meeting intel not pushed twice to Notion
5. **Audit trail**: All pushes logged with meeting ID + timestamp

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positive matches | Noise in Notion | Require confidence > 0.80 for push |
| Notion API rate limits | Sync failures | Batch pushes, exponential backoff |
| Field mapping drift | Push failures | Validate field existence before push |
| Duplicate pushes | Cluttered Notion | Track pushed meetings in deals.db |

## Architecture Decision: Why Not Airtable?

The existing `airtable_deal_sync.py` infrastructure suggests Airtable was considered. However:
- **V's current workflow** uses Notion for deal tracking (3 databases)
- **Bidirectional sync** is easier with Notion API (richer field support)
- **Single source of truth** = Notion; deals.db = local index for fast matching

Decision: **Notion is primary, deals.db is cache/index**

## Data Flow

```
                    ┌─────────────────┐
                    │  Meeting        │
                    │  (Recording)    │
                    └────────┬────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
┌─────────┐           ┌─────────────┐          ┌─────────────┐
│ Email   │           │ B-blocks    │          │ LinkedIn    │
│ (Gmail) │           │ Generated   │          │ (Kondo)     │
└────┬────┘           └──────┬──────┘          └──────┬──────┘
     │                       │                        │
     └───────────────────────┼────────────────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ deal_signal_detector│
                  │ (unified matching)  │
                  └──────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐  ┌───────────┐  ┌───────────┐
        │ Existing │  │ New Deal  │  │ Uncertain │
        │ Deal     │  │ (auto-    │  │ (HITL     │
        │ Match    │  │ create)   │  │ review)   │
        └────┬─────┘  └─────┬─────┘  └─────┬─────┘
             │              │              │
             ▼              ▼              │
        ┌─────────────────────────┐        │
        │ B37_DEAL_INTEL.md      │        │
        │ (meeting intel block)   │        │
        └───────────┬─────────────┘        │
                    │                      │
                    ▼                      ▼
        ┌─────────────────────┐    ┌──────────────────┐
        │ notion_deal_push.py │    │ N5/review/deals/ │
        │ (update Notion)     │    │ (human review)   │
        └───────────┬─────────┘    └──────────────────┘
                    │
                    ▼
        ┌─────────────────────┐
        │ deals.db            │
        │ (activity log)      │
        └─────────────────────┘
```

## Estimated Effort

- Phase 1: 2 hours (matching infrastructure) — ✅ DONE
- Phase 2: 2 hours (B37 generation)
- Phase 3: 2 hours (Notion push)
- Phase 4: 1 hour (integration)
- Phase 5: 3 hours (proactive deal sensing)
- Phase 6: 2 hours (email integration)

**Total: ~12 hours**

## References

- `file 'N5/scripts/deal_meeting_router.py'` — existing routing logic
- `file 'N5/scripts/airtable_deal_sync_v2.py'` — intel extraction patterns
- `file 'N5/scripts/meeting_crm_linker.py'` — attendee matching patterns
- `file 'N5/cache/deal_sync/'` — cached Notion data
