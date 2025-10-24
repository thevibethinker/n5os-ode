# Incantum Expansion Design Specification

**Date:** 2025-10-23  
**Purpose:** Evolve incantum from keyword triggers to natural language command parsing  
**Status:** Design Phase

---

## Requirements

### Core Objectives
1. **Natural Language Parsing:** Convert "N5 <natural language>" into command sequences
2. **Learning System:** Store and reference successful patterns for context-aware parsing
3. **User Shortcuts:** Support custom shortcuts (e.g., "eod" → end-of-day sequence)
4. **Smart Execution:** Auto-execute single commands, propose multi-step workflows

### Success Criteria
- Single command detection → immediate execution
- Multi-command detection → propose flow, await confirmation
- Learning system captures successful patterns with context
- Shortcuts resolve before full parsing
- System prompt integration seamless

---

## Architecture

### Components

```
incantum_parser.py          # Core NL → command mapping logic
├── parse_intent()          # Main entry point
├── check_shortcuts()       # Fast path: user-defined shortcuts
├── check_patterns()        # Learned patterns with context
├── extract_commands()      # LLM-based intent extraction
└── validate_sequence()     # Dependency checking

incantum_triggers.json      # Enhanced with intent patterns (existing, enhanced)
incantum_shortcuts.json     # User-defined shortcuts (new)
incantum_patterns.jsonl     # Learned successful patterns (new, append-only)
commands.jsonl              # Command registry (existing, SSOT)
```

### Data Flow

```
User: "N5 checkpoint this and update my build tracker"
  ↓
Zo detects "N5" prefix → calls incantum_parser.py
  ↓
Parser logic:
  1. Check shortcuts (not found)
  2. Check learned patterns (not found)
  3. Extract commands via intent mapping:
     - "checkpoint this" → thread-checkpoint
     - "update my build tracker" → ???  (need to resolve)
  4. Validate sequence
  5. Return: {commands: [...], confidence: 0.8, needs_confirmation: True}
  ↓
Zo: [2 commands detected]
  "I'll run these commands:
  1. thread-checkpoint
  2. [unknown - need clarification on build tracker]
  
  Shall I proceed?"
```

---

## File Specifications

### 1. `incantum_parser.py`

**Location:** `/home/workspace/N5/scripts/incantum_parser.py`

**Interface:**
```python
def parse_intent(
    natural_language: str,
    context: dict = None
) -> dict:
    """
    Parse natural language into command sequence.
    
    Args:
        natural_language: User's NL instruction (after "N5" prefix)
        context: Optional context (conversation_id, recent_files, etc.)
    
    Returns:
        {
            "commands": [{"name": str, "args": dict}, ...],
            "confidence": float,  # 0.0-1.0
            "needs_confirmation": bool,
            "rationale": str,
            "unresolved": [str, ...]  # Unresolved intents
        }
    """
```

**Core Logic:**
1. **Shortcuts** (O(1) lookup)
2. **Learned Patterns** (semantic similarity check)
3. **Intent Extraction** (LLM-based, query commands.jsonl)
4. **Sequence Validation** (check dependencies, order)

**Safety:**
- Dry-run by default for destructive operations
- Confidence threshold for auto-execution (>0.85)
- Always confirm multi-step sequences
- Log all parsed intents for learning

---

### 2. `incantum_triggers.json` (Enhanced)

**Location:** `/home/workspace/N5/config/incantum_triggers.json`

**Current:** Simple keyword → command mapping

**Enhancement:** Add intent patterns
```json
{
  "trigger": "end conversation",
  "aliases": ["close thread", "wrap up", "end step", "we're done"],
  "command": "conversation-end",
  "intent_patterns": [
    "finish this conversation",
    "I'm done here",
    "let's close out",
    "wrap this up"
  ],
  "keywords": ["end", "close", "wrap", "done", "finish"]
}
```

**Why:** Enables semantic matching beyond exact keywords

---

### 3. `incantum_shortcuts.json` (New)

**Location:** `/home/workspace/N5/config/incantum_shortcuts.json`

**Schema:**
```json
{
  "shortcuts": {
    "eod": {
      "description": "End of day routine",
      "commands": [
        {"name": "git-check", "args": {}},
        {"name": "lists-health-check", "args": {}},
        {"name": "conversation-end", "args": {}}
      ],
      "requires_confirmation": true
    },
    "checkpoint": {
      "description": "Quick thread checkpoint",
      "commands": [
        {"name": "thread-export", "args": {}}
      ],
      "requires_confirmation": false
    }
  }
}
```

**Operations:**
- User can add shortcuts via command: `incantum-add-shortcut <name> <sequence>`
- Shortcuts override learned patterns
- Editable directly (JSON file)

---

### 4. `incantum_patterns.jsonl` (New)

**Location:** `/home/workspace/N5/logs/incantum_patterns.jsonl`

