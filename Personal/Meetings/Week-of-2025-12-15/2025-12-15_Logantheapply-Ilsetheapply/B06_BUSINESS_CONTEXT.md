---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
---

# B06 – Business Context

## Company and product

- **Company:** Careerspan – AI-powered career and hiring platform with a strong emphasis on narrative “stories” rather than just resumes.
- **Core product themes in this meeting:**
  - Conversation-driven experiences (user chats, story completion) as the primary surface for value.
  - Employer-facing analytics that show who viewed roles, who applied, and how far they progressed through onboarding.
  - Lightweight configuration of analyses (what gets emphasized in a JD breakdown), but *not* yet a fully configurable API product.

## Data and infrastructure reality

- **Current data model:**
  - Event and entity data is stored in a Firebase-style, non-relational structure (employers, leads, users, stories, etc.).
  - There is no dedicated roll-up warehouse yet for analytics; insights like “how many applicants completed onboarding for Employer X” require multiple cross-collection reads.
- **Implications discussed:**
  - Fully-automatic, always-fresh analytics dashboards across all employers would be expensive in read volume at current scale.
  - Ad-hoc, per-employer reports are manageable, especially when driven by explicit requests and clear filters.
  - Any new endpoints for analytics should be designed with built-in constraints (e.g., employer scoping, clear warnings about cost) rather than open-ended queries.

## Customer and market context

- **Design partners:**
  - Early adopters like David (Skillcraft) are using Careerspan to test precise, skills-based hiring workflows and care about detailed insight into candidate flows.
  - Some design partners are “skills nerds” (very exacting about measurement) and will push for more granularity than the average buyer.
- **Buyer needs signaled here:**
  - Recruiters and hiring managers want clarity on whether jobs are getting seen and whether qualified candidates are moving through the funnel, but they are not yet asking for extremely fine-grained control over the analysis rules themselves.
  - There is appetite for low-friction experiments—paying for help on one or two painful roles—rather than full-scale, long-term contracts.

## GTM and growth strategy

- **Near-term GTM levers:**
  - Ilya’s 1:1 LinkedIn outreach to his recruiter and hiring-manager network, framed as warm intros to V and Logan.
  - December “specials” that lower the threshold for trying Careerspan on a small number of roles or candidates, with emphasis on quality and tangible outcomes.
  - GTM2: a systematic presence in targeted LinkedIn groups where ideal buyers gather, using ghostwritten posts under V’s and Logan’s names.
- **Positioning takeaways:**
  - Careerspan should be framed as a high-touch, founder-led, AI-native partner rather than a generic tool.
  - Metrics and analytics are important, but the *conversation experience* and quality of candidates surfaced remain the primary differentiators.

## Risk and opportunity lenses

- **Risk sensitivity:**
  - The team uses stories about crypto, regulation, and missed bets to think about when to take risk and when to be conservative.
  - In this meeting, that translates into: conservative infra decisions (no runaway analytics costs) paired with more aggressive GTM experimentation (outbound, offers, thought leadership).
- **Opportunities identified:**
  - Turn existing personal networks and alumni connections into early revenue via small, credible pilots.
  - Over time, evolve from ad-hoc spreadsheets toward a more robust analytics substrate as scale and demand justify it.

