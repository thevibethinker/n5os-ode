---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: b1da85fff91dc484a4d2376c61edcf57
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/lists-move.md
---
# `lists-move`\n\nVersion: 0.1.0\n\nSummary: Move an item from one list to another atomically\n\nWorkflow: lists\n\nTags: lists, move\n\n## Inputs\n- source_list : string (required) — Source list slug\n- item_id : string (required) — Item ID to move\n- dest_list : string (required) — Destination list slug\n\n## Outputs\n- item_id : text — Moved item id\n- source_path : path — Source JSONL path\n- dest_path : path — Destination JSONL path\n\n## Side Effects\n- modifies:file\n- writes:file\n\n## Examples\n- N5: run lists-move ideas abc123 system-upgrades\n\n## Failure Modes\n- List not found\n- Item not found\n- Source equals dest\n- Schema validation failure\n\n## Related Components\n\n**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/lists-docgen.md)\n\n**Knowledge Areas**: [List Management](../knowledge/list-management.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n