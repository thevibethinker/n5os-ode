---
created: 2026-03-10
last_edited: 2026-03-10
version: 1.0
provenance: meeting-system-recovery-redesign/D3.1
drop_id: D3.1
build_slug: meeting-system-recovery-redesign
---

# Execution Plan

**Status:** Awaiting V approval before any mutation  
**Scope:** Historical corpus restore, pipeline redesign, SQLite synchronization, skill creation, and future-source readiness

---

## Approval Gate

**⛔ NO PHASE BELOW EXECUTES UNTIL V REVIEWS THIS DOCUMENT AND GIVES EXPLICIT APPROVAL.**

Once approved, each phase has its own internal go/no-go checkpoint. V can approve all phases at once or approve them incrementally. Phase ordering is strict — later phases depend on earlier phase outputs.

---

## Execution phases

| Phase | Name | Mutates Filesystem? | Mutates SQLite? | Reversible? |
|-------|------|--------------------:|----------------:|------------:|
| 0 | Pre-flight validation | No | No | N/A |
| 1 | Historical corpus restore | Yes | No | Yes (delete restored folders) |
| 2 | SQLite synchronization | Yes | Yes | Yes (backup before write) |
| 3 | Skill creation + pipeline redesign | Yes | No | Yes (delete new skill dir) |
| 4 | Pipeline gate + archive wiring | Yes (code) | No | Yes (revert to meeting-ingestion) |
| 5 | Future-source adapter activation | Yes (code) | No | Yes (disable adapters) |
| 6 | Knowledge elevation wiring | Yes (code) | No | Yes (remove elevation scripts) |
| 7 | Export guardrail validation | No | No | N/A |

---

## Phase 0: Pre-flight Validation

**Purpose:** Confirm all inputs exist and the environment is ready before any mutation.

**Actions:**

1. Verify zip archive exists and is readable:
   ```bash
   ls -la "/home/.z/chat-uploads/Zo Meetings copy-e49d20a9b948.zip"
   ```

2. Verify `Personal/Meetings/Inbox/` exists:
   ```bash
   ls -d Personal/Meetings/Inbox/
   ```

3. Verify current live meeting (Nick Freund) is safe — it must not be overwritten by restore:
   ```bash
   ls Personal/Meetings/Inbox/2026-03-10_Nick-Freund-Vrijen-Attawar_Intro-Chat-via-Pams-Referral/manifest.json
   ```

4. Snapshot current filesystem state for rollback reference:
   ```bash
   find Personal/Meetings/ -type f | sort > /tmp/meetings-pre-restore-snapshot.txt
   ```

5. Verify build artifacts are all present (all 6 dependency specs):
   ```bash
   ls N5/builds/meeting-system-recovery-redesign/artifacts/{restore-map,system-audit,knowledge-audit,intake-contract,routing-and-titling-rules,skill-packaging-and-export-policy}.md
   ```

6. Check disk space (zip is ~50MB, expanded corpus is ~200MB estimated):
   ```bash
   df -h /home/workspace
   ```

**Checkpoint:** All 6 checks pass → proceed. Any failure → stop, report, resolve.

**Rollback:** N/A (no mutations).

---

## Phase 1: Historical Corpus Restore

**Purpose:** Extract meeting content from the zip archive, normalize it into the canonical `Personal/Meetings/` layout with provenance metadata, and stage quarantine items separately.

### Decision: DP-1 — Restore approach

**Resolution: Restore directly into canonical layout with provenance, NOT byte-for-byte replay of zip structure.**

Rationale (from restore-map.md):
- The zip contains at least four distinct state families (Inbox, Week-of, Archive, quarantine) with incompatible naming conventions
- The canonical target is `Personal/Meetings/` with manifest-v3 schema, not the historical `Week-of-*` layout
- Restoring the old layout would import dead infrastructure (filesystem state suffixes, quarter buckets) that the redesign explicitly removes
- Provenance fields in each recovered manifest preserve full lineage back to the zip

### Phase 1 steps

**Step 1.1: Extract zip to a temporary staging area (non-destructive)**

