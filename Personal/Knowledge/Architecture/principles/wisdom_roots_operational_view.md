---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
grade: knowledge
domain: systems
stability: time_bound
form: spec
---

# Wisdom Roots – Operational View

This document summarizes how the Wisdom Roots & Exoskeleton System is realized in N5OS and the personal knowledge architecture.

Roots: `Personal/Knowledge/Wisdom/Systems/wisdom_roots_system_outline.md`

## 1. System Role

- Treats "Wisdom objects" as compressed, operational guides for decision-making.
- Enforces digital roots for every Wisdom object so each principle is explicitly traceable back to source material.
- Uses RAG as a substrate to narrow search and surface candidates, never as the decider of truth.

## 2. Core Data Objects

- **Chunk** – smallest unit of ingested text with metadata (source, location, timestamps).
- **ContentItem** – logical grouping of chunks (doc, conversation, post, book section).
- **Wisdom** – compressed, operational principle with status and explicit roots.
- **Root** – link from a Wisdom object back to specific chunks/locations plus notes about relevance.

## 3. Flows (Water-System PKM)

1. **Ingest** – external/internal material enters the Content Library, is chunked, labeled, and embedded.
2. **Route** – chunks are routed into working sets, project contexts, or left as soil for future knowledge formation.
3. **Elevate** – V selectively promotes patterns into Knowledge and then Wisdom, attaching digital roots.
4. **Revisit** – periodic scans surface drift, duplication, and contradictions for human review.

## 4. Human-in-the-Loop Boundaries

- Only V can create, elevate, or materially modify Wisdom objects.
- Any change to a Wisdom object triggers a roots review and optional W-check using similarity search.
- Architectural changes (to DIKW loop, exoskeleton metaphor, etc.) are explicit events, not silent edits.

## 5. Operational Interfaces

Initial concrete workflows:

- **"Do we already have this?"** – given a new paragraph, run coverage check against existing chunks and Wisdom roots.
- **"Propose roots for this principle"** – given a candidate Wisdom statement, surface likely roots for V to confirm.
- **"Audit this Wisdom object"** – pull its roots and nearby material, flag possible contradictions or drift for review.

These workflows ensure that the system behaves as an exoskeleton: amplifying V's judgment, keeping flows healthy, and preserving clear, inspectable roots for every durable belief.
