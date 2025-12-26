---
created: 2025-12-08
last_edited: 2025-12-08
version: 1.0
---

# Meeting Archive Diagnostic Report
**Generated:** 2025-12-08 21:01:47 UTC-5  
**Stage:** MG-7 (Read-Only Diagnostic)

## Summary

| Metric | Count |
|--------|-------|
| Total `_[P]` meetings in Inbox | 4 |
| Meetings < 7 days old | 4 |
| Meetings ≥ 7 days old | 0 |

## Processed Meetings in Inbox (`_[P]` State)

All `_[P]` meetings are recent (processed today or within 3 days). They remain in Inbox pending review/follow-up completion.

| Meeting Name | Date | Age (days) | Time in [P] (days) |
|--------------|------|-----------|-------------------|
| 2025-12-05_logantheapplyai_[P] | 2025-12-05 | 3 | 0 |
| 2025-12-08_LinkedIn_powwow_[P] | 2025-12-08 | 0 | 0 |
| 2025-12-08_bradorange-quartercom_[P] | 2025-12-08 | 0 | 0 |
| 2025-12-08_ilyamycareerspancomloganmycareerspancomilsemycareerspancom_[P] | 2025-12-08 | 0 | 0 |

## Notes

- **No archival performed.** This prompt operates in read-only mode (v1.1+).
- **Archiving is performed exclusively by MG-7C** on meetings in `_[C]` state.
- Meetings ready for archival should first be transitioned to `_[C]` state using the C-state workflow.

## Next Steps

To archive meetings:
1. Complete follow-ups (MG-5) if not already done.
2. Mark meeting as `_[C]` (Completed) using `mark_meeting_c_state.py`.
3. Run MG-7C automation, which will move `_[C]` meetings to `Personal/Meetings/Archive/{YYYY}-Q{Q}/`.

