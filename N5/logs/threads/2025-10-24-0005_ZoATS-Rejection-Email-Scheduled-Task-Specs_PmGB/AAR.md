# After-Action Review (AAR)
**Conversation:** con_PmGBfimCfDhawS6h  
**Date:** 2025-10-24  
**Title:** 💬 ZoATS Rejection Email + Scheduled Task Specs

---

## Summary

Implemented ZoATS rejection email composer with config-driven Careerspan promo and optional legally-safe feedback system. Created 7 scheduled task specifications for ZoATS deployment pipeline (intake, parser, scoring, clarification monitoring, re-evaluation, dossier backfill, rejection drafts). All specs default to disabled and dry-run for safe deployment on new instances.

---

## Artifacts Created

### Primary Outputs
- file 'ZoATS/workers/rejection_email/config.json' — Config for promo placement and feedback options
- file 'ZoATS/workers/rejection_email/main.py' — Updated with feedback collection, legal filter, generic fallbacks
- file 'ZoATS/workers/rejection_email/batch.py' — Added --limit for one-at-a-time processing
- file 'ZoATS/workers/rejection_email/README.md' — Updated documentation

### Scheduled Task Specs (ZoATS/scheduled_tasks/)
- candidate_intake_5min.md
- parser_queue_5min.md
- scoring_queue_5min.md
- maybe_clarification_drafts_5min.md
- clarification_response_monitor_10min.md
- clarification_reeval_5min.md
- dossier_backfill_5min.md
- rejection_drafts_5min.md (initial)
- manifest.json — Machine-readable task registry

---

## Key Decisions

1. **Promo Placement:** Italic text before sign-off (third-person, respectful)
2. **Feedback Strategy:** Always collect; share only if config enabled; use legal filter + generic fallbacks
3. **Scheduling:** 5-min cadence, one-at-a-time processing to respect evaluation flow
4. **Deployment Safety:** All specs disabled + dry-run by default; not registered on this instance

---

## Tags
#ZoATS #ats #rejection-email #scheduling #specs #deployment

---

## Principles Applied
- P5 (Anti-Overwrite): Drafts only, no auto-send
- P7 (Dry-Run): Default mode for all scheduled tasks
- P15 (Complete Before Claiming): Full implementation with config, docs, specs
- P19 (Error Handling): Skip logic, logging, safe fallbacks
- P21 (Document Assumptions): Clear READMEs and spec files

---

## Related Work
- file 'ZoATS/workers/maybe_email/' — Clarification email approvals system
- file 'ZoATS/workers/scoring/main.py' — Gestalt evaluation source for feedback signals
- file 'N5/prefs/operations/scheduled-task-protocol.md' — Task safety requirements

---

## Notes
- No ZoATS tasks active on this Zo instance (specs only)
- Job-sourcing automation skipped per user preference (low volume)
