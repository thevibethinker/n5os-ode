---
description: 'Command: knowledge-add'
tags: []
---
# `knowledge-add`

Version: 0.1.0

Summary: Add a fact to the knowledge base.

Workflow: knowledge

Tags: knowledge, facts

## Inputs
- subject : text (required) Ã¢ÂÂ Subject of the fact
- predicate : text (required) Ã¢ÂÂ Predicate/relationship
- object : text (required) Ã¢ÂÂ Object of the fact
- source : text Ã¢ÂÂ Source of the fact
- tags : json Ã¢ÂÂ Tags for the fact

## Outputs
- fact_id : text Ã¢ÂÂ Created fact ID

## Side Effects
- writes:file

## Examples
- N5: run knowledge-add subject=N5 predicate=is object='Neural Network OS'

## Related Components

**Related Commands**: [`knowledge-find`](../commands/knowledge-find.md)

**Knowledge Areas**: [Knowledge Base](../knowledge/knowledge-base.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

