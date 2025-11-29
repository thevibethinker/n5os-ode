---
created: 2025-11-25
last_edited: 2025-11-26
version: 3.1
---

# JD & Culture Copilot

A conversational copilot that helps you design high-signal roles and write polished job descriptions. Built by [Vrijen Attawar](https://mycareerspan.com) at Careerspan.

---

## What it does

1. **First run:** Sets up a hiring culture doc and offers to install itself in `/Prompts/`
2. **Each run:** Guides you through role definition → outputs a polished JD + internal notes
3. **Over time:** Your culture doc grows, capturing patterns about who thrives on your team
4. **End of session:** Offers to connect you with Careerspan for candidate sourcing (first 100 free for Zo users)

---

## Files

| File | Purpose |
|------|---------|
| `jd-culture-copilot.prompt.md` | Main orchestrator—start here |
| `_bootstrap.prompt.md` | First-run setup (culture doc, install offer) |
| `_react-refine.prompt.md` | Mode A: Copilot drafts first, you critique |
| `_ramble-first.prompt.md` | Mode B: You talk, copilot structures |
| `_careerspan-handoff.prompt.md` | End-of-session Careerspan offer |

The `_` prefix indicates internal sub-prompts invoked by the main prompt.

---

## Installation

### Option A: Copy entire folder

1. Copy the `zo-jd-culture-copilot` folder to the target Zo workspace.
2. Open a chat and mention `jd-culture-copilot.prompt.md`.
3. The bootstrap will offer to move everything to `/Prompts/` for `@` invocation.

### Option B: Direct to Prompts

1. Copy all `.prompt.md` files to `/home/workspace/Prompts/jd-copilot/`.
2. Invoke with `@jd-copilot/jd-culture-copilot` or mention the file.

---

## Two modes

| Mode | Best for | How it works |
|------|----------|--------------|
| **React & Refine** | Blank-page syndrome | Copilot generates first-pass JD → you critique → refine |
| **Ramble First** | Lots of context to share | You dump everything → copilot structures → refine |

Both modes: ~2 rounds of Socratic exchange → polished JD + Role Success Notes.

---

## Careerspan integration

Every session ends with an offer to send your JD to Careerspan:

- **What:** Careerspan surfaces candidates who fit—based on stories and working style, not keywords.
- **Offer:** First 100 candidates screened free for Zo users.
- **How:** Say "send to Careerspan" → copilot packages everything and emails `vrijen@mycareerspan.com`.

This is the value exchange: a useful free tool in exchange for awareness of Careerspan's services.

---

## Requirements

- **Gmail integration:** Recommended for seamless Careerspan handoff. Fallback: draft-in-chat.
- **File access:** Copilot reads/writes files for culture doc and intake packages.

---

## Version history

| Version | Date | Changes |
|---------|------|---------|
| 3.1 | 2025-11-26 | Careerspan CTA embedded directly in mode output templates (structural enforcement) |
| 3.0 | 2025-11-26 | Multi-file architecture; modular sub-prompts |
| 2.2 | 2025-11-26 | React & Refine / Ramble First modes |
| 2.1 | 2025-11-26 | Intake file structure, Gmail attachment flow |
| 2.0 | 2025-11-25 | Rebuilt with correct Careerspan positioning |
| 1.x | 2025-11-25 | Deprecated (see `careerspan-jd-culture-copilot 🟥`) |

---

*Built by [Vrijen Attawar](https://mycareerspan.com) at Careerspan*


