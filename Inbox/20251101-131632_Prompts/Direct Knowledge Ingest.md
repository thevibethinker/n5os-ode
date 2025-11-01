---
description: 'Processes large document content directly through LLM conversation to
  extract structured knowledge into reservoirs:'
tags: []
tool: true
---
# Direct Knowledge Ingest

## Summary
Command for direct ingestion of large documents into N5 knowledge reservoirs using conversational LLM processing. Bypasses deep_research limitations for scalable knowledge extraction and synchronization.

## Purpose
Processes large document content directly through LLM conversation to extract structured knowledge into reservoirs:
- Bio information
- Timeline events
- Glossary terms
- Sources and references
- Company information
- Facts (as SPO triples)
- Schema expansion suggestions

## Usage
### Command Line
```bash
python scripts/run_direct_ingestion.py --input_text "<large_document_content>" --source_name "<source_identifier>" [--dry-run]
```

### N5 Integration
```bash
N5: run direct-knowledge-ingest --input "<content>" --source "<identifier>"
```

## Parameters
- `--input_text` (required): The large document content to process
- `--source_name` (optional): Identifier for the source (default: "direct_ingestion")
- `--dry-run` (optional): Preview what would be processed without making changes

## Process Flow
1. **Direct LLM Processing**: Content analyzed using conversational LLM
2. **Structured Extraction**: Information extracted into knowledge reservoirs
3. **Sync Analysis**: LLM reasoning identifies contradictions, supersessions, and updates
4. **Manual Reconciliation**: User reviews sync report and approves changes
5. **Reservoir Updates**: Approved changes applied to knowledge base

## Outputs
### Knowledge Reservoirs (updated in `knowledge/` directory)
- `bio.md`: Biographical information and summaries
- `timeline.md`: Chronological events and milestones
- `glossary.md`: Key terms and definitions
- `sources.md`: References and citations
- `company.md`: Company information and details
- `facts.jsonl`: Facts as subject-predicate-object triples (append-only)

### Sync Reports
- Analysis of contradictions between old and new information
- Recommendations for updates and reconciliations
- Suggestions for schema expansions

## Dependencies
- `scripts/direct_ingestion_mechanism.py`: Core processing engine
- `scripts/sync_mechanism.py`: Synchronization with existing knowledge
- `scripts/run_direct_ingestion.py`: Command runner
- `test/test_direct_ingestion.py`: Test suite

## Examples
### Basic Usage
```bash
python scripts/run_direct_ingestion.py --input_text "John Doe founded TechCorp in 2020..." --source_name "careerspan_doc"
```

### Dry Run Preview
```bash
python scripts/run_direct_ingestion.py --input_text "Large document content..." --dry-run
```

### Large Content Processing
```bash
python scripts/run_direct_ingestion.py --input_text "$(cat large_document.txt)" --source_name "annual_report"
```

## Safety Notes
- Manual reconciliation required before finalizing updates
- Facts reservoir is append-only; other reservoirs use LLM reasoning for conflicts
- Large documents (>50k characters) handled efficiently
- All changes logged and reversible

## Related Commands
- `knowledge-sync`: Manual reconciliation of sync reports
- `reservoir-update`: Direct updates to knowledge reservoirs
- `deep-research`: Alternative for smaller content analysis

## Testing
Run test suite: `python test/test_direct_ingestion.py`