---
created: 2026-03-10
last_edited: 2026-03-10
version: 1.0
provenance: meeting-system-recovery-redesign/D1.2
---

# Meeting Pipeline System Audit

**Auditor:** D1.2 (automated)
**Date:** 2026-03-10
**Scope:** Current meeting ingestion pipeline — code, databases, filesystem state, failure modes

---

## 1. Architecture Overview

The meeting system has two coexisting generations:

### v2 Pipeline (Legacy — Nov 2025)
- **Entry point:** `N5/scripts/meeting_pipeline/transcript_processor_v4.py` (deprecated)
- **State store:** `N5/data/meeting_pipeline.db` (SQLite, 2MB, 11 tables)
- **Lifecycle:** detected → queued_for_ai → complete/failed
- **Folder convention:** `_[P]` (processing), `_[C]` (complete) suffixes
- **Archive target:** `Personal/Meetings/Archive/YYYY-QN/`
- **Status:** Effectively dead. Most recent complete row: 2025-11-22. Only 2 scripts remain in `N5/scripts/meeting_pipeline/`.

### v3 Pipeline (Current — Jan 2026)
- **Entry point:** `Skills/meeting-ingestion/scripts/meeting_cli.py` (901 lines)
- **State store:** Manifest-first (`manifest.json` per meeting folder) + `N5/data/meeting_registry.db` (dedup/stats)
- **Lifecycle:** ingested → identified → gated → processed/complete → archived
- **Folder convention:** `YYYY-MM-DD_Participant-Name` (no suffixes)
- **Archive target:** `Personal/Meetings/Week-of-YYYY-MM-DD/internal|external/`
- **Status:** Active. Most recent successful processing: 2026-03-10 (today).

### Database Landscape (4 SQLite databases)

| Database | Path | Tables | Role | Last Written |
|----------|------|--------|------|-------------|
| meeting_pipeline.db | `N5/data/` | 11 | v2 lifecycle, webhooks, recall bots | 2026-03-05 |
| meeting_pipeline.db | `N5/runtime/` | 1 (blocks) | v3 block generation tracking | 2026-01-03 |
| meeting_registry.db | `N5/data/` | 1 (meetings) | v3 dedup + stats | 2026-02-09 |
| block_registry.db | `N5/data/` | 1 (blocks) | Cross-pipeline block queue | 2024-11-01 |

**Critical finding:** There are TWO `meeting_pipeline.db` files at different paths with different schemas. The `N5/data/` version is the v2 operational store (11 tables, actively written by webhook handlers). The `N5/runtime/` version is a v3-era block tracker (1 table, last written Jan 3). This is a P02 (SSOT) violation.

---

## 2. State Model Analysis

<!-- State model: documented vs actual transitions -->

### Documented v3 State Machine (from SKILL.md)

```
raw file → [ingest] → ingested → [identify] → identified → [gate] → gated → [process] → processed → [archive] → archived
```

### Actual v3 State Machine (from code + manifest evidence)

```
raw file → [ingest] → ingested → [title_normalize] → title_normalized
                                        ↓
                                  → identified → [gate] → (gate results embedded, no explicit "gated" status written)
                                        ↓
                                  → [process blocks] → complete
```

**Key discrepancies:**

1. **"gated" status is never written.** The quality gate runs and embeds results in the manifest (`quality_gate` field), writes HITL items, but does NOT advance status to "gated". The `tick` command proceeds to block generation regardless of gate pass/fail — it logs warnings but doesn't block.

2. **"title_normalized" is an undocumented intermediate state.** The `title_normalizer.py` module writes this status between ingested and identified. SKILL.md doesn't mention it.

3. **"processed" vs "complete" ambiguity.** SKILL.md says status becomes "processed" after block generation. The actual manifest shows `"status": "complete"` and a separate `"processed_at"` timestamp. The `status` command checks for both "complete" (v3) and "complete" (legacy) but the code paths differ.

4. **No "archived" status is ever written.** The archive command moves folders to `Week-of-*/` directories but the manifest is not updated with a final "archived" status. Once moved, the meeting disappears from Inbox scans.

