---
created: 2025-11-19
last_edited: 2025-11-19
version: 1.0
---

# B05: Action Items

## Immediate Actions (This Week)

### 1. **Cancel November 25 Meeting**
- **Owner:** Vrijen
- **Due:** Immediate
- **Description:** Cancel scheduled meeting with Alex on November 25 due to Thanksgiving conflict.
- **Status:** Committed during call

### 2. **Define ML Cost/Speed Business Objectives**
- **Owner:** Vrijen + ML Engineer (Ilsa referenced)
- **Due:** This week or next
- **Description:** Translate framework from Alex into concrete targets (e.g., "X$/search, Y minutes, Z% accuracy"). Replace current "make it faster/cheaper" vague objective with measurable targets.
- **Key context:** Current state ~1 week compute, $100+ cost per full database search. Target should be 2 hours, <$0.50 estimated.
- **Success criteria:** ML team has clear objective function to optimize against (not open-ended accuracy improvement)

### 3. **Begin Relationship Mapping for VC Outreach**
- **Owner:** Vrijen + Logan
- **Frequency:** 90 minutes/week recurring
- **Description:** Map network of known contacts at potential customer/acquirer companies, especially focus on decision-makers and VC firms. Identify 3-5 priority VCs and people to reach out to.
- **Specific targets mentioned:** 
  - Soma (from Marvin Ventures / McKinsey alumni fund)
  - Mark (last name unclear, Founder of Braze/MXV Capital, known via Yeshiva connection)
  - Andreessen Horowitz (as example; likely aspirational not priority)
- **Success criteria:** Clear contact list for targeted outreach

### 4. **Finalize Product Deliverables**
- **Owner:** Logan (working with Ilya)
- **Due:** 1-2 weeks (estimated)
- **Description:** Complete the following marketing/demo assets:
  - Explainer video (storyboard review with Alex later)
  - 2-minute platform demo
  - Refined "one-pager" on candidate presentation format
- **Context:** These will be sent to Alex and used in sales demos with prospects
- **Success criteria:** Assets are polished enough for customer/investor consumption

### 5. **Refactor ML Analysis Output**
- **Owner:** Ilsa (ML engineer) + Vrijen
- **Due:** This week or next
- **Description:** Stop generating 40-page analysis per candidate. Determine minimal critical information needed for decision-maker (hypothesis: 1 page). Test this against early demo customers.
- **Context:** Current verbosity is wasting compute and confusing customers
- **Success criteria:** One-pager format defined and prototyped

---

## Near-Term Actions (1-2 Weeks)

### 6. **Run First Demo with Prioritized VC**
- **Owner:** Vrijen + Logan
- **Due:** 1-2 weeks
- **Description:** Get at least one VC demo booked and executed. Use refined demo assets and two-moment approach (quick qualified candidates + follow-up with full analysis).
- **Context:** Soma mentioned as potential priority if they can be brought on board
- **Success criteria:** Demo completed, feedback captured

### 7. **Share Product Deliverables with Alex**
- **Owner:** Logan
- **Due:** After deliverables complete (1-2 weeks)
- **Description:** Send explainer video, demo, and one-pager to Alex for feedback and refinement discussion.
- **Context:** Alex wants to see "literal" product design (what info appears where) not just conceptual discussion
- **Success criteria:** Feedback received and incorporated

### 8. **Add Passive Job Seeker Signal to Onboarding**
- **Owner:** Product team (likely Logan overseeing)
- **Due:** 1-2 weeks
- **Description:** Update onboarding flow to ask candidates: "Are you looking for a job right now? In the next few months? Open?" (or similar). This enables messaging distinction between active and passive seekers.
- **Context:** Discussed but not yet formalized; needed for targeting VC portfolio model
- **Success criteria:** Onboarding updated and tested

### 9. **Create "Recently Hired" Feature for Search Results**
- **Owner:** Product team
- **Due:** 1-2 weeks or lower priority
- **Description:** Display "recently hired" candidates in search results alongside available candidates (like StubHub "ticket sold 2 hours ago"). Maintains engagement and FOMO.
- **Context:** Discussed as engagement/retention tactic
- **Success criteria:** Feature prototyped and tested in demo

