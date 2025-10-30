# Export Spec 004: Command Authoring System

**System:** AI-Assisted Command Creation Pipeline  
**Version:** 2.5 (Production)  
**Maturity:** Battle-tested, sophisticated multi-phase architecture  
**Last Updated:** 2025-10-28

---

## 1. System Overview

### Purpose
Transform natural language conversation into production-ready system commands through structured 6-phase pipeline with quality gates and telemetry.

### Core Concept
**Conversation → Command.**  
User describes what they want in conversation. System extracts intent, generates implementation, validates, and exports as registered command.

### Key Innovation
- **Phase-based pipeline** with clear handoffs and telemetry
- **Quality gates** at each phase (BLOCK/ALLOW/PASS)
- **Telemetry-driven** diagnostics and improvement
- **Separation of concerns** - each phase is independent, testable module

---

## 2. Architecture

### Six-Phase Pipeline

```
Phase 1: PARSE
  ↓ (conversation → segments)
Phase 2: SCOPE
  ↓ (segments → requirements)
Phase 3: GENERATE
  ↓ (requirements → implementation)
Phase 4: VALIDATE
  ↓ (implementation → validated spec)
Phase 5: RESOLVE
  ↓ (spec → resolved command)
Phase 6: EXPORT
  ↓ (command → registered + docs)
```

### Phase Handoff Protocol
Each phase outputs **telemetry JSON** with:
- Phase ID and status (SUCCESS/PARTIAL/FAILED)
- Primary artifact (the work product)
- Warnings/errors encountered
- Performance metrics
- Quality scores
- Next phase readiness assessment

---

## 3. Phase Details

### Phase 1: Conversation Parser
**Input:** Raw conversation transcript (markdown/text)  
**Output:** Structured JSON segments

**Responsibilities:**
- Identify user requests vs AI responses
- Extract tool calls and parameters
- Detect command intent signals
- Segment by topic/context shifts
- Tag key phrases and requirements

**Quality Gate:**
- Must identify primary command intent
- Must extract at least 3 requirement indicators
- BLOCK if: No clear intent, ambiguous requirements

**Example Output:**
```json
{
  "segments": [
    {
      "id": "seg_1",
      "type": "user_request",
      "content": "I want to search my commands",
      "intent": "query_system",
      "keywords": ["search", "commands"]
    }
  ],
  "primary_intent": "search_commands",
  "confidence": 0.92
}
```

---

### Phase 2: Requirements Scoper
**Input:** Parsed segments  
**Output:** Structured requirements document

**Responsibilities:**
- Define command interface (inputs/outputs)
- Identify constraints and dependencies
- Specify success criteria
- Map to existing system patterns
- Define test scenarios

**Quality Gate:**
- Must specify at least 1 input parameter
- Must define success criteria
- Must check for conflicts with existing commands
- BLOCK if: Duplicate command exists, requirements too vague

**Example Output:**
```json
{
  "command_name": "search-commands",
  "inputs": {
    "query": {"type": "string", "required": true},
    "tags": {"type": "array", "required": false}
  },
  "outputs": {
    "matches": {"type": "array", "items": "command_object"}
  },
  "success_criteria": [
    "Returns relevant commands ranked by match score",
    "Supports partial matching",
    "Handles no results gracefully"
  ]
}
```

---

### Phase 3: Implementation Generator
**Input:** Requirements document  
**Output:** Working code implementation

**Responsibilities:**
- Generate script/executable code
- Implement core logic
- Add error handling
- Include logging
- Follow language conventions
- Add inline documentation

**Quality Gate:**
- Must pass syntax check
- Must include error handling
- Must log key operations
- BLOCK if: Syntax errors, missing imports, no error handling

**Code Standards:**
- Python: pathlib, type hints, async where appropriate
- Shell: set -euo pipefail, proper quoting
- Error messages: specific and actionable
- Logging: structured (JSON or key=value)

---

### Phase 4: Validator
**Input:** Generated implementation  
**Output:** Validated command specification

**Responsibilities:**
- Run syntax checks (linting)
- Verify schema compliance
- Test core operations (dry-run)
- Check security concerns
- Validate against schema
- Performance profiling (optional)

