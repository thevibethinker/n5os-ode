---
created: 2026-02-17
last_edited: 2026-02-17
version: 2.0
provenance: con_korOfWz5bTYqA9FI
drop: D5
build: zo-hotline-v4
---

# D5 Deposit: Zo Documentation Ingestion — Complete

## Summary

Comprehensive documentation ingestion covering all three knowledge domains for the Zo Hotline, plus a conversational playbook bootstrapped from thematic analysis of 34 calls.

## Deliverables

### 1. Platform Documentation (96-zo-platform/) — 41 files
- **24 core files**: Every feature of Zo documented voice-friendly (≤200 words each)
- **12 gap-fill files**: Caught by sitemap diff (BYOK, Claude Code, Codex, billing, FAQ, SSH, etc.)
- **5 skills registry files**: 114 skills from zocomputer/skills catalogued across 4 categories
- All sourced from live docs.zocomputer.com + zocomputer.com + GitHub manifest

### 2. Pedagogy File (96-zo-platform/designing-rules-and-personas.md)
- Bridges Domain 1 (features) and Domain 2 (Meta-OS) — teaches callers HOW to design rules/personas
- 183 words, voice-optimized

### 3. Conversational Playbook (97-conversational-playbook/) — 6 files
- **00-playbook-overview.md**: Master pattern (Elicit → Mirror → Layer → Anchor), three caller modes
- **explorer-pathway.md**: For "just checking it out" callers (75% of volume) — profession pivots, fallback offers
- **challenger-pathway.md**: For "how is this different from Claude" callers — honesty-first framework, concession moves
- **builder-pathway.md**: For "I want to build X" callers — layering pattern with real examples from calls
- **proven-phrases.md**: Specific language that generated engagement (quantified value, scheduled agent reveal)
- **danger-zones.md**: 6 documented patterns that caused disengagement (abrupt corrections, feature avalanche, etc.)

### 4. Concept Mapping — ~280 entries in hotline-webhook.ts
- Platform docs: ~194 mappings
- Skills registry: ~40 mappings
- Playbook: 21 mappings
- Dual-variant (hyphen + underscore) for all entries
- Webhook still builds clean (1278 lines)

### 5. Freshness Agent — Scheduled monthly
- Checks docs.zocomputer.com sitemap for new/changed pages
- Checks zocomputer/skills manifest for new skills
- Auto-generates knowledge files for new content
- Emails report on 1st of each month, 10 AM ET

## Handoff to D4 (Conversation Design v3)

The playbook is bootstrapped but needs:
1. **System prompt integration** — Playbook patterns should inform Zoseph's system prompt directly
2. **Profession-specific pathways** — Expand explorer-pathway with 10+ profession variants
3. **Call-flow state machine** — Formalize the Elicit→Mirror→Layer→Anchor sequence into prompt logic
4. **Additional language mining** — As more calls come in, extract proven phrases and add to playbook

## Metrics

| Metric | Value |
|--------|-------|
| Knowledge files created | 48 (41 platform + 1 pedagogy + 6 playbook) |
| Concept mappings added | ~280 |
| Skills catalogued | 114 |
| Sitemap coverage | 30/30 core pages |
| Webhook file size | 1278 lines (builds clean) |
| Voice compliance | All files ≤200 words (except skills lists ~400-500w) |
