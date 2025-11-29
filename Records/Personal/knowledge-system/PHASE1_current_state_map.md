---
created: 2025-11-28
last_edited: 2025-11-28
version: 1.0
---

# Phase 1 – Current-State Knowledge System Map

## 1. Folder Map (Today)

### 1.1 `Personal/Knowledge/`

Top-level structure:
- `Personal/Knowledge/Canon/`
  - **Purpose:** Human-facing canon: long-form essays and core narrative artifacts.
  - Examples:
    - `Personal/Knowledge/Canon/VibeThinker/The_Architecture_Context_Flow_Post_3_FINAL.md`
    - `Personal/Knowledge/Canon/Vrijen/ai_experience_gap_article_v_voice.md`
  - **Role today:** Primary home for finalized, public-facing writing.

- `Personal/Knowledge/ContentLibrary/`
  - **Purpose:** Local content library service (articles + search/indexing tooling).
  - Contents:
    - Human content: `Personal/Knowledge/ContentLibrary/content/article_career-transitions-a-practical-guide_5bff37d8.md`
    - System assets:
      - `content-library.db`, `content-library.json`, `settings.json`
      - Python tooling: `scripts/content_to_knowledge.py`, `scripts/ingest.py`, `scripts/enhance.py`, `scripts/summarize.py`
  - **Role today:** Hybrid "knowledge app" that ingests and enhances articles and exposes them via a local CLI/API.

- `Personal/Knowledge/Frameworks/`
  - **Purpose:** Strategic and conceptual frameworks.
  - Example: `Personal/Knowledge/Frameworks/careerspan_strategic_frameworks.md`.
  - **Role today:** Small but clearly knowledge-facing; referenced in strategy work.

- `Personal/Knowledge/Legacy_Inbox/`
  - **Purpose:** Dense, legacy-but-still-live knowledge universe moved out of `Knowledge/`.
  - Key subtrees (representative, not exhaustive):
    - **Company canon:**
      - `Personal/Knowledge/Legacy_Inbox/stable/company/{history,overview,positioning,pricing,principles,strategy}.md`
      - `Personal/Knowledge/Legacy_Inbox/stable/careerspan-timeline.md`
      - `Personal/Knowledge/Legacy_Inbox/stable/glossary.md`
    - **Semi-stable state:**
      - `Personal/Knowledge/Legacy_Inbox/semi_stable/{current_metrics,positioning_current,product_current,team_current}.md`
    - **CRM (legacy/parallel to Knowledge/crm):**
      - `Personal/Knowledge/Legacy_Inbox/crm/crm.db`
      - `Personal/Knowledge/Legacy_Inbox/crm/individuals/*.md` (large set of profiles)
      - `events/index.jsonl`, `follow-ups/`, `organizations/quantum-labs.md`
    - **Market & GTM intelligence:**
      - `Personal/Knowledge/Legacy_Inbox/market/*.md`
      - `Personal/Knowledge/Legacy_Inbox/market_intelligence/*` including `gtm_intelligence.db`
      - `Personal/Knowledge/Legacy_Inbox/market-intelligence/meeting_registry.jsonl`
    - **Patterns & hypotheses:**
      - `Personal/Knowledge/Legacy_Inbox/patterns/*.md`
      - `Personal/Knowledge/Legacy_Inbox/hypotheses/*.md`
    - **Personal brand & social content:**
      - `Personal/Knowledge/Legacy_Inbox/personal-brand/social-content/**` (LinkedIn/Twitter post system)
    - **Systems & infrastructure docs:**
      - `Personal/Knowledge/Legacy_Inbox/systems/{content-library-integration.md,debug-logging.md}`
      - `Personal/Knowledge/Legacy_Inbox/infrastructure/syncthing-setup.md`
    - **Reasoning patterns:**
      - `Personal/Knowledge/Legacy_Inbox/reasoning-patterns/*.md`
  - **Role today:** De-facto home for most of the old `Knowledge/` tree (stable, semi_stable, market_intelligence, CRM, patterns, etc.). Acts as both live canon and historical dump, with many files still referenced by N5 docs and workflows.

- `Personal/Knowledge/Logs/`
  - Currently empty directory reserved for knowledge-related logs.
  - **Role today:** System placeholder; not actively used.

