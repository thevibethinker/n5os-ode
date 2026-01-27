# B25: Deliverable Content Map

## Committed Deliverables

| Item | Promised By | Promised When | Status | Link/File | Notes |
|------|-------------|---------------|--------|-----------|-------|
| Odeguard meeting-processing + Build Orchestrator + Conversation Close + semantic-memory setup | Us | 1/19 call (repo push) | IN_PROGRESS | GitHub repo (pushed into root, now appearing under `N5OS`) | Bootloader/personalize/semantic memory flows still need confirmation; once David runs `@bootloader`, `@personalize`, and verifies semantic memory entries we can document the resulting worker files and state. |
| Fathom API + webhook + folder automation plan (designated transcript drop location + format) | Us | During meeting (prompt submitted to Zoe) | IN_PROGRESS | – | Need to capture the exact folder naming convention, webhook payload schema, and handoff instructions so David can point Fathom at the folder without Zapier; plan generation underway inside Zo. |
| Transcript backfill / module dedup + content-library update (detect new concept modules, export MD Conversations db capability into ODE) | Us | Asked during meeting (backfill conversation) | IN_PROGRESS | – | Requires defining the container for extracted insights (slides vs. concept modules), exporting the Conversations DB, and wiring the new capability into the ODE repo before the experience is handed off. |
| Intro to Ben Erez + Supra/Sidebar community session (coffee/office visit + possible podcast) | Them | Next few days (per discussion) | PENDING | – | David will share Ben’s availability and mention Zoe’s desire to host him at the office/podcast; no confirmed date yet. |

*Note: `B02_COMMITMENTS` context was not yet surfaced in this workspace, so every deliverable above is sourced directly from the 1/19 transcript segments.*

## Resources Mentioned

**Shared during meeting:**
- Odeguard system GitHub (Build Orchestrator, Conversation Close, semantic memory setup) – pushed to David’s environment via the repo clone and bootloader/personalize instructions.
- Mind map (second link shared) that maps Vrijen’s key beliefs/ideas and illustrates the desired modular capture of insights.
- Fathom settings screen (API access + Zo integration) referenced while configuring the webhook.

**Requested for follow-up:**
- Instruction doc for David outlining the “ongoing”, high-level habits for working with Zoe (close conversations, bootloader/personalize, what to ask).
- Confirmation of the specific folders/transcript files that the Fathom webhook should drop into so the pipeline stays consistent.

## Links & References

**URLs shared:**
- No explicit URLs survived in the transcript capture (GitHub/mind map mentions were verbal; need to confirm exact links post-call).

**Documents referenced:**
- Mind map (second link from Vrijen) describing the intersection of key ideas/operating principles.
- Fathom API docs/settings screen (used to copy API key + webhook).

## Follow-Up Content Needs

**Items to prepare before follow-up:**
- [ ] Document the outcome of running `@bootloader`, `@personalize`, and the semantic memory setup so we can confirm the worker files and knowledge updates.
- [ ] Finalize the Fathom API + webhook implementation plan (folder pattern, payload format, automation steps) and capture it as a standalone instruction set.
- [ ] Build the transcript-processing backfill: split the aggregated file, tag new concepts/modules, and catalog the results inside the content library/MD Conversations database.

**Items to request from them:**
- [ ] Clarify whether the extracted units should map to slide decks, concept modules, or both, so the “container” for new learnings is locked in before we export it into ODE.
- [ ] Confirm Ben Erez’s availability and preferred format (office visit + Supra/Sidebar session) so Zoe can follow up with the right people.
- [ ] Share the exact GitHub and mind map URLs (and any repo paths) used in the call for reference in the follow-up email.

Timestamp: 2026-01-19 16:12 ET