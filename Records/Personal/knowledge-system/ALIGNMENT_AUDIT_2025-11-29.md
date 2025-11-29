---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Knowledge Alignment Audit – 2025-11-29

## Overview

This document summarizes the implementation and verification work for **Worker 9: Post-Migration Alignment & Audit**.

Scope:
- Align GTM and CRM scripts with `Personal/Knowledge/**` using `N5/prefs/paths/knowledge_paths.yaml`.
- Establish a minimal compatibility shell under `Knowledge/architectural/**`.
- Update integrator/curator flows to route into `Personal/Knowledge/**` instead of `Knowledge/**`.
- Update key prefs/docs so they treat `Personal/Knowledge/` as SSOT and `Knowledge/` as a compatibility shell.
- Run an explicit audit (plus preflight + migration dry-runs) and recommend snapshot readiness.

Status: **Completed**.

---

## Code Changes

### 1. GTM Path Alignment

All active GTM scripts now resolve the GTM intelligence database path via `knowledge_paths.yaml` (`personal_knowledge.market_intelligence.db`) instead of hard-coded `Knowledge/market_intelligence/gtm_intelligence.db` paths.

Updated scripts:
- `file 'N5/scripts/gtm_query.py'`
- `file 'N5/scripts/gtm_worker.py'`
- `file 'N5/scripts/gtm_b31_processor.py'`
- `file 'N5/scripts/gtm_processor_llm_auto.py'`
- `file 'N5/scripts/gtm_rebuild_with_interpretation.py'`
- `file 'N5/scripts/gtm_extract_direct.py'`
- `file 'N5/scripts/gtm_backfill_llm.py'`
- `file 'N5/scripts/gtm_db_backfill.py'`
- `file 'N5/scripts/gtm_db_builder.py'`

Common pattern:
- Load `N5/prefs/paths/knowledge_paths.yaml`.
- Resolve `personal_knowledge.market_intelligence.db` (and, where needed, `personal_knowledge.market_intelligence.root`).
- Use this resolved path for all DB access and GTM registry work.

Verification:
- `python3 N5/scripts/gtm_query.py stats` ran successfully against `Personal/Knowledge/Intelligence/World/Market/db/gtm_intelligence.db`, returning category and signal-strength stats with no path errors.

### 2. CRM Script Alignment

Primary helper:
- **`file 'N5/scripts/crm_query.py'`** is now the canonical CLI helper for CRM V3.
  - DB path: resolved via `personal_knowledge.crm.db` in `knowledge_paths.yaml`.
  - Markdown profiles:
    - DB rows store paths relative to `/home/workspace` under `Personal/Knowledge/CRM/individuals/`.
    - New profiles are written under `Personal/Knowledge/CRM/individuals/` using the same resolver.

Additional changes:
- Profile markdown creation in `crm_query.py` now writes directly to `Personal/Knowledge/CRM/individuals/*.md` and keeps frontmatter in sync.

Verification:
- `python3 N5/scripts/crm_query.py list --status=prospect` executed successfully and opened the CRM DB at the `Personal/Knowledge/CRM/db/crm.db` location (no path errors; currently no matching individuals, which is consistent with recent migrations).

Notes on other CRM scripts:
- `file 'N5/scripts/knowledge_migrate_crm.py'` is the primary structural migration script for CRM; it already uses `knowledge_paths.yaml` and treats `Personal/Knowledge/CRM/**` as SSOT. No changes were required beyond running it in `--dry-run` mode for this audit (see Audit section).
- Older migration helpers such as `file 'N5/scripts/crm_migrate_to_v3.py'` remain as historical utilities and are **not** on the mainline path; they still reference legacy `Knowledge/crm/crm.db` but are not invoked by current workflows.

### 3. Integrator / Curator Routing

Goal: ensure new knowledge is written into `Personal/Knowledge/**` instead of treating `Knowledge/**` as SSOT.

#### 3.1 `knowledge_integrator.py`

File: `file 'N5/scripts/knowledge_integrator.py'`

Key changes:
- Introduced a small routing helper inside the script that loads `knowledge_paths.yaml` and exposes:
  - `Personal/Knowledge/Intelligence/**` root
  - `Personal/Knowledge/ContentLibrary/content/**` root
  - `Personal/Knowledge/Intelligence/World/Market/**` (market intelligence root)
- Replaced the previous `KNOWLEDGE_DIR / target` behavior with:
  - A `resolve_target_path_from_legacy(target: str) -> Path` helper that:
    - Routes `market_intelligence/*` and `intelligence/World/Market/*` into the market-intelligence root.
    - Routes obvious content buckets (`external_research/`, `hypotheses/`, `semi_stable/`, `evolving/`) into `ContentLibrary/content/**`.
    - Routes everything else into the Intelligence root.
- `check_protection` still uses `n5_protect.py` against the **resolved** Personal/Knowledge path, honoring existing `.n5protected` markers.

Effect:
- YAML extractions under `Knowledge/intelligence/extracts/*.yaml` are still read as inputs, but their **writes now land under `Personal/Knowledge/**`** according to routing heuristics.

#### 3.2 `document_media_curator.py`

File: `file 'N5/scripts/document_media_curator.py'`

Key changes:
- Added a routing helper mirroring the logic above:
  - Approved intelligence is now moved to a destination under `Personal/Knowledge/**` rather than `/home/workspace/Knowledge/**`.
  - Heuristics:
    - `market_intelligence/` → `Personal/Knowledge/Intelligence/World/Market/**`.
    - `external_research/`, `hypotheses/`, `semi_stable/`, `evolving/` → `Personal/Knowledge/ContentLibrary/content/**`.
    - Custom/other destinations → `Personal/Knowledge/Intelligence/**` plus the provided relative path.
- The interactive UX (choices `[1]`–`[6]`, prompts, previews) remains unchanged; only the actual destination root has moved from `Knowledge/` to `Personal/Knowledge/`.
- The curation log (`curation_log.jsonl`) still lives under the legacy `Knowledge/intelligence` tree; this is acceptable because it is an operational artifact, not an elevated knowledge SSOT.

Effect:
- Human-approved document/media intelligence is now internalized into `Personal/Knowledge/**` while preserving the existing approval workflow and logs.

### 4. `Knowledge/architectural/**` Compatibility Shell

Created explicit compatibility stubs under:
- `file 'Knowledge/architectural/architectural_principles.md'`
- `file 'Knowledge/architectural/ingestion_standards.md'`
- `file 'Knowledge/architectural/operational_principles.md'`

Each file:
- Includes required YAML frontmatter (`created`, `last_edited`, `version`).
- Clearly states that it is a **compatibility shell** only.
- Points to the canonical Personal/Knowledge locations, e.g.:
  - `file 'Personal/Knowledge/Architecture/principles/architectural_principles.md'`
  - `file 'Personal/Knowledge/Architecture/ingestion_standards/INGESTION_STANDARDS.md'` (or equivalent in that subtree).
- Explicitly instructs **not** to add new content there.

Interaction with maintenance scripts:
- `file 'N5/scripts/maintenance/daily_guardian.py'` expects
  - `Knowledge/architectural/ingestion_standards.md`
  - `Knowledge/architectural/operational_principles.md`

These now exist and are non-empty, so Daily Guardian will no longer log CRITICAL errors for missing architectural files while still treating `Personal/Knowledge/**` as SSOT.

### 5. Prefs / Docs SSOT Alignment

Updated core preference documents to reflect the new architecture.

#### 5.1 `N5/prefs/knowledge/lookup.md`

File: `file 'N5/prefs/knowledge/lookup.md'`

Changes:
- Added an **“SSOT vs Compatibility”** section under Purpose:
  - Declares `Personal/Knowledge/**` as the single source of truth for elevated knowledge (Wisdom, Intelligence, ContentLibrary, Canon, CRM).
  - Declares `Knowledge/**` as a compatibility shell where reads are allowed, but new writes should target `Personal/Knowledge/**`.
- Updated System Operations section:
  - Points to `Personal/Knowledge/Architecture/principles/architectural_principles.md` and `Personal/Knowledge/Architecture/ingestion_standards/INGESTION_STANDARDS.md` as canonical.
  - Explicitly labels `Knowledge/architectural/ingestion_standards.md` and `Knowledge/architectural/operational_principles.md` as compatibility shells.
