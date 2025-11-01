---
description: 'Command: flow-run'
tags: []
tool: true
---
# `flow-run`

Version: 0.1.0

Summary: Execute a flow by chaining modules in sequence.

Workflow: misc

Tags: flows, modules, execution

## Inputs
- flow : string (required) â Flow name to execute
- inputs : json â Input parameters for the flow

## Outputs
- result : json â Execution results from each step

## Uses
- **Modules**: [`ingest-transcription-transformation`](../modules/ingest-transcription-transformation.md)

## Side Effects
- writes:file

## Examples
- N5: run flow-run flow=example-flow inputs={"audio_url": "http://example.com/audio.mp3"}

## Related Components

**Examples**: See [Examples Library](../examples/) for usage patterns

