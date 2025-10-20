---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 20c3fb6ccb24c15ea985474cb5a5b3b5
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/lists-export.md
---
# `lists-export`\n\nVersion: 0.1.0\n\nSummary: Export a list to MD or CSV format.\n\nWorkflow: lists\n\nTags: lists, export\n\n## Inputs\n- list : string (required) — List slug\n- format : enum (required)\n- output : path — Output file path\n\n## Outputs\n- file : path — Exported file path\n\n## Side Effects\n- writes:file\n\n## Examples\n- N5: run lists-export ideas md\n- N5: run lists-export ideas csv --output=/tmp/ideas.csv\n\n## Related Components\n\n**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/lists-docgen.md)\n\n**Knowledge Areas**: [List Management](../knowledge/list-management.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n