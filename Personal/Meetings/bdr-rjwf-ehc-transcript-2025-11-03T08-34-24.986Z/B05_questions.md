# Open Questions and Unresolved Issues

## Technical Questions

### System Architecture
- **Q: What's the optimal balance between centralized system files vs. local config?**
  - Context: Discussion about what to include in public repo vs. user-specific customizations
  - Status: Leaning toward more comprehensive base system with local config overrides
  - Decision needed: Finalize distribution model before wide release

- **Q: Should Persona switching include automatic model switching?**
  - Nafisa raised: Different models may be better for different tasks
  - Vrijen's response: Not currently implemented; Sonnet 4.5 is best all-rounder
  - Tradeoff: Cost optimization vs. performance optimization
  - Status: Deferred for now

- **Q: How to ensure package completeness during export?**
  - Problem: Scripts were missed in initial packaging despite rules
  - Current approach: Manual validation by Vrijen
  - Desired: Automated validation that AI can execute
  - Status: Ongoing challenge; Build Orchestrator helps but wasn't used this time

### Distribution & Installation

- **Q: What's the most effective installation validation?**
  - Current: End-to-end testing using debugger persona
  - Issues: Catches problems late in process
  - Alternative: Pre-flight checks before installation?
  - Status: Under development

- **Q: Should onboarding be conversational or prescriptive?**
  - Agreement: Conversational interaction is important for personalization
  - Question: When in the process? Before or after installation?
  - Tradeoff: Setup complexity vs. customization quality
  - Status: Decided to add after core installation

- **Q: How to handle version conflicts between local changes and updates?**
  - Git-based model: One-way sync from central repo
  - Question: What happens when user has modified core files?
  - Status: Not fully resolved

### Persona System

- **Q: Why isn't auto-switching working consistently?**
  - Observed: Worked repeatedly, then failed during demo
  - Hypothesis: Missing integration with Researcher, Strategist, Teacher personas
  - Status: Debugging needed

- **Q: What triggers should activate persona switching?**
  - Current: Keyword detection and contextual analysis
  - Question: What's the right threshold for switching?
  - Concern: Too aggressive = jarring; too passive = unused
  - Status: Needs refinement

## Product Strategy Questions

### Go-to-Market

- **Q: How much functionality should be given away?**
  - Nafisa's view: Enough that people want to explore, not so much they stop thinking
  - Vrijen's concern: Maintaining competitive advantage vs. reducing friction
  - Current decision: Give substantial base system
  - Question: Is this the right balance long-term?

- **Q: What's the target user profile for N5OS?**
  - Vrijen: "Folks who are brand new to Zo"
  - Observation: "Requires fair amount of understanding and interest in debugging"
  - Tension: Zo is buggy; N5OS adds complexity
  - Question: Is this too ambitious for non-technical users right now?

### Monetization

- **Q: What's the business model for N5OS?**
  - Not explicitly discussed
  - Context: Vrijen is bootstrapping, limited runway
  - Related: $2M fundraising goal mentioned
  - Status: Unclear

### Competitive Positioning

- **Q: How does N5OS differentiate from vanilla Zo?**
  - Quality of life improvements
  - Persona orchestration
  - Workflow automation
  - Question: Is this defensible? Can Zo team replicate?
  - Status: Not addressed

## Personal/Situational Questions

### Nafisa's Situation

- **Q: What will Nafisa decide about her father's job offer?**
  - Would require moving to Mumbai
  - Timeline: Needs to decide soon (actively assessing)
  - Impact: Would affect her setup and location
  - Status: Under consideration

- **Q: What's Nafisa's long-term plan post-Careerspan work?**
  - Currently evaluating options
  - No permanent setup until decision made
  - Question: What role will N5OS/Zo play in her next venture?

### Vrijen's Situation

- **Q: What's the funding situation and runway?**
  - Mentioned: All reserves from McKinsey are depleted
  - Goal: "Pull more than $2 million out of this hat"
  - Timeline pressure: Demo Wednesday
  - Question: What happens if demo doesn't lead to funding/traction?

## Testing & Validation Questions

### Current Installation

- **Q: What are the complete list of dependencies?**
  - Discovered: PyAMO, n5_safety, schemas, various scripts
  - Question: What else is missing that hasn't been discovered yet?
  - Status: Ongoing discovery through testing

- **Q: Will the directory structure work for all users?**
  - Issue: Confusion during installation
  - Question: Is this a packaging bug or design flaw?
  - Status: Being debugged

### Scalability

- **Q: Can this installation process scale to multiple users?**
  - Current: Highly manual, requires Vrijen's troubleshooting
  - Observation: "Fourth attempt" at packaging
  - Question: What needs to change for self-service installation?
  - Status: Significant work needed

## Follow-up Research Questions

### Technical Learning

- **Q: What can be learned from the two founder conversations Vrijen shared?**
  - Ben's conversation: "Has a lot of really good hints"
  - Topic: How to use Zo and philosophy of LLMs
  - Action: Nafisa to review
  - Question: What specific insights will be most valuable?

### Community

- **Q: Should Nafisa join the Zo Discord?**
  - Purpose: Bug reporting and community engagement
  - Vrijen's suggestion: Report the Zo crashing issue
  - Status: Not yet joined
  - Question: What's the community like? How responsive is Zo team?
