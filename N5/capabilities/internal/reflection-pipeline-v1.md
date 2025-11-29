---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Reflection Pipeline & Knowledge Bridge v1

```yaml
capability_id: reflection-pipeline-v1
name: "Reflection Pipeline & Knowledge Bridge"
category: internal
status: active
confidence: medium
last_verified: 2025-11-29
tags:
  - reflection
  - knowledge
  - content
  - pipeline
entry_points:
  - type: script
    id: "N5/scripts/reflection_ingest.py"
  - type: script
    id: "N5/scripts/reflection_orchestrator.py"
  - type: script
    id: "N5/scripts/reflection_pipeline.py"
  - type: script
    id: "N5/scripts/reflection_synthesizer_v2.py"
  - type: script
    id: "N5/workers/worker_knowledge_bridge.py"
owner: "V"
```

## What This Does

This system ingests V's reflections (voice or text) from email and Google Drive, classifies them, generates reflection blocks (B50–B99), and promotes selected content into the knowledge base.

It owns the **reflection intake, processing, and registry** under `N5/records/reflections/`, plus a bridge that promotes content and blocks into a SQLite‑backed knowledge base for long‑term reuse.

## How to Use It

### One-off ingestion (email or manual files)

1. **Stage files** into `file 'N5/records/reflections/incoming/'`  
   - Email with subject containing `reflection-ingest` or `[Reflect]` should be handled by Zo + `reflection_ingest.py` per prefs.
   - You can also copy `.mp3`, `.m4a`, `.wav`, `.txt`, or `.md` files directly into `incoming/`.

2. **Run unified ingest**:

```bash
# Ingest from both email + Drive (and process staged files)
python3 N5/scripts/reflection_ingest.py --source both

# Or only process manually staged files (no external pull)
python3 N5/scripts/reflection_ingest.py --source drive --dry-run
```

3. **Worker processing** is delegated to `reflection_worker.py`, which transcribes (or wraps text), generates basic summaries, and registers items.

### Full orchestrated pipeline

```bash
# End-to-end pipeline: ingest + classify + block generation + optional synthesis
python3 N5/scripts/reflection_orchestrator.py \
  --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
  --run-suggester \
  --run-synthesizer
```

The orchestrator coordinates:
- `reflection_ingest_v2.py` (Drive ingest)
- `reflection_classifier.py` (multi‑label classification)
- `reflection_block_generator.py` (B73 and other blocks)
- `reflection_block_suggester.py` (pattern detection)
- `reflection_synthesizer_v2.py` (B90/B91 synthesis)

### Promotion into knowledge base

Once reflections and blocks exist, the knowledge bridge can promote them into a consolidated knowledge DB:

```bash
python3 N5/workers/worker_knowledge_bridge.py
```

This reads content and block rows from a content‑library database and writes normalized entries plus bridge records into a `generation_history` table in the knowledge base.

## Associated Files & Assets

### Reflection storage & registry

- `file 'N5/records/reflections/incoming/'` – Staging area for raw audio/text reflections.
- `file 'N5/records/reflections/outputs/'` – Per‑reflection folders with blocks, prompts, transcripts, and metadata.
- `file 'N5/records/reflections/registry/registry.json'` – High‑level registry of processed reflections.
- `file 'N5/logs/reflection_pipeline_status_2025-11-04.md'` – Example execution report (11‑file Drive batch).
- `file 'N5/logs/reflection_errors.jsonl'` – Error log for ingest, classification, and block generation.

### Scripts (pipeline)

- `file 'N5/scripts/reflection_ingest.py'` – Unified ingest from email/Drive plus manual staging; orchestrates `reflection_worker.py`.
- `file 'N5/scripts/reflection_ingest_v2.py'` – Drive‑centric ingest used by the orchestrator.
- `file 'N5/scripts/reflection_worker.py'` – Per‑file worker: transcribe/wrap, create summary/detail/proposal outputs, update registry.
- `file 'N5/scripts/reflection_classifier.py'` – Multi‑label classifier that maps transcripts to reflection block types.
- `file 'N5/scripts/reflection_block_generator.py'` – Generates reflection blocks (e.g. B73 Strategic Thinking) from transcripts.
- `file 'N5/scripts/reflection_block_suggester.py'` – Suggests which reflections to synthesize based on recent activity.
- `file 'N5/scripts/reflection_synthesizer_v2.py'` – B90 (cross‑reflection synthesis) and B91 (meta‑reflection) generator.
- `file 'N5/scripts/reflection_orchestrator.py'` – High‑level orchestrator that sequences ingest → classify → generate → synthesize and updates registry.

### Knowledge bridge

- `file 'N5/workers/worker_knowledge_bridge.py'` – Promotes content and block rows into a knowledge‑base `generation_history` table with a `content_library_bridge` mapping.
- Content DB: `file 'Personal/Content-Library/content-library.db'` (source).
- Knowledge DB: `file 'Inbox/20251105-095007_Intelligence/blocks.db'` (target, as configured in worker).

### Configuration & style guides

- `file 'N5/config/reflection-sources.json'` – Drive folder ID and email ingestion parameters.
- `file 'N5/commands/reflection-ingest.md'` – Command reference for reflection ingestion workflow.
- `file 'N5/prefs/reflection_block_registry.json'` – Block registry for B50–B99 reflection blocks.
- `file 'N5/prefs/communication/style-guides/reflections/'` – Style guides for each reflection block type (B50 personal reflection, B73 strategic thinking, B90 insight compound, B91 meta‑reflection, etc.).

## Workflow

### End-to-end reflection pipeline

```mermaid
flowchart TD
  A[Sources
  - Email with [Reflect]
  - Drive folder
  - Manual files] --> B[reflection_ingest.py
  - stage to N5/records/reflections/incoming/]

  B --> C[reflection_worker.py
  - ensure transcript
  - basic summary/detail/proposal
  - update registry]

  C --> D[reflection_classifier.py
  - multi-label tags
  - map to B50–B99]

  D --> E[reflection_block_generator.py
  - generate blocks
  - save under outputs/{slug}/blocks/]

  E --> F[Optional: reflection_block_suggester.py
  - pattern detection]

  F --> G[Optional: reflection_synthesizer_v2.py
  - B90/B91 cross-reflection + meta]

  G --> H[worker_knowledge_bridge.py
  - promote into knowledge base
  - content_library_bridge table]
```

### Execution characteristics

- The orchestrator can be run manually or as a scheduled Zo task for ongoing Drive‑based reflection capture.
- Voice reflections require Zo’s `transcribe_audio` tool to be called at least once; text reflections are wrapped automatically into `.transcript.jsonl` files.
- Classification and generation steps are parameterized to support dry‑run execution for debugging.

## Notes / Gotchas

- **External tool dependency:** Drive and Gmail ingestion are intentionally stubbed for Zo’s `use_app_google_drive` / `use_app_gmail` tools. The scripts should not attempt to call those APIs directly themselves.
- **Classification failures:** Missing `*.classification.json` files will cause some reflections to skip block generation; see `reflection_errors.jsonl` and the pipeline status reports for details.
- **Path conventions matter:** The whole stack assumes `N5/records/reflections/incoming/` and `outputs/` layouts from the bootstrap export. Moving or renaming these directories without adjusting scripts will break the pipeline.
- **Knowledge bridge paths are currently hard‑coded.** If the content library or knowledge‑base DB paths change, `worker_knowledge_bridge.py` must be updated accordingly.

