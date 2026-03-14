---
created: 2026-03-10
last_edited: 2026-03-10
version: 1.0
provenance: con_OpmkepndGLiLsGms
---

# Zo Lead Mining — Build Plan

## Objective

Deep, exhaustive review of V's CRM (368 contacts) + semantic memory (37,875 blocks / 10,328 resources) to identify individuals who could be **power users, promoters, creators, or influential adopters** of Zo Computer.

**Output:** A single consolidated lead list ranked by potential, with minimal context per lead (name, org, role, why they matter for Zo).

## Lead Archetypes

| Archetype | Description |
|-----------|-------------|
| **Power User** | Technical or semi-technical person who would deeply use Zo's capabilities (automation, AI workflows, personal OS) |
| **Promoter** | Influencer, content creator, or community leader who would talk about Zo publicly |
| **Creator** | Builder who would create skills, integrations, or content on/for Zo |
| **Strategic Leader** | CEO/founder/team lead who would adopt Zo for their org or team |
| **Investor/Advisor** | VC or advisor in the AI/productivity/dev-tools space |

## Data Sources

1. **CRM Individuals** — `/home/workspace/Personal/Knowledge/CRM/individuals/` (368 files)
   - ~50 enriched profiles (>20 lines), rest are thin LD-GEN stubs
2. **Semantic Memory** — `N5/cognition/vectors_v2.db` (37,875 blocks)
   - Personal notes, conversation exports, documents, content library
   - Contains relationship context, meeting notes, interaction history not in CRM files
3. **Organizations** — `/home/workspace/Personal/Knowledge/CRM/organizations/`

## Approach

## Phase 1: Parallel Mining (Wave 1)

Each Drop scans a segment of data, extracts candidate leads, writes a deposit with structured results.

| Drop | Scope | Method |
|------|-------|--------|
| **D1.1** | CRM batch A-J (~145 files) | Read each CRM file, score against Zo archetypes |
| **D1.2** | CRM batch K-Z (~223 files) | Read each CRM file, score against Zo archetypes |
| **D1.3** | Semantic memory — tech/AI/tools/founder signals | Query vectors_v2.db for blocks mentioning AI tools, automation, Zo, personal OS, dev tools, power users, builders |
| **D1.4** | Semantic memory — relationship/influence signals | Query for blocks about influential people, investors, content creators, community leaders, promoters in V's network |

## Phase 2: Consolidation (Wave 2)

| Drop | Scope | Method |
|------|-------|--------|
| **D2.1** | Merge + deduplicate + rank | Read all Wave 1 deposits, merge into single ranked list, deduplicate, assign final scores |

## Success Criteria

1. Every CRM contact evaluated (368/368)
2. Semantic memory queried across at least 8 distinct signal dimensions
3. Final list contains all leads scoring >= 3/5 on Zo potential
4. Each lead has: name, org, role, archetype(s), 1-line rationale
5. No duplicates in final output

## Open Questions

- [x] What lead types exist in CRM? → Mostly LD-GEN, some LD-STRAT, LD-COM, LD-NET, LD-INV
- [x] How enriched are CRM profiles? → ~50 have >20 lines, rest are stubs
- [x] What's indexed in semantic memory? → 6919 Personal, 886 CRM, 510 Documents, 356 N5, 259 Skills resources

## Risks

- Thin CRM profiles may not have enough signal → Semantic memory compensates
- Semantic memory queries may surface noise → Filter by relevance score
- Some contacts may appear in both CRM and semantic memory → D2.1 deduplication handles this
