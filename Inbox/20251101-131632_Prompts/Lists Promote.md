---
description: 'Command: lists-promote'
tags: []
tool: true
---
# `lists-promote`

Version: 0.1.0

Summary: Promote a list with explicit approval.

Workflow: lists

Tags: lists, promote

## Inputs
- list : string (required) â List slug

## Outputs
- registry : path â Updated registry
- md : path â Updated MD file

## Side Effects
- modifies:file
- writes:file

## Permissions Required
- email_approval

## Examples
- N5: run lists-promote ideas --approve

## Related Components

**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

