# ZoATS Evaluation System Guide

**Version**: 1.0.0  
**Last Updated**: 2025-10-22  
**Audience**: Founders using ZoATS to evaluate candidates

---

## Overview

The ZoATS Evaluation System provides a comprehensive, evidence-based framework for scoring candidates that is:

- **Transparent**: Every score traces to specific evidence
- **Customizable**: Adapt rubrics to your exact role needs
- **AI-Assisted**: Leverage AI for initial scoring, human for final decisions
- **Fair**: Consistent criteria applied across all candidates
- **Efficient**: Automate 80% of screening, focus founder time on top candidates

---

## System Components

### 1. Rubrics (`file 'schemas/rubric.schema.json'`)

**What**: Job-specific evaluation criteria with weights and scoring scales

**Key Features**:
- Hierarchical structure: Groups → Criteria → Sub-criteria
- Flexible weighting at every level
- Evidence types required for each criterion
- Green flags and red flags for consistency
- Dealbreakers and bonus criteria

**When to Use**: Create one rubric per role before posting job

### 2. Criteria Library (`file 'criteria_library.md'`)

**What**: Reusable bank of common evaluation criteria

**Key Features**:
- 40+ pre-built criteria organized by category
- Ready-to-use evaluation prompts
- Standard green/red flags
- Common evidence types

**When to Use**: Starting point when building new rubrics

### 3. Candidate Records (`file 'schemas/candidate.schema.json'`)

**What**: Complete evaluation record for each applicant

**Key Features**:
- All raw evidence (resume, cover letter, portfolio)
- Extracted structured data (skills, experience)
- Criterion-level scores with supporting evidence
- Timeline of all evaluation events
- Interview recommendations

**When to Use**: Auto-generated for each application received

### 4. Scoring Configuration (`file 'scoring_weights.json'`)

**What**: System-wide defaults and role-specific weight presets

**Key Features**:
- Role presets (Founding Engineer, Designer, PM, etc.)
- Evidence reliability weights
- Normalization and time decay settings
- Threshold definitions

**When to Use**: Set once during system setup, reference when creating rubrics

### 5. Evidence Pipeline (`file 'evidence_pipeline.md'`)

**What**: Process for collecting, validating, and weighting evidence

**Key Features**:
- Multi-source evidence collection (application + external)
- Validation rules (cross-referencing, fact-checking)
- Reliability weighting by source
- Conflict resolution protocol

**When to Use**: Understanding how scores are calculated

---

## Quick Start: Evaluating Your First Role

### Step 1: Create Your Rubric (15-30 min)

1. **Start with a template** from `file 'examples/'`:
   - Founding Engineer → `file 'examples/founding-engineer-rubric.json'`
   - Founding Designer → `file 'examples/founding-designer-rubric.json'`
   - Product Manager → `file 'examples/product-manager-rubric.json'`

2. **Customize for your role**:
   - Adjust weights based on your priorities
   - Add role-specific criteria from `file 'criteria_library.md'`
   - Define dealbreakers (must-haves)
   - Set your thresholds (what score = interview?)

3. **Review with AI**:
   - Ask: "Does this rubric match my job description?"
   - Test on 1-2 sample candidates
   - Refine based on results

### Step 2: Configure Thresholds

Decide your scoring gates:

- **Auto-Reject** (< 45): Clear no, decline automatically
- **Review Required** (45-64): Borderline, founder reviews
- **Strong Candidate** (65-79): Likely interview
- **Auto-Advance** (80+): Definitely interview

*Adjust these based on application volume and role criticality*

### Step 3: Process Applications

For each candidate:

1. **AI Extracts Evidence** (automated):
   - Parses resume, cover letter, portfolio
   - Structures into candidate record
   - Collects external signals (LinkedIn, GitHub, etc.)

2. **AI Scores Each Criterion** (automated):
   - Evaluates against rubric
   - Cites specific evidence
   - Flags uncertainties
   - Notes ultra-signals and red flags

