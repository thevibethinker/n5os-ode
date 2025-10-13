---
date: "2025-09-24T01:36:00Z"
last-tested: "2025-09-24T01:36:00Z"
generated_date: "2025-09-24T01:36:00Z"
checksum: jobs_add_v0_1_0
tags:
  - jobs
  - careers
  - list-management
category: data-ingestion
priority: medium
related_files: 
anchors:
  - object Object
---
# `jobs-add`

Version: 0.1.0

Summary: Add one-off job to private list

Workflow: data

Tags: jobs, careers, tracking

## Inputs
- job_string : string (required) — Title@Company [location] [salary]

## Outputs
- job_id : string — Unique identifier for the added job
- confirmation : text — Confirmation message with job details

## Side Effects
- writes:file (Careerspan/Jobs/ list files)

## Examples
- Add basic job: `python N5/scripts/jobs_add.py "Senior Engineer@TechCorp"`
- With location: `python N5/scripts/jobs_add.py "Product Manager@StartupCo [San Francisco]"`
- With salary: `python N5/scripts/jobs_add.py "Data Scientist@BigCorp [Remote] [$120k-150k]"`
- Full details: `python N5/scripts/jobs_add.py "Engineering Manager@Company [NYC] [$180k]"`

## Related Components

**Related Commands**: [`jobs-review`](../commands/jobs-review.md), [`jobs-scrape`](../commands/jobs-scrape.md), [`lists-add`](../commands/lists-add.md)

**Scripts**: `N5/scripts/jobs_add.py` (to be created)

**Lists**: `Careerspan/Jobs/opportunities.jsonl`

**Examples**: See [Examples Library](../examples/) for usage patterns
