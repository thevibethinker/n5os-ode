---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
provenance: con_iHyzGDF1HGFcgQsu
---

# Block Quality Check Thresholds

Rationale and documentation for quality thresholds in `block_quality_check.py`.
All thresholds chosen with V's approval for sensible defaults.

## Word Count Thresholds

### Rationale
Different block types serve different purposes and audiences, requiring different levels of detail:

- **External-facing blocks** need substantial content for professional sharing
- **Action-oriented blocks** need specificity for accountability and execution  
- **Metadata blocks** need structured information but can be concise
- **Internal blocks** need adequate context for team coordination

### Thresholds by Block Type

#### Detailed Blocks (High Word Count)
| Block | Min Words | Rationale |
|-------|-----------|-----------|
| B01   | 200       | Comprehensive recap for external sharing - must be substantive |
| B28   | 150       | Strategic intelligence requires depth for executive value |
| B08   | 100       | Stakeholder insights need detail for actionable intelligence |

#### Standard Blocks (Moderate Word Count)
| Block | Min Words | Rationale |
|-------|-----------|-----------|
| B02   | 50        | Commitments need specificity for accountability |
| B03   | 50        | Decisions need context and rationale |
| B05   | 50        | Action items need detail for clear execution |
| B06   | 50        | Business context needs depth for relevance |
| B07   | 80        | Warm intros must be personal, not generic templates |
| B10   | 60        | Relationship analysis needs nuance |
| B13   | 60        | Plans need specificity to be actionable |
| B21   | 50        | Key moments need context to be meaningful |
| B33   | 60        | Decision reasoning requires explanatory depth |

#### Metadata Blocks (Basic Word Count)
| Block | Min Words | Rationale |
|-------|-----------|-----------|
| B25   | 30        | Deliverable map - structured list with owners |
| B26   | 30        | Meeting metadata - structured information |

#### Internal Blocks (Team Context)
| Block | Min Words | Rationale |
|-------|-----------|-----------|
| B40   | 40        | Internal decisions need team context |
| B41   | 40        | Coordination needs clear handoff details |
| B42   | 40        | Internal actions need execution clarity |
| B43   | 40        | Resource allocation needs specific details |
| B44   | 40        | Process improvements need actionable detail |
| B45   | 50        | Team dynamics require sensitivity and depth |
| B46   | 40        | Knowledge transfer needs clear information |
| B47   | 50        | Open debates need nuance to capture tensions |
| B48   | 60        | Strategic synthesis needs depth for leadership |

#### Special Cases
| Block | Min Words | Rationale |
|-------|-----------|-----------|
| B32   | 40        | Ideas need development but can be concise |
| B00   | 20        | Simple deferred intents list |
| B02_B05 | 60      | Combined block needs substantial content |
| Default | 30      | Reasonable minimum for any unlisted block |

## Format Compliance Thresholds

### Requirements
- **YAML Frontmatter**: All blocks must have metadata
- **H1 Heading**: Clear structure and organization  
- **Markdown Structure**: Not just plain text - use headers, lists, tables, bold
- **Minimum Sections**: At least 1 organized section

### Passing Score
- Must pass **3 out of 4** format checks (75% threshold)
- Rationale: Allows some flexibility while ensuring basic structure

## Hallucination Detection Thresholds

### AI Marker Detection
**Zero Tolerance** for AI meta-commentary:
- "As an AI...", "I cannot access...", "I don't have access..."
- "I apologize", "Let me clarify", "Based on the information provided"

### Rationale
- These phrases immediately identify AI-generated content
- Breaks immersion and professionalism
- Indicates prompt issues that need fixing

### Impossible Details  
- Future dates beyond 2026 (suspicious for meeting content)
- Overly precise timestamps without source
- Quotes attributed to non-participants

### Meta-Commentary Limit
- Allow up to **2 instances** of process commentary
- Examples: "Generated for meeting...", "Based on analysis..."
- More than 2 suggests over-processing

## Content Accuracy Thresholds

### Sampling Approach
- Check **3 key claims** per block (cost-effective)
- Focus on specific details: decisions, commitments, numbers, dates
- **80% verifiable ratio** required for passing