- `Personal/Knowledge/Specs/`
  - Representative files:
    - `Personal/Knowledge/Specs/n5_principles_snapshot.md`
    - `Personal/Knowledge/Specs/wisdom_roots_system_outline.md`
  - **Role today:** Design and specification notes for the knowledge system itself and related architectures.

- `Personal/Knowledge/Wisdom/`
  - Contains belief-level/philosophical material, e.g.:
    - `Personal/Knowledge/Wisdom/productivity_ai_age_philosophy.md`
    - `Personal/Knowledge/Wisdom/V-Beliefs/`
  - **Role today:** Higher-level worldview and philosophy feeding into architecture and voice.

- `Personal/Knowledge/universe_registry.yaml`
  - Registry-like config describing knowledge “universes”.
  - **Role today:** System-facing metadata about how knowledge spaces are organized.

### 1.2 `Knowledge/`

On-disk today:
- `Knowledge/crm/individuals/{ceren,elizabeth-keshishyan-ek,...}.md` + `index.jsonl`
- `Knowledge/reasoning-patterns/ambassador_announcement_rubric_loop.md`

Expected by N5 (from prefs/docs/logs):
- Architectural & operational core:
  - `Knowledge/architectural/**` (principles, planning prompt, case studies)
  - `Knowledge/stable/{bio,company.md,company/*,careerspan-timeline,glossary}.md`
  - `Knowledge/semi_stable/**`, `Knowledge/hypotheses/**`, `Knowledge/market_intelligence/**`, `Knowledge/personal-brand/**`, etc.

Reality gap:
- These expected files now live under `Personal/Knowledge/Legacy_Inbox/**` and/or were deleted from `Knowledge/`.
- Daily guardian logs show repeated CRITICALs for missing `Knowledge/architectural/ingestion_standards.md`, `operational_principles.md`, `stable/bio.md`, `stable/company.md`, and `Knowledge/README.md`.

**Role today:**
- Thin “shell” of the original SSOT knowledge base:
  - A small, active CRM subset under `Knowledge/crm/individuals/`.
  - One reasoning-pattern file.
- Automation and system docs still *assume* `Knowledge/` is the canonical SSOT, which is no longer true on disk.

### 1.3 `Personal/Meetings/`

Structure (high-level):
- Active meetings: `Personal/Meetings/2025-11-14_Husain_x_V_[M]`, `2025-11-14_Vrijen_Attawar_and_Emily_Velasco_[M]`, etc.
- Archive: `Personal/Meetings/Archive/{2025-Q3,2025-Q4}/...`
- Quarantine & staging: `Personal/Meetings/_quarantine/**`, `Personal/Meetings/Inbox/`, `Personal/Meetings/BULK_IMPORT_20251104/`.
- System docs & logs:
  - `Personal/Meetings/STATUS...`, `PROCESSING_LOG.jsonl`, `rename_log.jsonl`, `*_TRANSITION_REPORT*.md`, etc.

Within each meeting (examples):
- Intelligence blocks: `B01_DETAILED_RECAP.md`, `B02_COMMITMENTS_CONTEXTUAL.md`, `B08_STAKEHOLDER_INTELLIGENCE.md`, etc.
- Metadata: `manifest.json`, `B26_MEETING_METADATA*.md`, `_metadata.json`.
- Transcripts: `transcript.jsonl`, `*.transcript.md`, occasionally `.docx`.
- Generated deliverables: `FOLLOW_UP_EMAIL.md`, `INTRO_*.md`, `meeting_intelligence.md`.

**Role today:**
- Canonical SSOT for meeting intelligence and transcripts (per specs such as `N5/docs/meeting-system-reference.md`).
- Also doubles as an operational workspace for the meeting pipeline (staging, quarantine, bulk import, archive).

### 1.4 `N5/knowledge/`, `N5/prefs/knowledge/`, `N5/logs/knowledge/`

- `N5/knowledge/digests/*.md`
  - Daily/periodic digests summarizing system and knowledge activity, e.g. `2025-10-29.md`, `2025-11-01.md`.
- `N5/prefs/knowledge/lookup.md`
  - Human-readable “knowledge lookup” index that *assumes* a rich `Knowledge/` tree.
- `N5/logs/knowledge/Email/*.log`
  - Historical logs from email/knowledge integrations.
