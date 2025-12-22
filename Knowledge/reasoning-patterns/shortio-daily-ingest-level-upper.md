---
created: 2025-12-11
last_edited: 2025-12-11
version: 1.0
---

# Short.io daily ingest (Level Upper guided)

## When to reuse this pattern
- Any scheduled automation that runs a Short.io stats ingest and is critical to Careerspan reporting.
- When the task must follow the Level Upper checklist: enhanced reasoning, checkpoints at 33/66/100, and documented verification plus reasoning pattern storage.

## Core reasoning steps
1. **Level Upper baseline:** Start by ensuring Level Upper is active (`set_active_persona("76cccdcd-2709-490a-84a3-ca67c9852a82")` implicitly) so the job gets meta-reasoning support, and run `python3 N5/scripts/n5_load_context.py scheduler` for context.
2. **Ingest command execution:** Run `python3 N5/scripts/shortio_stats_ingest.py --days 1` with the required `SHORT_IO_KEY`, capturing stdout/stderr for later traceability (this represents the 33% checkpoint once execution begins).
3. **Result verification (66% checkpoint):** Confirm `N5/data/shortio_clicks.jsonl` has new entries for each link and `N5/logs/shortio_stats.log` records a clean finish; note any errors or rate-limit retries.
4. **Completion check (100% checkpoint):** Ensure there were no unhandled exceptions, log the final status, and tag the run as a success in the scheduler's log.
5. **Pattern capture:** Record this reasoning path in a file (this document) so future copies of this workflow can cite the steps before concluding.

## Outcomes to highlight
- The logic keeps ingest runs observable at every checkpoint (33/66/100) and prevents premature completion claims.
- It collates both the data (click rollups) and the diagnostics (log entry) before handing control back to Operator.
- The pattern doubles as a checklist for future Level Upper + scheduled ingest jobs.

