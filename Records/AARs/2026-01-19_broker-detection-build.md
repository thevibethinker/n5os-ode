---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_LtMXlYe5vtBsMym1
type: aar
build_slug: broker-detection
---

# AAR: Broker Detection System Build

**Date:** 2026-01-19  
**Duration:** ~45 minutes  
**Build:** broker-detection  
**Outcome:** ✅ Success

## Mission

Add automatic broker detection to the deal intelligence pipeline, so that when processing meeting transcripts, the system identifies people who could introduce Careerspan to potential acquirers (without being acquirers themselves).

## What Happened

1. **Trigger**: V received a meeting from Ray (Hearth founder) with acquisition advice. While manually processing it, realized the deal intel system didn't flag Ray as a broker despite clear signals.

2. **Build initiated**: Designed 4-phase approach — detection module → B37 integration → DB persistence → Notion sync.

3. **Detection challenges**: Initial heuristics triggered false negatives because negative patterns (e.g., "our company") were matching V's speech, not the broker's. Fixed by scoping negative patterns to "Them:" speaker content only.

4. **Successful validation**: Ray detected at 95% confidence with signals: M&A experience, offered introductions, mentioned leads, gave strategic advice, pre-existing relationship.

5. **Full pipeline working**: Ray persisted to `deal_contacts` table and synced to Notion Deal Brokers database.

## What Worked

- **Heuristic approach was sufficient** — no ML needed. Pattern matching on key phrases ("send me your stuff", "I know someone") combined with confidence scoring works well.
- **Name extraction from meeting metadata** — pulling broker name from folder/title instead of requiring attendee list.
- **Existing infrastructure** — `notion_deal_sync.py` outbox pattern made adding new entity type straightforward.

## What Didn't Work

- **Initial negative pattern scoping** — patterns meant to reduce false positives were triggering on V's speech, causing 0% confidence. Had to scope to "Them:" speaker content.
- **Notion app integration quirks** — `notion-create-page` vs `notion-create-page-from-database` parameter differences caused initial sync failure.

## Lessons Learned

1. **Speaker attribution matters** — when analyzing transcripts, patterns need to be scoped to the right speaker. V saying "our company" is very different from a counterpart saying it.

2. **Test with real data early** — the Ray meeting provided immediate validation. Without it, the false negative bug might have shipped.

3. **Outbox pattern is extensible** — adding new entity types to notion_deal_sync.py is now a known pattern: add to field mapping, handle in push_outbox action switch.

## Follow-Up Items

- [ ] Consider backfill script for existing B37s (decided: skip for now)
- [ ] Monitor false positive rate over next 10 meetings
- [ ] Add email/LinkedIn lookup for broker contact enrichment

## Files Changed

| File | Change |
|------|--------|
| `N5/scripts/broker_detector.py` | NEW — detection module |
| `N5/scripts/meeting_deal_intel.py` | MODIFIED — B37 integration |
| `N5/scripts/notion_deal_sync.py` | MODIFIED — create_page method, create action handler |
| `N5/data/deals.db` | SCHEMA — broker columns on deal_contacts |

## Metrics

- **Build time**: ~45 min (estimated 2 hours)
- **Files created**: 1 new, 2 modified
- **Test coverage**: 1 real meeting (Ray), full pipeline validated
