---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 8b28b93ff05e9282939979e520f6ed1e
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/docgen.md
---
# `docgen`\n\nVersion: 0.1.0\n\nSummary: Generate command catalog and update prefs Command Index from commands.jsonl\n\nAliases: generate-docs\n\nWorkflow: ops\n\nTags: catalog, validation\n\n## Outputs\n- catalog : file (markdown) — N5/commands.md\n\n## Side Effects\n- writes:file\n- modifies:file\n\n## Examples\n- N5: run docgen\n\n## Failure Modes\n- invalid schema\n- duplicate names\n\n## Related Components\n\n**Related Commands**: [`index-update`](../commands/index-update.md), [`index-rebuild`](../commands/index-rebuild.md), [`digest-runs`](../commands/digest-runs.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n