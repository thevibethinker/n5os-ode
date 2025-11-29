---
created: 2025-11-15
last_edited: 2025-11-15
version: 1
meeting_id: 2025-11-XX_Aviato_Demo
calendar_event_id: gfvlil3aqjqfie9p4u2238g8j8
attendees:
  - konrad@aviato.co
  - austin@aviato.co
  - vrijen@mycareerspan.com
meeting_type: product_demo
---
# Aviato Demo - Meeting Intelligence

## B01_DETAILED_RECAP

**Meeting Overview:**
Product demo and exploration meeting between V (Careerspan founder) and Aviato team (Konrad - co-founder, Austin - growth lead). V explored Aviato's data enrichment API for both personal CRM use via Zo and potential Careerspan integration.

**Key Discussion Points:**

1. **V's Use Cases:**
   - Personal: Building automated meeting intelligence pipeline with Zo that enriches contacts via LinkedIn, extracts stakeholder intelligence, and identifies networking opportunities
   - Professional: Exploring Aviato integration for Careerspan to enable better cold outreach and networking recommendations for candidates

2. **Aviato Platform Capabilities:**
   - **Scale:** 1.1 billion people profiles, 72 million companies
   - **Data Points:** Extensive coverage including vesting data, LinkedIn open-to-work signals, salary estimates, contact info, company data, Twitter database
   - **Delivery Methods:** API and flat files
   - **Refresh Cadence:** 2-5 day default for API (tiered: executives/founders first, then managers, entry-level, frontline workers)
   - **Query Options:** Single person lookup OR list creation with criteria in one API call
   - **Incremental Updates:** Can send just diffs for flat files stored client-side

3. **Customer Segments:**
   - 30% VCs/PE/family offices (investment insights, predicting founders going stealth)
   - 50% AI agents/tools (heavy recruitment use case)
   - Wholesaler for niche data providers (e.g., Firmable for Southeast Asia)

4. **Recruitment Intelligence Features:**
   - **Vesting data:** Identify executives/founders/engineers at equity cliff (4-year mark = high likelihood of exploring options)
   - **LinkedIn open-to-work signals:** Access hidden subset who are open but don't display green banner
   - **Movement signals:** Detect people who ended role but haven't started new one within 3 months

5. **Careerspan Integration Opportunity:**
   - V identified potential to use vesting data to proactively reach high-value candidates when they have negotiating leverage
   - Pitch: "Store your stories while you have momentum" + connect to top employers in Careerspan network
   - Careerspan advantage: Pro-candidate tool with 3-5% organic reactivation rate, 20-25 minute story deposits providing deep qualitative data

6. **Zo Integration Potential:**
   - V excited about using Aviato to replace Apollo for personal networking
   - Use cases: Track promotions in network, enrich meeting contacts, identify introduction opportunities
   - V recently set up n8n instance on Zo with one click, unlocking API integration capabilities

**Technical Details:**
- API access provided via key, configured with specific data sets/points needed
- Pricing based on: (1) data set volume, (2) specific data points (weight), (3) refresh cadence
- Test account: 100 people + 100 company credits, no time limit

**Mutual Introductions:**
- V offered to introduce Aviato team to Zo founders (Ben and Rob)
- V plans to feature Aviato integration in Zo Discord community
- Austin to send V API key to vrijen@mycareerspan.com

**Personal Context:**
- Austin splits time between Miami and Toronto, occasional NYC visits (formerly lived there)
- V based in Brooklyn, traveling to Jacksonville for friend's wedding
- Company naming: Aviato (trademarked t-shirts only), Bakchanity holding company secured

## B02_COMMITMENTS

**Austin (Aviato):**
- [✓ COMPLETED IN MEETING] Send API key to vrijen@mycareerspan.com
- [✓ COMPLETED IN MEETING] Send data documentation showing all supported data points
- Provide 100 people + 100 company test credits (no time limit)
- Open to increasing test credits if needed for proper evaluation

