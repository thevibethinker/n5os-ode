---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.1
---
# Phase 3 – Migration Plan & Safety Guardrails

Design-only plan to implement the Phase 2 target architecture. No file operations are executed by this document; all moves are described as **intended behavior** for future deterministic scripts.

---

## 1. Migration Phases & Order of Operations

(Phases 0–9 remain the same in structure; this version updates path targets to the refined architecture.)

- Phase 0 – Pre-flight & Protections
- Phase 1 – Architecture Skeleton & SSOT Declarations
- Phase 2 – CRM Realignment
- Phase 3 – GTM / Intelligence/World/Market Realignment
- Phase 4 – Architecture & Principles Consolidation
- Phase 5 – Frameworks, Patterns, Hypotheses, Reasoning Patterns
- Phase 6 – Canon, Archive, Personal Brand, and Content Library Imports
- Phase 7 – Intelligence Pipelines & System Surfaces
- Phase 8 – Compatibility Shell Tightening for `Knowledge/`
- Phase 9 – Automation Refactor & Final Verification

(Phase 0 and Phase 1 text unchanged conceptually; paths updated where needed.)

---

### Phase 3 – GTM / Intelligence/World/Market Realignment

**Goal:** Consolidate GTM and market intelligence (DB + narratives) under `Personal/Knowledge/Intelligence/World/Market/`.

**Pre-conditions**
- Phases 1–2 complete.
- Legacy GTM/market assets identified:
  - `Personal/Knowledge/Legacy_Inbox/market/*.md`.
  - `Personal/Knowledge/Legacy_Inbox/market_intelligence/**` including `gtm_intelligence.db`, `meeting_registry.jsonl`.
  - Any residual `Knowledge/market_intelligence/**` expected by scripts.

**Actions (design-only)**
- **DB relocation plan:**
  - Move `gtm_intelligence.db` and related registries into `Personal/Knowledge/Intelligence/World/Market/db/`.
  - Keep or create `meeting_registry.jsonl` under `Personal/Knowledge/Intelligence/World/Market/`.
- **Narrative normalization plan:**
  - Scripts scan `Personal/Knowledge/Legacy_Inbox/market/*.md` and any narrative-like files under `Legacy_Inbox/market_intelligence/`.
  - For each, classify:
    - Still-current, reusable GTM insight → `Personal/Knowledge/Intelligence/World/Market/narratives/`.
    - Historical or obsolete → `Personal/Knowledge/Archive/MarketIntelligence/` (or a similar archival subtree).
  - Ensure naming conventions tie narratives to DB entities or segments where relevant (e.g. `narratives/segment_<slug>.md`).
- **Compatibility for `Knowledge/market_intelligence/`:**
  - Similar to CRM, keep only minimal stubs or symlink-like pointers that direct readers/scripts to `Personal/Knowledge/Intelligence/World/Market/`.

**Post-conditions & Validation**
- `Personal/Knowledge/Intelligence/World/Market/db/gtm_intelligence.db` is the only live GTM DB location.
- Narrative GTM writeups live in `Personal/Knowledge/Intelligence/World/Market/narratives/`.
- `Personal/Knowledge/Legacy_Inbox/market_intelligence/` no longer contains live SSOT DBs or narratives (only logs/intake, if any).

---

### Phase 4 – Architecture & Principles Consolidation

(As in v1.0, with this clarification:)

- Architectural principles are canonically stored under `Personal/Knowledge/Architecture/principles/**`.
- Any copies or symlinks under `N5/docs/**` are treated as **mirrors** for convenience; scripts and prompts should treat `Personal/Knowledge/Architecture/principles/**` as the authoritative source.

---

### Phase 6 – Canon, Archive, Personal Brand, and Content Library Imports

**Goal:** Normalize all company canon, stable/semi-stable docs, personal-brand/social content, and relevant articles into the Canon + ContentLibrary + Archive model.

**Pre-conditions**
- Phases 1–5 complete.
- Legacy sources identified:
  - `Personal/Knowledge/Legacy_Inbox/stable/company/*` and related stable files.
  - `Personal/Knowledge/Legacy_Inbox/semi_stable/*`.
  - `Personal/Knowledge/Legacy_Inbox/personal-brand/social-content/**`.
  - `Documents/Knowledge/Articles/**`.

