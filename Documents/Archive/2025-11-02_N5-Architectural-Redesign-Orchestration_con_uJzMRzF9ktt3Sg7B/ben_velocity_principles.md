# Ben Guo's Velocity Coding Principles
**Source:** Velocity Coding Talk (Oct 2025) + Ben x V conversation (Oct 31, 2025)

## Core: THINK (70%) → PLAN (20%) → EXECUTE (10%)

### THINK Phase
- Simulation over doing
- Identify trap doors (hard to reverse)
- Evaluate trade-offs
- Spike/prototype to feel options
- Sleep on big decisions

### PLAN Phase  
- **OWN THE PLANNING PROCESS** - don't delegate to AI
- Planning prompt = DNA of codebase ("Bible")
- Obsess over plan (30-60 min normal)
- Don't settle for first AI output
- Use structured formats (RST > Markdown)

### EXECUTE Phase
- Fast models, mechanical generation
- By this point, quality already determined
- Mistakes made/avoided in Think+Plan phases

## The Squishy ↔ Deterministic Spectrum

1. **Squishy LLM + Squishy Format** (Markdown) - exploration only
2. **Squishy LLM + Structured Format** (YAML, CSV) - sweet spot  
3. **Structured Script + Structured Format** (Python + SQLite) - maximum determinism

**Key:** Gravitate toward determinism for stability over time.

## Critical Rules

### Never Lose "Feel" for Code
- Look at code always
- Develop spidey sense for dark forests, brittle parts
- If generating more code, should feel MORE TIRED
- "Code that's nice will grow by itself with AI"

### LLM Prompting
- DON'T say "use an LLM" (triggers external API calls)
- DO say "use your internal knowledge"
- DO say "transform this to that"
- Prompting is dark art - experiment

### File Formats
- **YAML** > JSON (easier for LLMs, less syntax)
- **SQLite** for organizing data (not folders)
- **CSV** for simple tabular data

### Architecture Patterns
- **Job queues** (Ben uses ) for workers
- **Scripts call Zo API** for agentic steps in deterministic flow
- **Separate orchestration** (don't edit existing code)
- **File markers** for coordination

## Three Tiers of Slowdown

1. Doing wrong thing (worst)
2. Doing it wrong way (bites later) 
3. Doing it badly (poor implementation)

Prevention: Proper Think→Plan→Execute sequence

## What Ben Validates for V

✅ Separate orchestration (workers, queues)
✅ File markers for coordination  
✅ Producer/consumer patterns
✅ SQLite for data
✅ YAML for structured text
✅ Gradual shift toward determinism

## Where V Should Adjust

⚠️ Stop saying "use LLM" - just instruct directly
⚠️ Use explicit job queues (huey) not file scanning
⚠️ Have scripts call Zo API for agentic steps
⚠️ Invest MORE in planning prompts (they're DNA)
⚠️ Shift from folders to SQLite+YAML for data
⚠️ Maintain "feel" discipline - review all code

## Where V's Instincts Are RIGHT

✅ Editing existing code is risky
✅ Need structured workflows  
✅ Separate orchestration points
✅ File markers for state
✅ Treat AI as entity, not rule-based system
✅ Slowing down for planning