3. **AI Generates Aggregate Score** (automated):
   - Applies weights from rubric
   - Normalizes across candidate pool
   - Categorizes by threshold

4. **Founder Reviews** (selective):
   - High scores (>75): Quick scan → interview decision
   - Borderline (45-64): Deeper review needed
   - Ultra-signals: Flag even if score moderate
   - Red flags: Investigate before proceeding

### Step 4: Make Decisions

**For strong candidates (>75)**:
- Review AI summary and key evidence
- Read ultra-signals section
- Check for any red flags
- Decision time: ~5 min/candidate

**For borderline (45-64)**:
- Review full evidence
- Check criteria where score was low
- Look for hidden strengths AI might have missed
- Trust gut + data
- Decision time: ~10-15 min/candidate

---

## Best Practices

### Creating Effective Rubrics

**DO**:
- ✅ Be specific about what "good" looks like
- ✅ Include 3-5 evaluation prompts per criterion
- ✅ Define clear green flags and red flags
- ✅ Weight heavily what truly matters (don't spread evenly)
- ✅ Include dealbreakers for true requirements
- ✅ Test on 2-3 candidates before full deployment

**DON'T**:
- ❌ Copy rubrics without customization
- ❌ Make all weights equal (defeats the purpose)
- ❌ Include criteria you can't evaluate from application
- ❌ Have more than 15-20 total criteria (overwhelming)
- ❌ Ignore evidence types (how will you score this?)

### Interpreting Scores

**Score Ranges**:
- **90-100**: Exceptional, rare (top 1-2%)
- **80-89**: Strong, likely great fit (top 10%)
- **70-79**: Good, worth interviewing (top 25%)
- **60-69**: Adequate, depends on pool
- **50-59**: Weak, likely pass
- **< 50**: Clear no

**Important**: Absolute scores matter less than **rank order** within your candidate pool. A 72 in a weak pool ≠ 72 in a strong pool.

### Working with AI Scoring

**AI is GOOD at**:
- Consistent application of rubric criteria
- Finding evidence in structured data (resume, LinkedIn)
- Detecting patterns across many candidates
- Flagging obvious strengths and weaknesses
- Saving time on clear no's

**AI is BAD at**:
- Detecting authentic passion vs. performative
- Understanding nuanced industry context
- Evaluating portfolio quality (subjective taste)
- Reading between lines
- Catching sophisticated deception

**Your Role**:
- Set the rubric (what matters)
- Review AI's work, especially borderline cases
- Override when gut disagrees with score
- Make final interview decisions
- Improve rubric based on hiring outcomes

### Avoiding Bias

**System safeguards**:
- Rubrics evaluated blind (no names/demographics in initial scoring)
- Evidence-based requirements (every score justified)
- Consistent criteria across all candidates
- Periodic rubric audits for inadvertent bias

**Your responsibility**:
- Review criteria for bias (education requirements, culture fit language)
- Don't override AI scores based on name/photo
- Apply same standards to all candidates
- Track diversity of who advances vs. doesn't

---

## Advanced Topics

### Normalization

After 5+ candidates, ZoATS can normalize scores to percentile ranks:
- Raw score + rank within pool
- Useful when comparing across application windows
- Auto-adjusts as more candidates apply

Enable in `file 'scoring_weights.json'` → `normalization_config`

### Time Decay

Weight recent experience more than old:
- Default: 24-month half-life
- Relevant for fast-moving fields
- Exempt education and core skills

Configure in `file 'scoring_weights.json'` → `time_decay_config`

### Evidence Validation

ZoATS can cross-check claimed experience:
- LinkedIn cross-reference
- GitHub contribution verification
- Company existence/role validation
- Educational credential checking

Configure in `file 'evidence_pipeline.md'` → Validation section

### Custom Criteria

Add company-specific criteria:

```json
{
  "id": "customer_empathy_saas",
  "name": "B2B SaaS Customer Empathy",
  "weight": 0.15,
  "scale": {"min": 0, "max": 10},
  "description": "Understanding of B2B buyer needs and enterprise sales cycles",
  "evidence_types": ["work_history", "cover_letter"],
  "evaluation_prompts": [
    "Have they sold to or supported enterprise customers?",
    "Do they understand long sales cycles?",
    "Evidence of stakeholder management?",
    "Champion vs. economic buyer awareness?"
  ],
  "green_flags": [
    "Enterprise SaaS experience",
    "Mentions procurement/security reviews",
    "Multi-stakeholder awareness",
    "Patient sales cycle experience"
  ],
  "red_flags": [
    "Only B2C experience",
    "Expects instant decisions",
    "Doesn't understand enterprise buying",
    "Impatient with slow processes"
  ]
}
```

---

## Troubleshooting

### "Scores seem too high/low"

- **Check thresholds**: Your 70 might be others' 60
- **Review weights**: Over-weighting easy-to-score criteria?
- **Examine pool**: Scores relative to applicant quality
- **Calibrate with AI**: Score 3-5 together, compare

### "AI scored someone wrong"

- **Review evidence**: What did AI see that you didn't (or vice versa)?
- **Check rubric clarity**: Are evaluation prompts specific enough?
- **Consider subjectivity**: Is this criterion truly objective?
- **Override and document**: Note why, improves future AI

### "Too many borderline candidates"

- **Tighten dealbreakers**: Add must-haves to auto-filter
- **Adjust weights**: Are you weighting differentiators enough?
- **Raise thresholds**: Move auto-advance bar higher
- **Add bonus criteria**: Reward truly exceptional traits

### "Not enough candidates passing"

- **Lower thresholds**: Your bar might be unrealistic for market
- **Review dealbreakers**: Are they truly essential?
- **Expand criteria**: Too narrow definition of "good"?
- **Check job posting**: Attracting wrong candidates?

---

## Continuous Improvement

### After Each Hire

1. **Retrospective on rubric**:
   - Did scores predict performance?
   - What did we miss in evaluation?
   - What criteria mattered most?

2. **Update rubric**:
   - Adjust weights based on learnings
   - Add new criteria that proved important
   - Remove criteria that didn't differentiate

3. **Document changes**:
   - Track rubric versions
   - Note why changes were made
   - A/B test when possible

### Quarterly Review

- **Calibration check**: Score 5 past candidates together, compare
- **Bias audit**: Who's advancing? Any patterns?
- **Criteria effectiveness**: Which predict success? Which don't?
- **System metrics**: Time saved? Quality of hires?

---

## File Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `file 'schemas/rubric.schema.json'` | Rubric structure | Creating new rubrics |
| `file 'schemas/candidate.schema.json'` | Candidate record format | Understanding evaluations |
| `file 'schemas/scoring_config.schema.json'` | Scoring configuration | System setup |
| `file 'criteria_library.md'` | Reusable criteria | Building rubrics |
| `file 'scoring_weights.json'` | Default weights & presets | Starting point for rubrics |
| `file 'evidence_pipeline.md'` | How evidence is processed | Understanding scoring |
| `file 'examples/founding-engineer-rubric.json'` | Engineer template | Evaluating technical roles |
| `file 'examples/founding-designer-rubric.json'` | Designer template | Evaluating design roles |
| `file 'examples/product-manager-rubric.json'` | PM template | Evaluating PM roles |

---

## Support

**Questions?** 
- Review examples in `file 'examples/'`
- Check troubleshooting section above
- Ask ZoATS: "How do I [specific question]?"

**Found an issue?**
- Document what went wrong
- Include rubric + candidate data
- File issue via Zo support

---

**Version History**:
- v1.0.0 (2025-10-22): Initial evaluation system documentation

**Next Steps**: Start with `file 'examples/'` templates and customize for your role!
