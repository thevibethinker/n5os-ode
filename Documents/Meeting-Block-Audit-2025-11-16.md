---
created: 2025-11-16
last_edited: 2025-11-17
version: 1.1
---
# Meeting Intelligence Block System Audit
**Generated:** 2025-11-16 13:32 EST  
**Purpose:** Comprehensive audit of block manifest, generation prompts, and optimization opportunities

---

## Executive Summary

Your meeting intelligence system currently has **21 canonical blocks** defined across three registries:
- **Meeting blocks (B01-B31):** 21 blocks in active use
- **Reflection blocks (B50-B99):** 11 specialized blocks for voice reflections
- **Total system:** 32 distinct block types

**Key Files:**
- Primary registry: `file 'N5/prefs/block_type_registry.json'` (meeting blocks)
- Canonical definitions: `file 'N5/config/canonical_blocks.yaml'` (standardized schema)
- Reflection registry: `file 'N5/prefs/reflection_block_registry.json'` (B50-B99)
- Generation system: `file 'Prompts/meeting-block-generator.prompt.md'`
- Selection system: `file 'Prompts/meeting-block-selector.prompt.md'`

---

## Complete Block Inventory (B01-B31)

### Tier 1: REQUIRED (Always Generated)
**5 blocks** - Generated for every meeting, form the core intelligence layer

| Block | Name | Purpose | Typical Length | Notes |
|-------|------|---------|----------------|-------|
| **B01** | DETAILED_RECAP | Comprehensive meeting overview with strategic depth | 800-2000 words | Decision summary + strategic context + critical next actions |
| **B02** | COMMITMENTS_CONTEXTUAL | Action items with accountability and dependencies | 200-500 words | Table format with owner/deliverable/context/due date/dependencies |
| **B21** | KEY_MOMENTS | Memorable quotes + strategic questions (merged B29+B21) | 200-500 words | Two sections: Quotes with context + Salient questions |
| **B25** | DELIVERABLE_CONTENT_MAP | Deliverables table + follow-up email draft | 300-700 words | REQUIRED for communications pipeline - maps deliverables and flags email needs |
| **B26** | MEETING_METADATA_SUMMARY | Classification, tags, and system metadata | 100-200 words | Quick-reference for filing, email generation, N5OS tag harmonization |

### Tier 2: HIGH PRIORITY (Stakeholder-Dependent)
**5 blocks** - Generated based on meeting type and stakeholder classification

| Block | Name | Purpose | When Generated | Typical Length |
|-------|------|---------|----------------|----------------|
| **B05** | OUTSTANDING_QUESTIONS | Unresolved items with blocker identification | Any meeting with open loops | 200-400 words |
| **B07** | WARM_INTRO_BIDIRECTIONAL | Facilitate connections in either direction | Intro promised or discussed | 150-300 words |
| **B08** | STAKEHOLDER_INTELLIGENCE | Unified stakeholder profile + resonance + CRM + domain authority + Howie tags | Every meeting (REQUIRED) | 400-1000 words |
| **B13** | PLAN_OF_ACTION | Phased execution roadmap with momentum analysis | Complex initiatives/partnerships | 400-700 words |
| **B27** | KEY_MESSAGING | Strategic messaging & talking points | Founder/investor/partnership meetings | 300-600 words |

**Note:** B08 was elevated to REQUIRED status - generates comprehensive stakeholder intelligence including CRM integration, domain authority tracking, and Howie scheduling tags.

### Tier 3: CONDITIONAL (Content-Triggered)
**8 blocks** - Generated only when specific content patterns detected

| Block | Name | Purpose | Trigger | Typical Length |
|-------|------|---------|---------|----------------|
| **B06** | PILOT_INTELLIGENCE | Pilot details with confidence scoring | Pilot explicitly discussed | 200-400 words |
| **B11** | METRICS_SNAPSHOT | All numbers discussed | 3+ substantive metrics mentioned | 200-400 words |
| **B14** | BLURBS_REQUESTED | Actual blurbs explicitly requested | Intro promised by other party | 150-300 words |
| **B15** | STAKEHOLDER_MAP | Who's who in complex situations | Multiple stakeholders/complex dynamics | 300-500 words |
| **B24** | PRODUCT_IDEA_EXTRACTION | Feature/product ideas with confidence | Product/ideation discussions | 200-500 words |

| **B31** | STAKEHOLDER_RESEARCH | Essential landscape insights with signal strength | Every meeting (REQUIRED) | 300-600 words |

**Note:** B25 and B31 were both elevated to REQUIRED - B25 for follow-up execution, B31 for intelligence gathering.

### Tier 4: ADDITIONAL BLOCKS (From canonical_blocks.yaml)
**4 blocks** - Additional standardized blocks in the system