5. **Gate failures don't block processing.** The `tick` command catches gate exceptions as non-fatal and continues to block generation. This means meetings with critical quality issues (host not identified, calendar mismatch) still get fully processed. The HITL queue receives items but is never consulted before proceeding.

### v2 State Machine (from DB evidence)

```
detected → queued_for_ai → complete/failed
```

**125 meetings stuck permanently at `queued_for_ai`** since 2025-11-04. These represent the entire backlog of transcripts from Sep-Nov 2025 that were queued for AI processing but never completed. The v2 processing pipeline was abandoned when v3 was built.

---

## 3. Reusable Components

<!-- Reusable components: salvageable vs broken -->

### Clearly Reusable (Working Well)

| Component | File | Lines | Evidence |
|-----------|------|-------|----------|
| **Ingest module** | `ingest.py` | 610 | Successfully ingests Fireflies JSONL + markdown. Creates correct v3 manifests. Used today. |
| **CRM enricher** | `crm_enricher.py` | 622 | Correctly identifies participants, classifies internal/external. Today's manifest shows accurate enrichment. |
| **Block selector** | `block_selector.py` | 437 | Smart block selection with recipe system. Today's manifest shows thoughtful conditional reasoning. |
| **Block generator** | `block_generator.py` | 706 | Generates B-blocks via `/zo/ask`. 12 blocks generated successfully today. |
| **HITL module** | `hitl.py` | 383 | Queue system works. 249 items in HITL queue, recent items correctly structured. |
| **Process module** | `process.py` | 539 | Orchestrates block selection + generation. Working end-to-end. |
| **Quality gate** | `quality_gate.py` | 690 | 8 checks implemented, scoring works. Issue is with how results are consumed, not the gate itself. |
| **Title normalizer** | `title_normalizer.py` | 295 | Enriches meeting titles via LLM analysis. Working. |
| **meeting_cli.py** | `meeting_cli.py` | 901 | CLI wrapper. Works but has the gate-bypass issue baked in. |
| **Manifest v3 schema** | — | — | Well-structured, comprehensive. Good foundation. |

### Broken / Needs Redesign

| Component | File | Issue |
|-----------|------|-------|
| **Archive module** | `archive.py` | Target dir (`Personal/Meetings/Week-of-*`) does not exist. No archive folders created yet. No `archived` status written. |
| **Calendar match** | `calendar_match.py` | Consistently returns 0.0 confidence. Every recent manifest shows `"confidence": 0.0`. Either the API integration is broken or the matching logic is too strict. |
| **Pull module** | `pull.py` | Google Drive pull — may work but untested in current pipeline. SKILL.md references it but `tick` doesn't use it. |
| **Gate → processing interlock** | `meeting_cli.py` (tick) | Gate failures are swallowed. No gating checkpoint exists. |
| **Inbox poller** | `inbox_poller.py` | 147 lines. Role unclear — seems to overlap with `tick`'s pre-step. |

### Dead / Deprecated

| Component | Path | Reason |
|-----------|------|--------|
| `N5/scripts/meeting_pipeline/transcript_processor_v4.py` | Deleted | v2 entry point, no longer exists |
| `N5/scripts/meeting_pipeline/m_to_p_transition.py` | Still exists | v2 state transition script with 75+ runtime JSON logs from Dec 2025. Dead code. |
| `N5/scripts/meeting_pipeline/manifest_validator.py` | Still exists | v2 manifest validator. Superseded by v3 `validate_manifest.py`. |
| `N5/data/block_registry.db` | Last written Nov 2024 | Orphaned. Not referenced by v3 code. |
| `N5/data/executables.db` | Last written Nov 2025 | Block generation tool registry. v3 uses block_generator.py directly. |
| `N5/runtime/meeting_pipeline/` | 75+ JSON files | v2 runtime transition logs. Stale since Dec 2025. |

---

## 4. Database Strategy (DP-2)

<!-- SQLite strategy: derivative index vs primary operational store -->

