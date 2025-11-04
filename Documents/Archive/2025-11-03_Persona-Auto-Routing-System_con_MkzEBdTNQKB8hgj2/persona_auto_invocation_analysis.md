# Persona Auto-Invocation Debug Analysis

**Date:** 2025-11-03  
**Issue:** Researcher, Strategist, Teacher personas not auto-invoking  
**Reporter:** V

## Problem Statement

Three specialized personas (Vibe Researcher, Vibe Strategist, Vibe Teacher) exist but don't get invoked automatically when their domains are triggered. V expects automatic switching when situations arise that match these personas' domains.

## Root Cause

**Manual routing ≠ Auto-invocation**

The persona system has:
- ✅ `routing_protocol` sections (manual guidance for other personas to route TO them)
- ✅ `when_to_invoke` sections (documentation of use cases)
- ❌ **No automatic trigger logic** - no code/system that reads these fields and switches personas

## Current State

### What EXISTS:
1. **9 personas registered** in Zo system (checked via `list_personas`)
2. Each persona has structured fields:
   - `routing_protocol` (where OTHER personas should route TO this one)
   - `when_to_invoke` (documented use cases)
   - `dont` (anti-patterns to avoid)

### What's MISSING:
1. **No trigger detection system** - nothing reads `when_to_invoke` patterns and activates persona
2. **No automatic switching logic** - no code that calls `set_active_persona` based on context
3. **No rule engine** - no system parsing conversation context and matching to persona domains

## Evidence

From persona definitions:

**Vibe Researcher (id: d0f04503-3ab4-447f-ba24-e02611993d90):**
```yaml
when_to_invoke:
  use: [Market research, Competitive intel, Literature review, Fact-finding, Synthesis, Exploring new domains]
  dont: [Strategic analysis→Strategist, Building tools→Builder, ...]
```

**Vibe Strategist (id: 39309f92-3f9e-448e-81e2-f23eef5c873c):**
```yaml
when_to_invoke:
  use: Strategic decisions, pattern extraction, option generation, framework building, analyzing qualitative data, stress-testing ideas
  dont: System building → Builder | Persona design → Architect | ...
```

**Vibe Teacher (id: 88d70597-80f3-4b3e-90c1-da2c99da7f1f):**
```yaml
when_to_invoke:
  use: Explaining technical concepts, teaching new skills, clarifying how systems work, technical documentation, learning facilitation
  dont: Building systems → Builder | Strategy work → Strategist | ...
```

## Current Behavior

**Operator (current active persona) must manually decide to route:**
- Operator reads request
- Determines which persona fits
- Explicitly calls `set_active_persona` with target persona ID
- **This is manual orchestration, not automatic invocation**

## Expected Behavior (V's Intent)

**Automatic context-based switching:**
1. V asks research question → System detects research domain → Auto-switches to Researcher
2. V asks for strategic analysis → System detects strategy domain → Auto-switches to Strategist
3. V asks to explain technical concept → System detects teaching domain → Auto-switches to Teacher

## Gap Analysis

### What would enable auto-invocation:

**Option A: LLM-based routing (pre-flight check)**
- Before each response, analyze request text
- Match against all `when_to_invoke` patterns
- If match confidence >70%, auto-switch persona
- Pros: Flexible, uses existing persona metadata
- Cons: Adds latency, token cost, potential mis-routing

**Option B: Rule-based trigger system**
- Define regex/keyword patterns for each persona
- Store in `N5/prefs/personas/triggers.json`
- Simple pattern matching before response
- Pros: Fast, deterministic
- Cons: Less flexible, requires maintenance

**Option C: Hybrid approach**
- Fast keyword pre-filter (rule-based)
- If ambiguous, LLM classification
- Switch only if high confidence
- Pros: Balance speed + accuracy
- Cons: More complex implementation

### Implementation Requirements

**Minimal viable auto-invocation:**
1. **Trigger database** - Map patterns → persona IDs
2. **Pre-response hook** - Analyze incoming message
3. **Confidence threshold** - Only switch if >80% match
4. **Manual override** - V can force persona with @mention
5. **Switchback protocol** - After task complete, return to Operator

## Principle Violations

**P15 (Complete Before Claiming):** Personas were delivered as "complete" but auto-invocation was implied but never built.

**P21 (Document Assumptions):** Assumption that `when_to_invoke` fields would enable automatic switching was never documented or validated.

**P28 (Plan DNA):** Design spec didn't explicitly address how invocation would work (manual vs automatic).

## Recommendations

### Short-term (Manual orchestration enhancement):
1. Add explicit routing guidance to Operator persona
2. Create quick-reference table of persona IDs + domains
3. Document current manual routing process clearly

### Medium-term (Rule-based triggers):
1. Extract `when_to_invoke` patterns from personas
2. Build simple keyword/regex trigger system
3. Add to Operator pre-flight check
4. Test with Researcher/Strategist/Teacher first

### Long-term (LLM-powered auto-routing):
1. Design classifier that reads all persona `when_to_invoke` sections
2. Build confidence scoring system
3. Implement switchback protocol (auto-return to Operator)
4. Add routing telemetry for continuous improvement

## Next Steps

**Immediate:**
1. Confirm with V: Manual orchestration acceptable short-term?
2. If yes → Enhance Operator routing guidance
3. If no → Prioritize trigger system build

**Design Questions for V:**
1. Acceptable to have manual routing in interim?
2. Preferred invocation method: keyword (@research), automatic detection, or hybrid?
3. Should personas auto-switch back to Operator after completing work?
4. What confidence threshold for auto-switching (suggest 80%)?

## Files Referenced
- Persona definitions: Retrieved via `list_personas` tool
- Orchestration pattern: file 'N5/prefs/principles/P36_orchestration_pattern.yaml'
- Task routing (example): file 'N5/prefs/protocols/task_routing_protocol.md'

## Status
**Diagnosis:** COMPLETE  
**Root Cause:** Confirmed - auto-invocation never implemented  
**Fix:** Design options documented, awaiting V input on preferred approach
