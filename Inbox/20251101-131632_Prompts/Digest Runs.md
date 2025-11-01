---
description: 'Command: digest-runs'
tags: []
tool: true
---
# `digest-runs`

Version: 0.1.0

Summary: Generate digest reports from run records for analysis and monitoring.

Workflow: ops

Tags: observability, monitoring, digest

## Inputs
- command : string â Specific command to analyze
- format : enum [default: markdown] â Output format
- since : date â Start date (YYYY-MM-DD)
- until : date â End date (YYYY-MM-DD)
- limit : number â Maximum runs to analyze

## Outputs
- report : file (markdown) â Digest report file

## Side Effects
- writes:file

## Examples
- N5: run digest-runs
- N5: run digest-runs command=docgen --format=summary
- N5: run digest-runs --since=2025-09-01 --until=2025-09-17

## Related Components

**Related Commands**: [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`index-rebuild`](../commands/index-rebuild.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

