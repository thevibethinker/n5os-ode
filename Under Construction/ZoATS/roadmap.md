# ATS-in-a-Box: Feature Roadmap

**Last Updated**: 2025-10-21 22:00 EST  
**Timeline**: MVP (tonight → 2 weeks), then iterative expansion

---

## Now (MVP - Night 1 → Week 2)

### Core Infrastructure
- [ ] Email ingestion (Gmail integration)
- [ ] Resume parsing (PDF/DOCX → structured JSON)
- [ ] Candidate file generation (markdown + JSON)
- [ ] Multi-job support (concurrent job postings)
- [ ] Rubric builder (text input, Socratic conversation)

### Intelligence Layer
- [ ] Quick-test filter (deal-breaker detection)
- [ ] AI-generation likelihood scoring
- [ ] Uniqueness/specificity scoring across applicants
- [ ] Clarifying question generator (personalized per candidate)
- [ ] Email response handling (48h async screening)
- [ ] LinkedIn cross-reference (basic validation)
- [ ] Simulated panel interview (multi-persona scoring)

### Founder Experience
- [ ] Founder digest automation (top 3-5 candidates, rationale)
- [ ] Bulk email drafting (BCC-ready candidate lists)
- [ ] Voice note ingestion for rubric building
- [ ] Manual finalist selection interface

### Business
- [ ] 2-week free trial setup
- [ ] Pricing integration (Zo subscription)
- [ ] Basic testimonial collection

---

## Next (Phase 2: Advanced Intelligence)

### Depth of Analysis
- [ ] Database migration (when candidates >100 per job)
- [ ] News cross-reference (validate newsworthy claims)
- [ ] GitHub/portfolio analysis (for technical roles)
- [ ] Pattern library of AI-generated application styles
- [ ] Candidate work sample analysis (not just resume)
- [ ] "Showcase different sides" prompts (unique interests, perspectives)

### Ultra-Signal Detection
- [ ] Self-taught skill identification
- [ ] Non-traditional background achievement scoring
- [ ] Passion authenticity vs. performance detection
- [ ] Deep work evidence vs. resume optimization

### Multi-Candidate Analysis
- [ ] Cohort comparison reports ("this candidate vs. your pool")
- [ ] Trending uniqueness insights ("most unique rationales this week")
- [ ] Competitive intelligence ("similar candidates applied to X, Y, Z")

---

## Later (Phase 3: Bias Mitigation)

- [ ] Resume anonymization pipeline
- [ ] Sanitized resume generation (for AI evaluation)
- [ ] Blind screening mode (founder sees scores before identities)
- [ ] Bias audit reports (demographic analysis, if data available)
- [ ] Fairness calibration (adjust rubric if systematic bias detected)

---

## Future (Phase 4: Team Collaboration)

- [ ] Multi-stakeholder rubric building (co-founders, advisors)
- [ ] Voice message ingestion from multiple team members
- [ ] Collaborative candidate evaluation (shared notes, voting)
- [ ] Interview scheduling integration
- [ ] Hiring pipeline dashboard (stages, bottlenecks)
- [ ] Team consensus scoring (weighted by role/expertise)

---

## Growth (Phase 5: Lead Magnet Optimization)

### Careerspan Integration
- [ ] Testimonial collection automation
- [ ] Case study generation (successful hires)
- [ ] Upsell workflows (Careerspan coaching for finalist interviews)
- [ ] Referral incentives (founders invite other founders)

### Distribution
- [ ] Public landing page (ats.careerspan.com?)
- [ ] Demo video (show intelligence in action)
- [ ] Founder community (hiring best practices)
- [ ] Integration marketplace (Slack, Notion, etc.)

---

## Exploratory (Phase 6: Novel Capabilities)

### Candidate-Side Innovation
- [ ] Candidate self-service portal (check status, update info)
- [ ] "Why I'm unique" freeform field (encourage authenticity)
- [ ] Portfolio upload (beyond resume)
- [ ] Video introduction option (async, optional)

