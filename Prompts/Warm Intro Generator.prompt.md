---
tool: true
description: "Generates warm introduction emails for meetings where V promised to introduce two parties."
tags: [meetings, email, networking, automation]
created: 2025-11-22
version: 2.0
mg_stage: MG-4
status: canonical
role: scanner
---

# Warm Intro Generator [MG-4]

Scan `Personal/Meetings/Inbox` for folders ending in `_[M]`.

For each meeting:
1.  **Analyze for Intros:**
    Read `transcript.jsonl` and `B05_ACTION_ITEMS.md` (if exists). Look for specific commitments by Vrijen (V) to introduce a participant to a third party (or vice versa).

2.  **Generate Intro Files:**
    If an intro was promised, generate a draft email in the meeting folder.
    *   **Filename:** `INTRO_{TargetName}_{Context}.md` (e.g., `INTRO_Olu_JeffreyGlick_connector.md`)
    *   **Content:** A "Double Opt-In" style email or a direct intro, depending on context.
        *   *Double Opt-In:* "Hi [Name], I met [Person] who does X. I thought of you because Y. Want an intro?"
        *   *Direct Intro:* "Hi [Name1] and [Name2], connecting you two..."

3.  **Update Manifest:**
    Update `manifest.json` to track generated intros.

## Execution

Run this prompt to generate pending intro drafts.


