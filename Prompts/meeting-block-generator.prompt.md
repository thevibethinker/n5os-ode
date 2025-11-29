---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
tool: false
description: Generate individual meeting intelligence blocks sequentially with full context
tags:
  - meetings
  - blocks
  - generation
  - automation
mg_stage: [MG-2, MG-6, MG-7]
status: deprecated
superseded_by:
  - Prompts/Meeting Intelligence Generator.prompt.md
  - Prompts/Meeting State Transition.prompt.md
  - Prompts/Meeting Archive.prompt.md
---

# Meeting Block Generator

**Purpose:** Generate ONE meeting intelligence block per execution with full transcript + prior blocks as context.

---

## Workflow

### STEP 1: Find Meetings with Pending Blocks

```bash
find /home/workspace/Personal/Meetings/Inbox -maxdepth 1 -type d -name "*_[M]" | while read folder; do
  # Check manifest exists
  if [ ! -f "$folder/manifest.json" ]; then
    continue
  fi
  
  # Check if blocks incomplete (file-based)
  manifest=$(cat "$folder/manifest.json")
  # Parse and check if any block has status="pending"
  
  # FOUND: Process this folder
  echo "$folder"
  break  # Process ONE block per run
done
```

**If no folder found:** Exit with "No blocks pending generation"

---

### STEP 2: Load Context

**Load manifest:**
```bash
manifest=$(cat "$folder/manifest.json")
```

**Load transcript:**
```bash
transcript=$(cat "$folder/transcript.md")
```

**Load all previously generated blocks:**
```bash
for block_file in "$folder"/B*.md; do
  if [ -f "$block_file" ]; then
    echo "=== $(basename $block_file) ==="
    cat "$block_file"
    echo ""
  fi
done
```

**Load block definition from registry:**
```bash
# Extract definition for the block we're about to generate
block_def=$(yq eval ".blocks.${block_canonical_name}" /home/workspace/N5/config/canonical_blocks.yaml)
```

---

### STEP 3: Identify Next Block to Generate

**Parse manifest to find first `status="pending"` block:**

```json
{
  "block_id": "B03",
  "canonical_name": "STAKEHOLDER_INTELLIGENCE",
  "status": "pending",
  "priority": 2
}
```

**Check if file already exists (idempotency):**
```bash
block_file="$folder/B03_STAKEHOLDER_INTELLIGENCE.md"
if [ -f "$block_file" ]; then
  # Update manifest status to "completed"
  # Continue to next pending block
fi
```

---

### STEP 4: Generate Block Content

**Context Assembly:**

Provide to LLM:
1. **Full transcript** (always complete context)
2. **All previously generated blocks** (cumulative intelligence)
3. **Block definition** (from registry: purpose, typical_length, structure)
4. **Generation instruction:**

```markdown
## Your Task

Generate ONLY the **${canonical_name}** block for this meeting.

### Block Specification
- **ID:** ${block_id}
- **Name:** ${canonical_name}
- **Purpose:** ${purpose}
- **Typical Length:** ${typical_length}
- **Structure:** ${structure_requirements}

### Context Provided
1. **Full Transcript:** [Complete meeting transcript below]
2. **Previously Generated Blocks:** [All completed blocks below]

### Requirements
- Use canonical filename: `${block_id}_${canonical_name}.md`
- Include YAML frontmatter: created, last_edited, version
- Follow structure from registry definition
- Write ${typical_length} words
- Be specific and actionable
- Extract information from transcript
- Reference prior blocks where relevant
- Include feedback checkbox: `**Feedback**: - [ ] Useful`

### Output Format

```markdown
---
created: ${date}
last_edited: ${date}
version: 1.0
---

# ${canonical_name}

---
**Feedback**: - [ ] Useful
---

[Block content following registry structure]
```

Generate this block now.
```

---

### STEP 5: Validate Generated Block

**Quality Checks:**
- ✅ File has correct name: `B##_CANONICAL_NAME.md`
- ✅ Has YAML frontmatter
- ✅ Has feedback checkbox
- ✅ Content length in reasonable range (not empty, not >5000 words)
- ✅ Content is specific to this meeting (no placeholders)
- ✅ Follows structure from registry

**Validation Script:**
```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/output_validator.py "$block_file"
```

**If validation fails:**
- Log error
- Delete invalid block file
- Do NOT update manifest
- Exit with failure