```bash
mkdir -p /tmp/meeting-recovery-staging
unzip -o "/home/.z/chat-uploads/Zo Meetings copy-e49d20a9b948.zip" -d /tmp/meeting-recovery-staging/
```

Verification:
```bash
find /tmp/meeting-recovery-staging -type d | head -20
```

**Step 1.2: Run recovery adapter over processed week-folder and archive content**

For each processed meeting folder in the zip (week-folder and archive families), apply the `recovery_v1` adapter as specified in the intake contract (§6.4):

1. Locate transcript file
2. If processed blocks exist (B01, B03, etc.) — preserve them (completed work)
3. Read historical manifest if present, extract usable fields
4. Infer `source.type` from evidence (Fireflies JSONL → fireflies, Fathom format → fathom, otherwise → manual)
5. Strip historical state suffixes (`_[P]`, `_[M]`, `_[C]`)
6. Generate manifest-v3 with `source.adapter: "recovery_v1"` and full provenance block
7. Set status based on existing processed state:
   - Has generated blocks → `"processed"` (skip re-processing)
   - Has transcript only → `"ingested"` (needs full pipeline)
   - Has identification data but no blocks → `"identified"` (needs gate + process)
8. Place into `Personal/Meetings/Inbox/<normalized-meeting-id>/` (processed items go to archive target, see Step 1.4)

**Deduplication rule:** When the same meeting exists in multiple zip families (week + archive + inbox), prefer the richest source — the one with the most generated blocks and complete manifest. Rank: complete processed week/archive folder > partial processed folder > Inbox transcript-only item.

**Step 1.3: Stage quarantine items separately**

Quarantine items from the zip do NOT enter the canonical corpus. They are restored to:
```
N5/builds/meeting-system-recovery-redesign/recovery-quarantine/
```

Each quarantine item gets a recovery manifest noting its original zip path and quarantine reason (if detectable). These items require V's per-item adjudication before any promotion to the canonical corpus.

**Step 1.4: Place recovered items**

| Recovery status | Target location |
|----------------|-----------------|
| `"processed"` or `"complete"` (has blocks) | `Personal/Meetings/Week-of-YYYY-MM-DD/external/` or `internal/` (create Week-of dirs as needed) |
| `"ingested"` (transcript only, needs pipeline) | `Personal/Meetings/Inbox/` |
| `"identified"` (partial pipeline) | `Personal/Meetings/Inbox/` |
| Quarantine | `N5/builds/meeting-system-recovery-redesign/recovery-quarantine/` |
| Raw Inbox-only (no richer processed version exists) | `Personal/Meetings/Inbox/` (marked for pipeline run) |

**Step 1.5: Clean up staging**

```bash
rm -rf /tmp/meeting-recovery-staging
```

### Phase 1 verification

```bash
# Count restored meetings
find Personal/Meetings/ -name "manifest.json" | wc -l

# Verify provenance on recovered items
grep -r "recovery_v1" Personal/Meetings/ --include="manifest.json" | wc -l

# Verify no state suffixes in folder names
find Personal/Meetings/ -type d -name "*_\[*" | wc -l  # should be 0

# Verify quarantine staging
ls N5/builds/meeting-system-recovery-redesign/recovery-quarantine/ | wc -l

# Verify live meeting was not overwritten
cat Personal/Meetings/Inbox/2026-03-10_Nick-Freund-Vrijen-Attawar_Intro-Chat-via-Pams-Referral/manifest.json | python3 -c "import json,sys; m=json.load(sys.stdin); print('OK' if m.get('source',{}).get('type')=='fireflies' else 'OVERWRITTEN')"
```

### Phase 1 rollback

If restore produces bad state:
1. Delete all folders in `Personal/Meetings/` that have `"source.adapter": "recovery_v1"` in their manifest
2. Delete `Personal/Meetings/Week-of-*` directories that were created during restore (check creation timestamps)
3. Verify the pre-restore snapshot matches post-rollback state

### Phase 1 risks

