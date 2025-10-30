# Zo Export Specification Format

**Version:** 1.0  
**Created:** 2025-10-28  
**Purpose:** Standardized format for transferring system knowledge between Zo instances

---

## Philosophy

**Principle:** Transfer understanding, not implementation.

Export specifications describe *how a system works* conceptually and architecturally. The receiving Zo learns from the spec and implements the functionality in its own native way, adapted to its context.

**Inspired by:** N5 Planning Prompt - "Code Is Free, Thinking Is Expensive"  
The valuable asset is the *design thinking*, not the code itself.

---

## Specification Structure

Each export spec is a self-contained markdown document that follows this template:

```markdown
# [System Name] - Zo Export Specification

**Version:** X.Y.Z  
**Export Date:** YYYY-MM-DD  
**Source System:** [System identifier]  
**Maturity:** [Prototype | Production | Battle-tested]

---

## 1. Overview

### Purpose
What problem does this solve? Why does it exist?

### Key Capabilities
- Bullet list of what the system does
- Focus on outcomes, not mechanics

### Use Cases
- Who uses this?
- When do they use it?
- What value does it provide?

### Success Metrics
How do you know it's working?

---

## 2. Architecture

### Design Philosophy
Key design values and trade-offs made

### System Components
High-level component diagram (mermaid or prose)

### Data Flow
How information moves through the system
- Entry points
- Transformation stages
- Output destinations
- Exit conditions

### Integration Points
How this system connects to:
- File system
- Commands/recipes
- Other systems
- External services

---

## 3. Data Structures

### Core Schemas
Include JSON schemas or describe structure

### File Formats
What files does this system read/write?

### State Management
How does the system track its state?

---

## 4. Core Logic

### Key Algorithms
Describe the important logic/algorithms (pseudocode acceptable)

### Validation Rules
What makes data valid/invalid?

### Error Handling
How does the system handle failures?

### Quality Gates
What quality checks are enforced?

---

## 5. Implementation Guidance

### Suggested Approach
Recommended implementation strategy for receiving system

### Trap Doors (Irreversible Decisions)
What decisions are hard to change later?

### Patterns to Consider
Useful patterns this system uses

### Anti-Patterns to Avoid
Known pitfalls from original implementation

---

## 6. Reference Implementation

### Example Code
Simplified reference implementation (can be pseudocode)

### Test Cases
Key test scenarios

### Example Inputs/Outputs
Concrete examples of system behavior

---

## 7. Operational Considerations

### Performance Characteristics
Speed, scale, resource usage

### Monitoring & Telemetry
What to track for system health

### Maintenance Requirements
What ongoing care does this need?

### Known Limitations
Current constraints or missing features

---

## 8. Evolution History

### Design Decisions
Key decisions and their rationale

### Lessons Learned
What would you do differently?

### Future Directions
Where could this system go?

---

## Appendices

### A. Glossary
Domain-specific terms

### B. Related Systems
Dependencies and integrations

### C. References
External resources, papers, inspirations
```

---

## Package Structure

When exporting multiple systems, organize as:

```
zo-export-[name]-[date]/
├── README.md                          # Export overview and manifest
├── specs/
│   ├── command-authoring.md          # Individual system specs
│   ├── documentation-generation.md
│   ├── timeline-system.md
│   └── telemetry-tracking.md
├── schemas/
│   ├── command.schema.json           # Referenced schemas
│   ├── timeline.schema.json
│   └── telemetry.schema.json
├── examples/
│   ├── sample-command.json
│   ├── sample-timeline-entries.jsonl
│   └── sample-outputs/
└── reference-impl/                    # Optional: simplified reference code
    ├── command_author_demo.py
    └── docgen_demo.py
```

---

## Transfer Protocol

**For Exporting System:**
1. Generate specs following this template
2. Include all referenced schemas
3. Provide concrete examples
4. Document design decisions and rationale
5. Test that spec is comprehensible standalone

**For Receiving System:**
1. Read and understand the spec
2. Identify integration points with local system
3. Adapt architecture to local patterns
4. Implement core logic as specified
5. Test against provided examples
6. Validate against schemas

---

## Quality Standards

**A good export spec should:**
- Be comprehensible without access to source code
- Explain *why* not just *what*
- Include concrete examples
- Identify trap doors explicitly
- Document trade-offs made
- Be implementation-agnostic (don't assume tech stack)

**Anti-patterns:**
- Just copying code with comments
- Assuming receiver knows your system
- Skipping the "why" and design rationale
- No examples or test cases
- Missing error handling guidance

---

## Maturity Levels

**Prototype:** Experimental, design may change  
**Production:** In active use, design stabilized  
**Battle-tested:** Multiple versions, proven patterns, lessons learned

Export specs should indicate maturity to set expectations.

---

*This format is itself a Zo export spec - meta!*
