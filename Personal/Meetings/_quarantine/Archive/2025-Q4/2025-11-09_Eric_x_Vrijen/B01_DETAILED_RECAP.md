---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Detailed Recap: N5OS Light Installation & Demo

## Meeting Overview
Vrijen walked Eric through installing and configuring N5OS Light, a lightweight version of Vrijen's AI-assisted work system. The session focused on unpacking the system, understanding its core components, and demonstrating key capabilities.

## Key Topics Discussed

### 1. System Installation Process
- Eric had not yet explored his Zo instance; it remained empty
- Vrijen guided him to download a tar/zip archive from email and unpack it into Zo
- Installation used a systematic, step-by-step approach with Claude Sonnet model
- The unpacking process revealed the folder structure and core components

### 2. System Architecture & Components
Eric received several key components:
- **Prompts folder**: Reusable workflow templates (Conversation Close, Deep Research, DocGen, InCantum QuickRef)
- **Personas**: Eight different perspective-switching modes for different task contexts
- **Architectural principles**: Design values for how the system operates
- **Rules system**: Governance rules for system behavior

### 3. Model Selection & Performance Context
Vrijen explained Claude model tiers:
- **Claude Haiku**: Lightweight model (~400k context window)
- **Claude Sonnet 4.5**: All-rounder, stronger performance (~1M context window)
- **Claude Opus**: Heavyweight "big boy" model
- New K2 thinking model available (10x cheaper than Sonnet, comparable performance)
- Discussion of context window sizes and their impact on reasoning effectiveness

### 4. Cost & Accessibility
- No mandatory Zo subscription upgrade required to run the system
- Free tier available; paid tiers offer 50% discount on token pricing
- Estimated monthly cost: ~$20 with proper optimization
- Emphasis on avoiding expensive token rabbit holes

### 5. Core Concept: Personas & Context Switching
- System includes 8 Personas for different task types
- Personas enable perspective-shifting within conversations (e.g., Researcher → Writer → Editor → Critic)
- Builder Persona activates when adding functionality
- Teacher Persona can explain system capabilities
- Auto-switching available but may require strengthening
- Manual invocation works reliably

### 6. Workspace Architecture
- Zo maintains two layers: explicit file system (left panel) and conversational workspace
- Files created during conversations live in Zo's private conversational space (`/home/z/...`)
- Files can be moved to permanent workspace explicitly
- Important technical detail: file attachment quirks when switching conversations

### 7. System Verification Process
- Installation completed with vetting process
- System rules and Personas evaluated for alignment
- All components were assessed as well-designed
- Implementation of system rules and Personas completed successfully

## Technical Insights Shared

### InCantum QuickRef System
- Natural language instruction → workflow/command interpretation
- Example: "N5 resume" automatically resumes from conversation drop-off
- Reduces hit rate misses on tool invocation

### Context Management
- Dynamic process of optimization across turns
- Each query triggers recompaction of relevant vs. irrelevant information
- Smaller context windows (Haiku) have knock-on effects on execution effectiveness

## Demonstrations
- Opened System Teacher Persona to showcase capabilities
- Teacher Persona successfully explained system identity and functionality
- Real-time demonstration of Persona switching

## Overall Sentiment & Energy
- Eric expressed enthusiasm: "This is exciting to check out, man"
- Vrijen pleased with successful installation and functionality
- Positive reception to system design and capabilities
- Eric found the Teacher Persona demonstration compelling

## System Quality Assessment
- Vrijen confirmed: "Apparently I did good work" based on vetting results
- Personas, rules, and architectural principles all assessed as well-aligned
- Edge cases documented and flagged

## Next Steps Identified
- Eric to tinker with and play with the system
- Learn through experimentation and exploration
- Clarify any missing files (system will indicate)
- Activate Vibe Debugger once installed to identify and fix inevitable bugs

