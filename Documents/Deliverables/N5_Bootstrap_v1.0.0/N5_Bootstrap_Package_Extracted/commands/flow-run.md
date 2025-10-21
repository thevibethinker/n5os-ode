---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: ca016c4b94aee69fc2cba1c44efbc9fb
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands/flow-run.md
---
# `flow-run`\n\nVersion: 0.1.0\n\nSummary: Execute a flow by chaining modules in sequence.\n\nWorkflow: misc\n\nTags: flows, modules, execution\n\n## Inputs\n- flow : string (required) — Flow name to execute\n- inputs : json — Input parameters for the flow\n\n## Outputs\n- result : json — Execution results from each step\n\n## Uses\n- **Modules**: [`ingest-transcription-transformation`](../modules/ingest-transcription-transformation.md)\n\n## Side Effects\n- writes:file\n\n## Examples\n- N5: run flow-run flow=example-flow inputs={"audio_url": "http://example.com/audio.mp3"}\n\n## Related Components\n\n**Examples**: See [Examples Library](../examples/) for usage patterns\n\n