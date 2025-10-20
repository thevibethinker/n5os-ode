## PRODUCT_INTELLIGENCE

---
**Feedback**: - [ ] Useful
---

### Product Vision & Positioning

#### Core Product Concept: "Career Agent for Passive Hiring"
- **What It Is**: Automated agent that monitors opportunities on behalf of top talent and surfaces matches to both candidate + hiring manager
- **What It's NOT**: Active job search tool, resume builder, or candidate-driven discovery platform
- **Key Quote**: "You don't want an agent you want [one] running on your behalf... Servicing opportunities"
- **User Mindset**: "You are an agent, your top talent... You've got this, like working on your behalf"

#### Product Philosophy
- **Design Principle**: Tool should run in background with minimal user effort
- **Target User**: High-quality candidates who aren't actively looking but would move for right opportunity
- **Value Prop**: "Build your for iron manager" - always-on representation to hiring managers
- **Anti-Pattern**: Requiring active engagement or frequent logins (passive by definition)

### Product Architecture & Requirements

#### Skeleton Crew Product Requirements
- **Core Constraint**: Must be maintainable by 2 founders with <10 hrs/week effort
- **Implication**: Strip to essential features, automate everything possible, minimize edge cases
- **V's Acknowledgment**: "The skeleton crew crop product... you and I can then, like, with less pressure... just you and me, like, kind of get out to people"
- **Success Criteria**: Product stays online, processes candidates, surfaces opportunities with minimal manual intervention

#### Three-Sided Marketplace Components

**1. Candidate Side**
- **Input**: Profile, preferences, "what would make me move" criteria
- **Value Delivery**: Opportunities surfaced automatically when they meet threshold
- **Monetization**: Earn placement bonus (~$7K) when hired through Careerspan
- **Retention**: Works in background, so low ongoing engagement required

**2. Hiring Manager Side**
- **Input**: Role description, ideal candidate profile, decision authority
- **Value Delivery**: Vetted candidates from their networks (not random applicants)
- **Privacy**: "We won't share your company [until match]"
- **Monetization**: Pay reduced agency fee (~$10K discount from standard 20%)
- **Quote**: "Hey, now, we give people the ability to surface things directly to the hiring manager. That would be of interest"

**3. Careerspan/Agent Side**
- **Matching Engine**: AI determines fit between candidate profile + hiring manager needs
- **Interest Threshold**: "We can set up an interest threshold... if [AI] didn't feel like did not pass it on to the hiring manager"
- **Human Override**: Hiring managers monitor matches, can engage or pass
- **Revenue Capture**: ~$3K per successful placement (from $20K total fee)

#### Critical Product Features (Must-Have for Skeleton Crew)

**Automated Matching & Surfacing**
- AI evaluates candidate-opportunity fit
- Surfaces to both sides only if threshold met
- Reduces noise for hiring managers, reduces spam for candidates

**Hiring Manager Dashboard**
- View candidate pipeline
- Accept/pass on matches
- Track active roles

**Candidate Agent Dashboard**
- Set preferences ("I'd move for...")
- View surfaced opportunities
- One-click interest expression

**Payment/Fee Infrastructure**
- Track placements
- Split fees (employer discount + candidate bonus + Careerspan cut)
- Handle invoicing/payouts

#### Cost Reduction Requirements (Pre-Skeleton Crew)

**AI Inference Costs**
- **Current State**: Presumably high due to LLM-heavy processing
- **Target**: <$5K/month to fit in $20-25K total OpEx
- **Owner**: Danny + Rockwell to implement before departure
- **Approach**: "Asking Elsa to bring costs down and asking Danny and Rockwell to basically build out stuff to, like, let itself sustain"

**Self-Sustaining Infrastructure**
- **Goal**: Minimal manual intervention required
- **Chad API Arrangement** (mentioned in passing): Potentially Chad covers inference costs in exchange for API access / tax-deductible expense
- **Quote**: "Chad onwards, we basically need to say, can we keep gaining clout if we keep adding people to career span"

### Product Roadmap & Priorities

#### Q4 2025 (Pre-Hibernation)
- **Priority 1**: Cost reduction (inference optimization)
- **Priority 2**: Feature stripping (remove anything high-maintenance)
- **Priority 3**: Self-sustaining automation (reduce manual ops)
- **Priority 4**: Hiring manager pilot (recruit first 5-10 HMs from network)

#### Q1 2026 (Post-Skeleton Crew)
- **Priority 1**: Messaging overhaul ("talent agency" positioning)
- **Priority 2**: Personal brand content (drive candidate inbound)
- **Priority 3**: Hiring manager network growth (expand to 20-30)
- **Priority 4**: First placements (prove model, generate revenue)

#### Q2-Q4 2026 (Optionality Phase)
- **Outcome 1**: If traction → Scale as lifestyle business or sell
- **Outcome 2**: If no traction → Shut down or pivot again
- **Metric**: Can we generate $20-25K/month in placement fees to be self-sustaining?

### Product Insights from Discussion

#### "Ironic" Return to Coaching Roots
- **Logan Quote**: "The irony of this is we started this. Kind of saying that we were career coaches, and we're going to end this saying the full confidence that we are career [coaches]"
- **Implication**: Product should amplify coaching/advisory work, not replace it
- **Integration**: Personal brand (coaching) + proprietary tool (Careerspan) + talent agency (placements)

#### Complexity as Enemy
- **V's Self-Awareness**: "My best attribute is making a plan that's more complicated than it needs to be with less money than you would want"
- **Product Corollary**: Strip complexity, focus on core loop (candidate → match → hiring manager → placement)
- **Logan's Critique**: "At every stage, we were like, no, that's. Let's do that because it would be cool" → Over-engineering pattern

#### Consumer Metrics Transformation
- **Old Model**: Engagement, active users, job applications sent (vanity metrics)
- **New Model**: Quality placements, hiring manager satisfaction, candidate earnings
- **V Quote**: "Our consumer numbers go from looking good. They're looking incredible, because now it's no longer about [high volume]... It's about sporadic, sort of like [high-quality matches]"

---

### Open Product Questions

1. **What features can be cut** to reach skeleton crew maintainability?
2. **How much inference cost reduction** is achievable? (Danny + Rockwell to assess)
3. **What's the MVP hiring manager experience** to pilot with first 5-10?
4. **How to balance candidate expectations** (passive tool) with engagement needed for quality matching?
5. **What's the automated matching algorithm's accuracy threshold** before surfacing to HM?

---

### Product Risks & Mitigations

**Risk 1: Over-Complexity**
- **Mitigation**: Ruthless feature cutting, focus on placement loop only

**Risk 2: Inference Costs Stay High**
- **Mitigation**: Danny + Rockwell cost reduction sprint; Chad API arrangement as backup

**Risk 3: Hiring Managers Don't Engage**
- **Mitigation**: Direct network outreach, personal relationships, quality over quantity

**Risk 4: Candidates Forget About Tool**
- **Mitigation**: Set expectations as "passive" upfront; occasional nudges for profile updates

**Risk 5: Unit Economics Don't Work**
- **Mitigation**: Validate fee split with first placements; adjust if needed
