---
description: 'Command: lists-export'
tags: []
---
# `lists-export`

Version: 0.1.0

Summary: Export a list to MD or CSV format.

Workflow: lists

Tags: lists, export

## Inputs
- list : string (required) â List slug
- format : enum (required)
- output : path â Output file path

## Outputs
- file : path â Exported file path

## Side Effects
- writes:file

## Examples
- N5: run lists-export ideas md
- N5: run lists-export ideas csv --output=/tmp/ideas.csv

## Related Components

**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

