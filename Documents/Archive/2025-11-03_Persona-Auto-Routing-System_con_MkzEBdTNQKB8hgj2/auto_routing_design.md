# Automatic Persona Routing System - Design

**Version:** 1.0  
**Date:** 2025-11-03  
**Status:** Design → Implementation  
**Decisions:** V-approved

## Requirements (V-Specified)

1. **Method:** LLM-based routing (Option A)
2. **Interim:** Manual routing acceptable during build
3. **Detection:** Automatic (no keywords required)
4. **Switchback:** Auto-return to Operator after work complete
5. **Threshold:** Switch only if ≥80% confidence

## Architecture

### Components

**1. Persona Domain Extractor**
- Reads all personas via `list_personas` API
- Extracts `when_to_invoke` patterns from each
- Builds routing knowledge base
- Output: JSON mapping persona_id → {domains, use_cases, anti_patterns}

**2. Request Classifier (LLM)**
- Input: User message + persona domain map
- Process: Analyze request against all persona domains
- Output: Ranked list of (persona_id, confidence_score, reasoning)

**3. Routing Decision Engine**
- Input: Classification results + current persona
- Logic: 
  - If top score ≥80% AND different from current → SWITCH
  - If top score <80% → STAY (default to Operator)
  - If already in target persona → CONTINUE
- Output: (should_switch: bool, target_persona_id, confidence)

**4. Switchback Protocol**
- Trigger: Specialized persona completes work
- Action: Call `set_active_persona(operator_id)` 
- Already exists in conditional rules ✓

### System Integration Points

**Current limitation:** No pre-flight hook in Zo message pipeline.

**Two implementation paths:**

#### Path A: Manual-Assisted (Interim - Deployable Now)
- Operator disciplines: Call router before responding to ambiguous requests
- Router recommends persona switch
- Operator executes switch manually
- **Pros:** Can deploy immediately
- **Cons:** Still requires Operator judgment

#### Path B: System-Level (Long-term - Requires Zo Changes)
- Add pre-flight routing hook to Zo conversation handler
- Hook calls router before persona generates response
- Automatic execution of switch if threshold met
- **Pros:** True automation
- **Cons:** Requires platform changes outside our control

**Decision:** Build Path A now, design Path B for future integration.

## Implementation Plan

### Phase 1: Core Router (This Session)

**Files to create:**
1. `N5/scripts/persona_router.py` - Core routing logic
2. `N5/prefs/protocols/persona_routing_protocol.md` - Usage guide
3. `N5/data/persona_domains.json` - Cached domain extraction
4. Unit tests

**Functions:**
```python
# persona_router.py

def extract_persona_domains() -> dict:
    """Call list_personas API, parse when_to_invoke fields"""
    
def classify_request(message: str, personas: dict) -> list[tuple]:
    """LLM analysis: message → [(persona_id, confidence, reasoning)]"""
    
def should_switch(classification: list, current_persona_id: str, threshold: float = 0.80) -> dict:
    """Decision logic with threshold"""
    
def route_request(message: str, current_persona_id: str) -> dict:
    """Main entry point: message → routing decision"""
```

**CLI interface:**
```bash
# Analyze request and recommend routing
python3 N5/scripts/persona_router.py analyze "How do I build a REST API?"

# Output:
# {
#   "should_switch": true,
#   "target_persona": "builder",
#   "target_id": "abc-123",
#   "confidence": 0.92,
#   "reasoning": "Request involves system building...",
#   "current_persona": "operator"
# }
```

### Phase 2: Operator Integration (This Session)

**Add to Operator persona:**
- Pre-flight check: Call router for non-trivial requests
- Execution: If router recommends switch, execute it
- Report: Tell user about switch and why

**Protocol:**
```
1. Receive user message
2. Quick assessment: Trivial (answer directly) or Complex (route)
3. If complex: Call persona_router.py
4. If confidence ≥80%: Switch persona + report
5. If confidence <80%: Continue as Operator
```

### Phase 3: Testing & Refinement (Next Session)