- `N5/logs/knowledge/Sync/*.log` + `sync_reports/*.json`
  - Historical sync runs between `Knowledge/` and other surfaces.

**Role today:**
- System-side metadata and logging about the knowledge system, still largely anchored to the pre-realignment `Knowledge/` layout.

### 1.5 Other `*/Knowledge/` Paths

- `Documents/Knowledge/Articles/`
  - Examples: `Documents/Knowledge/Articles/2025-11-28_context-rot_chroma.md`.
  - Human-facing articles, likely draft or experimental.
- `Inbox/20251028-132904_n5os-core/Knowledge/`
  - Snapshot of an N5OS-core `Knowledge/architectural/` bundle used for bootstrapping/exports.
  - Contains `architectural_principles.md` plus principle files under `architectural/principles/`.

**Role today:**
- Documents/Knowledge: supplemental article store (per-conversation or per-project content).
- Inbox/n5os-core/Knowledge: export/import artifact for N5 OS core; not part of the live SSOT.

---

## 2. Knowledge vs. System Object Classification

### 2.1 Primarily **Knowledge**

- `Personal/Knowledge/Canon/**`
  - Essays, canonical posts, and voice pieces.
- `Personal/Knowledge/Frameworks/**`
  - Strategic frameworks and conceptual models.
- `Personal/Knowledge/Wisdom/**`
  - Beliefs and philosophical foundations.
- `Personal/Knowledge/Legacy_Inbox/stable/**`
  - Company overview, strategy, glossary, timeline, and related stable canon.
- `Personal/Knowledge/Legacy_Inbox/semi_stable/**`
  - "Current" snapshots (metrics, positioning, product) used as baselines.
- `Personal/Knowledge/Legacy_Inbox/hypotheses/**`
  - Market, product, fundraising, GTM hypotheses.
- `Personal/Knowledge/Legacy_Inbox/market/**` and `market-intelligence/*.md`
  - Narrative market and GTM writeups.
- `Personal/Knowledge/Legacy_Inbox/patterns/**` and `reasoning-patterns/**`
  - Conceptual patterns for markets, systems, and reasoning.
- `Personal/Knowledge/Legacy_Inbox/personal-brand/social-content/**`
  - Social posts, drafts, and analyses (LinkedIn/Twitter).
- `Personal/Knowledge/Legacy_Inbox/stakeholder_research/**`
  - SHRM application, GTM research notes, etc.
- `Documents/Knowledge/Articles/**`
  - Article-style content.
- `Personal/Meetings/**` (block files, transcripts, summaries)
  - Human-facing recaps, decisions, and stakeholder intelligence.
- `N5/knowledge/digests/*.md` (content layer of digests)
  - Human-readable summaries of system/knowledge state.

### 2.2 Primarily **System**

- `Personal/Knowledge/ContentLibrary/{content-library.db,content-library.json,settings.json,query/**,scripts/**}`
  - Databases, scripts, and CLI tooling that *operate on* knowledge.
- `Personal/Knowledge/Logs/`
  - Reserved for logging; currently empty.
- `Personal/Knowledge/universe_registry.yaml`
  - Registry/config describing knowledge universes.
- `Personal/Knowledge/Legacy_Inbox/intelligence/{documents,extracts,media,processed,rejected}/`
  - Intelligence ingestion pipeline storage rather than curated canon.
- `Personal/Knowledge/Legacy_Inbox/schemas/**`
  - JSON schemas (e.g., `knowledge.facts.schema.json`).
- `Personal/Knowledge/Legacy_Inbox/crm/crm.db` and related index files
  - SQLite DB, indices, registry JSONL.
- `Personal/Knowledge/Legacy_Inbox/market_intelligence/gtm_intelligence.db` and scripts like `mark_unprocessed.py`
- `N5/knowledge/` (as a namespace)
  - Digests themselves are hybrid, but directory is owned by N5 as a system output area.
- `N5/prefs/knowledge/lookup.md`
  - System configuration and lookup metadata.
- `N5/logs/knowledge/**`
  - Logs and sync reports.
- `Knowledge/crm/individuals/index.jsonl`
  - Technical index for CRM subset in `Knowledge/`.
- `Inbox/20251028-132904_n5os-core/Knowledge/**`
  - Packaged architectural content used for bootstrapping/sync; behaves like an install payload, not live canon.

