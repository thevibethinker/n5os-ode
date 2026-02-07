---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
---

# Worker 1: LLM Extraction Layer Integration

**Orchestrator:** con_jYGYNfcv76UTmolk  
**Persona:** Vibe Builder  
**Priority:** High  
**Estimated Effort:** 45-60 min

---

## Context

We built an LLM extraction service to replace hardcoded regex/keyword patterns with flexible LLM reasoning. The service and prompts are complete. This worker integrates them into the meeting processing pipeline.

### Key Principle
> "Wherever you need flexible reasoning, use a prompt and an LLM call."

---

## Files to Read First

1. `file 'N5/prefs/architecture/llm-extraction-layer.md'` — Architecture spec
2. `file 'N5/scripts/llm_extractor.py'` — The new extraction service
3. `file 'N5/prompts/extraction/'` — 5 prompt templates (resources, actions, decisions, topics, quotes)
4. `file 'N5/scripts/b_block_parser.py'` — Primary target for refactor

---

## Deliverables

### 1. Update b_block_parser.py

**Current state:** Uses hardcoded regex patterns:
```python
# Lines ~190-250: suggest_relevant_resources()
tool_patterns = [
    (r'\b(YC|Y\s*Combinator)\b.*\b(founder|match)', "YC Founder Match"),
    (r'\b(calendly|schedule|book)\b', "calendly"),
    ...
]
```

**Target state:** Use LLMExtractor:
```python
from llm_extractor import LLMExtractor

class BBlockParser:
    def __init__(self, meeting_folder: Path):
        ...
        self.llm_extractor = LLMExtractor()
    
    def suggest_relevant_resources(self, transcript: str) -> List[ResourceReference]:
        # Get library items for matching
        library_items = self.content_library.search(query=None, limit=200)
        
        # Use LLM extraction
        result = self.llm_extractor.extract_resources(transcript, library_items)
        
        # Convert to ResourceReference objects
        resources = []
        for r in result.get("resources", []):
            resources.append(ResourceReference(
                title=r.get("title"),
                url=r.get("url"),
                content_library_id=r.get("library_id"),
                confidence=r.get("confidence", "explicit"),
            ))
        
        # Also capture unmatched commitments for V to review
        self.unmatched_commitments = result.get("unmatched_commitments", [])
        
        return resources
```

### 2. Update extract_action_items() method

Replace hardcoded action detection with:
```python
def extract_action_items(self, transcript: str) -> Dict[str, List]:
    result = self.llm_extractor.extract_action_items(transcript)
    return {
        "v_actions": result.get("v_actions", []),
        "other_actions": result.get("other_actions", []),
        "all_actions": result.get("action_items", []),
    }
```

### 3. Update topic detection

Replace hardcoded topic keywords with:
```python
def detect_topics(self, transcript: str) -> Dict[str, Any]:
    return self.llm_extractor.extract_topics(transcript)
```

### 4. Add quotable moments extraction

New method:
```python
def extract_quotes(self, transcript: str) -> List[Dict]:
    result = self.llm_extractor.extract_quotable_moments(transcript)
    return result.get("quotes", [])
```

### 5. Update parse_transcript() to use new methods

The main `parse_transcript()` method should call the new LLM-based methods.

---

## Testing

After implementation, test with a real transcript:

```bash
# Find a recent meeting with transcript
ls /home/workspace/Personal/Meetings/ | tail -5

# Run parser on it
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from b_block_parser import BBlockParser
from pathlib import Path

folder = Path('/home/workspace/Personal/Meetings/2025-11-12_ColinNavon_VrijenAttawar_[P]')
parser = BBlockParser(folder)
result = parser.parse_transcript()

print('Resources:', len(result.get('resources_suggested', [])))
for r in result.get('resources_suggested', [])[:5]:
    print(f'  - {r.title}: {r.url}')

print('Actions:', len(result.get('action_items', {}).get('v_actions', [])))
"
```

---

## Validation Checklist

- [ ] LLMExtractor imports successfully in b_block_parser.py
- [ ] suggest_relevant_resources() uses LLM instead of regex
- [ ] extract_action_items() uses LLM instead of regex
- [ ] detect_topics() uses LLM instead of hardcoded keywords
- [ ] extract_quotes() is new and working
- [ ] parse_transcript() returns enriched data
- [ ] Test with real transcript passes
- [ ] No regressions in email_composer.py integration

---

## Notes

- The LLMExtractor uses Claude Sonnet by default (fast + capable)
- Prompts are in `N5/prompts/extraction/` — edit these to tune extraction quality
- If API errors occur, the extractor returns empty results (graceful degradation)
- Consider caching extraction results to avoid re-running on same transcript

---

**Report completion to:** con_jYGYNfcv76UTmolk  
**Created:** 2025-12-02 00:18 ET

