# Implementation Correction: Stakeholder-Aware Meeting Processing

**Date:** 2025-10-10  
**Status:** Architecture Revision Required

---

## Problem Identified

The current implementation tries to have Python scripts call Zo LLM via subprocess, which creates circular dependency issues:
- Scripts can't directly invoke Zo (the AI assistant)
- Subprocess approach adds complexity without value
- Request/response file system is overly complicated

## Correct Architecture

**Zo (the AI assistant) should process meetings directly when invoked via command/scheduled task.**

### How It Should Work:

1. **Auto Processor** (Python script):
   - Monitors Google Drive for new transcripts
   - Downloads transcripts to Document Inbox
   - Classifies meetings (internal vs external)
   - Creates processing request metadata
   - **Does NOT call LLMs**

2. **Meeting Processor Command** (Zo processes directly):
   - Zo reads the transcript
   - Zo classifies stakeholder type
   - Zo loads appropriate templates
   - Zo extracts content for each block
   - Zo fills templates and saves blocks
   - Zo creates metadata

3. **Scheduled Task**:
   - Runs periodically
   - Invokes meeting processor command
   - Zo handles all LLM extraction

---

## What Needs To Change

### ❌ Remove:
- `zo_llm.py` wrapper (unnecessary complexity)
- Subprocess calls from MIO
- Request/response file system
- All simulation code (already done ✅)

### ✅ Keep:
- `stakeholder_classifier.py` (classification logic)
- Block templates (internal/external)
- Updated schema
- `meeting_auto_processor.py` structure

### 🔄 Update:
- Create simple `command 'N5/commands/meeting-process.md'`
- Command invokes Zo directly: "Process meeting transcript at X, classify stakeholders, generate blocks"
- Zo does all the LLM work natively in the conversation

---

## Simpler Flow

```
New Transcript Detected
    ↓
Auto Processor: Classify & Create Request
    ↓
Scheduled Task: "Zo, process this meeting"
    ↓
Zo: Read transcript, extract content, fill templates, save blocks
    ↓
Done
```

---

## Next Steps

1. Simplify MIO to be a data structure / template manager only
2. Create `meeting-process` command that Zo executes
3. Test with: `command 'N5/commands/meeting-process.md'` + sample transcript
4. Update scheduled task to use new command

---

**Key Insight:** Zo IS the LLM. Scripts should prepare data, Zo should process it.
