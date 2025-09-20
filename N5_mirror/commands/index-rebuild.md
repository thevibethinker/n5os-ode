---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: d342fb1e150533214d7b2a8bbb89fae4
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/index-rebuild.md
---
# `index-rebuild`\n\nVersion: 0.1.0\n\nSummary: Rebuild the N5 system index from source files\n\nWorkflow: ops\n\nTags: index, rebuild, system\n\n## Outputs\n- index_path : path — Path to the rebuilt index.jsonl\n\n## Side Effects\n- writes:file\n- modifies:file\n\n## Examples\n- N5: run index-rebuild\n\n## Failure Modes\n- Source file corruption\n- Permission errors\n\n## Related Components\n\n**Related Commands**: [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`digest-runs`](../commands/digest-runs.md)\n\n**Knowledge Areas**: [System Architecture](../knowledge/system-architecture.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n