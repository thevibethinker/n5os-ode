# Meeting Processing System — Conversation Export

This document summarizes the key information about the Careerspan meeting transcript ingestion and processing system, as discussed.

---

## 1. System Overview

The system ingests meeting transcripts from multiple sources (local files, Google Drive, emails), enriches context using meeting and email histories, and produces actionable intelligence in modular blocks. It supports contextual outputs, dashboards, and list integrations.

---

## 2. Commands and Usage

### `meeting-process`
- Processes a single meeting transcript
- Arguments include transcript source, meeting type(s), stakeholder type(s), mode (full/essential/quick), output format

### `transcript-ingest`
- Batch ingest transcripts from Google Drive folder

### `meeting-approve`
- Marks reviewed meetings as approved and triggers downstream workflows

---

## 3. Architecture

Central orchestrator manages transcript fetching, metadata extraction, historical context lookup, block generation, list integration, and metadata saving.

### Modular Block Generators
- Universal blocks: follow-up email, action items, decisions, key insights, stakeholder profile
- Conditional blocks: warm intros, risks, opportunities, user research, competitive intel
- Category-specific blocks based on meeting types

### Outputs
- Dashboard summary file
- Ready-to-use email drafts
- Intelligence reports
- Structured metadata JSON

### Integration with N5 Lists
- Auto-populates action item, must contact, and warm intro lists

---

## 4. Implementation

### Meeting Orchestrator Script
- `meeting_orchestrator.py` as core
- Version 2.0 with full block-based pipeline

### Schemas
- `meeting-metadata.schema.json` defines metadata structure

### Workflows
- Supports single transcript processing and batch ingestion

---

## 5. Diagram

![Meeting Processing System](./meeting_system_architecture.png)

---

## 6. References

- `file 'N5/commands/meeting-process.md'`
- `file 'N5/scripts/meeting_orchestrator.py'`
- `file 'N5/schemas/meeting-metadata.schema.json'`
- `file 'Careerspan/Meetings/External/2025-09-19_logan-currie_shujaat-ahmad_vrijen-attawar/'`

---

*Export generated on 2025-10-09*  
*By Careerspan AI Assistant*  
