---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: a9016c685dfe5237036449cbd3200ed0
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/index-update.md
---
# `index-update`\n\nVersion: 0.1.0\n\nSummary: Update the N5 index incrementally, scanning only changed files.\n\nAliases: index-incr\n\nWorkflow: ops\n\nTags: index, incremental\n\n## Outputs\n- index : file (jsonl) — N5/index.jsonl\n\n## Side Effects\n- writes:file\n- modifies:file\n\n## Examples\n- N5: run index-update\n\n## Related Components\n\n**Related Commands**: [`docgen`](../commands/docgen.md), [`index-rebuild`](../commands/index-rebuild.md), [`digest-runs`](../commands/digest-runs.md)\n\n**Knowledge Areas**: [System Architecture](../knowledge/system-architecture.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n