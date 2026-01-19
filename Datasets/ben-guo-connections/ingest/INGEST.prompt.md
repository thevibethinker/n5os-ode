---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_vGJtA4K5OLY7MYZR
---

# LinkedIn Connections Ingest

## Source Files

| File | Description |
|------|-------------|
| `source/*.csv` | LinkedIn Connections export (any CSV matching pattern) |

The script auto-discovers the first `.csv` file in `source/`. LinkedIn exports follow a consistent format with a 3-row preamble (privacy notes) followed by headers and data.

## Tables Created

### `connections`
One row per LinkedIn connection.

| Column | Type | Description |
|--------|------|-------------|
| `first_name` | VARCHAR | First name of the connection |
| `last_name` | VARCHAR | Last name (may include credentials) |
| `linkedin_url` | VARCHAR | Full LinkedIn profile URL |
| `email` | VARCHAR | Email (often NULL due to privacy settings) |
| `company` | VARCHAR | Current company/organization |
| `position` | VARCHAR | Current job title |
| `connected_on` | TIMESTAMP | Date connection was established |

## Transformations

1. **Header skip**: Skips 3-row LinkedIn preamble (privacy notice)
2. **Column rename**: Converts `First Name` → `first_name` (snake_case)
3. **Date parsing**: Converts `Connected On` from `DD Mon YYYY` format to TIMESTAMP
4. **Null filtering**: Excludes rows with NULL first_name (handles empty lines)
5. **Ordering**: Sorted by `connected_on DESC` (most recent first)

## Running

```bash
cd Datasets/ben-guo-connections
python ingest/ingest.py
```

Produces a fresh `data.duckdb` on each run.
