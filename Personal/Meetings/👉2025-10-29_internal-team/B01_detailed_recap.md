# Meeting Recap: Internal Team Standup - Oct 29, 2025

## Overview
Team standup among V (Vrijen), Ilse, and Rochel covering personal updates, recent explorations in AI/content security, and detailed product walkthrough of Careerspan's Direct Apply flow and candidate analysis system.

## Key Discussion Sections

### Personal Updates & Team Sync
- **Team Status**: Everyone managing multiple items; V has follow-up items but some exciting ones lined up
- **Travel**: Rochel remains in Israel (6 hours ahead), previously visited Romania and Bulgaria with colleagues Danny and Elsa; found Dracula's Castle area less impressive than expected (not worth the paid tour)
- **Haircuts & API Work**: Ilse got a haircut and discussed a "janky API endpoint" that enables real-time CSV updates through magic links

### AI & Security Research Discussion
- **AI Psychosis Research**: Ilse mentioned recent research papers on AI psychosis and concerning trends
- **ChatGPT Usage**: Discussion of Sam Altman mentioning that a million people weekly contact ChatGPT about self-harm
- **VC Going Viral**: Referenced a VC who posted about being gangstalked and gaining "privileged access" to ChatGPT responses (highlighted concerns about AI reliability and mental health)
- **Fingerprinting & Security**: Deep discussion on fingerprinting techniques used for leak tracking (Wagatha Christie case, deep fake tracking, pre-release book/movie fingerprinting using invisible characters and word choice variations)
- **Email Tagging System**: V explained using the "Howie" tool with email tags for auto-sorting (tags indicate investor status, follow-up timing, etc.) - planning to standardize across all AI systems

### Product Development - Careerspan

#### Application Status Flow Changes
- Rochel presented new flow for updating application statuses to make it more obvious that statuses are editable (moving from tag-like appearance to dropdown)
- Status progression: Vibe Check → Loading → In Progress → Apply/Archive states
- New "Got the Job" state added as an option for users

#### Candidate Analysis Display
Ilse walked through the detailed candidate analysis system showing:
- **Application Meta**: Time applied, status (Viewed/Applied), applicant feedback notes
- **Presentation to Employer**: Score, strengths, weaknesses, elevator pitch
- **Scoring System**: Overall score, background score, hard skills, soft skills, responsibilities, uniqueness
- **Deal Breakers**: Important blockers (e.g., no professional software experience, location mismatch)
- **Gaps**: Hard gaps (technical skills missing like Go, Memcached, Redis) and low gaps (some transferable experience)
- **Qualification Assessment**: Underqualified, Overqualified, Good Fit, or Mismatch
- **Career Trajectory**: Pivot, Lateral Promotion, etc.

#### User Review & Edit Capabilities
- Users can review how they're being presented to employers
- Users can edit deal breaker assessments (noted concern: internal inconsistencies possible if user overrides system assessment)
- Team decision: Accept potential inconsistencies at this stage; manual editorial oversight acceptable as they're already "so many leagues better than resume analysis"
- Resume upload available (optional now, may become required)
- Referral information capture

#### Direct Apply Modal Walkthrough
Rochel presented the UX flow:
1. Apply Modal opening with summary of how candidate is represented
2. Candidate feedback section ("did we misrepresent you?") - noted as internal feedback, not shared with employers
3. Opportunity to add another work story via "Fill in Gap" section
4. Deal breaker review section (uncertain items vs. pre-selected known items)
5. Confirmation and submission
6. Confirmation page with expiration date communication

#### Strategic Notes on Development
- Keeping modal experience (vs. full page) to maintain sense of progress for user
- Gap section not yet specific to individual gaps - deliberate decision to keep scope manageable
- Future enhancement mentioned: Gamification element (% of critical gaps filled) to incentivize users to reduce gaps
- Parity maintained with traditional resume for employer confidence-building

### Coordination on Posting & Tech Demo
- V and Ilse coordinating on where content gets posted (need clarity on posting locations)
- System filtering will be validated through demonstration: "reverse prove that our system was good at filtering"
- Client prospects "genuinely looking for tech like ours"

## Technical Details Mentioned
- CSV-based candidate import system
- Google Drive integration for file access
- Staging environment for testing
- Role closure state management
- Dynamic tag-based application status management

## Tone & Culture Notes
- Playful, collaborative dynamic with lots of in-jokes and tangential discussions
- V and Ilse have deep rapport (noticed email tagging system immediately)
- Team comfortable discussing half-baked ideas and future possibilities without pressure to finalize immediately
- Emphasis on shipping incrementally rather than perfecting before launch

