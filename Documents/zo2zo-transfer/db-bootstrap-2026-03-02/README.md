---
created: 2026-03-02
last_edited: 2026-03-02
version: 1.0
provenance: con_pLLTlqfVu4hKeKhT
---

# DB Bootstrap Kit (Empty Replicas)

This kit recreates empty DuckDB versions of the two large DB files intentionally excluded from bulk relay transfer.

## Target Files to Recreate
- `Skills/zode-moltbook/state/social_intelligence.db`
- `Datasets/career-hotline-calls/data.duckdb`

## Included Assets
- `social_intelligence.schema.sql` (raw schema export)
- `career_hotline_calls.schema.sql` (raw schema export)
- `social_intelligence.bootstrap.sql` (dependency-ordered, executable)
- `career_hotline_calls.bootstrap.sql` (dependency-ordered, executable)
- `social_intelligence.tables.txt` (table inventory)
- `career_hotline_calls.tables.txt` (table inventory)
- `bootstrap_empty_duckdbs.sh` (runnable setup script)
- `bootstrap_manifest.yaml` (machine-readable contract)

## Use
From workspace root:

```bash
bash Documents/zo2zo-transfer/db-bootstrap-2026-03-02/bootstrap_empty_duckdbs.sh
```

## Validation
The script runs:
- schema apply to fresh DB files
- table listing checks on both recreated DBs

## Notes
- This creates **empty** DBs (no row data).
- Use only bootstrap SQL files for creation (`*.bootstrap.sql`).
- Raw schema exports are included for reference/audit.
