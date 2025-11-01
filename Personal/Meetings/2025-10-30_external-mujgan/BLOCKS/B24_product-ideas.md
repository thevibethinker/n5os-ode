# B24: Product Ideas & Features

## Ideas Generated During Conversation

### 1. AI-Powered Relationship Context Surfacing

**The Idea:**
AI that infers relationship importance and proactively surfaces relevant context at the right moment to lower the cognitive cost of maintaining personal relationships.

**How It Would Work:**
- **Input Signals:**
  - Language patterns ("I love them very much")
  - Communication frequency
  - Explicit user instruction
  - Historical context
- **Context Surfacing:**
  - "Faith had a promotion last week"
  - "Here's what she's working on"
  - "You mentioned wanting to catch up after her project ended"
- **Timing:**
  - Surface when user has cognitive bandwidth
  - Not necessarily immediately when event happens
  - Prepare information so caring requires less activation energy

**Key Principles:**
- "Can't make caring totally easy" - shouldn't shortcut being a good friend
- "Organize circumstances for being a good friend" - scaffolding, not replacement
- Lower activation energy without removing human element

**Parallel Design Philosophy:**
Careerspan doesn't build resume builders (too easy, wrong solution) - builds tools to help people talk about themselves (harder, right solution). Same principle: challenge users "just the right amount."

**Market:**
- Busy professionals losing touch with friends
- Founders dealing with loneliness and relationship neglect
- Anyone struggling with context switching costs for personal caring

**Similar To:**
- Clay (relationship CRM) but with proactive AI context
- Superhuman for relationships
- Not just a CRM - a relationship assistant

---

### 2. AI Task Discernment Layer (The Unsolved Problem)