**Actions (design-only)**
- **Company canon:**
  - Files answering "What is Careerspan?" or conveying stable company story → `Personal/Knowledge/Canon/Company/`.
  - Latest "current metrics/positioning/product" snapshots → either
    - `Canon/Company/Snapshots/current.md` for the *current* snapshot, and
    - older snapshots into `Archive/Company_Snapshots/`.
- **Personal brand & social content:**
  - Normalize social content into `Personal/Knowledge/Canon/V/SocialContent/`.
  - Preserve systems/templates/rubrics under `Personal/Knowledge/Frameworks/Operational/social-systems/**` when they describe repeatable posting systems.
- **Articles & documents (Documents/Knowledge/Articles):**
  - For each file under `Documents/Knowledge/Articles/`:
    - If it is part of durable canon (e.g. a VibeThinker post or finalized essay) → `Personal/Knowledge/Canon/{V or Company}/`.
    - If it is important reference material for future synthesis but not canon → `Personal/Knowledge/ContentLibrary/content/`.
  - ContentLibrary is part of the **elevated library**: inclusion implies the document has already passed a discretion threshold and is worth keeping for reuse or promotion.

**Post-conditions & Validation**
- `Personal/Knowledge/Canon/` holds the canonical narrative for V, Company, Products, Stakeholders, and SocialContent.
- Relevant articles from `Documents/Knowledge/Articles/` live either in Canon or ContentLibrary/content under the new layout; `Documents/Knowledge/Articles/` is no longer a SSOT.

---

## 2. Path-Level Migration Rules (Concrete)

_Update the Market/GTM section to use Intelligence/World/Market paths; ContentLibrary and Architecture principles references updated as above. Other sections remain structurally as in v1.0 but implicitly point to the refined paths defined in Phase 2 v1.1._

(Keep the rest of the document unchanged except for path references matching the new architecture.)
---

### 2.1 CRM

- `Personal/Knowledge/Legacy_Inbox/crm/crm.db` → `Personal/Knowledge/CRM/db/crm.db`
- `Personal/Knowledge/Legacy_Inbox/crm/*.jsonl` (indices, registries) → `Personal/Knowledge/CRM/db/`
- `Personal/Knowledge/Legacy_Inbox/crm/individuals/*` → `Personal/Knowledge/CRM/individuals/*`
- `Knowledge/crm/individuals/*` →
  - Merge into `Personal/Knowledge/CRM/individuals/*` if unique.
  - Then convert originals into stub files that reference the new path.
- `Knowledge/crm/individuals/index.jsonl` → regenerated view over `Personal/Knowledge/CRM/individuals/` (non-SSOT).

### 2.2 Market & GTM Intelligence

- `Personal/Knowledge/Legacy_Inbox/market_intelligence/gtm_intelligence.db` → `Personal/Knowledge/Intelligence/World/Market/db/gtm_intelligence.db`
- `Personal/Knowledge/Legacy_Inbox/market_intelligence/meeting_registry.jsonl` → `Personal/Knowledge/Intelligence/World/Market/meeting_registry.jsonl`
- `Personal/Knowledge/Legacy_Inbox/market/*.md` →
  - Current, generalizable GTM insights → `Personal/Knowledge/Intelligence/World/Market/narratives/`
  - Historical-only → `Personal/Knowledge/Archive/MarketIntelligence/`
- Any residual `Knowledge/market_intelligence/**` → stubs pointing to `Personal/Knowledge/Intelligence/World/Market/**`.

### 2.3 Architecture & System Specs

- `Personal/Knowledge/Legacy_Inbox/systems/*` → `Personal/Knowledge/Architecture/specs/systems/`
- `Personal/Knowledge/Legacy_Inbox/infrastructure/*` → `Personal/Knowledge/Architecture/specs/infrastructure/`
- `Personal/Knowledge/Specs/*` →
  - System/architecture-facing material → `Personal/Knowledge/Architecture/specs/`
  - Belief-level/philosophical material → `Personal/Knowledge/Wisdom/`
- `Inbox/20251028-132904_n5os-core/Knowledge/architectural/principles/*` → `Personal/Knowledge/Architecture/principles/`
- `Inbox/20251028-132904_n5os-core/Knowledge/architectural/*.md` (top-level) → `Personal/Knowledge/Architecture/` (appropriate subtree) and an archival copy under `Personal/Knowledge/Archive/Legacy_Knowledge_Tree/`

