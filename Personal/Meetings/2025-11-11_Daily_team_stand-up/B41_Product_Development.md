---
created: 2025-11-12
last_edited: 2025-11-12
version: 1.0
block: B41
---

# B41: Product Development Updates

## Employer Portal (Danny)

### Status: ~95% Complete
**Timeline:** Built mostly in "a few days"  
**Current State:** Functional, needs testing with real data

### Completed Features
- Employer user authentication (Firebase, password reset flow)
- Role creation and management interface
- Applicant review dashboard with sorting/filtering
- Individual applicant detail pages with:
  - Overall scoring (hard skills, soft skills, responsibilities)
  - Deal breaker responses
  - Resume viewer (PDF, built-in browser viewer)
  - Applicant notes capability
  - Proceed/pass decision options
- Role breakdown view (skills, responsibilities, job description tabs)
- Radar graph visualization (adapted from client app)
- Employer-specific navigation and sidebar

### Remaining Work
- Role detail pages for individual skills/responsibilities (deprioritized - "seems a bit extra")
- Real data testing (waiting for Ilse to apply with deal breakers)
- Domain verification for email (DNS records setup needed)
- Elevator pitch text correction (using wrong section from narrative prep)

### Technical Decisions
- Using Firebase (acceptable scaling tradeoff given timeline)
- Single employer user model (no multi-user collaboration yet)
- Manual user creation process (via admin app → Firebase password reset)
- Staging environment for testing
- "Shoving data in convenient places" - acknowledged technical debt

### Demo Readiness
- Works with dummy/demo data
- Can use realistic but not real candidates
- Customized demo with actual customer JD + candidates is ideal but not required
- Average role analysis generation: ~4min 37sec (up from ~3min 30sec due to OpenAI slowdowns)

## AI Detection System (Ilse)

### Status: Near Completion (target: end of week)
**Purpose:** Detect fabricated/exaggerated stories, inconsistent voice, AI-generated content

### Capabilities Being Built
- **Story consistency analysis** across user's narrative
- **Voice/writing style verification** - detecting shifts that indicate fabrication
- **Responsibility level checking** - flagging inconsistent seniority claims
- **Stakeholder interaction validation** - CEO in one story, middle manager in another
- **Quantitative output verification** - catching big changes in claimed metrics

### Cost Optimization
- First implementation: ~$1/user
- Current optimized version: $0.20-0.30/user (for users with 5+ stories)
- Not per-application, per-user baseline

### Extended Use Cases
- Can fact-check resumes against user's narrative baseline
- Can analyze interview transcripts for consistency
- Can validate any document provided by user against their established voice/content patterns

### Technical Approach
- Sampling 10 production users with 6+ stories for testing
- Running consistency tests to ensure reliable behavior
- Not yet in employer dashboard, but functional

## Partnership/Integration Updates

### Emory University
- Meeting scheduled for tomorrow (2025-11-12)
- Planning rollout to alumni
- Special promo code requested for federal worker alumni
- Waiting on Ilse's code implementation

### Email Infrastructure
- Current issue: Wrong URL in emails
- Need domain verification in DNS records
- Multiple subdomains across SendGrid and Loops
- Logan and Ilse have domain registrar access

## Testing & Quality

### User Experience Insights (from Logan's demo)
1. **Notes feature assumption:** Logan expected notes to be shareable across employer team members
   - Current: Single user per employer account, notes are private by default
   - Future consideration: Multi-user collaboration features

2. **Skills/responsibilities reordering:**
   - Logan instinctively wanted to drag-reorder importance
   - Aligns with Ilse's vision for editability by employers
   - Seen as "conversation starter" about role requirements
   - Future: Potentially crowdsource importance via team upvotes

3. **Navigation patterns:**
   - Team agreed main list view is "money maker"
   - Stack ranking within list view preferred over next/previous arrows
   - Less need for quick navigation between individual candidate pages

### Product Philosophy Emerging
- "It's sexy" (having comprehensive role breakdowns)
- Tool as "means to an end" - stimulate conversation about roles
- Not just "look how fancy we are with 60 pages"
- Focus on practical utility over comprehensive documentation

