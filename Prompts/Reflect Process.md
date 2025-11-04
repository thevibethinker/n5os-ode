---
description: 'Process reflection queue end-to-end: ingest from Google Drive, classify,
tool: true
  and generate block content.'
tags: []
---
# reflect-process

**Command:** `reflect-process`  
**Alias:** `rp`  
**Category:** Reflection  
**Script:** `/home/workspace/N5/scripts/reflection_orchestrator.py`

---

## Purpose

Process reflection queue end-to-end: ingest from Google Drive, classify, and generate block content.

---

## Usage

```bash
# Standard execution
python3 /home/workspace/N5/scripts/reflection_orchestrator.py \
    --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV

# With optional features
python3 /home/workspace/N5/scripts/reflection_orchestrator.py \
    --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
    --run-suggester \
    --run-synthesizer

# Dry run (no changes)
python3 /home/workspace/N5/scripts/reflection_orchestrator.py \
    --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
    --dry-run
```

---

## Arguments

- `--folder-id` (required): Google Drive folder ID containing reflection audio files
- `--run-suggester` (optional): Run pattern detection after generation
- `--run-synthesizer` (optional): Run compound synthesis (B90/B91)
- `--dry-run` (optional): Simulate execution without making changes

---

## Workflow

The orchestrator coordinates Workers 1-5 in sequence:

1. **Worker 1: Ingest**
   - Poll Google Drive folder
   - Download new audio files
   - Transcribe using AssemblyAI
   - Save to `N5/records/reflections/incoming/`

2. **Worker 2: Classify**
   - Analyze transcripts
   - Multi-label classification
   - Block type mapping (B50-B99)
   - Confidence scoring

3. **Worker 4: Generate**
   - Create block content
   - Apply voice profiles
   - Auto-approve high-confidence blocks
   - Output to `N5/records/reflections/outputs/`

4. **Worker 5: Suggest** (optional, weekly)
   - Pattern detection across reflections
   - Suggest new block types
   - Output to `N5/records/reflections/suggestions/`

5. **Worker 5: Synthesize** (optional, weekly)
   - Cross-reflection synthesis
   - Generate B90/B91 compound blocks
   - Output to same outputs directory

6. **Registry Update**
   - Track all processed reflections
   - Update `N5/records/reflections/registry/reflections.jsonl`

---

## Output Structure

```
N5/records/reflections/
├── incoming/                    # Transcripts (Worker 1)
│   └── YYYY-MM-DD_topic.m4a.transcript.jsonl
├── outputs/                     # Generated blocks (Worker 4)
│   └── YYYY-MM-DD/
│       └── topic/
│           ├── B71_*.md
│           ├── B73_*.md
│           └── metadata.json
├── suggestions/                 # Pattern suggestions (Worker 5)
│   └── YYYY-MM-DD_suggestions.md
└── registry/                    # Audit trail
    └── reflections.jsonl
```

---

## Scheduled Execution

This command runs automatically via scheduled task:
- **Frequency:** 4x daily (1:07 AM, 7:07 AM, 1:07 PM, 7:07 PM ET)
- **Suggester:** Weekly only
- **Synthesizer:** Weekly only

To manually run with suggester/synthesizer:
```bash
python3 /home/workspace/N5/scripts/reflection_orchestrator.py \
    --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
    --run-suggester \
    --run-synthesizer
```

---

## Error Handling

**Per-Worker Failures:**
- Logged with context
- Pipeline continues
- Reflection marked for manual review

**Critical Failures:**
- Drive API unavailable → abort cycle
- Registry corruption → abort

**Recoverable Failures:**
- Single transcript fails → skip, continue
- Block generation fails → log, continue
- Synthesizer fails → log, continue (non-critical)

---

## Registry Schema

```json
{
  "id": "2025-10-24_pricing-strategy",
  "source_file": "2025-10-24_pricing-strategy.m4a",
  "transcript_path": "N5/records/reflections/incoming/2025-10-24_pricing-strategy.m4a.transcript.jsonl",
  "created_at": "2025-10-24T14:30:00Z",
  "phases": ["ingested", "classified", "generated"],
  "status": "processing"
}
```

---

## Dependencies

**Scripts:**
- `reflection_ingest_v2.py` (Worker 1)
- `reflection_classifier.py` (Worker 2)
- `reflection_block_generator.py` (Worker 4)
- `reflection_block_suggester.py` (Worker 5)
- `reflection_synthesizer_v2.py` (Worker 5)

**APIs:**
- Google Drive (for ingestion)
- AssemblyAI (for transcription)

**Directories:**
- `N5/records/reflections/{incoming,outputs,suggestions,registry}/`

---

## Related

- `file 'N5/prefs/communication/style-guides/reflections/'` - Style guides
- `file 'N5/prefs/reflection_block_registry.json'` - Block definitions
- `file 'N5/scripts/reflection_orchestrator.py'` - Implementation

---

**Version:** 1.0.0  
**Created:** 2025-10-26  
**Category:** Reflection Pipeline
