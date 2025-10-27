---
description: 'Command: extract-careerspan-insights'
tags: []
---
# `extract-careerspan-insights`

Extract strategic insights from research results with Careerspan relevance analysis.

## Usage

```bash
# Extract from research file
extract-careerspan-insights --input research-results.txt

# With entity context and output location
extract-careerspan-insights \
  --input sequoia-research.txt \
  --entity "Sequoia Capital" \
  --output Careerspan/Fundraising/sequoia-insights.md

# From knowledge base
extract-careerspan-insights \
  --from-knowledge \
  --entity "Acme Corp"

# Specify analysis focus
extract-careerspan-insights \
  --input research.txt \
  --analysis-type partnership
```

## Description

Post-processes research results to extract strategic insights relevant to Careerspan. Analyzes go-to-market opportunities, fundraising implications, partnership potential, and risks. Generates SWOT analysis and actionable recommendations.

**Use this after:**
1. Running `research-prompt-generator` to create research brief
2. Executing research off-platform (ChatGPT/Claude)
3. Saving research results to file

**Or use with:**
- Existing research pasted from anywhere
- Content already in N5 knowledge base via `--from-knowledge`

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--input` | path | * | Research results file |
| `--from-knowledge` | flag | * | Extract from N5 knowledge base |
| `--entity` | str | recommended | Entity name for context |
| `--output` | path | - | Output file (default: {input}_insights.md) |
| `--analysis-type` | enum | - | Focus area: partnership, investment, customer, general (default) |

*Either `--input` or `--from-knowledge` required

## Analysis Types

### partnership
**Focus:** Partnership evaluation & integration potential

**Key Questions:**
- What value does this partner bring to Careerspan?
- What value does Careerspan bring to them?
- What are integration requirements?
- What are the risks?
- What is timeline to value?

### investment
**Focus:** Investor alignment & fundraising implications

**Key Questions:**
- Does this investor align with our stage/sector?
- What is their track record in our space?
- What value beyond capital do they bring?
- What are potential red flags?
- How should we position Careerspan?

### customer
**Focus:** Customer fit & sales strategy

**Key Questions:**
- Is this a good ICP fit?
- What is their talent/hiring pain point?
- Who are the decision-makers?
- What is the sales cycle?
- What is expansion potential?

### general (default)
**Focus:** Comprehensive strategic assessment

**Key Questions:**
- How does this relate to Careerspan's mission?
- What opportunities does this surface?
- What threats should we monitor?
- What actions should we prioritize?

## What Gets Generated

**Output Structure:**
- **Executive Summary** - 2-3 paragraph narrative + Strategic-Fit Score (1-5)
- **Key Themes & Insights** - Major findings with Careerspan relevance
- **Strategic Relevance** - GTM, fundraising, partnership, product/tech synergies
- **SWOT Analysis** - Strengths, Weaknesses, Opportunities, Threats
- **Patterns & Trends** - Notable patterns with strategic implications
- **Recommended Actions** - Prioritized action items with owners/timelines
- **Strategic Questions** - Socratic questions for deeper exploration
- **Related Knowledge** - Links to N5 knowledge base entries

## Examples

```bash
# Extract insights from research file
extract-careerspan-insights --input sequoia-research.txt

# Partnership evaluation
extract-careerspan-insights \
  --input acme-research.txt \
  --entity "Acme Corp" \
  --analysis-type partnership \
  --output Careerspan/Partnerships/acme-insights.md

# Investor due diligence
extract-careerspan-insights \
  --input vc-research.txt \
  --entity "Sequoia Capital" \
  --analysis-type investment

# Extract from knowledge base
extract-careerspan-insights \
  --from-knowledge \
  --entity "Jane Doe" \
  --analysis-type general
```

## Integration with Knowledge Base

When using `--from-knowledge`:
- Queries `Knowledge/facts.jsonl` for entity mentions
- Retrieves timeline events from `Knowledge/timeline.jsonl`
- Checks opportunities in `N5/lists/opportunities.jsonl`
- Compiles into research text for analysis

Can also be used after `knowledge-ingest`:
```bash
# Step 1: Ingest research into knowledge base
knowledge-ingest --input_text "$(cat research.txt)"

# Step 2: Extract strategic insights
extract-careerspan-insights \
  --from-knowledge \
  --entity "Target Entity"
```

## Related Commands

- `research-prompt-generator` - Generate research briefs
- `knowledge-ingest` - Ingest content into knowledge base
- `direct-knowledge-ingest` - Large document ingestion

## Implementation

**Script:** `N5/scripts/careerspan_insights_extractor.py`

## Notes

- Entity name helps with context but is optional
- Default output location is adjacent to input file
- Analysis type determines strategic focus areas
- SWOT analysis generated automatically
- Cross-references N5 knowledge base when available
- Strategic-Fit Score (1-5) indicates alignment with Careerspan priorities