### Current Reality: 4 Databases, No Clear Authority

| DB | Used By | Writes | Last Write |
|----|---------|--------|------------|
| `N5/data/meeting_pipeline.db` | v2 scripts, webhook handlers, recall bots | Yes (webhooks still active) | 2026-03-05 |
| `N5/runtime/meeting_pipeline.db` | v3 block tracking (one meeting only) | Minimal | 2026-01-03 |
| `N5/data/meeting_registry.db` | v3 dedup/stats | Yes | 2026-02-09 |
| Manifest JSON files | v3 pipeline (primary) | Yes | 2026-03-10 |

### Assessment

**The v3 manifest is the de facto primary store.** The manifest.json files contain the richest, most current data — full status history, quality gate results, CRM enrichment, block selection reasoning, participant details. The SQLite databases are secondary indices at best.

**`N5/data/meeting_pipeline.db` is a zombie.** It has 125 permanently stuck meetings, 50 failed meetings, and active webhook tables (Fireflies: 227 rows, Fathom: 20 rows, Recall: 28 bots) that are still being written to. The webhook handlers are inserting data but nothing reads it for pipeline purposes.

**`N5/runtime/meeting_pipeline.db` is nearly orphaned.** Only 16 blocks for 1 meeting (Lensa Partnership, Jan 3). v3 processing doesn't use it for current meetings.

**`N5/data/meeting_registry.db` has 6 entries total.** It was built as a dedup index during the v3 build (Feb 2026) but is barely populated. Today's meeting is NOT in it — registration may not be wired into the pipeline.

### SQLite Strategy Recommendation

**Option A (Recommended): SQLite as derivative index, rebuilt from filesystem truth.**
- The manifest.json files ARE the source of truth
- SQLite should be a queryable index built by scanning `Personal/Meetings/` recursively
- Rebuild on demand: `meeting_cli.py rebuild-index`
- Schema: one unified table mirroring manifest key fields (meeting_id, date, status, type, participants, quality_score, archive_path)
- Drop all v2 tables except webhook receivers (those serve a different function)

**Option B: SQLite as operational primary.**
- Would require migrating all manifest data into SQLite
- Manifests become derivative
- Higher complexity, conflicts with P02 (manifests are currently more complete than any DB)

---

## 5. Filesystem State

### Current Layout

```
Personal/Meetings/
├── Inbox/
│   └── 2026-03-10_Nick-Freund-Vrijen-Attawar_Intro-Chat-via-Pams-Referral/
│       ├── manifest.json (status: complete, 12 blocks generated)
│       ├── transcript.md (55KB)
│       ├── transcript.jsonl (148KB, Fireflies source)
│       ├── metadata.json (1KB)
│       ├── B00_ZO_TAKE_HEED.md
│       ├── B01_DETAILED_RECAP.md
│       ├── ... (12 block files total)
│       └── B32_THOUGHT_PROVOKING_IDEAS.md
└── (no Archive/, no Week-of-* folders)
```

**Key observations:**

