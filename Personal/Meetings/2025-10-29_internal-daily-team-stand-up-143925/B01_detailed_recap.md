# Detailed Recap

## Meeting Overview
Internal daily standup with Vrijen (V), Ilse Funkhouser, and Rochel Polter discussing product development and team status updates.

## Key Discussion Points

### Personal Check-ins
- Rochel recently returned from travel in Romania and Bulgaria (over a month ago), visited Dracula's castle
- Ilse recently got a haircut (involving two barbers - a dad joke)
- V has substantial follow-ups pending but excited about a couple of good ones
- Rochel's roommate had a scooter accident in Israel but is recovering well; was ironically headed to chiropractor

### Product & Engineering Updates

**Email Tag System**
- V using custom tagging system (Howie) that auto-sorts emails based on tags
- Tags indicate investor status, follow-up timing, and request type (follow-up vs. reminder)
- Significant unlock for managing follow-up workflow

**Lead Analysis & Direct Apply Flow**
- Ilse demoing new lead analysis interface and Direct Apply flow
- Lead analysis includes: application timestamp, status (viewed/applied), candidate notes
- Analysis dashboard shows: elevator pitch, bottom line assessment, overall strength/weakness paragraphs, qualification level, career trajectory, deal breakers, hard/soft skill gaps, and composite scores

**Application Modal Design**
- Rochel presented new Direct Apply modal design
- Modal-based flow (not full page) to maintain lightweight user experience
- Includes: summary of how candidate is being represented, feedback form for candidates to dispute assessments, opportunity to tell additional work story
- Deal breaker presentation in two sections: uncertain items (yes/no toggle) and known items (pre-selected, editable)
- Final screen confirms application submission and shows expected close date

**Product Development Notes**
- New state management for closed roles in Direct Apply (Danny already has expiration date logic)
- Applied button being redesigned from tag appearance to tag dropdown for clarity
- Application status flow: Vibe Check loading → In progress → Apply or archive states
- Added "Got the job" state for direct applications
- First handful of customers will trial system; feedback on candidate disagreements with assessment is being collected
- Resume link functionality pending; currently preserving resume path for ATS parity
- Employer portal design allows quick toggle between Careerspan analysis and original resume
- Soft skills scores displayed in lead analysis

### Product Strategy & Decisions
- Addressing challenge of candidates editing deal breakers: team decided to let it be for now ("let sleeping dogs lie") - not trying for perfect internal consistency at this stage
- Goal is to be "so many leagues better than resume analysis" that perfection isn't required yet
- Accepting that employers may see internally inconsistent data from edited deal breakers, but this will be manually cleaned if needed
- Relative gamification approach discussed: showing candidates what % of critical gaps they're missing to incentivize gap-filling
- Not prioritizing gap-specific suggestions in modal yet, but available in fill-in-gap section

### Content Coordination & Filtering
- V coordinating with Ash on information gathering (waiting for call)
- Team planning to coordinate posting across locations and reverse-prove filtering system quality
- Tech demo will show system's filtering effectiveness

### External Discussion
- Discussion about AI research papers on AI psychosis (legitimate field)
- ChatGPT phenomenon: millions use it weekly for self-harm discussions
- Viral VC story about person claiming gangstalking via ChatGPT
- Broader discussion about deepfakes, content fingerprinting for tracking, and use of metadata manipulation (Wagatha Christie controversy reference) for tracking information leaks
- Metadata fingerprinting techniques used in movie/book pre-releases to identify leak sources

## Attendees
- Vrijen Attawar (V) - Leader
- Ilse Funkhouser - Product/Engineering
- Rochel Polter - Design/Product

## Duration
~31.6 minutes

## Tone
Casual, collaborative, interspersed with humor and tangential discussions while maintaining focus on product development
