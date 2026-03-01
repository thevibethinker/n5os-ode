---
created: 2026-02-22
last_edited: 2026-02-22
version: 1.0
provenance: con_AnJxbjm4sme0ShlY
---

# ACP Artifact Audit

## Keep (with edits)
- `REGISTRATION_GUIDE_v2.md`
  - Use as canonical registration copy.
  - Keep pricing ladder at $0.50/$0.75/$1.00.
- `competitive_positioning.md`
  - Keep as hypothesis doc, not as source-of-truth market facts.
- `zode_seller.py`
  - Keep as runtime scaffold; currently not production-complete.
- `conversion_tracker.py`
  - Keep as reporting utility once real jobs start flowing.

## Keep (reference only)
- `REGISTRATION_GUIDE.md`
  - Historical draft; do not use for active execution.
- `PROFILE_OPTIMIZATION_BRIEF.md`
  - Reusable brief for strategy-only worker threads.

## Gaps to resolve before claiming "live"
- Runtime dependency bootstrap missing (`python-dotenv` not installed by default).
- Seller handlers still contain placeholders/TODOs for semantic generation path.
- Discovery/resource claims must be verified before external usage.

## Canonical Execution Files
1. `RESET_PLAN.md`
2. `REGISTRATION_GUIDE_v2.md`
3. `zode_seller.py`
4. `conversion_tracker.py`
