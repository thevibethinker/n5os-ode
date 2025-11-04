# N5OS Lite Quick Start

**Get productive in 15 minutes**

---

## Your First 15 Minutes

### Minute 1-3: Understand the Core Idea

N5OS Lite is a framework for **thinking, planning, and building with AI**. It provides:
- **Personas** - Specialized modes for different work (Builder, Strategist, etc.)
- **Prompts** - Reusable workflows you can invoke
- **Principles** - Architectural guidelines (reference by ID: P1, P15, etc.)
- **Lists** - Structured knowledge in JSONL format

**Key Insight:** The bottleneck isn't code generation—it's clear thinking. N5OS helps you think clearly, then build quickly.

### Minute 4-6: Run Your First Workflow

**Task:** Plan a simple project

1. **Tell your AI:**
   ```
   Load Prompts/planning_prompt.md and help me plan a personal task tracker
   ```

2. **The AI will guide you through:**
   - **Think:** What problem are we solving? Why now?
   - **Plan:** What should we build? How will it work?
   - **Execute:** Let's build it step by step

3. **Watch for:**
   - The AI applying the Think→Plan→Execute framework
   - Questions about trap doors (irreversible decisions)
   - Progress reporting with actual percentages

### Minute 7-9: Try Persona Switching

**Task:** Get specialized help

1. **For building:**
   ```
   Switch to Builder persona and implement the task tracker we just planned
   ```

2. **For strategy:**
   ```
   Switch to Strategist persona and analyze 3 different approaches to task tracking
   ```

3. **For learning:**
   ```
   Switch to Teacher persona and explain how JSONL works
   ```

**Notice:** Each persona has different expertise and communication style.

### Minute 10-12: Use the List System

**Task:** Track tools you discover

1. **Add an entry:**
   ```
   Add ripgrep to my tools list. It's a fast grep alternative written in Rust.
   ```

2. **Query the list:**
   ```
   Show me all CLI tools in my tools list
   ```

3. **See the power:**
   - Lists become your external memory
   - AI can query and update them
   - Single source of truth (P2 principle)

### Minute 13-15: Apply Principles

**Task:** Reference architectural guidelines

1. **During work, reference principles:**
   ```
   I'm about to delete these files. What does P5 say about safe file operations?
   ```

2. **Get principle-based guidance:**
   ```
   Apply P15 (Complete Before Claiming) to this progress report
   ```

3. **Understand the value:**
   - Principles encode lessons learned
   - Reference by ID for quick guidance
   - Build shared vocabulary with your AI

---

## Common Workflows

### Building a New System

```
1. Load planning prompt
2. Switch to Builder persona
3. Follow Think→Plan→Execute
4. Reference P28 (Plan DNA) - quality upstream matters
5. Use P15 for honest progress reporting
```

### Research and Analysis

```
1. Switch to Researcher persona
2. Gather information
3. Switch to Strategist persona
4. Analyze patterns and generate options
5. Apply P27 (Nemawashi) - explore alternatives
```

### Debugging

```
1. Switch to Debugger persona
2. Systematic verification (5-phase methodology)
3. Map findings to principle violations
4. Get evidence-based fixes
```

### Writing and Documentation

```
1. Load generate-documentation prompt
2. Switch to Writer persona  
3. Apply P1 (Human-Readable First)
4. Get clear, accessible content
```

---

## Essential Commands

### Prompt Management
```
"List available prompts"
"Load Prompts/planning_prompt.md"
"Execute prompt Prompts/close-conversation.md"
```

### Persona Switching
```
"Switch to Builder persona"
"Activate Strategist mode"
"Use Teacher persona to explain X"
```

### List Operations
```
"Add [item] to [list]"
"Query [list] for [criteria]"
"Show all entries in [list] tagged [tag]"
```

### Principle Reference
```
"What does P15 say about progress reporting?"
"Apply P27 (Nemawashi) to this decision"
"List principles related to quality"
```

---

## Understanding Personas

### When to Use Each

