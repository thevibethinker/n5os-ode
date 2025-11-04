---
description: 'Command: knowledge-find'
tool: true
tags: []
---
# `knowledge-find`

Version: 0.1.0

Summary: Search and filter facts in the knowledge base.

Workflow: knowledge

Tags: knowledge, facts, search

## Inputs
- subject : text â Subject to match
- predicate : text â Predicate to match
- object : text â Object to match
- tags : json â Tags to match
- source : text â Source to match

## Outputs
- facts : json â Matching facts

## Side Effects
(None)

## Examples
- N5: run knowledge-find subject=N5
- N5: run knowledge-find tags=["list","promoted"]

## Related Components

**Related Commands**: [`knowledge-add`](../commands/knowledge-add.md)

**Knowledge Areas**: [Knowledge Base](../knowledge/knowledge-base.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