**V (Careerspan/Personal):**
- Introduce Aviato team to Zo founders (Ben and Rob)
- Test Aviato API integration with Zo on flight to Jacksonville
- Share use cases and feature Aviato in Zo Discord community
- Follow up after testing period

## B03_STAKEHOLDER_INTEL

**Konrad - Aviato Co-founder**
- Email: konrad@aviato.co
- Role: Co-founder
- Context: Technical/product focus (inferred from Austin leading demo)

**Austin - Aviato Growth Lead**
- Email: austin@aviato.co
- Role: Leads all things growth
- Location: Splits time between Miami and Toronto, occasional NYC visits
- Background: Formerly lived in New York
- Company Knowledge: Deep expertise in data enrichment use cases across VC, recruitment, AI agent segments
- Communication Style: Thorough, consultative, generous with trial access

**Company Intel:**
- Strong Silicon Valley connection via customer base (many YC companies)
- Brand: Silicon Valley TV show reference (Aviato) serving them well
- Holding company: Bakchanity (also Silicon Valley reference)
- Market positioning: Wholesaler + direct API provider
- Recent additions: Twitter database, expanding data points continuously

## B04_DECISIONS_MADE

1. **V will test Aviato API** via Zo integration for personal CRM use case first
2. **Test account provisioned** with 100 people + 100 company credits to evaluate platform
3. **Mutual introductions agreed:** V connects Aviato to Zo founders, explores community cross-pollination
4. **Careerspan integration deferred** to post-testing phase - validate personal use case first before commercial integration

## B05_STRATEGIC_IMPLICATIONS

**For V/Careerspan:**
1. **Recruitment AI differentiation:** Combining Aviato's quantitative signals (vesting, open-to-work) with Careerspan's qualitative depth (20-25 min stories) could create unique "talent agency" positioning
2. **Proactive outreach opportunity:** Target high-value candidates at equity cliffs before they start job search - first-mover advantage
3. **API infrastructure unlock:** Zo + n8n + Aviato = V can now build sophisticated workflows without technical dependency
4. **Personal CRM enhancement:** Meeting intelligence pipeline + Aviato enrichment = automated stakeholder intelligence system

**For Aviato:**
1. **New customer segment:** Solo founders/productivity enthusiasts in Zo community represent untapped market
2. **Qualitative data gap:** Aviato provides quantitative signals; Careerspan provides qualitative depth - potential partnership/integration value
3. **AI agent ecosystem:** Zo's API-first approach aligns with Aviato's 50% AI agent customer base

**Market Insight:**
- Recruitment intelligence moving from manual research to predictive signals (vesting data, hidden open-to-work flags, movement patterns)
- API-first data providers enabling non-technical founders to build sophisticated workflows
- Convergence of qualitative (conversational AI) and quantitative (data enrichment) approaches in recruitment tech

## B06_QUESTIONS_RAISED

**Technical:**
1. What are Aviato's coverage/accuracy rates for vesting data across different company sizes?
2. How does refresh cadence pricing work - what's the cost delta between 2-day vs 5-day refresh?
3. Can Aviato data be queried via n8n nodes or requires custom API integration?

**Strategic:**
1. What's the optimal way to combine Aviato's quantitative signals with Careerspan's qualitative data for candidate outreach?
2. Should Careerspan build vesting-based outreach as primary acquisition channel or supporting feature?
3. How do other Aviato customers handle compliance/privacy for proactive candidate outreach?

**Commercial:**
1. What's typical pricing structure for small team/startup usage beyond test credits?
2. Are there volume discounts for combining personal + commercial use cases?
3. What's the path from test account to production deployment?

## B07_RISKS_OPPORTUNITIES

**Opportunities:**
1. **First-mover advantage:** Proactive vesting-based outreach for Careerspan could differentiate in crowded recruitment tech market
2. **Network effects:** V's Zo evangelism + Aviato integration = potential customer acquisition channel for both platforms
3. **Personal productivity showcase:** V's meeting intelligence pipeline could become Zo/Aviato case study
4. **Qualitative + quantitative convergence:** Unique positioning combining deep candidate stories with predictive signals

