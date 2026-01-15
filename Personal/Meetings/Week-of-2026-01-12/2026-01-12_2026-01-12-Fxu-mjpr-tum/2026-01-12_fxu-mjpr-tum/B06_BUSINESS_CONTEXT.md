---
created: 2026-01-13
last_edited: 2026-01-13
version: 1.0
provenance: con_YB9D0AvmxMZVDyHL
block: B06
---

# B06: Business Context

## Companies & Products Discussed

### Zo (Primary Platform)
- **Context:** AI productivity platform V is heavily building on
- **V's Analysis:** "Stuck between too technical for non-technical people and not technical enough for technical people"
- **Proposed Solution:** Economic incentive through careers (indirect) or e-commerce (direct)
- **V's Relationship:** Has credibility with Tiffany (Zo team); pitched GTM analysis
- **Integration:** Fireflies API plugs into Zo nicely for transcripts

### Careerspan
- **Context:** V's company; David previously in advisory role
- **Evolution:** Relationship shifting from advisory to partnership
- **Note:** Not central to this discussion—focus on new joint venture

### PCA (Product Career Academy?)
- **Context:** Where David gained PM coaching experience
- **Relevance:** Source of David's methodology and network

### Flow (Jamie McDermott)
- **Context:** Toronto-based GTM consulting firm
- **David's Arrangement:** Partnering for execution capability
- **Model:** Addresses gap where advisors "only advise... then the company can't do anything"

### Maven (Platform)
- **Context:** Course platform for cohort-based learning
- **David's Plan:** Teaching PM courses on landing interviews
- **Reference:** Ethan Evans as top performer (ex-Amazon VP)

---

## Market Positioning Discussion

### Problem Statement
V articulated Zo's positioning challenge:
> "You're stuck between a product that is not technical enough for the technical people and too technical for the non-technical people."

### Proposed Solution Framework
V's GTM thesis shared with Tiffany:
- **Direct economic incentive:** E-commerce (Zo helps you make money)
- **Indirect economic incentive:** Careers (Zo helps you get a better job)

V's Proposal to David:
> "We build products for personal productivity that are built atop Zo. In building the productivity tool, you learn how to use Zo."

---

## Competitive Landscape

### Interview Prep/Analysis Tools
- **Super Interviews:** David has access
- **Ben Erez's Co-pilot:** David has access
- **V's Interview Analysis Tool:** Proof of concept; "directionally correct"

### PM Career Coaching
- **Ethan Evans:** Ex-Amazon VP; high-quality Maven courses
- **Wes Bush:** PLG advisor (critique: "only advise, goodbye")

---

## Business Model Discussion

### Challenges Identified
1. **Auth/State Management:** V wary of user accounts complexity
2. **Subscription vs Per-Use:** SaaS ideal but requires state
3. **Local vs Hosted:** Tradeoff between user data control and monetization

### Proposed MVP Model
- **Per-use payment:** $10-30 per transaction
- **No persistent state:** Session-only processing
- **Stripe integration:** Already working in V's tools

### Alternative Architecture (Brainstormed)
- Forward email to Zo server
- Check subscription status
- Return advice
- David noted: "I built that" (Email Tone Detector GPT)

