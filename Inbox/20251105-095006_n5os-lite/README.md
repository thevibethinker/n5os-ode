# N5OS Lite

**A lightweight, portable AI operating system for Zo Computer**

N5OS Lite is a streamlined system for building, organizing, and operating with AI assistance. It provides planning frameworks, architectural principles, specialized personas, and organizational patterns designed for human-AI collaboration.

## What Is This?

Think of N5OS Lite as an "operating system" for your AI assistant. It provides:

- **Planning Framework**: Structured approach to building systems with AI
- **Architectural Principles**: Design guidelines that prevent common pitfalls
- **Specialized Personas**: Different AI modes for different types of work
- **Organizational System**: File structure and preferences management
- **Safety Guardrails**: Protection mechanisms and quality standards

## Quick Start

### 1. Choose Your Setup

**Option A: Full Structure** (Recommended)
```bash
# Copy to your workspace root
cp -r n5os-lite/* /your/workspace/
```

**Option B: Selective Components**
```bash
# Just the essentials
cp n5os-lite/prompts/planning_prompt.md /your/workspace/Prompts/
cp -r n5os-lite/principles /your/workspace/
```

**Option C: Reference Only**
Keep N5OS Lite as reference, adopt patterns gradually.

### 2. Load Planning Framework

When starting significant work with AI:

```
Load and apply file 'prompts/planning_prompt.md'
```

This activates Think→Plan→Execute methodology and key architectural principles.

### 3. Use Specialized Personas

When you need specific expertise:

- **System Operator**: General coordination and execution
- **System Builder**: Building scripts, workflows, infrastructure
- **System Strategist**: Strategic analysis and pattern extraction
- **Content Writer**: Clear, concise content creation

Example: "Switch to Builder persona to implement this design"

### 4. Apply Principles

Reference principles by ID in conversations:

- "Follow P15 - report honest progress not premature completion"
- "Apply P7 - show me dry-run before executing"
- "Use P36 orchestration pattern for this multi-domain work"

## Core Components

### Planning Framework (`prompts/planning_prompt.md`)

Tactical planning approach based on:
- **70% Think + Plan**: Understand deeply, explore alternatives
- **20% Review**: Verify, test, check edge cases  
- **10% Execute**: Generate from plan, move fast

Includes guidance on:
- Squishy ↔ Deterministic spectrum
- Trap door identification (irreversible decisions)
- Refactor vs. rewrite decisions
- Quality bars and production testing

### Architectural Principles (`principles/`)

9 core principles covering:
- **P1: Human-Readable First** - Prose before structure
- **P2: Single Source of Truth** - One canonical location per fact
- **P5: Anti-Overwrite** - Safety and versioning
- **P7: Dry-Run by Default** - Verify before commit
- **P15: Complete Before Claiming** - Honest progress reporting
- **P36: Orchestration Pattern** - Multi-domain coordination
- **P37: Refactor Pattern** - Improving existing systems

See `principles/principles_index.yaml` for full list.

### Specialized Personas (`personas/`)

Four personas for different work modes:

**System Operator** - Execution and coordination
- File operations and navigation
- Risk assessment
- Task routing
- State tracking

**System Builder** - Implementation
- Scripts and workflows
- Infrastructure building
- Quality reviews
- Production deployment

**System Strategist** - Analysis and strategy
- Pattern extraction
- Option generation
- Framework building
- Strategic decisions

**Content Writer** - Communication
- Documentation
- Meeting notes
- Clear, concise content
- Direct voice

### System Organization (`system/`)

Guides for:
- **Directory Structure**: Recommended workspace layout
- **Naming Conventions**: Consistent naming patterns
- **Protection System**: Safeguarding critical directories

### Rules System (`rules/`)

Framework for defining persistent AI behavior preferences:
- Always-applied rules
- Conditional rules
- Rule categories and patterns
- Testing and management

## Usage Patterns

### Building New System

```
1. Load planning prompt
2. Switch to Builder persona
3. Apply Think→Plan→Execute framework
4. Follow P15 for progress reporting
5. Use P7 dry-run before destructive ops
```

