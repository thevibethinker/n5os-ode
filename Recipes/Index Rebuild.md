---
description: 'Command: index-rebuild'
tags: []
---
# `index-rebuild`

Version: 0.1.0

Summary: Rebuild the N5 system index from source files

Workflow: ops

Tags: index, rebuild, system

## Outputs
- index_path : path â Path to the rebuilt index.jsonl

## Side Effects
- writes:file
- modifies:file

## Examples
- N5: run index-rebuild

## Failure Modes
- Source file corruption
- Permission errors

## Related Components

**Related Commands**: [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`digest-runs`](../commands/digest-runs.md)

**Knowledge Areas**: [System Architecture](../knowledge/system-architecture.md)

**Examples**: See [Examples Library](../examples/) for usage patterns



## Inputs
(None)
