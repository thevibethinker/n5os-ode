---
description: 'Command: lists-find'
tags: []
tool: true
---
# `lists-find`

Version: 0.1.0

Summary: Search and filter items in a list.

Workflow: lists

Tags: lists, search

## Inputs
- list : string (required) â List slug
- status : enum
- priority : enum
- tags : json â Tags to match
- project : text
- title-contains : text â Substring in title

## Outputs
- items : json â Matching items

## Side Effects
(None)

## Examples
- N5: run lists-find list=ideas status=open
- N5: run lists-find list=ideas --count

## Related Components

**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-docgen`](../commands/docgen.md), [`lists-export`](../commands/lists-export.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

