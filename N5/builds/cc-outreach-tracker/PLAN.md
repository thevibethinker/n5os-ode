---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.0
provenance: con_Elf8BKYxCI9VX8OY
---

# Build Plan: CC Outreach Tracker

**Objective:** Auto-close contacts when V CCs va@zo.computer on outreach emails

**Pattern:** V sends email to contact, CCs va@zo.computer → Zo detects → updates CRM `last_contact_at` + marks list items done

---

## Open Questions

- [x] Trigger mechanism? → **Gmail polling agent** (simplest, uses existing tools)
- [x] How to avoid reprocessing? → Track `last_processed_at` in state file
- [ ] How often to run? → **3x daily** (9am, 1pm, 6pm) — catches morning/afternoon/evening outreach

---

## Checklist

### Phase 1: Core Script
- [ ] Create `N5/scripts/cc_outreach_processor.py`
- [ ] Gmail search: `from:attawar.v@gmail.com cc:va@zo.computer after:YYYY/MM/DD`
- [ ] Extract TO recipients (email addresses)
- [ ] Match against CRM profiles (by email field)
- [ ] Update `last_contact_at` for matched profiles
- [ ] Mark matching must-contact items as done
- [ ] Track state in `N5/data/cc_outreach_state.json`
- [ ] Test with --dry-run flag

### Phase 2: Scheduled Agent
- [ ] Create agent running 3x daily
- [ ] Instruction: Run cc_outreach_processor.py, report updates
- [ ] Verify with one manual test email

---

## Phase 1: Core Script

**Affected Files:**
- `N5/scripts/cc_outreach_processor.py` (NEW)
- `N5/data/cc_outreach_state.json` (NEW)
- `N5/data/crm_v3.db` (UPDATE last_contact_at)
- `Lists/must-contact.jsonl` (UPDATE status)

**Changes:**

```python
# cc_outreach_processor.py
# 1. Load last_processed_at from state file (default: 7 days ago)
# 2. Search Gmail: from:V cc:va@zo.computer after:last_processed_at
# 3. For each email:
#    a. Extract TO addresses
#    b. For each TO address:
#       - Search CRM for profile with matching email
#       - If found: UPDATE last_contact_at = email_date
#       - Search must-contact for matching name/context
#       - If found: mark status = done
# 4. Update last_processed_at to now
# 5. Log summary: "Updated X CRM profiles, closed Y list items"
```

**Unit Tests:**
- [ ] Dry run with real Gmail search returns expected structure
- [ ] CRM update works for known profile
- [ ] must-contact item marked done correctly
- [ ] State file persists between runs

---

## Phase 2: Scheduled Agent

**Affected Files:**
- Zo agent registry (via create_agent)

**Changes:**
- Create agent with rrule: `FREQ=DAILY;BYHOUR=9,13,18;BYMINUTE=0`
- Instruction: Execute cc_outreach_processor.py and report

**Unit Tests:**
- [ ] Agent created successfully
- [ ] Manual trigger works

---

## Success Criteria

1. V CCs va@zo.computer on outreach email
2. Within 4 hours, CRM `last_contact_at` updated
3. If contact was in must-contact, item marked done
4. Morning digest no longer shows that contact in Reconnects

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Gmail rate limits | Batch processing, reasonable frequency (3x/day) |
| Email matching failures | Log unmatched for manual review |
| False positives (CC'd but not outreach) | Only process emails TO external addresses |

---

## Alternatives Considered

| Approach | Verdict |
|----------|---------|
| Real-time inbound handler | Rejected: Platform feature may not exist |
| Manual prompt trigger | Rejected: Defeats purpose (adds friction) |
| **Gmail polling agent** | **Selected**: Simple, reliable, uses existing tools |

---

**Ready for Builder.** Start at Phase 1.

