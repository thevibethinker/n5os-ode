---
description: 'Command: lists-set'
tags: []
tool: true
---
# `lists-set`

Version: 0.1.0

Summary: Update fields of an item in a list.

Workflow: lists

Tags: lists, update

## Inputs
- list : string (required) â List slug
- item_id : string (required) â Item ID
- title : text
- body : text
- tags : json
- priority : enum
- status : enum
- project : text
- due : text â ISO date
- notes : text

## Outputs
- path : path â Path to JSONL file

## Side Effects
- modifies:file

## Examples
- N5: run lists-set list=ideas item_id=123 title="New Title"

## Related Components

**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md), [`lists-export`](../commands/lists-export.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

