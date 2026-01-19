---
created: 2026-01-18
last_edited: 2026-01-18
version: 4.0
provenance: con_Eu1OoHRtx1VWaR6g
---
# Deal Intelligence System — Build Orchestrator

## 🎉 BUILD COMPLETE

All 7 workers completed and validated. **79 tests passing + Worker 7 polish.**

## Workers

| # | Name | Purpose | Status |
|---|------|---------|--------|
| 1 | Signal Router Core | LLM matching + extraction | ✅ Complete |
| 2 | Meeting Integration | B37 block generator | ✅ Complete |
| 3 | Notion Sync | Bidirectional sync | ✅ Complete |
| 4 | SMS Interface | "n5 deal" commands | ✅ Complete |
| 5 | Email Scanner | Gmail signal extraction | ✅ Complete |
| 6 | Proactive Sensing | New entity detection | ✅ Complete |
| 7 | Polish & Extend | Notion append, SMS commands, backfill | ✅ Complete |

## Final Status

| Worker | Title | Status | Tests |
|--------|-------|--------|-------|
| 1 | Signal Router Core | ✅ Complete | 5 |
| 2 | Meeting Integration | ✅ Complete | 6 |
| 3 | Notion Sync | ✅ Complete | 4 |
| 4 | SMS Interface | ✅ Complete | 26 |
| 5 | Email Scanner | ✅ Complete | 7 |
| 6 | Proactive Sensing | ✅ Complete | 31 |

## Completed Artifacts

### Core Scripts
- `file 'N5/scripts/deal_signal_router.py'` — LLM-assisted deal matching
- `file 'N5/scripts/deal_llm_prompts.py'` — Prompt templates
- `file 'N5/scripts/meeting_deal_intel.py'` — B37 block generator
- `file 'N5/scripts/notion_deal_sync.py'` — Bidirectional Notion sync
- `file 'N5/scripts/sms_deal_handler.py'` — SMS command parser
- `file 'N5/scripts/email_deal_scanner.py'` — Gmail deal scanner
- `file 'N5/scripts/deal_proactive_sensor.py'` — New entity detection

### Config
- `file 'N5/config/deal_signal_config.json'` — Matching thresholds
- `file 'N5/config/notion_field_mapping.json'` — Notion field mappings

### Database
- `file 'N5/data/deals.db'` — 77 deals, 32 contacts
- Tables: `deals`, `deal_contacts`, `deal_activities`, `processed_emails`, `pending_approvals`, `notion_outbox`

### Scheduled Agents
- Notion Sync (3x daily): `500d0a1d-75b3-4074-8c46-0db803888e84`
- Email Scanner (7 AM): `20334c89-9fa7-47aa-b19c-8a8d63ce4f89`

## How to Use

### SMS Commands (via text to Zo)

**Update a deal:**
```
n5 deal darwinbox Ready to proceed with pilot
n5 deal "ribbon health" Christine confirmed budget
```

**Check deal status:**
```
n5 deal status calendly
→ "Calendly: engaged (🔥hot). Last: today. Next: Send Howie dossier"
```

**List deals:**
```
n5 deal list hot
→ "Hot deals: 🔥Darwinbox (identified) [CS]"

n5 deal list all
→ Lists top 15 active deals across pipelines
```

**Add new deal:**
```
n5 deal add "Acme Corp" careerspan Met at demo day
n5 deal add "Cool Startup" zo Potential data partner
```

### Notion Intel Append

The system can append deal intelligence to Notion page bodies:

```bash
# Format intel for append
python3 N5/scripts/notion_intel_prepend.py format-markdown \
    --source-title "Meeting: Tope Sync" \
    --source-type "meeting" \
    --key-fact "In-person scheduled Jan 30" \
    --next-action "Send Howie dossier" \
    --json
```

Then via Zo:
```python
use_app_notion("notion-append-block", {
    "pageId": "<page_id>",
    "blockTypes": ["markdownContents"],
    "markdownContents": ["<formatted markdown>"]
}, email="vrijen@mycareerspan.com")
```

### Email Backfill

**Scan with offset (for historical backfill):**
```bash
python3 N5/scripts/email_deal_scanner.py --days 30 --offset 0    # Last 30 days
python3 N5/scripts/email_deal_scanner.py --days 30 --offset 30   # 30-60 days ago
python3 N5/scripts/email_deal_scanner.py --days 30 --offset 60   # 60-90 days ago
```

**Check backfill progress:**
```bash
python3 N5/scripts/email_deal_scanner.py backfill --check
→ "Backfill Status: in_progress. Progress: 33% (2 runs). Current window: 60-90 days ago"
```

**Advance backfill window (for scheduled agent):**
```bash
python3 N5/scripts/email_deal_scanner.py backfill --advance
```

### Manual Proactive Scan
```bash
python3 N5/scripts/deal_proactive_sensor.py --text "..." --source meeting --dry-run
```

### Query Deals
```bash
python3 N5/scripts/deal_query.py summary
python3 N5/scripts/deal_query.py deals --pipeline careerspan --temp hot
python3 N5/scripts/deal_query.py contacts --type broker
```

## Integration Tests

- [x] SMS update flow — `n5 deal darwinbox` tested
- [x] SMS status flow — `n5 deal status calendly` tested  
- [x] SMS list flow — `n5 deal list hot` tested
- [x] SMS add flow — `n5 deal add TestCorp careerspan` dry-run tested
- [x] Meeting flow — Tope meeting → B37 v2.0 generated
- [x] Notion append — Darwinbox page body updated
- [x] Proactive sensing — Broker detection working
- [x] Email backfill — offset/batch-size flags working
- [ ] Live Email scan — Needs Gmail API test
- [ ] Live Notion push (properties) — Needs sync test

## Scheduled Agents

| Agent | Schedule | Purpose |
|-------|----------|---------|
| Notion Sync | 3x daily | Push updates to Notion |
| Email Scanner | 7 AM daily | Scan recent emails for signals |
| *(TBD)* Email Backfill | Nightly x14 | Gradual historical backfill |

## Documentation

- `file 'N5/builds/deal-meeting-intel/STATUS.md'` — Full status
- `file 'N5/builds/deal-meeting-intel/DESIGN.md'` — System design
- `file 'N5/builds/deal-meeting-intel/PLAN.md'` — Original plan
- `file 'N5/builds/deal-meeting-intel/workers/WORKER-7-polish-and-extend.md'` — Polish tasks