| Block | Name | Purpose | Notes |
|-------|------|---------|-------|
| **B03** | DECISIONS_MADE (or STAKEHOLDER_INTEL) | Decisions with rationale | Naming conflict with B08 |
| **B04** | OPEN_QUESTIONS (or RISKS_AND_FLAGS) | Questions requiring follow-up | Multiple variants exist |
| **B09** | REFERENCE_DATA | Key dates, metrics, contacts | Optional |
| **B10** | CONTEXT_CONNECTIONS (or RISK_REGISTER) | Cross-references to knowledge base | Optional |

---

## Block Generation System Architecture

### Two-Phase Workflow

**Phase 1: Selection (meeting-block-selector.prompt.md)**
- Scans Inbox for raw meetings (no suffix, no manifest)
- Analyzes transcript semantically
- Selects 6-10 blocks dynamically based on:
  - Core blocks (always)
  - Conditional blocks (trigger patterns)
  - 1-2 wildcards (AI-recommended)
- Generates `manifest.json` with block list
- Renames folder: `[no suffix]` → `[M]` (manifest ready)

**Phase 2: Generation (meeting-block-generator.prompt.md)**
- Finds meetings with status `[M]` and pending blocks
- Generates ONE block per execution with full context:
  - Complete transcript
  - All previously generated blocks
  - Block definition from registry
- Validates block quality
- Updates manifest status
- When all complete: renames `[M]` → `[P]` (placement ready)

### Key Design Principles
1. **One Block, One Turn:** Each block gets dedicated LLM focus
2. **Full Context Always:** Complete transcript + prior blocks provided
3. **Canonical Naming:** Names pulled from registry (no drift)
4. **Idempotent:** Check file existence before generation
5. **Resumable:** Parse manifest to continue from last successful block

---

## Prompt Optimization Opportunities

### 1. Guidance Clarity Issues

**B01 DETAILED_RECAP:**
- ✅ Clear structure (Key Decisions + Strategic Context + Critical Next Action)
- ⚠️ Balancing "conciseness with depth" is vague
- **Recommendation:** Add word count targets per section

**B02 COMMITMENTS_CONTEXTUAL:**
- ✅ Clear table format and owner classification
- ⚠️ "Context/Why column should explain strategic importance" - needs examples
- **Recommendation:** Show 2-3 example rows in guidance

**B08 STAKEHOLDER_INTELLIGENCE:**
- ⚠️ **MOST COMPLEX BLOCK** - 5 sections, multiple integration points
- ⚠️ Guidance is 60+ lines - risk of selective attention
- ⚠️ CRM/Howie/Domain Authority sections may compete for focus
- **Recommendation:** Consider splitting into 2 blocks:
  - B08a: Foundational Profile + Resonance
  - B08b: CRM Integration + Domain Authority

**B13 PLAN_OF_ACTION:**
- ✅ Clear phased structure
- ⚠️ Momentum section absorbed from deleted B16 - may feel tacked on
- **Recommendation:** Make Momentum its own top-level section with clear triggers

**B21 KEY_MOMENTS:**
- ✅ Clean merge of B29 (quotes) + B21 (questions)
- ✅ Two-section structure is intuitive
- **Recommendation:** Add examples of "why it matters" context analysis

**B25 DELIVERABLE_CONTENT_MAP:**
- ⚠️ Dual-purpose block (table + email draft)
- ⚠️ Email generation has 12 complex rules (Flesch-Kincaid, warmth scoring, etc.)
- **Recommendation:** Reference external email-generation system instead of embedding all rules

**B31 STAKEHOLDER_RESEARCH:**
- ✅ Clear signal strength rating system (1-5 dots)
- ⚠️ Source credibility section is complex (PRIMARY/SECONDARY/SPECULATIVE)
- ⚠️ Requires updating B08 after generation (circular dependency)
- **Recommendation:** Simplify credibility assessment or make it optional

### 2. Structural Issues

**Naming Conflicts:**
- B03 appears twice: DECISIONS_MADE vs STAKEHOLDER_INTEL
- B04 appears twice: OPEN_QUESTIONS vs RISKS_AND_FLAGS
- B05 appears twice: OUTSTANDING_QUESTIONS vs ACTION_ITEMS (canonical is B05_ACTION_ITEMS, but also conflicted)
- **Recommendation:** Audit and consolidate using `consolidation_map` in canonical_blocks.yaml

**Priority Confusion:**
- Registry says B08 is REQUIRED
- Registry says B25 is REQUIRED
- Registry says B31 is REQUIRED
- But selector prompt treats them as conditional
- **Recommendation:** Sync priority levels between systems

