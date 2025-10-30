## PRODUCT_IDEA_EXTRACTION

---
**Feedback**: - [ ] Useful
---

### Feature/Product Ideas Discussed

**1. Job Distribution via Email (Direct-to-Lensa Routing)**
- Description: Distribute Lensa's 25M jobs to Careerspan users via email, with apply links routing directly to Lensa registration flow (not Careerspan native apply)
- Rationale: Solves two problems simultaneously—clean job data for Careerspan (vs. scraping), and high-quality user acquisition for Lensa. Enables CPC revenue model.
- Source: Mai suggested, Vrijen agreed (13:02): "distribute jobs via email to Lensa... we'll route it to Lensa"
- Confidence: HIGH—explicitly agreed to implement, starting October test

---

**2. Segmented Job Feeds by Category/Geography**
- Description: Instead of full 25M job firehose, receive targeted feeds filtered by job category (product roles) and geography (Boston/SF/NY), with freshness filter (≤3 days old)
- Rationale: Matches Careerspan's current processing capacity (70-80 jobs/week) and user base distribution. Prevents overwhelming V1 matching system while still delivering relevant opportunities.
- Source: Mai offered (10:57): "we can cut down our files just so you're not processing a few million jobs at a time... test with those and slowly expand"
- Confidence: HIGH—Lensa confirmed ability to segment, Vrijen accepted eagerly

---

**3. Multi-Channel Integration Options (XML, API, Co-Reg)**
- Description: Flexible technical integration: XML feeds via Appcast (primary), API for programmatic pulls, or co-registration flow where Careerspan users opt into Lensa job alerts
- Rationale: Gives Careerspan flexibility to choose integration method based on technical constraints and user experience preferences
- Source: Mai outlined options (06:23): "XML feeds through Appcast... jobs API... or co registration"
- Confidence: MEDIUM—options presented, but XML/Appcast selected as primary path. API and co-reg remain available if XML underperforms.

---

**4. Progressive Expansion Path (Product → Engineering → Growth)**
- Description: Start with product roles only, expand to engineering and growth roles within 3 months as Careerspan's matching capacity and user base grows
- Rationale: Staged rollout aligns with Careerspan's community acquisition pace (200-400 users/week starting next week) and avoids overcommitting before proving product-market fit
- Source: Vrijen outlined (10:57), Mai accommodated: "test with those and slowly expand out to the other industries as you expand"
- Confidence: MEDIUM—timeline stated but not contractually committed. Dependent on test success and Careerspan's technical scaling.

---

**5. Always-On Engagement Model (Career Story Logging Beyond Job Search)**
- Description: Users engage with Careerspan monthly for career reflection/story logging independent of job search status, creating "always job-ready" positioning
- Rationale: Addresses job board churn problem—gives users reason to stay engaged even when not actively searching, potentially increasing LTV vs. typical job board traffic
- Source: Vrijen emphasized (15:08): "we give people a reason to engage beyond just the job search... you log the story, you're up to date"
- Confidence: HIGH—core to Careerspan's value prop and positioning with Lensa. Already implemented feature, not new build.

---

**6. High-Engagement Matching (Quality Over Volume)**
- Description: Tightly match users to jobs (resulting in 75-80% open rate, 15-16% CTR) rather than broad distribution, even if means lower CPC volume
- Rationale: Superior engagement metrics attract premium partners willing to pay for quality traffic; differentiates from commodity job board distribution
- Source: Vrijen positioned (08:51): "if we're evaluating purely on CPC basis, we may not look so hot... but we try to send folks that are highly likely to enter into that pipeline"
- Confidence: HIGH—Lensa explicitly accepted tradeoff, willing to test quality-focused approach
