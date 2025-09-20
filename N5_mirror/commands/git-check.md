---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: d586cee8f81dcb70956621e04198bb8b
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/git-check.md
---
# `git-check`\n\nVersion: 0.1.0\n\nSummary: Quick audit for overwrites or data loss in staged Git changes\n\nAliases: audit-changes\n\nWorkflow: ops\n\nTags: git, audit\n\n## Outputs\n- report : text — Audit report\n\n## Examples\n- N5: run git-check\n\n## Failure Modes\n- git error\n\n## Related Components\n\n**Related Commands**: [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`index-rebuild`](../commands/index-rebuild.md), [`digest-runs`](../commands/digest-runs.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n