### 2.4 Patterns, Hypotheses, Reasoning Patterns

- `Personal/Knowledge/Legacy_Inbox/patterns/*` → `Personal/Knowledge/Frameworks/Patterns/*`
- `Personal/Knowledge/Legacy_Inbox/hypotheses/*` → `Personal/Knowledge/Frameworks/Hypotheses/*`
- `Personal/Knowledge/Legacy_Inbox/reasoning-patterns/*` → `Personal/Knowledge/Frameworks/Patterns/*`
- `Knowledge/reasoning-patterns/*` →
  - Canonical copy under `Personal/Knowledge/Frameworks/Patterns/*`
  - Original replaced with stub referencing new path.

### 2.5 Personal Brand, Social Content, Stakeholder Research

- `Personal/Knowledge/Legacy_Inbox/personal-brand/social-content/**` →
  - Durable, voice-defining posts and archetypes → `Personal/Knowledge/Canon/V/SocialContent/**`
  - Posting systems, rubrics, and meta-frameworks → `Personal/Knowledge/Frameworks/Operational/social-systems/**`
- `Personal/Knowledge/Legacy_Inbox/stakeholder_research/**` →
  - Reusable, cross-meeting insights about stakeholders/segments → `Personal/Knowledge/Canon/Stakeholders/**` or `Personal/Knowledge/MarketIntelligence/narratives/**`.
  - Time-bound or low-signal raw research → `Personal/Knowledge/Archive/Stakeholder_Research/**`.

### 2.6 Stable & Semi-Stable Canon

- `Personal/Knowledge/Legacy_Inbox/stable/company/*` → `Personal/Knowledge/Canon/Company/*`
- `Personal/Knowledge/Legacy_Inbox/stable/{careerspan-timeline.md,glossary.md}` → `Personal/Knowledge/Canon/Company/{careerspan-timeline.md,glossary.md}`
- `Personal/Knowledge/Legacy_Inbox/semi_stable/*` →
  - Current snapshot → `Personal/Knowledge/Canon/Company/Snapshots/current.md`
  - Older snapshots → `Personal/Knowledge/Archive/Company_Snapshots/*`

### 2.7 Documents/Knowledge/Articles

- `Documents/Knowledge/Articles/*` →
  - If article is durable canon → `Personal/Knowledge/Canon/{V or Company}/*`
  - If article is reference content for tools → `Personal/Knowledge/ContentLibrary/content/*`

### 2.8 Intelligence Pipelines & Schemas

- `Personal/Knowledge/Legacy_Inbox/intelligence/**` → remain as system storage under `Legacy_Inbox/intelligence/` or later `Personal/Knowledge/Logs/intelligence/**`.
- `Personal/Knowledge/Legacy_Inbox/schemas/**` → system schemas; high-level docs → `Personal/Knowledge/Architecture/specs/intelligence_pipelines/**`.

### 2.9 Compatibility Shell – `Knowledge/`

- `Knowledge/crm/individuals/**` → compatibility stubs + index (no SSOT content).
- `Knowledge/reasoning-patterns/**` → compatibility stubs.
- Any remaining `Knowledge/*` content not specifically needed → archived to `Personal/Knowledge/Archive/Legacy_Knowledge_Tree/Knowledge/**` once automation refactors are complete.

---

## 3. Safety & Guardrails

### 3.1 `.n5protected` Usage

- Maintain `.n5protected` files in these roots at minimum:
  - `Personal/Knowledge/`
  - `Personal/Meetings/`
  - `Knowledge/`
  - `N5/`
  - `Records/Personal/knowledge-system/`
- For each `.n5protected` file, encode:
  - Reason (e.g. "SSOT knowledge root – migration requires explicit confirmation").
  - Scope (entire subtree vs specific patterns).
- All migration scripts must:
  - Call `N5/scripts/n5_protect.py check <path>` before any move/delete.
  - Abort (non-zero exit) on protected paths unless an explicit `--override` flag is provided and logged.

### 3.2 Git Snapshots & Change Windows

- Create a Git commit before and after each major phase.
- Optionally tag key milestones, e.g.:
  - `phase3-preflight`, `phase3-crm-migrated`, `phase3-gtm-migrated`, `phase3-architecture-consolidated`.
- Avoid overlapping large migrations; only one bulky phase should be "live" at a time.

### 3.3 Dry-Run Discipline for Bulk Operations

