# Zo Data Ingest Process

This document describes the process an AI agent should follow when working with a Zo Data dataset.

**A dataset directory is identified by the presence of `datapackage.json`.** Datasets can live anywhere in the workspace.

**As you work through each phase, check off items in the Summary Checklist at the bottom of this file.** This keeps track of progress and ensures nothing is missed.

---

## Overview

You've been dropped into a Zo Data directory. Your job is to:
1. Explore and understand the raw data in `source/`.
2. Decide what to include (scope).
3. Write `ingest.py` to transform that data into `data.duckdb`.
4. Iterate until the database is correct and complete.
5. Document the pipeline in `INGEST.prompt.md`.
6. Document the dataset in `README.md` (high-level context, business rules, example queries).
7. Add comments to all tables and columns in DuckDB, then run `generate_schema.py` to create `schema.yaml`.
8. Update `datapackage.json` with a name and resource reference to `data.duckdb`.

**Order matters.** Do not write documentation until the ingestion is stable.

---

## Scope: Comprehensive but Relevant

Many data exports are enormous. Google Takeout can contain dozens of services. Amazon exports include obscure internal categories. Twitter archives have diagnostic logs alongside tweets.

**Do not try to capture everything.** Focus on what a typical user would actually want to analyze about their own life.

### The Goal
Build a high-signal, queryable database. The resulting `data.duckdb` should be:
- **Queryable in seconds** (not minutes)
- **Developed quickly** (hours, not days)
- **Meaningful** (focused on what someone would actually want to analyze)

### Examples of Good Scope

**Twitter/X:**
| Include | Skip |
|---------|------|
| Tweets (your posts) | Ad targeting data |
| Likes | Device information |
| Bookmarks | IP audit logs |
| Replies/mentions | Periscope data |
| Followers/following | Twitter Circle membership |

**Amazon:**
| Include | Skip |
|---------|------|
| Retail order history | Advertising preferences |
| Kindle library/reading | Alexa voice recordings |
| Audible library | Customer service transcripts |
| Digital orders | Internal account identifiers |

**Google Takeout:**
| Include | Skip |
|---------|------|
| YouTube watch/search history | Access log activity |
| Chrome history/bookmarks | Ads settings |
| Maps timeline | Google Pay transactions (unless requested) |
| Photos metadata | Tasks (often empty) |
| Gmail labels/counts (not content) | Stadia data |

**Spotify:**
| Include | Skip |
|---------|------|
| Streaming history | Inferences |
| Playlists | Technical logs |
| Saved tracks/albums | Payment data |
| Followers/following | Identity verification |

### When in Doubt
Ask: "Would someone actually want to analyze this?" If the answer is "probably not," skip it. You can always add tables later — it's harder to remove complexity.

