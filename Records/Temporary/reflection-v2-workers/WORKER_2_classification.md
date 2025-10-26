# Worker 2: Classification & Block Registry

**Mission:** Multi-label classifier + block type registry setup\
**Time Estimate:** 60 minutes\
**Dependencies:** None (can start immediately)\
**Parallelizable:** Yes (with Worker 1)

---

## Objectives

1. ✅ Create reflection block registry (B50-B99) in `file N5/prefs/reflection_block_registry.json`
2. ✅ Update main block registry to include reflection blocks
3. ✅ Build multi-label classifier: `file N5/scripts/reflection_classifier.py`
4. ✅ Define classification logic with confidence scoring

---

## Deliverables

### 1. Reflection Block Registry

**File:** `file N5/prefs/reflection_block_registry.json`

**Structure:**

```json
{
  "version": "1.0.0",
  "blocks": {
    "B50": {
      "name": "Personal Reflection",
      "description": "Stream-of-consciousness self-reflection for personal growth",
      "domain": "internal",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B50-personal-reflection.md",
      "auto_approve_threshold": 10
    },
    "B60": {
      "name": "Learning & Synthesis",
      "description": "Capture insights from research, reading, conversations",
      "domain": "internal",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B60-learning-synthesis.md",
      "auto_approve_threshold": 10
    },
    "B70": {
      "name": "Thought Leadership",
      "description": "Original thinking on industry topics for professional audience",
      "domain": "external_professional",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B70-thought-leadership.md",
      "auto_approve_threshold": 5
    },
    "B71": {
      "name": "Market Analysis",
      "description": "Analysis of market trends, competitor landscape, opportunities",
      "domain": "internal",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B71-market-analysis.md",
      "auto_approve_threshold": 10
    },
    "B72": {
      "name": "Product Analysis",
      "description": "Deep dive on product decisions, features, roadmap",
      "domain": "internal",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B72-product-analysis.md",
      "auto_approve_threshold": 10
    },
    "B73": {
      "name": "Strategic Thinking",
      "description": "High-level strategy, positioning, long-term vision",
      "domain": "internal",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B73-strategic-thinking.md",
      "auto_approve_threshold": 10
    },
    "B80": {
      "name": "LinkedIn Post",
      "description": "Social content for external professional audience",
      "domain": "external_social",
      "voice_profile": "N5/prefs/communication/social-media-voice.md",
      "style_guide": "N5/prefs/communication/style-guides/linkedin-posts.md",
      "auto_approve_threshold": 0
    },
    "B81": {
      "name": "Blog Post",
      "description": "Long-form content for Careerspan blog or external publication",
      "domain": "external_professional",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B81-blog-post.md",
      "auto_approve_threshold": 0
    },
    "B82": {
      "name": "Executive Memo",
      "description": "Structured memo for internal stakeholders or external partners",
      "domain": "internal",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B82-executive-memo.md",
      "auto_approve_threshold": 5
    },
    "B90": {
      "name": "Insight Compounding",
      "description": "Synthesize patterns across multiple reflections over time",
      "domain": "internal",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B90-insight-compound.md",
      "auto_approve_threshold": 10
    },
    "B91": {
      "name": "Meta-Reflection",
      "description": "Reflection on reflection process itself, evolution of thinking",
      "domain": "internal",
      "voice_profile": "N5/prefs/communication/voice.md",
      "style_guide": "N5/prefs/communication/style-guides/reflections/B91-meta-reflection.md",
      "auto_approve_threshold": 10
    }
  }
}
```

### 2. Update Main Block Registry

**File:** `file N5/prefs/block_type_registry.json`

Add reflection blocks (B50-B99) to existing registry alongside meeting blocks (B01-B49).

---

### 3. Multi-Label Classifier

**File:** `file N5/scripts/reflection_classifier.py`

**Requirements:**

- Read transcript from incoming directory
- Classify into 1+ categories (multi-label)
- Return confidence scores (0.0-1.0)
- Map classifications to block types
- Log classification rationale

**Classification Categories:**

