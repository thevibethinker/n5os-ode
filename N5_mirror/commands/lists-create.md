---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: a8e25ed20f9938ccf33e697c0af20880
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/lists-create.md
---
# `lists-create`\n\nVersion: 0.1.0\n\nSummary: Create a new list registry entry with JSONL and MD files.\n\nWorkflow: lists\n\nTags: lists, registry\n\n## Inputs\n- slug : string (required) — List slug (lowercase, hyphens allowed)\n- title : text (required) — List title\n- tags : json — Tags\n\n## Outputs\n- registry : path — Path to index.jsonl\n- jsonl : path — Path to JSONL file\n- md : path — Path to MD file\n\n## Side Effects\n- writes:file\n- modifies:file\n\n## Examples\n- N5: run lists-create slug=ideas title="My Ideas" --dry-run\n\n## Related Components\n\n**Related Commands**: [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/lists-docgen.md), [`lists-export`](../commands/lists-export.md)\n\n**Knowledge Areas**: [List Management](../knowledge/list-management.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n