- For any operation affecting **>5 files**, scripts must support a `--dry-run` flag that:
  - Prints planned moves (source → destination) and counts per directory.
  - Does **not** modify the filesystem.
- Operator flow:
  1. Run dry-run, inspect sample operations.
  2. Confirm results look correct.
  3. Re-run with `--execute` (or equivalent) while logging to `migration_runs.log`.

### 3.4 High-Risk Areas – Minimal Structural Change

- `Personal/Meetings/**`
  - No structural changes to the MG-1…MG-7 layout.
  - Only **links out** to `Personal/Knowledge/**` for promoted insights.
- DB files:
  - `Personal/Knowledge/CRM/db/**`
  - `Personal/Knowledge/MarketIntelligence/db/**`
  - Any move or schema change must:
    - Be performed via dedicated scripts with backup copies and integrity checks.
    - Be fully reversible (backups kept until successful verification).
- `N5/**`
  - No large-scale renames or folder moves inside `N5/` as part of this migration.
  - Only path constant updates and configuration edits.

### 3.5 Use of Maintenance / Audit Scripts

- `daily_guardian.py` (after refactor):
  - Run in check-only mode after Phases 4, 5, and 9.
  - Expectation: no CRITICALs for missing architecture/SSOT files if mapping is consistent.
- Any existing monthly/quarterly audit scripts:
  - Extend to verify that no new knowledge is being written to `Knowledge/`.

---

## 4. Automation Refactor Plan

For each automation family, this section captures: **old assumptions, new conventions, and refactor approach**.

### 4.1 Knowledge Base & Daily Guardian

- **Old assumptions**
  - `Knowledge/` is SSOT for:
    - Architectural principles at `Knowledge/architectural/**`.
    - Company canon at `Knowledge/stable/**` and `Knowledge/semi_stable/**`.
  - Daily Guardian reads `Knowledge/architectural/ingestion_standards.md`, `Knowledge/architectural/operational_principles.md`, `Knowledge/stable/bio.md`, `Knowledge/stable/company.md`, `Knowledge/README.md`.

- **New path conventions**
  - Architecture:
    - `Personal/Knowledge/Architecture/principles/**`
    - `Personal/Knowledge/Architecture/ingestion_standards/**`
  - Company canon:
    - `Personal/Knowledge/Canon/Company/**`
  - Knowledge SSOT declaration:
    - `Personal/Knowledge/README.md` (plus Architecture README).

- **Refactor approach**
  - Introduce a centralized path config (e.g. `N5/config/paths.yaml`) defining:
    - `knowledge_architecture_root: Personal/Knowledge/Architecture`
    - `knowledge_canon_company_root: Personal/Knowledge/Canon/Company`
  - Update Daily Guardian and related checks to read from config rather than hardcoding `/Knowledge/...`.
  - Keep a thin compatibility check for `Knowledge/` (e.g. ensure `Knowledge/README.md` exists) but treat missing non-compatibility paths as expected.

### 4.2 CRM Automations

- **Old assumptions**
  - CRM DB and profiles under `Knowledge/crm/{crm.db,individuals/,index.jsonl}`.
  - Scripts: `crm_query.py`, `crm_query_helper.py`, `crm_migrate_to_v3.py`, `crm_migrate_profiles.py`, `sync_b08_to_crm.py`, `safe_stakeholder_updater.py`, `stakeholder_manager.py`, `linkedin_crm_sync.py`, `n5_networking_event_process.py`, warm-intro helpers.

- **New path conventions**
  - `Personal/Knowledge/CRM/db/crm.db`
  - `Personal/Knowledge/CRM/individuals/**`
  - `Personal/Knowledge/CRM/views/**`

- **Refactor approach**
  - Centralize CRM root path in config (same `paths.yaml`), e.g. `crm_root: Personal/Knowledge/CRM`.
  - Update all CRM-related scripts to use the config value rather than literal `Knowledge/crm/...`.
  - Treat any references to `Knowledge/crm/` as compatibility-only; ideally, these scripts will no longer read from there at all.

### 4.3 GTM / MarketIntelligence Automations

- **Old assumptions**
  - GTM DB and narratives under `Knowledge/market_intelligence/**`.
  - Scripts: `gtm_query.py`, `gtm_worker.py`, `gtm_db_builder.py`, `gtm_db_backfill.py`, `gtm_rebuild_with_interpretation.py`, `gtm_backfill_llm.py`, `gtm_b31_processor.py`.