- **Risk:** Duplicate meetings across families. **Mitigation:** Dedup by meeting identity (date + participants), not filename.
- **Risk:** Metadata richness varies. **Mitigation:** Recovery adapter tolerates both manifest-rich and transcript-only items.
- **Risk:** State suffixes encode workflow history. **Mitigation:** Strip suffixes, preserve in provenance.
- **Risk:** Archive may have better copies than week folders. **Mitigation:** Compare source families before choosing recovery winner.

### Phase 1 unresolved questions for V

1. **Quarantine review:** ~45 quarantine items contain real meeting content. Should V review them individually, or should they stay parked indefinitely?
2. **v2 backlog:** 125 meetings stuck at `queued_for_ai` in the v2 database (Sep–Nov 2025). Some may overlap with zip content. After zip restore, should remaining non-overlapping items be extracted as transcripts and fed to the v3 pipeline?
3. **Inbox-only items:** The zip contains ~281 raw Inbox items. Some have no richer processed counterpart. Should these all enter the pipeline, or only items from dates where no processed meeting exists?

---

## Phase 2: SQLite synchronization

**Purpose:** Bring SQLite databases into alignment with the recovered filesystem state.

### Decision: DP-1 (from brief) — Rebuild vs restore-and-reconcile

**Resolution: Rebuild the derivative index from filesystem truth. Do NOT attempt to patch the existing databases.**

Rationale (from system-audit.md §4):
- The v3 manifest is the de facto primary store — manifests contain richer data than any DB table
- Three of four SQLite DBs are stale or orphaned
- `meeting_registry.db` has only 6 entries out of ~250+ meetings
- Filesystem → DB rebuild is straightforward (scan folders, read manifests, insert)
- Patching the existing databases would require reconciling incompatible schemas (v2 11-table vs v3 1-table) and risk introducing inconsistencies

### Phase 2 steps

**Step 2.1: Backup all existing SQLite databases**

```bash
mkdir -p N5/data/sqlite-backups/pre-recovery-$(date +%Y%m%d)
cp N5/data/meeting_pipeline.db "N5/data/sqlite-backups/pre-recovery-$(date +%Y%m%d)/meeting_pipeline.db"
cp N5/data/meeting_registry.db "N5/data/sqlite-backups/pre-recovery-$(date +%Y%m%d)/meeting_registry.db"
cp N5/runtime/meeting_pipeline.db "N5/data/sqlite-backups/pre-recovery-$(date +%Y%m%d)/runtime_meeting_pipeline.db" 2>/dev/null || true
```

**Step 2.2: Rebuild the derivative meeting index**

Create a new unified `meeting_index.db` by scanning `Personal/Meetings/` recursively:

1. For each `manifest.json` found, extract key fields: `meeting_id`, `date`, `status`, `content_type`, `meeting.type`, participants (identified names), `quality_gate.score`, `source.type`, `source.adapter`, archive path
2. Insert into a single `meetings` table in the new index
3. Create secondary indices on `date`, `status`, `content_type`

Schema for the rebuilt index:
```sql
CREATE TABLE meetings (
    meeting_id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    content_type TEXT NOT NULL,
    meeting_type TEXT,
    title TEXT,
    participants TEXT,  -- JSON array of identified names
    quality_score REAL,
    source_type TEXT,
    source_adapter TEXT,
    block_count INTEGER,
    archive_path TEXT,
    manifest_path TEXT NOT NULL,
    recovered BOOLEAN DEFAULT FALSE,
    indexed_at TEXT NOT NULL
);

CREATE INDEX idx_meetings_date ON meetings(date);
CREATE INDEX idx_meetings_status ON meetings(status);
CREATE INDEX idx_meetings_content_type ON meetings(content_type);
```

**Step 2.3: Preserve webhook tables**

The webhook tables (Fireflies: 227 rows, Fathom: 20 rows, Recall: 28 bots) in `N5/data/meeting_pipeline.db` serve an intake function independent of pipeline state. These should be preserved in a separate `webhooks.db`:

