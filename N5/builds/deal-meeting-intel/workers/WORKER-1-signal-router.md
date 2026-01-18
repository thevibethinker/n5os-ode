---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_GCktM2iwLZIi5cHK
worker_id: 1
title: Signal Router Core
estimated_time: 3 hours
dependencies: []
---

# Worker 1: Signal Router Core

## Objective

Build the central intelligence router that:
1. Receives signals from any channel (meeting, email, SMS, Kondo)
2. Uses LLM to match signals to existing deals
3. Uses LLM to extract structured intelligence
4. Routes to appropriate update handler

## Deliverables

- [ ] `N5/scripts/deal_signal_router.py` — main orchestrator
- [ ] `N5/scripts/deal_llm_prompts.py` — centralized prompt templates
- [ ] `N5/config/deal_signal_config.json` — configurable thresholds
- [ ] Unit tests for matching and extraction

## Implementation Details

### 1. Deal Matcher (LLM-powered)

```python
def match_deal(query: str, context: str = "") -> Optional[DealMatch]:
    """
    Fuzzy match a query to an existing deal.
    
    Args:
        query: User input (e.g., "darwinbox", "Christine", "Aviato")
        context: Optional context (e.g., "careerspan" or "zo")
    
    Returns:
        DealMatch with deal_id, confidence, pipeline
    """
```

**LLM Prompt:**
```
You are matching a user query to a deal in our CRM.

Query: "{query}"
Context: "{context}"

Available deals:
{deal_list_formatted}

Available contacts:
{contact_list_formatted}

Instructions:
1. Find the best match considering: exact matches, partial names, contact names, common abbreviations
2. If query could match both zo and careerspan pipelines, prefer the one mentioned in context
3. Return confidence 0-100

Return JSON:
{{
  "deal_id": "string or null",
  "contact_id": "string or null", 
  "confidence": 0-100,
  "match_reason": "why this matched"
}}
```

### 2. Signal Extractor (LLM-powered)

```python
def extract_signal(text: str, deal_context: dict) -> SignalExtraction:
    """
    Extract structured intelligence from unstructured text.
    
    Args:
        text: The update text (SMS, email excerpt, meeting note)
        deal_context: Current deal state (stage, last_touch, etc.)
    
    Returns:
        SignalExtraction with stage_signal, key_facts, next_action, etc.
    """
```

**LLM Prompt:**
```
Extract deal intelligence from this update.

Update text: "{text}"

Current deal state:
- Company: {company}
- Current stage: {stage}
- Last touch: {last_touch}
- Pipeline: {pipeline}

Stage definitions:
- identified: Target recognized, not researched
- researched: Intel gathered, warm intro found
- outreach: First touch sent
- engaged: Response received, conversation open
- qualified: Confirmed mutual interest + fit
- negotiating: Terms being discussed
- closed_won: Deal completed
- closed_lost: Deal dead or declined

Return JSON:
{{
  "stage_signal": "none|positive|negative|stage_change",
  "inferred_stage": "stage_name or null if no change",
  "stage_change_reason": "why stage should change",
  "key_facts": ["fact1", "fact2"],
  "next_action": "string or null",
  "next_action_date": "YYYY-MM-DD or null",
  "sentiment": "positive|neutral|negative",
  "urgency": "low|medium|high"
}}
```

### 3. Router Logic

```python
class DealSignalRouter:
    def __init__(self):
        self.db = DealDatabase()
        self.notion_sync = NotionSync()
        
    def process_signal(self, source: str, content: str, metadata: dict) -> ProcessResult:
        """
        Main entry point for all signals.
        
        Args:
            source: "sms" | "email" | "meeting" | "kondo"
            content: The text content
            metadata: Source-specific metadata (email_id, meeting_folder, etc.)
        """
        # 1. Match to deal
        match = self.match_deal(content)
        
        if not match or match.confidence < 70:
            return self.handle_unknown_signal(content, metadata)
        
        # 2. Extract intelligence
        deal = self.db.get_deal(match.deal_id)
        signal = self.extract_signal(content, deal)
        
        # 3. Update local
        self.db.update_deal(match.deal_id, signal)
        self.db.log_activity(match.deal_id, source, content)
        
        # 4. Sync to Notion
        self.notion_sync.append_intelligence(match.deal_id, signal)
        
        return ProcessResult(success=True, deal=deal, signal=signal)
```

## Testing

```bash
# Test deal matching
python3 -c "
from deal_signal_router import DealSignalRouter
router = DealSignalRouter()
print(router.match_deal('darwinbox'))  # Should match cs-acq-darwinbox
print(router.match_deal('Christine'))   # Should match via contact
print(router.match_deal('aviato'))      # Should match zo-dp-aviato
"

# Test signal extraction
python3 -c "
from deal_signal_router import DealSignalRouter
router = DealSignalRouter()
signal = router.extract_signal(
    'They are ready to move forward, setting up call next week',
    {'stage': 'qualified', 'company': 'Darwinbox'}
)
print(signal)  # Should infer stage_change to negotiating
"
```

## Success Criteria

- [ ] Can match deals with >90% accuracy on test set
- [ ] Can extract stage changes correctly
- [ ] Can handle typos and partial names
- [ ] Processing time <2s per signal
- [ ] Graceful fallback when LLM unavailable
