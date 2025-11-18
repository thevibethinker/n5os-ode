---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Business Context: Strategic Pivot to Acquisition-Focused Mode

## Financial Runway & Cost Structure

Careerspan is shifting from venture-backed growth mode to a sustainable, low-burn acquisition strategy. The company has:
- **Runway for core team (Vrijen, Ilse, Logan)**: ~6 months at reduced spend
- **Team runway (Danny, Knockel, and others)**: 3 months covered with accelerated vesting if acquisition occurs within one year
- **Cost structure focus**: Keeping burn rate minimal while maintaining token/API infrastructure

The financial model is predicated on staying alive long enough to accrete users and value, then converting to an exit rather than perpetual VC funding.

## Market Validation & Competitive Position

Despite two well-funded competitors (Dax and Jack & Jill) with "shittier tech," Careerspan has significant strengths:
- **Strong product-market fit signals**: Retention and reactivation numbers are "through the roof" compared to competitors
- **Investor consensus**: Multiple VCs confirmed that staying alive and accreting users is the path forward
- **Core product value**: Collects "incredible data on people" with proven ability to identify quality candidates
- **Competitive advantage**: The decentralized talent network concept (single place to drop JDs and be contacted) has resonated extremely well with stakeholders

## Revenue Model Evolution

The company is pivoting away from VC-backable scaling toward multiple monetization streams:
- **Primary (near-term)**: Headhunting/placement fees (bounties for filling roles)
- **Secondary (high-potential)**: VC subscription revenue for access to qualified talent pool
  - Target ICPs: VCs that are fund-raising, need ground-running companies to hire, and have community teams
  - Vrijen is actively cultivating 1-2 VC partnerships for subscription models
- **Tertiary**: Employer portal subscriptions for job distribution and candidate access (currently being built out)

## Operational Constraints & Technical Reality

**API/Compute Limitations** (critical constraint identified by Ilse):
- Current analysis methodology (preferences check → vibe check → full analysis) is prohibitively expensive at scale
- Processing 50 jobs against 2,000 users takes 18-22+ hours due to:
  - Vibe check analysis alone costs $0.30-0.50 per user
  - Rate limits on OpenAI API (~requests per second cap)
  - High failure rates on API calls adding additional time overhead
- Scaling to thousands of users and hundreds of jobs/week is "literally impossible" with current resource model

**Product Philosophy in Tension**:
- Historical commitment: Maintain rigorous, accurate analysis to ensure employer trust (per Rewiring America feedback)
- New constraint: Need to reduce costs/complexity to remain viable for acquisition timeline
- Unresolved: Whether to maintain current rigor standards or pivot to "faster, cheaper, but worse" analysis for screening-level recommendations

## Go-to-Market & Distribution Strategy

Shifting from traditional recruiting/sales approach to community-driven, grassroots distribution:
- **Logan's focus**: Brand building through social media and community embeddedness
- **Technical focus (Ilse)**: Making job distribution cheaper and more scalable; reducing per-candidate processing costs
- **Network leverage**: Hiring managers are identified as peak demographic in existing network; positioning them as distribution channel
- **Pro-candidate posture**: Opening floodgates for candidate visibility to drive organic connections and momentum

**Rationale**: Career tech is a "barren wasteland" precisely because competitors move toward hiring-only or sourcing-adjacent models; Careerspan can leverage flexible pool approach to experiment at low cost while demonstrating metrics attractive to acquirers.

## Stakeholder Alignment Status

- **Vrijen + Logan**: Aligned on acquisition-focused pivot, reduced spend, distribution-heavy approach
- **Ilse**: Supportive in principle but raising critical technical/feasibility concerns about scaling current methodology
- **Pending alignment conversations**: Three-way discussion needed between Vrijen, Logan, and Ilse before presenting plan to Danny and Knockel (other team members)
- **Consideration**: Potential shift from full-time to part-time engagement for Ilse to be discussed