**Operator (Default):**
- General task execution
- File operations
- Routing to specialists
- When unsure which persona to use

**Builder:**
- Implementing systems
- Writing scripts
- Building infrastructure
- Refactoring code

**Strategist:**
- Strategic decisions
- Pattern analysis
- Generating options
- Framework building

**Architect:**
- Designing personas
- Creating prompts
- System blueprints
- Meta-design work

**Writer:**
- Documentation
- Content creation
- Technical writing
- User guides

**Teacher:**
- Learning new concepts
- Explaining systems
- Clarifying technical topics
- Pushing understanding boundaries

**Debugger:**
- Verification
- Testing
- Finding violations
- Quality assurance

**Researcher:**
- Information gathering
- Due diligence
- Competitive analysis
- Deep dives

---

## Essential Principles (Top 10)

Learn these first:

1. **P1 - Human-Readable First:** Write for humans, derive machine formats
2. **P2 - Single Source of Truth:** Each fact lives in one place
3. **P5 - Safety & Determinism:** Never overwrite without confirmation
4. **P7 - Dry-Run by Default:** Preview changes before committing
5. **P8 - Minimal Context:** Keep things self-contained
6. **P15 - Complete Before Claiming:** Report honest progress (most critical!)
7. **P23 - Identify Trap Doors:** Spot irreversible decisions early
8. **P27 - Nemawashi:** Explore 2-3 alternatives before committing
9. **P32 - Simple Over Easy:** Choose few concepts over convenient abstractions
10. **P36 - Orchestration:** Use multiple personas for complex work

---

## Power Tips

### 1. Combine Personas
```
"Strategist: analyze options for data storage
 Then Builder: implement the chosen option"
```

### 2. Chain Prompts
```
"Use planning prompt to design this feature,
 then generate documentation,
 then close this conversation"
```

### 3. Create Rules
Set persistent preferences:
```
"Create a rule: Before any significant building work, load planning prompt"
```

### 4. Build on Lists
Your lists become reusable knowledge:
```
"Query my tools list for Rust CLI tools,
 then research the top 3 and add details"
```

### 5. Reference Everything
Build a web of knowledge:
```
"Document this decision in decisions.jsonl
 Reference P23 (trap doors) and P27 (nemawashi)
 Link to the planning document"
```

---

## What to Build First

### Starter Projects

**1. Personal Dashboard**
- Track tools, resources, ideas
- Practice list operations
- Build with Builder persona

**2. Project Template**
- Create reusable project structure
- Apply planning prompt
- Document with principles

**3. Custom Prompt**
- Design workflow you repeat often
- Follow prompt authoring guide
- Test in fresh thread (P12)

**4. Knowledge Base**
- Organize your learning
- Use lists for resources
- Build searchable system

---

## Next Steps

1. **Read ARCHITECTURE.md** - Understand the design philosophy
2. **Browse principles/** - Learn the full principle set
3. **Explore prompts/** - See all available workflows
4. **Customize** - Add your own prompts, lists, rules
5. **Share** - Contribute improvements back to the community

---

## Getting Unstuck

### "I don't know which persona to use"

Start with Operator. It will route you to the right specialist.

### "The AI isn't following principles"

Explicitly reference them: "Apply P15 to this" or load planning prompt.

### "My workflow isn't working"

Test in a fresh conversation thread (P12) to find missing dependencies.

### "I'm building but making no progress"

Load planning prompt. You probably skipped the Think phase.

### "The system feels overwhelming"

Start with just 3 things: Planning prompt, Operator persona, P15 principle.

---

## Resources

- `README.md` - System overview
- `ARCHITECTURE.md` - Design philosophy
- `principles/principles_index.yaml` - All principles with descriptions
- `system/` - Detailed documentation
- GitHub Discussions - Ask questions, share workflows

---

**You're ready! Start building with clearer thinking and better execution.**

*"The constraint isn't code generation—it's strategic thinking."*

---

**Version:** 1.0  
**Last Updated:** 2025-11-03
