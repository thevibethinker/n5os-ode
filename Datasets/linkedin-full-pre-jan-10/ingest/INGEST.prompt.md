---
created: 2026-01-11
last_edited: 2026-01-11
version: 1.0
provenance: con_TMNfud0WH1oZVoDA
---

# LinkedIn Full Export (pre Jan 10) — Ingestion

## Goal
Transform a LinkedIn “Download larger data archive” ZIP export into a clean, queryable DuckDB database at `../data.duckdb`, with full `COMMENT ON TABLE` / `COMMENT ON COLUMN` metadata (used to generate `../schema.yaml`).

## Source Files
### Expected input
- `source/Complete_LinkedInDataExport_*.zip` — LinkedIn “larger data archive” export zip (recommended).[^1]

### Extraction behavior
- The ingest script will extract any `source/*.zip` into `source/extracted/` **only if** `source/extracted/` is currently empty.
- If `source/extracted/` already contains files, ingestion runs against the existing extracted files (to avoid churn).

## Tables Created (focused scope)
Row counts below are from the current run of this dataset.

| Table | What it is | Row count |
|---|---|---:|
| `profile` | Your profile info (single row) | 1 |
| `positions` | Work experience entries | 14 |
| `education` | Education entries | 3 |
| `skills` | Skills list | 50 |
| `connections` | 1st-degree connections | 3,357 |
| `messages` | LinkedIn messages (one row per message) | 15,101 |
| `shares` | Your shares/posts | 130 |
| `comments` | Your comments | 689 |
| `reactions` | Your reactions (likes, empathy, etc.) | 2,125 |
| `search_queries` | Searches you performed | 10,967 |
| `invitations` | Sent/received connection invites | 993 |
| `job_applications` | Job applications submitted via LinkedIn | 44 |
| `learning` | LinkedIn Learning activity (one row per content item) | 343 |

## Key Transformations / Normalization
- **Column naming:** All columns are normalized to `snake_case`.
- **Timestamp parsing:**
  - `messages.sent_at` is parsed from exported UTC strings.
  - `shares.shared_at`, `comments.commented_at`, `reactions.reacted_at` are parsed from `YYYY-MM-DD HH:MM:SS` strings.
  - `search_queries.searched_at` is read using `read_csv(... strict_mode=false, ignore_errors=true)` because DuckDB’s auto-dialect sniffing is brittle on this file.
  - `invitations.sent_at` and `job_applications.applied_at` are parsed from `M/D/YY, H:MM AM/PM` strings.
- **Learning export quirk:** `Learning.csv` has a trailing empty header column; DuckDB names it `column7`. We map that to `learning.notes`.
- **Boolean casting robustness:** Some columns may be auto-inferred as boolean. The ingest script casts to `VARCHAR` first where needed to avoid `NULLIF(..., '')` conversion errors.

## Running
From dataset root:

```bash
python ingest/ingest.py
```

Verification snippets:

```bash
duckdb data.duckdb -c "SHOW TABLES"
duckdb data.duckdb -c "SELECT COUNT(*) FROM messages"
duckdb data.duckdb -c "SELECT MIN(sent_at), MAX(sent_at) FROM messages"
```

## Extending / Changing Scope
- Add a new table by:
  1. Sampling the relevant file(s) in `source/extracted/`.
  2. Creating a new `CREATE TABLE ... AS SELECT ... FROM read_csv_auto(...)` block.
  3. Adding **one** `COMMENT ON TABLE` plus `COMMENT ON COLUMN` for **every** column.
  4. Re-running `python ingest/ingest.py`, then `python ../generate_schema.py`.

[^1]: https://www.linkedin.com/help/linkedin/answer/a566336/export-connections-from-linkedin

