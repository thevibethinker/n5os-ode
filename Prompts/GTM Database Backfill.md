---
description: Process unprocessed B31 files into GTM intelligence database
tags: [gtm, intelligence, backfill, database]
tool: true
---

# GTM Database Backfill

Extract insights from 47 unprocessed B31 files into SQLite database.

## Instructions

Process unprocessed meetings from  with B31_STAKEHOLDER_RESEARCH.md files.

For EACH meeting:
1. Read B31 file
2. Extract all insights (title, category, signal strength, evidence, why_it_matters, quote, confidence)
3. Extract stakeholder info (name, role, type, company)
4. INSERT into database: 

Report progress every 10 meetings. Process ALL 47 meetings.
