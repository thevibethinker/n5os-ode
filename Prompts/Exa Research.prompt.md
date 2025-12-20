---
created: 2025-12-04
last_edited: 2025-12-04
version: 1.0
title: Exa Research
description: |
  Run Exa-powered web research with neural search, deep search, live crawling,
  and direct Content Library ingestion. Powered by Exa's AI-first search API.
tags:
  - research
  - search
  - exa
  - content-library
  - intelligence
tool: true
---

# Exa Research

Run intelligent web research using Exa's AI-powered search API.

## Commands

### Neural Search (fast, semantic)
```bash
python3 N5/scripts/exa_research.py search "<query>" --num 10
```

### Deep Search (multi-step, comprehensive)
```bash
python3 N5/scripts/exa_research.py deep "<query>"
```

### Research API (autonomous agent)
```bash
python3 N5/scripts/exa_research.py research "<instructions>" --model exa-research
```

### Live Crawl (real-time content)
```bash
python3 N5/scripts/exa_research.py crawl "<url>" --subpages 5
```

### Find Similar
```bash
python3 N5/scripts/exa_research.py similar "<url>" --num 10
```

### Ingest to Content Library
```bash
python3 N5/scripts/exa_research.py ingest "<query>" --topics "topic1" "topic2" --max 5
```

## Categories for Specialized Search

Use `--category` with any of:
- `company` - Company homepages
- `research paper` - Academic papers
- `pdf` - PDF documents
- `github` - GitHub repositories
- `tweet` - Twitter/X posts
- `personal site` - Personal pages
- `linkedin profile` - LinkedIn profiles
- `financial report` - SEC filings, financial data

## Examples

**Find companies in career tech:**
```bash
python3 N5/scripts/exa_research.py search "AI-powered career coaching startup" --category company --num 5
```

**Deep research on a topic:**
```bash
python3 N5/scripts/exa_research.py deep "competitive landscape for AI career coaches"
```

**Ingest articles to Content Library:**
```bash
python3 N5/scripts/exa_research.py ingest "future of work AI automation" --topics "future-of-work" "ai" --max 5
```

## Output Formats

Add `--json` for JSON output, `--quiet` for minimal output.

