---
description: 'Command: system-timeline-add'
tags: []
---
# `system-timeline-add`

Version: 0.1.0

Summary: Add new entry to N5 OS system development timeline

Workflow: ops

Tags: system-timeline, history, logging, n5-os

## Inputs
- title : text (required) — Brief title of the change/feature
- description : text (required) — Detailed description of what was added/changed
- category : enum (required) — Type of change
- version : string — Version number (optional)
- components : json — Components affected (array)
- impact : enum [default: medium] — Impact level
- status : enum [default: completed] — Status
- tags : json — Additional tags (array)

## Outputs
- entry_id : text — Created timeline entry ID
- path : path — Path to system-timeline.jsonl

## Side Effects
- writes:file

## Examples
- N5: run system-timeline-add title='Added command authoring' category=feature description='Implemented new command authoring system'
- N5: run system-timeline-add title='Fixed list validation' category=fix impact=low

## Failure Modes
- Invalid category
- Write permission error

## Related Components

**Related Commands**: [`system-timeline`](../commands/system-timeline.md), [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`index-rebuild`](../commands/index-rebuild.md)

**Examples**: See [Examples Library](../examples/) for usage patterns
