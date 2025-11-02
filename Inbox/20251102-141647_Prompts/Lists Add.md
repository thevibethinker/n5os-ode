---
description: 'Command: lists-add'
tags: []
---
# `lists-add`

Version: 0.2.0

Summary: Add an item to a list with intelligent assignment

Workflow: lists

Tags: lists, ideas, auto-assign

## Inputs
- list : string â List slug (optional; auto-assigned if not provided)
- title : text (required) â Item title
- body : text â Item body
- tags : json â Tags (optional)
- priority : enum â Priority level
- status : enum [default: open] â Item status
- project : string â Associated project
- due : date â Due date (ISO format)
- notes : text â Additional notes

## Outputs
- item_id : text â Created item id
- path : path â Absolute path to JSONL file

## Uses
- **Modules**: [`listclassifier`](../modules/listclassifier.md)

## Side Effects
- writes:file
- modifies:file

## Examples
- N5: run lists-add title='Fix system workflow'
- N5: run lists-add list=ideas title='New idea'

## Failure Modes
- List not found in registry
- Schema validation failure
- Corrupt JSONL file

## Related Components

**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md), [`lists-export`](../commands/lists-export.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

