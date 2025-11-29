---
created: 2025-11-25
last_edited: 2025-11-25
version: 1.0
---

# B05 – Action Items

## Summary
Concrete follow‑ups inferred from the discussion. Owners and timelines are indicative; confirm and adjust in subsequent stand‑ups.

## Owner: Vrijen (V)
- **V‑1 – Own outbound employer/candidate email via SendGrid**
  - Coordinate setup or refinement of SendGrid‑based campaigns for key triggers (e.g., employer pass events, candidate status updates).
  - Ensure unsubscribe tracking and list hygiene are correctly configured for these flows.
- **V‑2 – Demo quality and volume**
  - Prepare with Ilse for the upcoming demo: smoother transitions, tighter time‑boxing, and clear hand‑offs in the script.
  - Work toward a steady cadence of ~10 demos every ~two weeks with conversion tracking.
- **V‑3 – Align on scoring roadmap**
  - With Ilse, define when and how to tackle the deeper scoring/transferability redesign vs. the conversation‑system refresh.

## Owner: Ilse
- **I‑1 – Clarify current notification capabilities**
  - Confirm the status of the in‑app notification system: what is designed vs. actually wired.
  - Document what would be required to use notifications for long‑running operations (e.g., vibe checks, full analysis) once prioritized.
- **I‑2 – Email vs. in‑app notification cost/effort**
  - Roughly quantify the implementation and maintenance cost of email‑only flows vs. combined email + notification flows.
  - Provide a short recommendation on what should be implemented first.
- **I‑3 – Scoring model investigation**
  - Capture current behavior where vibe checks under‑ or over‑estimate fitness once candidates have many stories.
  - Sketch options for separating global transferability scores from per‑job interpretation (no implementation yet, but enough structure to make a prioritization call).
- **I‑4 – Data quality/UX bugs**
  - Investigate the "direct apply from product manager/designer" labeling quirk and any similar data‑entry or mapping issues surfaced during the call.

## Owner: Rochel
- **R‑1 – Candidate experience for long‑running flows**
  - Map the current candidate journey for vibe checks and full analysis, highlighting wait points and failure modes (e.g., losing track of where to find results).
  - Propose a minimal but effective notification and/or progress‑tracking layer for these flows.
- **R‑2 – Funnel QA and CTA wiring**
  - Audit employer‑facing landing pages to identify CTAs that route to the wrong destinations (e.g., demo CTAs going to the job board).
  - Coordinate with Logan and engineering to update links and verify the full flow using test email addresses.
- **R‑3 – Employer configuration messaging**
  - Draft copy that explains recommended defaults for hard vs transferable skills (e.g., 80/20) and gently warns when employers over‑tighten filters.

## Owner: Ilya
- **IY‑1 – Candidate time‑commitment landing page**
  - Finalize the modular messaging (headline, sub‑headline, explainer, CTA) that positions extra time with Careerspan as a clear advantage for candidates.
  - Prepare 2–3 variants suitable for A/B testing.
- **IY‑2 – Ad creative and campaign design**
  - With Logan, select a small set of ad concepts (including the pre‑Christmas "open this gift early" theme) for initial testing.
  - Define guardrails for the potential Black Friday/Cyber Monday experiment: budget caps, geography, audience, and success metrics.
- **IY‑3 – Data/agent experiment framing**
  - Outline one or two concrete experiments where lightweight agents could manage multi‑sided communication and reporting, to be revisited once email basics are live.

## Owner: Logan (via references)
- **L‑1 – Visuals and landing pages**
  - Refine ad creative for the selected themes, ensuring visual consistency and broad appeal.
  - Implement or update the candidate‑facing and employer‑facing landing pages using the copy defined with Ilya and Rochel.
- **L‑2 – CTA forms and flows**
  - Ensure that demo/trial CTAs connect to the correct forms or scheduling tools (e.g., Calendly), not the job board, and that confirmation states feel coherent with the brand.

## Shared / Team
- **T‑1 – End‑to‑end funnel testing**
  - Before any campaign launch, run internal tests from ad click → landing page → form/Calendly → confirmation → follow‑up emails to validate the full flow.
- **T‑2 – MG‑stack follow‑through**
  - Use this intelligence to inform MG‑3/MG‑4 style workflows (e.g., warm intros, follow‑ups) while respecting meeting type and internal vs external boundaries.

