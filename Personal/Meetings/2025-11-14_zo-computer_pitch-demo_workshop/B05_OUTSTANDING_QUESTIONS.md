---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
block_id: B05
---

# B05 - OUTSTANDING QUESTIONS

## Technical Questions (Unresolved)

1. **Secret Key Management Security**
   - **Asker**: Logan
   - **Question**: How does Zo manage secret keys securely? Does it require revealing API keys, or is there a protected vault?
   - **Vrijen's Answer (Partial)**: "There is a section in Settings which I can't quite see in developer mode. I'll grab that in a second. But, yeah, there's a specific section where you can store your secret keys."
   - **Status**: UNRESOLVED - No concrete answer provided on security mechanism
   - **Why it Matters**: API key security is critical for integrations; unclear if approach is robust

2. **URL Hallucination in Research Output**
   - **Asker**: Gabby
   - **Question**: The deep research report had URLs (Fortune Business Insights: "AI in Construction Market"). Are these real URLs or AI-fabricated?
   - **Vrijen's Answer**: Acknowledged the issue exists generally with LLMs; "It's very prompt dependent... worth checking"
   - **Status**: PARTIALLY RESOLVED - No definitive answer on validation; acknowledged risk
   - **Why it Matters**: Research credibility depends on source verification; users need discipline to validate

3. **Token Usage Parity Between Zo and ChatGPT/Claude**
   - **Asker**: Sheila (in chat)
   - **Question**: Is token consumption truly identical between Zo and native ChatGPT/Claude interfaces?
   - **Vrijen's Answer**: "Yes. Yes, yes. Because they essentially don't have too heavy of an intermediating layer of their own."
   - **Status**: RESOLVED - Token consumption is comparable; Zo adds minimal overhead
   - **Why it Matters**: Pricing transparency; users want to understand true cost

## Product/Feature Questions (Unresolved)

4. **Zo Email Tool Integration with Cora**
   - **Asker**: Logan (context from Sheila's question)
   - **Question**: How does Zo integrate with email tools like Cora or Superhuman? What's the current capability?
   - **Vrijen's Answer**: Not directly addressed; conversation pivoted to other email tools
   - **Status**: UNRESOLVED
   - **Why it Matters**: Email is critical workflow; integration capability affects usefulness for knowledge workers

5. **Folder Organization & Chronological Ordering**
   - **Asker**: Gabby (during deep research demo)
   - **Question**: Why doesn't Zo output sort deliverables in chronological/logical order? It just randomly orders (or alphabetically) sections in reports.
   - **Vrijen's Answer**: "Yeah. Right. Which is another one of those sort of quality of life upgrades that I'm not only lobbying for in the back end, I'm essentially hoping to build that."
   - **Status**: ACKNOWLEDGED BUG/LIMITATION - Not yet fixed; Vrijen personally working on it
   - **Why it Matters**: Output usability; presentation quality; requires post-processing

6. **Zo Learning Curve & Adoption Friction**
   - **Asker**: Logan
   - **Question**: How much time does it really take to get organized in Zo? Is the bootstrap approach sufficient, or do you need deep customization to get value?
   - **Vrijen's Answer**: Bootstrap model helps, but real effort is thinking/taxonomy upfront. "The effort isn't setting up the system to capture your thoughts. The effort is the thinking that you already do."
   - **Status**: PARTIALLY RESOLVED - Acknowledges the tradeoff but no concrete metrics on ROI breakeven
   - **Why it Matters**: ROI calculation for adoption; justifies spending time on setup

## Market/Business Questions (Resolved or Implicit)

7. **Zo Pricing Model & Value Capture**
   - **Question**: How does Zo make money given consumer-first positioning? Is there VC pressure for unit economics?
   - **Vrijen's Context**: Token-based model; 50% discount via referral code; compute credits for architects
   - **Status**: RESOLVED (business model visible)

8. **Who is Zo Good For?**
   - **Question**: What's the target customer?
   - **Vrijen's Answer**: "Someone that just loves AI so much and loves trying out tools... wants to build out workflows... someone that wants customization and close control of things"
   - **Status**: RESOLVED (not a universal product; niche positioning)

## Research & Verification Needed Post-Call

**For Vrijen/Zo Team to Provide**:
- [ ] Secret key management documentation/security model
- [ ] Quality of life roadmap (chronological ordering, etc.)
- [ ] Integration documentation for email tools (Cora, etc.)
- [ ] Pricing calculator tool for token consumption estimate
- [ ] Case studies or metrics on adoption ROI

**For Gabby to Verify**:
- [ ] Check Fortune Business Insights URL: Does the article actually exist? [Likely hallucinated]
- [ ] Test source verification discipline on next research report
- [ ] Document which sources checked out vs. fabricated

**For Group to Explore**:
- [ ] Evaluate Zo vs. Cora/Superhuman integration for workflows
- [ ] Test deep research prompt on their own topic areas
- [ ] Measure actual time investment vs. perceived value (spreadsheet?)

## Follow-up Conversation Topics

1. **Security Deep Dive**: Schedule call to review Zo's secret management and data isolation model
2. **Research Workflow**: Gabby + Vrijen to discuss source validation discipline and prompt tuning
3. **Email Integration**: Clarify what's possible with Cora, Gmail, other tools
4. **Adoption Metrics**: How do we know Zo is worth the investment? What's the ROI signal?