### 2.3 **Hybrid** Areas

- `Personal/Knowledge/Legacy_Inbox/crm/individuals/*.md`
  - Human-readable profiles used by CRM automations and workflows.
- `Personal/Knowledge/Legacy_Inbox/operational/**`
  - Lessons learned and operational docs (knowledge about systems) that also steer behavior.
- `Personal/Knowledge/Specs/**`
  - Human-readable specs that directly inform automation and architecture.
- `N5/knowledge/digests/*.md`
  - Human summaries generated by system processes; both knowledge artifact and system telemetry.
- `Knowledge/crm/individuals/*.md`
  - Smaller subset of CRM profiles that likely mirror or diverge from the Legacy_Inbox CRM.
- `Personal/Meetings/` root and archive
  - Primarily knowledge (meeting narratives), but also holds pipeline state (quarantine, bulk import, transition reports).

---

## 3. Automation Touchpoints (Representative Map)

### 3.1 Knowledge Base (`Knowledge/` and related)

**Daily Guardian & Maintenance**
- `N5/scripts/maintenance/daily_guardian.py`
  - Reads/validates:
    - `/home/workspace/Knowledge/architectural/ingestion_standards.md`
    - `/home/workspace/Knowledge/architectural/operational_principles.md`
    - `/home/workspace/Knowledge/stable/bio.md`
    - `/home/workspace/Knowledge/stable/company.md`
    - `/home/workspace/Knowledge/README.md`
  - Today: these files are *missing* from `Knowledge/`, triggering recurring CRITICAL errors.

**CRM & Stakeholder Systems (expected `Knowledge/crm/...`)**
- `N5/scripts/crm_query.py`, `crm_query_helper.py`, `crm_migrate_to_v3.py`, `crm_migrate_profiles.py`, `sync_b08_to_crm.py`, `safe_stakeholder_updater.py`, `stakeholder_manager.py`, `linkedin_crm_sync.py`, `n5_networking_event_process.py`, warm intro systems, and many orchestration docs.
  - Expected paths:
    - `Knowledge/crm/crm.db`
    - `Knowledge/crm/individuals/*.md`
    - `Knowledge/crm/index.jsonl`
  - Reality:
    - `Knowledge/crm/individuals/` exists with *limited* profiles and `index.jsonl`.
    - `Knowledge/crm/crm.db` is **absent**.
    - A much richer CRM (db + markdown) lives under `Personal/Knowledge/Legacy_Inbox/crm/`.
  - Net effect: CRM automations are split between a partial `Knowledge/crm/` and a fuller Legacy_Inbox CRM, with docs still declaring `Knowledge/crm/` as SSOT.

**Market Intelligence & GTM**
- Scripts: `gtm_query.py`, `gtm_worker.py`, `gtm_db_builder.py`, `gtm_db_backfill.py`, `gtm_rebuild_with_interpretation.py`, `gtm_backfill_llm.py`, `gtm_b31_processor.py`.
  - Paths they *expect*:
    - `Knowledge/market_intelligence/gtm_intelligence.db`
    - `Knowledge/market_intelligence/aggregated_insights_*.md`
    - `Knowledge/market_intelligence/.processed_meetings.json`
  - Many of these files now live (or are mirrored) under `Personal/Knowledge/Legacy_Inbox/market_intelligence/`.

**Architectural Principles & System Docs**
- Dozens of prefs/specs/commands reference:
  - `Knowledge/architectural/architectural_principles.md`
  - `Knowledge/architectural/principles/*.md`
  - `Knowledge/architectural/ingestion_standards.md`
  - `Knowledge/architectural/planning_prompt.md`
- These files currently live under `Knowledge/architectural/` (according to Git history/logs), but are now flagged as deleted/moved in maintenance logs; equivalent/related material exists in `Personal/Knowledge/Specs/` and `Personal/Knowledge/Legacy_Inbox/`.

**Routing & File Protection**
- `N5/config/routing_config.json`
  - Treats `Knowledge/` as “Processed, structured information – stable reference material”.
- `N5/scripts/file_protector.py`
  - Special-cases any path containing `/Knowledge/` for extra safety.
- `N5/prefs/system/file-protection.md`, `git-governance.md`, etc.
  - Define protection & Git rules for `Knowledge/**/*.md`.

