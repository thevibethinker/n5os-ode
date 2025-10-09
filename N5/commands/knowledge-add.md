---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 3a0ae99b90af3c19304189f1b4347569
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/knowledge-add.md
---
# `knowledge-add`\n\nVersion: 0.1.0\n\nSummary: Add a fact to the knowledge base.\n\nWorkflow: knowledge\n\nTags: knowledge, facts\n\n## Inputs\n- subject : text (required) — Subject of the fact\n- predicate : text (required) — Predicate/relationship\n- object : text (required) — Object of the fact\n- source : text — Source of the fact\n- tags : json — Tags for the fact\n\n## Outputs\n- fact_id : text — Created fact ID\n\n## Side Effects\n- writes:file\n\n## Examples\n- N5: run knowledge-add subject=N5 predicate=is object='Neural Network OS'\n\n## Related Components\n\n**Related Commands**: [`knowledge-find`](../commands/knowledge-find.md)\n\n**Knowledge Areas**: [Knowledge Base](../knowledge/knowledge-base.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n