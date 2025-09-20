# Ingest-Transform-Email Workflow Example

This example demonstrates a complete workflow for ingesting audio content, transforming it through transcription, and sending the results via email.

## Overview

This workflow combines multiple N5 OS components:
- Audio ingestion and transcription (via `flow-run` with `ingest-transcription-transformation` module)
- Knowledge base integration (via `knowledge-add`)
- Email notification (via external integration)

## Workflow Steps

### 1. Run the Ingest-Transcription-Transformation Flow

```bash
N5: run flow-run flow=ingest-transcription-transformation inputs='{"audio_url": "https://example.com/podcast.mp3"}'
```

This step:
- Downloads the audio file
- Transcribes it to text
- Applies transformation rules
- Outputs structured data

### 2. Add Key Insights to Knowledge Base

```bash
N5: run knowledge-add subject="Podcast: AI Trends 2025" predicate="contains" object="Key insights from recent podcast on AI developments" source="transcription" tags='["ai", "trends", "podcast"]'
```

This step stores the processed information in the knowledge base for future reference.

### 3. Create Action Items List

```bash
N5: run lists-create slug=ai-podcast-actions title="AI Podcast Action Items"
```

Then add specific action items:

```bash
N5: run lists-add list=ai-podcast-actions title="Research quantum computing applications" body="Follow up on quantum AI research mentioned in podcast" tags='["research", "quantum"]' priority="H"
```

### 4. Generate Summary Report

```bash
N5: run digest-runs command=flow-run --format=markdown --since=2025-09-01
```

This generates a report of all flow runs for analysis.

## Related Components

- **Commands Used**: See [`flow-run`](../commands/flow-run.md), [`knowledge-add`](../commands/knowledge-add.md), [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`digest-runs`](../commands/digest-runs.md)
- **Modules Used**: See [`ingest-transcription-transformation`](../modules/ingest-transcription-transformation.md)
- **Knowledge Areas**: See [AI Trends](../knowledge/ai-trends.md), [Workflow Automation](../knowledge/workflow-automation.md)
- **Lists**: See [Action Items](../lists/action-items.md), [Research Topics](../lists/research-topics.md)

## Expected Outputs

- Transcribed and transformed content
- New knowledge facts in the base
- Action items list with prioritized tasks
- Execution summary report

## Error Handling

If the audio URL is invalid:
- The flow will fail gracefully with error logging
- Check the run records for detailed error information

If transcription fails:
- Partial results may still be available
- The system will attempt alternative processing methods