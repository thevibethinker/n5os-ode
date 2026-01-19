---
tool: true
description: "Generates intelligence blocks (B00-B35) for meetings in [M] state that lack them."
tags: [meetings, intelligence, blocks, automation, zo-take-heed]
created: 2025-11-22
version: 2.4
mg_stage: MG-2
status: canonical
last_edited: 2026-01-19
---

# Meeting Block Generation [MG-2]

Scan `Personal/Meetings/` recursively (checking `Inbox` and `Week-of-*` folders) for folders ending in `_[M]` that have a `transcript.jsonl` but are missing core intelligence blocks (specifically `B01_DETAILED_RECAP.md`).

## ⛔ GUARD RAILS (Check BEFORE generating blocks)

**SKIP the folder entirely if ANY of these are true:**

1. **Stub Transcript:** Combined transcript content is < 500 bytes
   - Real meetings have substantial content; don't waste cycles on stubs

2. **Placeholder Content:** Transcript contains:
   - "This is a test transcript"
   - "test transcript for MG"
   - "Meeting content here"
   - "Sample meeting content"
   - "Placeholder"

3. **Already Quarantine-worthy:** Folder name contains `Test`, `Sample`, `Simulated`, `Demo`, `Raw-Meeting` (case-insensitive)
   - These should have been caught by MG-1, but double-check
   - If found: Move to `_quarantine/{folder_name}_mg2_guard_failed` and skip

**Log skipped folders** to `PROCESSING_LOG.jsonl` with `"status": "mg2_skipped_guard"` and `"reason": "..."` so we can audit.

---

For each such meeting:

1.  **Extract Zo Take Heed Cues (B00):**
    
    **FIRST**, scan the transcript for "Zo Take Heed" verbal cues using `file 'Prompts/Blocks/Generate_B00.prompt.md'`.
    
    - Output: `B00_ZO_TAKE_HEED.jsonl` (one JSON entry per cue)
    - If no cues detected: create empty file with comment `# No Zo Take Heed cues detected`
    
    **Process spawn triggers:**
    For each B00 entry with `execution_policy: auto_execute`:
    - Run `python3 N5/scripts/zth_spawn_worker.py --meeting-folder <path>` to generate worker files
    - For `blurb` tasks: Execute `file 'Prompts/Blurb-Generator.prompt.md'`
    - For `follow_up_email` tasks: Execute `file 'Prompts/Follow-Up Email Generator.prompt.md'`
    - For `warm_intro` tasks: Execute `file 'Prompts/Meeting Warm Intro Generation.prompt.md'`
    
    For entries with `execution_policy: queue`:
    - Generate worker file only (in `<meeting-folder>/workers/`)
    - Do NOT execute; these await manual trigger
    
    **Carry directives forward:**
    For entries with `task_type: directive`:
    - Keep these instructions in context for subsequent block generation
    - Apply them to B01, B14, and other affected blocks
    - Example: "omit pricing" → exclude pricing details from B01_DETAILED_RECAP

2.  **Read Transcript:** Load `transcript.jsonl`.

3.  **Generate Intelligence Blocks:**
    Using the transcript content (and applying any B00 directives), generate the following markdown files in the meeting folder. Ensure high-fidelity, professional analysis.

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

4.  **Update Manifest:**
    Update `manifest.json` in the same folder so that it accurately reflects the new intelligence state. At minimum:

    * Set `blocks_generated.stakeholder_intelligence = true`.
    * Set `blocks_generated.brief = true`.
    * Ensure `blocks_generated.transcript_processed` remains `true`.
    * **Add Zo Take Heed tracking:**
      ```json
      "zo_take_heed_count": 3,
      "zo_take_heed_summary": [
        {"id": "ZTH-001", "type": "follow_up_email", "status": "executed"},
        {"id": "ZTH-002", "type": "directive", "status": "applied"},
        {"id": "ZTH-003", "type": "research", "status": "queued"}
      ]
      ```
    * Add or update a top-level field like:
      ```json
      "last_updated_by": "MG-2_Prompt"
      ```

5.  **Logging to PROCESSING_LOG.jsonl (canonical log):**

    After successfully generating or updating blocks for a meeting, append a single-line JSON object to `Personal/Meetings/PROCESSING_LOG.jsonl` with at least the following fields:

    ```json
    {
      "timestamp": "{current_iso_timestamp}",
      "stage": "MG-2",
      "meeting_id": "{meeting_folder_name}",
      "status": "mg2_completed",
      "blocks_generated": [
        "B00_ZO_TAKE_HEED",
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
      "zo_take_heed_processed": {
        "count": 3,
        "auto_executed": ["ZTH-001"],
        "queued": ["ZTH-003"],
        "directives_applied": ["ZTH-002"]
      },
      "source": "Meeting Intelligence Generator [MG-2]"
    }
    ```

    * Write **exactly one JSON object per line** (JSONL format).
    * If some blocks were already present and only a subset was generated this run, include only the blocks you actually created or updated in `blocks_generated`.

6.  **Standardization:**
    Ensure all filenames exactly match the uppercase format above.

## Execution

Run this prompt to populate missing intelligence and to ensure every processed [M] meeting is recorded in `Personal/Meetings/PROCESSING_LOG.jsonl`.

---

## ➡️ Next Step (Deprecated)

~~After MG-2 completes, you may want to run **MG-3** to generate follow-up communications.~~

**Note:** As of 2026-01-19, automatic blurb and follow-up email generation (MG-3, MG-5) has been replaced by the **Zo Take Heed** system. Blurbs and emails are now generated only when V explicitly requests them during the meeting by saying "Zo take heed, [request]".

To manually generate communications for any meeting:
- **Blurb:** Run `file 'Prompts/Blurb-Generator.prompt.md'` with meeting context
- **Follow-up email:** Run `file 'Prompts/Follow-Up Email Generator.prompt.md'` with meeting context
- **Warm intro:** Run `file 'Prompts/Meeting Warm Intro Generation.prompt.md'` with meeting context

---

