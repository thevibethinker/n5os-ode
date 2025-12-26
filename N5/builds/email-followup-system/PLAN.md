---
created: 2025-12-15
last_edited: 2025-12-15
version: 1
type: build_plan
status: draft
---
# Plan: Email follow-up + open-thread tracker

**Objective:** Create a CC- and label-gated email follow-up system that turns open obligations ("I owe" / "they owe") into Akiflow tasks and a daily digest, without scanning V's entire inbox.

**Trigger:** V is dropping email-based commitments across channels (Gmail, LinkedIn, Kondo, etc.) and wants a reliable, motivating loop where any monitored thread turns into concrete Akiflow work items and a focused daily review.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- Surface unknowns HERE at the TOP. Resolve before proceeding. -->
- [ ] Akiflow API details: confirm existing `akiflow_push.py` contract (payload shape, idempotency, rate limits) and whether tasks created by Zo should carry a distinct prefix or tag.
- [ ] Exact CC address convention: confirm whether to treat `va@zo.computer` as the canonical "monitor this thread" CC, or introduce a dedicated alias (e.g. `followup+va@zo.computer`).
- [ ] Gmail label strategy for phase 2: which system labels (e.g. IMPORTANT, STARRED) and/or custom labels (e.g. `N5/Monitor`) should gate non-CC scanning.
- [ ] Where to store the canonical open-thread registry (SQLite vs JSONL under `Lists/`), given performance and query needs.
- [ ] How to handle existing Akiflow tasks created from stars, to avoid duplicating tasks for the same obligation.

---

## Checklist

<!-- Concise one-liners. ☐ = pending, ☑ = complete. Zo updates as it executes. -->

### Phase 1: CC-gated monitored threads → Open-thread registry → Akiflow + daily digest (MVP)
- ☐ Document tagging / CC conventions for "monitored" threads and obligation direction (I owe / they owe) and due dates.
- ☐ Implement CC-gated Gmail ingestion that only processes threads where Zo is CC'd and excludes Promotions / Updates / obvious noise.
- ☐ Implement open-thread registry (single source of truth) with symmetric "I owe" / "they owe" records keyed by Gmail thread id.
- ☐ Implement LLM-based obligation extractor for monitored threads (generous capture, tags as overrides).
- ☐ Integrate with Akiflow via existing `akiflow_push.py` (or equivalent) to create/update tasks for active obligations.
- ☐ Implement a once-daily markdown digest summarizing obligations (3/7/14/30-day lookbacks) for V.
- ☐ Test end-to-end with a small set of CC'd threads and confirm Akiflow + digest both reflect reality.

### Phase 2: Label- and time-window–gated broader scan + cheap triage model
- ☐ Define Gmail label / metadata filters for non-CC scanning (e.g. INBOX + IMPORTANT / STARRED, exclude Promotions/Updates).
- ☐ Implement a cheap triage pass (heuristics + small model) to flag candidate threads with possible obligations.
- ☐ Implement a second-stage higher-precision extractor for triaged candidates, reusing the phase 1 registry + Akiflow pathways.
- ☐ Add time-window lookback logic (3/7/14/30 days) so twice-daily scans can surface overdue or at-risk threads.
- ☐ Extend the daily digest to distinguish CC-sourced obligations vs inferred label-based obligations.
- ☐ Test against a real-day snapshot to ensure noise is acceptable (generous but not overwhelming).

---

## Phase 1: CC-gated monitored threads → Open-thread registry → Akiflow + daily digest (MVP)

### Affected Files
<!-- List EVERY file this phase touches. Format: path - ACTION - brief description -->
- `N5/builds/email-followup-system/PLAN.md` - UPDATE - finalize and maintain this build plan.
- `N5/scripts/gmail_monitor.py` (or analogous Gmail ingestion script) - UPDATE - add CC-based filtering and routing for monitored threads.
- `N5/scripts/email_followup_registry.py` - CREATE - manage the open-thread registry (create/update/close obligations).
- `N5/data/email_followup.db` or `N5/data/email_followup_open_threads.jsonl` - CREATE - canonical storage for open obligations (schema defined in this phase).
- `N5/scripts/email_followup_extractor.py` - CREATE - LLM-based obligation extractor for monitored threads, respecting tags as overrides.
- `N5/scripts/akiflow_push.py` - UPDATE - add helper(s) for creating/updating Akiflow tasks from registry entries (or wrap existing behavior).
- `N5/scripts/email_followup_digest.py` - CREATE - generate once-daily markdown digest from the registry.
- `N5/digests/email-followup-YYYY-MM-DD.md` - CREATE - daily digest artifacts (one per day).
- `N5/config/email_followup.yaml` - CREATE - configuration for CC address, tag patterns, Akiflow options, and digest behavior.

