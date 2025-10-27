---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: e6a138d7d79e096d7c1e1a0827cb3a60
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/knowledge-find.md
---
# `knowledge-find`\n\nVersion: 0.1.0\n\nSummary: Search and filter facts in the knowledge base.\n\nWorkflow: knowledge\n\nTags: knowledge, facts, search\n\n## Inputs\n- subject : text — Subject to match\n- predicate : text — Predicate to match\n- object : text — Object to match\n- tags : json — Tags to match\n- source : text — Source to match\n\n## Outputs\n- facts : json — Matching facts\n\n## Side Effects
(None)

## Examples\n- N5: run knowledge-find subject=N5\n- N5: run knowledge-find tags=["list","promoted"]\n\n## Related Components\n\n**Related Commands**: [`knowledge-add`](../commands/knowledge-add.md)\n\n**Knowledge Areas**: [Knowledge Base](../knowledge/knowledge-base.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n