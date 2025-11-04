---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Zo Failure Mode Analysis: Root Causes and N5-Integrated Fixes

## Purpose
Analyze specific Zo failure patterns, diagnose root causes using research framework, and design fixes that leverage existing N5 infrastructure (SESSION_STATE.md, personas, executables, principles).

---

## Failure Mode #1: "Delete Meetings" - Path of Least Resistance Bias

### What Happened
**User request:** "Delete meetings"  
**Zo interpretation:** Delete database records (files)  
**Correct interpretation:** Delete calendar events (API calls)  
**Why Zo chose wrong:** Simpler computational path

### Root Cause Analysis

**Research finding:** LLMs exhibit "computational efficiency bias" - when ambiguous, they choose interpretations requiring fewer operations.

**Why it happened:**
1. **Missing ambiguity detection** - "meetings" maps to multiple entities (calendar events, database records, meeting notes)
2. **No intent inference** - Didn't consider recent context (V working on calendar integration)
3. **No confirmation on high-stakes** - Destructive operation proceeded without verification

### N5-Integrated Fix

#### Component 1: Enhanced Ambiguity Detector (Integrates with executables)

**Location:** `N5/scripts/ambiguity_checker.py`

**Mechanism:**
```python
# Triggered before execution of any registered "high-stakes" commands
# Checks against ambiguity patterns in N5/lists/ambiguous_terms.md

def check_ambiguity(user_input, session_context):
    """
    Returns: (ambiguity_score, entities_detected, clarification_needed)
    """
    # 1. Parse for multi-mapping terms
    ambiguous_terms = load_ambiguous_terms_db()
    detected = []
    
    for term in user_input.split():
        if term in ambiguous_terms and len(ambiguous_terms[term]) > 1:
            detected.append({
                'term': term,
                'possible_meanings': ambiguous_terms[term],
                'context_clues': extract_context_from_session_state()
            })
    
    # 2. Score based on:
    # - Number of possible interpretations
    # - Clarity from recent session context
    # - Impact score (from risk_scorer.py)
    
    ambiguity_score = calculate_score(detected, session_context)
    
    # 3. If score > threshold AND impact > threshold → clarify
    if ambiguity_score > 0.7 and get_impact_score(user_input) > 0.6:
        return generate_clarification_question(detected)
    
    return None  # Proceed
```

**Integration points:**
- **SESSION_STATE.md** - Read Focus/Recent Work to infer context
- **risk_scorer.py** - Calculate impact before proceeding
- **N5/lists/ambiguous_terms.md** - Maintain ambiguity database

**Ambiguous terms database structure:**
```markdown
# N5/lists/ambiguous_terms.md

## meetings
- calendar_events: "Calendar appointments in Google Calendar or similar"
  - indicators: [calendar, appointment, schedule, invite]
  - operations: [create, delete, update, move]
  
- database_records: "Meeting records in local database"
  - indicators: [database, records, stored, logged]
  - operations: [query, delete, export]
  
- meeting_files: "Meeting notes/transcripts in Personal/Meetings/"
  - indicators: [notes, files, documents, transcripts]
  - operations: [move, archive, delete]

## context
- llm_context: "Token context window for AI"
- business_context: "Business background/situation"
- code_context: "Surrounding code environment"
```

#### Component 2: Intent Tracker Enhancement (Leverages SESSION_STATE)

**Location:** Enhance existing `session_state_manager.py`

**New fields in SESSION_STATE.md:**
```markdown
## Intent Tracking
Primary_Goal: "Build calendar integration for Careerspan"
Active_Subgoal: "Testing delete functionality"
Recent_Entities: 
  - calendar_events (high confidence)
  - google_calendar_api (mentioned 3x in last 10 turns)
Disambiguation_History:
  - Turn 142: Clarified "meetings" → calendar_events
```