**The Problem:**
Existing tools solve capture (Akiflow's Slack/Linear integration) but create information overload. AI has context but lacks discernment about moment-to-moment priorities. Hard to trust AI to pick tasks.

**What's Needed:**
- **Aggressive Capture:** From Slack, Linear, email, everywhere (solved)
- **Intelligent Curation:** AI that understands priority without user having to review inbox daily (unsolved)
- **Behavioral Scaffolding:** Help users who "can't protect against overwork" (aspire to 20 tasks, know 3 is better)
- **Moment-to-Moment Awareness:** Gauge changing priorities throughout day
- **Trust-Building UX:** Make AI judgment transparent and overridable

**The UI Challenge:**
- Needs specialized interface ("polished Todoist app")
- Integration with existing tools
- Not just another workflow builder
- Hybrid human+AI approach

**Why It's Hard:**
- Trust barrier (even founders would be "finicky" about AI picking tasks)
- Discernment ≠ Context
- Behavioral component (lack of discipline)
- Priorities shift minute-by-minute
- No good data source for what "matters" vs. what's just "on the list"

**Potential Approach:**
- Learn from user overrides
- Infer importance from communication patterns
- Time-box task selection ("what can you realistically do in 3 hours?")
- Build in protection against overwork
- Make curation feel easier than manual inbox review

**Market Validation:**
Vrijen with his sophisticated Zo workflows still "flying by seat of pants" on tasks - if power users can't solve this, it's real problem.

---

### 3. Prompt-Based Workflow Builder for Non-Technical Sophisticates

**The ICP:**
"Just about technical enough to be dangerous" - understands concepts (state management, APIs) but can't/won't learn developer tooling (terminal, Cursor).

**The Solution:**
- Chatbot UI (already familiar from ChatGPT)
- File system view (already familiar from OS)
- Natural language workflow description
- LLM translates prompts into interconnected workflows
- No node-based building (Zapier/n8n)
- No code editing (Cursor/Replit)

**Key Differentiation:**
- Not about making coding easier
- About making building accessible without coding at all
- Translation of prompting skill → building capability
- Lower "tools of the craft" barrier

**The Interconnectedness Unlock:**
- Workflows reference each other naturally in language
- "When meetings relate to market intelligence, aggregate to database"
- "Compare writing to corpus, identify monologue type"
- LLM provides flexibility between information reservoirs

**Market:**
- Prosumer bent users (Notion power users, ChatGPT experts, productivity enthusiasts)
- Non-technical founders wanting sophisticated automation
- Knowledge workers who want "high maintenance information needs" met

**Competitive Advantage:**
Zo is doing this. Opportunity is in lowering adoption barrier (Careerspan consulting model).

---

### 4. Memory-as-Stickiness Product Strategy

**The Insight:**
"Once something really knows you, switching cost seems too high." Memory creates lock-in more than features.

**Implementation Ideas:**

**Explicit Memory:**
- Store user context, preferences, goals
- Business state, priorities, current projects
- Relationships and their context

**Implicit Memory:**
- Communication patterns
- Work habits and energy rhythms
- Decision-making patterns
- Values and priorities (inferred)

**Memory Portability Problem:**
- ChatGPT memory was "hardest part of leaving"
- Vrijen's workaround: "Air-gapped deep research queries" with web search off
- Extracted memory to take to new platform

**Product Opportunity:**
- Make memory portable between tools
- Memory import/export standard
- "Bring your knowledge graph"
- Lower switching costs for users, raise adoption for new tools

**Or: Lean Into Lock-In:**
- First-mover advantage in AI tools = knowledge accumulation
- Build deepest memory fastest
- Make extraction hard (standard SaaS playbook)
- But risks user resentment

**Ethical Tension:**
Memory lock-in feels manipulative, but it's also genuinely valuable. How to balance retention with user freedom?

---

### 5. Careerspan Consulting: Custom Workflow Implementation Service

**The Product:** (Already in development)
- Custom Zo implementations for "high maintenance information needs" users
- Lower upfront cost of workflow adaptation
- Make base repo free/open source on GitHub
- Charge for personalized setup and consulting

**Target Market:**
- Sophisticated non-technical users
- Prosumer bent (Notion power users, etc.)
- Willing to invest in productivity but not in learning developer tools
- High pain with current solutions

**Value Proposition:**
- "Almost no one I've spoken to is willing to make" upfront workflow adaptation investment
- Vrijen does the hard work of adaptation
- Users get sophisticated automation without learning curve
- "Challenge people just the right amount" - not too easy, not impossible

**Why It Works:**
- Zo supports it (addresses their adoption barrier)
- Power users create case studies
- Network effects from shared workflows
- Not competition to Zo, enablement

**Pricing Model:**
- Waitlist: https://calendly.com/v-at-careerspan/30min
- Likely high-touch consulting (not scalable initially)
- Could evolve to templates + consulting hybrid
- Base repo free (lead gen + goodwill)

**Why This Conversation Validates It:**
Mujgan's AGI research confirms: upfront adoption cost is real barrier. Consulting to overcome it = business opportunity.

---

### 6. Meeting Intelligence with Stakeholder-Aware Sub-Analysis

**How It Works:** (Vrijen's current implementation)
1. Meeting auto-recorded
2. AI analyzes for stakeholder type (internal, external, networking, customer, founder)
3. Based on classification, runs targeted sub-analyses:
   - **Some meetings:** Identify warm intros
   - **Some meetings:** Track commitments only
   - **Some meetings:** Extract quotable moments for customer use
   - **Some meetings:** Aggregate to market intelligence database

**The Smart Part:**
Different meetings need different intelligence. One-size-fits-all summary is noise.

**Product Opportunity:**
- Templatize Vrijen's approach
- "Smart blocks" for different meeting types
- User defines which blocks matter for which stakeholder types
- Automatically routes to right analysis

**Extension:**
- Aggregate specific blocks over time
- Market intelligence → SQL database → periodic reports
- Relationship insights → CRM
- Commitments → Task list
- Quotes → Content library

**Why It's Better Than Otter/Fireflies:**
- Not just transcription + summary
- Contextual intelligence based on relationship type
- Feeds into other systems automatically
- User-defined intelligence types

---

### 7. Voice-to-Content Pipeline with Personal Corpus

**Vrijen's Implementation:**
1. Voice record monologue
2. AI identifies monologue type (product reflection, LinkedIn idea, etc.)
3. Scans against personal writing corpus
4. Connects to past content
5. Outputs content that's "actually 90% there" (not the typical "claims 90%, actual 60%")

**Key Innovation:**
- Comparison to personal corpus (not generic LLM output)
- Connects past and present thinking
- Maintains authentic voice
- Type detection allows different processing

**Product Potential:**
- Voice-first content creation
- Personal voice preservation and evolution
- Context from historical writing
- Multiple output formats from same input

**Market:**
- Content creators wanting authentic voice
- Founders doing thought leadership
- Anyone who "likes monologuing" (Vrijen: "obviously you can see how much I like doing that")

**Technical Needs:**
- Good voice transcription
- Corpus analysis capability
- Voice style extraction
- Content type classification

---

### 8. Founder Peer Support Platform

**The Problem:**
30+ founders in NYC - "every single one of them is so alone"
- Can't go to co-founder (they hear from you constantly)
- Friends don't understand
- Family relationships suffering
- Professional network is transactional
- Self-sacrifice is celebrated (cultural reinforcement)

**What Exists:**
Vrijen organizing meetups manually - everyone shows up because everyone needs it.

**What Could Exist:**
- Platform for founder peer matching
- Not just Slack group (more noise)
- AI-facilitated introductions based on context
- "Office hours" for specific problems
- Accountability partnerships
- Celebration of wins (not just struggle porn)

**AI Role:**
- Match founders with complementary challenges
- Surface context for meaningful conversation
- Facilitate connection without replacing human element
- Help maintain weak ties in network

**Why It's Needed:**
Loneliness is universal among founders. Current solution (manual meetups) doesn't scale.

**Similar To:**
- YC founder matching
- OnDeck community
- But focused specifically on emotional support, not just business

---

### 9. Dynamic Context Repositories (Not "Sacred Texts")

**The Problem:**
ChatGPT project files go stale - "constant process of maintaining these records, these sacred texts the AI could refer to."

**Vrijen's Solution:**
"Very specific workflows that know exactly which reservoir of information to reference. Flexibility comes from LLM in the middle."

**Product Idea:**
- Information "reservoirs" that update automatically
- Business state file that workflows reference
- Priorities file that changes with context
- AI maintains these automatically through interactions
- No manual "update project files" step

**How It Works:**
- User: "Our priorities shifted - we're focusing on enterprise now"
- AI updates priorities reservoir
- All workflows reference updated context automatically
- No need to swap files in/out

**Single Source of Truth:**
One file for business state, all workflows reference it. Change once, affects everything.

**Product Opportunity:**
- Make this easy for non-technical users
- Visual map of information reservoirs
- Show which workflows reference which reservoirs
- Auto-detect when context is stale

---

## Feature Requests (Implicit)

**For Zo:**
1. Native memory implementation
2. Task management UI with discernment layer
3. Easier workflow interconnection visualization
4. Lower upfront adaptation cost (marketplace of templates?)

**For AGI:**
1. Communication consolidation across platforms
2. Relationship context surfacing
3. Founder-specific features (if pivoting that direction)

**For Any AI Tool:**
1. Right information at right time (not comprehensive archives)
2. Intelligent filtering (knowing when to hide, not just when to show)
3. Trust-building for AI judgment
4. Behavioral scaffolding (not just technical solutions)
5. Interconnected systems (workflows that reference each other)

---

## Innovation Themes

**Across all these ideas:**
1. **Discernment over capture** - filtering is more valuable than storing
2. **Interconnectedness** - workflows don't exist in vacuums
3. **Right-sized difficulty** - challenge users appropriately, don't make everything easy
4. **Context-aware processing** - different situations need different intelligence
5. **Lowering cognitive switching costs** - especially for caring/relationships
6. **Memory as moat** - knowledge accumulation creates stickiness
7. **Hybrid human+AI** - AI organizes circumstances, humans provide judgment

**The Meta-Product:**
All of these are variations on: **AI that knows you deeply, surfaces the right information at the right time, and lowers cognitive costs without removing human agency.**
