---
created: 2025-11-28
last_edited: 2025-11-28
version: 1
---
# Worker 1: Current-State Knowledge System Map

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W1-CURRENT-STATE  
**Estimated Time:** 45–60 minutes  
**Dependencies:** None

---

## Mission
Produce a clear, concise map of the *current* knowledge system architecture, explicitly separating **knowledge objects** from **system objects**, and documenting which automations touch each area.

---

## Context
V's workspace has multiple overlapping knowledge locations (e.g., `Knowledge/`, `Personal/Knowledge/`, `N5/knowledge/`, `Documents/Knowledge/Articles/`). Realignments and automation have created confusion about where canon lives and how N5 interacts with it. Before designing a new architecture, we need a precise, reality-based map of how things work *today*.

---

## Dependencies
- Read-only access to:
  - `Knowledge/`
  - `Personal/Knowledge/` (including `Legacy_Inbox/` and `ContentLibrary/`)
  - `Personal/Meetings/`
  - `N5/knowledge/`, `N5/prefs/knowledge/`, `N5/logs/knowledge/`
  - `Prompts/` (knowledge-related prompts)
  - Scheduled tasks and running services (already listed in this workspace).

---

## Deliverables

Create **one markdown document**:

- `Records/Personal/knowledge-system/PHASE1_current_state_map.md`

This doc must include:

1. **Folder Map (Today)**  
   - Short descriptions for each key area:
     - `Personal/Knowledge/` (Canon, ContentLibrary, Frameworks, Legacy_Inbox, Wisdom, Specs, Logs)
     - `Knowledge/`
     - `Personal/Meetings/`
     - `N5/knowledge/`, `N5/prefs/knowledge/`, `N5/logs/knowledge/`
     - Any other `*/Knowledge/` paths that matter.

2. **Knowledge vs. System Object Classification**  
   - For each major subtree, label it primarily as:
     - **Knowledge** (human-facing content, frameworks, writing, CRM profiles, research, etc.)
     - **System** (scripts, DBs, logs, orchestrator docs, runtime artifacts)
     - **Hybrid** (both, with examples of each).

3. **Automation Touchpoints**  
   - Table or bullet list mapping:
     - Key scripts/prompts/agents → the directories they read/write.  
       (e.g., File Flow Router, ContentLibrary scripts, Meeting pipeline, CRM workflows.)

4. **Pain Points & Ambiguities (Today)**  
   - Where the layout is confusing or overlapping.
   - Where SSOT is unclear.
   - Where automation behavior and folder semantics feel misaligned.

Keep it high-signal and skimmable. V should be able to read this in 5–10 minutes and say, "Yes, this is how it actually works right now."

---

## Requirements

- **Non-destructive:** Do not move, delete, or modify any files. Read-only analysis only.
- **Grounded:** Base all claims on actual scans (find/ls/grep), not assumptions.
- **Concrete paths:** Use real paths (e.g., `Personal/Knowledge/Legacy_Inbox/stable/…`).
- **Clarity over exhaustiveness:** Prefer clear summaries + representative examples over listing every file.

---

## Implementation Guide

Suggested steps (adapt as needed):

1. **Scan key locations**
   - `ls -R Personal/Knowledge | head -200`
   - `ls -R Knowledge`
   - `ls -R N5/knowledge N5/prefs/knowledge N5/logs/knowledge`
   - `find . -maxdepth 4 -type d -iname 'Knowledge'`

2. **Identify knowledge vs. system objects**
   - Knowledge objects: articles, frameworks, CRM profiles, research, stable/semi_stable, patterns, etc.
   - System objects: `.db`, logs, orchestrator docs, scripts, runtime reports.

3. **Map automations**
   - Grep relevant N5 scripts and prompts for these paths and summarize which ones touch:
     - `Personal/Knowledge/`
     - `Knowledge/`
     - `Personal/Meetings/`
   - Use script names and a one-line description per.

4. **Write the doc**
   - Organize by area (Personal, Knowledge, N5, Meetings).
   - Include a simple table for automation touchpoints.
   - End with a short "Pain Points & Ambiguities" section.

---

## Testing

- Verify file exists:
  - `ls -lh Records/Personal/knowledge-system/PHASE1_current_state_map.md`
- Sanity check contents:
  - Clear sections for: Folder Map, Classification, Automation Touchpoints, Pain Points.
  - At least a few concrete path examples per major area.

---

## Report Back

When this worker is complete, report to the orchestrator with:

1. Confirmation that `PHASE1_current_state_map.md` exists and is populated.
2. 2–3 sentence summary of key findings (how things *actually* work today).
3. Any surprises or contradictions you discovered.

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-28  

