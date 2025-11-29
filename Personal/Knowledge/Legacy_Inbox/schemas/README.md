# Knowledge Schemas

This directory contains JSON Schema definitions for validating knowledge data structures.

## Schemas

- **`knowledge.facts.schema.json`**: Schema for SPO (Subject-Predicate-Object) triples in `../evolving/facts.jsonl`
  - Validates fact structure, confidence scores, and source attribution
  - Used by direct processing and knowledge ingestion systems

## Usage

These schemas enable:
- **Validation**: Ensure data integrity during knowledge ingestion
- **Portability**: Knowledge data remains interpretable without N5 OS
- **Documentation**: Self-describing data format

## Related

- Data: `../evolving/facts.jsonl`
- Processing: `/home/workspace/N5/scripts/n5_knowledge_*.py`