### Employer-Side Innovation
- [ ] Job description optimizer (AI suggests improvements)
- [ ] Salary benchmarking (based on rubric requirements)
- [ ] Hiring velocity predictions (time-to-fill estimates)
- [ ] Culture fit simulator (test candidate scenarios)

### Market Expansion
- [ ] Talent pool curation (passive candidate sourcing)
- [ ] Reverse matching (candidates find fitting startups)
- [ ] Hiring playbooks (templates for different roles)
- [ ] API for third-party integrations

---

## Technical Debt & Refactoring

### Scalability
- [ ] Email → API migration (when volume >50/day)
- [ ] Markdown → Database (when candidates >100 per job)
- [ ] Async job processing (background workers for analysis)
- [ ] Caching layer (LinkedIn, news lookups)

### Code Quality
- [ ] Modular plugin architecture (swap AI models, detectors)
- [ ] Comprehensive test suite (unit, integration, end-to-end)
- [ ] Error handling & logging (debugging candidate issues)
- [ ] Performance monitoring (response time, accuracy metrics)

### Security & Privacy
- [ ] Data encryption at rest
- [ ] Candidate data deletion on request
- [ ] Audit trail for all AI decisions
- [ ] GDPR/compliance review

---

## Deferred (Good Ideas, Not Now)

- [ ] Mobile app (founders review candidates on-the-go)
- [ ] Chrome extension (apply from LinkedIn)
- [ ] Slack bot (daily candidate updates)
- [ ] Interview transcript analysis (post-hire feedback loop)
- [ ] Predictive hiring success (ML on past hires)
- [ ] Diversity goals tracking
- [ ] Offer letter generation
- [ ] Onboarding integration

---

## Decision Log

### Why These Priorities?

**MVP focuses on intelligence** because:
- That's the differentiation vs. legacy ATS
- Founders care about quality > quantity of candidates
- AI-generation detection is timely (everyone's resume is ChatGPT now)

**Bias mitigation in Phase 3** because:
- Requires anonymization pipeline (complex)
- MVP needs speed, can't afford added latency
- But it's a strong ethical selling point for Phase 3 marketing

**Database migration in Phase 2** because:
- Most MVP users won't hit 100 candidates
- Premature optimization wastes tonight's build time
- But we need clear migration path (don't want to rebuild)

**Team collaboration in Phase 4** because:
- Employees 1-3 are often solo founder or small team
- Rubric building can be async (voice notes work)
- Real-time collaboration adds UI complexity

---

## Future Capability Alignment Opportunities

### Cross-Feature Synergies
- **Voice notes + Bias mitigation**: Anonymize voice before transcription?
- **Ultra-signals + Predictive success**: Track which signals predicted great hires
- **LinkedIn cross-ref + Talent pool**: Build passive candidate database from validation
- **AI detection + Pattern library**: Crowdsource detection models across users

### Careerspan Service Tie-Ins
- **Finalist interviews**: Upsell to Careerspan coaching
- **Rubric building**: Premium service for complex/senior roles
- **Hiring playbooks**: Consulting engagement for hiring strategy
- **Culture fit**: Workshop to define company values (feeds rubric)

---

## Questions to Resolve

1. **Database choice**: PostgreSQL? SQLite? Stay in markdown longer?
2. **AI model**: Claude? GPT-4? Fine-tuned? Multi-model ensemble?
3. **Email provider**: Gmail API? SendGrid? Postmark?
4. **Pricing**: $50/month? $100? Per-job? Per-candidate?
5. **Bias mitigation**: How aggressive? Trade-off with accuracy?
6. **Candidate experience**: Do they know they're being AI-screened?

---

## North Star Metrics (6 Months Out)

- **100 founders** using ATS-in-a-Box
- **20% conversion** to paid Careerspan services
- **5+ testimonials** of "this changed our hiring"
- **<10% miss rate** (candidates filtered that shouldn't have been)
- **5+ hours saved per founder per week**
- **Built entirely in Zo** (proof of concept for agentic systems)

---

*This roadmap is a living document. Update as we learn.*
