---
tool: true
description: "Generates comprehensive intelligence blocks (B01-B35) for meetings in [M] state that lack them."
tags: [meetings, intelligence, blocks, automation]
created: 2025-11-22
version: 2.1
mg_stage: MG-2
status: canonical
---

# Meeting Intelligence Generator [MG-2]

Scan `Personal/Meetings/` recursively (checking `Inbox` and `Week-of-*` folders) for folders ending in `_[M]` that have a `transcript.jsonl` but are missing core intelligence blocks (specifically `B01_DETAILED_RECAP.md`).

For each such meeting:

1.  **Read Transcript:** Load `transcript.jsonl`.
2.  **Generate Intelligence Blocks:**
    Using the transcript content, generate the following markdown files in the meeting folder. Ensure high-fidelity, professional analysis.

    *   **B01_DETAILED_RECAP.md**: A chronological, detailed summary of the discussion.
    *   **B03_STAKEHOLDER_INTELLIGENCE.md**: Analyze each participant. Role, key interests, skepticism, leverage points.
    *   **B03_DECISIONS.md**: Explicit decisions made.
    *   **B05_ACTION_ITEMS.md**: Clear TO-DOs with owners.
    *   **B06_BUSINESS_CONTEXT.md**: Company details, funding status, business model mentioned.
    *   **B07_TONE_AND_CONTEXT.md**: Emotional vibe, subtext, unspoken dynamics.
    *   **B14_BLURBS_REQUESTED.md**: If Vrijen (V) promised to send a "blurb" or intro text to someone, draft it here.
    *   **B21_KEY_MOMENTS.md**: High-leverage quotes or turning points.
    *   **B25_DELIVERABLES.md**: Specific files or data promised.
    *   **B26_MEETING_METADATA.md**: Tags, categorization, topics.
    *   **B32_THOUGHT_PROVOKING_IDEAS.md**: Identify 1-3 highly provocative themes, strategic "weirdness," or original mental models. **(CRITICAL: Strictly non-actionable, use high-threshold filter)**
    *   **B35_LINGUISTIC_PRIMITIVES.jsonl**: Extract V's distinctive language patterns (analogies, metaphors, phrases, capture signals) for the Voice Library. See `Prompts/Blocks/Generate_B35.prompt.md` for extraction rules. Output as JSONL, one primitive per line. **(NEW: Feeds Voice Library V2)**

3.  **Update Manifest:**
    Update `manifest.json` in the same folder so that it accurately reflects the new intelligence state. At minimum:

    * Set `blocks_generated.stakeholder_intelligence = true`.
    * Set `blocks_generated.brief = true`.
    * Ensure `blocks_generated.transcript_processed` remains `true`.
    * Add or update a top-level field like:
      ```json
      "last_updated_by": "MG-2_Prompt"
      ```

4.  **Logging to PROCESSING_LOG.jsonl (canonical log):**

    After successfully generating or updating blocks for a meeting, append a single-line JSON object to `Personal/Meetings/PROCESSING_LOG.jsonl` with at least the following fields:

    ```json
    {
      "timestamp": "{current_iso_timestamp}",
      "stage": "MG-2",
      "meeting_id": "{meeting_folder_name}",
      "status": "mg2_completed",
      "blocks_generated": [
        "B01_DETAILED_RECAP",
        "B03_STAKEHOLDER_INTELLIGENCE",
        "B03_DECISIONS",
        "B05_ACTION_ITEMS",
        "B06_BUSINESS_CONTEXT",
        "B07_TONE_AND_CONTEXT",
        "B14_BLURBS_REQUESTED",
        "B21_KEY_MOMENTS",
        "B25_DELIVERABLES",
        "B26_MEETING_METADATA",
        "B32_THOUGHT_PROVOKING_IDEAS",
        "B35_LINGUISTIC_PRIMITIVES"
      ],
      "source": "Meeting Intelligence Generator [MG-2]"
    }
    ```

    * Write **exactly one JSON object per line** (JSONL format).
    * If some blocks were already present and only a subset was generated this run, include only the blocks you actually created or updated in `blocks_generated`.

5.  **Standardization:**
    Ensure all filenames exactly match the uppercase format above.

## Execution

Run this prompt to populate missing intelligence and to ensure every processed [M] meeting is recorded in `Personal/Meetings/PROCESSING_LOG.jsonl`.