### 3.2 Personal Knowledge (`Personal/Knowledge/`)

There are fewer direct N5 scripts pointed to `Personal/Knowledge/` today; most automation references still assume `Knowledge/` as SSOT, while the *actual* content migrated under `Personal/Knowledge/Legacy_Inbox/`.

Key touchpoints:
- **Content Library CLI** (local, not N5-driven):
  - `Personal/Knowledge/ContentLibrary/scripts/{ingest.py,enhance.py,summarize.py,content_to_knowledge.py}`
  - Read/write within `Personal/Knowledge/ContentLibrary/` (DB, JSON index, `content/` files).
- **System docs referencing migration:**
  - Various architectural case studies and logs describe `Knowledge/` → `Personal/Knowledge/Legacy_Inbox/` moves, but active N5 scripts are still mostly keyed to `Knowledge/` paths.

### 3.3 Meeting Pipeline (`Personal/Meetings/`)

**Ingestion (Fireflies, Google Drive, etc.)**
- `N5/services/fireflies_webhook/transcript_processor.py`
  - Writes raw transcripts to `Personal/Meetings/Inbox/{folder}/`.
- Google Drive ingestion scheduled task (see `N5/prefs/ingestion/drive_meetings*.yaml` and `N5/docs/scheduled_task_gdrive_meetings.md`):
  - Reads Drive folders, writes normalized transcripts to `Personal/Meetings/Inbox/`.

**Meeting Pipeline Core (MG-1…MG-7)**
- Scripts under `N5/scripts/meeting_pipeline/**` and related helpers:
  - `normalize_transcript.py`, `transcript_processor.py`, `format_normalizer.py`, `finalize_meeting_intelligence.py`, `archive_completed_meetings.py`, `m_to_p_transition.py`, `cleanup_duplicates.py`, etc.
  - Main flows:
    - **Inbox staging:** `Personal/Meetings/Inbox/` (raw + `[M]`/`[P]` folders).
    - **Processed meetings:** `Personal/Meetings/{meeting_id}_[M or P]/`.
    - **Archive:** `Personal/Meetings/Archive/{YYYY-QX}/{meeting_id}/`.
    - **Bulk import:** `Personal/Meetings/BULK_IMPORT_20251104/` staging and duplicates folders.

**Prompts/Workflows on Meetings**
- Prompt files under `Prompts/` use shell commands referencing `Personal/Meetings/Inbox` and `Personal/Meetings/Archive`, including:
  - `Meeting Manifest Generation.prompt.md` – detects unmanifested Inbox meetings.
  - `Meeting Intelligence Generator.prompt.md` – generates missing B-blocks and logs to `Personal/Meetings/PROCESSING_LOG.jsonl`.
  - `Meeting Archive.prompt.md` – moves `[P]` meetings from Inbox to `Personal/Meetings/Archive/YYYY-QX/`.
  - `Meeting State Transition.prompt.md`, `Meeting Mark C-State.prompt.md`, `Warm Intro Generator.prompt.md`, `meeting-placement-cleanup.prompt.md`, etc.

**Analytics and Derived Systems**
- Warm intro digests: `N5/digests/warm-intro-drafts-*.md`
  - Read INTRO files and B07 blocks across `Personal/Meetings/` and `Personal/Meetings/Inbox/`.
- Action-item registries and follow-up workflows:
  - `N5/registry/meeting_action_items.jsonl`, `N5/logs/meetings_with_followups.json`, etc., link back into `Personal/Meetings/.../B25_DELIVERABLE_CONTENT_MAP.md`.

### 3.4 Bridges Between Records and Knowledge

- **Document/media curation & knowledge integration**
  - `N5/scripts/document_media_curator.py`, `intelligence_extractor.py`, `knowledge_integrator.py`, `generate_curation_report.py`, `process_curation_responses.py`.
  - Intended flow (per specs):
    - Ingest raw documents → Intelligence extracts → Write to `Knowledge/intelligence/**` → Promote to permanent `Knowledge/{category}/`.
  - Current reality: much of this pipeline has been redirected into `Personal/Knowledge/Legacy_Inbox/intelligence/**` rather than live `Knowledge/`.