**Quality Gate:**
- Must pass all syntax checks
- Must pass schema validation
- Dry-run must succeed
- No critical security issues
- BLOCK if: Validation failures, security risks

**Validation Types:**
- **Syntax:** Language-specific linting
- **Schema:** JSON Schema validation
- **Functional:** Dry-run with test inputs
- **Security:** Path traversal, injection risks
- **Performance:** Resource usage profiling

---

### Phase 5: Dependency Resolver
**Input:** Validated specification  
**Output:** Fully resolved command ready for registration

**Responsibilities:**
- Resolve file paths (relative → absolute)
- Verify dependencies exist
- Check permissions
- Resolve cross-references
- Generate wrapper if needed

**Quality Gate:**
- All dependencies must exist
- Paths must be valid
- Permissions must be sufficient
- BLOCK if: Missing dependencies, permission errors

---

### Phase 6: Exporter
**Input:** Resolved command  
**Output:** Registered command + documentation

**Responsibilities:**
- Register in command registry (JSONL)
- Generate documentation (markdown)
- Create usage examples
- Update command index
- Log to system timeline (optional)

**Quality Gate:**
- Must not conflict with existing commands
- Documentation must be complete
- Registry update must succeed
- BLOCK if: Registration fails, docs incomplete

**Artifacts Created:**
- Command entry in registry
- Documentation file
- Usage examples
- Test fixtures (optional)

---

## 4. Telemetry System

### Purpose
Track pipeline health, identify bottlenecks, measure quality over time.

### Telemetry Points
**Per Phase:**
- Start/end timestamps
- Input size/complexity
- Output artifacts generated
- Warnings and errors
- Quality scores
- Resource usage

**Per Pipeline Run:**
- Total duration
- Phase breakdown
- Handoff delays
- Failure points
- Retry attempts

### Telemetry Schema
```json
{
  "run_id": "unique-id",
  "timestamp": "ISO-8601",
  "phase": "1-6",
  "phase_name": "parser|scoper|generator|validator|resolver|exporter",
  "status": "SUCCESS|PARTIAL|FAILED",
  "duration_ms": 1234,
  "artifacts": {
    "primary": {"type": "json", "path": "/path/to/output.json"},
    "secondary": []
  },
  "quality_scores": {
    "completeness": 0.95,
    "correctness": 1.0,
    "clarity": 0.88
  },
  "warnings": [],
  "errors": [],
  "metadata": {}
}
```

### Analytics
- Phase success rates
- Average duration per phase
- Common failure patterns
- Quality trend over time

---

## 5. Supporting Modules

### Security Reviewer
Scans implementation for security risks:
- Path traversal vulnerabilities
- Command injection points
- Unsafe file operations
- Credential leakage
- Privilege escalation

### Performance Optimizer
Suggests improvements:
- Async opportunities
- Caching strategies
- Database query optimization
- Resource cleanup

### UX Enhancer
Improves user experience:
- Error message clarity
- Help text quality
- Example completeness
- Progress indicators

### Test Data Generator
Creates fixtures for validation:
- Valid input samples
- Invalid input samples
- Edge cases
- Performance test data

---

## 6. Integration Points

### With Command Registry
Pipeline exports directly to command registry (JSONL file).

### With Documentation System
Docgen consumes command registry to generate docs.

### With Timeline
Major command additions logged to system timeline.

### With Lists
Command ideas can originate from lists, marked as "implemented" on export.

---

## 7. Quality Standards

### Code Generation
- **Type safety:** Use type hints (Python), strict mode (JS)
- **Error handling:** Explicit try/catch, never swallow errors
- **Logging:** Structured, contextual, appropriate level
- **Documentation:** Inline comments for complex logic only

### Phase Handoffs
- **Telemetry required:** Every phase must emit telemetry
- **Schema compliance:** Artifacts must validate against schemas
- **Atomic operations:** Failures don't corrupt state
- **Rollback capable:** Failed phases can be retried

### Command Registration
- **Uniqueness:** No duplicate command names
- **Completeness:** All required fields present
- **Documentation:** Markdown docs auto-generated
- **Discoverability:** Tags, search keywords added

---

## 8. Error Recovery

