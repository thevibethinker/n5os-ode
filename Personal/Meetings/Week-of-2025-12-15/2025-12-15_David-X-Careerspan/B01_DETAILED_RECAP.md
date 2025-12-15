---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
---

# B01 – Detailed Recap

**High-level summary**

Conversation between V and David Spiegel exploring whether to co-create a "networker in a box" system on Zo that captures David’s networking philosophy, leverages Zo + Condo + other tools, and could be delivered as a hands-on series for the Next Play community and similar "option maximizer" audiences.

## 1. Opening relationship and personal context

- Light personal warm-up about winter decorations, Hanukkah vs. Christmas, and New York/Jewish background.
- David shares family history (Queens/Brooklyn, Pale of Settlement, Ashkenazi roots; Sephardic friend tracing lineage via Chile to Syria).
- This establishes high trust and familiarity before shifting into product/strategy mode.

## 2. Core problem: networking is hard, ad hoc, and undersupported

- David notes that most professionals "know" they should network but lack a concrete system.
- He distinguishes **three distinct networking arenas**:
  1. **Job-search networking** – targeting roles and companies, using first- and second-degree connections and cold outreach.
  2. **Internal networking** – building cross-functional relationships inside a current company so people are known and effective.
  3. **Personal / keep‑in‑touch networking** – staying connected with past managers, colleagues, and friends over time.
- Across all three, the pain is *not* just knowing what to do; it is **staying organized, remembering who to contact when, and following through**.

## 3. Vision: "Spiegel in a box" / networking system built on Zo

- V proposes a productized system on Zo – effectively "Spiegel in a box" – that encodes David’s approach so others can follow it.
- Initial framing is a **networking agent / toolkit in a box**, installable from a GitHub repo into a user’s Zo instance.
- They imagine this being used in a **live series** (e.g., with Next Play and Ben Lang):
  - Attendees join with Zo instances.
  - They install a pre-built networking system.
  - Sessions walk them through customizing flows and actually using the system.
- David likes the idea *if* it can (a) codify his rules and (b) still respect the necessary human judgment in messaging.

## 4. Automation boundaries: what can be systematized vs. must stay human

- David emphasizes that **some parts are automatable**:
  - Surfacing who to reach out to (first/second-degree connections).
  - Reminding people when they are due for a check-in.
  - Suggesting candidate posts, articles, or events to use as touchpoints.
- Other parts must stay human:
  - Writing nuanced messages.
  - Deciding whether a particular opportunity or relationship feels right.
- V and David agree that Zo should **surface structured opportunities and context**, then hand off to a human for the last mile (editing, sending, judgment).

## 5. Tooling landscape: LinkedIn, Dex, Condo, and Zo

- David describes current tools:
  - **Dex (getdex / join decks)** – attempts to be a personal CRM but feels clunky for his workflows.
  - **Condo (Mitchell’s product)** – great for orchestrating email/LinkedIn messaging but explicitly *not* trying to be a full CRM.
- They discuss Zo’s strengths:
  - File-based system, scheduled agents, search, tagging.
  - Ability to connect to external providers (e.g., Condo, LinkedIn scrapers, email).
- A recurring constraint: **LinkedIn’s API limits and anti‑automation posture**, especially around search and scraping.
- V suggests optionally using third‑party data providers (e.g., Bright Data) for LinkedIn‑adjacent data, depending on cost and risk appetite.

## 6. Concept: lightweight CRM + scheduled agents + tagging discipline

- They brainstorm a Zo-native pattern for relationship tracking:
  - Simple person records (a lightweight CRM) living as files or structured entries.
  - Scheduled agents that:
    - Scan tags (e.g., "quarterly", "annual", "job_search") and last-contact dates.
    - Surface a small, manageable list of people to contact each week.
  - Mechanisms to ingest signals from email and Condo.
- V shares an existing pattern using **Howie** and hidden signature tags (e.g., `VOS` tags) to classify conversations and drive follow-ups.
- The idea is to reuse this style of "semantic tagging + scheduled agents" for networking use cases.

## 7. Audience and GTM framing

- They distinguish between:
  - **Acute pain / job search** – people actively job hunting who need networking to land roles (clear "painkiller").
  - **Option maximizers / slow-burn networkers** – high-performing professionals who are not in crisis but want to keep their network warm (more of a "vitamin").
- David has coached many product managers who begin with very small networks (e.g., 300 LinkedIn connections after 10+ years) and need to **deliberately expand and nurture** their network.
- V notes that Next Play’s audience skews toward ambitious "option maximizers"; a slow-burn, keep‑in‑touch system might fit them well while still being anchored in real networking outcomes.

## 8. Program structure ideas

- Potential **multi‑session series**:
  - Session 1: Install base Zo networking kit; connect Condo/email; define cohorts and cadences (weekly/monthly/quarterly/annual).
  - Session 2+: Implement specific flows (job-search outreach, internal networking, personal keep‑in‑touch, birthday/anniversary pings, etc.).
  - Later sessions: Add more advanced automations (e.g., scraping, richer enrichment, dynamic cadences).
- They also consider **sponsored integrations** (e.g., Condo, Aviato, other vendors) that could provide trial access and act as co‑marketing partners.

## 9. Principles: IKEA effect and guardrails

- V stresses that Zo is not a traditional SaaS app; users can change the system by using it, which is both power and risk.
- They agree on leaning into the **IKEA effect**:
  - Provide pre‑built components and guardrails.
  - Require users to assemble and lightly customize pieces themselves.
  - This increases understanding, buy‑in, and resilience when things change.
- Any kit they ship should therefore be **opinionated but modifiable**, with clear protection around core files so users cannot accidentally destroy the system without explicit intent.

## 10. Next steps and open questions

- V plans to speak with the Zo team ("the Zokes") about:
  - Where this fits in Zo’s broader ecosystem.
  - Whether they’d support a co‑branded series with Next Play.
  - What technical baselines (personas, commands, agents) already exist that can be packaged.
- David is open to collaborating on:
  - Writing down his three networking archetypes and rules in more detail.
  - Helping design curriculum and examples for a live cohort.
- Open design questions include:
  - Whether to lead with **job‑search networking** (clearer pain) or **slow‑burn relationship maintenance** (better long‑term fit for option maximizers).
  - How much LinkedIn automation to rely on vs. staying within email/Condo and user‑driven workflows.


