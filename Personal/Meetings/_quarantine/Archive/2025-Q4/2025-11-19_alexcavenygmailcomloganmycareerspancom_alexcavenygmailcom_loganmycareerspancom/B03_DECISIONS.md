---
created: 2025-11-19
last_edited: 2025-11-19
version: 1.0
---

# B03: Decisions

## Strategic Decisions Made

### 1. Product Focus: Core Workflow Prioritization
**Decision:** Ruthlessly prioritize the candidate triaging workflow (intake → rank → output) as the sole focus for excellence. All other product features are secondary.

**Rationale:** From Alex's M&A experience, acquirers only care about this core workflow. Database size, branding, and supply-side features are disposable. The triaging algorithm/process is the only modular piece with standalone value.

**Implication:** Stop building new features or optimizing tangential product areas until this core workflow is bulletproof and fast.

---

### 2. Business Model Direction: VC Portfolio as Primary Customer
**Decision:** Prioritize VC portfolio companies as customer segment over self-serve individual hiring.

**Rationale:** VCs need continuous talent pipelines for growth-stage hiring. Their hiring cycles align with passive seeker availability. Initial customer acquisition is faster/easier through VC channels than building a 3,000+ user self-serve hiring marketplace.

**Implication:** Demo and sales process should be tailored to VC use case (show ability to support portfolio company hiring rapidly). Emphasize speed and quality over database breadth initially.

---

### 3. ML Cost Optimization: Define Business Objectives, Not Accuracy Metrics
**Decision:** Shift ML optimization away from accuracy improvements and toward cost/speed targets.

**Concrete objective defined:** Produce results in 2 hours for <$0.50 cost (example, to be refined).

**Rationale:** Current exhaustive LLM analysis costs $100s and takes 1 week per search. Business cannot scale at this cost. Further accuracy improvements are irrelevant if cost/speed don't meet business targets.

**Implication:** Reframe ML engineer's performance metrics from "accuracy improvement" to "cost reduction + speed increase while maintaining acceptable accuracy threshold."

---

### 4. Go-to-Market: Relationship-Based Network Mapping Over Target Lists
**Decision:** Spend ~90 minutes/week on relationship mapping (who do we know at potential customer/acquirer companies) rather than identifying abstract "acquisition targets."

**Rationale:** Best customers and best acquisition opportunities are often the same people. Focus on relationship building and sales execution, not strategic planning.

**Implication:** Logan and Vrijen meeting weekly to identify relevant contacts at target companies and decision-makers. Majority of time invested in sales outreach and demo execution, not strategy.

---

### 5. Sales Process: Two-Moment Approach
**Decision:** Structure sales process with both short-term (hours) and long-term (1 week) "wow moments."

**Short-term:** Deliver 3-5 qualified candidates from existing database within hours.

**Long-term:** Full job posting analysis delivered after 1 week processing.

**Rationale:** Immediate win builds trust and proves capability. Delayed gratification requires upfront belief in vision. Combining both maximizes conversion probability.

**Implication:** Invest in creating compelling demo materials and case studies. Use narrative "you're almost there" to maintain engagement.

---

### 6. Geography Focus: Concentrate on SF and NYC
**Decision:** Limit initial location targeting to San Francisco and New York for candidate supply.

**Rationale:** Highest concentration of top candidates. Reduces compute burden (smaller database to analyze). Creates geographic brand positioning ("Careerspan SF 100" / "Careerspan NYC 100").

**Implication:** Update onboarding to ask location preference early. Create location-based candidate leaderboards (ranked by # of stories/activity).

---

### 7. M&A Positioning: Modularity Over Acquisition Readiness
**Decision:** Do NOT engineer specifically for acquisition. Focus on product modularity (core workflow can plug into other systems) and let acquisition happen opportunistically.

**Rationale:** Alex's company was not built for acquisition. Opportunistic buyer emerged because core product was modular and valuable. Over-engineering for M&A usually results in wrong product.

**Implication:** Stop over-optimizing for specific acquisition scenarios. Build great core product. Right acquirers will recognize value.

---

### 8. Customer Segments to Avoid (For Now)
**Decision:** Avoid university partnerships. Do NOT pursue high-touch pilot programs with educational institutions.

**Rationale:** University customers have high risk aversion, low budgets, extremely long sales cycles (17+ meetings, 20+ stakeholders), no motivation (indifferent to student employment outcomes), and minimal return on sales effort.

**Implication:** If university partnerships surface, only pursue if they are 100% self-serve with zero support/pilot work required.

---

### 9. Meeting Schedule Adjustment
**Decision:** Cancel November 25 meeting with Alex (Thanksgiving conflict). Reschedule next recurring meeting for December 3.

**Rationale:** Vrijen not originally from US; forgot Thanksgiving holiday.

**Implication:** Continue bi-monthly meeting cadence (2 meetings per month rolling average). December 3 counts as second November meeting.

---

### 10. Product Deliverables: Prioritize Marketing Assets
**Decision:** Prioritize creation of explainer video, 2-minute demo, and refined "one-pager" candidate presentation format.

**Rationale:** These are needed for sales process and can be provided to potential customers/investors for evaluation.

**Implication:** Logan (with support from Ilya/Ilsa) owns these assets. Timeline TBD but likely 1-2 weeks based on context ("in progress").

---

## Decisions NOT Made / Open Questions

1. **Exact ML cost/speed targets:** Business objectives discussed in principle; specific numbers to be finalized with engineering team.

2. **Passive job seeker messaging:** Discussed adding "are you open?" to onboarding but not formalized as decision.

3. **Profile encoding strategy:** Discussed concept of encoding profiles into cheaper-to-search formats, but no commitment to timeline/approach.

4. **Specific VC target list:** Despite relationship-mapping approach, no concrete list of priority VCs finalized during meeting.

5. **University partnership rejection:** Cautioned against, but not formally rejected—may revisit if self-serve model surfaces.

---

## Decision Quality Assessment

**Strong decisions:**
- Core workflow prioritization (clear, testable, actionable)
- M&A positioning approach (realistic, pattern-matched)
- VC portfolio customer focus (market-fit informed)

**Moderate clarity:**
- ML cost optimization (framework clear, specifics TBD)
- Sales process two-moment approach (concept clear, execution TBD)

**Implementation risk:**
- Geography concentration (may limit addressable market if not working)
- University avoidance (low risk but opportunity cost if market moves)
