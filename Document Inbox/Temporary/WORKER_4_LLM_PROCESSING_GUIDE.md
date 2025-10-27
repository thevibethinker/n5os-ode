# Worker 4: LLM Content Generation Guide

**Purpose:** How to use Worker 4's generated prompts for actual content generation

---

## Overview

Worker 4 creates **structured prompts** for LLM processing. The prompts are saved to `generation_prompts/` and contain all the context needed to generate final block content.

---

## Two-Phase Workflow

### Phase 1: Prompt Generation (Completed by Worker 4)

```bash
python3 N5/scripts/reflection_block_generator.py --input <transcript.jsonl>
```

**Output:**
- `generation_prompts/B73_prompt.md` - Full context + instructions
- `blocks/B73_strategic-thinking.md` - Placeholder file

### Phase 2: Content Generation (Manual or Automated)

**Option A: Manual (In Zo Chat)**
1. Read prompt file: `cat generation_prompts/B73_prompt.md`
2. Send to Zo: "Process this prompt and generate the final block content"
3. Save output to `blocks/B73_strategic-thinking.md`

**Option B: Batch Processing Script**
Create a helper script to process all prompts:

```python
#!/usr/bin/env python3
"""Process all generation prompts through LLM and save to blocks."""

from pathlib import Path
import sys

def process_prompts(output_dir: Path):
    prompts_dir = output_dir / "generation_prompts"
    blocks_dir = output_dir / "blocks"
    
    for prompt_file in prompts_dir.glob("*_prompt.md"):
        # Extract block ID
        block_id = prompt_file.stem.replace("_prompt", "")
        
        # Read prompt
        with open(prompt_file, 'r') as f:
            prompt = f.read()
        
        # TODO: Send to LLM API
        # content = llm_api.generate(prompt)
        
        print(f"Process: {prompt_file.name}")
        print(f"  → Save to: blocks/{block_id}_*.md")
        print()

if __name__ == "__main__":
    output_dir = Path(sys.argv[1])
    process_prompts(output_dir)
```

---

## Prompt Structure

Each prompt contains:

1. **Instructions** - What to generate and how
2. **Context** - Classification confidence score
3. **Voice Profile** - Full voice.md or social-media-voice.md
4. **Style Guide** - Complete style guide with QA checklist
5. **Transcript** - Full reflection text

**Example prompt structure:**
```markdown
Transform the following stream-of-consciousness reflection into a Strategic Thinking 
following the style guide and voice profile provided.

CLASSIFICATION CONFIDENCE: 0.88

VOICE PROFILE:
[16KB of voice.md content]

STYLE GUIDE:
[7KB of style guide with structure, examples, QA checklist]

TRANSCRIPT:
[5KB of reflection text]

Generate the Strategic Thinking block content now, following all requirements from the style guide.
Output only the final markdown content, no preamble or explanation.
```

---

## Manual Processing Workflow

### Step 1: Find Pending Outputs

```bash
find N5/records/reflections/outputs -name "generation_prompts" -type d
```

### Step 2: Review Metadata

```bash
cat N5/records/reflections/outputs/2025-10-21/reflections-on-n5-os/metadata.json
```

Check:
- `approval_mode`: "auto" or "manual"
- `blocks_generated`: List of blocks to generate

### Step 3: Process Each Prompt

For each block in `blocks_generated`:

1. **Read prompt:**
   ```bash
   cat generation_prompts/B73_prompt.md
   ```

2. **In Zo chat:**
   ```
   Generate the Strategic Thinking block following this prompt:
   [paste prompt content]
   ```

3. **Save output:**
   ```bash
   # Copy Zo's response to the block file
   vim blocks/B73_strategic-thinking.md
   ```

4. **Verify:**
   - Check word count matches style guide targets
   - Review QA checklist items
   - Ensure voice/tone match profile

### Step 4: Update Metadata

Once all blocks generated, update `metadata.json`:

```json
{
  "status": "generated",  // changed from "awaiting_approval"
  "generated_at_iso": "2025-10-27T02:00:00Z",
  "blocks_generated": [
    {
      "block_id": "B73",
      "generated": true,
      "word_count": 487  // actual count
    }
  ]
}
```

---

## Automated Processing (Future)

For automated processing via API:

```python
import anthropic
from pathlib import Path

def generate_block_content(prompt: str) -> str:
    """Send prompt to Claude API and return generated content."""
    
    client = anthropic.Anthropic(api_key="...")
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    return message.content[0].text

def process_reflection_output(output_dir: Path):
    """Process all prompts in an output directory."""
    
    prompts_dir = output_dir / "generation_prompts"
    blocks_dir = output_dir / "blocks"
    
    for prompt_file in prompts_dir.glob("*_prompt.md"):
        print(f"Processing {prompt_file.name}...")
        
        # Read prompt
        with open(prompt_file, 'r') as f:
            prompt = f.read()
        
        # Generate content
        content = generate_block_content(prompt)
        
        # Save to corresponding block file
        block_id = prompt_file.stem.replace("_prompt", "")
        block_files = list(blocks_dir.glob(f"{block_id}_*.md"))
        
        if block_files:
            block_file = block_files[0]
            with open(block_file, 'w') as f:
                f.write(content)
            print(f"  ✓ Saved to {block_file.name}")
        else:
            print(f"  ✗ No matching block file found for {block_id}")
```

---

## Quality Checks

After generation, verify:

1. **Word Count**
   ```bash
   wc -w blocks/*.md
   ```
   Compare to style guide targets (500-700, 300-500, etc.)

2. **Structure**
   - Check headers match style guide
   - Verify required sections present
   - Ensure proper markdown formatting

3. **Voice/Tone**
   - Read output aloud
   - Check against voice profile examples
   - Verify formality level appropriate for domain

4. **QA Checklist**
   - Review style guide QA section
   - Check off each item manually

---

## Integration with Approval Workflow

Once content generated:

1. **If approval_mode = "auto":**
   - Move to Worker 5 for automatic processing
   - Blocks will be ingested into Knowledge/Lists

2. **If approval_mode = "manual":**
   - Present blocks to V for review
   - V can edit, approve, or reject
   - Update metadata with approval status

---

## Example Complete Workflow

```bash
# 1. Generate prompts
python3 N5/scripts/reflection_block_generator.py \
  --input incoming/2025-10-21_reflections-on-n5-os.m4a.transcript.jsonl

# 2. Review metadata
cat outputs/2025-10-21/reflections-on-n5-os/metadata.json

# 3. Process first prompt manually
cat outputs/2025-10-21/reflections-on-n5-os/generation_prompts/B73_prompt.md

# 4. In Zo: Generate content from prompt

# 5. Save output
vim outputs/2025-10-21/reflections-on-n5-os/blocks/B73_strategic-thinking.md

# 6. Repeat for remaining blocks (B72, B70)

# 7. Update metadata.json status to "generated"

# 8. Pass to Worker 5 for approval
```

---

## Tips

1. **Process in order of confidence** - Start with highest confidence classifications
2. **Batch similar blocks** - Process all B73s together to maintain consistency
3. **Review style guides first** - Familiarize yourself with requirements before generating
4. **Use temperature=0.7** - Good balance for creative but consistent output
5. **Iterate if needed** - Don't hesitate to regenerate if quality is off

---

## Next Steps

After content generation complete:
- Worker 5 will handle approval workflow
- Auto-approved blocks → Knowledge/Lists
- Manual blocks → Present to V for review

---

**Created:** 2025-10-27 01:38 ET  
**Worker 4 Status:** ✅ COMPLETE
