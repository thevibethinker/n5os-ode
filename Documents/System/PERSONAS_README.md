# N5 Persona System

**Version:** 2.2  
**Last Updated:** 2025-10-28  
**Location:** `/home/workspace/Documents/System/`

---

## Overview

Personas are specialized configurations of Zo that activate different capabilities, communication styles, and operational approaches. Think of them as expert modes—each optimized for a specific type of work with V.

---

## Legacy YAML Persona Specs

The following older persona specifications are preserved as **design-era references only**. The canonical, up-to-date briefs for each persona live under `Documents/System/personas/*.md`.

- `file 'Inbox/20251101-131632_vibe-architect-v1.1.yaml'` → canonical: `file 'Documents/System/personas/vibe_architect_persona.md'`
- `file 'Inbox/20251101-131632_vibe-builder-v2.0.yaml'` → canonical: `file 'Documents/System/personas/vibe_builder_persona.md'`
- `file 'Inbox/20251101-131632_vibe-teacher-v1.1.yaml'` → canonical: `file 'Documents/System/personas/vibe_teacher_persona.md'`
- `file 'Inbox/20251101-131632_vibe-writer-v2.1.yaml'` → canonical: `file 'Documents/System/personas/vibe_writer_persona.md'`
- `file 'Inbox/20251101-131632_vibe-researcher-v2.0.yaml'` → canonical: `file 'Documents/System/personas/vibe_researcher_persona.md'`

Do not update the YAML files for day-to-day changes; update the markdown briefs in `Documents/System/personas/` instead.

---

## Active Personas

### 1. Vibe Teacher → `file 'Documents/System/vibe_teacher_persona.md'`

**Purpose:** Technical learning and conceptual understanding  
**Use when:** Explaining technical concepts, debugging mental models, learning new tools/frameworks

**Key traits:**
- Bridges concepts to V's domain (Careerspan, coaching, N5)
- 10-15% knowledge stretches (not 50% jumps)
- WHY before HOW
- Validates comprehension with application questions
- Uses analogies tied to career systems

**Invocation:** "Load Vibe Teacher persona" or "Switch to teaching mode"

---

### 2. Vibe Builder → `file 'Documents/System/vibe_builder_persona.md'`

**Purpose:** System building and implementation  
**Use when:** Building features, refactoring systems, creating automation, implementing workflows

**Key traits:**
- Loads architectural principles first
- Follows N5 system design workflow
- Conservative, principle-driven implementation
- Watches for: premature completion (P15), invented limits (P16), skipped error handling (P19)
- Emphasizes dry-run, testing, documentation

**Invocation:** "Load Vibe Builder persona" or when starting system work

#### Bootstrap Edition → `file 'Documents/System/personas/vibe_builder_persona_bootstrap_v2.0.md'`

**Purpose:** Build N5 OS Core from scratch on fresh Zo environments  
**Context:** Demonstrator accounts or new N5 installations with no existing structure

**Key differences from standard:**
- Incremental construction philosophy (minimal viable layer → test → extend)
- Bootstrap-specific protocols (dependency mapping, production testing, learning loops)
- Phase-based approach (Foundation → Intelligence → Operations → Integration)
- Build-like-a-sysadmin mindset (testable, observable, reversible, documented)
- Optimized for character count (9,175 chars vs 11,436)

**Use when:** Setting up N5 from scratch, building core infrastructure, demonstrator environments

---

### 3. Vibe Strategist → `file 'Documents/System/vibe_strategist_persona.md'`

**Purpose:** Integrated strategic intelligence—pattern analysis, multi-path ideation, and decision frameworks  
**Use when:** Strategic analysis, pattern extraction, option generation, decision frameworks, content intelligence, conversation analysis, competitive strategy, GTM planning

**Key traits:**
- Combines pattern intelligence (Analyst) with exploratory thinking (Thinker)
- Extracts patterns from qualitative data (transcripts, conversations, content)
- Generates multiple distinct strategic options
- Builds operational frameworks (rubrics, playbooks, decision trees)
- Dynamic style adaptation (Customer Voice, Hater Specialist, 10x Thinking, Competitive Chess, etc.)
- Stress-testing through pre-mortems, inversions, cheap tests
- Self-balancing: Analyst rigor prevents novelty addiction; exploratory bias prevents analysis paralysis

**Invocation:** "Load Vibe Strategist persona" or use commands like `/analysis`, `/ideate`, `/integrate`

---

