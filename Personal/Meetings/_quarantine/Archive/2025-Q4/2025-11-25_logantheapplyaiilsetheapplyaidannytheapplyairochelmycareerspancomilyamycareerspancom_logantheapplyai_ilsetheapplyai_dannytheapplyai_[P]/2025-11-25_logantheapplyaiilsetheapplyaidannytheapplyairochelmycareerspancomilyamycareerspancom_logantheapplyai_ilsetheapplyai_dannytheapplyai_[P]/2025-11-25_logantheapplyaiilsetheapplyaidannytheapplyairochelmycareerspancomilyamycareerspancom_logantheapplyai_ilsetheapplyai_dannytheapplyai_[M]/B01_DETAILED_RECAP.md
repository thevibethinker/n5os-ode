---
created: 2025-11-25
last_edited: 2025-11-25
version: 1.0
---

# B01 – Detailed Recap

## 1. Email, unsubscribes, and notification system
- Ilse and Rochel surface ongoing issues around unsubscribes and the broader challenge of managing employer–candidate communication at scale.
- Email is framed as the primary scalable channel; in contrast, "scanning"-style operations have no economies of scale and simply get more expensive as volume grows.
- The in‑app notification system exists in design but is effectively dormant; the UI is live but not actively wired up, so users are not being nudged via notifications today.

## 2. Concept: employer re‑engagement and AI agents
- The group discusses a feature where employers who pass on candidates can still maintain a relationship and possibly re‑engage them later.
- Ilya argues for a test‑heavy mindset: the team cannot reliably predict what the community will want, so they should instrument and experiment rather than over‑theorize.
- As a thought experiment, Ilya proposes AI agents that work all three sides of the market (candidates, employers, Careerspan) by maintaining polite, ongoing dialogue and surfacing behavioral insights in daily reports.

## 3. Pragmatic near‑term: own the email channel via SendGrid
- Ilse frames the concrete need as: when a clear trigger occurs, send the right emails to the right people, rather than over‑complicating things with heavy agents.
- V strongly supports Careerspan owning this communication channel directly via SendGrid, both for control and for the ability to track unsubscribes and behavior by email type.
- The emerging consensus: long‑term, agents and richer analytics may be useful, but in the near term the team should implement a simple, controlled email pipeline they operate themselves.

## 4. Demo readiness and pipeline thinking
- Conversation pivots to an upcoming demo; V reports that the previous demo hit the right notes overall but could be smoother in transitions and tighter on time.
- The team reads the prior call as a success because it moved the counterpart to an integration‑level discussion rather than a basic "is this a good idea" debate.
- V frames demos as part of a numbers game: if they can book around 10 demos every two weeks and convert roughly a third into ongoing revenue, the economics begin to look compelling, especially when combined with inbound motion.

## 5. Candidate experience: long‑running operations and notifications
- Rochel highlights how long some flows take (e.g., full analysis and vibe checking) and how painful it is for candidates to sit and wait or to have to hunt down results later.
- There is clear appetite for a notification system that tells candidates when long‑running processes finish, similar to how chat assistants offer "notify me when this is done" options.
- The group notes that this is currently under‑invested due to other priorities, but it is a critical UX upgrade once the core funnel stabilizes.

## 6. Vibe checks vs. full analysis – current architecture and cracks
- Ilse provides a history of vibe checks: originally designed as a way for a candidate to upload a job description and get guidance on whether applying is sensible, not as a hard filter.
- As users tell more stories (around five or more), the current scoring behavior flips: vibe checks start under‑representing their true fitness, so the signal becomes unreliable for filtering.
- Costs matter: vibe checks are intentionally kept cheap but still cost 8–10 cents each at current scale, so they must be used judiciously.
- Ilse also notes that today, a candidate can achieve very high scores on largely transferable skills alone, which is probably too generous and can mislead employers about readiness.