```bash
# Extract webhook tables to a new DB
sqlite3 N5/data/meeting_pipeline.db ".dump fireflies_webhooks" | sqlite3 N5/data/webhooks.db
sqlite3 N5/data/meeting_pipeline.db ".dump fathom_webhooks" | sqlite3 N5/data/webhooks.db
sqlite3 N5/data/meeting_pipeline.db ".dump recall_bots" | sqlite3 N5/data/webhooks.db
```

**Step 2.4: Deprecate stale databases**

After rebuild and webhook extraction:
- `N5/data/meeting_pipeline.db` → rename to `N5/data/sqlite-backups/meeting_pipeline_v2_deprecated.db`
- `N5/runtime/meeting_pipeline.db` → rename to `N5/data/sqlite-backups/runtime_meeting_pipeline_deprecated.db`
- `N5/data/block_registry.db` → rename to `N5/data/sqlite-backups/block_registry_deprecated.db`
- `N5/data/executables.db` → rename to `N5/data/sqlite-backups/executables_deprecated.db`
- `N5/data/meeting_registry.db` → replaced by the new `meeting_index.db`

**Step 2.5: Create refreshed SQLite backup**

```bash
cp N5/data/meeting_index.db "N5/data/sqlite-backups/meeting_index_post_recovery_$(date +%Y%m%d).db"
cp N5/data/webhooks.db "N5/data/sqlite-backups/webhooks_post_recovery_$(date +%Y%m%d).db"
```

### SQLite synchronization verification

```bash
# Count meetings in rebuilt index
sqlite3 N5/data/meeting_index.db "SELECT COUNT(*) FROM meetings"

# Count recovered items specifically
sqlite3 N5/data/meeting_index.db "SELECT COUNT(*) FROM meetings WHERE recovered = 1"

# Verify date coverage matches restore-map expectations
sqlite3 N5/data/meeting_index.db "SELECT MIN(date), MAX(date) FROM meetings"

# Verify webhook tables preserved
sqlite3 N5/data/webhooks.db "SELECT COUNT(*) FROM fireflies_webhooks"
sqlite3 N5/data/webhooks.db "SELECT COUNT(*) FROM fathom_webhooks"
```

### Phase 2 rollback

1. Delete `N5/data/meeting_index.db` and `N5/data/webhooks.db`
2. Restore original databases from `N5/data/sqlite-backups/pre-recovery-*/`
3. Rename deprecated files back to their original locations

---

## Phase 3: Skill creation + pipeline redesign

**Purpose:** Create the `Skills/meeting-system/` skill directory with redesigned scripts, references, fixtures, and tooling.

### Decision: DP-3 (from brief) — Skill creation timing

**Resolution: Create the skill scaffolding BEFORE live code changes, then populate it during implementation phases.**

Rationale:
- The skill directory structure needs to exist before modified scripts can be placed there
- Bootstrap and export tooling should be created early so they can validate their own environment as subsequent phases add infrastructure
- Creating the skill in parallel with implementation phases would require tracking two moving targets
- Creating after all implementation is done risks treating skill packaging as an afterthought (anti-pattern called out in the brief)

### Skill creation sequence

**Step 3.1: Create skill directory structure**

Confirm slug with V first. Recommended: `meeting-system` (per skill-packaging-and-export-policy.md §1).

```
Skills/meeting-system/
├── SKILL.md
├── .n5protected
├── .n5exportable
├── .export-allowlist
├── scripts/
├── references/
└── assets/
    └── fixtures/
```

**Step 3.2: Migrate salvageable scripts from `meeting-ingestion`**

Per system-audit.md §8 DP-1, copy and begin modifying:

| Script | Action |
|--------|--------|
| `meeting_cli.py` | Copy → modify (gate interlock, reflection routing, elevation command) |
| `ingest.py` | Copy → modify (add classification heuristic, Fathom/Pocket support) |
| `crm_enricher.py` | Copy → minimal changes |
| `block_selector.py` | Copy → add `reflection_standard` recipe |
| `block_generator.py` | Copy → minimal changes |
| `process.py` | Copy → enforce gate checkpoint |
| `quality_gate.py` | Copy → gate result blocks progression, reflection profile |
| `hitl.py` | Copy → auto-resolution for common cases |
| `title_normalizer.py` | Copy → implement title hierarchy from D2.2 |
| `archive.py` | Copy → redesign (create dirs, write `archived` status, reflection path) |
| `calendar_match.py` | Copy → debug/fix 0.0 confidence issue |
| `validate_manifest.py` | Copy → minimal changes |

