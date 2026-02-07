---
created: 2026-02-01
last_edited: 2026-02-01
version: 1.2
provenance: con_Cb3e3rZrJTKYFxn3
type: build_plan
status: ready
---

# Plan: Pulse — Waves schema rename + manual-drop launcher + Sentinel reliability

**Objective:** Update Pulse’s schema + scheduling to match V’s model (Waves/Streams/Drops) while preserving backward compatibility for existing builds, add `blocking: false` semantics, and improve manual-drop ergonomics + auto/manual recommendations + Sentinel diagnostics.

**Trigger:** V clarified desired model:
- Streams are sequential workflows
- Drops are one-conversation-sized units
- Waves are hard-barrier “rounds” of parallel work across streams
- Some drops are non-blocking and should not hold wave advancement
- Manual drops must be impossible to “forget” (clear `awaiting_manual` status + launcher artifact)

**Key Design Principle:** **Simple > Easy.** Add a compatibility adapter so we can support v3 without migrating old build folders.

---

## Decisions (resolved)

1) **Wave semantics:** ✅ **Hard barrier**. A later wave cannot start until:
   - all **blocking** drops in the current wave are complete **and**
   - all streams’ work for that wave is done (equivalently: all blocking drops in that wave complete; non-blocking may remain).

2) **Non-blocking drops:** ✅ Implement **now** via `blocking: false`.

3) **Centralization:** ✅ Launcher + briefs live in the build folder (`N5/builds/<slug>/...`). Orchestrator thread references those files. No mirroring into conversation workspace.

4) **Stream-level manual defaults:** ✅ **Not in v1.** Keep manual/auto at **drop level only**.

---

## Checklist

### Phase 1: Schema + scheduler rename (Currents → Waves; Streams sequential; blocking semantics)
- ☐ Define v3 meta schema (`schema_version: 3`, `waves`, drop fields incl. `blocking`)
- ☐ Implement backward-compat adapter for v1/v2 (`currents`, `current_stream`, etc.)
- ☐ Replace legacy “Current” scheduling with Wave barrier scheduling (respecting `blocking:false`)
- ☐ Enforce per-stream sequential ordering by drop order
- ☐ Harden drop-id parsing (support stream numbers ≥10)
- ☐ Update `STATUS.md` output to report Wave + manual wait states
- ☐ Tests: wave barrier + non-blocking bypass + stream ordering

### Phase 2: Manual-drop launcher + auto/manual recommendation
- ☐ Generate launcher artifact for manual drops when they become ready
- ☐ Add `pulse.py launch <slug> <drop_id>` to print the launcher prompt + file path
- ☐ Add recommender (heuristics-first; optional LLM) to propose manual vs auto
- ☐ Ensure manual drops block progression unless explicitly `blocking:false`
- ☐ Tests: launcher created + awaiting_manual surfaced + blocker behavior

### Phase 3: Sentinel reliability + smoke tests
- ☐ Improve sentinel diagnostics (token present? build list? tick error?)
- ☐ Add `sentinel.py --dry-run` (no mutations) + `pulse.py notify-test` (or equivalent)
- ☐ Smoke test: sentinel tick loop does not crash and reports actionable output

---

## Phase 1: Schema + scheduler rename

### Affected Files
- `Skills/pulse/scripts/pulse.py` - UPDATE - implement wave scheduler + blocking semantics; fix parsing; update status rendering
- `Skills/pulse/scripts/pulse_common.py` - UPDATE - add meta normalization helpers shared across scripts
- `Skills/pulse/SKILL.md` - UPDATE - canonical terminology + new meta schema documentation
- `Skills/pulse/references/` - CREATE/UPDATE - terminology mapping + updated templates (if needed)

### Changes

**1.1 Introduce schema versioning + normalization (no migration of old builds):**
- Add `schema_version` inference:
  - missing → treat as legacy
  - `3` → new wave model
- Add a normalization function (in `pulse_common.py`) that returns an in-memory normalized representation used by the scheduler.

**1.2 Replace “Currents” with “Waves” (hard barrier):**
- New field: `waves`.
- New scheduling rule:
  - Determine the **active wave** as the earliest wave with any *blocking* drop not complete.
  - Only consider drops from the active wave for spawning.

**1.3 Implement `blocking: false`:**
- Default: `blocking: true` if absent.
- Wave completion condition:
  - Wave is considered “done” when **all blocking drops in that wave** are terminal-success (complete) OR terminal-failure (failed/dead) per policy.
  - Non-blocking drops do **not** prevent wave advancement.

**1.4 Enforce stream sequential ordering:**
- Within a stream, drops run in ascending `order`.
- If `order` is absent, infer from drop id `D<stream>.<order>`.

**1.5 Fix fragile parsing:**
- Replace `int(drop_id[1])` parsing with robust parsing supporting multi-digit stream ids.

### Tests
- Wave barrier:
  - With `W1=[D1.1,D2.1]`, `W2=[D1.2,D2.2]`, only W1 drops spawn first.
- Non-blocking:
  - If `D1.1.blocking=false` and it’s still running, wave can advance once all *blocking* drops in W1 complete.
- Stream order:
  - `D1.2` cannot spawn until `D1.1` complete, even if both are in the same wave.

---

## Phase 2: Manual-drop launcher + recommendation

### Affected Files
- `Skills/pulse/scripts/pulse.py` - UPDATE
- `Skills/pulse/SKILL.md` - UPDATE

### Changes

**2.1 Launcher artifact generation:**
- For any ready drop with `spawn_mode: manual`:
  - set status `awaiting_manual`
  - write launcher file: `N5/builds/<slug>/launchers/<drop_id>.md`
  - update `STATUS.md` with the exact next step

**2.2 `pulse.py launch <slug> <drop_id>` command:**
- Prints the launcher path and the “paste into new thread” prompt.

**2.3 Recommender:**
- Heuristics-first; optional LLM.
- Writes recommendation into meta + status output.

**2.4 Blocking behavior:**
- Manual drops are treated like any other drop: if `blocking:true`, the wave will not advance until the deposit arrives and passes completion state.

---

## Phase 3: Sentinel reliability

### Affected Files
- `Skills/pulse/scripts/sentinel.py` - UPDATE
- `Skills/pulse/scripts/pulse.py` - UPDATE (if needed)

### Changes
- Add `--dry-run` to sentinel.
- Add a notification self-test.
- Improve diagnostics in stdout (and optionally `STATUS.md` append).

---

## Success Criteria

1. A v3 build using Waves executes with correct barrier semantics and stream sequential ordering.
2. `blocking:false` drops do not block wave advancement.
3. Manual drops create launcher artifacts and cannot be silently skipped.
4. Existing legacy builds still run without rewriting their `meta.json`.
5. Sentinel has a repeatable smoke test and produces actionable diagnostics.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Confusion between legacy “current_stream” and new wave barrier | Compatibility adapter + avoid relying on `current_stream` for scheduling in v3. |
| `blocking:false` creates partial/fuzzy completion states | Make status output explicit: “Wave advanced with N non-blocking drops still running.” |
| Manual drops accidentally set `blocking:false` and allow wave advancement | Status output should highlight any manual+nonblocking combination as ⚠️. |

---

## Next Step

Proceed to Phase 1 implementation in `file 'Skills/pulse/scripts/pulse.py'` + `file 'Skills/pulse/scripts/pulse_common.py'`.
