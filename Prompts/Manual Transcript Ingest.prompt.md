---
created: 2025-12-23
last_edited: 2026-01-14
version: 2.1
tool: true
title: Manual Transcript Ingest
description: |
  Paste any transcript to ingest it into the N5 meeting system. Automatically detects if speaker labels are missing and runs attribution pre-screen. Creates canonical folder structure in Personal/Meetings/Inbox/ ready for pipeline processing.
tags:
  - meetings
  - transcript
  - ingest
  - intake
---
# Manual Transcript Ingest

Ingest a transcript from any source (Fathom, Fireflies, Zoom, Loom, Granola, voice memos, etc.) into the N5 meeting system.

## Workflow

When V pastes a transcript:

### Step 1: Speaker Label Detection

First, run the detection script:
```bash
python3 /home/workspace/N5/scripts/detect_speaker_labels.py --segments --text "<transcript>"
```

**If `has_speaker_labels: true`** → Skip to Step 3 (Metadata Extraction)

**If `has_speaker_labels: false`** → Proceed to Step 2 (Speaker Attribution)

---

### Step 2: Speaker Attribution Pre-Screen

When no speaker labels are detected, help V identify who said what.

**2a. Analyze the segments returned by the detection script**

Use your semantic understanding to:
- Identify likely speaker count (usually 2, sometimes 3+)
- Cluster segments by speaking style, perspective, role
- Look for clues: "I" statements, questions vs answers, who's pitching vs receiving, technical vs non-technical language

**2b. Present attribution hypothesis to V**

Format your response like this:

```
📋 **Speaker Attribution Needed**

I detected this transcript has no speaker labels. Based on the content, I see **[N] speakers**:

**Speaker A** (tentative: [role guess, e.g., "the one pitching/asking questions"])
- Segment 1: "Welcome to today's sync. I wanted to talk about..."
- Segment 3: "Well, I think we could integrate our platforms..."
- Segment 5: "I'm thinking a simple webhook setup..."

**Speaker B** (tentative: [role guess, e.g., "the one receiving/responding"])
- Segment 2: "That sounds great. What did you have in mind?"
- Segment 4: "Thanks! We've been working hard on that..."

**Who are these people?**
- Speaker A = ?
- Speaker B = ?
```

**2c. Wait for V's response**

V will provide names like "Speaker A = me, Speaker B = Sarah from Acme"

**2d. Apply labels to transcript**

Once V confirms, mentally reconstruct the labeled transcript:
```
V: Welcome to today's sync. I wanted to talk about the partnership opportunity.
Sarah: That sounds great. What did you have in mind?
V: Well, I think we could integrate our platforms...
```

Use this labeled version for the ingest.

---

### Step 3: Metadata Extraction

From the (now-labeled) transcript, extract:

| Field | Source | Fallback |
|-------|--------|----------|
| **Title** | Meeting topic from content | Participant names joined |
| **Date** | Explicit mention, timestamps | Ask V |
| **Participants** | Speaker labels | Ask V |

**Only ask V if truly undetectable:**
- Date: No timestamps, no date mentions, no context clues
- Participants: Already provided during attribution step

---

### Step 4: Execute Ingest

```bash
python3 /home/workspace/N5/scripts/manual_ingest.py \
  --text "<labeled_transcript>" \
  --title "<extracted_title>" \
  --date "<YYYY-MM-DD>" \
  --participants "<comma,separated,names>"
```

If duplicate detected, inform V and offer `--force` option.

---

### Step 5: Confirm

Report:
```
✓ Ingested: Personal/Meetings/Inbox/YYYY-MM-DD_Title/
  - transcript.md
  - transcript.jsonl  
  - metadata.json

Ready for manifest generation pipeline.
```

---

## Output Structure

```
Personal/Meetings/Inbox/<date>_<name>/
├── transcript.md      # Human-readable with frontmatter
├── transcript.jsonl   # Structured utterances
└── metadata.json      # Pipeline manifest seed
```

The folder has **no suffix** initially — `Meeting Manifest Generation` adds `_[M]` when processing to manifest state.

---

## Speaker Attribution Heuristics

When analyzing unlabeled transcripts, look for:

| Signal | Interpretation |
|--------|----------------|
| Questions ending in "?" | Often interviewer/asker |
| "I think...", "We could..." | Active proposer |
| "That's interesting", "Makes sense" | Receiver/responder |
| Technical jargon | Engineer/builder |
| "Our product", "We've built" | Company representative |
| "What's your timeline?" | Sales/BD angle |
| "Let me check with..." | Junior or intermediary |

**V is almost always one of the speakers** — look for Careerspan context, career coaching framing, or the "host" energy.