### Follow User Intent
The examples above assume personal data analysis — the most common use case. But if the user explicitly asks to analyze something specific (even if it's in the "Skip" column above), follow their intent. For example, if someone wants to analyze their ad targeting data or device usage patterns, include that data.

---

## Phase 1: Explore the Source Data

### Locate the raw data
Check `source/` for files. Common patterns:
- Single zip/tar archive (Spotify, Twitter)
- Multiple archives or folders (Google Takeout)
- CSV/JSON files directly
- Database files (DuckDB, SQLite)
- Parquet files

### Source Type Handling

**Always produce a fresh `data.duckdb`** — never modify or rename source files.

| Source Type | Pre-processing | Ingestion Approach |
|-------------|----------------|-------------------|
| **Zip/tar** | Extract to `source/extracted/` | Process extracted contents |
| **DuckDB** | None needed | ATTACH source, CREATE tables in new DB |
| **SQLite** | None needed | Use `sqlite_scan()` to read tables |
| **Parquet** | None needed | Use `read_parquet()` |
| **JSON** | None needed | Use `read_json_auto()` |
| **CSV** | None needed | Use `read_csv_auto()` |

### Pre-process compressed archives
If the data is in an archive, extract to `source/extracted/`:
```bash
cd source

# Zip files
unzip spotify_data.zip -d extracted/

# Tar/gzip
mkdir -p extracted && tar -xzf archive.tar.gz -C extracted/

# Multiple zips (common for Google Takeout)
mkdir -p extracted
for f in *.zip; do unzip "$f" -d extracted/; done
```

### Sample, don't read entirely
**Never** read large files in full. Use sampling techniques:
```bash
# First 50 lines of a CSV
head -50 file.csv

# Structure of JSON
head -c 2000 file.json | jq '.' 

# List files in archive without extracting
unzip -l archive.zip | head -50
tar -tf archive.tar.gz | head -50

# Count lines
wc -l *.csv

# Inspect DuckDB file
duckdb source/data.duckdb -c "SHOW TABLES"
duckdb source/data.duckdb -c "SELECT * FROM <table> LIMIT 5"

# Inspect SQLite file
sqlite3 source/chat.db ".tables"
sqlite3 source/chat.db "SELECT * FROM messages LIMIT 5"

# Inspect Parquet file
duckdb -c "SELECT * FROM read_parquet('source/*.parquet') LIMIT 5"
```

### Limit output to stdout
**Keep terminal output minimal and readable.** Excessive output makes it impossible to review results and slows down the conversation.

- **Never** print entire tables, CSVs, or database contents
- **Always** use `LIMIT` (typically 3-10 rows) when querying data
- **Pipe through `head`** when output could be large: `some_command | head -50`
- **Summarize** rather than dump: prefer `COUNT(*)`, `MIN/MAX`, aggregates over raw data
- **Avoid verbose flags** unless debugging a specific issue
- **In Python scripts**, print progress sparingly (e.g., one line per table, not per row)

**Note:** The DuckDB CLI automatically truncates wide columns and limits row display, so queries run via `duckdb` don't require as much manual output limiting. The rules above apply more to raw file operations, `cat`, `jq`, and Python scripts.

### Document your understanding
As you explore, note:
- What tables/entities exist?
- What are the key fields?
- Are there date formats to normalize?
- Are there nested structures to flatten?

---

## Phase 2: Build `ingest.py` Iteratively

### The Contract
`ingest.py` must:
1. Be runnable as `python ingest.py` from the dataset directory — **no arguments**.
2. Delete and recreate `data.duckdb` on every run (idempotent).
3. Load all relevant data from `source/` into DuckDB tables.

### Source Discovery Convention

**The ingest script takes no arguments.** This is intentional — it enables a uniform workflow:

1. User exports their data from a service (Spotify, Google, etc.)
2. User drags the export into `source/`
3. User runs `python ingest.py`
4. The script figures out what to ingest

### Starter Template
```python
#!/usr/bin/env python3
"""
Ingest script for <dataset-name>.
Run from dataset root: python ingest/ingest.py
"""
import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data.duckdb"
SOURCE_DIR = Path(__file__).parent.parent / "source"

def main():
    # Delete existing DB for clean rebuild — always start fresh
    DB_PATH.unlink(missing_ok=True)
    
    con = duckdb.connect(str(DB_PATH))
    
    # Load data from SOURCE_DIR into tables
    # Choose pattern based on source type:
    #
    # JSON/CSV (extracted from zip):
    #   CREATE TABLE x AS SELECT * FROM read_json_auto('source/extracted/*.json')
    #
    # Parquet:
    #   CREATE TABLE x AS SELECT * FROM read_parquet('source/*.parquet')
    #
    # SQLite:
    #   INSTALL sqlite; LOAD sqlite;
    #   CREATE TABLE x AS SELECT * FROM sqlite_scan('source/data.db', 'table_name')
    #
    # DuckDB source:
    #   ATTACH 'source/original.duckdb' AS src (READ_ONLY);
    #   CREATE TABLE x AS SELECT * FROM src.table_name;
    #   DETACH src;
    
    con.close()
    print(f"Created {DB_PATH}")

if __name__ == "__main__":
    main()
```

### Iteration Loop

```
┌─────────────────────────────────────────────────────┐
│  1. Write/modify ingest.py                          │
│  2. Run: python ingest.py                           │
│  3. Verify: duckdb data.duckdb -c "SHOW TABLES"     │
│  4. Check row counts, sample rows, schema           │
│  5. If issues → go to step 1                        │
│  6. If complete → proceed to Phase 3                │
└─────────────────────────────────────────────────────┘
```

### Verification Checks
After each run, confirm:
```sql
-- List all tables
SHOW TABLES;

-- Row counts
SELECT COUNT(*) FROM <table>;

-- Sample data
SELECT * FROM <table> LIMIT 5;

-- Check for nulls in key columns
SELECT COUNT(*) FROM <table> WHERE <key_column> IS NULL;

-- Verify date parsing
SELECT MIN(timestamp), MAX(timestamp) FROM <table>;
```

### Common Patterns

**Loading JSON arrays:**
```python
con.execute("""
    CREATE TABLE history AS 
    SELECT * FROM read_json_auto('source/extracted/*.json')
""")
```

**Loading CSVs with headers:**
```python
con.execute("""
    CREATE TABLE orders AS 
    SELECT * FROM read_csv_auto('source/orders.csv', header=true)
""")
```

**Loading from Parquet:**
```python
con.execute("""
    CREATE TABLE events AS 
    SELECT * FROM read_parquet('source/*.parquet')
""")
```

**Loading from SQLite:**
```python
con.execute("INSTALL sqlite; LOAD sqlite")
con.execute("""
    CREATE TABLE messages AS 
    SELECT * FROM sqlite_scan('source/chat.db', 'message')
""")
```

**Loading from another DuckDB file:**
```python
con.execute("ATTACH 'source/original.duckdb' AS src (READ_ONLY)")
con.execute("CREATE TABLE users AS SELECT * FROM src.users")
con.execute("CREATE TABLE events AS SELECT * FROM src.events")
con.execute("DETACH src")
```

**Normalizing timestamps:**
```python
con.execute("""
    CREATE TABLE events AS 
    SELECT 
        *,
        strptime(ts_string, '%Y-%m-%d %H:%M') AS timestamp
    FROM read_json_auto('source/events.json')
""")
```

**Flattening nested JSON:**
```python
con.execute("""
    CREATE TABLE tracks AS 
    SELECT 
        item->>'trackName' AS track_name,
        item->>'artistName' AS artist_name,
        CAST(item->>'msPlayed' AS INTEGER) AS ms_played
    FROM read_json_auto('source/StreamingHistory*.json')
""")
```

---

## Phase 3: Write `INGEST.prompt.md`

Only after `ingest.py` is stable and verified.

This file documents **how the ingestion works** for future modifications:
- What source files are processed
- What tables are created
- Any transformations applied
- How to re-run or extend the pipeline

### Template

```markdown
# <Dataset Name> Ingestion

## Source Files
- `source/<filename>` - Description of contents

## Tables Created
| Table | Description | Row Count |
|-------|-------------|-----------|
| `streams` | Spotify listening history | ~50,000 |

## Transformations
- Timestamps converted from string to TIMESTAMP
- Duration converted from milliseconds to seconds

## Running
\`\`\`bash
python ingest/ingest.py
\`\`\`

## Extending
To add new export files, place them in `source/` and modify `ingest.py`.
```

---

## Phase 4: Write `README.md`

This is the **high-level, human-friendly documentation** for the dataset. It explains:
- **How to export the data** from the service (step-by-step instructions)
- What this dataset is and where it came from
- Time range and coverage
- Business rules and semantic meaning (what do certain values mean?)
- Example queries that answer real questions

**This is NOT a schema reference.** Don't list every column here — that goes in `schema.yaml`.

### Template

```markdown
# <Dataset Name>

This dataset contains your <service> data exported via GDPR/data export.

## How to Get Your Data

1. Go to [service.com/privacy](https://service.com/privacy)
2. Log in to your account
3. Click "Request data" or "Download your data"
4. Select the data categories you want
5. Wait for the export to be prepared (can take hours to days)
6. Download the archive and extract to `source/`

**Note**: Include any important tips like multiple zip files, specific options to select, etc.

## Coverage
- **Period**: January 2015 - December 2024
- **Source**: <Service> Data Export
- **Tables**: `streams`, `playlists`, `saved_tracks`

## What's Included

### Listening History
Your complete streaming history — every song you've played. Each record includes the track, artist, album, and how long you listened.

### Playlists
All playlists you've created or followed, including collaborative playlists.

## Business Rules & Semantics

- **`ms_played`**: Milliseconds the track was playing. A value under 30000 (30 seconds) typically means the track was skipped.
- **`offline`**: Boolean indicating if you were listening offline. Offline plays may have delayed timestamps.
- **`shuffle`**: Whether shuffle mode was active. Useful for analyzing intentional vs. random listening.
- **`reason_start`**: Why the track started playing:
  - `trackdone` = previous track ended naturally
  - `fwdbtn` = user clicked forward
  - `clickrow` = user explicitly selected this track

## Example Queries

### How many hours have I spent listening to music?
\`\`\`sql
SELECT SUM(ms_played) / 1000.0 / 60 / 60 AS total_hours 
FROM streams;
\`\`\`

### What are my top 10 artists?
\`\`\`sql
SELECT artist_name, COUNT(*) AS plays, SUM(ms_played) / 60000 AS minutes
FROM streams
GROUP BY artist_name
ORDER BY plays DESC
LIMIT 10;
\`\`\`

### What do I listen to on weekends vs weekdays?
\`\`\`sql
SELECT 
  CASE WHEN EXTRACT(DOW FROM played_at) IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
  artist_name,
  COUNT(*) AS plays
FROM streams
GROUP BY day_type, artist_name
ORDER BY day_type, plays DESC;
\`\`\`

## Notes
- Streaming history before 2018 may be incomplete due to Spotify's data retention policies.
- Podcast listening is in a separate table (`podcast_streams`) if available.
```

---

## Phase 5: Document Schema with DuckDB Comments

Instead of manually maintaining a schema file, we use DuckDB's built-in `COMMENT` feature to store descriptions directly in the database. The `generate_schema.py` script then extracts this metadata into `schema.yaml`.

### Step 1: Add Comments in `ingest.py`

After creating your tables, add comments to describe each table and column:

```python
# Add table comments
con.execute("""
    COMMENT ON TABLE streams IS 'Listening history — one row per track played'
""")

con.execute("""
    COMMENT ON TABLE playlists IS 'User playlists — one row per playlist'
""")

# Add column comments
con.execute("""
    COMMENT ON COLUMN streams.played_at IS 'When playback started'
""")
con.execute("""
    COMMENT ON COLUMN streams.track_name IS 'Song title'
""")
con.execute("""
    COMMENT ON COLUMN streams.artist_name IS 'Primary artist'
""")
con.execute("""
    COMMENT ON COLUMN streams.ms_played IS 'Milliseconds played (<30000 = skipped)'
""")
con.execute("""
    COMMENT ON COLUMN streams.shuffle IS 'Shuffle mode was active'
""")
con.execute("""
    COMMENT ON COLUMN streams.reason_start IS 'Why track started: trackdone, fwdbtn, clickrow'
""")
```

### Step 2: Generate `schema.yaml`

After ingestion is complete:

```bash
python generate_schema.py
```

This reads all table/column metadata from `data.duckdb` and writes `schema.yaml`:

```yaml
tables:
  - name: streams
    description: Listening history — one row per track played
    row_count: 85000
    columns:
      - name: played_at
        type: TIMESTAMP
        description: When playback started
      - name: track_name
        type: VARCHAR
        description: Song title
      # ...
```

### Guidelines

1. **Comment every table** — one-line description of what it contains.
2. **Comment every column** — brief description, especially for non-obvious fields.
3. **Include semantic meaning** — e.g., "Milliseconds played (<30000 = skipped)" is better than just "Milliseconds played".
4. **Run `generate_schema.py` after each ingest** — the schema.yaml stays in sync automatically.
5. **Don't edit `schema.yaml` manually** — it gets overwritten on regeneration.

---

## Phase 6: Update `datapackage.json`

Every Zo Data directory includes a `datapackage.json` following the [Frictionless Data](https://frictionlessdata.io/) standard. This makes the dataset discoverable and interoperable with standard tooling.

After ingestion is complete, update the template:

```json
{
  "name": "spotify-listening-history",
  "title": "Spotify Listening History",
  "resources": [
    { "path": "data.duckdb" }
  ]
}
```

### Guidelines

1. **`name`**: Lowercase, hyphen-separated, descriptive (e.g., `spotify-listening-history`, `amazon-orders`, `twitter-archive`).
2. **`title`**: Human-readable name (e.g., `Spotify Listening History`, `Amazon Order History`).
3. **`resources`**: Reference the DuckDB file. Keep it simple — one resource pointing to `data.duckdb`.

---

## Summary Checklist

Check off items as you complete each phase.

### Setup
- [x] Source data present in `source/`
- [x] Identified source type (zip, DuckDB, SQLite, Parquet, JSON, CSV)

### Phase 1: Exploration
- [x] Archives extracted to `source/extracted/` (if applicable) — N/A, txt file directly in source/
- [x] Sampled files to understand structure
- [x] Identified key entities/tables to create
- [x] Decided what to include vs. skip (scope)

### Phase 2: Ingestion
- [x] `ingest/ingest.py` written
- [x] Script runs without errors
- [x] Fresh `data.duckdb` created at dataset root (not copied/renamed from source)
- [x] All planned tables exist (`SHOW TABLES`)
- [x] Row counts are reasonable (not 0, not wildly off)
- [x] Sample queries return sensible data
- [x] Timestamps parsed correctly (check MIN/MAX) — N/A, no timestamps in genome data
- [x] No obvious data quality issues (nulls in key columns, etc.)

### Phase 3: Pipeline Documentation
- [x] `ingest/INGEST.prompt.md` documents source files
- [x] `ingest/INGEST.prompt.md` documents tables created
- [x] `ingest/INGEST.prompt.md` documents any transformations

### Phase 4: README
- [x] `README.md` includes "How to Get Your Data" export instructions
- [x] `README.md` explains what this dataset is
- [x] `README.md` describes coverage (time period, source)
- [x] `README.md` explains business rules and semantics
- [x] `README.md` includes 3-5 example queries with explanations

### Phase 5: Schema
- [x] All tables have COMMENT ON TABLE descriptions in `ingest.py`
- [x] All columns have COMMENT ON COLUMN descriptions in `ingest.py`
- [x] `python generate_schema.py` runs successfully
- [x] `schema.yaml` contains all tables with descriptions and row counts

### Phase 6: Data Package
- [x] `datapackage.json` has a descriptive `name` (lowercase, hyphens)
- [x] `datapackage.json` has a human-readable `title`
- [x] `datapackage.json` references `data.duckdb` in `resources`

### Final Verification
- [x] Can answer "How much X did I do?" type questions
- [x] Can answer "What are my top Y?" type questions
- [x] Can answer time-based questions (trends, by month, etc.) — N/A, genome data is a snapshot, not temporal


