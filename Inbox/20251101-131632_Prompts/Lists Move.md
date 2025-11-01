---
description: 'Command: lists-move'
tags: []
tool: true
---
# `lists-move`

Version: 0.1.0

Summary: Move an item from one list to another atomically

Workflow: lists

Tags: lists, move

## Inputs
- source_list : string (required) â Source list slug
- item_id : string (required) â Item ID to move
- dest_list : string (required) â Destination list slug

## Outputs
- item_id : text â Moved item id
- source_path : path â Source JSONL path
- dest_path : path â Destination JSONL path

## Side Effects
- modifies:file
- writes:file

## Examples
- N5: run lists-move ideas abc123 system-upgrades

## Failure Modes
- List not found
- Item not found
- Source equals dest
- Schema validation failure

## Related Components

**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