- **Conversation-end / artifact placement protocols**
  - `N5/prefs/operations/{conversation-end-cleanup-protocol.md,artifact-placement.md}`
  - Declare target locations in `Knowledge/` for final artifacts, but on disk many of the “finals” now land under `Personal/Knowledge/Legacy_Inbox/` or stay in Records/Inbox folders.

---

## 4. Pain Points & Ambiguities (Today)

1. **SSOT Drift: `Knowledge/` vs `Personal/Knowledge/Legacy_Inbox/`**
   - N5 preferences, safety rules, and routing configs still treat `Knowledge/` as *the* SSOT for architectural and company canon.
   - Actual canonical files (company overview, strategy, glossary, timeline, many principles) now live under `Personal/Knowledge/Legacy_Inbox/stable/**` and related subtrees.
   - Result: daily maintenance logs show recurring CRITICAL errors for missing `Knowledge/architectural/*` and `Knowledge/stable/*`, while the real content exists elsewhere.

2. **Dual CRM Roots**
   - There is a partial CRM under `Knowledge/crm/individuals/` **and** a richer CRM under `Personal/Knowledge/Legacy_Inbox/crm/`.
   - Many scripts and orchestration docs assume `Knowledge/crm/crm.db` and `Knowledge/crm/individuals/` as SSOT, but `crm.db` is missing and the bulk of profiles live under Legacy_Inbox.
   - This split increases risk of profile divergence and makes it unclear which directory a given workflow should trust.

3. **Architectural Principles Location Confusion**
   - Architectural/spec content exists in multiple places:
     - Exported/archival: `Inbox/20251028-132904_n5os-core/Knowledge/architectural/**` and `N5/specs/architectural/**`.
     - Legacy/live-ish: references to `Knowledge/architectural/**` in many system docs.
     - Higher-level wisdom/specs under `Personal/Knowledge/Specs/` and `Personal/Knowledge/Wisdom/`.
   - Automations and prompts consistently point to `Knowledge/architectural/architectural_principles.md` as the load-first file, but that path is now in an inconsistent state.

4. **Meetings: Canon vs. Pipeline State**
   - `Personal/Meetings/` is both:
     - The SSOT for meeting intelligence (what actually happened, decisions, commitments), **and**
     - A live processing environment (Inbox, bulk import, quarantine, state transitions).
   - Because the same tree is used for both, it’s easy for automation to treat pipeline artifacts (e.g., BULK_IMPORT staging, intermediate manifests) as canon, and vice versa.

5. **Artifacts in Records vs. Knowledge**
   - Several workflows (e.g., follow-up generators, GTM aggregators) write semi-final outputs to `Records/` or meeting folders but rely on protocols that *intend* to promote durable artifacts into `Knowledge/`.
   - With `Knowledge/` partially hollowed out and Legacy_Inbox holding much of the canon, it’s unclear which path should be used for future promotion.

6. **N5 Prefs vs. Reality**
   - `N5/prefs/knowledge/lookup.md`, `N5/docs/reference_files_system.md`, and multiple protocols describe a clean hierarchy:
     - `Knowledge/` = SSOT
     - `Lists/` = task/priority system
     - `Records/` = raw history/logs
   - Current disk layout violates that model:
     - Canonical knowledge is split between `Knowledge/`, `Personal/Knowledge/Canon`, and `Personal/Knowledge/Legacy_Inbox/**`.
     - Some “knowledge-like” content (e.g., meeting digests) remains under `Personal/Meetings/` and N5 digests rather than being promoted into a consolidated knowledge tree.

7. **Automation Target Mismatch**
   - Many automations still read/write `Knowledge/` paths that no longer exist or no longer hold the authoritative versions of files (e.g., market_intelligence DBs, architectural principles, CRM DBs).
   - Newer workflows (especially around meetings and some AI pipelines) correctly target `Personal/Meetings/` and `Personal/Knowledge/` but coexist with the older assumptions, creating conflicting mental models.

---

**Current Status Check**
- File created: `Records/Personal/knowledge-system/PHASE1_current_state_map.md`
- Sections included: Folder Map, Classification, Automation Touchpoints, Pain Points.
- Based on direct scans of `Personal/Knowledge/`, `Knowledge/`, `Personal/Meetings/`, `N5/knowledge/`, `N5/prefs/knowledge/`, `N5/logs/knowledge/`, and other `*/Knowledge/` paths.

