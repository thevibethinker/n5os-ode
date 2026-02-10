---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
provenance: con_8HSoybIvJ0AA2vPW
---

# Smart Sentinel: Recovery Engine for Pulse

## Open Questions

None — strategy session resolved design decisions. Option 1 (Smart Sentinel with deterministic rules + AI judgment fallback) selected by V.

## Checklist

### Phase 1: Recovery Engine Core
- ☐ Add RECOVERY_DEFAULTS to pulse_common.py
- ☐ Add `assess_and_recover()` function to pulse.py
- ☐ Add `_classify_failure()` helper to pulse.py
- ☐ Add `_log_recovery_action()` helper to pulse.py (RECOVERY_LOG.jsonl)
- ☐ Add `_check_build_stale()` helper to pulse.py
- ☐ Add `_check_wave_death()` helper to pulse.py
- ☐ Test: verify recovery rules R1-R5 trigger correctly

### Phase 2: Sentinel Integration
- ☐ Update sentinel.py to call assess_and_recover after tick
- ☐ Add recovery summary to sentinel output
- ☐ Test: sentinel dry-run shows recovery candidates

### Phase 3: STATUS.md + Docs
- ☐ Update `update_status_md()` in pulse.py to show recovery indicators
- ☐ Update SKILL.md with Smart Sentinel documentation
- ☐ Update escalation-protocol.md with recovery events
- ☐ Add sentinel-recovery-template to SKILL.md

## Phase 1: Recovery Engine Core

### Affected Files
- `Skills/pulse/scripts/pulse_common.py` — add RECOVERY_DEFAULTS
- `Skills/pulse/scripts/pulse.py` — add assess_and_recover + helpers

### Changes

**pulse_common.py:**
Add recovery defaults dict:
```python
RECOVERY_DEFAULTS = {
    "max_auto_retries": 2,
    "dead_threshold_seconds": 900,
    "stale_threshold_hours": 4,
    "stale_no_progress_minutes": 60,
    "enable_ai_judgment": True,
}
```

**pulse.py — new functions:**

1. `_classify_failure(drop_id: str, info: dict, slug: str) -> str`
   - Returns one of: "dead_timeout", "spawn_error", "content_error", "unknown"
   - Reads failure_reason/dead_reason to classify
   - "spawn_error" if reason contains "Spawn error", "API returned", "timeout"
   - "dead_timeout" if status == "dead"
   - "content_error" if deposit exists with status blocked/partial
   - "unknown" otherwise

2. `_log_recovery_action(slug: str, action: dict) -> None`
   - Appends to `N5/builds/<slug>/RECOVERY_LOG.jsonl`
   - Action dict: {timestamp, drop_id, rule, action, reason, retry_number}

3. `_check_build_stale(slug: str, meta: dict) -> bool`
   - Checks if build has been active > stale_threshold_hours
   - AND no Drop status changed in last stale_no_progress_minutes
   - Uses `last_progress_at` field on meta (set whenever a Drop changes status in tick)

4. `_check_wave_death(meta: dict) -> bool`
   - Returns True if ALL blocking Drops in current wave are dead/failed AND all have retry_count >= max_auto_retries

5. `assess_and_recover(slug: str, meta: dict = None) -> list[dict]`
   - Main entry point. Loads meta if not provided.
   - Gets recovery config (meta.recovery merged with RECOVERY_DEFAULTS)
   - Iterates drops, applies rules R1-R5:
     - R1: dead + retry_count < max → call retry_drop, log action
     - R2: failed + spawn_error + retry_count < max → call retry_drop, log action
     - R3: failed + content_error → append to "needs_judgment" list
     - R4: wave death → set build status "blocked", append escalation
     - R5: stale build → append escalation
   - Saves meta after all mutations
   - Updates STATUS.md
   - Returns list of actions taken (for sentinel reporting)

**Also in tick():** Add `meta["last_progress_at"] = now.isoformat()` wherever a Drop status changes (the existing spots where `broadcasts_updated = True`).

