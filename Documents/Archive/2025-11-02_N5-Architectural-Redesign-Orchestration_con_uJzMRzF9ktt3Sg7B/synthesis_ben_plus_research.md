# Synthesis: Ben's Velocity Principles + LLM Code Editing Research

## Ben's Core Framework: THINK (70%) → PLAN (20%) → EXECUTE (10%)

### The Squishy ↔ Deterministic Spectrum

**Ben's Key Insight:** Different parts of the system require different approaches.

- **Squishy Side (AI-appropriate):**
  - Brainstorming, ideation
  - Pattern recognition
  - Content transformation
  - Summarization

- **Deterministic Side (Script-appropriate):**
  - File operations
  - Exact transformations
  - Scheduled jobs
  - State management

**Critical Rule:** Don't edit existing complex code with LLMs. Create separate orchestration points instead.

## Why LLM Code Editing Is Risky (From Conversation + Research)

### The Fundamental Problem
LLMs can't make **line-based edits** effectively. They either:
1. Rewrite everything (high risk of breaking things)
2. Require you to specify exact lines (defeats the purpose)

### Research-Backed Findings

**From "Can It Edit?" (arXiv 2312.12450):**
- LLMs struggle with precise code editing instructions
- Success rate for editing existing code: 37% (vs 63% for new code generation)
- Editing introduces subtle bugs that new generation doesn't

**From "Refactoring vs Refuctoring" (CodeScene):**
- AI refactoring breaks code **63% of the time** without fact-checking
- Common failures: drops branches, inverts boolean logic, breaks scope (e.g.,  in JS)
- These bugs are **subtle and hard to spot** in code review

**From Princeton/Cornell studies:**
- 40% of AI-generated code contains security vulnerabilities
- 27-30% of AI code in GitHub has CWEs (Common Weakness Enumeration)
- Editing existing code has HIGHER failure rate than new generation

## V's Correct Instincts (Validated by Ben + Research)

✅ **Separate orchestration points** - Ben explicitly endorsed this
✅ **File markers for coordination** - Matches producer/consumer pattern
✅ **Slowing down for planning** - Ben's 70% THINK time
✅ **Treat AI as entity with preferences** - Not rule-based system

## Where V Should Calibrate (Ben's Authority)

⚠️ **SQLite + YAML > Folders for data** - Ben emphasized this multiple times
⚠️ **Job queues (huey) > File watchers** - More deterministic
⚠️ **Scripts call Zo API** - Not pure Zo workflows for critical paths  
⚠️ **Planning prompts as DNA** - Obsess over these, version them
⚠️ **Prompting discipline** - DON'T say "use LLM", DO say "transform X to Y"

## The Architectural Principle (P36)

**Core Directive:** Because LLMs editing existing code is fundamentally risky (63% failure rate for refactoring, 37% for general edits), use **separate orchestration points** instead of inline code modification.

**Pattern:** Producer/Consumer with File Markers
- DON'T: Ask Zo to edit  
- DO: Create  that consumes outputs

**Why This Works:**
- Independent failure modes (one breaks ≠ both break)
- Clear state management via files
- Easier to test/validate
- Matches LLM strengths (new code) vs weaknesses (editing)