**Risks:**
1. **Privacy/compliance concerns:** Proactive outreach to vesting employees may trigger legal/ethical questions
2. **Data accuracy dependency:** Careerspan value prop relies on Aviato data quality - need validation
3. **Cost structure unknown:** Test credits are generous but production pricing could be prohibitive for early-stage startup
4. **Technical complexity:** Despite Zo's accessibility, API integration still requires learning curve for non-technical founder
5. **Scope creep:** V juggling personal CRM build + Careerspan integration + Zo evangelism - risk of diluted execution

## B08_ACTION_ITEMS

**Immediate (Next 48 hours):**
- [ ] **V:** Test Aviato API key on flight to Jacksonville
- [ ] **V:** Draft introduction email connecting Aviato team to Zo founders
- [ ] **V:** Document initial Aviato + Zo integration architecture

**Short-term (Next 2 weeks):**
- [ ] **V:** Build personal CRM proof-of-concept with Aviato enrichment
- [ ] **V:** Write Zo Discord post showcasing Aviato integration use cases
- [ ] **V:** Evaluate Aviato data quality/coverage for Careerspan target personas
- [ ] **V:** Document 3-5 specific use cases for Careerspan + Aviato integration

**Medium-term (Next 30 days):**
- [ ] **V:** Request pricing proposal for Careerspan commercial deployment
- [ ] **V:** Build prototype: Vesting-based candidate outreach workflow
- [ ] **V:** Analyze legal/compliance requirements for proactive recruitment outreach
- [ ] **V:** Schedule follow-up with Austin to discuss commercial integration

**Long-term (30+ days):**
- [ ] **V:** Decide on Careerspan integration priority vs other product initiatives
- [ ] **V:** Build case study if personal CRM implementation successful

## B09_FOLLOW_UP_REQUIRED

**With Aviato:**
- After test period: Commercial pricing discussion for Careerspan use case
- After proof-of-concept: Deep dive on vesting data accuracy and coverage
- Ongoing: Feedback loop on API experience and feature requests

**With Zo Founders:**
- Introduction email connecting to Aviato team
- Share Aviato integration as community showcase
- Discuss potential formal partnership/integration

**Internal:**
- Evaluate Careerspan product roadmap priority for Aviato integration
- Research compliance requirements for vesting-based outreach
- Document learnings from personal CRM build for team knowledge base

## B10_CONTEXT_CONNECTIONS

**Related to V's Existing Projects:**
- **Zo meeting intelligence pipeline:** Aviato becomes enrichment layer in automated contact intelligence system
- **Careerspan positioning:** Validates thesis that qualitative data (stories) + quantitative signals (Aviato) = superior candidate insights
- **Personal productivity system:** Another API integration building V's "non-technical founder who builds technical systems" capability

**Broader Market Themes:**
- **AI agent economy:** Both Zo and Aviato enabling solo founders to build sophisticated automation
- **Data enrichment commoditization:** API-first providers making enterprise capabilities accessible to individuals
- **Recruitment tech evolution:** From job boards → ATS → conversational AI + predictive signals

**Network Connections:**
- Zo community = potential Aviato customers (solo founders, productivity enthusiasts)
- YC network overlap (Aviato serves many YC companies, V connected to YC ecosystem)
- Careerspan + Aviato could create unique talent agency positioning in market

**Technology Stack:**
- Zo (AI workspace) + n8n (workflow automation) + Aviato (data enrichment) = complete non-technical founder toolkit
- Demonstrates thesis that API economy enables non-engineers to build production systems

## METADATA

**Meeting Classification:** Product Demo, Partnership Exploration
**Relationship Stage:** First Meeting → Test Phase
**Next Milestone:** V completes API testing and reports back
**Strategic Priority:** Medium-High (personal productivity) + TBD (Careerspan integration pending test results)
**Key Topics:** Data enrichment, recruitment intelligence, API integration, personal CRM, AI agents

