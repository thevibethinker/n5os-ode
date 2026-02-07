---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_LhnxuEVVapCNdXle
---

# Build Principles (Pulse v2)

## Orchestration

1. **Skills over Prompts**: All new capabilities built as Skills in `Skills/`, not prompts in `Prompts/`
2. **Local-first with Outposts**: Source of truth is workspace. External services (Drive, etc.) are shareable outposts
3. **Graceful Degradation**: Every external integration has a local fallback

## Planning

1. **Light Initial, Detailed Later**: Start with structure, add detail as build progresses
2. **Interview Gate**: No build starts without human seed tokens
3. **Plan Review Gate**: No execution without explicit approval

## Execution

1. **Flat over Nested**: Prefer `Skills/pulse/scripts/file.py` over `Skills/pulse/scripts/category/file.py`
2. **JSONL for Logs**: Append-only logs use JSONL format
3. **Model Attribution**: All telemetry includes persona + model

## Quality

1. **Tidying Swarm**: Every build ends with hygiene checks
2. **Teaching Integration**: Learning opportunities surfaced, not forced
3. **Feedback → Learnings**: V's feedback becomes system improvement via lesson ledger

## Building Fundamentals (P35-P39)

Core principles from programming fundamentals, adapted for N5/Zo. See `file 'Personal/Knowledge/Architecture/principles/P35-P39_building_fundamentals.md'` for full details.

1. **Version, Don't Overwrite (P35)**: Input artifacts are immutable; transforms create new outputs
2. **Make State Visible (P36)**: Declare state dependencies; validate before proceeding
3. **Design as Pipelines (P37)**: Clear stages; any stage can re-run from its inputs
4. **Isolate & Parallelize (P38)**: Workers don't share state; proactively recommend Pulse for large tasks
5. **Audit Everything (P39)**: Every output traceable to its source, trigger, and timestamp

### Application to Pulse Builds

- **P35 in Pulse:** Drops write to `deposits/` (new files), never modify shared state
- **P36 in Pulse:** `meta.json` is explicit state; drops validate build exists before working
- **P37 in Pulse:** Streams are pipeline stages; each stream's deposits feed the next
- **P38 in Pulse:** Worker isolation is enforced; lesson ledger is the only cross-drop channel
- **P39 in Pulse:** Every deposit has provenance; BUILD_LESSONS.json captures learnings

## Reference

- Pulse v2 Skill: `Skills/pulse/SKILL.md`
- Build config: `Skills/pulse/config/pulse_v2_config.json`
- Operational guidelines: `N5/prefs/operations/pulse_v2_guidelines.md`
