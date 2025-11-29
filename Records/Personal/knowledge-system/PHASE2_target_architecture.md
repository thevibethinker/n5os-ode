---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.1
---

# Phase 2 – Target Knowledge Architecture & Migration Rules

## 1. Target Folder Topology

**Goal:** `Personal/Knowledge/` is the single source of truth (SSOT) for human-facing knowledge. `Knowledge/` becomes a thin compatibility shell only. N5 is a *system lens* sitting on top of `Personal/Knowledge/` + `Personal/Meetings/` + system DBs.

### 1.1 Target High-Level Tree

```text
Personal/
  Knowledge/                           # Human-facing knowledge SSOT (all domains)
    Wisdom/                            # Enduring principles, beliefs, worldview
      Self/                            # Personal beliefs
      World/                           # Deep theories about markets, tech, careers
      Systems/                         # System/N5 doctrines and architectural principles
    Intelligence/                      # Elevated, synthesized understanding (knowledge tier)
      Self/                            # Self-related intelligence
      World/                           # World intelligence (macro, domains, actors)
        Market/                        # Market/GTM intelligence under World
          db/                          # gtm_intelligence.db and related (system)
          narratives/                  # GTM/market syntheses
          snapshots/                   # Time-bounded GTM snapshots
      Systems/                         # Patterns about how your own systems behave
      Relationships/                   # Stakeholder/relationship intelligence
    ContentLibrary/                    # Curated documents & blocks (information/knowledge staging)
      content/                         # Full documents OR blocks; curated, not raw
      content-library.db               # DB (system)
      content-library.json             # Index (system)
      scripts/                         # Tooling (system)
      settings.json                    # Config (system)
    Canon/                             # Finalized narrative canon (company + V + products)
      Company/                         # Careerspan company canon
      V/                               # V-specific canon
        SocialContent/                 # Personal brand / social content canon
      Products/                        # Product narratives
      Stakeholders/                    # Stable stakeholder/segment narratives
    Frameworks/                        # Strategic/operational frameworks & patterns
      Strategic/                       # Strategy & GTM frameworks
      Operational/                     # Internal ops/process frameworks
      Patterns/                        # Market/system/reasoning patterns
      Hypotheses/                      # Structured hypotheses (linked to evidence)
    CRM/                               # **SSOT for CRM** (people/orgs)
      db/                              # crm.db and related indices (system-owned)
      individuals/                     # Human-readable profiles
      organizations/                   # Org profiles
      events/                          # Events, interactions, follow-ups
      views/                           # Saved slices / segment definitions
    Architecture/                      # **SSOT for system & knowledge architecture docs**
      principles/                      # Architectural + operational principles (loaded by N5)
      ingestion_standards/             # Standards for what enters Knowledge
      planning_prompts/                # System-facing planning prompts (human-readable)
      case_studies/                    # Architecture/knowledge case studies
      specs/                           # Human-facing specs for systems & workflows
    Logs/                              # Knowledge-related logs (system-facing)
    Archive/                           # Long-term cold storage for superseded knowledge
      Pre_2025/                        # Example time-bounded or project-bounded archives
      Legacy_Knowledge_Tree/          # Archived copy of old Knowledge/ layout if needed
    Legacy_Inbox/                      # Transitional: dense legacy universe (read-mostly)
      intelligence/                    # Intake staging (system-facing)
      schemas/                         # JSON schemas etc. (system-facing)
      crm/                             # Legacy CRM (to be normalized → CRM/)
      market_intelligence/             # Legacy GTM DBs (→ Intelligence/World/Market/)
      stable/                          # Legacy stable canon (→ Canon/ + Architecture/ + Wisdom/Systems)
      semi_stable/                     # Legacy current snapshots (→ Canon/ or Archive/)
      patterns/, hypotheses/, ...      # Legacy conceptual material (→ Frameworks/)

  Meetings/                            # **SSOT for meeting intelligence** (unchanged root)
    ...                                # Existing MG-1…MG-7 structure

Records/
  Personal/
    knowledge-system/                  # Design, migration plans, reasoning traces
      PHASE1_current_state_map.md
      PHASE2_target_architecture.md
      PHASE3_migration_plan.md

Knowledge/                             # Compatibility shell only (no SSOT domains)
  crm/individuals/                     # Thin mirror/stubs → point to Personal/Knowledge/CRM/
  reasoning-patterns/                  # Thin mirror/stubs → point to Frameworks/Patterns/
  README.md                            # Explicitly declares deprecation + new SSOT

N5/
  knowledge/digests/                   # System digests (hybrid: telemetry + draft knowledge)
  prefs/knowledge/                     # Lookup + routing configs (system-only)
  logs/knowledge/                      # Logs (system-only)
```

