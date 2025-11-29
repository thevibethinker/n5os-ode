---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Meeting Metadata Summary

## Meeting Identifiers
- **Date**: November 17, 2025
- **Time**: ~45 minutes (estimated from transcript length)
- **Format**: Video call (confirmed by audio setup discussion)
- **Meeting Type**: External introduction & strategic exploration

## Participants
| Role | Name | Organization | Context |
|------|------|--------------|---------|
| Host | Sujay | Career tech startup | Founded recruiting/matching platform targeting universities + enterprises |
| Guest | V (Vrijen Attawar) | Careerspan | Founder; career coach background; 10 years coaching + 4 years entrepreneurship |

## Communication Channel & Discovery
- **How Sujay found V**: Either Borderly or LinkedIn (uncertain which; expressed "let's shoot our shot")
- **V's assessment of Sujay**: "You guys are crushing it" - positive first impression based on 1K LinkedIn followers in 7 months
- **Relationship status**: Initial outreach → exploratory conversation → mutual interest in ongoing relationship

## Organizational Context

### Sujay's Startup Status
- **Stage**: Early; 7 months of public activity visible
- **Founding team**: 
  - Sujay (founder)
  - Sujay (co-founder/eng lead)
  - Jaden (recently promoted to founding engineer status)
  - 2 additional founding engineers (one Purdue Master's, one UIUC student)
  - 2 more founding engineers added for career services feature development
  - **Total**: ~7 people (approximate)
- **Funding**: Access to $500K+ in cloud credits (Kratex + venture access)
- **Current LLM spend**: ~$300 total (highly optimized)

### Traction Metrics
- **Geographic reach**: India (tier 1 & tier 2 pilot programs), US universities (UIUC, Georgia Tech)
- **Backing**: Adventure program acceleration at Georgia Tech
- **University partnerships mentioned**: UIUC career services, Georgia Tech
- **Enterprise testing**: Ellis (San Bernardino, CA) - data analytics company; hiring data scientists from UIUC

## Core Business Model
- **Customer segments**: 
  - Universities (free access)
  - Students (free access)
  - Employers (paid - primary revenue)
- **Pricing**: $250/month base; scales by number of schools accessed
- **No percentage-of-hire model** (deliberate rejection of traditional recruiter fee structure)

## Technology Architecture
- **LLM approach**: Decomposed, modular system using Claude Sonnet 4.5
  - Task-based model selection (using dumbest viable model per task)
  - Manual candidate profile input (not resume parsing to reduce bias)
  - Graph vector storage for ranking
  - Paragraph-based LLM reasoning (ChatGPT-style explanations)
- **Platform features**: 
  - In-house ATS
  - Career event/hackathon hosting capability
  - Candidate profile with projects/experiences
  - Employer job posting interface
- **Candidate flow**: Manual profile creation → LLM pre-ranking → LLM ranking per job → top 25 matches auto-sent to employer

## Conversation Themes
1. **Problem diagnosis**: Resume visibility gap (not candidate viability problem)
2. **Data structure**: Resume as outdated data format; need for upgrade
3. **Marketplace dynamics**: Two-sided platform challenges; Handshake case study
4. **University economics**: Limited recruitment budgets vs. tech talent teams; NACE/Sherm conferences matter
5. **LLM design**: State-of-art model lock-in risks; cost optimization through decomposition
6. **Self-reflection gap**: Career tech blind spot - people struggle with self-examination/positioning

## Relationship Trajectory
- **Tone**: Collegial, mutually respectful, substantive
- **Outcome**: Advisor relationship proposed + accepted
- **Community integration**: Invitation to monthly career tech founder meetups
- **Geographic plan**: NYC in-person meetup (V travels to NY for Camina's events)
- **Slack/ongoing**: Email exchange pending; follow-up on advisor structure details

## External Connections Mentioned
- **Camina** (Human Options): Runs career-focused events; recommended both to universities and serves as key connector
- **Jerry Chen**: Career tech founder; introduced by Camina; recently attended V's birthday
- **NACE**: National Association for Colleges and Employers (key conference)
- **Sherm**: Recruitment tech accelerator; $200K competition at year-end
- **Georgia Tech**: Adventure program; Great X program backing Sujay's startup

## Strategic Observations
- **V's assessment**: Sujay's team has demonstrated better "cut through" than typical early founders; visibility problem framing is sound
- **Careerspan positioning**: V positioned Careerspan as reflection-oriented UX + matching tech; components partially built
- **Model parity concern**: V noted Careerspan using 4o (not 5); Sujay locked into Sonnet 4.5 (opportunity to optimize)
- **Handshake comparison**: Sujay building cheaper, lighter alternative; V supportive of disruption attempt

## Next Steps Ownership
| Item | Owner | Timeline |
|------|-------|----------|
| Email address for Slack | Sujay | This week |
| Advisor structure details | Sujay | 1-2 weeks |
| NYC meetup coordination | Sujay + V | 1-2 weeks |
| Community intro materials | V/Careerspan | 1-2 weeks |
| Follow-up on model optimization | Sujay's eng team | As needed |
