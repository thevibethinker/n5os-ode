# Zo Setup Foundation Rubric (v1)

Reference: file N5.md

Purpose: score the foundational setup of Zo Computer and N5 OS on a weighted 0–10 scale.

Scoring scale
- 10: Fully designed, tested, and documented; resilient and auditable
- 7–9: Strong foundation, minor gaps or untested edge cases
- 4–6: Partial; key elements exist but lack rigor, validation, or docs
- 1–3: Weak; ad hoc or brittle, little safety
- 0: Not set

Criteria (weights sum to 100%)
1) Core OS structure & indexing — 10%
- 10: N5 present, index/update working, command catalog current
- 5: N5 present, index occasionally stale
- 0: No coherent OS structure

2) Preferences & safety guardrails — 10%
- 10: prefs.md enforced; dry-run defaults; approval gates; locks; scheduling defaults sane
- 5: Stated but not enforced/validated
- 0: No safety model

3) Data model & schemas — 8%
- 10: JSONL canonical; schemas defined; validation used in workflows
- 5: Schemas exist but not enforced
- 0: No schemas

4) File organization & naming — 7%
- 10: Clear hierarchy, consistent names, project overrides documented
- 5: Mixed patterns
- 0: Disorganized

5) Knowledge base setup — 7%
- 10: facts.jsonl, glossary, sources, timeline; citable; updated
- 5: Exists but incomplete or stale
- 0: Absent

6) Lists & workflows — 8%
- 10: Lists registry, JSONL + MD views, docgen reliable, find/add/set used
- 5: Lists exist without automation
- 0: None

7) Automation & scheduling hygiene — 8%
- 10: Tasks use wrappers (retries, locks, TZ, missed-run policy); safe by default
- 5: Some manual scheduling without guardrails
- 0: None or unsafe

8) Services & hosting — 8%
- 10: Needed services registered, logged, monitored; clean start/stop; ports minimal
- 5: Services run but lack observability
- 0: Ad hoc/manual

9) Security & access — 12%
- 10: Strong auth, key-only access, least privilege, secrets managed
- 5: Mixed posture, secrets scattered
- 0: Lax

10) Backup & recovery (time travel) — 10%
- 10: Periodic snapshots, verify restores, documented recovery
- 5: Snapshots exist, untested
- 0: None

11) Monitoring & telemetry — 6%
- 10: Runs recorded, digests generated, alerts for failures
- 5: Logs only
- 0: No visibility

12) Documentation & onboarding — 6%
- 10: README/runbooks, decision records, how-to workflows
- 5: Sparse notes
- 0: None

How to score
- Use file N5/zo_setup_rubric.sheet.json. Enter a 0–10 score per criterion; the sheet computes a weighted total (0–10).
- Keep brief notes/evidence in the Notes column. Where possible, link to files (e.g., file N5/index.md, file N5/prefs.md).

Next
- We’ll populate the sheet in a follow-up, compare to a target profile, and create a prioritized remediation plan.
