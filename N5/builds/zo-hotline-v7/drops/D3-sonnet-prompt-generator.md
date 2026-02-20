---
created: 2026-02-19
drop_id: D3
stream: S2
title: Sonnet-Powered Prompt Generator
status: pending
depends_on: [D1]
provenance: con_tdpDMlVT0VZmXDPS
---

# D3: Sonnet-Powered Prompt Generator

## Objective

Upgrade `generateFollowUpContent` to produce Zo-native, implementation-ready prompts using Sonnet 4.6 (for co-build calls) and the meta-prompter context from D1. Standard calls continue using Haiku.

## Deliverables

1. **Upgraded `generateFollowUpContent`** in `hotline-webhook.ts`:
   - Detects whether call had co-build diagnostic data
   - **Co-build path** (Sonnet): Injects meta-prompter context + diagnostic data → generates prompts that create rules, scheduled agents, personas, pipelines, etc.
   - **Standard path** (Haiku): Injects meta-prompter context → generates better-than-current prompts that at least reference Zo-specific features
   - Both paths produce paste-ready prompts, not generic suggestions

2. **Prompt output structure** — Each prompt should include:
   - A clear label ("Set up your morning briefing", "Create a client intake pipeline")
   - The actual prompt text that works when pasted into Zo
   - Prompt harness patterns where appropriate: structured instructions that guide Zo to ask the right clarifying questions before executing

3. **Model routing logic**:
   - `ANTHROPIC_SONNET_MODEL` constant: `claude-sonnet-4-20250514`
   - `ANTHROPIC_HAIKU_MODEL` constant: `claude-haiku-4-5-20251001`
   - Co-build calls → Sonnet for prompt generation
   - Standard calls → Haiku for prompt generation (but with meta-prompter context)
   - All other LLM calls (email, topic classification) → Haiku unchanged

## Constraints

- Meta-prompter context from D1 must be loaded at startup and cached
- Sonnet calls should have higher max_tokens (2000) vs Haiku (1000)
- Generated prompts must be specific to the caller's discussed use case, not generic

## Deposit

`deposits/D3-sonnet-prompt-generator.json` with:
- `model_routing`: description of when each model is used
- `prompt_quality_sample`: one example generated prompt (from test data)
- `files_modified`: list of changed files