---

## Medium-Term Actions (2-4 Weeks)

### 10. **Optimize ML Pipeline for Cost/Speed**
- **Owner:** Ilsa (ML engineer)
- **Due:** 2-4 weeks (after objectives defined)
- **Description:** Implement optimizations to hit business objectives:
  - Hard filters (location, category) first
  - Lightweight first-pass encoding
  - Only deep analysis for demo candidates initially
  - Auto-encoding of profiles for cheaper search
- **Context:** Alex emphasized avoiding exhaustive database scans; use "hacks" to achieve business targets
- **Success criteria:** Unit economics improve to target range

### 11. **Launch Location-Filtered Candidate Lists**
- **Owner:** Product team
- **Due:** 2-4 weeks
- **Description:** Create SF and NYC candidate leaderboards/filtered lists. Rank by activity (# stories completed) to build "Careerspan SF 100" / "Careerspan NYC 100" positioning.
- **Context:** Concentration strategy discussed; reduces compute, builds geographic brand
- **Success criteria:** Lists created and promoted in sales materials

### 12. **Prepare First Customer Case Study Materials**
- **Owner:** Vrijen + Logan
- **Due:** 2-4 weeks (after first customer/demo)
- **Description:** Once a demo customer is secured or shows interest, document their job posting, candidate matches, hiring timeline, and feedback. Create case study for VC distribution.
- **Context:** Alex offered to distribute to hiring contacts; case studies strengthen positioning
- **Success criteria:** At least 1 case study drafted

### 13. **Establish Bi-Weekly Check-In Cadence with ML Team**
- **Owner:** Vrijen
- **Due:** First check-in within 1 week
- **Description:** Schedule recurring meetings with Ilsa to monitor ML optimization progress against business objectives. Prevent over-optimization for accuracy at expense of cost/speed.
- **Context:** Alex emphasized need for CEO/founder to "rein in" ML engineer and enforce business discipline
- **Success criteria:** Check-ins scheduled and tracked

---

## Ongoing Actions (Recurring)

### 14. **Weekly Relationship Mapping & Outreach (90 min/week)**
- **Owner:** Vrijen + Logan
- **Frequency:** Every week
- **Description:** Identify new contacts, refine outreach strategy, maintain pipeline of VC demos.

### 15. **Monthly Sales Process Refinement**
- **Owner:** Logan (primary owner per context)
- **Frequency:** Monthly check-in with Vrijen
- **Description:** Analyze demo feedback, refine sales materials, test two-moment approach variations.

### 16. **Bi-Monthly Check-In with Alex**
- **Owner:** Vrijen (organizer)
- **Frequency:** Every other month (December 3 next)
- **Description:** Share progress, get feedback on pivots, discuss new opportunities.

---

## Decision Points / Open Questions Requiring Follow-Up

1. **ML cost/speed targets:** What are the final numbers? (Discussed in principle, needs formalization)
2. **One-pager content:** What information does it contain? (Discussed as TBD, critical for sales)
3. **First demo target:** Who is the first VC we approach? (Soma mentioned conditionally)
4. **University partnerships:** Confirm formal rejection or revisit conditions for self-serve model?
5. **Passive seeker onboarding:** What exact questions? (Framework discussed, copy TBD)

---

## Notes on Ownership & Accountability

- **Vrijen:** Strategic direction, external relationships, ML discipline, schedule coordination
- **Logan:** Product/sales execution, marketing assets, onboarding, case studies, VC outreach
- **Ilsa (ML engineer):** Cost/speed optimization, profile encoding, analysis output
- **Ilya (sales support):** Creative/explainer video, demo refinement
- **Alex (external advisor):** Feedback provider, referral source for hiring contacts

---

## Success Metrics / Checkpoints

**Near-term (2 weeks):**
- Product deliverables complete
- ML objectives formally defined
- 1st demo booked

**Medium-term (4 weeks):**
- 1st demo completed with feedback
- ML optimizations show cost/speed improvement
- Location-filtered lists live

**Long-term (next meeting, Dec 3):**
- Progress on 1st customer
- Refined sales process based on demo feedback
- Alex prepared to make introductions