**Step 3.3: Create new scripts**

| Script | Purpose |
|--------|---------|
| `classifier.py` | Meeting vs. reflection classification module (D2.2 §1.2) |
| `move_ready.py` | Move-ready verification engine (D2.2 §4.3-4.4) |
| `reflect.py` | Reflection pipeline processing |
| `elevate.py` | Post-archive knowledge elevation/routing |
| `rebuild_index.py` | Derivative SQLite index rebuild from filesystem |
| `bootstrap.py` | Environment setup — check/setup commands |
| `export_skill.py` | Allowlist-driven export tool |

**Step 3.4: Populate references**

Copy and update reference docs from `meeting-ingestion/references/` plus new specs:
- `manifest-v3.schema.json`
- `meeting-id-convention.md`
- `block-picker-v2-policy.md`
- `quality-harness-checks.md`
- `hitl-queue-spec.md`
- `quality-gate-docs.md`
- `block-quality-thresholds.md`
- `intake-contract.md` (from D2.1 artifact, sanitized)
- `routing-and-titling-rules.md` (from D2.2 artifact, sanitized)
- `reflection-pipeline.md` (new)

**Step 3.5: Create sanitized fixtures**

Create synthetic example files in `assets/fixtures/`:
- `example-manifest.json` — synthetic participants ("Alice", "Bob"), fake dates (2099-01-15)
- `example-block-B01.md` — fictional meeting recap
- `example-hitl-item.json` — synthetic escalation

**Step 3.6: Create markers and allowlist**

- `.n5protected` — workspace protection
- `.n5exportable` — `{"exportable": true, "export_version": "1.0", "created": "YYYY-MM-DD", "allowlist": ".export-allowlist"}`
- `.export-allowlist` — per skill-packaging-and-export-policy.md §3.2

**Step 3.7: Write SKILL.md**

Comprehensive documentation covering: purpose, invocation, system dependencies, content types, pipeline stages, block recipes, CLI commands, bootstrap, export.

### Skill creation verification

```bash
# Verify directory structure
ls Skills/meeting-system/{SKILL.md,.n5protected,.n5exportable,.export-allowlist}

# Verify scripts exist
ls Skills/meeting-system/scripts/{meeting_cli,ingest,crm_enricher,block_selector,block_generator,process,quality_gate,hitl,title_normalizer,archive,calendar_match,validate_manifest,classifier,move_ready,reflect,elevate,rebuild_index,bootstrap,export_skill}.py

# Verify references
ls Skills/meeting-system/references/

# Verify fixtures
ls Skills/meeting-system/assets/fixtures/

# Run bootstrap check
python3 Skills/meeting-system/scripts/bootstrap.py check
```

### Phase 3 rollback

1. Delete `Skills/meeting-system/` entirely
2. `Skills/meeting-ingestion/` remains untouched as the running production system

### Phase 3 unresolved questions for V

1. **Skill slug confirmation:** Recommended `meeting-system`. V should confirm before directory creation.
2. **meeting-ingestion archive timing:** When should the old skill be moved to `Skills/.backups/meeting-ingestion.<timestamp>/`? Recommend: after Phase 4 validation, not during Phase 3.

---

## Phase 4: Pipeline Gate + Archive Wiring

**Purpose:** Fix the two most critical pipeline breakpoints: the gate bypass (B1) and the missing archive infrastructure (B3).

### Step 4.1: Fix gate interlock

Modify `meeting_cli.py` `tick` command so that:
- Quality gate is a **hard checkpoint** before block generation
- Critical gate failures (participant_confidence < 0.5, encoding corruption) block processing entirely
- Non-critical gate failures (calendar_match 0.0 — currently broken system-wide) proceed with a warning
- Gate results write `"gated_at"` timestamp to manifest regardless of pass/fail

