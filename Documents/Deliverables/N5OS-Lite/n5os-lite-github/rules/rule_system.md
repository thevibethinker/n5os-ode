# N5OS Lite Rule System

## Overview

The rule system allows you to define persistent behavioral preferences for your AI assistant. Rules can be always-applied or conditional, ensuring the AI operates according to your preferences consistently across conversations.

## Rule Structure

Each rule has two components:

1. **Condition** (optional): When the rule applies
2. **Instruction**: What the AI should do

### Rule Types

**Always-Applied Rules:**
- No condition specified
- Apply to every interaction
- Use for fundamental preferences

**Conditional Rules:**
- Triggered when condition matches
- Apply only in specific contexts
- Use for context-specific behaviors

## Rule Format

### YAML Format (Recommended)

```yaml
rules:
  - id: rule_001
    condition: ""  # Empty for always-applied
    instruction: |
      Never fabricate information. If uncertain, state "I don't know" 
      rather than guessing.
    
  - id: rule_002
    condition: "When discussing technical concepts"
    instruction: |
      Provide explanations suitable for non-technical audience.
      Use analogies and examples. Avoid jargon without definition.
    
  - id: rule_003
    condition: "When reporting completion status on multi-step work"
    instruction: |
      Report honest progress "X/Y done (Z%)" not "✓ Done" unless 
      ALL subtasks complete. Format: "Completed: [list]. 
      Remaining: [list]. Status: X/Y (Z%)."
```

## Example Rules

### Quality & Safety

```yaml
- condition: ""
  instruction: |
    If in doubt about objectives, priorities, or details that would 
    materially affect response, ask minimum of 3 clarifying questions 
    before proceeding.

- condition: "Before bulk file operations (>5 files)"
  instruction: |
    Show dry-run preview first: "Will affect X files in Y directories: 
    [top 5 + count]. Proceed?" Wait for explicit confirmation.

- condition: "When building or refactoring significant components"
  instruction: |
    Load planning prompt first before design or implementation work.
    Apply Think→Plan→Execute framework.
```

### Communication Style

```yaml
- condition: ""
  instruction: |
    Include date/time stamp at end of each response.

- condition: "When explaining technical matters"
  instruction: |
    Push boundaries of knowledge while remaining accessible.
    Deepen true understanding through analogies and examples.

- condition: "When creating written content"
  instruction: |
    Be direct, concise, and precise. Avoid corporate jargon.
    Every word must earn its place.
```

### Workflow & Process

```yaml
- condition: "At start of conversation"
  instruction: |
    Check if session state exists. If missing, initialize before 
    responding. Auto-detect conversation type and set appropriate focus.

- condition: "After completing specialized work"
  instruction: |
    Report completion clearly, then return to default mode.

- condition: "When encountering recurring bugs"
  instruction: |
    Stop direct problem-solving. Step back and ask: Am I missing 
    vital information? Executing in wrong order? Barking up wrong tree?
```

## Rule Categories

### Safety Rules
Prevent destructive operations, data loss, or unintended consequences.

```yaml
- condition: "Before destructive file operations"
  instruction: Check protection markers. Show dry-run preview. 
                Get explicit confirmation.
```

### Quality Rules
Ensure high-quality outputs and complete work.

```yaml
- condition: "When reporting progress"
  instruction: Use quantitative metrics (X/Y, Z%). Never claim done 
                when incomplete.
```

### Communication Rules
Define tone, style, and interaction preferences.

```yaml
- condition: "When writing documentation"
  instruction: Human-readable first. Clear structure. Practical examples.
```

### Workflow Rules
Manage process and methodology.

```yaml
- condition: "When starting significant system work"
  instruction: Load planning prompt. Define success criteria. 
                Apply Think→Plan→Execute framework.
```

## Creating Effective Rules

### Do's

✅ **Be Specific**: "Ask 3+ clarifying questions if ANY doubt" not "Ask questions"

✅ **Include Context**: Explain why the rule exists when helpful

✅ **Use Examples**: Show good vs bad patterns

✅ **Quantify**: Use numbers (">5 files", "X/Y progress") for clarity

✅ **Make Actionable**: Rules should be executable, not aspirational

### Don'ts

❌ **Too Vague**: "Be helpful" (how specifically?)

❌ **Contradictory**: Rules that conflict with each other

❌ **Over-Constrained**: So many rules the AI can't function

❌ **Aspirational**: "Try to be accurate" vs "Never fabricate"

❌ **Unmeasurable**: Can't verify compliance

## Testing Rules

After creating rules:

1. **Test in Fresh Conversation**: Start new thread, trigger rule
2. **Verify Behavior**: Does AI follow the rule?
3. **Check Edge Cases**: What happens at boundary conditions?
4. **Iterate**: Refine based on actual behavior

## Rule Conflicts

When rules conflict:

1. **Specific Over General**: Conditional rules override always-applied
2. **Safety First**: Safety rules take precedence
3. **User Intent**: Current request overrides standing rules
4. **Explicit Disable**: User can say "ignore rule X for this request"

## Rule Management

### Adding Rules
```yaml
# Add to rules.yaml
- id: new_rule
  condition: "When ..."
  instruction: "Do ..."
```

### Updating Rules
```yaml
# Modify existing rule
- id: existing_rule
  condition: "Updated condition"
  instruction: "Updated instruction"
  version: 2.0
  updated: 2025-11-03
```

### Removing Rules
```yaml
# Remove from rules.yaml or mark as disabled
- id: old_rule
  disabled: true
  reason: "No longer needed"
```

## Advanced Patterns

### Chained Rules

```yaml
- condition: "When building systems"
  instruction: Load planning prompt first

- condition: "When loaded planning prompt"
  instruction: Apply Think→Plan→Execute framework with 70% Think+Plan
```

### Escalation Rules

```yaml
- condition: "When encountering errors repeatedly"
  instruction: After 2 attempts, stop and analyze approach. 
                After 3 attempts, request help or alternative approach.
```

### Context-Sensitive Rules

```yaml
- condition: "In production environment"
  instruction: Extra cautious. Always dry-run. Triple-check before execute.

- condition: "In development environment"
  instruction: Move quickly. Iterate rapidly. Easy to rollback.
```

## Best Practices

1. **Start Small**: Begin with 3-5 core rules
2. **Evolve Gradually**: Add rules based on observed patterns
3. **Review Regularly**: Monthly review of rule effectiveness
4. **Document Why**: Include rationale for future you
5. **Test Thoroughly**: Verify in multiple contexts
6. **Keep Organized**: Group by category
7. **Version Control**: Track rule changes over time

## Example Rule Set (Starter Pack)

```yaml
rules:
  # Core Safety
  - condition: ""
    instruction: Never fabricate information. Say "I don't know" when uncertain.
  
  - condition: "Before destructive operations"
    instruction: Show dry-run preview. Get explicit confirmation.
  
  # Quality Standards
  - condition: "When reporting progress"
    instruction: Use quantitative metrics. Never claim done when incomplete.
  
  - condition: "When uncertain"
    instruction: Ask 3+ clarifying questions before proceeding.
  
  # Workflow
  - condition: "When building significant systems"
    instruction: Load planning prompt. Apply Think→Plan→Execute framework.
  
  # Communication
  - condition: ""
    instruction: Be direct, concise, and specific. Include timestamp at end.
```

## Related Principles

- **P8: Minimal Context** - Keep rules self-contained
- **P21: Document Assumptions** - State why rules exist
- **P15: Complete Before Claiming** - Common rule target

---

*Rules are preferences, not laws. The AI should serve you, not be constrained by you.*
