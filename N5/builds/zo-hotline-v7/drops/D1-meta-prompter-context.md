---
created: 2026-02-19
drop_id: D1
stream: S1
title: Meta-Prompter Context
status: pending
depends_on: []
provenance: con_tdpDMlVT0VZmXDPS
---

# D1: Meta-Prompter Context

## Objective

Build a condensed Zo capabilities index (~2-3KB) that the prompt generator can use to create implementation-ready prompts. This is NOT the full knowledge base — it's a curated cheat sheet of "what's possible on Zo" optimized for prompt generation.

## Deliverables

1. **`Skills/zo-hotline/assets/meta-prompter-context.md`** — Condensed capabilities index covering:
   - Rules (always-applied, conditional) with example syntax
   - Scheduled agents (cron patterns, delivery methods, what they can do)
   - Personas (custom AI personalities, switching)
   - zo.space (pages, APIs, widgets — instant deploy)
   - Datasets (import, query, analyze)
   - Integrations (Gmail, Calendar, Drive, Notion, Airtable)
   - Pipelines (email → processing → output patterns)
   - File organization patterns (Documents/, Projects/, Knowledge/)
   - SMS/email delivery
   - Key prompting patterns that work well on Zo

2. **`Skills/zo-hotline/assets/meta-prompter-examples.md`** — 8-10 example "Zo-native prompts" across use cases showing what good output looks like. Each should be paste-ready and actually work.

## Constraints

- Total context must fit in ~3KB (will be injected into LLM prompt)
- Must be model-agnostic (works whether Sonnet or Haiku reads it)
- Include "prompt harness" patterns: structured instructions that guide Zo to ask clarifying questions before executing
- Periodic refresh: design for easy updates (just re-read the file)

## Source Material

- `Knowledge/zo-hotline/96-zo-platform/` — 41 platform docs
- `Knowledge/zo-hotline/70-architectural-patterns/` — webhook, dataset, pipeline patterns
- `Knowledge/zo-hotline/90-technical-advice/` — rules vs personas, debugging, zo.space tips
- Existing Zo capabilities from the system (rules, agents, personas, integrations)

## Deposit

`deposits/D1-meta-prompter-context.json` with:
- `files_created`: list of file paths
- `context_size_bytes`: size of the condensed context
- `capabilities_covered`: list of Zo capabilities included
- `example_count`: number of example prompts
