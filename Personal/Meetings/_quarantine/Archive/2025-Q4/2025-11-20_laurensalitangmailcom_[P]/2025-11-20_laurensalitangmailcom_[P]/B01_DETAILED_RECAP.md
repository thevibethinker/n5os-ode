---
created: 2025-11-20
last_edited: 2025-11-20
version: 1.0
---

# Meeting Recap: Lauren Salitan x Vrijen (Zo Product Demo & Networking)

## Overview
Vrijen conducted an extensive product demonstration of Zo with Lauren Salitan, a solutions engineering consultant from Austin, Texas. The conversation evolved from personal connection and background sharing into a deep technical exploration of Zo's capabilities, use cases, and positioning. This was both a product demo and relationship-building session with a technical solopreneur who may become a user and potential evangelist.

## Background & Relationship
- **How they met:** Lauren discovered Vrijen through a Springboard Software Engineering program talk where Vrijen spoke about Careerspan. Lauren then reconnected via LinkedIn after seeing Vrijen's recent post.
- **Lauren's background:** Solutions engineering consultant running her own tech consultancy in Austin, TX. Self-taught programmer initially, then formalized skills through Springboard. Works on automation, internal tools, and custom systems for businesses.
- **Vrijen's background:** Brooklyn-based founder of Careerspan, about to hit the 3-year mark with co-founder. Non-technical founder with deep expertise in career coaching and now building AI-powered workflow systems.
- **Shared perspective:** Both have non-traditional technical backgrounds—Vrijen emphasized doing this "looking at zero lines of code" while Lauren is self-taught but highly technical. Both value bridging technical and non-technical worlds.

## Zo Product Demonstration

### What is Zo?
Vrijen explained Zo as "effectively a computer in the cloud" or more accurately "a server in the cloud" that allows users to:
- Prompt the system with natural language instructions
- Connect to APIs easily (demonstrated with Aviato API) by simply providing documentation
- Leverage agentic systems for automating complex workflows
- Access integrations (email, SMS, Google Drive, Gmail, etc.)

### Key Capabilities Demonstrated

**1. API Integration & Automation**
- Vrijen showed how Zo can connect to third-party APIs (like Aviato) with minimal technical overhead
- The system reads API documentation and sets up connections with natural language instructions
- Even less technical users can achieve integration through "disciplined vibe coding"

**2. Meeting Intelligence Automation**
- Vrijen shared his personal workflow: after every meeting, Zo automatically aggregates meeting data
- The system processes transcripts, generates analysis, identifies follow-up needs dynamically
- Distinguishes internal vs. external meetings and tailors responses accordingly
- Integration with Fireflies webhook for automatic transcript ingestion (initially from Google Drive, now direct via webhook)

**3. Knowledge Base & Sacred Texts**
- Core philosophy: In the age of AI, high-quality information is critical ("sacred texts" at highest informational grade)
- AI can leverage information infinitely, so consolidation matters
- Zo captures information over time as users live their lives, creating an accreting knowledge system
- Goal: one centralized pool of information about self, business, work, and worldview

**4. Personas & Flexible Workflows**
- Zo supports multiple "Personas"—layered prompts that switch context without reloading conversations
- Demonstrated personas:
  - **Vibe Strategist:** Strategic thinking and frameworks
  - **Vibe Builder:** Implementation and code production
  - **Vibe Teacher:** Explanation and learning
- Can embed files within personas for contextual awareness
- Personas can change themselves based on workflow needs

**5. System Rules & Conditional Logic**
- System rules define guardrails and automation triggers
- Rules can be conditional (enabled only under specific circumstances)
- Example: Automatic session state file creation at conversation start
- Prevents unintended actions (e.g., requiring explicit consent for outgoing transmissions)

**6. Content Generation & Personalization**
- Demonstrated generating cold emails using strategic frameworks
- Example: Pull CRM contact data (Lauren), apply strategist framework, switch to writer persona, generate personalized cold email
- Much higher quality than typical cold outreach due to framework-driven approach
- Allows seamless persona-switching without restarting context

**7. Large-Scale Data Processing**
- Supports ~1TB of online storage (with Ultra subscription), 64GB memory, decent CPU
- Can theoretically run Ollama locally (though slowly at ~1 token/second)
- Could be used for batch data processing through LLMs at very low cost

## Key Business Insights from Vrijen

### Lowering the Barrier to Entry
- Zo's real challenge and opportunity: making the platform accessible to non-technical users
- Vrijen emphasizes this isn't about dumbing down—it's about intelligent design
- Quote: "The real gap that they're facing is how do we lower the barrier to entry?"
- Vrijen's "vibe coding" approach demonstrates it's possible for non-technical founders to build sophisticated automations

### Ecosystem Philosophy
- Launched yesterday and went "pretty viral on Twitter"
- Large community on Discord with solopreneurs, small business owners, tech founders, designers, and programmers
- Vrijen: "Zo's the only product where every use case is a killer use case because it's your use case"
- Not prescriptive—adaptable to whatever workflow users actually need

### Model Preferences & Multi-Model Strategy
- Vrijen uses different models for different tasks:
  - **Claude:** For code production and avoiding errors, but misses what might be forgotten
  - **ChatGPT:** For vibe coding and brainstorming, massive memory library for ongoing context
  - **Strategy:** Start with ChatGPT for idea generation, migrate to Claude for execution
- Zo allows seamless model switching based on task needs

### Cost Structure
- Zo charges pure token pricing with no markup (VC-funded, not extracting revenue)
- Users pay exactly what they pay on Anthropic/OpenAI websites
- Promo code offered (20% discount)
- Trade-off: May be higher cost than flat monthly subscription plans if using heavily
- But positioned for users who "should probably be on a pro plan anyway"

## Context Engineering & Data Strategy
- Important insight on context windows: Smaller, modular files are better than one giant file
- Zo can search within folders effectively, so segmentation improves recall precision
- Contrast to OpenAI's approach: Zo allows choosing specific documents to reference vs. spreading attention across all files
- This precise context engineering gives Zo an advantage for knowledge-heavy workflows

## Use Cases Identified in Conversation

**From Vrijen:**
- Automatic meeting processing and intelligence generation
- Cold email generation via strategist framework
- CRM data enrichment and strategic outreach
- Knowledge capture and consolidation
- Workflow automation for non-technical founders
- Personal knowledge base management

**From Lauren (potential):**
- Tracking conversational history with contacts
- Automating client audit workflows
- Templating non-technical translation (technical to everyday language)
- Centralizing records and operational automation
- Efficiency improvements for consultancy work

## Tone & Relationship Dynamics
- Very friendly, collaborative energy
- Mutual respect: Vrijen clearly values Lauren's technical perspective; Lauren appreciates Vrijen's evangelism
- Lauren expressed genuine excitement about the product
- Vrijen is generous with knowledge and shares his setup/frameworks
- Both discussed the importance of bridging technical/non-technical divides
- Lauren mentioned potential next phase: wanting to "take the load off a lot of my work" to focus on what's next

## Product Demo Outcome
Vrijen offered to send Lauren:
1. A zip file with base-layer Zo setup and instructions
2. Tips for getting started (tinker first, don't overcomplicate)
3. Discord community link to join ecosystem
4. Encouragement to try the platform without pressure
