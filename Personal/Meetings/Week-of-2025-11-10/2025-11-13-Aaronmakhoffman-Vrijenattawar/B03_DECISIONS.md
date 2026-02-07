# B03: Decisions Made

## Decision 1: Zo Not Ready for Customer-Facing Applications

**DECISION:** Both participants agreed to hold off on using Zo for customer-facing applications at this time.

**CONTEXT:** The conversation explored using Zo as a client communication portal. Both acknowledged that while Zo offers personalization benefits, it is not stable or reliable enough for production customer use.

**DECIDED BY:** Joint agreement between Vrijen Attawar and Aaron Mak Hoffman

**IMPLICATIONS:** Customer-facing workflows will continue to be handled through existing channels rather than Zo-hosted sites or messaging interfaces.

**ALTERNATIVES CONSIDERED:** Aaron considered piping client communications through Zo with a dedicated client-facing site, but decided against it due to reliability concerns.

## Decision 2: Zo for Planning and Structure, Replit Agent for Code Execution

**DECISION:** Aaron Mak Hoffman will use Zo for context management, planning, and code structure, while using Replit Agent for actual code writing and implementation.

**CONTEXT:** Aaron found that Zo excels at pulling in the right context at the right time, but Replit Agent has better guardrails, Lang Graph architecture, and cloud integration for advanced coding tasks.

**DECIDED BY:** Aaron Mak Hoffman

**IMPLICATIONS:** This creates a hybrid workflow: Zo handles strategic planning, documentation, and architectural decisions; Replit Agent executes the actual code implementation. Aaron's build time reduced from 40-60 hours to 3 hours using this approach.

**ALTERNATIVES CONSIDERED:** Using Zo for both planning and code execution was found to be less effective for complex applications due to Zo's limitations in recalling references and context at the right times.

## Decision 3: Mandatory Technical Documentation + README for All Projects

**DECISION:** All development projects will generate both a technical implementation document AND a non-technical README before code execution.

**CONTEXT:** Aaron discovered this approach ensures maintainability and gives him the ability to understand and take control of the system if needed, despite being non-technical.

**DECIDED BY:** Aaron Mak Hoffman

**IMPLICATIONS:** Every feature or module will have a planning document in natural language (covering features, UI, integrations) and a distilled README that serves as an ultra-compressed reference for future work.

**ALTERNATIVES CONSIDERED:** Relying solely on code output without documentation was rejected due to the risk of accumulating technical debt and losing understanding of the system.

## Decision 4: Three-Tier Documentation Compression System

**DECISION:** Aaron will use a staged compression approach for documentation: massive PRD (full technical detail) → planning docs (natural language) → README (ultra-distilled reference).

**CONTEXT:** This mirrors Aaron's overall compression philosophy and creates clear stages of information density that can be referenced depending on the context and need.

**DECIDED BY:** Aaron Mak Hoffman

**IMPLICATIONS:** Each stage serves a distinct purpose—the PRD for full context, planning docs for natural language understanding of features and workflows, and READMEs for quick reference and non-technical comprehension.

**ALTERNATIVES CONSIDERED:** Single-document approaches were rejected for not providing the right level of detail at the right time.

## Decision 5: Database-Driven Project Tracking and Website Auto-Updates

**DECISION:** Aaron will use an automated agent that scans chat history daily to update a database of active projects, which then automatically updates his website.

**CONTEXT:** Aaron wants project timelines to update automatically without manual intervention. The agent identifies what he's actively working on from chat history and maintains current/active/inactive status.

**DECIDED BY:** Aaron Mak Hoffman

**IMPLICATIONS:** Project timelines on Aaron's website stay synchronized with actual work activity. Items automatically become inactive if not mentioned in chat for a month.

**ALTERNATIVES CONSIDERED:** Manual project updates were replaced with this automated system. Aaron also explored using Zo's session state database but found his own approach worked better for his needs.