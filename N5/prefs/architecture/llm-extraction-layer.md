---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
status: design
---

# LLM Extraction Layer Architecture

## Principle

**Wherever you need flexible reasoning, use a prompt and an LLM call.**

Hardcoded regex/keyword patterns are:
- Brittle (miss variations)
- Maintenance-heavy (must manually add new patterns)
- Context-blind (can't understand intent)

LLM extraction is:
- Flexible (handles variations naturally)
- Self-updating (understands new contexts)
- Intent-aware (understands what V is committing to)

---

## Components to Replace

### Priority 1: Resource Extraction (b_block_parser.py)

| Current | Problem | LLM Replacement |
|---------|---------|-----------------|
| `tool_patterns` (lines 128-136) | Hardcoded list of tools | LLM extracts any commitment to send resources |
| `implicit_patterns` (lines 170-175) | Misses variations | LLM understands "I'll send", "let me share", "here's a link" |
| `topic_keywords` (lines 222-231) | Static topic list | LLM detects topics dynamically |

### Priority 2: Decision/Action Extraction

| Current | Problem | LLM Replacement |
|---------|---------|-----------------|
| `decision_signals` (line 358) | Pattern matching | LLM identifies decisions in context |
| `action_signals` (line 373) | Pattern matching | LLM extracts action items with owners |

### Priority 3: Quote/Eloquence Detection

| Current | Problem | LLM Replacement |
|---------|---------|-----------------|
| `speaker_pattern` (line 247) | Regex parsing | LLM identifies speaker turns |
| Eloquence scoring | Heuristic | LLM judges what's quotable |

---

## Design: LLM Extraction Service

### File: `N5/scripts/llm_extractor.py`

```python
"""
LLM Extraction Service

Replaces hardcoded pattern matching with flexible LLM reasoning.
Uses structured output for reliable parsing.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Prompt templates live in N5/prompts/extraction/
PROMPT_DIR = Path("/home/workspace/N5/prompts/extraction")

@dataclass
class ExtractionResult:
    """Structured extraction result"""
    items: List[Dict[str, Any]]
    confidence: float
    reasoning: str

class LLMExtractor:
    """
    Unified extraction service using LLM reasoning.
    
    Usage:
        extractor = LLMExtractor()
        resources = extractor.extract_resources(transcript_text)
        actions = extractor.extract_action_items(transcript_text)
    """
    
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load extraction prompts from files"""
        prompts = {}
        for prompt_file in PROMPT_DIR.glob("*.md"):
            prompts[prompt_file.stem] = prompt_file.read_text()
        return prompts
    
    def extract_resources(
        self, 
        text: str, 
        content_library_items: List[Dict]
    ) -> List[Dict]:
        """
        Extract resources V committed to sending.
        
        LLM receives:
        - The transcript text
        - List of available Content Library items
        
        LLM returns:
        - Commitments detected
        - Matched Content Library items
        - Suggested items if no exact match
        """
        prompt = self.prompts["extract_resources"].format(
            transcript=text,
            library_items=json.dumps(content_library_items, indent=2)
        )
        
        result = self._call_llm(prompt)
        return result.get("resources", [])
    
    def extract_action_items(self, text: str) -> List[Dict]:
        """Extract action items with owners and deadlines"""
        prompt = self.prompts["extract_actions"].format(transcript=text)
        result = self._call_llm(prompt)
        return result.get("action_items", [])
    
    def extract_decisions(self, text: str) -> List[Dict]:
        """Extract decisions made during the call"""
        prompt = self.prompts["extract_decisions"].format(transcript=text)
        result = self._call_llm(prompt)
        return result.get("decisions", [])
    
    def extract_topics(self, text: str) -> List[str]:
        """Detect conversation topics dynamically"""
        prompt = self.prompts["extract_topics"].format(transcript=text)
        result = self._call_llm(prompt)
        return result.get("topics", [])
    
    def extract_quotable_moments(self, text: str) -> List[Dict]:
        """Find eloquent, quotable moments"""
        prompt = self.prompts["extract_quotes"].format(transcript=text)
        result = self._call_llm(prompt)
        return result.get("quotes", [])
    
    def _call_llm(self, prompt: str) -> Dict:
        """
        Call LLM with structured output.
        
        Implementation uses Zo's native LLM calling capability.
        Returns parsed JSON response.
        """
        # Implementation details - uses anthropic client or zo bridge
        pass
```

---

## Prompt Templates

### `N5/prompts/extraction/extract_resources.md`

```markdown
You are analyzing a meeting transcript to identify resources that V (Vrijen) committed to sending.

## Transcript
{transcript}

## Available Content Library Items
{library_items}

## Task

1. Identify every instance where V commits to sending, sharing, or providing something:
   - Explicit: "I'll send you the link", "Here's the resource", "Let me share"
   - Implicit: "You should check out", "There's a great guide", "We have a demo"

2. For each commitment, try to match it to a Content Library item:
   - Match by title similarity
   - Match by topic/category
   - Match by URL if mentioned

3. Return structured JSON:

```json
{
  "resources": [
    {
      "commitment_text": "exact quote from transcript",
      "intent": "what V is offering to send",
      "matched_item_id": "content library ID or null",
      "matched_item_url": "URL if matched",
      "confidence": "high|medium|low",
      "reasoning": "why this match"
    }
  ]
}
```

Be generous in detecting commitments - it's better to catch more and filter later.
```

### `N5/prompts/extraction/extract_actions.md`

```markdown
You are analyzing a meeting transcript to extract action items.

## Transcript
{transcript}

## Task

Identify action items - things someone agreed to do:
- Look for: "I'll", "I will", "Let me", "I can", "We should", "Next step"
- Identify the owner (who will do it)
- Identify deadline if mentioned
- Identify what specifically needs to be done

Return structured JSON:

```json
{
  "action_items": [
    {
      "action": "specific task description",
      "owner": "person responsible",
      "deadline": "date/timeframe or null",
      "context": "relevant quote from transcript",
      "confidence": "high|medium|low"
    }
  ]
}
```
```

### `N5/prompts/extraction/extract_topics.md`

```markdown
You are analyzing a meeting transcript to identify discussion topics.

## Transcript
{transcript}

## Task

Identify the main topics discussed. Think about:
- Career/job search themes
- Startup/entrepreneurship themes  
- Product/technology themes
- Personal development themes
- Specific tools or services mentioned

Return structured JSON:

```json
{
  "topics": ["topic1", "topic2", ...],
  "primary_topic": "the main focus of the conversation",
  "topic_breakdown": [
    {"topic": "name", "time_percentage": 30, "key_points": ["point1", "point2"]}
  ]
}
```
```

---

## Integration with b_block_parser.py

### Before (hardcoded)
```python
def extract_explicit_resources(self, text: str) -> List[ResourceReference]:
    # 50+ lines of regex patterns
    tool_patterns = [
        (r'\b(YC|Y\s*Combinator)\s+(founder\s+)?match(ing)?\b', "YC Founder Match"),
        # ... more hardcoded patterns
    ]
```

### After (LLM-based)
```python
def extract_explicit_resources(self, text: str) -> List[ResourceReference]:
    # Get all Content Library items for matching context
    library_items = self.content_library.search(query=None, limit=200)
    library_summary = [
        {"id": i["id"], "title": i.get("title"), "url": i.get("url"), "type": i.get("item_type")}
        for i in library_items
    ]
    
    # LLM extraction
    extracted = self.llm_extractor.extract_resources(text, library_summary)
    
    # Convert to ResourceReference objects
    resources = []
    for item in extracted:
        if item.get("matched_item_id"):
            full_item = self.content_library.get(item["matched_item_id"])
            resources.append(ResourceReference(
                content=full_item.get("url") or full_item.get("content"),
                title=full_item.get("title"),
                url=full_item.get("url"),
                context=item.get("commitment_text"),
                confidence=item.get("confidence", "medium")
            ))
        else:
            resources.append(ResourceReference(
                content=item.get("intent"),
                context=item.get("commitment_text"),
                confidence="implicit"
            ))
    
    return resources
```

---

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create `N5/scripts/llm_extractor.py` 
2. Create prompt templates in `N5/prompts/extraction/`
3. Test extraction in isolation

### Phase 2: Integrate with b_block_parser.py
1. Replace `extract_explicit_resources()` 
2. Replace `suggest_relevant_resources()`
3. Replace `extract_action_items()`
4. Replace `extract_decisions()`

### Phase 3: Audit & Replace Remaining
1. Scan all meeting scripts for hardcoded patterns
2. Replace with LLM calls
3. Validate end-to-end

---

## Cost Consideration

LLM calls cost tokens. Mitigation:
- Use efficient prompts (minimize input tokens)
- Cache results per transcript
- Use lighter model for simple extractions (e.g., haiku for topics)
- Batch extractions in single call where possible

---

*Designed by Vibe Architect | 2025-12-02*