### 1.2 Relationship to `Personal/Meetings/` and `Records/`

- `Personal/Meetings/` remains **SSOT for meeting intelligence** (per-meeting transcripts, blocks, commitments, stakeholder intel).
- `Personal/Knowledge/` is **SSOT for generalized, de-meeting-ified knowledge** that outlives individual meetings.
- `Records/` continues as **chronological history + operational traces** (logs, transition reports, design docs like this one). It is *not* a knowledge SSOT; durable knowledge is promoted into `Personal/Knowledge/`.

---

## 2. Role Definitions & SSOT Declarations

### 2.1 `Personal/Knowledge/Wisdom/`
- **Role:** Enduring principles, beliefs, worldview feeding into architecture, canon, and decision-making.
- **SSOT:** Yes – for **belief-level material and worldview**, including system doctrines that are conceptually part of V's wisdom.
- **Examples:**
  - V’s beliefs about productivity in the AI age.
  - Philosophical notes that inform product/design.
  - System/N5 doctrines that are written as principles about how the world and the system should work.

### 2.2 `Personal/Knowledge/Intelligence/`
- **Role:** Elevated, synthesized understanding – **Knowledge tier**: time-bound or situational aggregators, world intelligence, self/system/relationship intelligence.
- **SSOT:** Yes – for **knowledge-level material** (patterns and aggregators) once promoted from meetings/projects.
- **Examples:**
  - GTM intelligence snapshots (under `Intelligence/World/Market/`).
  - Stakeholder/relationship patterns under `Intelligence/Relationships/`.
  - System behavior analyses under `Intelligence/Systems/`.

### 2.3 `Intelligence/World/Market/`
- **Role:** Market/GTM intelligence as a *subtree* of World Intelligence.
- **SSOT:** Yes – for GTM/market intelligence, both structured DBs and narratives.
- **Examples:**
  - `db/gtm_intelligence.db`.
  - `narratives/*.md` summarizing ICPs, segments, GTM experiments.
  - `snapshots/*.md` for time-bounded views.

### 2.4 `Personal/Knowledge/ContentLibrary/`
- **Role:** Curated library of documents **and** blocks that are worth keeping as reusable information/knowledge. It is part of the *elevated* layer: anything here has already passed a basic discretion threshold.
- **SSOT:**
  - For `content/` entries (full docs or blocks): Yes – they are curated inputs into the knowledge system.
  - For DBs/scripts/config: No – system-only implementation details.
- **Examples:**
  - Ingested or authored documents that are valuable references (not raw noise).
  - Highlight bundles or block collections that are kept for reuse.
  - Long-form documents that haven’t yet been distilled into Intelligence or Wisdom, but are important enough to live in the library.

### 2.5 `Personal/Knowledge/Canon/`
- **Role:** Finalized narrative canon: essays, company story, product narratives, personal brand/social content, and other artifacts that represent the "official" story.
- **SSOT:** Yes – for *narrative canon* about V, Careerspan, products, and key stakeholders.
- **Examples:**
  - Company history and positioning posts.
  - V’s long-form public essays.
  - Curated social content under `Canon/V/SocialContent/`.

### 2.6 `Personal/Knowledge/CRM/`
- **Role:** Central home for CRM: people, organizations, events, and CRM DBs.
- **SSOT:** Yes – for **all CRM data**, both DB-level and human-readable profiles.

### 2.7 `Personal/Knowledge/Architecture/`
- **Role:** Human-facing architecture & system specs actually loaded by N5 as reference: principles, standards, design docs for N5, knowledge system, meeting pipeline, etc.
- **SSOT:** Yes – for **system and knowledge architecture docs** consumed by humans and AIs.
- **N5 relationship:**
  - N5 loads architectural principles from here (e.g. `Architecture/principles/architectural_principles.md`).
  - N5 may keep convenience copies or symlinks under `N5/docs/**`, but those are **views**, not the canonical source.