**Missing Guidance:**
- B06 (PILOT_INTELLIGENCE): Good structure but no examples
- B11 (METRICS_SNAPSHOT): Very simple guidance, could use more detail on what counts as "substantive"
- B15 (STAKEHOLDER_MAP): Missing example of "power dynamics" analysis

### 3. Generation System Issues

**Token Efficiency:**
- Full transcript loaded for every block (could be 5000+ tokens)
- All prior blocks loaded (cumulative, could be 10K+ tokens by block 7)
- **Impact:** Expensive for meetings with 8-10 blocks
- **Recommendation:** Consider compression for transcript context after block 3

**Validation Gaps:**
- Validator checks file name, frontmatter, feedback checkbox, length
- Does NOT validate content quality or adherence to structure
- **Recommendation:** Add structure validation (e.g., B02 must have table)

**Error Recovery:**
- If generation fails: delete block, don't update manifest, allow retry
- No limit on retry attempts
- **Recommendation:** Add retry counter, escalate after 3 failures

---

## Registry Comparison Analysis

### block_type_registry.json (Primary)
- **21 blocks** defined (B01-B31, not sequential)
- Includes detailed guidance arrays
- Has stakeholder combinations (INVESTOR, FOUNDER, NETWORKING, CUSTOMER)
- Version 1.6
- Includes reflection_blocks_registry reference

### canonical_blocks.yaml (Standardized Schema)
- **21 blocks** defined with YAML structure
- Organized by category: core, contextual, optional
- Includes selection rules by meeting type
- Has consolidation_map for legacy names
- More structured but less detailed guidance

### Recommendation: Unify Registries
- Keep JSON as source of truth for guidance
- Use YAML for selection logic and categorization
- Create sync script to ensure consistency

---

## Reflection Blocks (B50-B99)

**11 specialized blocks** for voice reflection processing:
- Separate registry: `file 'N5/prefs/reflection_block_registry.json'`
- Style guides: `file 'N5/prefs/communication/style-guides/reflections/'`
- Not covered in meeting block system
- Out of scope for this audit (focused on meeting blocks)

---

## Optimization Roadmap

### Phase 1: Quick Wins (1-2 hours)
1. ✅ Create this audit document
2. Add examples to B02, B06, B15 guidance
3. Fix naming conflicts (B03, B04, B05)
4. Sync priority levels between registries
5. Add retry limits to generator

### Phase 2: Medium Effort (3-5 hours)
1. Split B08 into two blocks (if testing confirms complexity issue)
2. Add structure validation to output validator
3. Create registry sync script
4. Compress transcript context after block 3
5. Extract email generation rules from B25 into separate system

### Phase 3: Strategic (1-2 days)
1. User testing: Which blocks are most/least valuable?
2. Quality sampling: Audit 20-30 generated blocks for adherence
3. Token cost analysis: Measure actual cost per meeting
4. Feedback system: Analyze checkbox usage patterns
5. Consider dynamic block selection based on feedback data

---

## How to Study and Optimize Prompts

### Recommended Workflow

**Step 1: Read Registry with Block Context**
```bash
# View full guidance for specific block
jq '.blocks.B08' /home/workspace/N5/prefs/block_type_registry.json
```

**Step 2: Find Real Examples**
```bash
# Find all B08 files in processed meetings
find /home/workspace/Personal/Meetings -name "B08_*.md" | head -5
```

**Step 3: Compare Guidance vs Output**
- Open registry guidance side-by-side with real output
- Check: Are all sections present? Is structure followed? Is length appropriate?

**Step 4: Identify Patterns**
- What's consistently missing?
- What's consistently excellent?
- Where does AI deviate from guidance?

**Step 5: Refine Guidance**
- Add examples for ambiguous instructions
- Simplify overly complex blocks
- Strengthen weak areas with explicit requirements

### Testing Approach
1. Select 3 blocks to optimize (suggest B08, B25, B31 - most complex)
2. Generate 5 test meetings with current prompts
3. Rate outputs 1-5 on: Structure adherence, Content quality, Length appropriateness
4. Modify prompts
5. Generate same 5 meetings with new prompts
6. Compare scores

---

## Next Steps

**Immediate Actions:**
1. Review this audit and prioritize optimization targets
2. Decide: Split B08 or simplify guidance?
3. Fix naming conflicts in registries
4. Test 3-5 meetings end-to-end with current system

**Questions for You:**
- Which blocks do you use most frequently?
- Which blocks are least valuable to you?
- Are there any missing blocks you wish existed?
- What's your tolerance for token cost vs comprehensiveness?

---

**This is conversation con_MMUy9beXziOyCQC5**

*Generated: 2025-11-16 13:32 EST*



