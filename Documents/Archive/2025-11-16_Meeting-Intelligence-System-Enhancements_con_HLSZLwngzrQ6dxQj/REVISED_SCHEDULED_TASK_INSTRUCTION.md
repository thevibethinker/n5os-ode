---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Revised Scheduled Task Instruction

## Problem Identified

The current scheduled task instruction is **incomplete and misleading**. It tells the LLM to:

1. Run the Python script (`intelligence_block_generator.py`)
2. Claims the script will "Write the block to the blocks/ subdirectory" and "Update the manifest"

**But the Python script does NOT do this.** The script only:
- Creates prompt files (`B*_*_prompt.txt`)
- Outputs a message saying "(Actual LLM generation happens in the Zo conversation context)"
- Reports "success" even though no blocks were generated

This causes Haiku to think the job is done when it's only halfway complete.

---

## Root Cause

**The Python script is designed as a PROMPT GENERATOR, not a BLOCK GENERATOR.**

The workflow should be:
1. **Python script** → Prepare prompts (mechanical work)
2. **LLM** → Read prompts, generate block content, save files, update manifest (semantic work)

But the scheduled task instruction **stops after step 1** and doesn't guide the LLM through step 2.

---

## Revised Instruction (v2.0)

```markdown
🧠 Meeting Intelligence Block Generation (Pipeline 1)

Generate up to 3 meeting intelligence blocks per run with full context.

**STEP 1: Find meeting with pending blocks**
Run: `ls -d /home/workspace/Personal/Meetings/Inbox/*/ | while read dir; do test -f "$dir/manifest.json" && grep -q '"status": "pending"' "$dir/manifest.json" 2>/dev/null && echo "$dir"; done | head -1`

If empty, exit silently (no meetings need intelligence generation).

If found, store the path as MEETING_PATH and proceed to STEP 2.

**STEP 2: Prepare generation prompts**
Run:
`python3 /home/workspace/N5/scripts/meeting_pipeline/intelligence_block_generator.py --meeting-path $MEETING_PATH --max-blocks 3`

This creates prompt files (B*_*_prompt.txt) in the meeting folder.

**STEP 3: Generate blocks from prompts**
For each prompt file created in STEP 2:

1. Read the prompt file: `cat $MEETING_PATH/B*_*_prompt.txt`
2. Generate the block content following the prompt instructions exactly
3. Save output to `$MEETING_PATH/BXX_BLOCK_NAME.md` with YAML frontmatter:
   ```yaml
   ---
   created: YYYY-MM-DD
   last_edited: YYYY-MM-DD
   version: 1.0
   ---
   ```
4. Ensure block content is comprehensive, accurate, and extracts all relevant details from transcript

**STEP 4: Update manifest**
After generating all blocks:

1. Read current manifest: `cat $MEETING_PATH/manifest.json`
2. For each generated block, update its entry in the manifest:
   - Change `"status": "pending"` to `"status": "generated"`
   - Add `"generated_at": "YYYY-MM-DDTHH:MM:SSZ"`
3. Write updated manifest back to file

**STEP 5: Verify and report**
Confirm files were created:
```bash
ls -lh $MEETING_PATH/B*.md
```

Output summary:
- Meeting processed
- Blocks generated (list IDs)
- Blocks remaining
- Manifest updated: yes/no

**CRITICAL: You MUST complete ALL 5 steps. The Python script in STEP 2 only prepares prompts - it does NOT generate blocks. YOU must generate the actual block content in STEP 3.**
```

---

## Alternative Approach: Make the Python Script Do Everything

Instead of having the LLM do the generation, the Python script could call the LLM API directly:

```python
# In intelligence_block_generator.py, after creating prompt:

import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=4000,
    messages=[{
        "role": "user",
        "content": prompt
    }]
)

block_content = response.content[0].text

# Save block to file
block_file = meeting_folder / f"{block_id}_{block_name}.md"
with open(block_file, 'w') as f:
    f.write(f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
---

{block_content}
""")

# Update manifest...
```

**Pros:**
- Python script is self-contained
- Scheduled task instruction is simpler
- No risk of LLM misunderstanding what to do

**Cons:**
- Requires API key configuration in script
- Less flexible (can't leverage conversation context)
- Harder to debug generation quality

---

## Recommendation

**Option 1 (Preferred):** Update the scheduled task instruction to clearly guide the LLM through all 5 steps, with explicit emphasis on step 3 (the actual generation).

**Option 2:** Modify the Python script to call the LLM API directly, making it a true end-to-end block generator. Then simplify the scheduled task to just run the script.

**Hybrid:** Keep the script as-is for preparing prompts, but add a helper function that the LLM can call to execute the generation workflow. Something like:

```python
# New function in the script
def execute_block_generation(meeting_path: str, max_blocks: int = 3):
    """Full pipeline: prepare prompts → call LLM → save blocks → update manifest"""
    # Prepare prompts (existing logic)
    # Call LLM API for each prompt
    # Save generated content
    # Update manifest
    # Return summary
```

Then the scheduled task just runs:
```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/intelligence_block_generator.py \
  --meeting-path "$MEETING_PATH" --max-blocks 3 --execute
```

---

## Next Steps

1. Choose approach (Option 1 recommended for now)
2. Update scheduled task instruction with revised v2.0
3. Test with Haiku model on next scheduled run
4. Monitor for successful block generation
5. Consider Option 2 or Hybrid if issues persist

