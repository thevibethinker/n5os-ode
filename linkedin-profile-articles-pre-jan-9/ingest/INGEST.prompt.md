# ZoData Ingestion Instructions

This document guides the AI agent and the user on how to ingest data for this dataset.

## Goal
Transform raw files in `../source/` into a structured DuckDB database at `../data.duckdb` and document it in `../schema.md`.

## Data Source
- Look in `../source/` for the raw files (zips, json, csv, etc).
- Description: [TODO: Describe what kind of data is expected here, e.g. "Spotify GDPR Export zip file"]

## Ingestion Logic (`ingest.py`)
- The script `ingest.py` contains the logic.
- **Current State:** Boilerplate / Incomplete.
- **Task:** Modify `ingest.py` to handle the specific file formats found in `source/`.

## Schema (`../schema.md`)
- After running `ingest.py`, the `schema.md` file should be updated to reflect the tables and columns in `data.duckdb`.
- This allows the AI to query the data effectively.

## Steps to Ingest
1. Place raw data in `../source/`.
2. Update `ingest.py` to parse the specific file formats.
3. Run `python ingest.py`.
4. Verify `../data.duckdb` works and `../schema.md` is accurate.

## Output Guidelines
- **Never print entire tables or files** — always use `LIMIT` (3-10 rows) when sampling data.
- **Keep ingest.py output minimal** — print one summary line per table (e.g., "Created streams: 50,000 rows"), not per-row output.
- **Pipe large output through `head`** when exploring files.
- Excessive stdout is unreadable and slows down the conversation.