1. **Inbox has exactly 1 meeting.** Everything processed before today has been... somewhere. Not in Archive (doesn't exist), not at the Meetings root (0 folders found). Processed meetings may have been manually moved or cleaned up in previous sessions.

2. **No archive infrastructure exists.** The `archive.py` module targets `Week-of-YYYY-MM-DD/internal|external/` but no such directories exist. The v2 reference doc mentions `Personal/Meetings/Archive/YYYY-QN/` — a different structure entirely.

3. **Completed meetings sit in Inbox indefinitely.** Today's meeting has status "complete" but is still in Inbox. There is no automated archive step running.

4. **The "complete" meeting in Inbox hasn't been gated.** Manifest shows `"gated_at": null` — confirming the gate-bypass behavior.

---

## 6. Breakpoints and Failure Modes

### B1: Gate Bypass (High severity)
**What:** Quality gate failures don't prevent block generation. HITL items are queued but never consulted.
**Evidence:** Today's meeting: quality_gate.passed=false, score=0.63, yet 12 blocks generated successfully.
**Impact:** Blocks generated from potentially unreliable input. Calendar mismatch means meeting might be wrongly dated. No host identified means attribution may be wrong.
**Redesign implication:** Gate must be a hard checkpoint. Processing should not proceed without gate pass OR explicit HITL resolution.

### B2: Calendar Match Always Fails (High severity)
**What:** `calendar_match_score` is 0.0 for every recent meeting. Every meeting triggers HITL.
**Evidence:** Last 5 HITL items all show `"calendar_match_score": 0.0`. Today's manifest: `"confidence": 0.0, "method": "none"`.
**Impact:** Calendar data (correct date, duration, attendees from invite) is never incorporated. Pipeline relies entirely on transcript heuristics.
**Redesign implication:** Calendar match integration needs debugging or replacement. May be an API credential issue, a timing window issue, or a matching algorithm that's too strict.

### B3: No Archive Path (Medium severity)
**What:** No archive folders exist. Completed meetings accumulate in Inbox.
**Evidence:** `ls Personal/Meetings/Archive/` returns "No Archive folder". Zero Week-of-* folders.
**Impact:** Inbox will grow indefinitely. No organized historical access.
**Redesign implication:** Archive step needs to be wired and run. Need to decide: Week-of-* (v3 design) vs YYYY-QN/ (v2 design) vs flat (simplest).

### B4: Zombie v2 Database (Medium severity)
**What:** `N5/data/meeting_pipeline.db` has 125 meetings stuck at `queued_for_ai` since Nov 2025.
**Evidence:** `SELECT COUNT(*) FROM meetings WHERE status='queued_for_ai'` returns 125.
**Impact:** These represent real historical meetings (Sep-Nov 2025) that were never fully processed with blocks. They may need reprocessing through the v3 pipeline.
**Redesign implication:** Decide: (a) reprocess through v3, (b) mark as historical and skip, (c) extract transcripts and feed to v3 ingest.

### B5: HITL Queue Grows Without Resolution (Medium severity)
**What:** 249 HITL items, all apparently unresolved.
**Evidence:** `wc -l hitl-queue.jsonl` = 249. Recent items all show `"status": "pending"`.
**Impact:** The queue is effectively a write-only log. No review workflow drives resolution.
**Redesign implication:** HITL needs either (a) integration into a V-facing review surface, or (b) automatic resolution for common cases (e.g., calendar mismatch → skip calendar, proceed anyway).

### B6: Meeting Registry Not Populated (Low severity)
**What:** `meeting_registry.db` has only 6 entries. Today's meeting is not registered.
**Evidence:** DB query returns 6 rows. Last entry: 2026-02-09.
**Impact:** Dedup index is unreliable. Can't query historical meetings via SQL.
**Redesign implication:** Either wire registration into the pipeline or eliminate the registry in favor of filesystem scans.

### B7: Dual DB Schema Confusion (Low severity)
**What:** Two files named `meeting_pipeline.db` at different paths with different schemas.
**Evidence:** `N5/data/meeting_pipeline.db` (11 tables) vs `N5/runtime/meeting_pipeline.db` (1 table).
**Impact:** Any script that references "meeting_pipeline.db" without a full path risks hitting the wrong one.
**Redesign implication:** Consolidate or rename. Runtime DB should be deprecated if manifests are primary.

---

## 7. Webhook / Source Integration State

### Active Webhook Receivers

| Source | Table | Total Rows | Status Breakdown |
|--------|-------|-----------|-----------------|
| Fireflies | `fireflies_webhooks` | 227 | 194 processed, 33 failed |
| Fathom | `fathom_webhooks` | 20 | 20 processed |
| Recall.ai | `recall_bots` | 28 | 28 scheduled |

**These webhook tables live in the v2 database** (`N5/data/meeting_pipeline.db`) but are still being written to (last write: Mar 5). The v3 pipeline's `ingest.py` doesn't read from these tables — it processes files directly from Inbox.

**Gap:** Webhook data (Fireflies transcript IDs, Fathom recording IDs) could provide dedup signals and source metadata, but the v3 pipeline ignores them. The webhook → v3 pipeline handoff is undefined.

---

## 8. Decision Point Analysis

### DP-1: Salvageable vs. Replaceable Components

**Salvageable (keep with fixes):**
- `ingest.py` — Works well. Needs: register meetings in index after ingest.
- `crm_enricher.py` — Works well. No changes needed.
- `block_selector.py` — Smart selection is a strength. Keep.
- `block_generator.py` — Working. Keep.
- `process.py` — Working orchestrator. Keep.
- `quality_gate.py` — Logic is sound. Needs: gate result to actually block progression.
- `hitl.py` — Queue management works. Needs: resolution workflow.
- `title_normalizer.py` — Working. Keep.
- `meeting_cli.py` — Good CLI surface. Needs: gate interlock fix, archive wiring.
- Manifest v3 schema — Comprehensive. Keep as-is.

**Replace/Redesign:**
- `archive.py` — Target structure doesn't exist. Needs redesign with actual directory creation.
- `calendar_match.py` — Consistently returns 0.0. Needs debugging or architectural change.
- `inbox_poller.py` — Overlaps with `tick`. Consolidate or remove.
- `pull.py` — Role unclear in v3. May need replacement with webhook-driven intake.
- All v2 scripts in `N5/scripts/meeting_pipeline/` — Dead code. Remove.

**Drop entirely:**
- `N5/runtime/meeting_pipeline.db` — Orphaned v3 block tracker. Not used.
- `N5/data/block_registry.db` — Orphaned. Not referenced by v3.
- `N5/data/executables.db` — Orphaned block tool registry.
- `backfill_inbox.py` — One-time migration utility.
- `manifest_converter.py` — v2→v3 migration. One-time use.
- `stage.py` — v2 legacy staging.
- `normalize_inbox.py` — Overlaps with ingest.
- `processor.py` — Legacy v2 processor (different from `process.py`).

### DP-2: SQLite Role

**Recommendation: Derivative index (Option A).**

Evidence supporting this:
1. Manifests contain richer data than any DB table
2. The v3 pipeline already treats manifests as primary (reads/writes manifest.json in every step)
3. Three of four SQLite DBs are stale or orphaned
4. Filesystem → DB rebuild is straightforward (scan folders, read manifests, insert)

The webhook tables (Fireflies, Fathom, Recall) should be preserved in a separate `webhooks.db` since they serve an intake function independent of pipeline state.

---

## 9. Redesign Implications Summary

### Must Fix (blocking normal operation)
1. **Gate interlock** — Gate must be a hard checkpoint before block generation
2. **Calendar match** — Debug why confidence is always 0.0
3. **Archive step** — Create target directories and wire into pipeline

### Should Fix (for reliability)
4. **HITL resolution workflow** — Either auto-resolve common cases or expose to V
5. **Meeting registry population** — Wire into ingest or eliminate
6. **DB consolidation** — Merge/rename/drop to one pipeline DB + one webhook DB
7. **v2 backlog decision** — 125 queued meetings need a fate

### Can Defer
8. **Webhook → v3 handoff** — Currently works via file-based Inbox, adequate for now
9. **Dead code cleanup** — v2 scripts, orphaned DBs
10. **Process-all parallelism** — Works but untested at scale

---

## 10. Current Pipeline Health (as of 2026-03-10)

| Metric | Value | Assessment |
|--------|-------|------------|
| v3 pipeline functional | Yes | Ingest → identify → process works end-to-end |
| Gate enforced | No | Gate runs but doesn't block |
| Calendar integration | Broken | Always returns 0.0 confidence |
| Archive functioning | No | No archive folders exist |
| HITL queue | Write-only | 249 pending items, no resolution flow |
| v2 database | Zombie | 125 stuck meetings, webhook tables still active |
| Meeting registry | Minimal | 6 of ~250+ meetings registered |
| Today's processing | Successful | 12 blocks generated for Nick Freund meeting |
