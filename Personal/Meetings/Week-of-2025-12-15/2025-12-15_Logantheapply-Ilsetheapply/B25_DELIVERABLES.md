---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
---

# B25 – Deliverables

> **Scope:** Concrete artifacts, tools, or materials that were discussed as outcomes of this meeting.

## 1. Employer analytics report(s)
- **Owner:** Ilse
- **Description:** Maintain and regenerate, as needed, a spreadsheet-style report showing for selected employers:
  - Number of candidates who viewed the role,
  - Number who clicked the direct-apply link (`distributed = true`),
  - Number who fully completed onboarding.
- **Status:** In progress (first version exists for key accounts like Skillcraft). Future variants may be produced via an on-demand endpoint, scoped by employer.

## 2. On-demand analytics endpoint (scoped, not global)
- **Owner:** Ilse
- **Description:** A callable internal endpoint that, when invoked for a specific employer or small cohort, generates the analytics report described above.
- **Constraints:**
  - Must be designed with read-cost limits in mind (no default “all employers” mode).
  - Should be accompanied by clear guidance on expected cost when run at larger scales.
- **Status:** Concept discussed and aligned; implementation is lower priority than conversation UX work.

## 3. December “experiment” offer definition
- **Owner:** V (with input from Ilya)
- **Description:** A short written definition of the December trial offer (e.g., first ~100 candidates processed, or 1–2 roles per employer for a fixed test fee) that:
  - Feels premium and credible,
  - Is simple enough to explain in a single LinkedIn message or email,
  - Is easy to operationalize with existing systems.
- **Status:** To be drafted post-meeting; Ilya is waiting on this to anchor his outreach scripts.

## 4. LinkedIn 1:1 outreach scripts and tracking
- **Owner:** Ilya
- **Description:**
  - Concrete DM/email templates for re-engaging recruiter/hiring-manager contacts, introducing Careerspan, and presenting the December offer.
  - A simple tracking system (spreadsheet or CRM) noting who was contacted, their response path (no reply / curious / ready to buy), and any follow-up needed.
- **Status:** In planning; relies on the offer definition in Deliverable #3.

## 5. GTM2 playbook and content library
- **Owner:** Ilya (with V and Logan as voices)
- **Description:**
  - Document listing target LinkedIn groups, membership rules, and audience types.
  - A library of ghostwritten posts under V’s and Logan’s names, mapped to groups and scheduled over time.
- **Status:** Being assembled; group rules are partly documented, and content creation is the next major step.

## 6. Founder-intro landing / intake pattern
- **Owner:** V
- **Description:** Continued use and refinement of the pattern already in place for the McKinsey site (Marvin Ventures): a simple form that collects LinkedIn + pain points and automatically drafts an outreach email from V.
- **Status:** Already implemented for McKinsey context; this meeting reaffirms it as the default “facetime with the founder” path for similar campaigns.

