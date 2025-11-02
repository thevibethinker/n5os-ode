---
description: 'Command: index-update'
tags: []
---
# `index-update`

Version: 0.1.0

Summary: Update the N5 index incrementally, scanning only changed files.

Aliases: index-incr

Workflow: ops

Tags: index, incremental

## Outputs
- index : file (jsonl) â N5/index.jsonl

## Side Effects
- writes:file
- modifies:file

## Examples
- N5: run index-update

## Related Components

**Related Commands**: [`docgen`](../commands/docgen.md), [`index-rebuild`](../commands/index-rebuild.md), [`digest-runs`](../commands/digest-runs.md)

**Knowledge Areas**: [System Architecture](../knowledge/system-architecture.md)

**Examples**: See [Examples Library](../examples/) for usage patterns



## Inputs
(None)