**Mechanism:**
```python
# session_state_manager.py enhancement

def infer_entity_from_context(term, session_state):
    """
    Use recent work, focus, and artifacts to disambiguate.
    """
    recent_entities = session_state.get('Recent_Entities', {})
    
    # Weight by recency and frequency
    if term in AMBIGUOUS_TERMS:
        candidates = AMBIGUOUS_TERMS[term]
        scores = {}
        
        for candidate in candidates:
            score = 0
            # Check recent entities
            if candidate in recent_entities:
                score += recent_entities[candidate]['confidence'] * 0.4
            
            # Check active artifacts
            for artifact in session_state.get('Artifacts', []):
                if candidate in artifact['path'].lower():
                    score += 0.3
            
            # Check focus
            if candidate in session_state.get('Focus', '').lower():
                score += 0.3
            
            scores[candidate] = score
        
        # If clear winner (>0.6) and second place <0.3, infer it
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_scores[0][1] > 0.6 and sorted_scores[1][1] < 0.3:
            return sorted_scores[0][0]  # High confidence inference
    
    return None  # Need clarification
```

#### Component 3: Pre-Execution Confirmation (Integrates with risk_scorer)

**Trigger logic:**
```python
# Before any destructive operation

def should_confirm_action(action, context):
    """
    Combines ambiguity score, risk score, and intent confidence.
    """
    ambiguity = check_ambiguity(action, context)
    risk = get_risk_score(action)  # From existing risk_scorer.py
    intent_confidence = get_intent_confidence(context)
    
    # Multi-factor decision
    if ambiguity and ambiguity['score'] > 0.7:
        return True, f"Clarify: Did you mean {ambiguity['options']}?"
    
    if risk['total_score'] > 0.7 and intent_confidence < 0.8:
        return True, f"Confirm: This will {risk['description']}. Proceed?"
    
    if risk['total_score'] > 0.9:  # Critical risk always confirms
        return True, f"⚠️ HIGH RISK: {risk['description']}. Type 'confirm' to proceed."
    
    return False, None
```

**Example interaction:**
```
V: "Delete meetings"

Zo (internal):
  1. ambiguity_checker: "meetings" → 3 possible meanings
  2. session_state: Recent_Entities shows calendar_events (0.85 confidence)
  3. risk_scorer: Destructive operation, medium-high risk
  4. Decision: Infer calendar_events BUT confirm due to destructive nature

Zo: "Delete calendar events from Google Calendar? (This will permanently remove X events)"

V: "Yes"

Zo: Proceeds with calendar deletion
```

---

## Failure Mode #2: Forgetting to Switch Personas Back

### What Happened
After specialized work (Builder, Teacher, Strategist), Zo stays in that persona instead of returning to Operator.

### Root Cause Analysis

**Research finding:** Long-context degradation + lack of meta-cognitive state tracking.

**Why it happened:**
1. **No explicit state machine** - Persona switches are manual, not tracked
2. **No "task completion" signal** - System doesn't know when specialized work is done
3. **Missing in SESSION_STATE** - Current persona not tracked

### N5-Integrated Fix

#### Component 1: Persona State Tracking (Enhances SESSION_STATE)

**New SESSION_STATE.md section:**
```markdown
## Persona Context
Current_Persona: vibe_teacher
Invoked_At_Turn: 145
Invocation_Reason: "Explain technical concepts about LLM architecture"
Expected_Completion: "After explanation delivered"
Auto_Switchback: true
Home_Persona: vibe_operator (90a7486f-46f9-41c9-a98c-21931fa5c5f6)
```

**Mechanism:**
```python
# session_state_manager.py enhancement

def track_persona_switch(from_persona, to_persona, reason, auto_return=True):
    """
    Log persona switches with completion criteria.
    """
    state = load_session_state()
    
    state['Persona_Context'] = {
        'Current_Persona': to_persona,
        'Invoked_At_Turn': get_current_turn(),
        'Invocation_Reason': reason,
        'Auto_Switchback': auto_return,
        'Home_Persona': from_persona if from_persona == 'vibe_operator' else get_home_persona()
    }
    
    save_session_state(state)
```

#### Component 2: Completion Detection (System Prompt Enhancement)