**Schema (one JSON object per line):**
```json
{
  "timestamp": "2025-10-23T22:00:00Z",
  "natural_language": "checkpoint this and commit",
  "context": {
    "conversation_id": "con_XYZ",
    "recent_files": ["meeting_notes.md"],
    "hour_of_day": 22
  },
  "commands": [
    {"name": "thread-export", "args": {}},
    {"name": "git-check", "args": {}}
  ],
  "success": true,
  "user_feedback": "perfect"
}
```

**Learning Process:**
1. Parser returns sequence
2. User confirms and executes
3. On successful completion, append to patterns.jsonl
4. Future similar queries match against this pattern

**Pattern Matching:**
- Semantic similarity (embeddings or keyword overlap)
- Context similarity (time of day, file types, etc.)
- Confidence threshold for pattern reuse (>0.7)

---

## System Prompt Integration

### Addition to System Prompt

```markdown
## Incantum Command Parser

**Trigger Detection:**
When user message starts with "N5" or "incantum" (case-insensitive):
1. Extract natural language after trigger: "N5 <instruction>"
2. Call incantum parser: `python3 N5/scripts/incantum_parser.py parse "<instruction>"`
3. Parse JSON result

**Execution Logic:**
- Single command + confidence > 0.85 → Auto-execute
- Multiple commands OR confidence < 0.85 → Propose flow, await confirmation
- Unresolved intents → Ask clarifying questions

**Learning:**
- On successful execution, log to incantum_patterns.jsonl
- Include context: conversation_id, time, files, user feedback

**Example:**
User: "N5 checkpoint and commit"
→ Parse: ["thread-export", "git-check"]
→ Propose: "I'll checkpoint this thread and run a git check. Proceed?"
→ Execute on confirmation
→ Log successful pattern
```

---

## Error Handling

### Failure Modes

1. **Parser fails to extract commands**
   - Return: `{"commands": [], "unresolved": ["<original text>"]}`
   - Zo asks: "I couldn't parse that. Did you mean...?"

2. **Command not found in registry**
   - Return: `{"commands": [...], "unresolved": ["unknown command"]}`
   - Zo asks: "I don't recognize 'X'. Available commands: [suggestions]"

3. **Dependency conflict**
   - Return: `{"error": "Command A requires B to run first"}`
   - Zo proposes: "I'll reorder to: [B, A]"

4. **Ambiguous intent**
   - Return: `{"confidence": 0.4, "candidates": [...]}`
   - Zo asks: "Did you mean: 1) X, 2) Y, 3) Z?"

---

## Testing Strategy

### Dry-Run Tests
```bash
# Test single command
python3 N5/scripts/incantum_parser.py parse "checkpoint this" --dry-run

# Test multi-command
python3 N5/scripts/incantum_parser.py parse "checkpoint and commit" --dry-run

# Test shortcut
python3 N5/scripts/incantum_parser.py parse "eod" --dry-run

# Test learned pattern
python3 N5/scripts/incantum_parser.py parse "wrap up and commit" --dry-run
```

### Production Tests
1. Add test shortcut
2. Parse known command
3. Parse multi-step workflow
4. Verify pattern learning
5. Test pattern reuse
6. Test error cases

---

## Implementation Phases

### Phase 1: Core Parser (MVP)
- [ ] Create `incantum_parser.py` with basic intent extraction
- [ ] Enhance `incantum_triggers.json` with intent patterns
- [ ] Test against commands.jsonl registry
- [ ] Return confidence + command sequence

### Phase 2: Shortcuts System
- [ ] Create `incantum_shortcuts.json`
- [ ] Implement shortcut resolution
- [ ] Add CLI for managing shortcuts
- [ ] Test shortcut execution

### Phase 3: Learning System
- [ ] Create `incantum_patterns.jsonl`
- [ ] Implement pattern logging
- [ ] Implement pattern matching
- [ ] Test pattern reuse

### Phase 4: System Prompt Integration
- [ ] Update system prompt with parser logic
- [ ] Test auto-execution
- [ ] Test confirmation flow
- [ ] Test learning loop

### Phase 5: Validation & Documentation
- [ ] Test all failure modes
- [ ] Document parser behavior
- [ ] Update N5.md
- [ ] Create user guide

---

## Principles Compliance

✅ **P1 (Human-Readable):** JSON schemas, clear command names  
✅ **P2 (SSOT):** commands.jsonl is the command registry  
✅ **P5 (Anti-Overwrite):** Check file protection before commands  
✅ **P7 (Dry-Run):** Parser supports --dry-run flag  
✅ **P11 (Failure Modes):** All error cases documented  
✅ **P15 (Complete):** All phases defined, testing planned  
✅ **P18 (State Verification):** Log and verify successful patterns  
✅ **P19 (Error Handling):** Explicit error paths for all failures  
✅ **P20 (Modular):** Parser is standalone, integrates cleanly

---

## Questions for V

1. ✅ Integration (system prompt + standalone script)
2. ✅ Execution model (auto-execute single, confirm multi)
3. ✅ Learning (store patterns) + shortcuts (user-defined)

---

## Next Steps

1. Implement Phase 1 (Core Parser)
2. Test with existing commands
3. Show V examples and gather feedback
4. Iterate to Phases 2-5