```python
CATEGORIES = {
    "personal": ["B50"],  # Personal Reflection
    "learning": ["B60"],  # Learning & Synthesis
    "thought_leadership": ["B70"],  # External professional content
    "market_analysis": ["B71"],
    "product_analysis": ["B72"],
    "strategic": ["B73"],
    "social_post": ["B80"],  # LinkedIn, social
    "blog": ["B81"],
    "executive_memo": ["B82"],
    "compound": ["B90"],  # Pattern detection across reflections
    "meta": ["B91"]  # Reflection on reflection
}
```

**Classification Logic:**

```python
def classify_reflection(transcript_text: str) -> dict:
    """
    Multi-label classification with confidence scoring.
    
    Returns:
    {
        "classifications": [
            {"category": "strategic", "blocks": ["B73"], "confidence": 0.85},
            {"category": "product_analysis", "blocks": ["B72"], "confidence": 0.72}
        ],
        "recommended_blocks": ["B73", "B72"],
        "rationale": "Strategic discussion of product roadmap..."
    }
    """
    
    # Keywords/patterns for each category
    patterns = {
        "personal": ["feeling", "personally", "struggling with", "learning about myself"],
        "learning": ["insight from", "learned that", "discovered", "synthesis"],
        "thought_leadership": ["industry", "trend", "future of", "prediction"],
        "market_analysis": ["competitor", "market", "landscape", "positioning"],
        "product_analysis": ["feature", "roadmap", "user", "product"],
        "strategic": ["strategy", "vision", "long-term", "positioning"],
        "social_post": ["announcement", "sharing", "excited to", "proud to"],
        "blog": ["deep dive", "comprehensive", "detailed analysis"],
        "executive_memo": ["decision", "recommendation", "action items"],
        "compound": ["pattern across", "noticed over time", "evolution of"],
        "meta": ["reflection process", "how I think", "my thinking"]
    }
    
    # Score each category
    scores = {}
    for category, keywords in patterns.items():
        score = calculate_keyword_density(transcript_text, keywords)
        if score > 0.3:  # Threshold
            scores[category] = score
    
    # Convert to block recommendations
    classifications = []
    for category, confidence in scores.items():
        classifications.append({
            "category": category,
            "blocks": CATEGORIES[category],
            "confidence": confidence
        })
    
    # Extract all recommended blocks
    recommended_blocks = []
    for c in classifications:
        recommended_blocks.extend(c["blocks"])
    
    return {
        "classifications": classifications,
        "recommended_blocks": list(set(recommended_blocks)),
        "rationale": generate_rationale(transcript_text, classifications)
    }
```

**Usage:**

```bash
python3 /home/workspace/N5/scripts/reflection_classifier.py \
  --input /home/workspace/N5/records/reflections/incoming/2025-10-24_reflection.m4a.transcript.jsonl \
  --output /home/workspace/N5/records/reflections/incoming/2025-10-24_reflection.classification.json
```

---

## Testing

1. Test with personal reflection text → Should return B50
2. Test with strategic analysis → Should return B73
3. Test with hybrid content → Should return multiple blocks
4. Verify confidence scores are reasonable
5. Verify rationale makes sense

---

## Principles Applied

- **P2 (SSOT):** Block registry is single source for all block definitions
- **P8 (Minimal Context):** Classifier only loads transcript, not full system
- **P18 (Verify State):** Validate block IDs before returning blocks
- **P19 (Error Handling):** Comprehensive error handling
- **P21 (Document Assumptions):** Classification rationale included

---

## Success Criteria

Worker 2 is complete when:

1. ✅ Reflection block registry (B50-B99) created
2. ✅ Main block registry updated
3. ✅ Classifier script functional
4. ✅ Multi-label classification works
5. ✅ Classification → block mapping works
6. ✅ Confidence scoring works
7. ✅ All tests pass

---

**Status:** ✅ COMPLETE\
**Created:** 2025-10-24\
**Completed:** 2025-10-25 21:00 ET\
**Duration:** \~20 minutes