## 7. Future direction for scoring and transferability
- V asks whether the team can simply "tune thresholds" quickly; Ilse explains that the problem is deeper than a scalar adjustment and likely requires a redesign.
- Ilse outlines two possible architectures:
  - Maintain a globally consistent notion of what "transferable level 5" means, then have a second layer that interprets those scores differently per job.
  - Or make the interpretation itself per‑job or per‑line‑item, so some roles (e.g. product management) can demand stricter direct experience while others (e.g. certain tools) tolerate high transferability.
- This dual‑layer approach would allow, for example, employers to specify how much transferability they will tolerate, but it is more expensive and requires careful work to integrate with pre‑stored story semantics.
- Ilse flags that her next major product priority, per prior discussion with V, is modernizing the conversation system, so a deep scoring redesign is acknowledged but not immediately scheduled.

## 8. Ethics, employer control, and candidate opportunity
- Rochel and Ilse discuss giving employers knobs to tune the balance between hard skills and transferable skills (e.g., "80% hard / 20% transferable" as a recommended default).
- They want to avoid building a tool that simply lets employers over‑optimize for pedigree (e.g., Ivy League filtering) while still acknowledging that employers will pursue their preferences one way or another.
- V and Ilya note that powerful filtering already exists (e.g., Boolean searches on LinkedIn); the real question is how Careerspan can steer employers toward healthier, more inclusive defaults while not blocking legitimate needs.
- There’s a tension between supporting non‑traditional candidates (e.g., teachers moving into tech) and being honest about the onboarding burden and performance expectations for employers.

## 9. Community, data moats, and monetization ideas
- Ilya tells a story about LinkedIn’s anti‑scraping measures to illustrate how guarding access to data preserves platform value.
- The team imagines a future where Careerspan accumulates rich metadata across candidates and employers; any given user sees only a small slice by default.
- Upsell concepts include paywalled "deeper views" or temporary visibility boosts (likened to XP bonuses in games) that unlock richer insights for a single search or for a limited time window.

## 10. Candidate time‑commitment landing page
- Ilya walks through a slide deck for a candidate‑facing landing page focused on time commitment: persuading candidates that spending more time with Careerspan is to their advantage.
- The deck is structured as modular blocks: headlines, sub‑headlines, explanatory paragraphs, and calls‑to‑action that can be mixed and matched.
- The central narrative: "Welcome to Careerspan; you’ll spend a bit more time here, and that investment dramatically increases your odds of landing better work." The messaging leans on behavioral nudging and clear framing of benefits.

## 11. Creative directions for ad campaigns
- Ilya describes multiple ad themes: AI "slop" avoidance, richer views of candidates, and a standout pre‑Christmas concept where employers "open a gift early" to discover new talent.
- Logan has taken rough mockups and refined them into cleaner, more universal creative that could resonate across demographics.
- The favorite concept currently is the simple, clean gift‑themed ad that invites employers to "see something new" at Careerspan.

## 12. Funnel endpoints and CTAs
- Post‑ad CTAs under consideration include: watch a short video, book a demo, or start a trial.
- There is a known gap: at least one existing sales landing page currently routes the "Schedule 30‑minute demo" CTA to the job board instead of a Calendly or equivalent booking flow; this must be corrected.
- The team wants a clean flow where an interested employer can quickly express interest, submit contact details, and be routed into a predictable demo pipeline.

## 13. Black Friday / Cyber Monday campaign test
- With Thanksgiving and Black Friday approaching, the team debates whether to run a constrained experimental campaign during the holiday window.
- The idea is to set tight spend guardrails so that if engagement is low, cost remains negligible; if engagement is high, they gather useful signal without over‑exposing the system.
- Any launch will require end‑to‑end testing of the funnel: ads → landing page → form/Calendly → confirmation, with several dry runs using internal email addresses.

## 14. Closing and next steps
- The call closes with light banter and mutual recognition that the product and go‑to‑market motion are maturing: more demos, better messaging, richer employer controls, and deeper candidate experience.
- Immediate focus areas are: owning outbound email via SendGrid, tightening demo performance, clarifying scoring and transferability direction, and shipping the candidate time‑commitment landing page and supporting ads.

