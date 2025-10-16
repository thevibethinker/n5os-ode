## STAKEHOLDER_RESEARCH

---
**Feedback**: - [ ] Useful
---

**Perspective**: Speaking as AI application builder / technical founder (Careerspan co-founder working with engineer Ilsa)

### Industry Landscape Insights

#### 1. Model provider lock-in is real and expensive to escape
- **Evidence**: "Anyone that tells you can just swap models around is a goddamn liar. So I really need to communicate this because this really almost like fucked us several times... we saw dramatically worse results switching from OpenAI to Gemini. And that's not because [Gemini is worse], it completely like the fact that it uses react versus whatever is like OpenAI's like strategy for models completely wrecks the outputs."
- **Why it matters**: Switching costs are architectural, not just API-level - different reasoning frameworks (React vs OpenAI's approach) break prompt engineering assumptions, making provider migration high-risk once you've built complex agentic workflows.
- **Signal strength**: ● ● ● ● ○ (4/5 - firsthand painful experience, specific technical mechanism identified)
- **Category**: Product Strategy
- **Source credibility**:
  - **Stakeholder**: Jaya Pokuri (see B08 for full profile)
  - **Relevant experience**: Co-founded Careerspan, scaled to 1K+ users with heavy LLM usage (past OpenAI tier 5), attempted production migration OpenAI → Gemini
  - **Source type**: PRIMARY (direct operational experience, not hearsay)
  - **Firsthand?**: Yes - "almost fucked us several times" indicates personal experience with failed migration
  - **Weight justification**: High weight - specific failure mode identified (React framework difference), real business impact quantified (couldn't switch despite material cost savings opportunity)

#### 2. Token cost matters less than net task cost at scale
- **Evidence**: "Don't just look at the token prices, look at the all in price for running benchmarks for a model... some models that are seemingly cheap actually huge token hoard. So they will absolutely eat up your tokens."
- **Why it matters**: Advertised per-token pricing is misleading - some "cheap" models generate 3-5x more tokens per task than expensive models, resulting in higher total cost. Evaluation strategy should benchmark full task completion cost, not unit economics.
- **Signal strength**: ● ● ● ○ ○ (3/5 - solid practitioner insight but commonly known in AI circles)
- **Category**: Product Strategy
- **Source credibility**:
  - **Stakeholder**: Jaya Pokuri
  - **Relevant experience**: Careerspan scaled to tier 5 OpenAI usage, obsessed with token optimization due to high per-user data consumption
  - **Source type**: PRIMARY (lived experience optimizing production costs)
  - **Firsthand?**: Yes - "we saw" and references to Open Arena benchmarks suggest active research/testing
  - **Weight justification**: Medium-high weight - practical operational knowledge, though insight is somewhat obvious to experienced builders

#### 3. B2B AI pricing is inelastic if accuracy matters
- **Evidence**: "Harvey can charge like half a million to law firms because they're price inelastic... You can actually burn more tokens and be less efficient than you need to because your end user is price inelastic and still deliver a higher quality product."
- **Why it matters**: Healthcare and legal AI can optimize for quality over cost because customer willingness-to-pay is driven by accuracy/risk-mitigation, not cost-per-query. This inverts typical startup optimization priorities (can throw GPT-4 at problems instead of obsessing over GPT-4-mini savings).
- **Signal strength**: ● ● ● ● ○ (4/5 - counterintuitive strategic insight with specific example)
- **Category**: GTM Strategy
- **Source credibility**:
  - **Stakeholder**: Jaya Pokuri
  - **Relevant experience**: Building career tech product (adjacent to Bonfire's healthcare vertical - both regulated, high-stakes domains)
  - **Source type**: SECONDARY (Harvey example is public knowledge, but application to healthcare is strategic inference)
  - **Firsthand?**: No - Harvey pricing is market observation, not firsthand experience
  - **Weight justification**: Medium weight - smart strategic reasoning but not unique insider knowledge; treat as hypothesis to validate with healthcare sales data
