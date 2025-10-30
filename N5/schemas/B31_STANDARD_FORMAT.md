# B31 Standard Format (v2.0)

**Effective Date**: 2025-10-30  
**Purpose**: Ensure all future B31 files can be reliably extracted into GTM Intelligence Database

---

## Template Structure

```markdown
# B31: Stakeholder Research

**Meeting Date**: YYYY-MM-DD  
**Stakeholder**: [Full Name] - [Role/Company]  
**Research Focus**: [One-line description of what intelligence was gathered]

---

## Insight 1: [Concise Title]

**Category**: [Pick ONE from category list below]  
**Signal Strength**: ●●●●○ [1-5 bullets filled]

**What We Learned**:
[1-2 paragraphs describing the insight. What is the core finding?]

**Evidence**:
[Direct quotes from transcript, or specific observations that support this insight]

**Business Implications**:
[Why this matters for Careerspan. What decisions does this inform? What actions should we take?]

**Confidence Level**: [HIGH / MEDIUM / LOW] - [One sentence justification]

---

[Repeat for Insight 2, 3, etc.]
```

---

## Standard Categories (Use Exactly)

- **Market Pain Point** - Customer problems/frustrations
- **GTM Strategy** - Go-to-market approaches, channels, positioning
- **Product Strategy** - What to build, product roadmap insights
- **Competitive Landscape** - Competitor intel, differentiation
- **Pricing & Business Model** - How to charge, rev models
- **Partnership Strategy** - Who to partner with, how
- **Market Dynamics** - Trends, shifts, macro forces
- **Fundraising** - Investor perspectives, funding strategies
- **Hiring & Talent** - Recruiting, team building insights
- **Customer Segmentation** - Who to target, persona insights

---

## Signal Strength Scale

- **●●●●●** (5/5) - Validated with data/evidence across multiple sources
- **●●●●○** (4/5) - Strong evidence, confirmed by stakeholder's direct experience
- **●●●○○** (3/5) - Credible observation, limited validation
- **●●○○○** (2/5) - Hypothesis or early signal, needs validation
- **●○○○○** (1/5) - Speculative, contradicts other signals

---

## Confidence Level Guidelines

- **HIGH** - Stakeholder has direct, firsthand experience with this insight
- **MEDIUM** - Stakeholder observed this pattern secondhand, or has partial experience
- **LOW** - Stakeholder is speculating or relaying hearsay

---

## Example (Full)

```markdown
# B31: Stakeholder Research

**Meeting Date**: 2025-10-29  
**Stakeholder**: Jeff Sipe - Recruiting Industry Veteran  
**Research Focus**: Recruiting Agency Market Dynamics & Partnership Validation

---

## Insight 1: Recruiting Agencies Desperate for Sourcing Solutions

**Category**: Market Pain Point  
**Signal Strength**: ●●●●○

**What We Learned**:
Recruiting agencies are "out of ideas for how to get to talent." Traditional sourcing channels (LinkedIn, job boards) have collapsed in effectiveness due to saturation. Inbound applicant quality is "terrible." Agencies are actively seeking new infrastructure for candidate sourcing, creating immediate market opening for Careerspan's agency channel.

**Evidence**:
- Jeff's direct observation: "Recruiting agencies are out of ideas for how to get to talent"
- LinkedIn and job boards "don't work anymore" for quality sourcing
- Agencies expressing interest: Superposition, LaunchSam, Matchbox
- Jeff identified Careerspan as solution 2 years ago

**Business Implications**:
Recruiting agencies represent a "desperate" market segment actively seeking solutions. This validates agency channel as high-priority GTM strategy. Jeff's network provides immediate access to decision-makers. Timing is optimal - agencies know current tools are failing and are open to new approaches.

**Confidence Level**: HIGH - Jeff has direct daily exposure to recruiting agency pain points through his extensive network. Multiple agencies already expressing interest validates this isn't isolated observation.

---

## Insight 2: "Refined Gold Not Ore" Value Proposition

[... continue with same structure ...]
```

---

## Implementation

1. **All new B31 files MUST follow this format**
2. **Meeting processing scripts updated to generate this format**
3. **Database extraction script expects this format**
4. **Legacy B31 files extracted via forgiving one-time backfill (already complete)**

---

**Last Updated**: 2025-10-30  
**Version**: 2.0 (append-only database architecture)
