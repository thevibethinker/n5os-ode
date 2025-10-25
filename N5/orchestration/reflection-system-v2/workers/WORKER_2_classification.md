# Worker 2: Classification & Block Registry

**Mission:** Multi-label classifier + block type registry setup  
**Time Estimate:** 60 minutes  
**Dependencies:** None (can start immediately)  
**Parallelizable:** Yes (with Worker 1)

---

## Objectives

1. ✅ Create reflection block registry (B50-B99) in `N5/prefs/reflection_block_registry.json`
2. ✅ Update main block registry to include reflection blocks
3. ✅ Build multi-label classifier: `N5/scripts/reflection_classifier.py`
4. ✅ Define classification → block mapping logic
5. ✅ Support `--dry-run` flag

---

## Deliverables

### Primary
- `N5/prefs/reflection_block_registry.json` - Reflection block definitions (B50-B99)
- `N5/scripts/reflection_classifier.py` - Multi-label classification script
- Update to `N5/prefs/block_type_registry.json` - Add reflection blocks

### Secondary
- Classification → block mapping matrix
- Confidence scoring for classifications
- Logging with classification rationale

---

## Block Registry Structure

### File: `N5/prefs/reflection_block_registry.json`

```json
{
  "artifact": "Reflection Block Type Registry",
  "type": "Companion",
  "code": "50-99",
  "short_name": "Reflection_Blocks",
  "version": "1.0",
  "purpose": "Define reflection block types (B50-B99) with voice routing and style guide references",
  "blocks": {
    "B50": {
      "name": "PERSONAL_REFLECTION",
      "purpose": "Stream of consciousness processing, personal insights",
      "audience": "internal",
      "voice_profile": "voice.md",
      "priority": "HIGH",
      "guidance": [
        "Preserve raw thinking, don't over-polish",
        "Capture decision rationale and emotional context",
        "Include doubts, questions, uncertainties",
        "This is for V's eyes only - total honesty"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B50-personal-reflection.md"
    },
    "B51": {
      "name": "LEARNING_INSIGHT",
      "purpose": "Lessons learned, mental models, skill development",
      "audience": "internal",
      "voice_profile": "voice.md",
      "priority": "HIGH",
      "guidance": [
        "Extract specific, actionable lessons",
        "Connect to existing mental models",
        "Note what changed in thinking",
        "Include failure analysis if relevant"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B51-learning-insight.md"
    },
    "B52": {
      "name": "STRATEGIC_MEMO",
      "purpose": "Internal strategic thinking, decision frameworks",
      "audience": "internal",
      "voice_profile": "voice.md",
      "priority": "MEDIUM",
      "guidance": [
        "Structure: Context → Analysis → Options → Recommendation",
        "Include trade-offs and risks",
        "Reference relevant data/insights",
        "Decision-ready format"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B52-strategic-memo.md"
    },
    "B53": {
      "name": "DEBATE_POINTS",
      "purpose": "Internal argument mapping, pros/cons analysis",
      "audience": "internal",
      "voice_profile": "voice.md",
      "priority": "MEDIUM",
      "guidance": [
        "Two-column format: For vs Against",
        "Steel-man both sides",
        "Include uncertainty levels",
        "Note information needed to decide"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B53-debate-points.md"
    },
    "B60": {
      "name": "THOUGHT_LEADERSHIP",
      "purpose": "Long-form article foundations, op-ed material",
      "audience": "external_professional",
      "voice_profile": "voice.md",
      "priority": "HIGH",
      "guidance": [
        "Structure: Hook → Thesis → Evidence → Implications → Call-to-action",
        "1000-1500 word foundation (will be edited)",
        "Include supporting data/examples",
        "Professional tone, accessible language"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B60-thought-leadership.md"
    },
    "B61": {
      "name": "MARKET_ANALYSIS",
      "purpose": "Market observations, competitive intelligence",
      "audience": "external_professional",
      "voice_profile": "voice.md",
      "priority": "HIGH",
      "guidance": [
        "Structured sections: Observation → Implications → Strategic Response",
        "Data-driven where possible",
        "Competitive positioning analysis",
        "Actionable insights"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B61-market-analysis.md"
    },
    "B62": {
      "name": "PRODUCT_ANALYSIS",
      "purpose": "Product strategy reflections, feature rationale",
      "audience": "external_professional",
      "voice_profile": "voice.md",
      "priority": "HIGH",
      "guidance": [
        "Link to user pain points",
        "Explain design decisions",
        "Include trade-offs made",
        "Defensible rationale"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B62-product-analysis.md"
    },
    "B63": {
      "name": "CURRICULUM_MODULE",
      "purpose": "Training/education content building blocks",
      "audience": "external_professional",
      "voice_profile": "voice.md",
      "priority": "MEDIUM",
      "guidance": [
        "Learning objective first",
        "Step-by-step breakdown",
        "Include examples and exercises",
        "Assessment criteria"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B63-curriculum-module.md"
    },
    "B80": {
      "name": "LINKEDIN_POST",
      "purpose": "Ready-to-publish LinkedIn post",
      "audience": "external_social",
      "voice_profile": "social-media-voice.md",
      "priority": "HIGH",
      "guidance": [
        "Hook in first 2 lines",
        "Story-driven, personal angle",
        "300-500 words max",
        "CTA at end",
        "Use line breaks for readability"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B80-linkedin-post.md"
    },
    "B81": {
      "name": "TWITTER_THREAD",
      "purpose": "Thread structure with hooks",
      "audience": "external_social",
      "voice_profile": "social-media-voice.md",
      "priority": "MEDIUM",
      "guidance": [
        "Tweet 1: Hook + promise",
        "Tweets 2-N: Deliver on promise",
        "Each tweet: standalone + thread flow",
        "280 chars max per tweet",
        "End with CTA or question"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B81-twitter-thread.md"
    },
    "B82": {
      "name": "STORY_SNIPPET",
      "purpose": "Narrative moments for storytelling",
      "audience": "external_social",
      "voice_profile": "social-media-voice.md",
      "priority": "MEDIUM",
      "guidance": [
        "Scene-setting details",
        "Emotional arc",
        "Relatable struggle/triumph",
        "Universal insight at end",
        "200-400 words"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B82-story-snippet.md"
    },
    "B90": {
      "name": "INSIGHT_COMPOUND",
      "purpose": "Connections across multiple reflections",
      "audience": "internal",
      "voice_profile": "voice.md",
      "priority": "LOW",
      "guidance": [
        "Identify patterns across 3+ reflections",
        "Synthesize higher-order insights",
        "Note contradictions or evolution",
        "Generate meta-questions"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B90-insight-compound.md"
    },
    "B91": {
      "name": "THEME_EMERGENCE",
      "purpose": "Patterns detected over time",
      "audience": "internal",
      "voice_profile": "voice.md",
      "priority": "LOW",
      "guidance": [
        "Identify recurring topics",
        "Track theme evolution",
        "Quantify frequency/intensity",
        "Suggest investigations"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B91-theme-emergence.md"
    },
    "B92": {
      "name": "BLOCK_SUGGESTION",
      "purpose": "New block type proposal based on recurring patterns",
      "audience": "internal",
      "voice_profile": "voice.md",
      "priority": "LOW",
      "guidance": [
        "Identify gap in current block types",
        "Show 3+ examples that don't fit",
        "Propose new block definition",
        "Justify with usage frequency"
      ],
      "style_guide": "N5/prefs/communication/style-guides/reflections/B92-block-suggestion.md"
    }
  }
}
```

---

## Classification System

### Multi-Label Categories

**Primary Content Categories:**
- `product_strategy`
- `founder_journey`
- `market_intelligence`
- `dilemma`
- `pitch_narrative`
- `announcement`
- `hiring`
- `learning`

**Audience Intent:**
- `internal_only`
- `external_professional`
- `external_social`

**Content Maturity:**
- `raw` (stream of consciousness)
- `structured` (organized thoughts)
- `polished` (nearly ready)

### Classification → Block Mapping

```json
{
  "classification_mapping": {
    "product_strategy + internal_only": ["B50", "B52", "B62"],
    "product_strategy + external_professional": ["B60", "B62"],
    "product_strategy + external_social": ["B80", "B62"],
    
    "founder_journey + internal_only": ["B50", "B51"],
    "founder_journey + external_professional": ["B60"],
    "founder_journey + external_social": ["B80", "B82"],
    
    "market_intelligence + internal_only": ["B52", "B61"],
    "market_intelligence + external_professional": ["B60", "B61"],
    "market_intelligence + external_social": ["B80", "B61"],
    
    "pitch_narrative + external_professional": ["B60", "B63"],
    "pitch_narrative + external_social": ["B80", "B81", "B82"],
    
    "dilemma + internal_only": ["B50", "B53"],
    
    "announcement + external_social": ["B80", "B81"],
    "announcement + external_professional": ["B60"],
    
    "hiring + internal_only": ["B52"],
    "hiring + external_social": ["B80"],
    
    "learning + internal_only": ["B50", "B51"],
    "learning + external_social": ["B80", "B82"]
  }
}
```

---

## Classifier Script

### File: `N5/scripts/reflection_classifier.py`

**Function:**
```python
#!/usr/bin/env python3
import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def classify_reflection(text: str) -> Dict:
    """
    Multi-label classification of reflection text.
    
    Returns:
        {
            "primary_categories": ["product_strategy", "founder_journey"],
            "audience_intent": ["internal_only"],
            "content_maturity": "raw",
            "confidence_scores": {
                "product_strategy": 0.85,
                "founder_journey": 0.72
            },
            "rationale": "Detected product strategy discussion (mentions 'feature', 'roadmap'). Founder journey evident from first-person challenges."
        }
    """
    # TODO: Implement classification logic
    # Use keyword detection + LLM-based classification
    
    pass

def get_candidate_blocks(classification: Dict) -> List[str]:
    """
    Given classification, return candidate block IDs.
    
    Returns: ["B50", "B52", "B62"]
    """
    mapping = load_classification_mapping()
    
    # Combine tags
    tags = classification["primary_categories"] + classification["audience_intent"]
    
    # Look up blocks
    blocks = set()
    for combo in generate_combinations(tags):
        if combo in mapping:
            blocks.update(mapping[combo])
    
    return sorted(blocks)

def main(reflection_file: str, dry_run: bool = False) -> int:
    """Classify reflection and return candidate blocks."""
    try:
        text = Path(reflection_file).read_text()
        
        logger.info(f"Classifying: {reflection_file}")
        classification = classify_reflection(text)
        
        logger.info(f"Classification: {classification}")
        
        blocks = get_candidate_blocks(classification)
        logger.info(f"Candidate blocks: {blocks}")
        
        if not dry_run:
            # Save classification result
            output_file = Path(reflection_file).with_suffix(".classification.json")
            output_file.write_text(json.dumps(classification, indent=2))
            logger.info(f"Saved: {output_file}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reflection_file", help="Path to reflection text file")
    parser.add_argument("--dry-run", action="store_true")
    exit(main(parser.parse_args().reflection_file, dry_run=parser.parse_args().dry_run))
```

---

## Integration with Main Block Registry

### Update: `N5/prefs/block_type_registry.json`

Add new section:

```json
{
  "blocks": {
    "B01": { ... },
    ...existing meeting blocks...
    "B31": { ... },
    
    "B50": { ...import from reflection_block_registry.json... },
    "B51": { ... },
    ...etc...
  },
  
  "reflection_combinations": {
    "PERSONAL_REFLECTION": {
      "description": "Personal stream-of-consciousness reflections",
      "block_ids": ["B50", "B51", "B52", "B53"]
    },
    "EXTERNAL_CONTENT": {
      "description": "Professional external content generation",
      "block_ids": ["B60", "B61", "B62", "B63"]
    },
    "SOCIAL_CONTENT": {
      "description": "Social media content generation",
      "block_ids": ["B80", "B81", "B82"]
    }
  }
}
```

---

## Testing Checklist

- [ ] Reflection block registry created
- [ ] Main block registry updated
- [ ] Classifier detects primary categories
- [ ] Classifier detects audience intent
- [ ] Classifier detects content maturity
- [ ] Classification → block mapping works
- [ ] Confidence scores generated
- [ ] Rationale provided for classifications
- [ ] Dry-run flag works
- [ ] Classification saved to .classification.json

---

## Principles Applied

- **P1 (Human-Readable):** Block registry is JSON, easily editable
- **P2 (SSOT):** Block registry is single source for definitions
- **P7 (Dry-Run):** Support `--dry-run` flag
- **P15 (Complete Before Claiming):** Only save classification after full analysis
- **P18 (Verify State):** Verify classification before returning blocks
- **P19 (Error Handling):** Comprehensive error handling
- **P21 (Document Assumptions):** Classification rationale included

---

## Success Criteria

Worker 2 is complete when:
1. Reflection block registry (B50-B99) created
2. Main block registry updated
3. Classifier script functional
4. Multi-label classification works
5. Classification → block mapping works
6. Confidence scoring works
7. All tests pass

---

**Status:** Ready to start  
**Created:** 2025-10-24 18:09 ET