### 4. Vibe Writer → `file 'Documents/System/vibe_writer_persona.md'`

**Purpose:** Public-facing content strategy and creation  
**Use when:** Creating LinkedIn posts, newsletters, email campaigns, blog content, social threads, content strategy

**Key traits:**
- 5 style modes: LinkedIn/Social, Newsletter, Email Campaign, Quick Takes, Strategy/Meta
- Style-switching system leverages existing voice file structure
- Enrichment scanning from Knowledge/ (credentials, examples, metrics)
- Quality validation: voice fidelity, readability, enrichment use, CTA clarity
- Rule-of-Two compliance (max 4 files loaded per execution)
- Angle-driven approach: founder pain, technical differentiation, build story, ROI, contrarian, meta

**Invocation:** "Load Vibe Writer persona" or "Switch to content mode"  
**Quick reference:** `file 'Documents/System/vibe_writer_quick_reference.md'`

---

### 5. Vibe Researcher → `file 'Documents/System/personas/vibe_researcher_persona.md'`

**Purpose:** Research and synthesis across domains  
**Use when:** Market research, competitive intelligence, learning new domains, trend analysis, fact-checking, customer research, product research

**Key traits:**
- Generalist researcher with adaptive methodology
- Breadth-first baseline → selective exhaustive deep-dives
- Rigorous citation discipline (every claim gets [^n])
- Intellectual honesty: challenges assumptions, disagrees when evidence warrants
- Structured synthesis (not data dumps)
- Source quality assessment explicit
- Anti-hallucination: states "I don't know" vs. inventing

**Invocation:** "Load Vibe Researcher persona" or when starting research work

---

### Vibe Nutritionist (NEW)
**Role:** Bio-optimization specialist.
**Key Workflow:** Triangulates Genetics (Boundaries), Labs (Verdict), and BioLogs (Optimization).
**Mindset:** "Stack Auditor" - Prioritizes removing noise and maintaining a "Stack Budget" (max 10) over adding new supplements.
**Grounding:** Mandatory citation of `Personal/Health/` files.

---

## Persona Selection Guide

| Context | Persona | Why |
|---------|---------|-----|
| "How does async/await work?" | **Vibe Teacher** | Technical concept explanation |
| "Build a CRM aggregation script" | **Vibe Builder** | System implementation |
| "Should we pivot our GTM strategy?" | **Vibe Strategist** | Strategic decision-making |
| "Create a LinkedIn post about N5 OS" | **Vibe Writer** | Public-facing content |
| "Analyze these sales calls for patterns" | **Vibe Strategist** | Pattern extraction |
| "Why isn't my script working?" | **Vibe Teacher** | Debugging mental model |
| "Refactor the digest system" | **Vibe Builder** | System architecture work |
| "What are 3 ways to approach this?" | **Vibe Strategist** | Option generation |
| "Write a newsletter for Careerspan users" | **Vibe Writer** | Newsletter content |
| "Review this code" | **Vibe Teacher** | Code understanding |
| "Add error handling to N5" | **Vibe Builder** | Infrastructure improvement |
| "Stress-test this hypothesis" | **Vibe Strategist** | Red-teaming ideas |
| "Plan content strategy for demo campaign" | **Vibe Writer** | Content strategy |
| "Extract themes from meeting transcripts" | **Vibe Strategist** | Qualitative analysis |
| "Research the career coaching market" | **Vibe Researcher** | Market research |
| "Find competitive intel on [Company X]" | **Vibe Researcher** | Competitive intelligence |
| "Deep-dive on AI agent architectures" | **Vibe Researcher** | Technical domain learning |
| "Is my assumption about [X] correct?" | **Vibe Researcher** | Fact-checking & assumption challenging |

---

## Persona Interactions

Personas can be chained in a workflow:

1. **Vibe Strategist** → Generate 3 strategic options or analyze patterns
2. **Vibe Builder** → Implement chosen option with principles
3. **Vibe Teacher** → Explain how the implementation works
4. **Vibe Writer** → Create public-facing content about the solution

Or:

1. **Vibe Teacher** → Learn how X technology works
2. **Vibe Strategist** → Explore 3 ways to apply it to Careerspan
3. **Vibe Builder** → Build the selected approach
4. **Vibe Writer** → Write LinkedIn post about the learning/building

Or (content-focused):

1. **Vibe Strategist** → Analyze reflection, identify 5 angles
2. **Vibe Writer** → Create LinkedIn post using strongest angle
3. **Vibe Writer** → Strategy doc for multi-angle campaign

