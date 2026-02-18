---
created: 2026-02-17
last_edited: 2026-02-17
version: 2.0
provenance: con_D22Ewo8OGuQrMBrx
spawn_mode: manual
status: complete
dependencies: []
build: zo-hotline-v4
---

# D5: Zo Documentation Ingestion

## Objective

Ingest, parse, and structure official Zo Computer documentation so Zoseph can reference it accurately during calls. This is the foundation drop — every other drop benefits from Zoseph actually knowing what Zo does.

## Current State

- **46 knowledge files** in `Knowledge/zo-hotline/` organized by numbered folders (00-95)
- **90+ concept mappings** in `Skills/zo-hotline/scripts/hotline-webhook.ts` (the `conceptFiles` object)
- **explainConcept tool** reads files from `Knowledge/zo-hotline/` and returns content to the model
- Knowledge was hand-written during v1-v3 builds — NOT sourced from actual Zo docs
- Callers ask about features, pricing, integrations, troubleshooting — Zoseph currently wings it from the system prompt's brief feature list

## What to Crawl

### Primary Sources
1. **support.zocomputer.com** — Official support docs (features, how-tos, troubleshooting)
2. **zocomputer.com** — Marketing site (pricing, plans, positioning, feature descriptions)

### Secondary Sources (if primary is thin)
3. **Zo changelog/blog** — Recent feature announcements
4. **zo.space docs** — If separate from support site

## Deliverables

### 1. Parsed Doc Files
- Target location: `Knowledge/zo-hotline/` (augment existing structure)
- Format: Voice-friendly markdown — short paragraphs, no tables, no code blocks longer than 2 lines
- Each file should be readable aloud in under 60 seconds (roughly 150-200 words max per concept chunk)
- Use the existing numbered folder convention (e.g., new files could go in a `45-zo-features/` or similar)

### 2. Updated Concept Mapping
- Add new entries to the `conceptFiles` object in `hotline-webhook.ts`
- Include both hyphen and underscore variants (existing pattern)
- Map common caller phrasings, not just technical names

### 3. Gap Analysis
- What's in the docs that Zoseph doesn't currently know
- What callers ask about (from thematic analysis) that the docs don't cover
- What's in the system prompt that contradicts the actual docs (pricing especially)

## Key Design Decisions to Make During the Drop

1. **Chunk size**: How big should each knowledge file be? Current files vary wildly (some are 50 words, some are 500+). Voice retrieval favors shorter — the model reads the whole file into context on each explainConcept call.

2. **Augment vs restructure**: The existing 00-95 folder numbering system covers the Meta-OS framework. Zo platform docs are a different category. Subfolder? New number range? Separate directory?

3. **Freshness strategy**: Docs will go stale as Zo ships updates. How do we flag this? (Can be deferred but worth noting.)

## Reference Files

- Existing knowledge base: `Knowledge/zo-hotline/` (46 files across 10 folders)
- Concept mapping: `Skills/zo-hotline/scripts/hotline-webhook.ts` (search for `conceptFiles`)
- Thematic analysis: `Research/zo-hotline/hotline-thematic-analysis.md` (what callers actually ask)
- System prompt: `Skills/zo-hotline/prompts/zoseph-system-prompt.md` (current Zo knowledge section)

## Acceptance Criteria

- [ ] All major Zo features documented in voice-friendly format
- [ ] Pricing/plans accurate and current
- [ ] Integration list complete (Gmail, Calendar, Drive, Notion, Airtable, Stripe, etc.)
- [ ] Troubleshooting coverage expanded beyond current basics
- [ ] conceptFiles mapping updated with new entries
- [ ] Gap analysis delivered
- [ ] No file exceeds ~200 words (voice-optimized chunking)
