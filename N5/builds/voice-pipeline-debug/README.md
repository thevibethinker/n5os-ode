---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
---

# Voice Pipeline Debug Cycle

Orchestrated, evidence-based audit of Voice Library V2 + Voice Injection Layer + Pangram policy, producing a consolidated report and patch plan.

## Objective

Identify correctness gaps and policy conflicts; prove runtime wiring; deliver patch-ready recommendations without applying changes.

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| worker_runtime_wiring | runtime_wiring_audit | pending | - | 2h |
| worker_db_data_audit | db_data_audit | pending | - | 2h |
| worker_pangram_policy_audit | pangram_policy_audit | pending | - | 1h |
| worker_doc_hygiene_audit | doc_hygiene_audit | pending | - | 1h |

## Key Decisions

- Phase 1 is read-only audit with evidence; Phase 2 is patch plan only.
- Do not mistake prompt docs for runtime wiring; require script entrypoint proof.
- Pangram should be ad-hoc calibration, not an automatic gate (unless explicitly re-authorized).

## Relevant Files

- `N5/scripts/voice_layer.py`
- `N5/scripts/retrieve_primitives.py`
- `N5/scripts/extract_voice_primitives.py`
- `N5/data/voice_library.db`
- `Prompts/Follow-Up Email Generator.prompt.md`
- `Prompts/Blurb-Generator.prompt.md`
- `Prompts/X Thought Leader.prompt.md`
- `Prompts/Social Post Generate Multi Angle.prompt.md`
- `Prompts/Generate With Voice.prompt.md`
- `Prompts/Meeting Intelligence Generator.prompt.md`
- `Prompts/Pangram Check.prompt.md`
- `Prompts/Pangram.prompt.md`
- `N5/builds/voice-pipeline-debug/PLAN.md`