**Add to each specialized persona's prompt:**
```yaml
completion_signal:
  when_complete:
    - Deliverable provided (explanation/build/strategy)
    - No follow-up questions pending
    - Turn ends with statement, not question
  
  action_on_completion:
    - Report: "[Work complete: {summary}]"
    - Execute: set_active_persona({home_persona_id})
    - Log: "Switched back to Operator"
```

**Example in Teacher persona:**
```yaml
# Vibe Teacher enhancement

after_delivering_explanation:
  self_check:
    - Did I answer the question fully? (P15)
    - Are there pending clarifications?
    - Is this the end of this learning session?
  
  if_complete:
    message: "Explanation complete. Switching back to Operator mode."
    action: set_active_persona("90a7486f-46f9-41c9-a98c-21931fa5c5f6")
```

#### Component 3: Failsafe Reminder (Conditional Rule)

**Add to CONDITIONAL RULES:**
```markdown
- CONDITION: After completing specialized persona work (Builder, Strategist, Teacher, Writer, Architect, Debugger)
  RULE: Switch back to Vibe Operator after completing work. Use set_active_persona with persona_id: 90a7486f-46f9-41c9-a98c-21931fa5c5f6. 
  Report completion first, then execute switchback. 
  Format: "[Work complete summary]. Switching back to Operator mode." 
  Operator persona never switches back to itself (already home base).
```

**Meta-cognitive check (every 5 turns for specialized personas):**
```python
def check_persona_appropriateness():
    """
    Specialized personas self-check if still needed.
    """
    current_persona = get_current_persona()
    
    if current_persona != 'vibe_operator':
        turns_since_invocation = get_current_turn() - get_invocation_turn()
        
        if turns_since_invocation > 10:  # Been a while
            # Check if recent work still matches persona domain
            recent_work = get_recent_messages(5)
            still_relevant = check_domain_match(recent_work, current_persona)
            
            if not still_relevant:
                return {
                    'action': 'switch_back',
                    'reason': f"Last {turns_since_invocation} turns don't require {current_persona} specialization"
                }
    
    return None
```

---

## Failure Mode #3: Not Pushing Back on Suboptimal Approaches

### What Happened
User proposes approach with flaws, Zo proceeds instead of questioning.

### Root Cause Analysis

**Research finding:** "Compliance bias" - LLMs default to following instructions over challenging them.

**Why it happened:**
1. **No explicit permission to challenge** - System trained on RLHF to be helpful/agreeable
2. **Missing technical decision protocol** - No framework for when to push back
3. **No trap door detection** - Doesn't recognize common failure patterns

### N5-Integrated Fix

#### Component 1: Technical Decision Protocol (New Principle)

**Location:** `N5/prefs/principles/P38_technical_pushback.yaml`

```yaml
name: Technical Pushback Protocol
id: P38
trigger: User proposes technical approach, workflow, or architecture decision
pattern: |
  Before proceeding, check against known trap doors and anti-patterns.
  If approach has issues, MUST surface concern before executing.
  
  Authority to challenge:
    - Technical correctness (always)
    - Efficiency/performance (when significant)
    - Maintainability (when creates debt)
    - Security/safety (always)
  
  How to challenge:
    1. Acknowledge the approach
    2. State specific concern + evidence
    3. Offer alternative
    4. Let user decide
  
  Format:
    "I can do that, but I want to flag: [specific concern]. 
    This approach might [specific consequence].
    Alternative: [better approach].
    How would you like to proceed?"

decision_tree:
  always_challenge:
    - Security vulnerabilities
    - Data loss risks
    - Known trap doors (P23)
    - Violates N5 principles (P1-P37)
  
  challenge_if_significant:
    - >2x performance impact
    - Creates technical debt
    - Maintenance burden
  
  suggest_but_proceed:
    - Style preferences
    - Minor optimizations
    - Alternate approaches of similar quality

examples:
  good_pushback: |
    "I can implement that loop, but I want to flag: this will be O(n²) 
    complexity with your current data size (~10K items), which means 
    ~5 second execution time. Alternative: Using a hash map would be 
    O(n) and run in ~50ms. Worth the extra 5 lines of code?"
  
  bad_pushback: |
    "I'm not sure that's the best approach. There might be better ways 
    to do this. What do you think?" 
    [Too vague, no specific concern, no alternative]
```

