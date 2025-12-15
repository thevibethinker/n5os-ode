---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
---

# B01 – Detailed Recap

**High-level summary**

Internal product and GTM check-in focused on (1) experimenting with Fireflies’ limits, (2) whether to ship a configurable job-analysis endpoint, (3) how to surface usage analytics without blowing up infrastructure costs, and (4) Ilya’s LinkedIn-led outbound and LinkedIn-groups GTM plan for Careerspan.

## 1. Opening: Fireflies experiment and AI boundaries

- Ilse and the team jokingly try to get Fireflies to perform a dramatic reading of “The Witch of Coös” with character voices, framing it as “mission critical” and even claiming investors are listening.
- Fireflies repeatedly refuses, insisting it is designed only for meeting-related tasks (action items, bookmarks, information capture).
- After several humorous attempts (including threats to “fire” the bot), the group accepts the limitation and moves on.

## 2. Job-analysis configuration tool question

- Ilse proposes a tool, callable via an internal endpoint, that would let someone describe how they want job-analysis to differ (e.g., different hard-skill emphasis) without requiring repeated tweaks to the chat UX.
- She notes there has been little concrete feedback that users care deeply about ultra-granular control over which responsibilities or skills are highlighted.
- V confirms that while people like *some* control, nobody is “clamoring” for deep configuration; having Ilse or V adjust things manually is acceptable.
- **Conclusion:** Ilse will *not* prioritize this configuration tool right now and will focus on user-chat / conversation improvements for the week.

## 3. Usage analytics, PostHog spreadsheet, and infra constraints

- V inspects design-partner usage (e.g., David Shuklett’s Skillcraft account) and observes a pattern: ~10 people have viewed the role and 3–4 have applied.
- He asks whether there is a centralized way (e.g., via PostHog) to see who viewed, who applied, and how far applicants progressed through onboarding.
- Ilse walks through a spreadsheet she generated:
  - `applied = true` marks actual applicants.
  - `distributed = true` marks people who clicked the direct apply link.
  - An onboarding-status column shows whether a user just uploaded a resume or fully completed onboarding.
- She explains that because the data lives in Firebase-style collections (employers, leads, users, stories), computing roll-ups is read-expensive and doesn’t scale if run too often or across many employers.
- They discuss exposing an endpoint that can regenerate the spreadsheet for a selected subset of employers, with the understanding that beyond ~1,000 views the reads become expensive and must be used cautiously.
- **Conclusion:** Current state (manual spreadsheet + selective endpoint) is acceptable; fully-automated, always-fresh analytics is deferred until the system and data model are more mature.

## 4. Crypto and personal context (relationship-building)

- The conversation drifts into a candid discussion of crypto windfalls and missed opportunities.
- Logan shares the story of his friend Lizzie, whose family wealth comes from early Bitcoin and Tesla bets; they now live comfortably in Cambridge, reinforcing the “we missed crypto” feeling.
- Ilse recounts nearly installing one of the first Bitcoin ATMs in Chicago but backing out due to her lawyer father’s concerns about being implicated in drug-related transactions and corruption.
- V empathizes with the tradeoffs and frames it as an example of rational risk-avoidance that nonetheless carried huge opportunity cost.
- This segment is primarily bonding and context, not operational, but it underlines the team’s awareness of risk, regulation, and path dependence.

## 5. LinkedIn outreach and December offer framing

- Ilya has a long tail of recruiter and hiring-manager 1:1 LinkedIn connections at target-sized companies and wants to re-engage them.
- His plan is to send personal messages along the lines of “you need to meet these people,” effectively introducing V and Logan and positioning Careerspan as a must-see AI hiring tool.
- They map out scenarios:
  - Contacts go dark → at least they receive a concise intro and possibly a link to learn more.
  - Contacts express curiosity → send them to a short form that gathers pain points and triggers a founder follow-up.
  - Contacts are ready to pay for help with one or two hard roles → need a clear, credible “December special” they can say yes to quickly.
- V is comfortable with flexible introductory offers (e.g., discounted or “first ~100 candidates processed” style deals) as long as they feel premium rather than cheap; the offer should foreground quality and proof-of-value.

## 6. GTM2: LinkedIn groups and thought leadership

- Ilya outlines “GTM2”: seeding and sustaining a presence inside targeted LinkedIn groups where their buyers spend time.
- He is cataloging group rules in a document and proposes to ghostwrite a substantial batch of posts for V (and ideally Logan) so they can drip content into these communities over time.
- Everyone acknowledges this as a slower, compounding channel rather than a quick-demand spike, but strategically important because it directly targets decision-makers.

## 7. Close and immediate next steps

- V expresses appreciation for the way Ilya’s various workstreams (sales content, GTM2, LinkedIn outreach) are converging.
- V needs to drop to handle other work; Logan and Ilya briefly discuss internal matters (e.g., contract questions), and Ilse remains a point person for follow-ups.
- The meeting ends with alignment that, near term, the team will:
  - Emphasize conversation UX and user chats over new configurability features.
  - Use the analytics spreadsheet + selective endpoints carefully, given database-read costs.
  - Move ahead with Ilya’s LinkedIn-led outreach and GTM2 program as key go-to-market experiments.

