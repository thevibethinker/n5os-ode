---
created: 2025-11-12
last_edited: 2025-11-12
version: 1.0
block: B43
---

# B43: Operational Updates & Execution

## Individual Workstreams

### Danny Williams - Engineering
**Focus:** Employer portal completion + testing support  
**Velocity:** "Mostly done in a few days"  
**Next:** Testing support, minor fixes, knowledge transfer to Ilse on deployment

**Notable:**
- Built test user creation flow during call
- Demonstrated product live to team
- Comfortable pushing back on scope creep
- Leaving company next month - knowledge transfer in progress

### Ilse Funkhouser - Engineering/Product
**Focus:** AI detection system completion  
**Timeline:** End of week target  
**Secondary:** Backend deployment learning, Emory code implementation

**Notable:**
- Optimized detection cost from $1 to $0.20-0.30 per user
- Never deployed backend before - using this as learning opportunity
- "Really happy" with collaboration style with Danny
- Embracing technical debt given exit timeline

### Logan Currie - Business Development/Strategy
**Focus:** "Page 18" GTM work, acquisition pipeline  
**Schedule:** "Miraculously free of meetings" day  
**Next:** Testing employer portal, acquisition outreach, video creator vetting

**Notable:**
- Systems thinking about product UX
- Building acquisition target database
- Coordinating multiple workstreams (demo, outreach, partnerships)

### Ilya Kucherenko - Marketing/Sales
**Focus:** Customer-facing language/messaging framework  
**Timeline:** Target completion today  
**Deliverables:** Trial language → demo guidelines → video storyboard

**Notable:**
- Pacific timezone (newest to team dynamics)
- "Racing towards" video storyboard (longest lead time)
- Self-aware about boundaries as new team member
- Iterating heavily on messaging (discarded first drafts)

### Vrijen Attawar - CEO/Founder
**Focus:** High-level acquisition conversations, partnership coordination  
**Meetings:** Darwin Box followup, Rockle 1:1, Ilya sync later

**Notable:**
- "Pulling strings" for founder-level conversations
- Managing acquisition narrative and timing
- Coordinating team demo preparation
- Balance between urgency and not seeming desperate

## Cross-Functional Coordination

### Engineering → Product
- Danny teaching Ilse backend deployment
- Coordinating on employer portal testing (Ilse creating test data)
- Aligned on technical debt acceptance

### Product → Sales
- Ilse providing technical depth for Ilya's messaging work
- "Science behind it" explanations for non-technical audiences
- Feedback loop on what features to emphasize in demo

### Business Development → Sales
- Logan and Ilya coordinating on positioning for different acquirer types
- Sharing learnings from acquisition conversations
- Video creator selection collaboration
- Weekly sync proposed to maintain alignment

### Leadership → Team
- V briefing team on external conversations (Darwin Box, DAO)
- Transparent about acquisition strategy and timeline
- Creating space for team to prepare (giving Darwin Box time before demo)

## Process & Rituals

### This Stand-up
- Started with timezone small talk (Ilya's first few days)
- Product update (Danny)
- Acquisition update (V)
- Live demo session
- Strategic discussion
- Individual status updates
- Book recommendations/team bonding

### Proposed New Rituals
- Weekly acquisition strategy briefing (Tuesdays proposed)
- Regular demo rehearsals/product reviews
- Continued daily stand-ups

## Infrastructure & Technical Operations

### Email System Issues
- Wrong URLs in emails (Firebase domain not verified)
- Need DNS record updates
- Multiple subdomain sprawl (SendGrid, Loops)
- Logan and Ilse have registrar access

### Deployment & Testing
- Staging environment active
- Manual user creation via admin app + Firebase
- Testing workflow: admin creates employer → Firebase password reset → employer portal login
- Need real data for proper testing

### User Authentication
- Firebase-based
- Password reset email flow
- No Google login implemented (bare minimum for now)
- Employer users separate from client users (different permission sets)

## Timeline & Dependencies

### This Week
- **Ilse:** AI detection system complete
- **Ilya:** Customer-facing language/demo guidelines/video storyboard
- **Logan:** Video creator selection, GTM page 18
- **Danny:** Employer portal testing/fixes
- **Team:** Prepare for Darwin Box demo next week

### Next Week
- **Darwin Box demo call** (V, Logan, Ilse, potentially Ilya)
- **Emory meeting** (V) - tomorrow (2025-11-12)
- **Continued acquisition outreach** (V, Logan)

### Longer Term
- Danny leaving next month
- Video production (3-6 days once storyboard ready)
- 15-20 acquisition conversations in pipeline
- Emory alumni rollout

## Resource Management

### Cost Awareness
- OpenAI getting slower (4:37 avg, up from 3:30) - no code changes
- AI detection system cost optimization priority
- Acceptable to "break the bank" slightly for quality features
- Firebase costs acceptable given timeline

### Team Capacity
- Danny: High output, time-boxed contribution (leaving soon)
- Ilse: Balancing multiple technical projects
- Logan: Juggling outreach, product testing, strategic planning
- Ilya: Learning company while producing at full speed
- V: External-facing, coordinating moving parts

### Knowledge Transfer
- Danny → Ilse: Backend deployment
- Ilya → Team: Negotiation tactics from previous exits
- Logan → Team: Acquisition process learnings
- Team → Ilya: Company context, product depth

## Risk Mitigation

### Technical Debt Acknowledged
- Firebase scaling limitations
- "Convenient places" for data storage
- Email infrastructure needs work
- Accepted as reasonable tradeoff given exit timeline

### Team Transitions
- Danny leaving creates urgency for knowledge transfer
- Ilya new, being careful about boundaries
- Building shared context rapidly

### External Dependencies
- Fiverr video creator availability
- OpenAI performance degradation
- Acquisition conversation timing
- Partnership timelines (Emory)