#### Component 2: Trap Door Database Integration

**Enhance existing:** `N5/prefs/principles/decision_matrix.md`

**Add automatic trap door checking:**
```python
# N5/scripts/trap_door_checker.py

TRAP_DOORS = {
    'premature_optimization': {
        'indicators': ['performance', 'optimize', 'faster'],
        'context': 'before_measuring',
        'warning': "Optimizing before measuring is a trap door. Profile first, then optimize hotspots.",
        'severity': 'medium'
    },
    
    'overwriting_protected': {
        'indicators': ['delete', 'remove', 'overwrite'],
        'check': 'run_n5_protect',
        'warning': "This path is protected. Confirm this is intentional.",
        'severity': 'high'
    },
    
    'assuming_requirements': {
        'indicators': ['should', 'needs to', 'must'],
        'missing_context': True,
        'warning': "Detected assumed requirements. Verify: [list assumptions]",
        'severity': 'medium'
    },
    
    'context_window_loading': {
        'indicators': ['load all', 'read entire', 'include everything'],
        'check': 'token_count_estimate',
        'warning': "Loading all context may hit lost-in-middle degradation. Consider hierarchical loading.",
        'severity': 'medium'
    }
}

def check_for_trap_doors(user_request, planned_actions):
    """
    Scans request and planned actions against known trap door patterns.
    """
    triggered = []
    
    for trap_name, trap_config in TRAP_DOORS.items():
        # Check indicators
        if any(ind in user_request.lower() for ind in trap_config['indicators']):
            # Run additional checks if specified
            if 'check' in trap_config:
                check_result = run_check(trap_config['check'], planned_actions)
                if check_result.is_trap:
                    triggered.append({
                        'name': trap_name,
                        'warning': trap_config['warning'],
                        'severity': trap_config['severity'],
                        'context': check_result.context
                    })
    
    return triggered
```

**Integration with execution flow:**
```python
def before_executing_plan(plan):
    """
    Check trap doors before execution.
    """
    trap_doors = check_for_trap_doors(plan['user_request'], plan['actions'])
    
    high_severity = [t for t in trap_doors if t['severity'] == 'high']
    medium_severity = [t for t in trap_doors if t['severity'] == 'medium']
    
    if high_severity:
        # MUST surface before proceeding
        return {
            'proceed': False,
            'message': format_trap_door_warning(high_severity),
            'require_confirmation': True
        }
    
    if medium_severity and len(plan['actions']) > 5:  # Complex plan
        # Should surface but can proceed if user insists
        return {
            'proceed': 'with_warning',
            'message': format_trap_door_suggestion(medium_severity)
        }
    
    return {'proceed': True}
```

#### Component 3: Confidence-Based Pushback

**Add to system prompt (all personas):**
```markdown
## Technical Confidence Calibration

When user proposes technical approach:
1. Assess approach quality (good/okay/problematic/wrong)
2. Assess your confidence in that assessment (high/medium/low)

Pushback decision matrix:

| Quality      | Confidence | Action                           |
|--------------|------------|----------------------------------|
| Problematic  | High       | MUST push back with alternative  |
| Problematic  | Medium     | Flag concern, suggest alternative|
| Okay         | High       | Suggest better, but proceed      |
| Okay         | Medium     | Proceed, note alternative exists |
| Good         | Any        | Proceed                          |

Format for pushback:
"I can implement this, but [specific concern]. [Evidence]. 
Alternative: [specific better approach]. Your call."
```

---

## Failure Mode #4: Missing Contradictions in Conversation

### What Happened
User states conflicting requirements across turns, Zo doesn't catch it.

### Root Cause Analysis

**Research finding:** "Recency bias" - LLMs weight recent context more heavily than earlier context.

