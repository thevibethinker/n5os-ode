---
created: 2025-12-23
last_edited: 2025-12-23
version: 1.0
tool: true
title: Manual Transcript Ingest
description: >
  Ingest a transcript from any source (Fathom, Fireflies, Zoom, Loom, Granola, etc.)
  into the N5 meeting system. Creates canonical folder structure with metadata.
  Uses Socratic clarification when information is missing.
tags:
  - meetings
  - transcripts
  - intake
  - pseudo-webhook
command: manual-ingest
provenance: con_eCLbOiRyc7HgzEQp
---

# Manual Transcript Ingest

**Purpose:** Process a transcript from any source into the N5 meeting system, creating the canonical folder structure, metadata, and preparing it for the meeting intelligence pipeline.

## Invocation

```
@Manual Transcript Ingest <paste transcript or provide file path>
```

## Workflow

### Step 1: Receive Input

Accept transcript in any of these formats:
- **Direct paste:** User pastes transcript text directly
- **File reference:** User provides `file 'path/to/transcript.txt'`
- **Clipboard:** User says "from clipboard" or "I just copied it"

### Step 2: Analyze Transcript

Run semantic analysis to extract:
- **Date:** Look for explicit date mentions ("December 23", "today", "last Tuesday")
- **Participants:** Extract speaker names from "Speaker: text" patterns
- **Title:** Look for meeting title mentions or infer from context
- **Duration:** If timestamps present, calculate duration

### Step 3: Socratic Clarification (if needed)

If critical information is missing or ambiguous, ask:

**For missing date:**
> I couldn't detect the meeting date from the transcript. When was this recorded?
> - A specific date (e.g., "December 20")
> - "Today" or "Yesterday"  
> - "Last [day of week]"

**For ambiguous participants:**
> I detected these speakers: [list]. Are these the correct participant names?
> Should I add anyone else?

**For missing title:**
> What should I call this meeting? (Or I can name it after the first participant)

### Step 3: Analyze Semantically

Analyze the transcript semantically to extract:
1. **Meeting Title**: Generate a concise, human-readable title (e.g., "Partnership Sync - Ribbon & Careerspan")
2. **Meeting Date**: Identify the recording date (Priority: Transcript mention > External metadata > Today)
3. **Participants**: Extract speaker names (Vrijen Attawar, Christine Song, etc.)
4. **Structured Utterances**: Convert the raw text into a list of speaker-mapped segments.

### Step 4: Execute Ingestion

Call the `manual_ingest.py` script with the `--json-input` flag, providing the parsed data in the following format:

```bash
python3 /home/workspace/N5/scripts/manual_ingest.py \
  --json-input '{
    "text": "<full transcript text>",
    "title": "<title>",
    "date": "YYYY-MM-DD",
    "participants": ["Name 1", "Name 2"],
    "utterances": [
      {"speaker": "Name 1", "text": "...", "start_ms": 0},
      {"speaker": "Name 2", "text": "...", "start_ms": 1000}
    ]
  }'
```

### Step 5: Report Results

On success:
> ✓ **Transcript ingested successfully**
> 
> **Folder:** `Personal/Meetings/Inbox/2025-12-23_Meeting-Name/`
> **Date:** December 23, 2025
> **Participants:** John, Jane
> 
> The meeting is now in the Inbox awaiting manifest generation.
> Run `@Meeting Manifest Generation` to continue processing.

On duplicate detected:
> ⚠️ **Duplicate detected**
> 
> This transcript appears to match an existing meeting:
> `Personal/Meetings/Week-of-2025-12-16/2025-12-20_Same-Meeting/`
> 
> Do you want to:
> 1. Skip (keep existing)
> 2. Force re-ingest (create new folder)
> 3. View the existing meeting

## Date Resolution Priority

1. **Semantic detection:** Scan transcript for date mentions
2. **Calendar lookup:** Check Google Calendar for matching meetings
3. **Explicit override:** User provides date via clarifying question
4. **Today:** Default to current date

## Examples

### Example 1: Simple paste
```
User: @Manual Transcript Ingest
John: Hey everyone, thanks for joining.
Sarah: Happy to be here.
John: Let's discuss the Q1 roadmap...

Zo: I detected 2 participants (John, Sarah) but couldn't find a date.
    When was this meeting recorded?

User: Yesterday

Zo: ✓ Transcript ingested successfully
    Folder: Personal/Meetings/Inbox/2025-12-22_John/
```

### Example 2: With file
```
User: @Manual Transcript Ingest file 'Downloads/zoom_transcript.txt'

Zo: ✓ Transcript ingested successfully
    Folder: Personal/Meetings/Inbox/2025-12-23_Team-Sync/
    Date: December 23, 2025 (detected from transcript)
    Participants: V, Mike, Lisa
```

### Example 3: Full override
```
User: @Manual Transcript Ingest --title "Board Meeting" --date 2025-12-15
[transcript text]

Zo: ✓ Transcript ingested successfully
    Folder: Personal/Meetings/Inbox/2025-12-15_Board-Meeting/
```

## Technical Details

- **Engine:** `N5/services/intake/intake_engine.py`
- **CLI:** `N5/scripts/manual_ingest.py`
- **Dedup DB:** `N5/data/intake_dedup.db`
- **Output:** `Personal/Meetings/Inbox/<date>_<name>/`

## Files Created

Each ingested meeting creates:
```
Personal/Meetings/Inbox/<date>_<name>/
├── transcript.md      # Human-readable transcript
├── transcript.jsonl   # Structured transcript with utterances
└── metadata.json      # Meeting metadata for pipeline
```


