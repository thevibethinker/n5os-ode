

# B03_DECISIONS

---
created: 2025-11-13
last_edited: 2025-11-13
version: 1.0
provenance: meeting-2025-11-13-aaron-mak-hoffman
block_type: B03
---

# B03: Decisions Made

## Decision 1: Persona System for Contextual AI Behavior

**DECISION:** V uses dedicated personas (Vibe Operator, Vibe Builder, Vibe Writer, Vibe Teacher, Vibe Level Upper) with automatic switching rather than a single monolithic prompt, and embeds switching logic within persona definitions plus rules.
**CONTEXT:** Different tasks require fundamentally different AI orientations — navigation vs. code generation vs. writing vs. teaching. Persona switching allows the system to adopt the right "lens" organically during a workflow.
**DECIDED BY:** V (established practice, shared with Aaron)
**IMPLICATIONS:** Each persona carries its own context (e.g., Builder has anti-hallucination principles like "you are the AI, just interpret it"), reducing prompt bloat per interaction. Switching reliability improves with explicit persona IDs in rules.
**ALTERNATIVES CONSIDERED:** Aaron's approach of embedding everything in rules/prompts without persona switching — acknowledged as doing "roughly the same thing" but personas add a perspective layer on top.

## Decision 2: Three-Layer Information Architecture

**DECISION:** V organizes information in three tiers: raw data → content library (middle compression) → knowledge base ("sacred texts"), with information distilling upward through processing stages.
**CONTEXT:** Meeting intelligence, emails, and other inputs need progressive refinement to become actionable knowledge. The knowledge base represents the highest-fidelity, most curated information.
**DECIDED BY:** V (architectural choice, explained to Aaron)
**IMPLICATIONS:** Downstream systems (follow-up emails, CRM updates, go-to-market hypotheses) pull from the appropriate tier rather than always processing raw data. Prevents knowledge base pollution with unprocessed content.

## Decision 3: Session State Tracking via Conversation Database

**DECISION:** V tracks every Zo conversation in a structured database (conversations DB) with session state files, rather than relying solely on native RAG/chat history retrieval.
**CONTEXT:** Native chat history retrieval was found unreliable for referencing specific past conversations. A concrete database provides deterministic lookups versus "stochastic toss in the air" retrieval.
**DECIDED BY:** V (built and demonstrated the system)
**IMPLICATIONS:** Enables the build orchestrator pattern — spinning off worker conversations that can be tracked, referenced, and synthesized. Foundation for parallel task execution across multiple Zo threads.
**ALTERNATIVES CONSIDERED:** Aaron's approach of a daily agent that scrapes chat history into a database — similar goal, different mechanism (periodic batch vs. real-time session init).

## Decision 4: Build Orchestrator for Parallel Worker Threads

**DECISION:** V built an orchestrator that creates worker files and tracks them in a workspace, designed to spawn and coordinate multiple Zo conversations for parallel execution.
**CONTEXT:** Complex builds benefit from decomposition into independent worker threads. The orchestrator provides the coordination layer that Zo doesn't natively support well yet.
**DECIDED BY:** V (implemented, though constrained by platform limitations)
**IMPLICATIONS:** Parallel conversation execution is limited by Zo's current architecture — switching conversations mid-query stalls the previous one. V works around this by keeping multiple browser windows/tabs open simultaneously.

## Decision 5: No Customer-Facing Zo Deployments Yet

**DECISION:** Neither V nor Aaron is putting Zo-powered systems in front of customers at this stage.
**CONTEXT:** Both acknowledged Zo is "not ready for prime time" for customer-facing use. Aaron expressed temptation to pipe client communications through Zo sites but is holding back.
**DECIDED BY:** Mutual agreement (V and Aaron)
**IMPLICATIONS:** Current Zo usage remains internal/personal productivity. The threshold for customer deployment is reliability — "the level of personalization overrides the clunkiness" hasn't been consistently met yet.

## Decision (IMPLIED): Planning-First Approach to Vibe Coding

**DECISION:** Aaron's methodology of spending 3x longer on planning than building — with progressive compression from PRD → planning docs → technical implementation → README — was recognized by V as a significant unlock worth adopting.
**CONTEXT:** V acknowledged "I kind of just dove in" without structured planning, leading to technical debt that is "an absolute untangle." Aaron's approach of natural-language planning docs that a non-technical person can understand, followed by handing clean prompts to execution agents (Replit), reduced build times from 40-60 hours to ~3 hours.
**DECIDED BY:** V expressed strong intent to adopt ("that's going to be such a huge unlock")
**IMPLICATIONS:** Suggests V will restructure build workflows to include explicit planning artifacts with progressive distillation before execution.