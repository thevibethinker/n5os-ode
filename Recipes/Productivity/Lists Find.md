---
description: 'Command: lists-find'
tags: []
---
# `lists-find`\n\nVersion: 0.1.0\n\nSummary: Search and filter items in a list.\n\nWorkflow: lists\n\nTags: lists, search\n\n## Inputs\n- list : string (required) — List slug\n- status : enum\n- priority : enum\n- tags : json — Tags to match\n- project : text\n- title-contains : text — Substring in title\n\n## Outputs\n- items : json — Matching items\n\n## Side Effects
(None)

## Examples\n- N5: run lists-find list=ideas status=open\n- N5: run lists-find list=ideas --count\n\n## Related Components\n\n**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-docgen`](../commands/docgen.md), [`lists-export`](../commands/lists-export.md)\n\n**Knowledge Areas**: [List Management](../knowledge/list-management.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n