---
created: 2026-01-04
last_edited: 2026-01-05
version: 2.0
provenance: con_Elf8BKYxCI9VX8OY
---

# Build Plan: CC Outreach Tracker + Inbound Email Protocol

**Objective:** Auto-process emails where V CCs va@zo.computer, parsing V-OS tags to update CRM, create follow-ups, and mark list items complete.

## Updated Understanding (v2)

### V-OS Tag System

V embeds **white text tags** after email signatures. The system now supports **AI routing**:

```
V-OS Tags: {Zo} [CRM] [F-7] [DONE] * {Howie} [GPT-I] *
           ↑ AI target   ↑ tags      ↑ trigger
```

**Rules:**
1. `{Zo}` or `{Howie}` in curly braces = AI routing
2. Tags in brackets = instructions
3. Asterisk `*` = trigger (execute these tags)
4. No asterisk = template signature (ignore)
5. Raw expanded form = ignore entirely

### Zo-Relevant Tags

| Tag | Action |
|-----|--------|
| `[CRM]` | Update `last_contact_at` for recipient |
| `[DONE]` | Mark related must-contact items complete |
| `[F-X]` | Create follow-up reminder for X days |
| `[LD-*]` | Set/update CRM category |
| `[TERM]` | Mark relationship inactive |

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Gmail (Sent)   │────▶│  Polling Agent   │────▶│  Tag Parser     │
│  CC: va@zo      │     │  (3x daily)      │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                    ┌─────────────────────────────────────┼─────────────────┐
                    ▼                                     ▼                 ▼
           ┌────────────────┐                 ┌────────────────┐  ┌────────────────┐
           │  CRM Updater   │                 │  List Closer   │  │  Follow-up     │
           │  last_contact  │                 │  must-contact  │  │  Creator       │
           └────────────────┘                 └────────────────┘  └────────────────┘
```

---

## Phases

### Phase 1: Core Infrastructure ✅ → IN PROGRESS

**Files:**
- `N5/scripts/vos_tag_parser.py` — Parse V-OS tags from email body
- `N5/scripts/cc_outreach_processor.py` — Main processing script

**Parser Logic:**
```python
def parse_vos_tags(email_body: str) -> dict:
    """
    Returns:
    {
        "zo": {"tags": ["CRM", "F-7", "DONE"], "triggered": True},
        "howie": {"tags": ["GPT-I"], "triggered": True},
        "raw": False  # True if template signature detected
    }
    """
    # 1. Find V-OS Tags block (after signature, white text)
    # 2. Check for curly brace AI routing: {Zo}, {Howie}
    # 3. Check for asterisk trigger
    # 4. Extract bracket tags
```

### Phase 2: CRM Integration

- Match email recipients to CRM profiles (by email)
- Update `last_contact_at`
- Update category if `[LD-*]` tag present

### Phase 3: List Closure

- Search `must-contact.jsonl` for recipient name/email
- Mark matching items as `status: done`
- Update `last_suggested_at` in CRM

### Phase 4: Follow-up Creation

- Parse `[F-X]` tags (e.g., `[F-7]` = 7 days)
- Create entry in `Lists/followups.jsonl` or scheduled agent
- Include context from email subject

### Phase 5: Agent Setup

- Create scheduled agent: `CC Outreach Processor`
- Schedule: 9am, 1pm, 6pm ET
- Polls Gmail, processes new CC'd emails

---

## Email Sources

| Account | Purpose |
|---------|---------|
| `attawar.v@gmail.com` | Personal outreach |
| `vrijen@mycareerspan.com` | Business outreach |

Both accounts should be polled.

---

## State Tracking

To avoid reprocessing emails:

```json
// N5/data/cc_outreach_state.json
{
  "last_processed": {
    "attawar.v@gmail.com": "2026-01-05T14:00:00Z",
    "vrijen@mycareerspan.com": "2026-01-05T14:00:00Z"
  },
  "processed_message_ids": ["abc123", "def456"]
}
```

---

## Test Cases

1. **Basic CRM update:**
   - Email CC'd to va@zo, tags: `{Zo} [CRM] *`
   - Expected: recipient's `last_contact_at` updated

2. **Follow-up creation:**
   - Tags: `{Zo} [CRM] [F-7] *`
   - Expected: CRM updated + 7-day follow-up created

3. **List closure:**
   - Recipient in must-contact.jsonl
   - Tags: `{Zo} [CRM] [DONE] *`
   - Expected: CRM updated + must-contact item marked done

4. **Howie-only (Zo ignores):**
   - Tags: `{Howie} [GPT-F] *`
   - Expected: Zo takes no action

5. **No trigger (template):**
   - Raw V-OS Tags block, no asterisk
   - Expected: Zo takes no action

---

## Dependencies

- `use_app_gmail` for email search
- `N5/data/crm_v3.db` for CRM updates
- `Lists/must-contact.jsonl` for list closure

---

## Parallel Work Stream

**Worker spawned:** `WORKER_ASSIGNMENT_20260105_024500_TAG_CENTRALIZATION.md`
- Centralizes V-OS tag definitions
- Creates canonical `N5/config/vos_tags.json`
- Documents at `N5/docs/vos-tag-system.md`

---

**Ready for Builder.** Start at Phase 1: vos_tag_parser.py

