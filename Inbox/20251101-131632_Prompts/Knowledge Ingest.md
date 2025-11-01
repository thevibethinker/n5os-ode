---
description: 'Command: knowledge-ingest'
tags: []
tool: true
---
# `knowledge-ingest`

Version: 0.1.0

Summary: Ingest biographical/historical/strategic information about V and Careerspan, analyze with LLM, and store across knowledge reservoirs.

Workflow: knowledge

Tags: ingest, llm, analysis

## Inputs
- input_text : string (required) â The large text chunk to ingest

## Side Effects
- modifies:file
- writes:file

## Examples
- N5: run knowledge-ingest --input_text '...'

## Related Components

**Related Commands**: [`knowledge-add`](../commands/knowledge-add.md), [`knowledge-find`](../commands/knowledge-find.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