- **New path conventions**
  - `Personal/Knowledge/Intelligence/World/Market/db/gtm_intelligence.db`
  - `Personal/Knowledge/Intelligence/World/Market/narratives/**`
  - `Personal/Knowledge/Intelligence/World/Market/meeting_registry.jsonl`

- **Refactor approach**
  - Add `market_intelligence_root` and `market_intelligence_db_path` to path config.
  - Update GTM scripts to use these keys.
  - Where scripts still expect `Knowledge/market_intelligence/`, add explicit shims or paths.yaml entries that route them through the new root.

### 4.4 Architecture Loading & System Docs

- **Old assumptions**
  - Many prompts, prefs, and docs tell N5 to load `Knowledge/architectural/architectural_principles.md` first.

- **New path conventions**
  - Recommended primary load file: `Personal/Knowledge/Architecture/principles/architectural_principles.md`.

- **Refactor approach**
  - Update reference docs (`N5/prefs/knowledge/lookup.md`, `N5/docs/reference_files_system.md`, etc.) to name the new path.
  - Update any orchestration prompts that load architecture docs to reference `Personal/Knowledge/Architecture/**`.
  - Keep `Knowledge/architectural/*` only as archival if needed, not as a live load target.

### 4.5 Document/Media Curation & Knowledge Integrator

- **Old assumptions**
  - Intake → `Knowledge/intelligence/**` → promotion directly into `Knowledge/{category}/`.

- **New path conventions**
  - Intake/logging → `Personal/Knowledge/Legacy_Inbox/intelligence/**` (or future `Logs/intelligence/`).
  - Promotion targets:
    - Canon: `Personal/Knowledge/Canon/**`
    - Frameworks: `Personal/Knowledge/Frameworks/**`
    - MarketIntelligence: `Personal/Knowledge/MarketIntelligence/**`
    - Architecture: `Personal/Knowledge/Architecture/**`

- **Refactor approach**
  - Update curation/integration scripts to write promoted artifacts only into `Personal/Knowledge/**`.
  - Ensure they treat any writes to `Knowledge/` as a bug.

### 4.6 Meeting Pipeline, Warm Intros, and Derived Systems

- **Old assumptions**
  - Meeting pipeline already correctly uses `Personal/Meetings/**` as SSOT.
  - Some downstream workflows (warm-intro digests, action-item registries) may reference `Knowledge/` for promotion.

- **New path conventions**
  - Meeting intelligence remains under `Personal/Meetings/**`.
  - Promoted stakeholder/segment narratives → `Personal/Knowledge/Canon/Stakeholders/**`.
  - CRM enrichments → `Personal/Knowledge/CRM/individuals/**`.
  - GTM patterns → `Personal/Knowledge/MarketIntelligence/narratives/**`.

- **Refactor approach**
  - Ensure warm-intro generators and action-item systems:
    - Read from `Personal/Meetings/**`.
    - Write any durable knowledge contributions to the appropriate `Personal/Knowledge/**` subtree.

### 4.7 Routing Configs, File Protection, and Prefs

- **Old assumptions**
  - `N5/config/routing_config.json` and file protection docs treat `/Knowledge/` as the SSOT for "processed, structured information".

- **New path conventions**
  - Update routing config to:
    - Treat `Personal/Knowledge/**` as processed/structured knowledge.
    - Retain `Knowledge/` only as compatibility.

- **Refactor approach**
  - Add entries for the new roots in routing config and protection rules.
  - Ensure `file_protector.py` understands both `Personal/Knowledge/**` and `Knowledge/**` (latter as legacy-protected).

---

## 5. Compatibility Shell Strategy for `Knowledge/`

### 5.1 What Remains in `Knowledge/` During Compatibility Window

- `Knowledge/README.md` – clearly states:
  - `Personal/Knowledge/` is the SSOT.
  - `Knowledge/` is a compatibility layer only.
- `Knowledge/crm/individuals/` – stub markdown files and `index.jsonl` auto-generated from `Personal/Knowledge/CRM/individuals/`.
- `Knowledge/reasoning-patterns/` – stub files pointing to `Personal/Knowledge/Frameworks/Patterns/`.
- Any other compatibility-critical files explicitly required by high-risk automations yet to be refactored.

### 5.2 Criteria to Stop Mirroring into `Knowledge/`