**Test cases:**
- "What's the capital of France?" → Operator (trivial, no switch)
- "Research the top 5 project management tools" → Researcher (≥80%)
- "How do I use async/await in Python?" → Teacher (≥80%)
- "Should we pivot to B2B or B2C?" → Strategist (≥80%)
- "Build me a task tracker" → Builder (≥80%)
- "Fix this bug in my code" → Debugger (≥80%)

**Metrics:**
- Routing accuracy (correct persona chosen)
- False positive rate (wrong switches)
- False negative rate (missed switches)
- Latency impact

### Phase 4: System Integration Design (Future)

**Specification for Zo team:**

```typescript
// Proposed pre-flight hook in Zo conversation handler

interface PersonaRouter {
  analyzeRequest(message: string, currentPersona: string): Promise<RoutingDecision>;
}

interface RoutingDecision {
  shouldSwitch: boolean;
  targetPersonaId?: string;
  confidence: number;
  reasoning: string;
}

// In message handler:
async function handleUserMessage(message: string, conversationId: string) {
  const currentPersona = getActivePersona(conversationId);
  const routing = await personaRouter.analyzeRequest(message, currentPersona);
  
  if (routing.shouldSwitch && routing.confidence >= 0.80) {
    await setActivePersona(conversationId, routing.targetPersonaId);
    logRoutingDecision(routing);
  }
  
  // Continue with normal response generation
  return generateResponse(message, conversationId);
}
```

## Persona Domain Mapping (Initial)

Based on current personas:

| Persona | Primary Domain | Trigger Patterns |
|---------|---------------|------------------|
| Operator | General coordination, execution mechanics | Default, unclear requests |
| Researcher | Information gathering, synthesis | "research", "find", "what does X do", "compare" |
| Strategist | Strategy, frameworks, decisions | "should we", "strategy", "framework", "analyze patterns" |
| Teacher | Explaining concepts, teaching | "how does X work", "explain", "teach me", "what is" |
| Builder | System implementation | "build", "implement", "create system", "deploy" |
| Architect | System design, persona design | "design", "architecture", "create persona" |
| Writer | Content creation | "write", "draft", "post", "article" |
| Debugger | Problem diagnosis | "bug", "error", "not working", "debug" |

## Edge Cases

**1. Multi-domain requests**
- "Research and write about X" → Research first, Writer second
- Solution: Route to first domain, let persona route onward

**2. Ambiguous requests**
- "Tell me about async programming" → Teacher OR Researcher?
- Solution: If confidence <80%, stay with Operator

**3. Rapid context switching**
- User jumps between topics quickly
- Solution: Allow switches, trust threshold to prevent thrashing

**4. Override mechanism**
- User wants to force specific persona
- Solution: Add @persona mentions (future enhancement)

## Success Metrics

**Short-term (Manual-assisted):**
- Operator successfully uses router for 90%+ of routing decisions
- Routing recommendations accepted 80%+ of time
- User satisfaction with persona selection

**Long-term (Automated):**
- 85%+ routing accuracy
- <5% false positive rate
- <500ms latency overhead
- User override rate <10%

## Rollout Plan

1. **Build Phase** (This session)
   - Implement persona_router.py
   - Create protocol document
   - Unit test with example requests

2. **Manual Testing** (Next few conversations)
   - Operator uses router manually
   - Collect routing decisions + outcomes
   - Refine classification logic

3. **Operator Integration** (After validation)
   - Add router discipline to Operator persona
   - Make routing automatic for Operator

4. **System Integration** (Future, requires Zo changes)
   - Provide specification to Zo team
   - True pre-flight automation

## Principles Applied

- **P28 (Plan DNA):** Design quality determines implementation success
- **P21 (Document Assumptions):** Explicit confidence threshold, edge case handling
- **P8 (Minimal Context):** Router loads only persona domains, not full prompts
- **P12 (Testing Fresh Threads):** Will test in new conversations
- **P15 (Complete Before Claiming):** Clear phases, no premature "done"

## Open Questions

1. Should router consider conversation history or just current message?
2. How to handle multi-turn persona workflows (research → strategy → build)?
3. Should certain personas have "stickiness" (harder to switch away from)?
4. What telemetry to collect for continuous improvement?

## Next Action

Build `persona_router.py` with core routing logic.
