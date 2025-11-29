---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
tool: false
description: Generate manifest.json for meeting block generation with dynamic selection based on content analysis
tags:
  - meetings
  - manifest
  - block-selection
  - automation
mg_stage: MG-1
status: deprecated
superseded_by: Prompts/Meeting Manifest Generation.prompt.md
---

# Meeting Block Selector

**Purpose:** Analyze meeting transcript and generate manifest.json with dynamically selected blocks.

---

## Workflow

### STEP 1: Scan Inbox for Raw Meetings

Find folders without suffix and without manifest:

```bash
find /home/workspace/Personal/Meetings/Inbox -maxdepth 1 -type d -name "20*" | while read folder; do
  # Skip if has suffix marker
  if [[ "$folder" =~ _\[M\]$ ]] || [[ "$folder" =~ _\[P\]$ ]]; then
    continue
  fi
  
  # Check if manifest already exists (file-based check)
  if [ -f "$folder/manifest.json" ]; then
    continue
  fi
  
  # Check if transcript exists
  if [ ! -f "$folder/transcript.md" ]; then
    continue
  fi
  
  # FOUND: Process this folder
  echo "$folder"
  break  # Process ONE meeting per run
done
```

**If no folder found:** Exit with message "No meetings ready for manifest generation"

---

### STEP 2: Load Block Registry

Read canonical block definitions:

```bash
cat /home/workspace/N5/config/canonical_blocks.yaml
```

Extract all block definitions including:
- `always_generate: true` (core blocks)
- Conditional blocks with trigger patterns
- Typical lengths and priorities

---

### STEP 3: Analyze Transcript

**Read the transcript:**
```bash
cat "$folder/transcript.md"
```

**Read block detection guidance:**
```bash
cat /home/workspace/N5/config/canonical_blocks.yaml
```

**Semantic Analysis (AI Task):**

**CRITICAL:** For each conditional block, read its `detection_guidance` section from canonical_blocks.yaml and apply the semantic triggers, contextual scenarios, and examples provided.

1. Identify meeting type (internal/external/partnership/technical/strategic)
2. Count participants
3. Detect key themes
4. **For each block with detection_guidance, analyze using LLM understanding:**
   - B14_BLURBS_REQUESTED: Check for BOTH outbound commitments ("I'll send you") AND inbound requests ("Can you send"). Look for introduction scenarios, stakeholder communication needs, partnership facilitation contexts.
   - Apply semantic understanding, not keyword matching
   - Consider speaker intent and context
   - Review examples in detection_guidance

---

### STEP 4: Select Blocks Dynamically

**Selection Logic:**

**1. Always Include (Core Blocks with always_generate: true):**
- B01_DETAILED_RECAP
- B03_DECISIONS (mark not_applicable if no decisions, with deletion_reason)
- B05_ACTION_ITEMS (mark not_applicable if none, with deletion_reason)
- B14_BLURBS_REQUESTED (mark not_applicable if none, with deletion_reason)
- B25_DELIVERABLES (mark not_applicable if none, with deletion_reason)
- B26_MEETING_METADATA

**2. Semantic Block Detection (Use detection_guidance from YAML):**

For blocks with `detection_guidance` in canonical_blocks.yaml:
- **Read the guidance carefully**
- **Apply semantic triggers** (not just keywords)
- **Consider examples** provided
- **Understand context** (speaker roles, implicit needs)

**Example: B14_BLURBS_REQUESTED**
- ✅ Check for outbound: "I'll send you", "Let me provide"
- ✅ Check for inbound: "Can you send", "Do you have"
- ✅ Check contextual: Introduction scenarios, stakeholder communication
- ✅ Evidence from transcript: Quote specific lines
- ❌ Don't just grep for "blurb" keyword

**3. Conditional Blocks (Based on Semantic Analysis):**

| Analysis Result | Add Block |
|----------------|-----------|
| Partnership/collaboration detected | B03_STAKEHOLDER_INTELLIGENCE |
| Decisions or agreements mentioned | B03_DECISIONS |
| Strategic/vision keywords | B08_STRATEGIC_IMPLICATIONS |
| Risk/opportunity themes | B06_RISKS_OPPORTUNITIES |
| Follow-up needs identified | B07_FOLLOW_UP_REQUIRED |

---

### STEP 5: Generate manifest.json

**Structure:**
```json
{
  "meeting_id": "2025-11-16_Title",
  "generated_at": "2025-11-16T12:30:00Z",
  "transcript_path": "transcript.md",
  "blocks": [
    {
      "block_id": "B01",
      "canonical_name": "DETAILED_RECAP",
      "status": "pending",
      "priority": 1
    },
    {
      "block_id": "B02",
      "canonical_name": "COMMITMENTS",
      "status": "pending",
      "priority": 1
    },
    {
      "block_id": "B03",
      "canonical_name": "STAKEHOLDER_INTELLIGENCE",
      "status": "pending",
      "priority": 2,
      "trigger": "3+ participants detected"
    }
  ],
  "selection_rationale": "Brief explanation of why these blocks were selected",
  "total_blocks": 6
}
```

**Write to folder:**
```bash
echo "$manifest_json" > "$folder/manifest.json"
```

---

### STEP 6: Rename Folder (Add Suffix)

```bash
# Add [M] suffix for human visibility
mv "$folder" "${folder}_[M]"
```

**Log:** "✓ Generated manifest for: ${folder_name}_[M] (6 blocks selected)"

---

## Quality Checks

**Before generating manifest:**
- ✅ Transcript exists and is readable
- ✅ Transcript is >100 words (meaningful content)
- ✅ Meeting ID is valid date format
- ✅ Block selections are justified

**Validation:**
- All selected blocks exist in canonical registry
- No duplicate block IDs
- At least 3 blocks selected (minimum)
- No more than 12 blocks (practical maximum)
- All `always_generate` blocks included

---

## Error Handling

**If transcript too short (<100 words):**
- Log warning
- Generate minimal manifest (B01, B02, B26 only)
- Add note in manifest: `"warning": "Short transcript, minimal blocks"`

**If folder name invalid:**
- Log error
- Skip folder
- Continue to next

**If manifest write fails:**
- Log error with details
- Do NOT rename folder
- Exit with failure message

---

## Success Output

```
✓ Processed: 2025-11-16_Client_Call_[M]
✓ Manifest: 7 blocks selected (3 core + 4 conditional)
✓ Rationale: Partnership discussion with technical details and strategic implications
✓ Ready for block generation
```

---

## Notes

- **Incremental:** Process ONE meeting per run
- **Idempotent:** Skip if manifest exists or suffix present
- **Resumable:** Folder rename only happens after successful manifest write
- **File-based:** Source of truth is manifest.json existence, not suffix
- **Human UX:** Suffix provides visual status for debugging

---

**Execution:** This prompt is invoked by scheduled task every 15 minutes.