Mirroring/stub maintenance can stop when:

1. All CRM and reasoning-pattern scripts read exclusively from `Personal/Knowledge/**`.
2. No scheduled tasks or prompts invoke paths under `Knowledge/crm/` or `Knowledge/reasoning-patterns/`.
3. A code search over the repo for `/Knowledge/` shows only:
   - Compatibility docs.
   - Explicit migration notes.

### 5.3 Criteria to Retire / Repurpose `Knowledge/`

Before retiring `Knowledge/` as an active compatibility shell:

- **Verification window:**
  - For at least 30 days of regular use, no new files are written under `Knowledge/` by scripts or prompts.
- **Audit checks:**
  - Daily Guardian and related maintenance scripts pass without referencing `Knowledge/` as SSOT.
- **Archive step:**
  - Take a Git tag and, if desired, archive the full historic tree under `Personal/Knowledge/Archive/Legacy_Knowledge_Tree/Knowledge/**`.

After these conditions are met, `Knowledge/` can be:
- Left as a tiny shell with README + optional stubs; **or**
- Fully repurposed for some future use, with explicit docs making clear it no longer carries historical semantics.

---

## 6. Testing & Verification Plan

### 6.1 Directory Sanity Checks

- After each phase:
  - Confirm that no new canonical files remain in `Personal/Knowledge/Legacy_Inbox/` except those explicitly designated as system-only (e.g. `intelligence/`, `schemas/`).
  - Confirm that:
    - `Personal/Knowledge/CRM/` holds all CRM SSOT content.
    - `Personal/Knowledge/MarketIntelligence/` holds all GTM SSOT content.
    - `Personal/Knowledge/Architecture/` holds all architecture docs.
    - `Personal/Knowledge/Frameworks/` holds all frameworks/patterns/hypotheses.
    - `Personal/Knowledge/Canon/` holds company/V/product/stakeholder canon.
- For Legacy_Inbox:
  - Ensure remaining content is clearly marked as staging/system/archival, not live canon.

### 6.2 Script-Level Checks

- For each migration script (future work):
  - Run with `--dry-run` and capture output into `Records/Personal/knowledge-system/logs/`.
  - After live runs, re-run with `--dry-run` to confirm idempotence (no further moves required).

### 6.3 Automation & Prefs Validation

- After refactoring each automation family:
  - Run its primary script(s) in check-only mode (or against a small test sample) to ensure they:
    - Read from `Personal/Knowledge/**` and `Personal/Meetings/**` only.
    - Do not attempt to write to `Knowledge/` except via compatibility stubs.
- Re-run `daily_guardian.py` and inspect logs for:
  - Absence of CRITICAL errors pointing to missing `Knowledge/architectural/*` or `Knowledge/stable/*`.

### 6.4 End-to-End Spot Checks

- **CRM:**
  - Pick 5–10 representative individuals and verify:
    - Canonical profile exists under `Personal/Knowledge/CRM/individuals/`.
    - Upstream artifacts (meeting B-blocks, stakeholder research) link correctly.
- **GTM:**
  - Pick 3–5 GTM narratives and confirm they:
    - Live under `Personal/Knowledge/Intelligence/World/Market/narratives/`.
    - Have pointers to contributing meetings and DB entries.
- **Architecture:**
  - Start from `Personal/Knowledge/Architecture/README.md` and follow links to confirm architectural docs are coherent and discoverable.

### 6.5 Final Green Checklist for Migration Completion

The migration can be considered successful (Phase 3 complete) when:

1. `Personal/Knowledge/` matches the Phase 2 topology and contains all SSOT domains.
2. `Personal/Meetings/` remains stable and continues to serve as SSOT for meeting intelligence.
3. `Knowledge/` is reduced to a compatibility shell with no SSOT content.
4. All high-risk automations and scheduled tasks refer to `Personal/Knowledge/**` and `Personal/Meetings/**` as their primary roots.
5. Directory scans show **no live canon** remaining in `Personal/Knowledge/Legacy_Inbox/` except explicitly designated archival or system-only areas.
6. Maintenance scripts (e.g., Daily Guardian) run clean with no SSOT-path mismatches.

---

**Status:** Design-only. This document specifies the migration plan and guardrails for implementing the Phase 2 architecture. All actual moves, renames, or deletions must be executed by deterministic scripts or supervised manual steps that follow the safety rules defined above.


