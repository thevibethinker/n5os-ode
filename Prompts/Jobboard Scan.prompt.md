---
created: 2025-12-13
last_edited: 2025-12-13
version: 1.0
title: Jobboard Scan
description: |
  Scans the Careerspan job board on Notion and creates short.io links for new jobs.
  Uses diff-based processing - only creates links for jobs not already tracked.
tags:
  - jobboard
  - shortio
  - notion
  - careerspan
tool: true
---

# Jobboard Link Scanner

This prompt scans the Careerspan job board Notion database and creates short.io links for any new jobs.

## How it works

1. **Fetch** the current job listings from Notion via API
2. **Compare** against previously tracked jobs in `N5/data/jobboard_links.jsonl`
3. **Create** short.io links only for NEW jobs (diff-based)
4. **Record** new links to tracking file

## Slug Format

- Full-time job: `jb-{company}-{role}[-{location}]`
- Internship: `it-{company}-{role}[-{location}]`
- Part-time job: `pt-{company}-{role}[-{location}]`
- Talent call: `tc-{company}-{role}[-{location}]`

## Usage

When the user invokes this prompt, execute these steps:

### Step 1: Refresh Notion cache

Fetch the current job listings from Notion via API (data source ID: `29c5c3d6-a5db-81a3-9aa6-000b1c83fa24`) and save the raw JSON list to:
- `N5/data/jobboard_cache.json`

### Step 2: Run the scanner
```bash
# Dry run first to preview
python3 N5/scripts/jobboard_scan.py --dry-run

# If looks good, run for real
python3 N5/scripts/jobboard_scan.py
```

### Step 3: Report results
Show the user which links were created with their short URLs.

## Files

- **Script**: `N5/scripts/jobboard_scan.py`
- **Tracking**: `N5/data/jobboard_links.jsonl`
- **Cache**: `N5/data/jobboard_cache.json`


