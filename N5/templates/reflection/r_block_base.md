# R-Block Base Template

**Version:** 1.0
**Purpose:** Common 7-section structure that ALL reflection blocks (R00-R09 + RIX) inherit

---

## How to Use This Template

1. Copy this template to create a new R-block prompt
2. Replace all `{{PLACEHOLDER}}` markers with block-specific content
3. Fill in each of the 7 sections with domain-specific details
4. Run through the Quality Checklist before finalizing
5. Test with 2-3 real reflections to validate depth and coverage

---

## Block Metadata

**Block ID:** {{BLOCK_ID}}
**Block Name:** {{BLOCK_NAME}}
**Description:** {{SHORT_DESCRIPTION}}

---

## 1. Domain Definition

### What This Lens Sees
{{DOMAIN_DEFINITION}}

<!--
Describe the specific content types this block extracts.
Be precise about the analytical territory this lens covers.
Example: "R04 sees competitive dynamics, market trends, pricing signals, distribution channels..."
-->

### What This Lens Ignores
{{EXCLUSIONS}}

<!--
Explicitly list what falls outside this block's scope.
This prevents overlap with other R-blocks.
Example: "R04 ignores internal product decisions (R05), personal reactions (R01)..."
-->

### Boundary Cases
{{BOUNDARY_CASES}}

<!--
Define how to handle ambiguous content that could belong to multiple blocks.
Provide decision rules for edge cases.
Example: "If market insight drives a product decision, extract the market signal here;
         the product decision belongs in R05."
-->

---

## 2. Extraction Framework

### Trigger Patterns
{{TRIGGER_PATTERNS}}

<!--
List keywords and phrases that indicate this block is relevant.
These are the literal text signals to watch for.
Example: ["competitor", "market share", "pricing", "customer segment", "channel"]
-->

### Semantic Indicators
{{SEMANTIC_INDICATORS}}

<!--
Describe conceptual markers that go beyond keywords.
These help identify content even when explicit trigger words are absent.
Example: "Discussion of external dynamics affecting business positioning"
-->

### Counter-Indicators
{{COUNTER_INDICATORS}}

<!--
Signals that indicate this block is NOT appropriate despite surface-level matches.
Example: "Internal team dynamics that don't reflect market conditions"
-->

---

## 3. Analysis Dimensions

### Primary Dimensions
{{PRIMARY_DIMENSIONS}}

<!--
List 3-5 specific analytical angles for this block type.
Each dimension is a question or framework to apply to the content.
Example for R04:
1. Market Structure Analysis - Who are the players and what's the competitive dynamic?
2. Signal Classification - What type of signal is this? (Trend, Threat, Opportunity)
3. Implication Mapping - What does this mean for our positioning?
-->

### Depth Guidance
{{DEPTH_GUIDANCE}}

<!--
Define the expected level of analysis:
- Surface: Identify and list (not sufficient for R-blocks)
- Standard: Analyze with supporting evidence
- Deep: Root cause analysis with implications and connections
Specify which level is expected and what distinguishes each.
-->

### Quality Bar
{{QUALITY_BAR}}

<!--
What distinguishes a GOOD extraction from a WEAK one?
Provide specific criteria and anti-patterns.
Example:
- GOOD: Each signal has a direct quote as evidence
- WEAK: Generic observations without specific references
-->

---

## 4. Memory Integration

```python
# Memory Query Configuration for {{BLOCK_ID}}

# Profiles to query for context enrichment
profiles_to_query = {{PROFILES_TO_QUERY}}  # e.g., ["knowledge", "positions", "meetings"]

# Semantic search query template
# Use {transcript_key_concepts} as placeholder for extracted concepts
query_template = """{{QUERY_TEMPLATE}}"""

# Example queries this block might run:
# {{EXAMPLE_QUERIES}}
```

### Connection Detection
{{CONNECTION_DETECTION}}

<!--
How should this block detect connections to prior knowledge?
What patterns indicate "this connects to X"?
Example: "If a competitor mentioned in the reflection exists in knowledge base,
         flag for comparison with stored intelligence."
-->

---

## 5. Output Schema

```markdown
## {{BLOCK_ID}}: {{BLOCK_NAME}}

**Generated:** {timestamp}
**Source:** {source_file}
**Confidence:** {overall_confidence}

### {{PRIMARY_SECTION_1}}
{{PRIMARY_CONTENT_1}}

### {{PRIMARY_SECTION_2}}
{{PRIMARY_CONTENT_2}}

### {{OPTIONAL_SECTION}}
{{OPTIONAL_CONTENT}}

---

### Connections Identified
- Links to: {prior_reflections}
- Relates to positions: {position_ids}
- Knowledge base hits: {knowledge_articles}

### Metadata
- Word count: {word_count}
- Extraction confidence: {confidence}
- Applicable blocks also triggered: {sibling_blocks}
```

### Required Fields
{{REQUIRED_FIELDS}}

<!--
List fields that MUST be present in every output.
Mark which can be "N/A" vs which require content.
-->

### Optional Fields
{{OPTIONAL_FIELDS}}

<!--
List fields that appear only when relevant content exists.
-->

---

## 6. Connection Hooks

### Upstream Connections
{{UPSTREAM_CONNECTIONS}}

<!--
What prior content might this reflection extend or refine?
How to detect building-on-prior-ideas patterns?
Example: "Check for mentions of prior decisions, 'as I mentioned before',
         references to past insights."
-->

### Downstream Connections
{{DOWNSTREAM_CONNECTIONS}}

<!--
What future reflections might build on this?
What makes this output referenceable?
Example: "Tag key insights with semantic markers for future retrieval.
         Flag 'open questions' for resolution tracking."
-->

### Cross-Block Connections
{{CROSS_BLOCK_CONNECTIONS}}

<!--
Which other R-blocks might have related extractions from the same transcript?
How should they reference each other?
Example: "If R04 (Market) identifies a competitive threat, check if R05 (Product)
         identified a response. Link if both exist."
-->

---

## 7. Worked Example

### Sample Input Transcript
```
{{SAMPLE_TRANSCRIPT}}
```

### Extraction Process

**What was noticed:**
{{EXTRACTION_OBSERVATIONS}}

**Why it matters:**
{{EXTRACTION_REASONING}}

**Analysis applied:**
{{ANALYSIS_STEPS}}

### Final Formatted Output
```markdown
{{EXAMPLE_OUTPUT}}
```

---

## Quality Checklist

Before finalizing this R-block prompt, verify:

### Structure
- [ ] All 7 sections are present and filled in
- [ ] Placeholder markers have been replaced with specific content
- [ ] Domain definition clearly distinguishes this block from others

### Depth
- [ ] Extraction framework includes specific analytical questions (not just categories)
- [ ] Quality bar defines what "good" looks like with concrete examples
- [ ] Worked example demonstrates expected depth (not surface summaries)

### Integration
- [ ] Memory profiles specified are appropriate for this block
- [ ] Connection hooks describe both directions (upstream/downstream)
- [ ] Output schema includes connection metadata

### Usability
- [ ] Someone unfamiliar with this block could produce correct output from the prompt
- [ ] "Not applicable" criteria are explicit
- [ ] Edge cases and boundary conditions are addressed

---

## Block-Specific Notes

{{ADDITIONAL_NOTES}}

<!--
Any additional context, warnings, or guidance specific to this block.
-->

---

*Template Version: 1.0*
*Last Updated: 2026-01-09*
*Part of: R-Block Framework (r-block-framework)*
