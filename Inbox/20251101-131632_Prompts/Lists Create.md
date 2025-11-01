---
description: 'Command: lists-create'
tags: []
tool: true
---
# `lists-create`

Version: 0.1.0

Summary: Create a new list registry entry with JSONL and MD files.

Workflow: lists

Tags: lists, registry

## Inputs
- slug : string (required) — List slug (lowercase, hyphens allowed)
- title : text (required) — List title
- tags : json — Tags

## Outputs
- registry : path — Path to index.jsonl
- jsonl : path — Path to JSONL file
- md : path — Path to MD file

## Side Effects
- writes:file
- modifies:file

## Examples
- N5: run lists-create slug=ideas title="My Ideas" --dry-run

## Related Components

**Related Commands**: [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md), [`lists-export`](../commands/lists-export.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns
