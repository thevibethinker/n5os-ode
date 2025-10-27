# Worker 4: Block Content Generator

**Mission:** Generate block content from transcripts using classification + style guides  
**Time Estimate:** 75 minutes  
**Dependencies:** Worker 2 (classifier), Worker 3 (style guides)  
**Parallelizable:** No

---

## Objectives

1. ✅ Build block content generator: `N5/scripts/reflection_block_generator.py`
2. ✅ Integrate classification → block selection → content generation
3. ✅ Apply correct voice profile per block type
4. ✅ Use style guides for output formatting
5. ✅ Save generated blocks to output directory

---

## Deliverables

### Script: `N5/scripts/reflection_block_generator.py`

**Requirements:**
- Read transcript + classification from incoming directory
- Load relevant block definitions from registry
- For each recommended block:
  - Load appropriate style guide
  - Load appropriate voice profile
  - Generate block content
  - Save to output directory
- Create metadata file tracking generation details
- Support dry-run mode

---

## Input/Output

**Input:**
```
N5/records/reflections/incoming/
├── 2025-10-24_pricing-strategy.m4a.transcript.jsonl
└── 2025-10-24_pricing-strategy.classification.json
```

**Output:**
```
N5/records/reflections/outputs/2025-10-24/pricing-strategy/
├── blocks/
│   ├── B71_market-analysis.md
│   ├── B72_product-analysis.md
│   └── B73_strategic-thinking.md
├── metadata.json
└── transcript.jsonl  # copy of original
```

**Metadata JSON:**
```json
{
  "reflection_id": "2025-10-24_pricing-strategy",
  "generated_at_iso": "2025-10-24T20:30:00Z",
  "source_file": "2025-10-24_pricing-strategy.m4a",
  "classifications": [
    {"category": "market_analysis", "confidence": 0.82},
    {"category": "product_analysis", "confidence": 0.75},
    {"category": "strategic", "confidence": 0.88}
  ],
  "blocks_generated": [
    {
      "block_id": "B71",
      "block_name": "Market Analysis",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B71-market-analysis.md",
      "word_count": 427,
      "auto_approve_eligible": true,
      "auto_approve_threshold": 10
    },
    {
      "block_id": "B72",
      "block_name": "Product Analysis",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B72-product-analysis.md",
      "word_count": 385,
      "auto_approve_eligible": true,
      "auto_approve_threshold": 10
    },
    {
      "block_id": "B73",
      "block_name": "Strategic Thinking",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B73-strategic-thinking.md",
      "word_count": 512,
      "auto_approve_eligible": true,
      "auto_approve_threshold": 10
    }
  ],
  "status": "awaiting_approval",
  "approval_mode": "manual"  # or "auto" if all blocks auto-approved
}
```

---

## Content Generation Logic

```python
def generate_block(transcript: str, block_def: dict, classification: dict) -> str:
    """
    Generate block content using:
    - Transcript text
    - Block definition (from registry)
    - Classification confidence
    - Voice profile
    - Style guide
    """
    
    # Load voice profile
    voice_profile = load_file(block_def["voice_profile"])
    
    # Load style guide
    style_guide = load_file(block_def["style_guide"])
    
    # Build generation prompt
    prompt = f"""
Transform the following stream-of-consciousness reflection into a {block_def["name"]} 
following the style guide and voice profile provided.

TRANSCRIPT:
{transcript}

VOICE PROFILE:
{voice_profile}

STYLE GUIDE:
{style_guide}

CLASSIFICATION CONFIDENCE: {classification["confidence"]}

Generate the {block_def["name"]} block content:
"""
    
    # Generate content (using LLM or transformation logic)
    content = generate_content(prompt)
    
    # Validate against style guide QA checklist
    if not validate_content(content, style_guide):
        logger.warning(f"Content validation failed for {block_def['block_id']}")
    
    return content
```

---

## Voice Routing

**Decision Tree:**
```python
def get_voice_profile(block_id: str, block_def: dict) -> str:
    """Determine which voice profile to use based on block domain."""
    
    domain = block_def.get("domain", "internal")
    
    if domain == "external_social":
        return "N5/prefs/communication/social-media-voice.md"
    elif domain in ["external_professional", "internal"]:
        return "N5/prefs/communication/voice.md"
    else:
        logger.warning(f"Unknown domain {domain}, defaulting to voice.md")
        return "N5/prefs/communication/voice.md"
```

---

## Auto-Approve Logic

```python
def determine_approval_mode(blocks_generated: list) -> str:
    """
    Determine if blocks can be auto-approved.
    
    Rules:
    - ALL blocks must have auto_approve_threshold > 0
    - ALL blocks must be under their threshold count
    - External social (B80-B89) never auto-approve
    """
    
    for block in blocks_generated:
        block_def = get_block_definition(block["block_id"])
        
        # Check if auto-approve eligible
        if block_def["auto_approve_threshold"] == 0:
            return "manual"
        
        # Check historical count for this block type
        count = count_blocks_generated(block["block_id"], days=30)
        if count >= block_def["auto_approve_threshold"]:
            return "manual"
    
    return "auto"
```

---

## Usage

```bash
# Generate blocks for a single reflection
python3 /home/workspace/N5/scripts/reflection_block_generator.py \
  --input /home/workspace/N5/records/reflections/incoming/2025-10-24_pricing-strategy.m4a.transcript.jsonl \
  --output /home/workspace/N5/records/reflections/outputs/2025-10-24/pricing-strategy/ \
  [--dry-run]

# Generate blocks for all pending reflections
python3 /home/workspace/N5/scripts/reflection_block_generator.py \
  --process-all \
  [--dry-run]
```

---

## Testing

1. Generate blocks for personal reflection → Should create B50
2. Generate blocks for strategic reflection → Should create B73
3. Generate blocks for multi-category → Should create multiple blocks
4. Verify voice profile routing is correct
5. Verify auto-approve logic works
6. Test dry-run mode

---

## Principles Applied

- **P7 (Dry-Run):** Dry-run mode supported
- **P18 (Verify State):** Validate all blocks generated successfully
- **P19 (Error Handling):** Handle missing style guides, voice profiles
- **P20 (Modular):** Each block generated independently

---

## Success Criteria

Worker 4 is complete when:
1. ✅ Block generator script functional
2. ✅ Classification → block selection works
3. ✅ Voice profile routing correct
4. ✅ Style guide application works
5. ✅ Auto-approve logic implemented
6. ✅ Metadata tracking complete
7. ✅ All tests pass

---

**Status:** ✅ COMPLETE  
**Created:** 2025-10-24  
**Completed:** 2025-10-27  
**Actual Time:** ~6 minutes  
**Deliverable:** `/home/workspace/N5/scripts/reflection_block_generator.py`