### 2.8 `Personal/Knowledge/Logs/`, `Archive/`, `Legacy_Inbox/`
- As in v1.0, but with the understanding that Legacy_Inbox is transitional and that Archive holds demoted K/W objects.

(Other role definitions from v1.0 remain, updated implicitly by the tree above.)

---

## 3. N5 Integration, Migration Rules, and Interfaces

_Remains as in v1.0, with the following clarifications:_

- Anywhere Phase 2 previously referenced `Personal/Knowledge/MarketIntelligence/`, the canonical target for GTM/market intelligence is now `Personal/Knowledge/Intelligence/World/Market/`.
- ContentLibrary is treated as part of the **elevated** library layer; scripts should exercise discretion when adding to it, since inclusion implies the content matters enough to be reused or further distilled.
- Architectural principles are conceptually part of Wisdom/Systems but are **operationally loaded** via `Personal/Knowledge/Architecture/principles/**`. N5-local copies (if any) must be treated as mirrors of this canonical source.

---

## 4. Migration Rules (Semantic, Not Mechanical)

> Worker 3 will design and execute the actual steps. This section defines **where things belong**, not how to move them.

### 4.1 Legacy Stable & Semi-Stable Company Canon

- **From:** `Personal/Knowledge/Legacy_Inbox/stable/company/*.md`, `Personal/Knowledge/Legacy_Inbox/stable/{careerspan-timeline.md,glossary.md}`, `Personal/Knowledge/Legacy_Inbox/semi_stable/*.md`.
- **To:**
  - Narrative, public-facing material → `Personal/Knowledge/Canon/Company/`.
  - Internal operational/architectural aspects (e.g., how the knowledge system works) → `Personal/Knowledge/Architecture/specs/`.
  - Time-bound "current state" snapshots →
    - Either `Personal/Knowledge/Canon/Company/Snapshots/` **or** `Personal/Knowledge/Archive/Company_Snapshots/` depending on how live they need to be.
- **Semantic rule:**
  - If the primary question is "What is Careerspan?" → Canon.
  - If the primary question is "How does the system work?" → Architecture.
  - If the primary question is "What was true on date X?" → Archive.

### 4.2 Legacy CRM

- **From:**
  - `Personal/Knowledge/Legacy_Inbox/crm/crm.db` and related indices.
  - `Personal/Knowledge/Legacy_Inbox/crm/individuals/*.md`.
  - `Knowledge/crm/individuals/*.md` + `Knowledge/crm/individuals/index.jsonl`.
- **To:**
  - **SSOT DB:** `Personal/Knowledge/CRM/db/crm.db`.
  - **SSOT profiles:** `Personal/Knowledge/CRM/individuals/*.md`.
  - `Knowledge/crm/individuals/` becomes a *view/mirror* only, potentially containing:
    - Thin stubs that point back to `Personal/Knowledge/CRM/individuals/`.
- **Semantic rule:**
  - All CRM logic (scripts, prompts, specs) should eventually treat `Personal/Knowledge/CRM/` as **the** CRM root.
  - Any divergence between `Knowledge/crm/` and `Personal/Knowledge/CRM/` is a **bug**, not a feature.

### 4.3 Market & GTM Intelligence

- **From:**
  - `Personal/Knowledge/Legacy_Inbox/market/*.md`.
  - `Personal/Knowledge/Legacy_Inbox/market_intelligence/**` (including `gtm_intelligence.db`, `meeting_registry.jsonl`).
  - Any residual `Knowledge/market_intelligence/**` references.
- **To:**
  - `Personal/Knowledge/MarketIntelligence/db/gtm_intelligence.db` (and peers) as SSOT DBs.
  - `Personal/Knowledge/MarketIntelligence/narratives/*.md` for synthesized writeups.
  - `Personal/Knowledge/MarketIntelligence/meeting_registry.jsonl` for registry.
- **Semantic rule:**
  - If the artifact answers "What are we seeing in the market / GTM?" in a reusable way → MarketIntelligence.
  - Meeting-specific raw intel stays under `Personal/Meetings/` and is only referenced.

### 4.4 Patterns, Hypotheses, Reasoning Patterns

