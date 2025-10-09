---
date: "2025-09-20T22:24:55Z"
last-tested: "2025-09-20T22:24:55Z"
generated_date: "2025-09-20T22:24:55Z"
checksum: a9d31bc4958dfe622e584def84e9fb89
tags: []
category: unknown
priority: medium
related_files: []
anchors: 
input: null
output: /home/workspace/N5_mirror/scripts/README_email_workflow.md
---
# Email Ingestion Workflow - Consolidated Implementation

## Overview
This consolidated workflow processes transcripts into structured content maps and generates follow-up emails, warm introduction tickets, and content blurbs using N5OS standards and MasterVoiceSchema compliance.

## Components Created

### 1. `summarize_segments.py`
- **Purpose**: Chunks raw transcripts into semantic segments and summarizes using LLM
- **Input**: Raw transcript text file
- **Output**: JSON file with original chunks and AI-generated summaries
- **Voice**: Applies MasterVoiceSchema tone for reflective, balanced summaries

### 2. `deliverable_orchestrator.py` 
- **Purpose**: Generates blurbs, follow-up emails, and warm introduction tickets from content maps
- **Features**:
  - LLM-based warm intro opportunity detection (no regex)
  - Dual-sided warm intro email generation 
  - Follow-up emails per Function [02] specifications
  - Ticket creation with priority scoring
- **Voice**: Connector-style for warm intros, balanced formality for follow-ups

### 3. `consolidated_workflow.py`
- **Purpose**: Orchestrates the complete pipeline from transcript to final outputs
- **Pipeline**: 
  1. Process transcript → segments
  2. Create comprehensive content map
  3. Generate all outputs (emails, tickets, blurbs)  
  4. Validate per N5OS standards
- **Features**: Workspace organization, dry-run support, comprehensive logging

## Usage Examples

### Quick Start - Full Pipeline
```bash
cd /home/workspace/N5_mirror/scripts
python3 consolidated_workflow.py /path/to/transcript.txt --workspace ./output
```

### Individual Components
```bash
# Generate segments only
python3 summarize_segments.py transcript.txt segments.json --dry-run

# Generate tickets from existing content map  
python3 deliverable_orchestrator.py content_map.json --output-dir ./tickets
```

## N5OS Compliance Features

### Logging & Telemetry
- All activities logged to `/home/workspace/N5/knowledge/logs/Email/{date}.log`
- Structured logging with timestamps and severity levels
- Output file paths logged for audit trails

### Safety & Control
- `--dry-run` flag for preview without side effects
- Socratic expansion via ticket approval workflow
- Validation checks for voice fidelity and completeness

### Voice Fidelity (MasterVoiceSchema ≥ 1.2)
- Tone calibration per relationship depth and context
- CTA library with soft/balanced/direct options
- Formality adaptation (casual/balanced/formal)
- Length optimization (150-250 words for follow-ups)

## Output Structure
```
workspace/
├── content_maps/
│   ├── {transcript}_segments.json
│   └── {transcript}_content_map.json
├── emails/
│   └── follow_up_{timestamp}_{n}.md
└── tickets/
    └── blurb_tickets_{timestamp}.json
```

## Warm Introduction Workflow
1. **Detection**: LLM analyzes content map for mutual contacts, shared interests, complementary skills
2. **Prioritization**: High/medium/low based on strategic fit and explicit networking requests  
3. **Generation**: Dual emails (one per party) with connector-style tone
4. **Ticketing**: Structured tickets with approval gates before sending

## Next Steps for Production
1. **API Integration**: Replace placeholder OpenAI calls with proper authentication
2. **Enhanced Validation**: Add schema validation for content maps and outputs
3. **Batch Processing**: Support for multiple transcripts in single workflow run
4. **Integration Testing**: End-to-end validation with real transcript samples

## Dependencies
- Python 3.8+
- aiohttp (async HTTP client)
- OpenAI API access (or alternative LLM provider)
- Standard library: json, logging, pathlib, asyncio

The workflow is now complete and ready for testing with sample transcripts.