Verification:
```bash
# Process a test meeting through the pipeline, verify gate blocks on critical failure
python3 Skills/meeting-system/scripts/meeting_cli.py tick --dry-run
```

### Step 4.2: Wire archive infrastructure

Modify `archive.py` to:
- Create `Week-of-YYYY-MM-DD` directories as needed
- Create `external/`, `internal/`, `reflections/` subdirectories
- Update manifest with `status: "archived"` and `archived_at` timestamp
- Support `--dry-run` flag

### Step 4.3: Wire move-ready verification

Add `check-move-ready` command to CLI:
```bash
python3 Skills/meeting-system/scripts/meeting_cli.py check-move-ready <meeting-folder>
python3 Skills/meeting-system/scripts/meeting_cli.py check-move-ready --all
```

### Step 4.4: Run pipeline on recovered Inbox items

For meetings recovered in Phase 1 that landed in Inbox with status `"ingested"`:
- Run the full pipeline: identify → gate → process → check-move-ready → archive
- Use `--dry-run` first to preview

### Phase 4 verification

```bash
# Verify gate is enforced
grep -n "gated_at" Personal/Meetings/Inbox/*/manifest.json | head -5

# Verify archive directories were created
find Personal/Meetings -type d -name "Week-of-*" | sort

# Verify archived meetings have correct status
grep -r '"archived"' Personal/Meetings/Week-of-*/*/manifest.json | wc -l

# Verify move-ready works
python3 Skills/meeting-system/scripts/meeting_cli.py check-move-ready --all
```

### Phase 4 rollback

1. Revert `Skills/meeting-system/scripts/` to Phase 3 state (pre-modification)
2. Alternatively, fall back to `Skills/meeting-ingestion/` as the production pipeline

---

## Phase 5: Future-Source Adapter Activation

**Purpose:** Enable Fathom and Pocket intake adapters so new content from those sources can enter the normalized pipeline.

### Decision: DP-2 (from brief) — Backfill timing

**Resolution: Activate new adapters AFTER intake redesign is in place and validated, NOT before.**

Rationale:
- The intake contract (D2.1) defines the canonical landing shape that all sources must produce
- Enabling adapters before the contract is validated would allow non-conforming content into the pipeline
- Fireflies adapter already works (v3 pipeline uses it today); Fathom and Pocket need new adapters
- Historical Fireflies backfill from webhooks can also be addressed here, but only after the pipeline changes from Phase 4 are stable

### Phase 5 steps

**Step 5.1: Implement Fathom adapter (`fathom_v1`)**

Per intake-contract.md §6.2. Test with sample Fathom output.

**Step 5.2: Implement Pocket adapter (`pocket_v1`)**

Per intake-contract.md §6.3. Includes meeting/reflection signal detection.

**Step 5.3: Implement classification module**

Per routing-and-titling-rules.md §1.2. The `classifier.py` module performs the two-pass classification (deterministic + LLM fallback).

**Step 5.4: Implement reflection block recipe**

Per routing-and-titling-rules.md §3.2. Register `reflection_standard` recipe in block selector.

**Step 5.5: Test end-to-end with each source type**

```bash
# Test Fathom intake
python3 Skills/meeting-system/scripts/meeting_cli.py ingest --source fathom --path /tmp/test-fathom-transcript.md --dry-run

# Test Pocket intake (should classify as reflection)
python3 Skills/meeting-system/scripts/meeting_cli.py ingest --source pocket --path /tmp/test-pocket-note.md --dry-run

# Test Pocket with multi-speaker (should classify as meeting)
python3 Skills/meeting-system/scripts/meeting_cli.py ingest --source pocket --path /tmp/test-pocket-multiparty.md --dry-run
```