### Strategic Analysis

```
1. Switch to Strategist persona
2. Provide data for analysis
3. Request pattern extraction
4. Get 3-5 distinct options with trade-offs
5. Receive actionable framework
```

### Complex Multi-Domain Work

```
1. Switch to Operator persona
2. Request P36 orchestration
3. Operator coordinates specialists
4. Each phase has clear success criteria
5. Operator integrates results
```

## Key Concepts

### Think → Plan → Execute

Time allocation framework:
- **40% Think**: Understand problem, explore alternatives
- **30% Plan**: Write spec, define criteria, document assumptions
- **10% Execute**: Generate code, move fast
- **20% Review**: Test everything, verify all criteria

### Squishy ↔ Deterministic Spectrum

**Zone 1** (Squishy): Markdown, exploration, brainstorming
**Zone 2** (Sweet Spot): YAML/CSV, structured AI output  
**Zone 3** (Deterministic): Python + SQLite, critical paths

Guideline: Gravitate toward determinism for stability.

### Trap Doors

Irreversible or high-cost-to-reverse decisions:
- Database choice (SQLite vs PostgreSQL)
- File format (JSONL vs SQLite vs YAML)
- Script language (Python vs Shell vs Node)

When you hit one: STOP, explore 2-3 alternatives, document decision.

### Nemawashi

Japanese concept: Explore 2-3 alternatives explicitly before deciding.

Prevents:
- Premature convergence
- Missed better options
- Undocumented trade-offs

## Best Practices

### 1. Load Planning Prompt Early
For any significant system work, load the planning prompt first. It's the foundation.

### 2. Report Honest Progress
Never say "done" when 60% complete. Use "X/Y complete (Z%). Remaining: [list]".

### 3. Dry-Run Before Destructive Ops
Always preview bulk operations or irreversible changes. Use `--dry-run` flags.

### 4. Apply Principles Explicitly
Reference principles by ID (P1, P15, etc.) to ensure consistent application.

### 5. Use Right Persona for the Job
Operator for coordination, Builder for implementation, Strategist for analysis, Writer for content.

### 6. Document Trap Door Decisions
When making irreversible decisions, use the trap door template to document reasoning.

## Customization

N5OS Lite is a starting point, not a rigid system:

- **Adapt Directory Structure**: Match your workflow
- **Add Custom Principles**: Document your own patterns
- **Create New Personas**: For specialized domains
- **Extend Rules**: Add project-specific preferences

## Philosophy

N5OS Lite is built on these beliefs:

1. **Code Is Free, Thinking Is Expensive**: AI generates code easily; your strategic thinking is the constraint.

2. **Simple Over Easy**: Choose disentangled designs over convenient ones.

3. **Maintenance Over Organization**: Build detection and routing, don't just organize.

4. **Human-Readable First**: Prose and markdown before JSON skeletons.

5. **Quality Comes from Planning**: All code quality comes from planning quality. Execution is mechanical.

## Getting Help

### Common Issues

**Q: Planning prompt seems too heavy for simple tasks**
A: Don't load it for tactical operations. It's for significant system work only.

**Q: Too many principles to remember**
A: Start with P1, P2, P15, P36. Add others as patterns emerge.

**Q: Personas feel constraining**
A: They're modes, not rigid roles. Blend as needed. Operator is default.

**Q: Directory structure doesn't fit my workflow**
A: Customize it! Structure should serve you, not constrain you.

### Further Reading

- `ARCHITECTURE.md` - Design philosophy and system architecture
- `prompts/planning_prompt.md` - Complete planning framework
- `principles/principles_index.yaml` - All principles with summaries
- `system/directory_structure.md` - Detailed organization guide

## Version

**N5OS Lite v1.0**  
Extracted and sanitized for demonstration purposes  
Created: 2025-11-03

## License

Use freely. Adapt to your needs. Share improvements.

---

*Built for human-AI collaboration. Optimized for thinking, not just coding.*
