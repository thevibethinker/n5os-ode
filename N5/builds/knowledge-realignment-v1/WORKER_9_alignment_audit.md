---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 9: Post-Migration Alignment & Audit

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W9-ALIGNMENT-AUDIT  
**Estimated Time:** 60–120 minutes  
**Dependencies:**
- Workers 1–8 (and 7B) complete.
- `Personal/Knowledge/**` populated per Phase 2/3.

---

## Mission

Align **code, prefs, and compatibility shells** with the new knowledge architecture so that:

- GTM and CRM scripts use `Personal/Knowledge/**` and `knowledge_paths.yaml` instead of hard-coded `Knowledge/**` paths.
- N5 maintenance and personas stop treating `Knowledge/architectural/**` as the live SSOT while still having a minimal compatibility shell.
- Integrator/curator scripts route new material into `Personal/Knowledge/**` (Intelligence, ContentLibrary) instead of `Knowledge/**`.
- Key prefs/docs truthfully describe `Personal/Knowledge/` as SSOT.
- A final audit confirms no unexpected live content under `Knowledge/**` and recommends a snapshot point.

This worker should **not** move or delete large numbers of files; structural migrations are already done. It focuses on path alignment, compatibility shims, and verification.

---

## Deliverables

1. **GTM Path Alignment**
   - Updated GTM scripts (pick at least the current, supported path) to use `knowledge_paths.yaml` instead of hard-coded `Knowledge/market_intelligence/gtm_intelligence.db`:
     - Candidates: `N5/scripts/gtm_query.py`, `gtm_processor_llm_auto.py`, `gtm_worker.py`, `gtm_db_builder.py`, `gtm_db_backfill.py`, `gtm_extract_direct.py`, `gtm_backfill_llm.py`, `gtm_b31_processor.py`.
   - All updated scripts should:
     - Load `N5/prefs/paths/knowledge_paths.yaml`.
     - Resolve DB path from `personal_knowledge.market_intelligence.db`.
   - Optional: clearly mark truly legacy GTM scripts as deprecated in comments if not updated.

2. **CRM Script Alignment**
   - Choose a primary CRM helper (e.g. `N5/scripts/crm_query.py` or a new wrapper) and update it to:
     - Use `personal_knowledge.crm.db` from `knowledge_paths.yaml` for the DB.
     - Resolve markdown profiles from `Personal/Knowledge/CRM/individuals/` (not `Knowledge/crm/individuals/`).
   - For other CRM-related scripts that are still live (e.g. used by scheduled tasks or recent workflows), either:
     - Update their paths to call the new CRM helper, or
     - Clearly mark them as deprecated with pointers to the new helper.

3. **`Knowledge/architectural/**` Compatibility Shell**
   - Under `/home/workspace/Knowledge/architectural/`, create minimal compatibility files that:
     - Exist at the paths expected by maintenance/system docs (e.g. `architectural_principles.md`, `ingestion_standards.md`, `operational_principles.md`).
     - Contain a brief header note pointing to canonical sources under `Personal/Knowledge/Architecture/**`.
     - Optionally, include a short excerpt or link list rather than full duplicated content.
   - Ensure that daily maintenance scripts (`maintenance/daily_guardian.py`, etc.) no longer log CRITICAL for missing `Knowledge/architectural/...` files.

4. **Integrator/Curator Routing Update**
   - For scripts that still write to `Knowledge/**` as if it were SSOT (e.g. `knowledge_integrator.py`, `document_media_curator.py`, any obvious others):
     - Introduce or use a routing helper that decides whether a given item should land in:
       - `Personal/Knowledge/Intelligence/**`, or
       - `Personal/Knowledge/ContentLibrary/content/`.
     - Replace direct `Knowledge/` writes in active paths with calls to this router.
   - Do **not** attempt a full ontology-based reclassification; keep changes minimal but directionally correct.

5. **Prefs/Docs SSOT Alignment**
   - Update a small set of key N5 prefs/docs to reflect the new SSOT, for example:
     - `N5/prefs/knowledge/lookup.md`
     - `N5/prefs/system/architecture-enforcement.md`
     - `N5/prefs/system/folder-policy.md`
     - Any README that currently claims `Knowledge/` is the primary knowledge home.
   - Ensure they:
     - Declare `Personal/Knowledge/` as the canonical location for elevated knowledge.
     - Treat `Knowledge/` explicitly as a compatibility shell.
     - Reference `Personal/Knowledge/Architecture/principles/architectural_principles.md` as the canonical architecture file.

6. **Final Audit & Snapshot Recommendation**
   - Implement a small audit script or process that:
     - Scans `Knowledge/**` and reports:
       - Non-stub markdown files (if any).
       - Any unexpected DBs or logs.
     - Confirms that:
       - `Knowledge/crm/individuals/**` are stubs.
       - `Knowledge/reasoning-patterns/**` is a stub.
       - `Knowledge/architectural/**` contains only the intended compatibility shell.
   - Run `knowledge_preflight.py --check-only`, CRM & GTM migrations in `--dry-run`, and record the results.
   - Produce a final alignment report, e.g. `Records/Personal/knowledge-system/ALIGNMENT_AUDIT_2025-11-29.md`, summarizing:
     - Scripts updated.
     - Remaining legacy references (if any) and why they’re safe.
     - Recommendation: “Safe to take git + system snapshot now.”

---

## Requirements

- **Scope discipline:**
  - No new large migrations; keep changes focused on code/prefs/routing and tiny compatibility files.
  - Prefer updating a **small set of actively used scripts** over trying to refactor every historical script.
- **Safety:**
  - Respect `.n5protected` markers.
  - Do not delete anything under `Knowledge/**`; only add small compatibility files.
- **Config-aware:**
  - Wherever possible, use `knowledge_paths.yaml` instead of embedding new hard-coded paths.

---

## Implementation Guide (High-Level)

1. **GTM Alignment Pass**
   - Identify the current production GTM entry point(s) and update paths there first.
   - Use `knowledge_paths.yaml` for DB location.

2. **CRM Alignment Pass**
   - Make one helper authoritative (`crm_query` or a successor) and route others through it.

3. **Compatibility Shell Creation**
   - Implement minimal `Knowledge/architectural/**` files with clear "this moved" messaging.

4. **Integrator Routing Update**
   - Factor out a helper to pick between Intelligence vs ContentLibrary destinations.

5. **Prefs/Docs Update**
   - Edit only the most central prefs/docs; add a short “SSOT = Personal/Knowledge/” section.

6. **Audit + Report**
   - Run the checks, summarize results, and explicitly state whether the system is ready for a snapshot.

---

## Testing

- Verify updated GTM/CRM scripts run without path errors.
- Confirm daily maintenance logs no longer show CRITICAL missing `Knowledge/architectural/...` files.
- Run the audit script and confirm it reports no unexpected live content under `Knowledge/**`.

---

## Report Back

When this worker is complete, report to the orchestrator with:

1. Scripts and prefs actually modified (paths).
2. Any remaining legacy `Knowledge/**` references that were intentionally left as-is (with rationale).
3. Link to the final alignment report and a clear recommendation on taking a git + system snapshot.

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-29  