**Step 5.6: Fireflies webhook backfill (optional, V's call)**

The v2 database has 227 Fireflies webhook entries (194 processed, 33 failed). If V wants to backfill the failed ones through the redesigned pipeline:
1. Extract transcript IDs from `webhooks.db`
2. Pull corresponding transcripts via Fireflies API
3. Feed through `fireflies_v1` adapter into Inbox
4. Process through pipeline

This is optional and can be deferred.

### Phase 5 verification

```bash
# Verify all adapter types have manifests with correct source.adapter field
grep -r '"adapter"' Personal/Meetings/Inbox/*/manifest.json | sort -u

# Verify reflection classification
grep -r '"reflection"' Personal/Meetings/Inbox/*/manifest.json | wc -l

# Verify Fathom items are processable
python3 Skills/meeting-system/scripts/meeting_cli.py status --source fathom
```

### Phase 5 rollback

1. Remove or disable Fathom/Pocket adapter functions in `ingest.py`
2. Remove `classifier.py` and `reflect.py`
3. Pipeline falls back to Fireflies-only intake (current behavior)

---

## Phase 6: Knowledge Elevation Wiring

**Purpose:** Create the post-archive stage that routes high-signal intelligence blocks to downstream knowledge destinations.

### Phase 6 steps

**Step 6.1: Create `elevate.py` post-archive module**

Per knowledge-audit.md RI-1, this module:
- Runs after a meeting is archived
- Scores blocks for signal quality (Zone 2: LLM + structured output)
- Routes high-signal blocks to destinations based on deterministic rules

**Step 6.2: Wire initial elevation targets**

| Target | Routing Rule | Zone |
|--------|-------------|------|
| Position candidates | B32 blocks with novelty > threshold → position extraction | Zone 2 (existing `b32_position_extractor.py`) |
| Content Library | Tier A blocks (score > 80) → content library ingest | Zone 3 (deterministic) |
| CRM update queue | B08 blocks with participant confidence > 0.7 → CRM update candidates | Zone 3 (rule-based routing), Zone 2 (content synthesis) |

**Step 6.3: Wire `elevate` into pipeline CLI**

```bash
python3 Skills/meeting-system/scripts/meeting_cli.py elevate <meeting-folder>
python3 Skills/meeting-system/scripts/meeting_cli.py elevate --all-archived
```

**Note:** This phase is the lightest-touch version. The full relationship-intelligence-os promotion gate and brain.db edge creation are deferred to a future build. This phase creates the elevation hook and the simplest useful routing.

### Phase 6 verification

```bash
# Verify elevation ran
grep -r '"elevated_at"' Personal/Meetings/Week-of-*/*/manifest.json | head -5

# Verify position candidates were generated
wc -l N5/data/position_candidates.jsonl
```

### Phase 6 rollback

1. Remove `elevate.py` from skill
2. Remove `elevate` command from CLI
3. Knowledge pipeline reverts to current state (no post-archive processing)

---

## Phase 7: Export Guardrail Validation

**Purpose:** Validate that the skill is export-safe before it could ever be shared.

### Phase 7 steps

**Step 7.1: Run export dry-run**

```bash
python3 Skills/meeting-system/scripts/export_skill.py --dry-run
```

Verify:
- Only allowlisted files appear in the manifest
- No real meeting data, transcripts, or PII in any exported file
- No workspace-private paths leaked into fixtures
- `.n5exportable` marker present
- `.export-allowlist` enforced

**Step 7.2: Run fixture validation**

Per skill-packaging-and-export-policy.md §8.2:
- Scan `assets/fixtures/` for real workspace paths
- Cross-check against CRM names
- Verify all participant names are synthetic

**Step 7.3: Run full export and inspect**

```bash
python3 Skills/meeting-system/scripts/export_skill.py --output /tmp/meeting-system-export/ --format dir
ls -la /tmp/meeting-system-export/
cat /tmp/meeting-system-export/MANIFEST.txt
```

### Phase 7 verification

```bash
# Verify no PII in export
grep -ri "Personal/" /tmp/meeting-system-export/ || echo "Clean: no Personal/ references"
grep -ri "@" /tmp/meeting-system-export/assets/ || echo "Clean: no emails in fixtures"

# Verify MANIFEST.txt exists with checksums
head -20 /tmp/meeting-system-export/MANIFEST.txt
```

### Phase 7 rollback

N/A (no mutations — this phase is validation only).

---

## Post-Execution: Cleanup and Handoff

After all phases complete:

1. **Archive `meeting-ingestion`:**
   ```bash
   mv Skills/meeting-ingestion "Skills/.backups/meeting-ingestion.$(date +%Y%m%d_%H%M%S)"
   ```

2. **Update scheduled agents** to point to `Skills/meeting-system/` instead of `Skills/meeting-ingestion/`

3. **Run bootstrap check** to confirm environment is fully wired:
   ```bash
   python3 Skills/meeting-system/scripts/bootstrap.py check
   ```

4. **Rebuild index** to capture final state:
   ```bash
   python3 Skills/meeting-system/scripts/rebuild_index.py
   ```

5. **Generate final build deposit** with artifact inventory and completion metrics

---

## Trap-Door Questions Requiring V Approval Before Mutation

These are unresolved decisions that could materially affect execution. Each must be answered before the relevant phase begins.

| # | Question | Affects Phase | Options | Recommendation |
|---|----------|--------------|---------|----------------|
| T1 | Skill slug: `meeting-system` or something else? | Phase 3 | Any valid slug | `meeting-system` |
| T2 | Quarantine items: review individually, park indefinitely, or bulk-discard? | Phase 1 | 3 | Park indefinitely in build staging, review later |
| T3 | v2 backlog (125 queued meetings): reprocess, skip, or extract+reprocess? | Phase 1 | 3 | After Phase 1, check overlap with zip. Remaining non-overlapping items → extract transcripts → feed to v3 pipeline |
| T4 | Inbox-only zip items: all enter pipeline, or only gap-fill? | Phase 1 | 2 | Gap-fill only — enter pipeline only when no richer processed version exists for that date |
| T5 | Fireflies webhook backfill (33 failed): reprocess through redesigned pipeline? | Phase 5 | Yes/No/Defer | Defer to after Phase 5 validation |
| T6 | Calendar match debugging: invest time fixing the 0.0 confidence issue, or defer? | Phase 4 | Fix/Defer | Defer — the system works without calendar match (quality gate allows non-critical failure) |
| T7 | Knowledge elevation scope: minimal routing (Phase 6 as written) or full relationship-intelligence-os absorption? | Phase 6 | Minimal/Full | Minimal for this build, full in a follow-up build |

---

## Execution Timeline Estimate

| Phase | Estimated Effort | Dependencies |
|-------|-----------------|--------------|
| Phase 0 | 5 minutes | None |
| Phase 1 | 2-3 hours (script development + execution) | Phase 0 |
| Phase 2 | 30-60 minutes | Phase 1 |
| Phase 3 | 3-4 hours (scaffolding + migration + new scripts) | Phase 1 (for recovery adapter context) |
| Phase 4 | 2-3 hours | Phase 3 |
| Phase 5 | 2-3 hours | Phase 4 |
| Phase 6 | 1-2 hours | Phase 4 |
| Phase 7 | 15-30 minutes | Phase 3 |

Phases 3 and 2 can run in parallel (different targets). Phases 5 and 6 can also run in parallel (independent code).

---

## Principles Compliance

| Principle | How This Plan Complies |
|-----------|----------------------|
| P05 Safety, Anti-Overwrite | Every phase has explicit rollback. All SQLite DBs backed up before mutation. No overwrites of live data. |
| P24 Simulation Over Doing | Approval gate before any execution. `--dry-run` on all mutating commands. |
| P35 Version, Don't Overwrite | Zip and existing DBs treated as immutable inputs. Recovery creates NEW manifests, doesn't patch old ones. |
| P36 Make State Visible | Each phase declares inputs, outputs, verification commands. Status visible at every checkpoint. |
| P37 Design as Pipelines | Clear stage progression: extract → normalize → place → index → wire → validate. |
| P38 Isolate & Parallelize | Phases 2+3 can run in parallel. Phases 5+6 can run in parallel. Each phase is independently reversible. |
| P39 Audit Everything | Provenance on every recovered item. MANIFEST.txt with checksums on export. Verification commands at every stage. |
