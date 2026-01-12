---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_JpgmOCcNVGniGrq2
---

# Careerspan acquirer target research — local tracking (v1)

## Files
- CSV tracker: `file 'Scratch/careerspan_acquirer-targets_tracking_v1.csv'`

## Column conventions
- `category_simple`: one of ATS | HRIS | Recruiting marketplace | Career platform | Staffing tech | Verification tech | Other
- `hr_stack_stage`: 1–3 stages, separated by `;` (e.g., `Sourcing;Matching`)
- `evidence_links`: 2–4 URLs, separated by `;`
- `research_status`: suggested values: `candidate` | `validated` | `rejected` | `duplicate`
- `exa_enriched` / `aviato_enriched`: `no` | `partial` | `yes`
- `priority`: `high` | `med` | `low`

## Workflow (human-in-the-loop)
1) Add raw candidates as `research_status=candidate` with at least 1 credible link.
2) Upgrade to `validated` once we have: clear rationale + 2–4 strong evidence links.
3) Only after a decent batch is validated, we push the validated subset into Notion SSOT.

