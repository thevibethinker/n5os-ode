---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 0c72c6c941bcc5145a10f36539a8989a
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/lists-promote.md
---
# `lists-promote`\n\nVersion: 0.1.0\n\nSummary: Promote a list with explicit approval.\n\nWorkflow: lists\n\nTags: lists, promote\n\n## Inputs\n- list : string (required) — List slug\n\n## Outputs\n- registry : path — Updated registry\n- md : path — Updated MD file\n\n## Side Effects\n- modifies:file\n- writes:file\n\n## Permissions Required\n- email_approval\n\n## Examples\n- N5: run lists-promote ideas --approve\n\n## Related Components\n\n**Related Commands**: [`lists-create`](../commands/lists-create.md), [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/docgen.md)\n\n**Knowledge Areas**: [List Management](../knowledge/list-management.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n