# Simple "Record" Integration into Existing N5 Command System

## Understanding N5's Existing Command System

N5 already has a structured command system with commands like:
- `knowledge-add` - Add facts to knowledge base
- `lists-add` - Add items to lists with intelligent assignment
- `timeline-add` - Add timeline events
- `system-upgrades-add` - Add system upgrade items

Each command has:
- Structured inputs/outputs defined
- Documentation in `/home/workspace/N5/commands/`
- Integration with existing workflows
- Schema validation and safety systems

## The Simple Integration Approach

Instead of creating a new workflow system, we integrate "record" as **shorthand aliases** for existing commands.

### Core Concept
"Record" becomes a **smart router** that maps natural language to existing N5 commands:
- `record link <url>` → `essential-links-add url=<url>`
- `record fact <subject> <predicate> <object>` → `knowledge-add subject=<subject> predicate=<predicate> object=<object>`
- `record idea <idea>` → `lists-add title=<idea>`
- `record person <name>` → `knowledge-add subject=<name> predicate=is object=person`

## Implementation Plan

### Step 1: Create Record Command Definition
Add `record` as a new command following N5's existing command structure.

**File**: `/home/workspace/N5/commands/record_20250920_132252.md`

```markdown
# `record`

Version: 0.1.0

Summary: Natural language interface to record various types of data

Workflow: meta-command

Tags: record, routing, natural-language

## Inputs
- type : enum [link, fact, idea, person, event] (required) — Type of data to record
- data : text (required) — Primary data content
- context : text — Additional context or description
- tags : json — Tags for the recorded item

## Outputs
- command_executed : text — The actual N5 command that was executed
- result : json — Result from the executed command

## Side Effects
- Delegates to other commands, inheriting their side effects

## Examples
- N5: run record type=link data="https://example.com" context="Important resource"
- N5: run record type=fact data="N5 is powerful"
- N5: run record type=idea data="Improve workflow system"

## Related Components
**Related Commands**: All data entry commands (knowledge-add, lists-add, etc.)
```

### Step 2: Create Record Script Implementation
**File**: `/home/workspace/N5/scripts/n5_record.py`

This script should:
1. Parse the "record" command inputs
2. Map the type to appropriate existing N5 command
3. Transform the data into the correct format for that command
4. Execute the target command
5. Return the result

**Key Mappings**:
```python
RECORD_MAPPINGS = {
    'link': {
        'command': 'essential-links-add',
        'transform': lambda data, context: {
            'url': data,
            'title': context or 'Recorded Link'
        }
    },
    'fact': {
        'command': 'knowledge-add', 
        'transform': lambda data, context: {
            'subject': 'recorded-fact',
            'predicate': 'states',
            'object': data,
            'source': context
        }
    },
    'idea': {
        'command': 'lists-add',
        'transform': lambda data, context: {
            'title': data,
            'body': context
        }
    }
}
```

### Step 3: Integrate with Existing Command System
1. Add record command to the command registry (however N5 tracks commands)
2. Ensure it follows N5's safety and logging patterns
3. Test with existing commands to ensure compatibility

## Execution Steps

### Phase 1: Basic Implementation
1. **Create Command Definition**: Add record command documentation following N5 patterns
2. **Create Record Script**: Simple router that delegates to existing commands
3. **Test Integration**: Verify it works with `essential-links-add` from Phase 1

### Phase 2: Expand Mappings
1. **Add Fact Recording**: Map to `knowledge-add`
2. **Add Idea Recording**: Map to `lists-add`  
3. **Add Person Recording**: Create person-specific knowledge entries

### Phase 3: Smart Classification
1. **Add LLM Classification**: When type is ambiguous, use LLM to determine intent
2. **Add Context Parsing**: Extract structured data from natural language
3. **Add Validation**: Ensure data quality before delegation

## Key Benefits of This Approach

1. **Leverages Existing System**: No new architecture, just a smart router
2. **Maintains Safety**: Inherits all existing N5 safety mechanisms
3. **Simple to Understand**: Maps natural language to existing commands
4. **Easy to Extend**: Add new mappings without changing core system
5. **Backward Compatible**: All existing commands continue to work unchanged

## Files to Create

1. `/home/workspace/N5/commands/record_20250920_132252.md` - Command documentation
2. `/home/workspace/N5/scripts/n5_record.py` - Implementation script
3. Update command registry to include "record" command

## Testing Plan

1. Test `record link` → `essential-links-add` delegation
2. Test `record fact` → `knowledge-add` delegation  
3. Test `record idea` → `lists-add` delegation
4. Verify all existing commands still work unchanged
5. Test error handling and validation

This approach respects N5's existing architecture while adding the natural language "record" interface you want.