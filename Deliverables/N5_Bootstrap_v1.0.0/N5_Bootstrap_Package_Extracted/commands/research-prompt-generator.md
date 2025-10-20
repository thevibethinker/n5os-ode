# `research-prompt-generator`

Generate deep research prompts for off-platform execution on ChatGPT/Claude.

## Usage

```bash
# Basic usage
research-prompt-generator --entity "Entity Name" --type {person|company|nonprofit|vc|topic}

# With depth and context
research-prompt-generator \
  --entity "Sequoia Capital" \
  --type vc \
  --depth deep \
  --context "Series A investor evaluation"

# Save to file
research-prompt-generator \
  --entity "Jane Doe" \
  --type person \
  --output research-prompt.xml
```

## Description

Generates comprehensive, structured research prompts that you copy/paste into ChatGPT or Claude for deep research execution. Prompts include [COMPANY] strategic context, entity-specific information requirements, and citation guidelines.

**Workflow:**
1. Generate prompt in N5 (this command)
2. Copy prompt to ChatGPT/Claude (off-platform)
3. Execute research and save results
4. Return to N5 and run `extract-[COMPANY]-insights` on results

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--entity` | str | ✓ | Entity name to research |
| `--type` | enum | ✓ | Entity type: person, company, nonprofit, vc, topic |
| `--depth` | enum | - | Research depth: light, standard (default), deep |
| `--context` | str | - | Custom context/framing for research |
| `--output` | path | - | Save prompt to file (default: clipboard + stdout) |

## Entity Types

### person
Research an individual (executive, expert, contact).

**Information Gathered:**
- Biography & career timeline
- Current role & organization
- Public statements on relevant topics
- Board seats, investments, philanthropy
- Professional network & connections

### company
Research a business entity (B2B/B2C startup or company).

**Information Gathered:**
- Products/services & value proposition
- Go-to-market motion (channels, pricing, ICP)
- Founder bios & team
- Fundraising & investors
- Momentum metrics (ARR, growth, headcount)

### nonprofit
Research NGO, foundation, or nonprofit organization.

**Information Gathered:**
- Mission & programs
- Leadership bios
- Funding sources & major donors
- Partnerships & advocacy focus
- Impact metrics

### vc
Research venture capital firm.

**Information Gathered:**
- Fund sizes & vintage years
- GP/founding partner bios
- Investment theses & thematic focus
- Portfolio highlights (esp. HR-tech/future-of-work)
- Recent deals & cadence
- Co-investor network

### topic
General-purpose research on any subject (NEW).

**Information Gathered:**
- Comprehensive definition & scope
- Historical context & evolution
- Current state of the art
- Key players & thought leaders
- Recent developments & trends
- Relevance to [COMPANY]

## Depth Levels

### light
- **Length:** 500-1000 words
- **Sources:** ≥3 sources
- **Time:** 15-30 minutes
- **Sections:** Executive summary, key facts, [COMPANY] relevance

### standard (default)
- **Length:** 1500-2500 words
- **Sources:** ≥5 sources, ≥2 per key fact
- **Time:** 45-90 minutes
- **Sections:** All standard sections + SWOT

### deep
- **Length:** 3000-5000 words
- **Sources:** ≥10 sources, ≥2 independent per key fact
- **Time:** 2-4 hours
- **Sections:** All sections + competitive analysis + network graph + counter-thesis
- **Requirements:** Confidence tags, cross-referenced facts, assumptions stated

## Examples

```bash
# Research potential partnership contact
research-prompt-generator --entity "Jane Doe" --type person

# Research company for partnership eval
research-prompt-generator \
  --entity "Acme Corp" \
  --type company \
  --context "Evaluating as Q1 2026 partnership"

# Deep research on topic
research-prompt-generator \
  --entity "AI agent orchestration patterns" \
  --type topic \
  --depth deep

# VC investor due diligence
research-prompt-generator \
  --entity "Sequoia Capital" \
  --type vc \
  --depth deep \
  --context "Series A investor evaluation"
```

## Output Format

Generated prompts are XML-structured with:
- Core metadata (persona, audience, tone)
- Research objectives & deliverable structure
- Entity-specific information requirements
- [COMPANY] strategic lens
- Citation requirements & constraints
- Depth-specific modifiers

**Output Methods:**
- ✓ Copied to clipboard
- ✓ Printed to stdout
- ✓ Saved to file (if --output specified)

## Related Commands

- `extract-[COMPANY]-insights` - Process research results
- `knowledge-ingest` - Ingest results into knowledge base
- `meeting-prep-digest` - Automated light research for meetings

## Implementation

**Script:** `N5/scripts/research_prompt_generator.py`

## Notes

- Prompts include [COMPANY] context automatically
- Generated prompts are self-contained (no Zo-specific references)
- Standard depth is appropriate for most use cases
- Deep research is time-intensive; use strategically
