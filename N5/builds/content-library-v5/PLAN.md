---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.1
provenance: con_GiPSVev8LxpKdAcO
type: build_plan
status: draft
build_slug: content-library-v5
---

# Plan: Content Library v5 Upgrade

## Objective (1 sentence)
Upgrade the Content Library so that (1) ingest produces **clean original text + short summary** (no raw web scrape), (2) filesystem content and DB are always consistent (incl. Calendly), and (3) contextual metadata accumulates safely over time (defaults written, curated context never overwritten).

## Trigger
V observed broken ingest behavior (raw scrape stored as “article/link”), Calendly sync generating high-quality files but not populating DB, and systemic file↔DB drift.

## Ground Truth Requirements (from V)
- **Normalization standard:** **B = clean original text + short summary in frontmatter**.
- **No garbage scrape:** Keep only the content text we need (article text, profile bio/overview, etc.).
- **Calendly:** must be in DB *and* files; include “context around when to use.”
- **Context merge policy:** Hybrid — write defaults, draw from existing context, **never overwrite existing curated context**.
- **Schema changes allowed.**
- **Content Library role:** first port of call for assets/resources to share (not the routing brain).

---

## Open Questions (must be answered in design, not by V)
1. **Canonical source of truth:** DB is canonical index; files are canonical artifacts. How do we guarantee deterministic sync without duplication?
2. **Stable IDs:** Should items have stable `id` derived from (type + subtype + slug) vs UUID?
3. **Normalization engine:** Prefer Python libs (readability-lxml / trafilatura) vs deterministic heuristics? (Must be reproducible and cheap.)

---

## Work Strategy (phased)

### Phase 1 — Spec + Architecture
Define taxonomy, frontmatter schema, merge semantics, and invariants; decide migration approach.

### Phase 2 — Core implementation
Schema migrations + ingest/normalize pipeline + Calendly DB integration.

### Phase 3 — Sync/Backfill & consistency tooling
Make `sync` reliable; detect + repair orphans; ensure Calendly is picked up.

### Phase 4 — Docs + operator workflows
Update system guide and add clear “how to add X” workflows.

---

## Invariants / Success Criteria
1. **No raw scrape stored:** Ingest never writes nav/boilerplate; saved content is clean text + summary.
2. **Calendly parity:** Every active Calendly event type has (a) a canonical md file and (b) a DB item referencing it.
3. **Sync correctness:** `content_library.py sync` achieves a stable fixed point (run twice = no changes).
4. **Non-destructive enrichment:** Existing contextual fields are never overwritten by automation.
5. **Developer ergonomics:** One recommended CLI path per intake type (url→link/profile/resource, save_webpage→article, media→companion md).

---

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Duplicate items from inconsistent IDs | Define stable ID/slug rules + uniqueness constraints + dedupe logic |
| Overwriting curated context | Field-level merge strategy: “only fill empty” + explicit `managed_fields` |
| Hard-to-reproduce cleaning | Prefer deterministic extraction pipeline; log normalization decisions |
| Breaking legacy callers of `content_library.py` | Add compatibility layer + gradual migration; keep old API stable |

---

## Worker Briefs

| Wave | Worker | Thread Title | Brief File |
|------|--------|--------------|------------|
| 1 | W1.1 | [content-library-v5] W1.1: Spec (taxonomy + frontmatter + merge semantics) | `workers/W1.1-spec.md` |
| 1 | W1.2 | [content-library-v5] W1.2: DB schema + migrations + API alignment | `workers/W1.2-db-schema-and-api.md` |
| 1 | W1.3 | [content-library-v5] W1.3: Ingest v5 (clean text + summary; no raw scrape) | `workers/W1.3-ingest-normalization.md` |
| 1 | W1.4 | [content-library-v5] W1.4: Calendly sync → DB (non-destructive enrichment) | `workers/W1.4-calendly-db-sync.md` |
| 2 | W2.1 | [content-library-v5] W2.1: Sync/backfill correctness + repair tooling | `workers/W2.1-sync-backfill-tooling.md` |
| 2 | W2.2 | [content-library-v5] W2.2: Migration/dedupe for existing library items | `workers/W2.2-migration-dedupe.md` |
| 2 | W2.3 | [content-library-v5] W2.3: Documentation + operator workflows | `workers/W2.3-docs-and-workflows.md` |

---

## Test Plan (high-level)
- **Golden file tests:** Known inputs (save_webpage article md/html, GitHub profile html) → expected clean text output.
- **Calendly fixture test:** Fake event_types payload → generates md + DB record; re-run is idempotent.
- **Sync idempotence:** Run `sync` twice; second run produces 0 changes.
- **Merge policy tests:** If file/frontmatter contains `audience`, automation must not overwrite; only fill missing.

---

## Files Likely to Change (initial list)
- `N5/scripts/content_ingest.py`
- `N5/scripts/content_backfill.py`
- `N5/scripts/content_library.py`
- `Integrations/calendly/sync_links.py`
- `Documents/System/guides/content-library-system.md`
- `N5/data/content_library.db` (via migrations)

---

## Execution Notes
- Workers **must not commit**.
- Workers write completion reports to `N5/builds/content-library-v5/completions/<worker_id>.json`.
- Orchestrator (this thread) aggregates completions, adapts briefs for Wave 2, then commits at final close.