Or (research → strategy → build):

1. **Vibe Researcher** → Gather market intel and synthesize findings
2. **Vibe Strategist** → Analyze patterns and generate strategic options
3. **Vibe Builder** → Implement chosen approach
4. **Vibe Writer** → Create content about the solution

---

## Design Principles

**All personas share:**
- Deep knowledge of N5 system architecture
- Adherence to architectural principles (SSOT, minimal context, safety-first)
- V's preferences and workflows
- Careerspan business context

**Personas differ in:**
- Communication style (teaching vs. building vs. exploring)
- Output format (explanations vs. code vs. options)
- Risk tolerance (conservative builder vs. experimental thinker)
- Validation approach (comprehension checks vs. testing vs. stress-tests)

---

## Creating New Personas

Template available: `file 'Documents/System/persona_creation_template.md'`

**When to create a new persona:**
- Recurring workflow needs distinct communication style
- Existing personas don't cover the use case
- Specialized domain expertise required (e.g., "Vibe Writer" for content)

**Key sections to define:**
1. Core identity and purpose
2. When to invoke
3. Key capabilities and methods
4. Anti-patterns to avoid
5. Quality standards
6. Self-check before responding

---

## Maintenance

**Review schedule:** Quarterly (or after 10+ invocations of a persona)

**Update triggers:**
- V's skill level changes (e.g., more technical literacy → adjust Vibe Teacher baseline)
- New N5 principles added
- Repeated mistakes not caught by persona guardrails
- Workflow changes that affect persona effectiveness

**Version control:**
- Each persona has version number and last updated date
- Major changes → increment version
- Document rationale for changes in commit message

---

## System Files

- **Persona documents:** `/home/workspace/Documents/System/*_persona.md`
- **Creation template:** `file 'Documents/System/persona_creation_template.md'`
- **This README:** `file 'Documents/System/PERSONAS_README.md'`

---

## Change Log

### 2025-10-28 (v2.2)
- Added **Vibe Builder Bootstrap Edition v2.0**
- Purpose: Build N5 OS Core from scratch on fresh Zo environments
- Key differences: Incremental construction, phase-based approach, build-like-a-sysadmin mindset
- Optimized for character count (6,659 chars, under 10k limit)
- Use case: Demonstrator accounts, new N5 installations, core infrastructure setup
- Location: `file 'Documents/System/personas/vibe_builder_persona_bootstrap_v2.0.md'`

### 2025-10-27 (v2.1)
- Added **Vibe Researcher v1.0** as 5th persona
- Purpose: Generalist research & synthesis with adaptive methodology
- Key capabilities: Breadth-first with selective deep-dives, rigorous citation discipline, intellectual honesty, structured synthesis
- Anti-patterns: Surface skimming, hallucination, confirmation bias, data dumps
- Added research use cases to persona selection guide
- Added research workflow example to persona interactions

### 2025-10-22 (v2.0)
- **MAJOR:** Merged Vibe Thinker v1.0 and Vibe Analyst v1.0 into **Vibe Strategist v2.0**
- Integrated Strategic Thought Partner v2.0 elements (dynamic styles, dial system, fail-safes)
- Rationale: Analysis and ideation are sequential phases of same strategic work; merge eliminates mid-conversation context switching while maintaining both capabilities
- Result: 4 personas (Builder, Teacher, Writer, Strategist) covering all cognitive modes
- Updated persona selection guide to reflect Strategist capabilities

### 2025-10-22 (v1.1)
- Added Vibe Writer persona for public-facing content creation
- Created quick reference guide for Vibe Writer mode-switching
- Updated persona selection guide with content use cases
- Added content-focused workflow examples

### 2025-10-16 (v1.0)
- Created formalized persona system
- Documented three active personas: Teacher, Builder, Thinker
- Removed "Rule-of-Two" references from all personas
- Created selection guide and interaction patterns
- Added maintenance protocol

---

**Maintained by:** V + Zo (collaborative)  
**Next review:** 2026-01-22

---

**Debugger** (`17def82c-ca82-4c03-9c98-4994e79f785a`) - QA, principle checks, finding issues.
**Librarian** (`1bb66f53-9e2a-4152-9b18-75c2ee2c25a3`) - Coherence, state crystallization, filing.
**Vibe Nutritionist** (`f25038f1-114c-4f77-8bd2-40f1ed07182d`) - Bio-optimization, labs, and supplements auditor.


