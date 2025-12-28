---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.1
status: ready
provenance: con_WoVYvJ5iACxi1PaC
---
# Smart Event Detector - Implementation Plan

## Objective
Add a second-tier discovery layer that scans ALL recent emails for event signals, catching sources not yet in the allowlist.

## Supported Platforms & URL Patterns

| Platform | URL Patterns | Gmail Search Term | Notes |
|----------|-------------|-------------------|-------|
| **Luma** | `lu.ma/<slug>`, `lu.ma/<slug>?k=<key>`, `luma.com/join/<id>` | `"lu.ma"` | Primary event platform. Short slugs like `lu.ma/29g30um6` |
| **Partiful** | `partiful.com/e/<id>` | `"partiful.com/e/"` | IDs are alphanumeric ~20 chars, e.g. `nNFOLqcPtLeB5aSUb04g` |
| **Supermomos** | `supermomos.com/events/<slug>` | `"supermomos.com/events"` | Professional networking events |
| **Eventbrite** | `eventbrite.com/e/<name>-<id>` | `"eventbrite.com/e/"` | ID is numeric, e.g. `tickets-1234567890` |
| **Meetup** | `meetup.com/<group>/events/<id>` | `"meetup.com" "events"` | Group-based events |

### URL Regex Patterns (for extraction)
```python
EVENT_URL_PATTERNS = {
    "luma": [
        r"https?://lu\.ma/[a-zA-Z0-9_-]+",           # lu.ma/slug
        r"https?://luma\.com/join/[a-zA-Z0-9_-]+",   # luma.com/join/id
    ],
    "partiful": [
        r"https?://partiful\.com/e/[a-zA-Z0-9]+",    # partiful.com/e/id
    ],
    "supermomos": [
        r"https?://(?:www\.)?supermomos\.com/events/[a-zA-Z0-9_-]+",
    ],
    "eventbrite": [
        r"https?://(?:www\.)?eventbrite\.com/e/[a-zA-Z0-9_-]+-\d+",
    ],
    "meetup": [
        r"https?://(?:www\.)?meetup\.com/[^/]+/events/\d+",
    ],
}
```

## Architecture

### How It Works
```
┌─────────────────────────────────────────────────────────────────┐
│                     DAILY EVENT PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tier 1: Allowlist (High Precision)                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Gmail: from:(allowlist) newer_than:2d                    │   │
│  │ → Extract event URLs → Score → Recommend                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          ↓                                       │
│  Tier 2: Smart Detector (High Recall)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Gmail: ("lu.ma" OR "partiful.com/e/" OR                  │   │
│  │        "supermomos.com/events" OR "eventbrite.com/e/"    │   │
│  │        OR "meetup.com" "events") newer_than:2d           │   │
│  │        -from:(already_allowlisted)                       │   │
│  │ → Extract URLs + Sender → Flag for Review                │   │
│  │ → If good: Auto-add sender to allowlist                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Insight
We're not indexing all emails. We're pattern-matching for **event signals** in recent emails.

## Checklist

### Phase 1: Core Script
- [x] Create `N5/scripts/smart_event_detector.py`
  - [x] Build Gmail query excluding allowlist senders
  - [x] Extract event URLs using regex patterns above
  - [x] Extract sender email + name from each match
  - [x] Output: `N5/data/detected_events.json`

### Phase 2: Integration
- [x] Add to Daily Luma Pipeline (runs AFTER Tier 1)
- [x] Output format compatible with existing event processing

### Phase 3: Auto-Allowlist (Optional)
- [ ] If same sender detected 2+ times → auto-add to allowlist
- [ ] Log additions for transparency

## Affected Files
- `N5/scripts/smart_event_detector.py` (new)
- `N5/scripts/luma_orchestrator.py` (modified - add Tier 2 call)
- `N5/data/detected_events.json` (new output)

## Unit Tests
- [ ] Query generation excludes allowlist senders
- [ ] URL extraction handles all 5 platform patterns
- [ ] Empty results don't crash


