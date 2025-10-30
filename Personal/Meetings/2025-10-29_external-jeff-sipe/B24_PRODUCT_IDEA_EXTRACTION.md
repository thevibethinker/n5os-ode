# B24: Product Ideas & Feature Requests

## Ideas from Jeff (Direct or Implied)

### IDEA 1: Agency Dashboard / Reporting
**Source**: Implied from agency use case discussion  
**Need**: Recruiting agencies would need visibility into:
- Active roles posted through Careerspan
- Candidate pipeline per role (volume, quality indicators)
- Candidate progression (viewed, applied, interviewed)
- Placement status and commission tracking

**Priority**: HIGH - Essential for agency pilots

**Rationale**: Agencies manage multiple roles simultaneously. They need self-service visibility rather than requesting updates from Careerspan team. This is table-stakes for agency adoption.

---

### IDEA 2: Multi-Role Management for Single Agency
**Source**: Implied from "they'll bring you a role" → likely will bring multiple roles  
**Need**: Agency can manage 5-10+ concurrent roles through single Careerspan account
- Bulk posting capabilities
- Role-level tracking and analytics
- Different magic links per role for attribution

**Priority**: HIGH - Required before scaling beyond single-role pilots

**Rationale**: Current magic linking is one-off per founder. Agencies will want to post multiple roles simultaneously and track performance independently.

---

### IDEA 3: White-Label or Agency-Branded Experience
**Source**: Implied from "they want refined gold" positioning  
**Need**: Candidates might see "Powered by Careerspan" but agency should be primary brand in candidate experience
- Agency logo on posting pages
- Agency contact info for follow-up
- Seamless hand-off when candidate is qualified

**Priority**: MEDIUM - Nice to have for initial pilots, required for scale

**Rationale**: Agencies have their own brands and client relationships. They won't want candidates thinking Careerspan is the employer or recruiter. Need to position as backend infrastructure.

---

### IDEA 4: Commission Tracking & Payment Integration
**Source**: Implied from commission-split business model  
**Need**: Automated tracking of:
- Which candidates came through Careerspan
- Placement confirmations (hired = yes/no)
- Commission amounts owed to Careerspan
- Payment reconciliation

**Priority**: HIGH - Required before any commission-based deals

**Rationale**: Manual tracking of commission splits will break at scale. Need system to attribute placements to Careerspan pipeline and calculate payouts automatically.

---

### IDEA 5: Experience-Based Profile Quality Indicators
**Source**: Jeff's insight on "harder to deceive mechanism"  
**Enhancement**: Surface profile quality signals to agencies
- Profile completeness score
- Experience verification indicators
- Activity/engagement signals
- "Hardness to fake" confidence score

**Priority**: MEDIUM - Differentiator but not blocking

**Rationale**: Jeff identified experience-based profiles as Careerspan's moat vs. resume-based competitors. Make this visible to agencies so they understand WHY Careerspan candidates are higher quality. This becomes selling point.

---

### IDEA 6: Marketplace Features (Long-term)
**Source**: Jeff's vision of "pit recruiters against each other for top talent"  
**Future State**: 
- Top talent can see which agencies/companies are interested
- Agencies can "bid" or compete for candidate attention
- Platform facilitates matching from both sides
- Commission flows from both agency and talent (like talent agents)

**Priority**: LOW - 12-18+ month roadmap

**Rationale**: This is the strategic endgame Jeff envisions. Not for immediate build, but should influence architecture decisions today. If we build agency-only features now, are we painting ourselves into corner for future two-sided marketplace?

---

## Ideas from Vrijen (Not in Meeting, But Inspired By It)

### IDEA 7: Agency Performance Analytics
**Not discussed, but logical next step**  
**Need**: Show agencies how Careerspan pipeline compares to their other sourcing channels
- Time to placement (Careerspan vs. LinkedIn vs. referrals)
- Quality of candidates (interview-to-offer ratio)
- Cost per placement comparison

**Why Valuable**: Agencies will want proof that Careerspan channel is worth commission split. Need data to show ROI.

---

### IDEA 8: Candidate Quality Filtering Preferences
**Not discussed, but implied by "refined gold" positioning**  
**Need**: Let agencies set filtering thresholds
- Minimum years experience
- Required skills/technologies
- Geographic requirements
- Compensation expectations alignment

**Why Valuable**: "Refined gold" means different things to different agencies. Some want senior-only; some want mix. Configurability ensures we deliver what each agency considers "refined."

---

## Product Principles Validated by Conversation

**✓ Quality Over Quantity**: Jeff confirmed agencies are drowning in unqualified leads. Careerspan should optimize for candidate quality (fewer, better matches) vs. volume (more, lower quality).

**✓ Experience-Based vs. Resume-Based**: This is the defensible moat. Double down on making experience profiles harder to fake and richer in signal.

**✓ Platform Infrastructure Mindset**: Jeff's long-term vision is marketplace. Even if building for agencies today, architecture should enable two-sided marketplace tomorrow.

**✓ Self-Service Where Possible**: Agencies won't want to email Careerspan for every update. Build for agency autonomy from day one.

---

## Open Product Questions

**Q1**: Should we build agency features into current magic linking product, or separate "agency edition"?

**Q2**: How much manual curation is acceptable in initial agency pilots vs. what must be automated?

**Q3**: What's minimum viable dashboard for agency pilot? (Don't over-build before validating model)

**Q4**: How do we prevent agencies from using Careerspan to identify candidates, then circumventing platform to avoid commission? (Need candidate tracking/attribution system)
