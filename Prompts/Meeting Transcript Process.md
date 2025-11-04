---
description: Process a meeting transcript using **semantic analysis by Zo** (not regex
tool: true
  parsing).
tags: []
---
# Command: meeting-transcript-process

**Category**: meeting  
**Workflow**: automation  
**Script**: `/home/workspace/N5/scripts/process_meeting_transcript.py`

---

## Purpose

Process a meeting transcript using **semantic analysis by Zo** (not regex parsing).

Generates comprehensive meeting intelligence:
- Action items with owners, deadlines, priorities
- Decisions made with rationale and impact
- Key insights, quotes, pain points, and learnings

**This replaces the old regex-based extraction system.**

---

## Usage

```bash
python /home/workspace/N5/scripts/process_meeting_transcript.py <transcript_path> [meeting_type] [stakeholder_slug]
```

### Parameters

1. **transcript_path** (required): Path to transcript file (.txt or .docx)
2. **meeting_type** (optional): Type of meeting (sales, product, internal, etc.) - default: "general"
3. **stakeholder_slug** (optional): Stakeholder identifier for folder naming - default: "meeting"

### Examples

```bash
# Basic usage
python /home/workspace/N5/scripts/process_meeting_transcript.py transcript.txt

# With meeting type and stakeholder
python /home/workspace/N5/scripts/process_meeting_transcript.py transcript.txt sales allie-cialeo

# Process .docx file (auto-converts to .txt)
python /home/workspace/N5/scripts/process_meeting_transcript.py meeting_notes.docx product acme-corp
```

---

## What It Does

1. **Converts .docx to .txt** if needed (using pandoc)
2. **Creates output directory**: `Careerspan/Meetings/YYYY-MM-DD_HHMM_type_stakeholder/`
3. **Copies transcript** to output directory
4. **Creates processing request** file with full transcript
5. **Zo processes semantically** and generates intelligence files

---

## Output Structure

```
Careerspan/Meetings/2025-10-10_0000_sales_allie-cialeo/
├── transcript.txt
├── _PROCESSING_REQUEST.md  (for Zo)
└── INTELLIGENCE/
    ├── action-items.md
    ├── decisions.md
    └── detailed-notes.md
```

---

## Intelligence Files Generated

### 1. action-items.md
- Categorized by timeframe (Immediate, Short-term, Medium-term, Long-term)
- Real owner names from transcript
- Deadlines inferred from context
- Priority levels and context

### 2. decisions.md
- Decision statements with rationale
- Who decided and when
- Impact assessment
- Categories (Strategic, Tactical, Resource Allocation, Process)

### 3. detailed-notes.md
- Key insights with quotes
- Pain points identified
- Advice and recommendations
- Market insights
- Numbers, metrics, facts
- Aha moments and realizations

---

## How It Works

**NO REGEX. NO STUBS. NO SIMULATION.**

1. Script creates a processing request file with the full transcript
2. You (or Zo) open that file
3. Zo reads and understands the transcript semantically
4. Zo generates all intelligence outputs with real content
5. Done

This is **semantic processing**, not pattern matching.

---

## Migration Note

This replaces:
- ❌ `llm_client.py` (stub generator)
- ❌ `action_items_extractor.py` (regex-based)
- ❌ `decisions_extractor.py` (regex-based)
- ❌ `key_insights_extractor.py` (regex-based)
- ❌ `meeting_orchestrator.py` (old complex system)

All deprecated files moved to: `N5/scripts/_DEPRECATED_2025-10-10/`

---

## Related Commands

- `command 'meeting-approve'` - Approve outputs and trigger downstream actions
- `command 'deliverable-generate'` - Generate follow-up emails, blurbs, proposals
- `command 'meeting-prep-digest'` - Daily meeting prep intelligence

---

**Last Updated**: 2025-10-10  
**Status**: ✅ Active (replaces old regex system)