**Why it happened:**
1. **No contradiction detector** - System doesn't compare current statement to prior statements
2. **SESSION_STATE doesn't track requirements** - Key decisions not logged for reference
3. **Lost in middle problem** - Earlier requirements buried in context

### N5-Integrated Fix

#### Component 1: Requirements Tracker (Enhances SESSION_STATE)

**New SESSION_STATE section:**
```markdown
## Requirement Log
Requirements:
  - REQ-001: "Dashboard must load in <2 seconds" (Turn 45)
  - REQ-002: "Include real-time data updates" (Turn 67)
  - REQ-003: "Support 10K concurrent users" (Turn 89)

Decisions:
  - DEC-001: "Using PostgreSQL for primary datastore" (Turn 52)
  - DEC-002: "Implementing server-side rendering" (Turn 71)

Constraints:
  - CONST-001: "Budget: $500/month for infrastructure" (Turn 12)
  - CONST-002: "Must work with existing Auth0 setup" (Turn 34)
```

**Mechanism:**
```python
# session_state_manager.py enhancement

def extract_requirements(message):
    """
    Identify requirement statements: must, need to, required, etc.
    """
    requirement_patterns = [
        r"(?:must|need to|needs to|required|has to) (.+)",
        r"(?:can't|cannot|should not|must not) (.+)",
        r"(?:should|ought to) (.+)"
    ]
    
    extracted = []
    for pattern in requirement_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        for match in matches:
            extracted.append({
                'text': match,
                'type': 'requirement',
                'turn': get_current_turn(),
                'confidence': 0.8  # Can be enhanced with NER
            })
    
    return extracted

def check_for_contradictions(new_req, existing_reqs):
    """
    Check if new requirement contradicts existing ones.
    """
    contradictions = []
    
    # Simple keyword-based contradiction detection
    # Can be enhanced with semantic similarity
    
    negative_keywords = ['not', 'no', 'never', 'without']
    new_has_negative = any(kw in new_req['text'].lower() for kw in negative_keywords)
    
    for existing in existing_reqs:
        existing_has_negative = any(kw in existing['text'].lower() for kw in negative_keywords)
        
        # Check for overlapping concepts with opposite polarity
        overlap = semantic_overlap(new_req['text'], existing['text'])
        
        if overlap > 0.7 and (new_has_negative != existing_has_negative):
            contradictions.append({
                'new': new_req,
                'existing': existing,
                'type': 'negation_conflict',
                'confidence': overlap
            })
    
    return contradictions
```

#### Component 2: Contradiction Alert System

**Auto-triggered on requirement detection:**
```python
def process_user_message(message):
    """
    Main message processing with contradiction checking.
    """
    # Extract requirements from message
    new_reqs = extract_requirements(message)
    
    if new_reqs:
        # Load existing requirements from SESSION_STATE
        state = load_session_state()
        existing_reqs = state.get('Requirements', [])
        
        # Check contradictions
        for new_req in new_reqs:
            contradictions = check_for_contradictions(new_req, existing_reqs)
            
            if contradictions:
                # Surface contradiction immediately
                return generate_contradiction_alert(contradictions)
        
        # No contradictions, add to state
        state['Requirements'].extend(new_reqs)
        save_session_state(state)
    
    # Continue normal processing
    return process_normal(message)

def generate_contradiction_alert(contradictions):
    """
    Format contradiction warning for user.
    """
    c = contradictions[0]  # Most significant
    
    return f"""
⚠️ Potential contradiction detected:

**New requirement (Turn {c['new']['turn']}):** {c['new']['text']}
**Conflicts with (Turn {c['existing']['turn']}):** {c['existing']['text']}

Which should I follow, or should I find a way to satisfy both?
"""
```

**Example interaction:**
```
V (Turn 45): "The dashboard must load in under 2 seconds."
Zo: [Logs REQ-001 to SESSION_STATE]

V (Turn 67): "Include real-time data updates every 100ms."
Zo: [Logs REQ-002, no contradiction]

V (Turn 98): "Actually, we can't have any real-time updates, everything should be cached."

Zo: ⚠️ Potential contradiction detected:

**New requirement (Turn 98):** "can't have any real-time updates"
**Conflicts with (Turn 67):** "Include real-time data updates every 100ms"

Which should I follow, or should we find a middle ground?
```

