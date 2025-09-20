---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 67c733eeb085fea3f102a9f113515abe
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/timeline.md
---
# `timeline`\n\nVersion: 0.1.0\n\nSummary: View n5.os development timeline and system history\n\nWorkflow: ops\n\nTags: timeline, history, system\n\n## Inputs\n- category : string — Filter by category (infrastructure,feature,command,workflow,ui,integration,fix)\n- from : date — Start date (ISO format)\n- to : date — End date (ISO format)\n- limit : integer [default: 20] — Number of entries to show\n- format : enum [default: table] — Output format\n\n## Outputs\n- entries : array — Timeline entries matching criteria\n- count : integer — Number of entries returned\n\n## Examples\n- N5: run timeline\n- N5: run timeline category=feature limit=10\n\n## Failure Modes\n- Invalid date format\n- Category not found\n\n## Related Components\n\n**Related Commands**: [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`index-rebuild`](../commands/index-rebuild.md), [`digest-runs`](../commands/digest-runs.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n