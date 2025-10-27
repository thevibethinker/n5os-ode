---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 67c733eeb085fea3f102a9f113515abe
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/system-timeline.md
---
# `system-timeline`

Version: 0.1.0

Summary: View N5 OS system development timeline and history

Workflow: ops

Tags: system-timeline, history, system, n5-os

## Inputs
- category : string — Filter by category (infrastructure,feature,command,workflow,ui,integration,fix)
- from : date — Start date (ISO format)
- to : date — End date (ISO format)
- limit : integer [default: 20] — Number of entries to show
- format : enum [default: table] — Output format

## Outputs
- entries : array — Timeline entries matching criteria
- count : integer — Number of entries returned


## Side Effects
(None)

## Examples
- N5: run system-timeline
- N5: run system-timeline category=feature limit=10

## Failure Modes
- Invalid date format
- Category not found

## Related Components

**Related Commands**: [`system-timeline-add`](../commands/system-timeline-add.md), [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`index-rebuild`](../commands/index-rebuild.md)

**Examples**: See [Examples Library](../examples/) for usage patterns
