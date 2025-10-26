---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 89afb1f4a116f09502c2212b4a0b7bcc
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/lists-pin.md
---
# `lists-pin`\n\nVersion: 0.1.0\n\nSummary: Pin or unpin an item in a list.\n\nWorkflow: lists\n\nTags: lists, pin\n\n## Inputs\n- list : string (required) — List slug\n- item_id : string (required) — Item ID\n\n## Outputs\n- path : path — Path to JSONL file\n\n## Side Effects\n- modifies:file\n\n## Examples\n- N5: run lists-pin list=ideas item_id=123\n- N5: run lists-pin list=ideas item_id=123 --unpin\n\n## Related Components\n\n**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md)\n\n**Knowledge Areas**: [List Management](../knowledge/list-management.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n