### Changes

**1.1 Define conventions for monitored threads, direction, and due dates**
- Document that any Gmail thread where Zo is CC'd (e.g. `va@zo.computer` or a dedicated alias) is considered a **monitored thread**.
- Within monitored threads, define obligation direction and due dates as follows:
  - Direction overrides via tags (rare, explicit):
    - `[N5F-I-OWE]` → V owes something to the other party.
    - `[N5F-THEY-OWE]` → the other party owes something to V.
  - Due-date overrides via tags: `[N5F-DUE-<days>]` (e.g. `[N5F-DUE-3]`, `[N5F-DUE-7]`, `[N5F-DUE-30]`).
  - Importance override: `[N5F-KEY]` marks must-not-drop threads.
- When tags are absent, treat them as **overrides**, not prerequisites:
  - Use generous LLM-based extraction on recent messages in the thread to infer:
    - Whether there is an obligation.
    - Whether it is "I owe" or "they owe".
    - A reasonable follow-up horizon based on language (e.g. "next week" → 7–10 days).

**1.2 CC-gated Gmail ingestion (privacy-preserving subset)**
- Update or extend the Gmail monitor script (e.g. `gmail_monitor.py`) to:
  - Only consider messages where:
    - Zo is in `Cc` or `To` (CC is the primary signal), AND
    - The message is not labeled as Promotions, Updates, or Spam.
  - Pull the following for each relevant message:
    - `threadId`, `messageId`, `from`, `to`, `cc`, `subject`, `internalDate`, `labelIds`, `snippet` / body, and any user labels.
- For each monitored thread, consolidate metadata into a normalized internal representation (e.g. last 5–10 messages with directions and timestamps) and hand it off to `email_followup_extractor.py`.

**1.3 Open-thread registry (single source of truth)**
- Create `email_followup_registry.py` that exposes functions like:
  - `upsert_obligation(thread_id, direction, kind, due_date, description, importance, source)`.
  - `close_obligations_for_thread(thread_id, reason)`.
  - `list_open_obligations(filter_params)`.
- Choose storage for this MVP (likely SQLite `N5/data/email_followup.db` with a single `open_obligations` table):
  - Columns: `id`, `thread_id`, `direction` (`I_OWE` / `THEY_OWE`), `kind` (deliverable / reply / intro / decision / other), `description`, `created_at`, `last_seen_at`, `due_date`, `importance` (normal / key), `source` (CC / label), `status` (open / closed), `closed_at`, `closed_reason`.
- Ensure registry updates are **idempotent** per `(thread_id, direction, description)` so repeated scans do not create duplicate rows.

**1.4 LLM-based obligation extraction for monitored threads (generous capture)**
- Implement `email_followup_extractor.py` that:
  - Accepts normalized thread content + metadata and the current registry snapshot for that thread.
  - Applies explicit tags first (if present) to set direction, due-date, and importance.
  - When tags are absent, uses a generous LLM prompt to:
    - Identify all current obligations (both "I owe" and "they owe") that are not obviously closed.
    - For each obligation, generate a short description suitable for an Akiflow task.
    - Propose a due date (in days from now) when not overridden.
  - Returns a structured list of obligations to be passed into the registry.
- Incorporate simple heuristics to avoid noise:
  - Ignore obviously informational-only messages (newsletters, pure FYIs) even if CC'd.
  - Prefer the most recent explicit commitment in the thread over stale ones.

**1.5 Akiflow integration (tasks as the concrete work surface)**
- Extend or wrap `akiflow_push.py` to:
  - Create a new Akiflow task when the registry has an open obligation without an associated Akiflow id.
  - Update an existing task (e.g. title, due date) when the obligation changes.
  - Optionally add a prefix/tag like `[Zo Followup]` to distinguish system-created tasks.
- Map registry fields to Akiflow fields:
  - Title: short description, including direction (e.g. `I owe: send deck to Alex (email)` or `Waiting on: Sara – contract revision`).
  - Due date: `due_date` from the registry.
  - Notes: link to Gmail thread (if available) + brief context.
