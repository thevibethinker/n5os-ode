---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 9cc2133e67b81d42efb3126ca9becadf
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/lists-set.md
---
# `lists-set`\n\nVersion: 0.1.0\n\nSummary: Update fields of an item in a list.\n\nWorkflow: lists\n\nTags: lists, update\n\n## Inputs\n- list : string (required) — List slug\n- item_id : string (required) — Item ID\n- title : text\n- body : text\n- tags : json\n- priority : enum\n- status : enum\n- project : text\n- due : text — ISO date\n- notes : text\n\n## Outputs\n- path : path — Path to JSONL file\n\n## Side Effects\n- modifies:file\n\n## Examples\n- N5: run lists-set list=ideas item_id=123 title="New Title"\n\n## Related Components\n\n**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/lists-docgen.md), [`lists-export`](../commands/lists-export.md)\n\n**Knowledge Areas**: [List Management](../knowledge/list-management.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n