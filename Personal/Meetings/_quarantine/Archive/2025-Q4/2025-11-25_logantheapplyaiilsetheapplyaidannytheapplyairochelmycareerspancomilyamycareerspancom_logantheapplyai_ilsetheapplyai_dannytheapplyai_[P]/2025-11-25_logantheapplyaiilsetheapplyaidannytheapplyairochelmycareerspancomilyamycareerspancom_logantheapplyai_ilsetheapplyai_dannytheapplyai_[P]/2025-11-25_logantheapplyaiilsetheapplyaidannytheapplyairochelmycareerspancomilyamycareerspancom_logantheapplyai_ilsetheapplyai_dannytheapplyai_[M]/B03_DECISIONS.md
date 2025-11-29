---
created: 2025-11-25
last_edited: 2025-11-25
version: 1.0
---

# B03 – Decisions

## 1. Channel ownership for employer–candidate follow‑ups
- **Decision**: Careerspan should own and operate the key email flows to candidates and employers, using SendGrid rather than pushing this entirely onto employers or passive systems.
- **Rationale**:
  - Email scales whereas ad‑hoc "scanning" and manual processes do not; costs can be predicted and optimized.
  - Owning the channel enables fine‑grained tracking of unsubscribes and engagement by email type.

## 2. Near‑term implementation philosophy
- **Decision**: Treat the immediate problem as a simple trigger→email pipeline ("when this happens, send the right emails to the right people") instead of over‑investing in agent orchestration right now.
- **Rationale**:
  - There is a straightforward, high‑value path that can be shipped quickly.
  - More elaborate agent‑based systems can be revisited once the basic flow is working and producing data.

## 3. Demo strategy and expectations
- **Decision**: Continue pursuing demos as a primary motion, with an implicit target of ~10 demos every ~two weeks and a working benchmark of converting roughly a third into ongoing revenue.
- **Rationale**:
  - Recent demo performance has already moved counterparties to integration‑level discussions, validating the pitch.
  - A simple volumetric model (demos × conversion) gives the team a concrete way to think about growth.

## 4. Candidate time‑commitment framing
- **Decision**: Adopt the narrative that spending more time with Careerspan is an *advantage* for candidates, not a tax, and embed this in dedicated candidate‑facing landing page(s).
- **Rationale**:
  - The product asks for meaningful time investment; this must be proactively framed and justified.
  - Ilya’s modular deck of headlines, sub‑headlines, and copy will be the basis for this messaging.

## 5. Ad creative direction
- **Decision**: Treat multiple ad concepts as testable themes, with particular enthusiasm for the pre‑Christmas "open this gift early" concept refined by Logan.
- **Rationale**:
  - The gift‑themed creative is simple, visually clean, and likely to cut across demographics.
  - Running several concepts in parallel will provide signal on what resonates without locking the team into a single narrative.

## 6. Funnel integrity and CTAs
- **Decision**: Fix mis‑wired CTAs where "Schedule 30‑minute demo" routes to the job board; ensure that employer‑facing CTAs lead to appropriate destinations (e.g., Calendly, forms).
- **Rationale**:
  - Current behavior leaks intent and undermines the value of ads and landing pages.
  - The team plans explicit end‑to‑end testing of the funnel before or during any holiday campaign.

## 7. Scoring and transferability – directional decisions
- **Decision (directional, not yet scheduled)**:
  - Long‑term, vibe checks and the full analysis will need a more nuanced architecture that separates global scoring semantics from per‑job interpretation (e.g., tighter tolerances for product roles, looser for certain tools or contexts).
- **Rationale**:
  - Current linearish scales show cracks, especially once candidates accumulate many stories.
  - Overly generous transferability can mislead employers and undercut trust in the system.

## 8. Holiday experiment posture
- **Decision**: Explore a constrained Black Friday / Cyber Monday campaign with strict spend guardrails, contingent on having the basic funnel wired up.
- **Rationale**:
  - Device usage and attention will be high; a low‑risk test could yield useful signal.
  - Guardrails ensure that, in the worst case, the team pays very little while validating infrastructure and messaging.