- Ensure deduplication so a single open obligation corresponds to a single Akiflow task.

**1.6 Daily markdown digest (single focused review surface)**
- Implement `email_followup_digest.py` that runs once daily and:
  - Queries the registry for open obligations.
  - Groups items into buckets by age / due date, e.g.:
    - Created/last-touched 3 days ago.
    - 7 days ago.
    - 14 days ago.
    - 30+ days ago.
  - Distinguishes:
    - `I_OWE` vs `THEY_OWE`.
    - `KEY` vs normal.
    - Source: `CC` (phase 1) vs `LABEL` (phase 2, future field).
- Output path: `N5/digests/email-followup-YYYY-MM-DD.md` with:
  - Clear sections for `I owe` and `They owe`.
  - Subsections by lookback bucket.
  - Links or references back to Akiflow tasks and/or Gmail threads where possible.
- No direct sending in this phase; the digest lives in N5 and can later be emailed or surfaced elsewhere.

### Unit Tests
<!-- Tests for THIS phase. Run after phase completion. -->
- **Test 1: CC-gated privacy** — Send multiple test emails, some with Zo CC'd and some without. Verify only CC'd threads appear in the registry and digests.
- **Test 2: I owe / they owe symmetry** — Use a monitored thread where V makes a commitment and another where the counterparty makes a commitment. Confirm both obligations are captured with correct direction and due dates.
- **Test 3: Tag overrides** — Add `[N5F-I-OWE]`, `[N5F-THEY-OWE]`, `[N5F-DUE-7]`, and `[N5F-KEY]` to monitored threads and confirm they override LLM inference.
- **Test 4: Akiflow task creation** — For several open obligations in the registry, run the Akiflow integration and confirm one corresponding task per obligation is created with the right title and due date.
- **Test 5: Daily digest content** — Generate a digest after seeding the registry with obligations at different ages and directions. Confirm grouping (3/7/14/30+ days) and separation (`I owe` vs `they owe`) looks correct.

---

## Phase 2: Label- and time-window–gated broader scan + cheap triage model

### Affected Files
- `N5/config/email_followup.yaml` - UPDATE - add label filters, triage thresholds, and time-window settings.
- `N5/scripts/gmail_monitor.py` - UPDATE - add label-based candidate selection for non-CC threads, respecting configured filters.
- `N5/scripts/email_followup_triage.py` - CREATE - implement cheap heuristic + small-model triage for potential obligations.
- `N5/scripts/email_followup_extractor.py` - UPDATE - support triage-mode inputs and reuse extraction logic for non-CC threads.
- `N5/scripts/email_followup_registry.py` - UPDATE - add fields/flags to distinguish CC vs label-sourced obligations and triage confidence.
- `N5/scripts/email_followup_digest.py` - UPDATE - extend digest sections to reflect label-based obligations and confidence levels.

### Changes

**2.1 Define Gmail label / metadata filters and time windows**
- In `email_followup.yaml`, configure which Gmail labels and axes are eligible for non-CC scanning, for example:
  - Include: `INBOX`, `SENT`, `IMPORTANT`, `STARRED`.
  - Exclude: `CATEGORY_PROMOTIONS`, `CATEGORY_UPDATES`, `SPAM`, `TRASH`.
  - Optionally include a custom label like `N5/Monitor` for future precision.
- Implement time-window configuration for twice-daily scans:
  - Each run considers messages whose `internalDate` falls into the relevant lookback buckets relative to **today**: 3, 7, 14, 30+ days.
  - This supports the "scan relative to today" behavior V described (each day sweep 3/7/14/30 days back and resurface open items).

**2.2 Cheap triage model for large-scale scanning**
- Create `email_followup_triage.py` that:
  - Operates on candidate messages/threads selected by label filters.
  - Uses a **cheap first pass** consisting of:
    - Deterministic heuristics (presence of request/commitment phrases, reply-to patterns).
    - A small LLM model or reduced-context prompt to score likelihood that the thread contains an obligation.
  - Marks candidates above a configurable confidence threshold as `triage_candidate = True` and forwards only those to the full extractor (`email_followup_extractor.py`).
- Ensure triage is tuned to be **generous** at first (allowing some false positives) to substantially shrink the search space without missing many real obligations.

