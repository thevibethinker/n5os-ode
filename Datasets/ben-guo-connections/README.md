---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_vGJtA4K5OLY7MYZR
---

# Ben Guo LinkedIn Connections

A queryable database of LinkedIn connections for Ben Guo, exported from LinkedIn.

## What's Here

**2,718 connections** spanning **December 2010 – January 2026** (~15 years of networking).

| Metric | Value |
|--------|-------|
| Total connections | 2,718 |
| With email visible | 36 (1.3%) |
| With company | 2,699 (99.3%) |
| Date range | Dec 2010 – Jan 2026 |

## How to Get Your LinkedIn Connections Data

1. Go to [LinkedIn Settings > Data Privacy](https://www.linkedin.com/mypreferences/d/download-my-data)
2. Click **Get a copy of your data**
3. Select **Connections** (or download the full archive)
4. Wait for LinkedIn to prepare the export (usually a few minutes)
5. Download and extract the ZIP file
6. Place the `Connections.csv` file in this dataset's `source/` folder
7. Run: `python ingest/ingest.py`

## Business Rules

- **Email visibility**: Most email addresses are NULL. LinkedIn only includes emails for connections who enabled the "Allow connections to download my email" setting.
- **Company/Position**: Reflects what's currently on the person's profile, not what it was when you connected.
- **Connected On date**: The date you became 1st-degree connections.

## Example Queries

### How many connections do I have per year?

```sql
SELECT 
    YEAR(connected_on) AS year, 
    COUNT(*) AS connections 
FROM connections 
GROUP BY 1 
ORDER BY 1;
```

### Who are my most recent connections?

```sql
SELECT first_name, last_name, company, position, connected_on
FROM connections
ORDER BY connected_on DESC
LIMIT 10;
```

### What companies have the most connections?

```sql
SELECT company, COUNT(*) AS people
FROM connections
WHERE company IS NOT NULL
GROUP BY company
ORDER BY people DESC
LIMIT 15;
```

### Which connections have visible emails?

```sql
SELECT first_name, last_name, email, company
FROM connections
WHERE email IS NOT NULL;
```

### Connection growth: how many new connections per month in 2024?

```sql
SELECT 
    DATE_TRUNC('month', connected_on) AS month,
    COUNT(*) AS new_connections
FROM connections
WHERE YEAR(connected_on) = 2024
GROUP BY 1
ORDER BY 1;
```

## Schema

See `schema.yaml` for the full schema with column descriptions, or query:

```sql
DESCRIBE connections;
```
