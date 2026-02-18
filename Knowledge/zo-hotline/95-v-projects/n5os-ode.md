---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
provenance: con_lUAmO8hsfnmiy3xh
---

# N5OS Ode — Cognitive OS for Zo

Open-source system that transforms Zo from a generic assistant into a structured thinking partner. Think of it as firmware for your AI.

## What It Adds
- **6 specialist personas**: Operator, Builder, Debugger, Strategist, Writer, Researcher — each loads optimized context for different work types
- **Behavioral rules**: Persistent instructions so your AI asks before deleting, doesn't claim "done" prematurely, tracks conversation state
- **Session state tracking**: Long conversations don't lose the plot
- **Block system**: Turns meeting transcripts into structured intelligence (commitments, decisions, questions)
- **Principles library**: 18 battle-tested architectural guidelines in parseable YAML
- **Safety rails**: File protection, blast radius control, PII tracking

## Install
```
git clone https://github.com/vrijenattawar/n5os-ode.git && cd n5os-ode && bash install.sh
```
Then run `@BOOTLOADER.prompt.md` in a new conversation.

## Key Idea
Personas aren't personalities — they're focused lenses. Same AI, different context. Builder loads coding standards. Writer loads voice rules. Operator routes between them.

## Who It's For
People who use Zo daily for knowledge work and want consistency, memory, and specialization without starting from scratch each conversation.

Repo: github.com/vrijenattawar/n5os-ode
