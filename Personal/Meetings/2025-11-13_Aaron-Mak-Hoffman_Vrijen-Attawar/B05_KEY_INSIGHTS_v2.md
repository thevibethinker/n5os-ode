---
created: 2025-11-13
last_edited: 2025-11-14
version: 1.0
---

# B05: Key Insights & Principles

## Architectural Insights

### Three-Tier Information Compression
**Pattern:** Both independently developed identical information architecture:
- **Raw:** Unprocessed input (transcripts, full PRDs)
- **Processing Layer:** Organized/annotated (meeting blocks, planning docs)
- **Sacred Texts/Readmes:** Ultra-distilled (high-authority, minimal)

**Implication:** This appears to be fundamental to maintainable systems. Compression stages reduce cognitive load and enable different stakeholders to engage at appropriate abstraction levels.

### Personas as Lenses vs. Modes
**Distinction:** Vrijen frames personas as "perspectives on the underlying system" rather than separate systems. This reframe clarifies why Aaron's "embedded prompts" approach works—the question isn't "which persona" but "what principle set should I apply to this task."

**Practical:** Personas work best when explicitly constrained with principle sets that guide decision-making, not just tone-shifting.

## Planning & Technical Debt

### Planning ROI (Aaron's 70/30 Ratio)
**Finding:** Allocating 70% of project time to planning and 30% to execution dramatically reduces technical debt.
**Mechanism:** 
- Natural-language plan review catches design flaws before coding
- Technical implementation docs written pre-build (acts as spec)
- Readme ensures non-technical reviewer can validate approach

**Vrijen's Observation:** This is conceptually identical to his information architecture—compression requires patience upfront.

### Vibe Coding Debt Accumulation
**Warning:** Rapid AI-assisted coding without planning creates "absolute untangle" technical debt. Vrijen: "If you build up a lot of technical debt, it is an absolute untangle."

**Implication:** Zo's power to iterate fast can mask structural problems until they become irreversible.

## Reliability & Customer-Facing Readiness

### Personalization > Absolute Reliability (for Internal Use)
**Finding:** For personal/internal systems, extreme personalization is worth occasional failures. For customer-facing, reliability threshold is much higher.

**Vrijen's Framing:** "The level of personalization overrides the clunkiness of it, like, not working right every single time"

**Implication:** Zo systems are ideal for personal knowledge work but require different architecture for customer delivery.

### Automatic Persona Switching Reliability
**Question:** Can automatic persona switching be made reliable? **Answer:** Yes, with explicit rule-based triggers. Rule-based switching (IF user asks to learn THEN switch to Teacher) is more reliable than implicit switching.

## Integration & Automation Patterns

### Embedded Prompts > Persona Switching for Recurring Tasks
**Aaron's Finding:** Embedding reusable prompts into rules/agents is more reliable than relying on automatic persona switching because "you can't pull out of a persona." Prompt-based approach maintains context across multiple steps.

**Use Case:** Recurring workflows that need consistent behavior (e.g., email processing, data classification).

### Documentation-First vs. Code-First
**Aaron's Approach:** Treat documentation as primary source of truth; keep everything in docs (not GitHub-first). When code changes, explicitly prompt AI to update docs.

**Trade-off:** Gains documentation quality and human understanding at cost of requiring discipline about doc updates and missing version control benefits.

## Strategic Choices

### When to Use Personas
✓ Multiple distinct lenses on same underlying work  
✓ Context-switching between roles  
✓ Teaching/explanation vs. execution  
✗ Recurring automated tasks (use embedded prompts instead)  
✗ Tasks requiring multi-step consistency  

### When AI System is Ready for Production
- ✓ Internal/personal use: personalization > occasional failure
- ✗ Customer-facing: requires reliability engineering, fallback strategies, explicit SLAs
- Current Zo State: "Not ready for prime time" (Vrijen) / "too nervous" (Aaron for client comms)