### Unit Tests
- Verify R1: mock dead drop with retry_count=0 → assess_and_recover returns auto_retry action
- Verify R1 cap: mock dead drop with retry_count=2 → no auto_retry, returns escalation
- Verify R4: all Wave drops dead+maxed → build status set to "blocked"
- Verify recovery log written to RECOVERY_LOG.jsonl

## Phase 2: Sentinel Integration

### Affected Files
- `Skills/pulse/scripts/sentinel.py`

### Changes

After the `asyncio.run(tick(slug))` call, add:
```python
from pulse import assess_and_recover

actions = assess_and_recover(slug)
if actions:
    retries = [a for a in actions if a["action"] == "auto_retry"]
    escalations = [a for a in actions if a["action"] == "escalate"]
    judgments = [a for a in actions if a["action"] == "needs_judgment"]
    
    if retries:
        print(f"[SENTINEL] Auto-retried {len(retries)} drop(s): {', '.join(a['drop_id'] for a in retries)}")
    if escalations:
        print(f"[SENTINEL] Escalations: {len(escalations)}")
    if judgments:
        print(f"[SENTINEL] Needs AI judgment: {len(judgments)}")
```

Add `--dry-run` support for recovery assessment (report candidates without acting).

### Unit Tests
- Verify sentinel calls assess_and_recover after tick
- Verify dry-run skips recovery

## Phase 3: STATUS.md + Docs

### Affected Files
- `Skills/pulse/scripts/pulse.py` — update_status_md function
- `Skills/pulse/SKILL.md` — documentation
- `Skills/pulse/references/escalation-protocol.md` — new recovery events

### Changes

**update_status_md():**
Add a "### 🔄 Recovery Actions" section when RECOVERY_LOG.jsonl has recent entries (last tick cycle). Show:
- Which drops were auto-retried and attempt number
- Which drops need judgment
- Which drops are escalated

**SKILL.md:**
Add "## Smart Sentinel (Recovery)" section documenting:
- Recovery rules R1-R5
- Configuration options (meta.json `recovery` field)
- RECOVERY_LOG.jsonl format
- Enhanced sentinel agent prompt template

**escalation-protocol.md:**
Add recovery-specific events:
- Drop auto-retried (INFO)
- Drop retry exhausted (HIGH)
- Build blocked — all wave drops failed (CRITICAL)
- Build stale (HIGH)

### Unit Tests
- Verify STATUS.md includes recovery section when actions exist

## Success Criteria

1. Dead Drops with retry_count < 2 are auto-retried within 1 tick cycle
2. RECOVERY_LOG.jsonl captures every recovery action with provenance
3. STATUS.md shows recovery indicators (🔄 retrying, ⚠️ needs attention)
4. Drops that fail 2x are NOT retried — they escalate
5. Wave death detection marks build as "blocked"
6. Stale build detection after 4h with no progress
7. `pulse stop` still kills everything instantly (no interference)
8. Existing tests and behavior unchanged for builds without failures

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Auto-retry infinite loop | Hard cap MAX_RETRIES=2, enforced in assess_and_recover |
| Retrying a Drop that failed for good reason | R3 separates content failures → AI judgment, not auto-retry |
| Recovery interferes with manual intervention | recovery_source field distinguishes auto vs manual |
| tick() + assess_and_recover double-save meta | assess_and_recover is called AFTER tick, reads fresh meta |

## Trap Doors

**None identified.** All changes are additive:
- New functions added, existing functions unchanged except minor additions
- New fields on meta are optional (old builds work without them)
- RECOVERY_LOG.jsonl is append-only
- Can be disabled per-build via `recovery.max_auto_retries: 0`

## Alternatives Considered

1. **Pure tick() enhancement** — Add retry logic directly into tick(). Rejected: complects tick's state machine with recovery decisions. Simpler to keep them separate.
2. **Full Sentinel-as-Orchestrator** — Move all orchestration into the Sentinel agent prompt. Rejected: too much risk for first iteration. Smart Sentinel is a stepping stone.
3. **Recovery as separate script** — `pulse_recovery.py`. Rejected: recovery needs to read/write the same meta.json as tick, so co-locating in pulse.py avoids import complexity.
