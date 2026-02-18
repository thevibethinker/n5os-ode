---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_WwjnyDfYInMgpQas
---

# The Decomposition Pattern: V's Universal Build Method

## The Pattern

This is how non-technical people build technical systems:

1. **I have a need** — Articulate what you want clearly
2. **What are the blocks?** — Ask AI to decompose into primitives  
3. **Build each block** — One conversation per component
4. **Connect the blocks** — Assembly conversation
5. **Test and refine** — Iteration until it works

## Real Example: Flight Search System

**Need:** "I want to search flights filtered by my preferences"

**Blocks:** 
- A place to store my airline preferences (config file)
- A way to get flight data (API connection)
- Logic to apply my filters (processing script)
- A natural language interface (conversation layer)

**Build:** Each piece was a separate AI conversation

**Connect:** Final conversation to tie everything together

## Why This Works

**Separate conversations = focused attention**
Each piece gets full AI focus without context dilution

**Building blocks are finite and learnable**
APIs are pipes, scripts are recipes, configs are preference files

**Non-technical intuition transfers**
"I need somewhere to store preferences" = config file

## Trigger Phrases Callers Use

- "This seems too complicated to build"
- "I don't know where to start"
- "I'm not technical enough for this"
- "How do people actually build systems?"

## The Translation Layer

| Scary Term | Plain English |
|------------|---------------|
| API | A pipe between systems |
| Script | A recipe |
| Config file | A place to store preferences |
| Webhook | A trigger |
| Database | An organized filing cabinet |

## Implementation

Next time you have a complex need:
1. Describe it to AI in plain English
2. Ask: "What are the building blocks for this?"
3. Build each block in a separate conversation
4. Connect them together

Complexity is just unfamiliarity with the blocks.