---
created: 2026-02-11
last_edited: 2026-02-11
version: 1.0
provenance: lora-voice-evolution
---

# LoRA Voice Evolution: Orchestrator Document

## Current Status

**Phase:** Planning Complete → Ready for Wave 1  
**Active Wave:** W1 (Data Collection)  
**Next Action:** Spawn W1 Drops for source discovery and extraction

## Build Overview

This build creates a fine-tuned LLM using LoRA that encodes V's authentic writing voice directly into model weights. See `PLAN.md` for full specification.

## Quick Commands

```bash
# Check status
python3 Skills/pulse/scripts/pulse.py status lora-voice-evolution

# Validate plan
python3 Skills/pulse/scripts/pulse.py validate lora-voice-evolution

# Start automated orchestration
python3 Skills/pulse/scripts/pulse.py start lora-voice-evolution

# Manual tick (for testing)
python3 Skills/pulse/scripts/pulse.py tick lora-voice-evolution

# Launch a manual Drop
python3 Skills/pulse/scripts/pulse.py launch lora-voice-evolution <drop_id>
```

## Wave Progress

| Wave | Status | Drops | Description |
|------|--------|-------|-------------|
| W1 | pending | 9 | Source discovery and extraction |
| W2 | pending | 6 | Dataset formatting |
| W3 | pending | 6 | Training environment setup |
| W4 | pending | 6 | Model training execution |
| W5 | pending | 6 | vLLM server setup |
| W6 | pending | 6 | API development |
| W7 | pending | 8 | Voice system integration |
| W8 | pending | 5 | User interface |
| W9 | pending | 7 | Testing and validation |
| W10 | pending | 5 | Documentation and handoff |

## Checkpoints (Human Review Required)

1. **After W1:** Dataset Quality Review — V reviews curated samples
2. **After W4:** Model Validation — V reviews sample outputs
3. **After W8:** End-to-End Test — V tests integrated system

## Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Training data | `Datasets/lora-voice-training/train.jsonl` | pending |
| LoRA adapter | `N5/builds/lora-voice-evolution/artifacts/v-voice-lora-adapter/` | pending |
| API server | `va.zo.space/api/generate-voice` | pending |

## Notes

- This is a delegate-only build — all work happens in Drops
- GPU time required for W3-W4 (training phase)
- Estimated total build time: 2-3 days (mostly sequential due to dependencies)
