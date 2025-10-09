---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 70d594623c75f3dc813350bd76cea015
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/docgen-with-schedule-wrapper.md
---
# `docgen-with-schedule-wrapper`\n\nVersion: 0.1.0\n\nSummary: Docgen command wrapped with scheduling wrapper for retries/lock/timezone/missed-run.\n\nWorkflow: ops\n\nTags: catalog, validation, schedule-wrapper\n\n## Outputs\n- catalog : file (markdown) — N5/commands.md\n\n## Side Effects\n- writes:file\n- modifies:file\n\n## Examples\n- N5: run docgen-with-schedule-wrapper --use-wrapper\n\n## Failure Modes\n- invalid schema\n- duplicate names\n\n## Related Components\n\n**Related Commands**: [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`index-rebuild`](../commands/index-rebuild.md), [`digest-runs`](../commands/digest-runs.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n

## Inputs
(None)