- **From:**
  - `Personal/Knowledge/Legacy_Inbox/patterns/*.md`.
  - `Personal/Knowledge/Legacy_Inbox/hypotheses/*.md`.
  - `Personal/Knowledge/Legacy_Inbox/reasoning-patterns/*.md`.
  - `Knowledge/reasoning-patterns/*.md`.
- **To:**
  - `Personal/Knowledge/Frameworks/Patterns/*.md`.
  - `Personal/Knowledge/Frameworks/Hypotheses/*.md`.
- **Semantic rule:**
  - If the file describes a reusable pattern or hypothesis structure → Frameworks.
  - `Knowledge/reasoning-patterns/` becomes a compatibility mirror with stubs or thin copies linking back to Frameworks.

### 4.5 Systems & Infrastructure Docs

- **From:**
  - `Personal/Knowledge/Legacy_Inbox/systems/*.md`.
  - `Personal/Knowledge/Legacy_Inbox/infrastructure/*.md`.
  - Old `Knowledge/architectural/**` exports.
- **To:**
  - `Personal/Knowledge/Architecture/specs/**` (or subtrees like `systems/` and `infrastructure/`).
- **Semantic rule:**
  - If the primary consumer is "someone trying to understand or change the system", it belongs in Architecture.

### 4.6 Intelligence Pipelines & Schemas

- **From:**
  - `Personal/Knowledge/Legacy_Inbox/intelligence/{documents,extracts,media,processed,rejected}/`.
  - `Personal/Knowledge/Legacy_Inbox/schemas/**`.
- **To:**
  - Remain primarily **system-facing**.
  - Optionally, high-level docs about the pipeline/schemas → `Personal/Knowledge/Architecture/specs/`.
- **Semantic rule:**
  - Raw pipeline storage remains under `Legacy_Inbox/intelligence/` or future `Personal/Knowledge/Logs/` until a clearer pipeline design is in place.

### 4.7 Documents/Knowledge/Articles

- **From:** `Documents/Knowledge/Articles/**`.
- **To:**
  - If an article is part of durable canon → `Personal/Knowledge/Canon/{V or Company}/`.
  - If primarily reference content to be surfaced via tools → `Personal/Knowledge/ContentLibrary/content/`.
- **Semantic rule:**
  - One article = one SSOT location; other surfaces link to it.

### 4.8 Legacy `Knowledge/` Tree

- **From:** Whatever remains live under `Knowledge/**` plus expectations in N5 scripts/prefs.
- **To:**
  - `Knowledge/` becomes a *compatibility facade* only:
    - Minimal necessary files to keep high-risk automations running.
    - Explicit `Knowledge/README.md` declaring `Personal/Knowledge/` as SSOT.
  - Full historical copy may be archived under `Personal/Knowledge/Archive/Legacy_Knowledge_Tree/`.
- **Semantic rule:**
  - No new knowledge is authored directly under `Knowledge/`.
  - Any writes to `Knowledge/` by automations are treated as a migration debt to be refactored.

---

## 5. Meeting & Records Interfaces

### 5.1 When Meeting Intelligence "Graduates" to `Personal/Knowledge/`

A meeting-derived insight should be promoted from `Personal/Meetings/` into `Personal/Knowledge/` when it is:

1. **Recurring:** The same pattern or fact appears across ≥3 meetings.
2. **Generalizable:** It’s phrased in a way that applies beyond a single meeting (e.g., segment behavior, stakeholder pattern, GTM lesson).
3. **Decision-Relevant:** It influences product/strategy/relationship decisions going forward.

**Examples:**
- Repeated patterns from `B08_STAKEHOLDER_INTELLIGENCE.md` become:
  - Stakeholder/segment narratives in `Personal/Knowledge/Canon/Stakeholders/`.
  - CRM profile enrichments in `Personal/Knowledge/CRM/individuals/*.md`.
- Repeated GTM lessons from B31/GTm blocks become narratives in `Personal/Knowledge/MarketIntelligence/narratives/`.
- Durable process learnings from meeting retros become frameworks in `Personal/Knowledge/Frameworks/Operational/`.

### 5.2 Promotion Workflow (Conceptual)

