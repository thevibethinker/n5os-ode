---
name: build-close
description: |
  Post-build synthesis for Pulse builds. Aggregates all deposits, synthesizes
  decisions and learnings, extracts positions, generates build AAR.
  Replaces N per-worker closes with 1 build-level close.
  For normal threads use thread-close. For Pulse workers use drop-close.
---

# Build Close

Post-build synthesis for Pulse orchestrated builds.

## When to Use

- After `pulse finalize <slug>` completes
- When all Drops have deposited
- To generate build-level synthesis

**Wrong tool?**
- If normal thread → use `thread-close`
- If you're a Pulse Drop → use `drop-close`

## Quick Start

```bash
# Close a completed build
python3 Skills/build-close/scripts/close.py --slug my-build

# Dry run (preview only)
python3 Skills/build-close/scripts/close.py --slug my-build --dry-run
```

## What It Does

1. **Validates build** — Must exist and be terminal (complete/partial/failed)
2. **Loads all deposits** from `N5/builds/<slug>/deposits/`
3. **Generates title** — 3-slot emoji system for orchestrator thread
4. **Aggregates decisions** — All decisions with rationale across Drops
5. **Aggregates learnings** — Key insights from all workers
6. **Aggregates concerns** — Issues raised by workers
7. **Extracts positions** — Belief candidates from aggregate context
8. **Scans content library** — Reusable artifacts from build
9. **Generates BUILD_CLOSE.md** — Human-readable synthesis
10. **Generates BUILD_AAR.md** — Comprehensive after-action report

## Title Generation (REQUIRED)

After the script outputs aggregated context, you MUST generate a title for the **orchestrator thread** using the 3-slot emoji system.

### Format
```
MMM DD | {state} {type} {content} Build Title
```

### For Build Orchestrators:
- **Slot 1 (State):** Based on build outcome
  - `✅` — All drops complete, no major concerns
  - `⏸️` — Partial completion, work remaining
  - `❌` — Build failed or blocked
- **Slot 2 (Type):** Always `🐙` (orchestrator)
- **Slot 3 (Content):** `🏗️` (build) unless build was primarily something else
- **NO brackets** — Orchestrator threads ARE the parent, don't bracket themselves

### Example Titles
```
Jan 24 | ✅ 🐙 🏗️ Pulse System Validation Build
Jan 24 | ✅ 🐙 🏗️ Close Skills Refactor
Jan 24 | ⏸️ 🐙 🏗️ API Integration (3/5 drops complete)
Jan 24 | ❌ 🐙 🏗️ Auth System Build (blocked on credentials)
```

### Title Generation Steps
1. Load build meta.json for the build title
2. Assess build outcome from deposits:
   - All complete with no concerns → ✅
   - Partial or concerns noted → ⏸️
   - Failed/blocked → ❌
3. Use 🐙 for type (always orchestrator)
4. Use 🏗️ for content (standard for builds)
5. Use the build's title as the semantic portion
6. Add parenthetical if partial/failed explaining why

### Emoji Quick Reference

| Slot | Emoji | Meaning |
|------|-------|---------|
| State | ✅ | Complete, successful |
| State | ⏸️ | Partial, work remaining |
| State | ❌ | Failed/blocked |
| Type | 🐙 | Orchestrator (always for build-close) |
| Content | 🏗️ | Build (default) |
| Content | 🛠️ | Repair-focused build |
| Content | 🔎 | Research-focused build |

## Options

- `--slug` (required): Build slug
- `--dry-run`: Preview without writing files
- `--force`: Bypass guards (use if build not in terminal state)
- `--skip-positions`: Skip position extraction

## Output Files

After running, you'll find:

```
N5/builds/<slug>/
├── BUILD_CLOSE.md    # Human-readable synthesis
├── BUILD_AAR.md      # After-action report
└── deposits/         # (unchanged)
```

## BUILD_CLOSE.md Format

```markdown
# Build Close: my-build

## Summary

Synthesized 7 deposits.

## Decisions (12)

- Chose async over threads: Better for I/O-bound operations
- Used SQLite over Postgres: Simpler deployment for V1
...

## Learnings

- [D1.1] The API requires auth even for public endpoints
- [D2.1] Rate limiting kicks in after 100 req/min
...

## Concerns

- [D1.2] Error handling is incomplete for edge cases
- [D2.3] No tests for the new auth flow
...

## Position Candidates (3)

- [D1.1] "Simple beats clever in production systems" — multiple drops reinforced this
...

## Content Library Candidates (2)

- Artifact: auth-flow-diagram.md
...
```

## Integration with Pulse

Call after Pulse finalization:

```bash
# Standard flow
python3 Skills/pulse/scripts/pulse.py finalize my-build
python3 Skills/build-close/scripts/close.py --slug my-build
```

Or integrate into Pulse finalize step.

## Fail-Safes

This skill includes context guards:

```
⚠️  WRONG SKILL DETECTED

You called: build-close
Suggested:  drop-close
Reason:     Build not in terminal state (status: active)

Run the suggested skill instead, or use --force to override.
```

## Checklist Before Completing

- [ ] Title generated with all 3 emoji slots
- [ ] Title uses 🐙 for orchestrator type
- [ ] Title does NOT have brackets (orchestrator is the parent)
- [ ] BUILD_CLOSE.md written
- [ ] BUILD_AAR.md written (if warranted)
- [ ] All deposits reviewed and synthesized
- [ ] Position candidates extracted (if any)
- [ ] Content library candidates noted (if any)

## Related

- `file 'N5/config/emoji-legend.json'` — Full emoji definitions
- `file 'N5/lib/close/emoji.py'` — Title generation helpers
- `file 'Skills/thread-close/SKILL.md'` — Normal thread close
- `file 'Skills/drop-close/SKILL.md'` — Drop worker close
