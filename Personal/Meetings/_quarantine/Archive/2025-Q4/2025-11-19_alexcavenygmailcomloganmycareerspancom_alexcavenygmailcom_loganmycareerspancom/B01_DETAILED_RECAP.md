---
created: 2025-11-19
last_edited: 2025-11-19
version: 1.0
---

# B01: Detailed Recap

## Overview
This was a strategic meeting between Careerspan founders (Vrijen and Logan) and Alex Caveny, an experienced founder/investor with prior successful exit experience. The discussion centered on Careerspan's positioning, product strategy, go-to-market approach, and acquisition readiness.

## Key Context Established
- Careerspan is in active fundraising conversations with multiple VCs (Marvin Ventures LOI received, Sapphire Ventures demo scheduled)
- Strong product-market signals: 3,000+ signups, ~500 active users with full profiles, high usage satisfaction
- VCs express strong interest in deploying Careerspan as a talent partner/hiring solution for their portfolio companies
- Core tension: Sourcing talent pipeline economics are challenging; need to clarify business model priorities

## Major Discussion Areas

### 1. VC as Customer vs. Acquisition Target
**Key insight from Alex:** Don't worry excessively about M&A targets. Focus on building product correctly and talking to the right people (potential customers and acquirers are often the same people). His company's acquisition was opportunistic—they were talking to publishers as customers, one of whom decided to buy rather than distribute.

**Careerspan's approach:** 90 minutes/week on relationship mapping (not target-setting) to identify decision-makers at potential customers and acquirers. Majority of time focused on sales and customer acquisition.

### 2. Core Product vs. Moat
**Critical framing from Alex:** The talent triaging workflow (intake applicants → rank → deliver ranked list) is what will be valuable in M&A scenarios. Careerspan's specific database size, branding, and supply-side features won't matter; acquirers will extract the core algorithm and embed it into their platform. This means the core triaging workflow must be bulletproof and efficient.

### 3. VC Portfolio Model Opportunity
**Alex's observation:** The VC hiring cycle perfectly aligns with passive seeker availability cycles. VCs need continuous talent pipelines for portfolio companies but don't have active hiring needs year-round. Careerspan could serve as a standing talent reservoir that VCs tap into when portfolio companies raise and need to scale.

**Implementation discussion:** 
- A portfolio company raises capital, needs 5 engineers
- They request Careerspan, get qualified candidates within days vs. weeks
- Creates compounding advantage: speed of hiring becomes a competitive differentiator for the VC's portfolio

### 4. Business Model Clarity Needed
**Challenge:** Current unit economics for full talent scanning (exhaustive LLM analysis across entire database) are prohibitive (~$100s per search). Compute time: ~1 week per exhaustive scan.

**Solution direction:** Rather than perfecting accuracy, Careerspan should focus on cost and speed. Options discussed:
- Hard filters first (location, job category) to reduce candidate pool
- Lightweight first-pass model to encode profiles into cheaper-to-search representations
- Only deep analysis for warm-start demo candidates, not full database scans initially

### 5. "Wow Moments" & Sales Conversion
**Short-term (hours):** Demo showing 3-5 highly qualified candidates from existing database against employer's needs. This proves capability and warm-starts hiring process.

**Long-term (1 week):** Employer posts full job, Careerspan processes all inbound, delivers ranked shortlist. This demonstrates full value but requires delayed gratification—hard to close on promise alone.

**Key insight:** Mix both moments. Quick demo wins trust; follow-up with full processing. The narrative: "You didn't find your perfect candidate yet, but you're almost there—stay with us."

**Parallel strategy:** Show "recently hired" candidates in search results (like StubHub ticket sales) to maintain engagement and FOMO. "This engineer got hired through Careerspan last week—keep checking back."

### 6. Machine Learning Optimization
**Alex's war story:** Led AI team at computer vision home security startup. Previous approach: optimize accuracy endlessly. His approach: Define business objective (e.g., "accurate results in 2 hours for <$0.50 cost"), then ruthlessly hack the system to meet those constraints rather than chase theoretical perfection.

**Application to Careerspan:** 
- Don't let ML engineer optimize for accuracy percentage points
- Define business constraints: speed targets, cost per search, acceptable accuracy threshold
- Use "hacks" (persistence metrics, profile encoding, lightweight models) to achieve business objectives
- Current state: 40 pages of analysis per user is 39 pages too many; refactor ruthlessly

## Strategic Recommendations from Alex

1. **Focus relentlessly on core workflow:** Intake → Rank → Deliver. This must work perfectly. Everything else is secondary.

2. **Don't over-optimize before customers:** Get first paying customers, learn what they actually want on the output page, then prune ruthlessly.

3. **Acquisition naturally follows good product:** If the product is modular, fast, and effective at triaging, acquirers will come calling. Don't engineer specifically for acquisition.

4. **Location-specific concentration:** Focus on San Francisco and New York talent supply first. This gives concentration advantage for initial VC partnerships and reduces compute burden.

5. **University channel is a trap:** Extremely long sales cycles, no motivation for them, high risk aversion, low budget. Avoid unless truly self-serve with zero support required.

## VCs and Partnership Opportunities Discussed

- **Marvin Ventures:** McKinsey alumni fund. Potential for LOI partnership as official hiring channel + program perk
- **Sapphire Ventures:** Demo scheduled
- **Superposition:** Existing partnership example; loyalty-building through speed (helped Julia fill CTO role via Betaworks in competitive hiring)
- **University partnerships:** Self-serve model only; avoid pilots/high-touch

## Operational Notes
- Next meeting scheduled December 3rd (moved from November 25 due to Thanksgiving)
- Alex willing to distribute marketing materials once product deliverables ready
- Looking for explainer video, quick demo, and refined "one-pager" on candidate presentation format
- Emphasis on creating polished product assets for demo/sales process
