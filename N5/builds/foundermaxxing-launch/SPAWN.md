---
created: 2026-02-19
last_edited: 2026-02-19
version: 1.0
provenance: con_u475mQtYnFGIl1Sd
---

# FounderMaxxing Launch — Spawn Document

## Purpose

This document is a self-contained brief for rebuilding the FounderMaxxing landing page.
It contains everything needed to pick up this work in a new conversation or Pulse drop.

---

## Context

V (Vrijen Attawar) is launching **FounderMaxxing** — a weekly live workshop + 24/7 
support system for non-technical funded founders who want to maximize their productivity 
using agentic AI while building real AI fluency as a byproduct.

### V's Background (for credibility section)
- Founder of Careerspan (career tech company, 4 years)
- Decade of career coaching experience
- Non-technical but builds production-grade AI systems (CRMs, hiring pipelines, 
  content engines, meeting prep workflows, 24/7 hotlines — all with AI)
- Ran "Next Play" session for 80+ founders — overwhelming feedback was "more building"
- Self-describes as "the best non-technical coder most people have met"
- Unique position: engineering instincts + non-technical perspective + teaching background

### The Product
- **Weekly 45-min live sessions** — show & tell, build-along, apply to your context
- **Full archive** of all recordings, repos, templates, design patterns
- **Zo-to-Zo mentorship** — V's Zo provides 24/7 guidance to members' Zos
- **Co-building hotline** — live support between sessions
- **Monthly office hours** — deep-dive on individual challenges
- **Community voting** — members pick half the topics
- **AI news curation** — personalized to session discussions
- **Weekly digest** — Chatham House filtered summary (future: free tier lead magnet)

### Pricing (Stripe products already created)
| Tier | Price | Stripe Link | Notes |
|------|-------|-------------|-------|
| **Founding Class** | $100/mo | https://buy.stripe.com/bJebJ148ygjrc6dgi2bsc0a | First 30 spots. Locked forever. Show this prominently. |
| **Class of 2026** | $200/mo | https://buy.stripe.com/5kQ5kD48yc3b1rzaXIbsc09 | **HIDDEN on page until Founding fills.** Locked forever for 2026 joiners. |
| **Zo-to-Zo Subscription** | $150/mo | https://buy.stripe.com/7sYbJ1bB06IR4DL1n8bsc08 | Standalone. Just mentorship + hotline. No live sessions. |

### Key Constraint: 1-month minimum, cancel anytime, rate locked forever.

---

## Narrative Architecture

Read: `file 'N5/builds/foundermaxxing-launch/NARRATIVE.md'` for the full story arc.

**Summary of the 7 beats:**

1. **Hook** — AI is the most productive technology ever. You haven't built a system to harness it yet.
2. **Reframe** — This isn't an AI course. It's a productivity system where AI fluency is the byproduct.
3. **Why V (N-of-1)** — Venn diagram: funded founder × engineering instincts × teaching background. This person doesn't exist elsewhere.
4. **Social proof** — Horizontal infinite scroll of impressive founders (placeholder slots okay for now).
5. **Value stack** — Each benefit as a compact, high-impact block.
6. **Pricing** — Founding Class ($100/mo) prominent. Zo-to-Zo ($150/mo) secondary. Class of 2026 hidden.
7. **Application** — Short form. "What would you build first?" as the key question.

---

## Messaging Constraints (Non-Negotiable)

- **NEVER** imply V or any founder is "falling behind" or failing
- **Frame as opportunity/upside**, not fear/deficit
- **Non-technical = strength** (divergent thinking), not a gap
- **Zo-native throughout** — NO ChatGPT references, NO tool-agnostic positioning
- **"Design patterns that transfer"** > tool tutorials
- **Productivity is the trojan horse** for AI literacy
- Keep copy tight — every word earns its place

---

## Design Requirements

- **Aesthetic:** Dark editorial. High contrast. Intentional density (not sparse).
- **Layout:** Asymmetric where possible. NOT centered-everything.
- **Venn diagram:** Generate graphic showing V's N-of-1 overlap (3 circles)
- **Social proof:** Horizontal marquee/infinite scroll of founder faces + names
- **Anti-slop:** Follow `Skills/frontend-design/SKILL.md` rigorously
  - No default blue, no generic gradients, no Hero→Features→CTA template
  - No identical card grids, no centered-everything, no shadow-everything
- **Mobile responsive**
- **Premium feel** matching $100-200/mo price point

---

## Technical Details

- **Platform:** zo.space (React + Tailwind CSS 4 + lucide-react)
- **Page route:** `/foundermaxxing` (public)
- **API route:** `/api/foundermaxxing-apply` (already live, handles form submissions)
- **Form stores to:** `/home/workspace/Personal/Business/foundermaxxing-applications.json`
- **Domain (future):** foundermaxx.ing (V has purchased this)

---

## Existing Stripe Product IDs

- Founding Class: `prod_U0eZ60eiQ8zeKx` / `price_1T2dGeHQ08I7w6YsuMZZ60Ba`
- Class of 2026: `prod_U0eZz7GTHZDGtM` / `price_1T2dGeHQ08I7w6YsnXb7pBLO`
- Zo-to-Zo: `prod_U0eZY4l7JiJEPb` / `price_1T2dGeHQ08I7w6YsGh4nI0Vp`

---

## Concept Document

Full concept with all business logic: `file 'Personal/Business/FounderMaxxing-Concept-V1.md'`

---

## What to Build (Drops)

### Drop A: Venn Diagram Graphic
- Generate a clean, dark-themed 3-circle Venn diagram
- Circles: "Funded Founder" / "Engineering Instincts" / "Teaching & Coaching"
- Center intersection: V's unique position
- Upload as zo.space asset

### Drop B: Landing Page Rebuild
- Depends on: Drop A (needs the graphic), NARRATIVE.md
- Implement the 7-beat narrative as a single-page React component
- Follow all design requirements above
- Include infinite-scroll social proof section (placeholder-ready)
- Include application form (use existing /api/foundermaxxing-apply)
- Only show Founding Class + Zo-to-Zo pricing (hide Class of 2026)

### Drop C: Testimonial/Social Proof Collection
- Manual — V needs to identify 3-5 impressive founders
- Draft outreach messages
- Design the social proof component to accept dynamic data

### Drop D: Outreach Drafts
- Testimonial collection outreach
- Launch announcement for V's network
- Depends on: Drop B being approved
