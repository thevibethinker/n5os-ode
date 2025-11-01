---
description: 'Command: careerspan-timeline'
tags: []
tool: true
---
# `careerspan-timeline`

Version: 0.1.0

Summary: View Careerspan company and personal life timeline

Workflow: knowledge

Tags: careerspan-timeline, history, company, personal

## Inputs
- year : string — Filter by year
- category : string — Filter by category (company, personal, milestone)
- limit : integer [default: all] — Number of entries to show
- format : enum [default: markdown] — Output format (markdown, json)

## Outputs
- entries : array — Timeline entries matching criteria
- count : integer — Number of entries returned


## Side Effects
(None)

## Examples
- N5: run careerspan-timeline
- N5: run careerspan-timeline year=2025
- N5: run careerspan-timeline category=company

## Failure Modes
- Invalid year format
- File not found

## Related Components

**Related Commands**: [`careerspan-timeline-add`](../commands/careerspan-timeline-add.md), [`knowledge-search`](../commands/knowledge-search.md)

**Examples**: See [Examples Library](../examples/) for usage patterns
