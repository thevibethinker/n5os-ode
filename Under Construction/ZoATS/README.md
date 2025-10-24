# ZoATS Evaluation System

**Version**: 1.0.0  
**Created**: 2025-10-22  
**Status**: ✅ Complete Core System

---

## What's Here

This directory contains the complete candidate evaluation system for ZoATS, including rubric schemas, scoring configuration, criteria library, and example templates.

### Quick Start

1. **Read the guide**: Start with `file 'docs/evaluation-system-guide.md'`
2. **Pick a template**: Browse `file 'examples/'` for your role type
3. **Customize rubric**: Adapt template using `file 'criteria_library.md'`
4. **Configure scoring**: Review `file 'scoring_weights.json'` for defaults
5. **Understand evidence**: Read `file 'evidence_pipeline.md'` to see how scoring works

---

## Directory Structure

```
ZoATS/
├── schemas/                          # JSON schemas defining data structures
│   ├── rubric.schema.json           # Job-specific evaluation rubric
│   ├── candidate.schema.json        # Candidate evaluation record
│   └── scoring_config.schema.json   # Scoring configuration
├── examples/                         # Complete rubric templates
│   ├── founding-engineer-rubric.json
│   ├── founding-designer-rubric.json
│   └── product-manager-rubric.json
├── docs/                            # Documentation
│   └── evaluation-system-guide.md   # Complete usage guide
├── criteria_library.md              # Reusable evaluation criteria (40+ criteria)
├── scoring_weights.json             # Default weights & role presets
├── evidence_pipeline.md             # How evidence is collected & validated
└── README.md                        # This file
```

---

## Core Concepts

### Rubrics
Job-specific evaluation frameworks that define:
- What criteria matter for this role
- How much each criterion weighs
- What evidence is needed to score it
- Thresholds for pass/interview/reject

### Criteria
Individual evaluation dimensions like "Technical Skills" or "Culture Fit":
- Have clear definitions
- Include evaluation prompts for consistency
- List green flags (good signs) and red flags (warning signs)
- Specify what evidence types validate them

### Evidence
Concrete data supporting scores:
- Application materials (resume, cover letter, portfolio)
- External signals (LinkedIn, GitHub, references)
- Validated facts vs. unverified claims
- Weighted by source reliability

### Scoring
Multi-step process:
1. AI extracts evidence from application
2. AI scores each criterion against rubric
3. Scores aggregated using weights
4. Normalized within candidate pool
5. Categorized by thresholds
6. Founder reviews and decides

---

## Example Templates

### Founding Engineer (`file 'examples/founding-engineer-rubric.json'`)
**Focus**: Technical depth + early-stage fit + ownership  
**Key Criteria**: Architecture skills, 0-1 experience, self-direction, authenticity  
**Weights**: 35% technical, 30% early-stage fit, 20% soft skills, 15% culture

### Founding Designer (`file 'examples/founding-designer-rubric.json'`)
**Focus**: Design craft + product thinking + versatility  
**Key Criteria**: Portfolio quality, product strategy, speed & iteration, collaboration  
**Weights**: 40% design skills, 25% early-stage fit, 20% collaboration, 15% culture

### Product Manager (`file 'examples/product-manager-rubric.json'`)
**Focus**: Execution + technical PM + stakeholder management  
**Key Criteria**: Shipping track record, data-driven decisions, communication, business acumen  
**Weights**: 35% PM skills, 20% technical ability, 25% leadership, 10% business, 10% culture

*All templates are starting points - customize weights and criteria for your specific role.*

---

## Criteria Library Highlights

40+ pre-built criteria organized by category:

**Technical Skill**: Coding ability, architecture, debugging, system design  
**Soft Skills**: Communication, collaboration, ownership, adaptability  
**Experience**: 0-1 experience, domain expertise, startup experience, execution track record  
**Culture Fit**: Mission alignment, values match, company stage fit, working style  
**Authenticity**: AI detection, genuine interest, unique perspective, signal vs. noise

Each criterion includes:
- Clear definition and evaluation prompts
- Evidence types needed
- Green flags and red flags
- Typical weights for different role types

---

## Key Features

### Evidence-Based Scoring
Every score traces to specific evidence with source citations. No black-box decisions.

### Flexible Weighting
Customize at every level: criterion groups, individual criteria, evidence types. Match your actual priorities.

### AI-Assisted + Human-Reviewed
AI handles 80% of grunt work (parsing, initial scoring, pattern detection). Founder focuses on borderline cases and final decisions.

### Bias Mitigation
Blind initial scoring, consistent criteria, evidence requirements, and audit tools reduce unconscious bias.

### Continuous Learning
Track rubric effectiveness, update based on hiring outcomes, improve over time.

---

## Getting Started

### For Your First Role

1. **Choose template** matching your role type from `file 'examples/'`
2. **Read the guide** in `file 'docs/evaluation-system-guide.md'`
3. **Customize rubric**:
   - Adjust weights based on your priorities
   - Add role-specific criteria from `file 'criteria_library.md'`
   - Define your dealbreakers
   - Set thresholds (what score = interview?)
4. **Test with 2-3 candidates** before full deployment
5. **Refine based on results**

### For Additional Roles

1. **Start with closest template** or build from `file 'criteria_library.md'`
2. **Copy and adapt** relevant criteria
3. **Adjust weights** for this role's priorities
4. **Define role-specific thresholds**
5. **Document your reasoning** (helps future rubric updates)

---

## Implementation Checklist

- [x] Rubric schema defined (`file 'schemas/rubric.schema.json'`)
- [x] Candidate record schema defined (`file 'schemas/candidate.schema.json'`)
- [x] Scoring configuration schema defined (`file 'schemas/scoring_config.schema.json'`)
- [x] Comprehensive criteria library created (40+ criteria)
- [x] Default scoring weights and role presets configured
- [x] Evidence collection and validation pipeline designed
- [x] Three complete example rubrics (Engineer, Designer, PM)
- [x] Complete evaluation system guide written
- [ ] Scoring engine implementation (code)
- [ ] Evidence extraction pipeline (code)
- [ ] External signal integration (LinkedIn, GitHub APIs)
- [ ] UI for rubric creation and candidate review
- [ ] Reporting and analytics dashboard

---

## Design Principles

From `file 'Documents/Archive/2025-10-22-ZoATS-Planning/ats-in-a-box-principles.md'`:

1. **Founder-First**: Built for non-technical founders hiring their first 5 employees
2. **Evidence-Based**: Every decision traceable to specific evidence
3. **AI-Assisted, Human-Decided**: AI does grunt work, human makes final call
4. **Authentic Signal Detection**: Surface genuine passion/fit, filter AI slop
5. **Modular & Extensible**: Start simple, expand as needed
6. **Portable**: Easy export, no lock-in, data ownership

---

## Next Steps

**Ready to evaluate candidates?**
→ Start with `file 'docs/evaluation-system-guide.md'`

**Want to understand the system deeply?**
→ Read `file 'evidence_pipeline.md'` and review schemas in `file 'schemas/'`

**Building your first rubric?**
→ Open an example from `file 'examples/'` and customize using `file 'criteria_library.md'`

**Questions or issues?**
→ Review troubleshooting section in guide or ask ZoATS

---

**Version History**:
- v1.0.0 (2025-10-22): Initial evaluation system release

**Related Work**:
- Parent conversation: con_E5iuQnmFOeZcOUDX (ZoATS Planning & Architecture)
- Worker thread: con_CpwiV2McHv7SLCka (Evaluation System Development)
- Principles doc: `file 'Documents/Archive/2025-10-22-ZoATS-Planning/ats-in-a-box-principles.md'`