### Plausibility Checks
- Overly specific timestamps without justification
- Extremely precise numbers that seem fabricated
- Internal contradictions within same block

### Rationale
Full transcript verification would be expensive and slow. Sampling approach catches major hallucinations while keeping costs reasonable.

## Overall Quality Scoring

### Weighted Average
| Component | Weight | Rationale |
|-----------|--------|-----------|
| Length    | 30%    | Adequate detail is fundamental |
| Format    | 25%    | Structure enables usability |
| Hallucination | 25% | Accuracy is critical for trust |
| Content Accuracy | 20% | Verifiability matters but sampling is limited |

### Passing Score: 75%
**Rationale**: High enough to ensure quality, low enough to avoid excessive retries on borderline cases.

## Remediation Flags

### Retry Conditions
- Overall score between **40-75%** (in "warning" range)
- No corruption or encoding issues detected
- **Rationale**: These blocks likely need prompt refinement or regeneration

### HITL (Human-in-Loop) Conditions  
- Overall score **< 40%** (very low confidence)
- Hallucination markers detected
- File corruption or encoding issues
- **Rationale**: These require human judgment or system fixes

### Low Confidence Threshold: 60%
- Blocks scoring below 60% flagged for attention
- **Rationale**: Early warning system before blocks fail entirely

## Configuration

### Environment Variables
- `QUALITY_CHECKS_ENABLED`: Enable/disable validation (default: true)
- `QUALITY_PASSING_SCORE`: Override passing threshold (default: 0.75)
- `QUALITY_RETRY_THRESHOLD`: Override retry threshold (default: 0.40)
- `QUALITY_HITL_THRESHOLD`: Override HITL threshold (default: 0.40)

### Customization
All thresholds are configurable in the `QUALITY_THRESHOLDS` dictionary at the top of `block_quality_check.py`. This allows per-deployment tuning without code changes.

## Monitoring and Tuning

### Expected Pass Rates
- **Overall**: 85-90% of blocks should pass on first generation
- **Retry Success**: 70-80% of flagged blocks should pass after regeneration  
- **HITL Rate**: Should be < 5% of all blocks

### Adjustment Triggers
If pass rates consistently fall outside these ranges:

1. **Low Pass Rate (< 80%)**: Consider lowering thresholds or improving prompts
2. **High Pass Rate (> 95%)**: Consider raising thresholds for better quality
3. **High HITL Rate (> 10%)**: Check for systematic prompt or generation issues

### Quality Metrics
The system tracks:
- Pass rates by block type
- Common failure patterns  
- Retry effectiveness
- Time-to-pass distributions

These metrics inform threshold adjustments and prompt improvements over time.

## Block Type Specific Notes

### B01 (Detailed Recap)
- Highest threshold (200 words) because it's often shared externally
- Must be comprehensive enough to stand alone as meeting summary

### B07 (Warm Introductions)
- Higher threshold (80 words) because generic intros are worse than no intros
- Needs personalization and context to be valuable

### B28 (Strategic Intelligence)  
- High threshold (150 words) for executive consumption
- Requires depth and analysis, not just facts

### B45 (Team Dynamics)
- Higher threshold (50 words) because interpersonal notes need nuance
- Superficial treatment can be counterproductive

### Internal Blocks (B40-B48)
- Moderate thresholds reflecting team context needs
- Balance between comprehensive and practical

## Implementation Notes

### Performance
- Quality check runs in ~2-5 seconds per block
- Parallel processing for multiple blocks
- Designed for real-time validation during generation

### Dependencies
- No external API calls (cost and latency considerations)
- Pure Python text processing
- Works offline/in restricted environments

### Future Enhancements
- Semantic similarity checking against transcript (when cost-effective)
- Block-to-block consistency validation
- Domain-specific quality rules by meeting type
- Machine learning-based quality scoring

This threshold system provides a balanced approach to quality assurance: strict enough to catch real issues, flexible enough to avoid excessive false positives, and transparent enough for ongoing tuning and improvement.