---

### STEP 6: Update Manifest

**Mark block as completed:**

```bash
# Update manifest.json
jq '.blocks |= map(if .block_id == "B03" then .status = "completed" | .completed_at = "'$(date -Iseconds)'" else . end)' \
  "$folder/manifest.json" > "$folder/manifest.json.tmp"
mv "$folder/manifest.json.tmp" "$folder/manifest.json"
```

---

### STEP 7: Check if All Blocks Complete

**Count pending blocks:**
```bash
pending_count=$(jq '[.blocks[] | select(.status == "pending")] | length' "$folder/manifest.json")
```

**If all complete (pending_count == 0):**

```bash
# Rename folder: [M] → [P]
new_folder="${folder%_\[M\]}_[P]"
mv "$folder" "$new_folder"

echo "✓ All blocks complete: $(basename $new_folder)"

# Check if communications needed
if [ -f "$new_folder/B14_BLURBS_REQUESTED.md" ] || [ -f "$new_folder/B25_DELIVERABLE_CONTENT_MAP.md" ]; then
  echo "📧 Communications needed (B14 or B25 exists)"
  echo "  → Will be processed by Communications Generator"
  echo "  → State: [P] (awaiting communications)"
else
  echo "✓ No communications needed"
  echo "  → Moving directly to [R] state"
  # Rename [P] → [R] directly if no communications needed
  final_folder="${new_folder%_[P]}_[R]"
  mv "$new_folder" "$final_folder"
  echo "✓ Ready for deployment: $(basename $final_folder)"
fi
```

**If blocks remaining:**
```bash
echo "✓ Generated: ${block_id}_${canonical_name}.md"
echo "  Remaining: $pending_count blocks"
```

---

## State Machine

**State Definitions:**
- **[M]:** Manifest created, blocks being generated
- **[P]:** Processing complete (all intelligence blocks done), may need communications
- **[R]:** Ready for deployment (communications done or not needed)

**State Transitions:**
- `[M] → [P]`: All blocks generated
- `[P] → [R]`: Communications complete (or skipped if not needed)

**Communications Trigger:**
- Folder enters [P] state → Check for B14 or B25
- If either exists → Communications Generator will process
- If neither exists → Move directly to [R] state

---

## Error Handling

**If transcript missing:**
- Log error: "Cannot generate without transcript"
- Skip folder

**If manifest malformed:**
- Log error with JSON parse details
- Skip folder
- Alert for manual review

**If block generation fails:**
- Log error
- Do NOT update manifest
- Do NOT rename folder
- Preserve state for retry

**If validation fails:**
- Delete invalid block
- Log specific validation error
- Allow retry on next run

---

## Success Output

**Case 1: Block generated, more remaining:**
```
✓ Generated: B03_STAKEHOLDER_INTELLIGENCE.md (850 words)
✓ Manifest updated: 3/7 blocks complete
✓ Meeting: 2025-11-16_Client_Call_[M]
  Remaining: 4 blocks
```

**Case 2: Final block generated:**
```
✓ Generated: B09_CONTEXT_CONNECTIONS.md (600 words)
✓ All blocks complete: 7/7
✓ Renamed: 2025-11-16_Client_Call_[M] → 2025-11-16_Client_Call_[P]
✓ Ready for placement
```

---

## Design Principles

**One Block, One Turn:**
- Each block gets dedicated LLM turn
- Full cognitive focus on single artifact
- No splitting attention across multiple blocks

**Full Context Always:**
- Complete transcript provided every time
- All prior blocks provided as context
- Cumulative intelligence building

**Canonical Naming:**
- Names pulled from registry (no drift)
- Format: `B##_CANONICAL_NAME.md`
- Never deviate from registry

**Idempotent:**
- Check file existence before generation
- Skip if block file already exists
- Manifest is source of truth

**Resumable:**
- Parse manifest to find next pending
- Folder state survives crashes
- Generation continues from last successful block

---

## Notes

- **Incremental:** ONE block per run
- **Frequency:** Run every 30 minutes
- **Priority:** Process blocks in manifest order (priority field)
- **Token Efficiency:** Only generate what's needed, skip existing blocks
- **Quality:** Validation gate prevents bad blocks from being marked complete

---

**Execution:** This prompt is invoked by scheduled task every 30 minutes.




