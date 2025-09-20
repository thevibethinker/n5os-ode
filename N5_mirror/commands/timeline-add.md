---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 26f1d4bcbb8e03ba29817c6cbe2140e2
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/timeline-add.md
---
# `timeline-add`\n\nVersion: 0.1.0\n\nSummary: Add new entry to n5.os development timeline\n\nWorkflow: ops\n\nTags: timeline, history, logging\n\n## Inputs\n- title : text (required) — Brief title of the change/feature\n- description : text (required) — Detailed description of what was added/changed\n- category : enum (required) — Type of change\n- version : string — Version number (optional)\n- components : json — Components affected (array)\n- impact : enum [default: medium] — Impact level\n- status : enum [default: completed] — Status\n- tags : json — Additional tags (array)\n\n## Outputs\n- entry_id : text — Created timeline entry ID\n- path : path — Path to timeline.jsonl\n\n## Side Effects\n- writes:file\n\n## Examples\n- N5: run timeline-add title='Added command authoring' category=feature description='Implemented new command authoring system'\n- N5: run timeline-add title='Fixed list validation' category=fix impact=low\n\n## Failure Modes\n- Invalid category\n- Write permission error\n\n## Related Components\n\n**Related Commands**: [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md), [`index-rebuild`](../commands/index-rebuild.md), [`digest-runs`](../commands/digest-runs.md)\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n