**2.3 Second-stage extraction + registry / Akiflow reuse**
- Reuse the phase 1 extraction/registry/Akiflow pipeline for triaged candidates:
  - For each triaged thread, run `email_followup_extractor.py` to identify concrete obligations.
  - Update the registry with `source = LABEL` and a `triage_confidence` field.
  - Create/update Akiflow tasks exactly as in phase 1; avoid duplicating tasks where obligations already exist from CC-based monitoring.

**2.4 Extend daily digest with triage information**
- Update `email_followup_digest.py` so the daily markdown includes:
  - Separate or clearly labeled subsections for:
    - CC-sourced obligations.
    - Label/triage-sourced obligations.
  - Optional indicators of triage confidence for label-sourced items.
- Keep the **surface** focused by default:
  - Continue grouping by 3/7/14/30-day lookbacks.
  - Respect a maximum number of surfaced items per bucket (configurable) and prioritize:
    - `KEY` obligations.
    - Sooner due dates.
    - Higher triage confidence for label-sourced items.

### Unit Tests
- **Test 6: Label filtering** — Seed test messages with different Gmail labels and verify only the configured labels are eligible for triage.
- **Test 7: Triage generosity** — Run triage on a mixed set of real-ish messages and confirm it captures the majority of true obligations while reducing the number of threads that hit the full extractor.
- **Test 8: Registry deduplication across CC + labels** — Create obligations for a thread via CC and then via label-based triage, and ensure the registry maintains a single logical obligation and a single Akiflow task.
- **Test 9: Time-window behavior** — Simulate runs on different days and verify the 3/7/14/30-day lookbacks select the expected obligations.
- **Test 10: Digest clarity with mixed sources** — With both CC and label-based obligations present, generate a daily digest and confirm sections are understandable and not overwhelming.

---

## Success Criteria

<!-- How do we know we're done? Measurable outcomes. -->
1. For any email thread where V CCs Zo and makes or receives a clear commitment, there is a corresponding open obligation in the registry **within one scan cycle** and a matching Akiflow task.
2. Daily digest `email-followup-YYYY-MM-DD.md` is generated successfully every day, clearly separating `I owe` vs `they owe` and grouping obligations into 3/7/14/30-day lookbacks.
3. The system **never processes non-monitored threads in phase 1**, and phase 2 only processes threads matching explicitly configured label filters (privacy preserved).
4. Triaged label-based scanning (phase 2) reduces the number of full-extraction threads by at least 70% while missing no more than a small, acceptable fraction of true obligations (to be tuned with real data).
5. No duplicate Akiflow tasks exist for the same obligation; closing or resolving an obligation is reflected both in the registry and in Akiflow.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Overwhelming number of surfaced obligations (especially once label-based scan is enabled) | Start with CC-only monitoring (phase 1) and generous but still filtered triage in phase 2; cap the number of items surfaced per digest section and prioritize `KEY` + soonest due dates. |
| Misclassification of direction (I owe vs they owe) or spurious obligations | Use tags as explicit overrides; iterate on the extractor prompt with real examples; log and review misclassifications to refine heuristics and prompts. |
| Privacy concerns from scanning too much of the inbox | Phase 1 strictly CC-gated; phase 2 gated by explicit label filters and categories (exclude Promotions/Updates/Spam), with configuration documented and reviewable. |
| Duplicate or noisy Akiflow tasks | Enforce idempotent mapping from registry obligation to Akiflow task id; include simple duplicate detection (same thread, direction, and description) before creating new tasks. |
| Performance / cost of large-scale LLM scanning | Use a cheap triage pass plus strict label filters; cache thread analyses where possible and avoid reprocessing unchanged threads. |

---

## Level Upper Review

<!-- Architect invokes Level Upper before finalizing. Document the divergent input here. -->

### Counterintuitive Suggestions Received:
1. Use CC-based monitoring as the **only** hard privacy boundary in phase 1, and treat label-based scanning as an explicitly opt-in expansion documented in `email_followup.yaml`.
2. Treat Akiflow as the *only* task sink for this system (no secondary lists) to avoid fragmentation of where "work" lives.

### Incorporated:
- CC-based monitoring as the phase 1 privacy boundary with no other threads processed.
- Akiflow as the single concrete work surface, with the registry + digest serving as internal infrastructure and review aids.

### Rejected (with rationale):
- Idea: Build a completely separate visual dashboard before Akiflow integration. **Why rejected:** Akiflow already serves as V's canonical task manager; a separate dashboard would add complexity and another place to check, violating the simplicity principle. The markdown digest plus Akiflow tasks are sufficient for v1.


