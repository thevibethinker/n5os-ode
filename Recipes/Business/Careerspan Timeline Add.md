---
description: 'Command: careerspan-timeline-add'
tags: []
---
# `careerspan-timeline-add`

Version: 0.1.0

Summary: Add new entry to Careerspan company and personal life timeline

Workflow: knowledge

Tags: careerspan-timeline, history, logging, company, personal

## Inputs
- year : string (required) — Year or date of the event
- title : text (required) — Brief title of the event/milestone
- description : text (required) — Detailed description
- category : enum — Type of event (company, personal, milestone)
- tags : json — Additional tags (array)

## Outputs
- success : boolean — Whether the entry was added
- path : path — Path to careerspan-timeline.md

## Side Effects
- writes:file

## Examples
- N5: run careerspan-timeline-add year='October 2025' title='Series A Funding' description='Raised $5M Series A' category=company
- N5: run careerspan-timeline-add year='2025' title='Product Launch' description='Launched career agent platform'

## Failure Modes
- Invalid category
- Write permission error

## Related Components

**Related Commands**: [`careerspan-timeline`](../commands/careerspan-timeline.md), [`knowledge-ingest`](../commands/knowledge-ingest.md)

**Examples**: See [Examples Library](../examples/) for usage patterns
