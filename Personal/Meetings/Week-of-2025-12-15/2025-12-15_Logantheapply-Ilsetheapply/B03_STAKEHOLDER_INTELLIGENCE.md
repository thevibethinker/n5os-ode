---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
---

# B03 – Stakeholder Intelligence

## Vrijen Attawar (V) – Founder & CEO, Careerspan

- **Role / mandate**: Overall product and GTM decider; balances ambition with execution risk and infrastructure costs.
- **Current focus (from this meeting)**:
  - Keep primary engineering focus on conversation UX and user chats rather than secondary configuration tools.
  - Obtain clear, decision-grade usage analytics (views, applies, onboarding completion) without committing to brittle or overly expensive infra.
  - Shape early commercial offers that feel premium and credible, not “cheap,” while still lowering friction for first-time buyers.
- **Motivations / interests**:
  - Wants fast, human-grade insight into what is working (e.g., two-story completion patterns, design-partner behavior).
  - Values honest discussion of risk vs upside (e.g., crypto regret stories are used as analogies for product and infra decisions).
  - Appreciates GTM work that compounds over time (LinkedIn groups, 1:1 outbound) rather than shallow bursts.
- **Concerns / skepticism**:
  - Wary of overbuilding analytics or configuration before there is strong user pull.
  - Sensitive to hidden infrastructure costs (high read volume in Firebase-style data model).
- **Leverage points**:
  - Founder access and credibility with target buyers (e.g., McKinsey alumni, early-stage founders).
  - Willingness to personally engage via calls and tailored emails if prospects are pre-warmed properly.

## Logan Currie – Co-founder / Product & Narrative

- **Role / mandate**: Co-founder with strong product, narrative, and relationship instincts; uses stories and humor to humanize complex topics.
- **What matters to Logan here**:
  - Making sure product decisions reflect real founder personas (e.g., distinguishing “skills nerd” founders like David from more typical buyers).
  - Protecting focus on the highest-leverage surfaces (conversation UX, buyer conversations) instead of niche configuration.
  - Keeping an honest, emotionally grounded view of wealth, risk, and status (crypto, IPO anecdotes) that influences how they talk to buyers.
- **Behavioral signals**:
  - Uses detailed stories (Lizzie’s crypto wealth, Upload vs The Good Place) to explore ethics, control, and technology’s human impact.
  - Quick to endorse ideas that keep them close to users (conversations, thought-leadership in groups) versus abstract analytics work.
- **Leverage points**:
  - Strong storyteller who can front-facingly represent Careerspan in LinkedIn content and founder calls.
  - Personal network and credibility with tech-savvy peers.

## Ilse Funkhouser – Product / Engineering Lead

- **Role / mandate**: Owns internal tooling, data access, and infrastructure decisions; gatekeeper for what is technically safe and sustainable.
- **Current priorities (from this meeting)**:
  - Evaluate whether to ship an API-style configuration tool for job analysis (decision: defer; low current demand).
  - Provide V with a usable spreadsheet of employer/job analytics while managing database read costs.
  - Clarify technical constraints so commercial decisions (e.g., how often to refresh analytics) are grounded in reality.
- **Motivations / values**:
  - Strong bias toward infrastructure that scales sanely; resists “nice-to-have” features that could quietly become cost sinks.
  - Wants to be transparent about architectural debt (Firebase, lack of roll-up tables) rather than hide it behind dashboards.
- **Concerns / risk flags**:
  - Automatic, frequent recomputation of analytics across many employers would create unbounded read costs.
  - Nightly or always-on rollups strictly for analytics feel like “work for the sake of analytics” unless there is clear business payoff.
- **Leverage points**:
  - Deep understanding of the current data model and how to safely expose on-demand analytics.
  - Can ship pragmatic endpoints/tools quickly when there is a clear, narrow use-case (e.g., per-employer report generation).

## Ilya Kucherenko – GTM / Sales & Partnerships

- **Role / mandate**: Drives outbound, partnerships, and GTM experimentation; translates product value into motions that fill the top of the funnel.
- **Current initiatives (from this meeting)**:
  - Mine his 1:1 LinkedIn network of recruiters and hiring managers for warm introductions to Careerspan.
  - Frame December as a window for “small but meaningful” paid experiments (e.g., one or two hard roles per company with a simple, clear offer).
  - Operationalize GTM2 – structured posting into curated LinkedIn groups where ideal buyers congregate, using ghostwritten content from V and Logan.
- **Motivations / style**:
  - Prefers concrete scripts, offers, and fallback paths (“if they go dark, then send X”) rather than vague marketing language.
  - Comfortable doing manual, relationship-heavy work if it leads to high-quality conversations with the right buyers.
- **Concerns / questions**:
  - Needs clarity on pricing and structure of “specials” so he does not over- or under-sell the product.
  - Wants a clear default link / landing experience to send people to when they are curious but not ready to book a call.
- **Leverage points**:
  - Deep existing network at target companies after years in the space.
  - Willingness to ghostwrite and systematize founder-led content, which can compound in LinkedIn groups over time.

## Tools / non-human participants

- **Fireflies.ai Notetaker**: Serves as meeting recorder and action-item helper only; explicitly refuses theatrical or non-meeting tasks. The team’s playful attempts to push its boundaries surfaced clear design constraints and underscored the need to position tool capabilities honestly with users.