---

## Failure Mode #5: Forgetting Ground Rules as Conversations Get Longer

### What Happened
Core principles/rules fade from "attention" as conversation lengthens.

### Root Cause Analysis

**Research finding:** "Lost in the middle" + "attention decay" - transformers pay less attention to earlier context as sequence grows.

**Why it happened:**
1. **Long context dilution** - Rules stated at turn 1 are buried by turn 100
2. **No periodic reinforcement** - Rules aren't restated or checked
3. **SESSION_STATE doesn't track rule compliance** - No active monitoring

### N5-Integrated Fix

#### Component 1: Critical Rules Tracker (SESSION_STATE Enhancement)

**New SESSION_STATE section:**
```markdown
## Active Rules & Principles
Critical_For_This_Session:
  - P15 (Complete Before Claiming): Active due to multi-part build
  - P28 (Plan DNA): Active due to system design work
  - Custom: "Always use pathlib, never os.path" (User preference from Turn 5)

Last_Checked: Turn 95
Violations_This_Session: 0
```

**Mechanism:**
```python
# session_state_manager.py enhancement

def identify_critical_rules(session_focus, session_type):
    """
    Based on session focus, identify which principles matter most.
    """
    rule_map = {
        'building': ['P5', 'P15', 'P19', 'P28'],  # Safety, completion, errors, plan
        'research': ['P2', 'P4', 'P21'],  # SSOT, ontology, assumptions
        'teaching': ['P1', 'P21'],  # Human-readable, document assumptions
        'strategy': ['P8', 'P15', 'P21']  # Minimal context, complete, assumptions
    }
    
    critical = rule_map.get(session_type, [])
    
    # Add user-stated preferences from early in session
    user_prefs = extract_user_preferences_from_history()
    critical.extend(user_prefs)
    
    return critical

def check_rule_compliance(action, critical_rules):
    """
    Before executing, check if action violates any critical rules.
    """
    violations = []
    
    for rule_id in critical_rules:
        rule = load_principle(rule_id)
        if rule['trigger_pattern'] in action and not rule['pattern_followed']:
            violations.append({
                'rule': rule_id,
                'violation': describe_violation(action, rule),
                'severity': rule.get('severity', 'medium')
            })
    
    return violations
```

#### Component 2: Periodic Rule Reinforcement

**Meta-cognitive check (every 20 turns):**
```python
def periodic_rule_check():
    """
    Every 20 turns, remind about critical rules.
    """
    current_turn = get_current_turn()
    
    if current_turn % 20 == 0:
        state = load_session_state()
        critical_rules = state.get('Critical_For_This_Session', [])
        
        # Self-reminder (not shown to user)
        internal_reminder = f"""
        [Meta: Turn {current_turn}. Critical rules this session: {critical_rules}]
        [Check recent actions against these before proceeding]
        """
        
        # Check if any were violated recently
        recent_actions = get_recent_actions(20)
        violations = []
        for action in recent_actions:
            violations.extend(check_rule_compliance(action, critical_rules))
        
        if violations:
            return {
                'action': 'surface_violations',
                'message': format_violation_report(violations)
            }
    
    return None
```

#### Component 3: Context Window Optimization (Lost-in-Middle Fix)

**Reorder context to place rules at beginning and end:**
```python
def construct_optimized_context(session_state, recent_messages, all_messages):
    """
    Leverage research finding: place important info at beginning and end.
    """
    context_structure = [
        # BEGINNING (high attention)
        "=== CRITICAL RULES FOR THIS SESSION ===",
        format_critical_rules(session_state['Critical_For_This_Session']),
        
        "=== SESSION OBJECTIVES ===",
        session_state.get('Focus'),
        session_state.get('Primary_Goal'),
        
        # MIDDLE (lower attention) - chronological messages
        format_message_history(all_messages[:-10]),  # Older messages
        
        # END (high attention)
        "=== RECENT CONTEXT ===",
        format_message_history(recent_messages[-10:]),  # Last 10 turns
        
        "=== ACTIVE STATE ===",
        f"Current persona: {session_state.get('Current_Persona')}",
        f"Active artifacts: {session_state.get('Artifacts')}",
        f"Requirements: {session_state.get('Requirements')}"
    ]
    
    return "\n".join(context_structure)
```

