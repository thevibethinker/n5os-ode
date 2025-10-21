---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: e3ceb9fff329f77a3ac4608ab610d340
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/lists-docgen.md
---
# `lists-docgen`\n\nVersion: 0.1.0\n\nSummary: Regenerate MD views from JSONL for lists.\n\nWorkflow: lists\n\nTags: lists, docgen\n\n## Inputs\n- list : string — Specific list slug, else all\n\n## Outputs\n- md_files : json — Paths to updated MD files\n\n## Side Effects\n- writes:file\n- modifies:file\n\n## Examples\n- N5: run lists-docgen\n- N5: run lists-docgen list=ideas\n\n## Related Components\n\n**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-export`](../commands/lists-export.md)\n\n**Knowledge Areas**: [List Management](../knowledge/list-management.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n