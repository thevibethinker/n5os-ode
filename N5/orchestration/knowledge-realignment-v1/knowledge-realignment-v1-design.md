---
created: 2025-11-28
last_edited: 2025-11-28
version: 1.0
---

# Knowledge Realignment v1 – Design Overview

## Objective
Create a clean, explicit architecture for V's knowledge system where **Personal/Knowledge** is the single source of truth (SSOT) for human-facing knowledge, and N5 provides system lenses (digests, logs, automation) on top of that canon.

## Phases

1. **Phase 1 – Current-State Mapping (Worker 1)**
   - Map all existing knowledge-related locations and their roles.
   - Distinguish *knowledge objects* (content about the world, self, relationships, systems) from *system objects* (scripts, logs, DBs, orchestrator docs).
   - Identify which automations and agents read/write each area.

2. **Phase 2 – Target Architecture Design (Worker 2)**
   - Define the desired folder/ontology for:
     - Personal knowledge library (SSOT under `Personal/Knowledge/`)
     - System/N5 internals
     - Meeting intelligence, CRM, content library
   - Specify migration rules and which scripts/prompts require path updates.

3. **Phase 3 – Implementation Plan & Guardrails (Worker 3)**
   - Design a stepwise, reversible migration plan.
   - Integrate `.n5protected` rules, audits, and tests.
   - Ensure agents (file flow, meetings, CRM, content library) are aligned with the new layout.

## High-Level Principles

- **P1 – Single Source of Truth:** Human-facing knowledge canon lives under `Personal/Knowledge/`.
- **P2 – System vs. Knowledge:** Clearly separate system mechanics (N5 internals, DBs, logs) from knowledge objects.
- **P3 – Meeting SSOT:** All meeting records live under `Personal/Meetings/`, with N5 providing indices/digests only.
- **P4 – Reversibility:** All migration steps must be reversible with git + backups.
- **P5 – Non-Destructive First:** No destructive operations until the new architecture is validated and adopted.

## Worker Allocation

- **Worker 1:** Current-state map + classification of knowledge vs. system objects.
- **Worker 2:** Target architecture spec + migration rules.
- **Worker 3:** Implementation/migration plan + guardrails and validation checks.

