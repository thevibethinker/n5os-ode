---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: con_AVUiANpq2GYAc3Qz
type: worker_assignment
worker_id: W2_SEMANTIC_LINKING
parent_build: position-system-overhaul
sequence: 2
depends_on: WORKER_c3Qz_20260115_232953
adapted_from: N5/builds/vrijenattawar-domain-transition/workers/E-position-connections-linking.md
execution_mode: independent
---

# Worker 2: Semantic Position Linking (Adapted + Upgraded)

**Objective:** Reduce orphan rate by adding high-quality, typed connections between positions. Use embeddings for candidate discovery + LLM for relationship typing. This intentionally surfaces “weak” positions by revealing which ones cannot connect.

---

## Confirm / Challenge V’s Guess (Don’t blindly follow)

V guessed: “The Worker E approach is too simplistic and we need something much more sophisticated.”

✅ **Confirmed.** Worker E is a strong *seed*, but it’s incomplete for this system because:
1. It defaults to a generic `related_to` relationship (low semantic value)
2. It doesn’t enforce JSON hygiene / idempotency
3. It doesn’t preserve existing hand-crafted semantic edges
4. It doesn’t separate **candidate discovery** (fast) from **relationship judgment** (slow + high-value)

So we will keep Worker E’s *core idea* (embeddings for nearest neighbors) but upgrade everything around it.

---

## Preconditions (Sequential Dependency)

This worker MUST start only after Worker 1 is completed, because it depends on:
- Backup-before-write (`position_backup.py`)
- Dry-run/apply protocol
- Idempotency guards
- JSON validation for existing `connections`

If W1 is incomplete, STOP and report back; do not proceed.

---

## Current Data Reality (Must be verified at runtime)

At runtime, compute:
- total positions
- orphan positions count
- whether `connections` fields are valid JSON arrays

We previously observed ~164 positions and ~87% orphans, but you MUST re-check.

---

## Target Outputs

1. `N5/scripts/position_linker_v2.py` (or similarly named) implementing:
   - `--dry-run` outputs proposed changes
   - `--apply` writes to db (after backup)
   - `--sample N` for staged rollout
   - `--threshold` for similarity cutoff
   - checkpointing (`.json` checkpoint file)

2. `N5/builds/position-system-overhaul/linking_report.md` containing:
   - orphan rate before/after
   - # edges added
   - breakdown by relationship types
   - list of positions still orphaned (weak candidates)

3. Updated position graph visualization
   - regenerate HTML
   - ensure it is served via existing `position-viz` service (don’t create new service unless needed)

---

## Algorithm

### Step A — Candidate Discovery (Embeddings)
- Embed each position using `title + insight`
- For each orphan position, find top K neighbors by cosine similarity
- K default: 5
- Similarity threshold default: 0.70

### Step B — Relationship Typing (LLM)
For each proposed neighbor pair (A→B), ask LLM to choose one of:
- implies
- supports
- contradicts
- extends
- prerequisite
- none

Return JSON: `{relationship, confidence, reasoning}`

Apply only if confidence ≥ 0.75 and relationship != none.

### Step C — Apply Connections (Idempotent)
- Preserve existing edges
- Do not add duplicates
- Store as JSON array in `connections`

---

## “Expose Weak Positions” Behavior

If a position has no neighbors above threshold OR all relationships come back as `none`, keep it orphaned and add it to the “Weak/Unanchored” list. This is *desired output*.

---

## Safety / Discipline Requirements

- Backup before apply
- Always dry-run first
- First apply should be `--sample 10`
- Provide HITL review markdown for the first 50 edges before applying the rest

---

## Completion Criteria

- orphan rate drops materially (target <30%, or at least a clear improvement)
- relationships are typed (no `related_to`)
- report created and accurate

---

## Reporting Back

Because execution_mode is “independent,” at completion:
- Write a concise summary back to the parent conversation
- Include exact file paths for artifacts
