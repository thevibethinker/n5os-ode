---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_LhnxuEVVapCNdXle
---

# Model Preferences

## Default Build Model

Currently: `anthropic:claude-opus-4-5-20251101`

This is configurable in `Skills/pulse/config/pulse_v2_config.json` under `default_build_model`.

## Model Selection

- **Opus**: Complex builds, major writing, strategic decisions
- **Sonnet**: Fast iteration, simple tasks
- **Flash**: Quick lookups, simple routing

## Telemetry

All telemetry logs `used_default_model: true/false` to track when non-default models are used during builds.

## Build Model Override

Drops can override the default model by specifying in frontmatter:

```yaml
model: anthropic:claude-sonnet-4-20250514
```

When omitted, the default build model is used.
