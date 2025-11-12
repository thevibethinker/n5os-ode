---
description: 'Command: lists-pin'
tool: true
tags: []
---
# `lists-pin`

Version: 0.1.0

Summary: Pin or unpin an item in a list.

Workflow: lists

Tags: lists, pin

## Inputs
- list : string (required) â List slug
- item_id : string (required) â Item ID

## Outputs
- path : path â Path to JSONL file

## Side Effects
- modifies:file

## Examples
- N5: run lists-pin list=ideas item_id=123
- N5: run lists-pin list=ideas item_id=123 --unpin

## Related Components

**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