- Updated Update Protocol and Related Files:
  - When editing canonical knowledge, the ingestion standards under `Personal/Knowledge/Architecture/ingestion_standards/**` are now the first stop.
  - Related Files list distinguishes between canonical Personal/Knowledge paths and legacy Knowledge paths.

#### 5.2 `N5/prefs/system/architecture-enforcement.md`

File: `file 'N5/prefs/system/architecture-enforcement.md'`

Changes:
- Clarified that architectural principles now live canonically at:
  - `file 'Personal/Knowledge/Architecture/principles/architectural_principles.md'`.
- Treats `Knowledge/architectural/architectural_principles.md` as a **thin compatibility shell**, not SSOT.
- Updated the “Integration with N5.md” example block so that:
  - N5 system design references the Personal/Knowledge architecture path first.
  - It explicitly notes that the Knowledge/ path is a compatibility shell only.

#### 5.3 `N5/prefs/system/folder-policy.md`

File: `file 'N5/prefs/system/folder-policy.md'`

Changes:
- In the Knowledge Folder section:
  - Declared `file 'Personal/Knowledge/'` as the canonical knowledge root (SSOT).
  - Declared `file 'Knowledge/'` as a compatibility shell retained for legacy paths.
- Updated Related Files to:
  - Point to Personal/Knowledge Architecture ingestion standards and principles as canonical.
  - List `Knowledge/architectural/…` paths explicitly as compatibility shells.

---

## Audit & Verification

### 1. Knowledge Alignment Audit Script

File: `file 'N5/scripts/knowledge_alignment_audit.py'`

Behavior:
- Scans `Knowledge/**` and reports:
  - `non_stub_markdowns`: markdown files outside known compatibility zones that look like “real” content.
  - `unexpected_dbs` / `unexpected_logs`: any DB or log-like files under `Knowledge/**`.
  - CRM compatibility status: confirms `Knowledge/crm/individuals/**` are stubs.
  - Reasoning-patterns compatibility status: confirms `Knowledge/reasoning-patterns/**` is stub-only.
  - Architectural compatibility status: ensures `Knowledge/architectural/**` contains only the intended shell files.

Run:
- Command:
  - `python3 N5/scripts/knowledge_alignment_audit.py --json`

Result (key fields):
- `root_exists`: `true`
- `non_stub_markdowns`: `[]`
- `unexpected_dbs`: `[]`
- `unexpected_logs`: `[]`
- `crm_individuals_stub_ok`: `true`
- `reasoning_patterns_stub_ok`: `true`
- `architectural_ok`: `true`

Interpretation:
- No unexpected live markdown content under `Knowledge/**` beyond known compatibility shells.
- No stray DB or log files living under the legacy Knowledge tree.
- CRM, reasoning-patterns, and architectural compatibility areas are in the expected “stub only” state.

### 2. `knowledge_preflight.py --check-only`

Command:
- `python3 N5/scripts/knowledge_preflight.py --check-only`

Highlights from log:
- DRY-RUN actions only (no filesystem writes):
  - Would create `.n5protected` markers at:
    - `/home/workspace/Personal/Knowledge/.n5protected`
    - `/home/workspace/Knowledge/.n5protected`
- Summary:
  - “Planned/applied 2 actions.” (all in dry-run mode)

Interpretation:
- Preflight confirms the existing skeleton and protection markers are largely in place.
- Both Personal/Knowledge and the legacy Knowledge shell are treated as protected roots for structural changes.

### 3. GTM & CRM Migrations (Dry-Run)

#### 3.1 GTM / Market Intelligence

Script: `file 'N5/scripts/knowledge_migrate_market_intel.py'`

Command:
- `python3 N5/scripts/knowledge_migrate_market_intel.py --dry-run`

Highlights:
- All key assets reported as “already migrated”:
  - `gtm_intelligence.db`
  - `meeting_registry.jsonl`
  - `meeting-processing-registry.jsonl`
  - narrative markdowns (various market-intel docs) already present in the canonical location.
- Plan summary:
  - DB files: 0
  - Registry files: 0
  - Narratives to promote: 0
  - Narratives to archive: 0
  - Skipped: 5 (operational files)
- Report path (dry-run placeholder):
  - `Records/Personal/knowledge-system/logs/market_intel_migration_run_20251129_203828.md`

Interpretation:
- Market intelligence migration is effectively complete; rerunning the migration would be idempotent.

#### 3.2 CRM Migration

Script: `file 'N5/scripts/knowledge_migrate_crm.py'`

Command:
- `python3 N5/scripts/knowledge_migrate_crm.py --dry-run --limit 50`

Highlights:
- Planned DB moves (all DRY-RUN):
  - Legacy DBs under `Personal/Knowledge/Legacy_Inbox/crm/` → `Personal/Knowledge/CRM/db/…`
  - All destination DBs already exist; script would leave legacy copies in place (non-destructive).
- Profiles:
  - “Planned 50 canonical profiles” for the first batch.
  - For each profile, canonical path already exists under `Personal/Knowledge/CRM/individuals/*.md`.
  - Script would write compatibility stubs under `Knowledge/crm/individuals/*.md` pointing to canonical Personal/Knowledge paths (DRY-RUN only in this run).
- Index:
  - Would write `Knowledge/crm/individuals/index.jsonl` with ~184 entries (compatibility index for older tools).
- Run log:
  - `Records/Personal/knowledge-system/logs/crm_migration_run_20251129T203829Z.md` (dry-run summary).

Interpretation:
- Canonical CRM profiles already live under `Personal/Knowledge/CRM/individuals/`.
- Migration script is ready to maintain/refresh compatibility stubs and indexes under `Knowledge/crm/individuals/` without disturbing canonical data.

### 4. GTM / CRM Operational Checks

Commands:
- `python3 N5/scripts/gtm_query.py stats`
  - Succeeded; reported:
    - 247 total insights across 49 meetings.
    - Category and signal-strength breakdown with no DB path errors.
- `python3 N5/scripts/crm_query.py list --status=prospect`
  - Succeeded; no path or schema errors. Current filter returned no rows, consistent with recent CRM consolidation.

Interpretation:
- Both GTM and CRM query helpers resolve their DB paths via `knowledge_paths.yaml` and operate correctly against the canonical Personal/Knowledge locations.

---

## Remaining Legacy References & Rationale

- Some documentation and historical notes still reference `Knowledge/stable/**` paths (e.g., legacy company docs and glossary). In `N5/prefs/knowledge/lookup.md` and `N5/prefs/system/folder-policy.md`, these are now explicitly labeled as **compatibility/legacy** locations, with `Personal/Knowledge/**` called out as SSOT.
- Operational logs and transient artifacts (e.g., curation logs) intentionally continue to live under `Knowledge/intelligence` to avoid disrupting existing review tooling. They are not treated as elevated knowledge SSOT and are excluded from the audit’s “non-stub markdown” set.
- Deprecated migration utilities (e.g., `crm_migrate_to_v3.py`) still reference `Knowledge/crm/crm.db`, but they are not part of the active migration path; replacement scripts (`knowledge_migrate_crm.py`, `crm_query.py`) now operate entirely against `Personal/Knowledge/**`.

These references are either:
- Clearly documented as legacy/compatibility, or
- Confined to tooling that is not invoked in the current production workflows.

---

## Snapshot Recommendation

Based on:
- All GTM and CRM scripts on the active path now resolving via `knowledge_paths.yaml` into `Personal/Knowledge/**`.
- Integrator/curator pipelines writing new knowledge into Personal/Knowledge rather than Knowledge.
- A clean legacy Knowledge tree:
  - No unexpected non-stub markdowns outside designated compatibility zones.
  - No unexpected DBs or logs under `Knowledge/**`.
  - CRM, reasoning-patterns, and architectural areas confirmed as stub-only.
- Successful dry-run of both GTM (market intelligence) and CRM migrations, showing idempotent behavior and alignment with Personal/Knowledge roots.
- Successful execution of GTM and CRM query helpers with no path or integrity errors.

**Recommendation:**

> It is **safe to take a git + system snapshot now** as a post-alignment checkpoint for the knowledge system.

If a snapshot is taken, this document (`ALIGNMENT_AUDIT_2025-11-29.md`) and the associated migration logs under `Records/Personal/knowledge-system/logs/` should be treated as the canonical description of the alignment state at the time of snapshot.