1. **Source:** Meeting blocks (B01, B02, B08, B31, etc.) + follow-up artifacts under `Personal/Meetings/**`.
2. **Detection:** N5 workflows scan for recurring entities/patterns across meetings.
3. **Drafting:** Draft promotion notes are created (likely in `Records/Personal/knowledge-system/drafts/` or directly as PR-style changes).
4. **Curation:** V (with AI support) reviews and edits.
5. **Placement:** Finalized insight lands in the appropriate `Personal/Knowledge/` subtree:
   - Canon, Frameworks, CRM, MarketIntelligence, or Architecture.
6. **Linking:** Backlinks are added:
   - From promoted files to the specific meeting IDs and blocks.
   - (Optional) From meetings to the promoted knowledge node.

### 5.3 Role of `Records/` in This Flow

- `Records/` holds:
  - Curation reports.
  - Promotion decisions (what was promoted, what was rejected and why).
  - Migration/mapping docs (like this one).
- Durable outputs live in `Personal/Knowledge/`; `Records/` is the **audit trail**, not the SSOT for knowledge itself.

---

## 6. Open Questions / Design Decisions

1. **Granularity of Canon vs. Architecture:**
   - How strictly should we separate "company story" (Canon) from "system design" (Architecture)?
   - Recommended: Keep them separate but allow cross-links; avoid mixing implementation details into narrative canon.

2. **Snapshots in Canon vs. Archive:**
   - Should historical "current state" snapshots live in `Canon/Company/Snapshots/` (for quick reference) or only under `Archive/`?
   - Recommended: Keep the *latest* snapshot under Canon, move older ones to Archive.

3. **Legacy_Inbox Lifecycle:**
   - How aggressive should we be about draining `Legacy_Inbox/`?
   - Recommended: Treat it as a **time-bounded** staging area (e.g., aim for <12 months). After material is migrated or deemed obsolete, move residuals into `Archive/Legacy_Inbox_Final/`.

4. **Compatibility Guarantees for `Knowledge/`:**
   - Do we want a hard cut-over date after which `Knowledge/` is no longer maintained as a facade?
   - Recommended: Yes, but only **after** high-risk automations have been refactored to `Personal/Knowledge/` roots.

5. **DB Normalization Strategy (CRM & GTM):**
   - How tightly coupled should markdown profiles and DBs be?
   - Recommended: Treat DBs as **implementation detail**; human-readable profiles in `Personal/Knowledge/CRM/individuals/` and `MarketIntelligence/narratives/` are primary for interpretation, with explicit IDs linking to DB rows.

6. **Ownership of N5 Digests:**
   - Should any digests themselves ever be considered canonical knowledge?
   - Recommended: No. Only curated extracts promoted into `Personal/Knowledge/` become canon; digests remain telemetry/history.

7. **Naming Conventions & Namespaces:**
   - Some subtrees (e.g., `Frameworks/Patterns/` vs `Patterns/` as a top-level) could be flattened.
   - Recommended: Start with the nested structure above; if it proves noisy, Worker 3 can propose a refactor before heavy migration.

---

## 7. Metadata Model (Conceptual)

To make Context + Grade operational without over-constraining the folder structure, elevated objects (typically under `Personal/Knowledge/**`) should gradually adopt a common frontmatter schema, for example:

```yaml
grade: knowledge        # data | information | knowledge | wisdom
domain: world           # self | world | systems | relationships | output
stability: time_bound   # transient | time_bound | durable
form: aggregator        # raw | block | aggregator | principle | artifact

external_refs:
  - provider: google_drive
    kind: doc          # doc | sheet | slide | folder | other
    id: "<file_id>"
    url: "https://docs.google.com/document/d/..."
  - provider: notion
    kind: page         # page | block | database
    id: "<page_or_block_id>"
    url: "https://www.notion.so/..."
```

- **DIKW Grade** is tracked via `grade`, not rigid directory splits.
- **Domains** (self/world/systems/relationships/output) cut across all elevated folders.
- **Stability** helps distinguish enduring Wisdom from time-bound Intelligence.
- **external_refs** allows elevated objects to reference canonical or related artifacts stored in Google Drive, Notion, or other systems, so the knowledge system is not limited to local markdown.

This metadata model is descriptive at this stage; Worker 3 and subsequent implementation work will decide how and where to apply it first.

---

**Status:** Design-only. No files have been moved, renamed, or deleted. This document is the reference for Worker 3’s migration and for refactoring N5 preferences to use `Personal/Knowledge/` as the SSOT.


