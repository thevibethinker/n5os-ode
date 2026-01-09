---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_OYys6PCWmGnEhbmU
---

# R-Block Framework: Central Theory & Deep Analysis Prompts

**Build ID:** r-block-framework  
**Status:** Planning  
**Architect:** Vibe Architect  

---

## Open Questions

1. **RESOLVED:** Query existing profiles (knowledge, positions, meetings). Create emergent `integration-patterns` store only when patterns earn promotion (appear in 3+ reflections OR become super-connectors with 5+ links).
2. **RESOLVED:** Both JSONL edges (machine-queryable at `N5/data/reflection_edges.jsonl`) AND inline markdown in RIX output (human-readable). RIX writes both simultaneously.
3. **RESOLVED:** <100 words = skip full block processing, create lightweight capture only (title + timestamp + raw text).

---

## Central Theory: The R-Block Substructure

### Core Principle

Every R-block is a **lens** — a specific analytical framework applied to raw thought. The same transcript viewed through R04 (Market) reveals different intelligence than through R05 (Product) or R03 (Strategic).

Each lens must be:
- **Deep:** Not a summary, but a rigorous extraction with supporting evidence
- **Deterministic:** Same input → same structural output (content varies, structure doesn't)
- **Connectable:** Outputs that can be linked to prior knowledge and future reflections

### The Common Substructure (All R-Blocks)

Every R-block prompt MUST contain these seven sections:

```
┌─────────────────────────────────────────────────────────┐
│  1. DOMAIN DEFINITION                                   │
│     - What this lens sees                               │
│     - What it ignores                                   │
│     - Boundary conditions (when to use, when not to)    │
├─────────────────────────────────────────────────────────┤
│  2. MEMORY CONTEXT (Load First)                         │
│     - Which memory profiles to query                    │
│     - What prior knowledge enriches this analysis       │
│     - How to detect "this connects to X"                │
├─────────────────────────────────────────────────────────┤
│  3. EXTRACTION FRAMEWORK                                │
│     - The specific analytical questions this lens asks  │
│     - Evidence requirements (quotes, specificity)       │
│     - Depth expectations (not surface summaries)        │
├─────────────────────────────────────────────────────────┤
│  4. OUTPUT SCHEMA                                       │
│     - Structured markdown format                        │
│     - Required fields vs optional fields                │
│     - Metadata (frontmatter, provenance, timestamps)    │
├─────────────────────────────────────────────────────────┤
│  5. QUALITY GATES                                       │
│     - Minimum substance threshold                       │
│     - Anti-patterns to avoid                            │
│     - "Not applicable" criteria                         │
├─────────────────────────────────────────────────────────┤
│  6. CONNECTION HOOKS                                    │
│     - How to flag potential links to other content      │
│     - Tags/categories for cross-reference               │
│     - Input to Integration Block (RIX)                  │
├─────────────────────────────────────────────────────────┤
│  7. EXAMPLE (Worked)                                    │
│     - Real or realistic example showing depth expected  │
│     - Demonstrates the difference between shallow/deep  │
└─────────────────────────────────────────────────────────┘
```

### The Integration Block (RIX)

**Architectural Decision:** RIX is a **special block** — not numbered, always runs after all applicable R-blocks complete. It is the mandatory final step of reflection processing.

**Why distinct from numbered blocks:**
- R01-R09 are **lenses** — selective, may return "not applicable"
- RIX is **connective tissue** — always runs, never "not applicable" (at minimum outputs "novel territory - no prior connections found")

**Memory Query Strategy:**
- Query existing profiles: `knowledge`, `positions`, `meetings`
- Do NOT create a separate `reflections` profile initially
- If cross-profile noise becomes a problem, revisit this decision

**Purpose:** Connect the current reflection to V's existing knowledge graph.

**Runs AFTER** all applicable R-blocks are generated. Takes as input:
- The raw transcript
- All generated R-blocks from this reflection
- Query results from semantic memory

**Outputs:**
- Explicit connections to prior reflections, positions, knowledge articles
- New edges to add to the knowledge graph
- "This extends/challenges/refines [prior idea]" declarations
- Suggestions for knowledge consolidation

### Processing Flow

```
Raw Reflection
      │
      ▼
┌─────────────────┐
│  Classification │ ← Identify which R-blocks are applicable
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Parallel R-Block Generation            │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │
│  │ R03 │ │ R04 │ │ R05 │ │ ... │       │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘       │
└─────┼───────┼───────┼───────┼──────────┘
      │       │       │       │
      └───────┴───────┴───────┘
                  │
                  ▼
         ┌───────────────┐
         │  RIX Block    │ ← Integration: connect to knowledge graph
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │  File Output  │ ← Multiple files per reflection
         └───────────────┘
```

### File Structure Per Reflection

```
Personal/Reflections/YYYY/MM/YYYY-MM-DD_slug/
├── transcript.md          # Original input (preserved)
├── R03_strategic.md       # If applicable
├── R04_market.md          # If applicable
├── R05_product.md         # If applicable
├── R0X_....md             # Other applicable blocks
├── RIX_integration.md     # Always generated (connections)
└── manifest.json          # Metadata, blocks generated, connections found
```

---

## Checklist

### Phase 1: Foundation
- [ ] Finalize common substructure template
- [ ] Define memory query patterns for reflections
- [ ] Create base prompt template that all R-blocks inherit from

### Phase 2: Block Development (One per R-type)
- [ ] R01: Personal Insight — deep emotional/psychological extraction
- [ ] R02: Learning Note — knowledge acquisition patterns
- [ ] R03: Strategic Thought — business/life direction analysis
- [ ] R04: Market Signal — competitive intelligence framework
- [ ] R05: Product Idea — feature/capability extraction with evidence
- [ ] R06: Synthesis — cross-domain connection detection
- [ ] R07: Prediction — future state hypothesis with falsifiability
- [ ] R08: Venture Idea — business opportunity assessment
- [ ] R09: Content Idea — publishable content extraction
- [ ] R00: Emergent — new category detection (already more developed)

### Phase 3: Integration Layer
- [ ] RIX: Integration Block — knowledge graph connection engine
- [ ] Define edge types (extends, challenges, refines, supports, contradicts)
- [ ] Memory profile setup for reflections corpus

### Phase 4: Orchestration
- [ ] Update Process Reflection prompt as orchestrator
- [ ] Classification logic (which blocks apply)
- [ ] Parallel execution pattern
- [ ] Output filing and manifest generation

---

## Phase 1: Foundation

### Affected Files
- `N5/templates/r-block-base.md` (NEW) — base template all R-blocks inherit
- `N5/prefs/reflection_engine_config.md` — update with memory query patterns

### Changes

**Create base template** with all seven sections as scaffolding. Each R-block will:
1. Import/inherit the base structure
2. Fill in domain-specific content for each section
3. Maintain structural consistency

**Memory query pattern:**
```python
# Standard queries for any R-block
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()

# 1. Prior reflections on similar topics
prior_reflections = client.search_profile(
    profile="reflections",
    query=f"{key_concepts_from_transcript}",
    limit=5
)

# 2. Related positions (V's established views)
related_positions = client.search_profile(
    profile="positions", 
    query=f"{key_concepts_from_transcript}",
    limit=3
)

# 3. Knowledge articles that might connect
knowledge_hits = client.search_profile(
    profile="knowledge",
    query=f"{key_concepts_from_transcript}",
    limit=5
)
```

### Unit Tests
- [ ] Base template renders valid markdown
- [ ] Memory query returns expected structure
- [ ] Empty transcript handled gracefully (returns "insufficient content")

---

## Phase 2: Block Development

### Affected Files
- `Prompts/Blocks/Reflection/R01_Personal.prompt.md` — REWRITE
- `Prompts/Blocks/Reflection/R02_Learning.prompt.md` — REWRITE
- `Prompts/Blocks/Reflection/R03_Strategic.prompt.md` — REWRITE
- `Prompts/Blocks/Reflection/R04_Market.prompt.md` — REWRITE
- `Prompts/Blocks/Reflection/R05_Product.prompt.md` — REWRITE
- `Prompts/Blocks/Reflection/R06_Synthesis.prompt.md` — REWRITE
- `Prompts/Blocks/Reflection/R07_Prediction.prompt.md` — REWRITE
- `Prompts/Blocks/Reflection/R08_Venture.prompt.md` — REWRITE
- `Prompts/Blocks/Reflection/R09_Content.prompt.md` — REWRITE

### Changes

Each block goes from ~40 lines (output template) to ~150-250 lines (deep analytical framework).

**Example transformation for R04 (Market Signal):**

Current (skeleton):
```markdown
## Output Format
1. Signal
2. Source  
3. Signal Strength
4. Implication for Careerspan
```

Target (deep framework):
```markdown
## Domain Definition
R04 sees: Competitive dynamics, market trends, distribution channels, 
customer segments, pricing signals, technology shifts, regulatory changes,
partnership opportunities, threat vectors.

R04 ignores: Internal product decisions (R05), personal reactions (R01),
strategic direction (R03 unless market-driven).

## Extraction Framework

### Market Structure Analysis
- Who are the players mentioned? (Direct competitors, adjacent players, enablers)
- What market category is being discussed?
- What's the competitive dynamic? (Winner-take-all, fragmented, consolidating)

### Signal Extraction
For EACH market signal identified:
1. **The Signal:** What specifically was observed/discussed
2. **Evidence:** Direct quote or specific reference
3. **Signal Type:** [Competitive | Trend | Opportunity | Threat | Channel | Pricing]
4. **Confidence:** [High: firsthand/validated | Medium: secondhand/plausible | Low: speculation]
5. **Time Horizon:** [Immediate | 6-12mo | 1-3yr | Secular trend]

### Implication Mapping
- How does this affect Careerspan's positioning?
- Does this validate or invalidate current assumptions?
- What action might this signal warrant?

### Competitor/Player Profiles
For each entity mentioned:
- Name
- Category (competitor, partner, customer, threat)
- What was revealed about them
- Intelligence gap (what we still don't know)

## Quality Gates
- Minimum: 2 distinct signals with evidence
- Each signal must have a direct quote or specific reference
- "Implication" must be specific to Careerspan, not generic
- NOT APPLICABLE if: Reflection contains no market/competitive content
```

### Unit Tests
- [ ] Each rewritten block follows 7-section structure
- [ ] Example output demonstrates expected depth
- [ ] "Not applicable" fires correctly on non-matching content

---

## Phase 3: Integration Layer

### Affected Files
- `Prompts/Blocks/Reflection/RIX_Integration.prompt.md` (NEW)
- `N5/cognition/reflection_edges.py` (NEW) — edge type definitions
- `N5/data/reflection_graph.jsonl` (NEW) — connection storage

### Changes

**RIX Integration Block extracts:**

1. **Explicit Connections**
   - "This reminds me of..." → link to prior reflection
   - "This builds on..." → extends relationship
   - "This contradicts..." → challenges relationship

2. **Implicit Connections** (via semantic search)
   - Similar concepts in prior reflections
   - Related positions that might need updating
   - Knowledge articles that connect

3. **Edge Types**
   ```
   EXTENDS    — builds on prior idea
   CHALLENGES — contradicts or questions prior idea
   REFINES    — narrows or clarifies prior idea
   SUPPORTS   — provides evidence for prior idea
   CONNECTS   — thematic link without directional relationship
   SUPERSEDES — replaces prior idea entirely
   ```

4. **Output Format**
   ```markdown
   ## RIX: Integration Analysis
   
   ### Connections Found
   
   #### To Prior Reflections
   - **EXTENDS** `2025-12-15_candidate-ownership-model`
     - This reflection develops the "candidate as customer" thread
     - Specific link: [quote from current] ↔ [quote from prior]
   
   #### To Positions
   - **SUPPORTS** Position #47: "Distribution > Product in early markets"
     - Evidence: [quote about AI headhunters as channel]
   
   #### To Knowledge Base
   - **CONNECTS** `Knowledge/market-intel/ai-recruiting-landscape.md`
     - New information about Marvin, Ribbon worth adding
   
   ### Suggested Actions
   - [ ] Update position #47 with new supporting evidence
   - [ ] Add Marvin profile to competitor tracking
   - [ ] Flag for weekly synthesis review
   ```

### Unit Tests
- [ ] Edge types validate correctly
- [ ] JSONL edges are parseable
- [ ] Duplicate connections detected and merged

---

## Phase 4: Orchestration

### Affected Files
- `Prompts/Process Reflection.prompt.md` — REWRITE as orchestrator
- `N5/scripts/reflection_processor.py` (NEW) — automation support

### Changes

**Process Reflection becomes pure orchestrator:**

1. **Input Resolution** (existing, keep)
2. **Classification** — determine which R-blocks apply
3. **Parallel Dispatch** — invoke relevant R-block prompts
4. **Integration** — invoke RIX after all blocks complete
5. **Filing** — create folder structure, manifest

**Classification Logic:**
```python
# Signal words/patterns that trigger each block
BLOCK_TRIGGERS = {
    "R01": ["feel", "frustrated", "excited", "worried", "energy", "drained"],
    "R02": ["learned", "realized", "discovered", "understood", "insight"],
    "R03": ["strategy", "direction", "priority", "focus", "bet", "decision"],
    "R04": ["competitor", "market", "customer", "channel", "pricing", "trend"],
    "R05": ["feature", "build", "product", "user", "interface", "workflow"],
    "R06": ["connects to", "reminds me", "pattern", "across", "synthesis"],
    "R07": ["predict", "will happen", "in X years", "bet that", "future"],
    "R08": ["startup idea", "business", "someone should build", "opportunity"],
    "R09": ["write about", "blog post", "content", "publish", "audience"],
}

# Also use semantic similarity for edge cases
```

### Unit Tests
- [ ] Classification correctly identifies applicable blocks
- [ ] Parallel dispatch doesn't duplicate work
- [ ] Manifest accurately reflects what was generated

---

## Success Criteria

1. **Depth:** R-block outputs are 3-5x more substantive than current skeleton outputs
2. **Consistency:** Same reflection processed twice yields structurally identical results
3. **Connectedness:** Every reflection has at least 1 connection to prior knowledge (or explicit "novel territory" flag)
4. **Discoverability:** V can query "what have I thought about X" and get relevant reflections with context

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-engineering blocks | Medium | Medium | Start with R04 as pilot, validate depth is useful before scaling |
| Memory queries slow processing | Low | Medium | Cache common queries, use async where possible |
| Too many "not applicable" blocks | Medium | Low | Tune classification thresholds based on real reflections |
| Connection graph becomes noise | Medium | High | Require evidence for each edge, prune weak connections |

---

## Alternatives Considered

### Alternative 1: Single Mega-Block Instead of Multiple R-Blocks
**Rejected because:** Loses the "lens" benefit. A single analysis tends to be shallow across all dimensions vs. deep in specific ones.

### Alternative 2: Pure LLM Classification (No Trigger Words)
**Considered but deferred:** Could improve accuracy but adds latency. Start with trigger words + semantic backup, upgrade if needed.

### Alternative 3: Graph Database for Connections
**Deferred:** JSONL is sufficient for current scale. Can migrate to Neo4j/similar if connection queries become complex.

---

## Handoff

**When plan is approved:**
- Builder executes Phase 1-4 sequentially
- Each phase has a validation checkpoint before proceeding
- R04 (Market) is developed first as the pilot block

**Builder persona:** `set_active_persona("567cc602-060b-4251-91e7-40be591b9bc3")`



