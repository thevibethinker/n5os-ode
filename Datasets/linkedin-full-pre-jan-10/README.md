---
created: 2026-01-11
last_edited: 2026-01-11
version: 1.0
provenance: con_TMNfud0WH1oZVoDA
---

# LinkedIn Full Export (pre Jan 10)

This dataset turns a LinkedIn “Download larger data archive” export into a queryable DuckDB database (`data.duckdb`). It’s designed for personal analytics questions like:
- How many messages have I sent (and when)?
- How has my connection network grown over time?
- What have I been posting/commenting about?
- What do I search for most?

## How to Get Your Data (LinkedIn Export)
LinkedIn lets you request a data archive from Settings.

High-level flow (UI labels may change):
1. In LinkedIn, click **Me** (your profile icon).
2. Go to **Settings & Privacy**.
3. Find **Get a copy of your data**.
4. Choose the **larger data archive** option (the “big” export, not a single-category export).[^1]
5. Request the archive and wait for LinkedIn to email you a download link.[^1]
6. Download the ZIP.

Then:
- Put the ZIP in `source/` (example: `source/Complete_LinkedInDataExport_01-10-2026.zip`).
- Run:

```bash
python ingest/ingest.py
```

## What’s Included (Scope)
This dataset focuses on “life-analytics-relevant” LinkedIn data:

**Included tables:**
- Profile: `profile`, `positions`, `education`, `skills`
- Network: `connections`, `invitations`
- Messaging: `messages`
- Content & activity: `shares`, `comments`, `reactions`
- Behavioral signals: `search_queries`, `learning`
- Job hunt history: `job_applications`

**Not included (by default):** advertising / targeting files, login/security logs, and similar diagnostic data (these exist in the raw export, but are intentionally out of scope unless you explicitly want them).

## Coverage (from this export)
Based on min/max timestamps in the ingested tables:
- `connections.connected_on`: 2014-01-13 → 2026-01-08
- `messages.sent_at`: 2016-07-26 → 2026-01-09
- `shares.shared_at`: 2020-04-17 → 2025-12-18
- `comments.commented_at`: 2019-07-17 → 2026-01-08
- `reactions.reacted_at`: 2017-03-30 → 2026-01-09
- `search_queries.searched_at`: 2024-12-10 → 2026-01-09

## How to Query
You can query with DuckDB CLI:

```bash
duckdb data.duckdb
```

Or run one-off queries:

```bash
duckdb data.duckdb -c "SHOW TABLES"
```

Schema reference is auto-generated in `schema.yaml` (do not edit it manually).

## Example Queries

### 1) How many messages have I sent vs received?
```sql
SELECT
  CASE WHEN is_from_v THEN 'sent' ELSE 'received' END AS direction,
  COUNT(*) AS message_count
FROM messages
GROUP BY 1
ORDER BY message_count DESC;
```

### 2) Who do I message most? (rough)
Notes:
- For sent messages, this uses `recipient_names`.
- For received messages, this uses `sender_name`.
- Group threads will count as a single “recipient_names” blob.

```sql
WITH expanded AS (
  SELECT
    sent_at,
    CASE
      WHEN is_from_v THEN TRIM(r) ELSE sender_name
    END AS counterparty
  FROM messages
  LEFT JOIN UNNEST(
    CASE WHEN is_from_v THEN str_split(recipient_names, ',') ELSE [] END
  ) AS t(r) ON TRUE
)
SELECT counterparty, COUNT(*) AS messages
FROM expanded
WHERE counterparty IS NOT NULL AND counterparty <> ''
GROUP BY 1
ORDER BY messages DESC
LIMIT 25;
```

### 3) How has my network grown over time?
```sql
SELECT
  date_trunc('month', connected_on) AS month,
  COUNT(*) AS new_connections
FROM connections
WHERE connected_on IS NOT NULL
GROUP BY 1
ORDER BY 1;
```

### 4) Posting cadence: how many shares per month?
```sql
SELECT
  date_trunc('month', shared_at) AS month,
  COUNT(*) AS shares
FROM shares
WHERE shared_at IS NOT NULL
GROUP BY 1
ORDER BY 1;
```

### 5) What do I search for most?
```sql
SELECT search_query, COUNT(*) AS searches
FROM search_queries
WHERE search_query IS NOT NULL AND search_query <> ''
GROUP BY 1
ORDER BY searches DESC
LIMIT 50;
```

## Notes / Caveats
- Some timestamps in the export are explicitly UTC (e.g., message timestamps). Other activity timestamps may not include a timezone.
- LinkedIn exports can include "notes"/freeform text fields with embedded HTML; these are preserved as text.

[^1]: https://www.linkedin.com/help/linkedin/answer/a566336/export-connections-from-linkedin