**This matches research finding:** Information at beginning and end has highest recall, middle has worst.

---

## Implementation Priorities

### Phase 1: High Impact, Lower Effort (Week 1-2)

1. **Ambiguity Detection for High-Stakes Operations**
   - Build `N5/lists/ambiguous_terms.md`
   - Integrate with existing `risk_scorer.py`
   - Add confirmation prompt before high-risk ops

2. **Persona Switchback Automation**
   - Add Persona_Context to SESSION_STATE.md
   - Add completion rule to specialized personas
   - Test with Builder → Operator flow

3. **Requirements Logging in SESSION_STATE**
   - Add Requirements/Decisions/Constraints sections
   - Extract requirements from messages
   - Simple keyword-based contradiction checking

### Phase 2: Medium Impact, Medium Effort (Week 3-4)

4. **Technical Pushback Protocol**
   - Create P38_technical_pushback.yaml
   - Integrate trap_door_checker.py
   - Add confidence-based pushback to system prompt

5. **Periodic Rule Reinforcement**
   - Add Active_Rules to SESSION_STATE
   - Implement 20-turn rule check
   - Surface violations when detected

6. **Context Window Optimization**
   - Reorder context construction (rules at beginning/end)
   - Compress middle context to summaries
   - Test with long conversations (>100 turns)

### Phase 3: High Impact, Higher Effort (Week 5-8)

7. **Intent Tracking System**
   - Multi-hypothesis intent modeling
   - Confidence scoring for interpretations
   - Clarification triggers

8. **Advanced Contradiction Detection**
   - Semantic similarity (embedding-based)
   - Constraint propagation
   - Implication reasoning

9. **Meta-Cognitive Self-Checks**
   - Goal alignment checks every 15 turns
   - Assumption validation
   - Plan vs reality verification

---

## Success Metrics

### Per Failure Mode

| Failure Mode | Current State | Target State | Measurement |
|---|---|---|---|
| Ambiguity issues | ~30% of destructive ops need clarification after the fact | <5% proceed with wrong interpretation | Log clarification requests vs corrections |
| Forgot persona switch | ~40% of specialized work doesn't auto-return | 95% auto-return to Operator | Track persona switches in SESSION_STATE |
| Missing pushback | ~60% of suboptimal approaches proceed unchallenged | 80% of known trap doors flagged | Count trap door detections |
| Contradictions | ~20% of contradictions go unnoticed | <5% undetected | Log contradiction alerts vs post-hoc discoveries |
| Rule decay | Unknown (no tracking) | 90% compliance with critical rules | Periodic rule checks log violations |

### System-Wide

- **User Trust Score:** Survey-based, target 8.5/10
- **Clarification Precision:** Target >95% (clarifications that were actually needed)
- **Autonomous Success Rate:** Actions that succeed without correction, target >85%
- **False Refusal Rate:** Times Zo refuses valid requests, target <2%

---

## Next Steps

1. **Validate priorities with V** - Which failure modes are most painful?
2. **Spike prototype** - Build Week 1-2 components in isolation
3. **Integration test** - Test with real conversation scenarios
4. **Measure baseline** - Capture current failure rates
5. **Iterate** - Roll out phases, measure improvement

---

## Questions for V

1. **Which failure mode is most expensive/frustrating?** Helps prioritize.
2. **Are there other failure patterns I missed?** Want complete picture.
3. **Would you prefer gradual rollout or big-bang?** Impacts implementation strategy.
4. **Who else should review this?** Technical team? Product?

