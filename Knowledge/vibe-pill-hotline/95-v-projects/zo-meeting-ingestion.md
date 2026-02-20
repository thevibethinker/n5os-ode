---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
provenance: con_lUAmO8hsfnmiy3xh
---

# Meeting Ingestion — Transcript to Intelligence

Skill that processes meeting transcripts from Google Drive into structured intelligence blocks. Replaces manual note-taking with automated extraction.

## What It Produces
From a raw transcript, it generates blocks:
- **B01**: Detailed recap
- **B02**: Commitments extracted
- **B03**: Decisions made
- **B04**: Open questions
- **B05**: Questions raised
- **B06**: Business context
Plus 20+ additional block types for deeper analysis.

## How It Works
1. Connects to Google Drive where transcripts live
2. Pulls new transcripts automatically
3. Runs LLM-powered extraction for each block type
4. Stores structured output alongside the original

## Install
```bash
cd Skills && git clone https://github.com/vrijenattawar/zo-meeting-ingestion.git meeting-ingestion
python3 meeting-ingestion/bootloader.py
```
Requires: Google Drive, Calendar, and Gmail integrations connected.

## Commands
```bash
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --dry-run
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process
```

## Why This Matters
Meetings generate more information than anyone captures manually. This skill extracts what matters — commitments, decisions, open loops — so nothing slips through.

Repo: github.com/vrijenattawar/zo-meeting-ingestion