### Phase Failure Strategies
**Parser fails:** Request clarification, provide examples  
**Scoper fails:** Highlight missing requirements, suggest similar commands  
**Generator fails:** Fall back to template-based generation  
**Validator fails:** Report specific issues, suggest fixes  
**Resolver fails:** Check dependencies, suggest installation  
**Exporter fails:** Verify registry not corrupted, retry write

### Partial Success
Some phases support partial success:
- Parser: Can extract some requirements even if ambiguous
- Generator: Can produce partial implementation for review
- Validator: Can warn on non-critical issues but allow proceed

---

## 9. Extension Points

### Custom Phases
Insert additional phases:
- **Post-Generator:** Code formatting, optimization
- **Pre-Validator:** Static analysis, linting
- **Post-Exporter:** Notification, deployment

### Custom Validators
Add domain-specific validation:
- Database schema compatibility
- API contract compliance
- Performance benchmarks
- Accessibility checks

### Custom Templates
Provide command templates for common patterns:
- CRUD operations
- Query interfaces
- Data transformations
- Integration workflows

---

## 10. Example Implementation

### Minimal Pipeline Orchestrator
```python
#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

def run_phase(phase_num, phase_func, input_data):
    """Execute a phase with telemetry"""
    start = datetime.now()
    
    try:
        output = phase_func(input_data)
        status = "SUCCESS"
        errors = []
    except Exception as e:
        output = None
        status = "FAILED"
        errors = [str(e)]
    
    duration = (datetime.now() - start).total_seconds() * 1000
    
    telemetry = {
        "phase": phase_num,
        "status": status,
        "duration_ms": duration,
        "errors": errors,
        "timestamp": datetime.now().isoformat()
    }
    
    return output, telemetry

def parse_conversation(transcript):
    # Extract segments, identify intent
    return {"segments": [...], "intent": "..."}

def scope_requirements(parsed):
    # Define inputs/outputs, constraints
    return {"command_name": "...", "inputs": {...}}

def generate_implementation(requirements):
    # Generate code
    return {"code": "...", "language": "python"}

def validate_implementation(implementation):
    # Run tests, check syntax
    return {"valid": True, "issues": []}

def resolve_dependencies(validated):
    # Check dependencies, resolve paths
    return {"resolved": True, "command_spec": {...}}

def export_command(resolved):
    # Register command, generate docs
    return {"registered": True, "path": "..."}

# Pipeline execution
def author_command(conversation_file):
    phases = [
        (parse_conversation, "parse"),
        (scope_requirements, "scope"),
        (generate_implementation, "generate"),
        (validate_implementation, "validate"),
        (resolve_dependencies, "resolve"),
        (export_command, "export")
    ]
    
    data = Path(conversation_file).read_text()
    telemetry_log = []
    
    for i, (phase_func, name) in enumerate(phases, 1):
        print(f"Phase {i}: {name}")
        data, telemetry = run_phase(i, phase_func, data)
        telemetry_log.append(telemetry)
        
        if telemetry["status"] == "FAILED":
            print(f"Pipeline failed at phase {i}")
            break
    
    # Save telemetry
    Path("telemetry.jsonl").write_text(
        '\n'.join(json.dumps(t) for t in telemetry_log)
    )
    
    return data

# Usage
result = author_command("conversation.md")
```

---

## 11. Testing Strategy

### Unit Tests
- Each phase independently testable
- Mock inputs for each phase
- Validate telemetry output format
- Test error handling per phase

### Integration Tests
- Full pipeline with real conversations
- End-to-end command generation
- Quality gate triggering
- Rollback scenarios

### Acceptance Tests
- Generate commands from sample conversations
- Verify registered commands work
- Check documentation quality
- Validate telemetry completeness

---

## Implementation Checklist

- [ ] Design phase interface (input/output contracts)
- [ ] Implement Phase 1: Parser
- [ ] Implement Phase 2: Scoper
- [ ] Implement Phase 3: Generator
- [ ] Implement Phase 4: Validator
- [ ] Implement Phase 5: Resolver
- [ ] Implement Phase 6: Exporter
- [ ] Build telemetry collection system
- [ ] Create phase handoff validation
- [ ] Add quality gates
- [ ] Write phase unit tests
- [ ] Write pipeline integration tests
- [ ] Create orchestrator CLI
- [ ] Document extension points
- [ ] Set up telemetry analytics (optional)

---

*Export specification format v1.0*
