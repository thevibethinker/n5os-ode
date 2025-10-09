# Decisions: Alex Coaching Session

## Strategic Decisions

### 1. Product-First Staffing Focus
**Decision**: Target product manager roles exclusively (initially) in NY, SF, Boston

**Rationale**:
- PM hiring is "insanely varied" - candidates come from diverse backgrounds
- Career transitions, IC contributors, varied paths make it chaotic to hire
- Perfect match for Careerspan strength: surfacing atypical profiles with rich context
- Easier to establish proof of concept in focused vertical than broad staffing

**Impact**: High  
**Reversibility**: Medium (can expand to other roles after proof)  
**Owner**: Vrijen + Logan  
**Finalized**: 2025-09-24

---

### 2. "Playing Card" UI for Candidate Presentation
**Decision**: Replace long-form candidate descriptions with visual "sports card" format

**What It Means**:
- One card per candidate: picture (smaller), name, 2-3 experience bullets, 2-3 story bullets
- One sentence per bullet point maximum
- Categorize candidates thematically ("Clear Fits", "Hidden Gems") not by percentage score
- Show trade-offs: 3-5 strengths + 3-5 weaknesses per candidate

**Rationale** (from Alex's experience as hiring manager):
- Long text descriptions don't get read ("too long")
- Hiring managers want digestible info to decide whether to dig deeper
- Resume bullet points are boring and blend together
- Stories are more interesting and differentiated
- Percentage fit scores feel algorithmic/corporate, not curated

**Impact**: High (core UX change)  
**Reversibility**: High (UI layer only)  
**Owner**: Vrijen (design) + Logan (implementation)  
**Finalized**: 2025-09-24

---

### 3. URL-Based Candidate Bundles
**Decision**: Host candidate packs on unique URLs, not PDFs or email attachments

**Benefits**:
- Track engagement metrics (click-through rate, profiles viewed, time spent)
- Tell complete story on one webpage (intro + cards + CTA)
- Update dynamically without resending files
- Create conversion funnel with anonymization

**Implementation**:
- Each URL is unique per employer/job
- Contains 10-30 candidates depending on quality
- Sandwich structure: context at top, cards in middle, CTA at bottom

**Impact**: Medium (enables metrics, improves experience)  
**Reversibility**: High  
**Owner**: Logan (build), Vrijen (content strategy)  
**Finalized**: 2025-09-24

---

### 4. Target Hiring Managers, Not HR
**Decision**: Direct outreach to team leads/engineering managers, bypass HR/talent departments

**Rationale** (from Alex's experience):
- HR likes their normal ATS process - it's their job security
- Hiring managers are burned out from resume review, want digestible info
- Managers have authority to skip people from ATS directly
- More receptive to human-centric, curated approach
- Careerspan is effectively doing HR's filtering job anyway

**Tactics**:
- Look for job postings that list actual hiring manager
- Send URL with "here are candidates" - goods upfront, no relationship building first
- Test newly posted jobs (engaged manager) vs. month-old jobs (burned-out manager)

**Impact**: High (changes ICP and outreach strategy)  
**Reversibility**: High (can always test HR later if this doesn't work)  
**Owner**: Vrijen  
**Finalized**: 2025-09-24

---

### 5. "Goods Upfront" Outreach Approach
**Decision**: Send candidate bundle immediately in first contact, don't establish relationship first

**Rationale** (from Alex as hiring manager receiving recruiter emails):
- Recruiters who tried to "establish relationship first" were ignored
- "I don't want to start a conversation with every recruiter that reaches out"
- "I want to see your candidates. That's all I care about."
- "I have no idea who you are and once I start talking you'll never leave me alone"

**Anti-Pattern to Avoid**:
- Long introductory emails about Careerspan
- Trying to schedule discovery calls before showing candidates
- "Establishing relationship" before demonstrating value

**New Approach**:
- Email: Minimal copy + URL to candidate bundle
- URL tells full story (what Careerspan is, why these candidates, CTA)
- "Here are candidates. If you like them, we can talk. If not, no problem."

**Impact**: High (fundamentally changes outreach tone and conversion funnel)  
**Reversibility**: High (copy/approach change only)  
**Owner**: Vrijen  
**Finalized**: 2025-09-24

---

### 6. Thematic Categorization Over Percentage Scores
**Decision**: Group candidates as "Clear Fits" / "Hidden Gems" instead of "75% match"

**Rationale**:
- Percentage scores feel algorithmic, corporate, not curated
- "If I see percentage fit scores, I'm like, an algorithm did this. It might just be bullshit."
- Thematic categories feel more human-centric and trust-building
- "More engaged with this list you gave me" when it feels curated

**Categories**:
- **Clear Fits**: Obviously strong on paper, meet all key criteria
- **Hidden Gems**: Career transitions, non-obvious but strong - "people you'll miss if not thinking carefully"
- Include trade-offs for transparency (strengths + weaknesses)

**Impact**: Medium (UX and positioning)  
**Reversibility**: High (presentation layer)  
**Owner**: Vrijen + Head of AI  
**Finalized**: 2025-09-24

---

### 7. Candidate Anonymization in Initial Bundle
**Decision**: Hide candidate names/contact info until employer signs on or pays

**What's Shown Initially**:
- Picture
- First name only (maybe - TBD if too revealing with employment history)
- Blurb / summary
- Stories and experience highlights

**What's Hidden**:
- Full name
- Contact information
- Full resume (maybe)

**Rationale**:
- Protects candidates from being contacted outside Careerspan
- Creates conversion point (pay to unlock)
- "Employers pay way more than candidates" - prioritize their conversion
- Still enough info to assess interest and fit

**Impact**: Medium (affects both candidate trust and employer conversion)  
**Reversibility**: High  
**Owner**: Logan (implementation), Vrijen (policy)  
**Finalized**: 2025-09-24

---

### 8. Pricing Model: Warm Intro Fee
**Decision**: Charge $300-400 per warm intro, subscription model comes later after proof

**Current State**:
- Companies have agreed to pay per warm intro
- Subscription interest is contingent on "show me at least one good candidate"
- Don't have enough qualified candidates in NY/Boston yet to prove out

**Strategy**:
- Use warm intro model to establish proof
- Build candidate pool through magic link jobs + community partnerships
- Move to subscription once trust and quality established

**Impact**: High (revenue model)  
**Reversibility**: Medium (easier to go intro → subscription than reverse)  
**Owner**: Vrijen  
**Finalized**: 2025-09-24 (confirmed existing direction)

---

## Confidence Level Decisions

### High Confidence
- Playing card UI (Alex validated strongly from hiring manager experience)
- Goods upfront outreach (Alex's direct pain point as recipient)
- Target hiring managers not HR (Alex's clear preference)

### Medium Confidence  
- Product manager focus (good rationale, but narrow)
- URL-based delivery (logical, but untested)
- Anonymization strategy (need to test how much to hide)

### Requires Testing
- Newly posted vs. month-old job timing (two competing hypotheses)
- Exact data points on each candidate card (iterate with real users)
- Whether to show resume at all in initial bundle

---

## Decisions NOT Made (Require More Information)

1. **Exactly what goes on each candidate card** - needs user research and iteration
2. **Resume visibility** - show in initial bundle or only after payment?
3. **How much anonymization** - first name only? Or even more restricted?
4. **Employer UI vs. manual sends** - build platform view for employers or keep manual for now?
5. **Optimal timing** - new jobs vs. old jobs for outreach
6. **Geographic expansion** - when to expand beyond NY/SF/Boston

---

## Alignment Check

**What Vrijen Was Already Doing**:
- Product manager focus ✓
- Magic link system for jobs ✓
- Warm intro pricing model ✓
- Community partnerships ✓

**What Alex Redirected/Refined**:
- How to present candidates (card format, not long descriptions)
- Who to target (hiring managers, not HR)
- How to reach out (goods first, not relationship building)
- How to categorize (themes, not percentages)

**Net Effect**: Tactical refinement of execution, not strategic pivot. Alex validated strategy and improved go-to-market tactics.
