---
created: 2025-11-11
last_edited: 2025-11-11
version: 1.0
---

# Rule Priority System

**Purpose:** Establish clear priority hierarchy for user rules to ensure critical behavior is never skipped.

## Priority Levels

### P0: CRITICAL - Must Execute or Fail
**Enforcement:** These rules MUST be executed first. Failure = conversation fails.  
**Characteristics:**
- Session initialization and tracking
- Safety checks before destructive operations
- Conversation ID declaration
- SESSION_STATE maintenance

**Rules:**
- `5c72e81d-529d-44e7-84bf-9d750208949b`: SESSION_STATE initialization
- `1f5346fe-fb94-4f7c-bdbf-d43b6e480bda`: SESSION_STATE maintenance
- (TBD): Safety checks for destructive ops

### P1: HIGH - Strong Preference
**Enforcement:** Should execute unless explicitly overridden by user in conversation.  
**Characteristics:**
- Quality standards (no hallucination, ask clarifying questions)
- Technical explanation style
- Documentation requirements
- Workflow discipline (debug logging, component validation)

**Rules:**
- `dea82942-f43e-494f-a541-18e292428001`: No hallucination
- `32ace0a3-46ff-48a6-a0d4-2ef135f6ce5d`: Clarifying questions (3 minimum)
- `905df1e4-7df1-4349-90f3-20565c2e3978`: Technical explanation style
- `87801b51-abfe-40f8-a175-b252a11a0b21`: Debug logging discipline
- `75305aba-2c4d-40e5-9bdc-2244b011bb6b`: Component validation
- `50952733-3c96-4030-a525-28aad3f77044`: Load planning prompt for N5 work
- `575404c2-ef45-4008-96ee-06b7b89edb1b`: Prompt-first approach

### P2: MEDIUM - General Guidance
**Enforcement:** Follow unless context suggests otherwise.  
**Characteristics:**
- Formatting preferences
- File organization patterns
- Communication style
- Process protocols

**Rules:**
- `93131fa2-d4ea-41d0-9217-4f3cd8fb54ab`: Timestamp at end of responses
- `d3183710-fe9e-41e7-a5ca-0102f501f5cb`: No messages/downloads without authorization
- `076735f6-e36e-466a-9853-a38e1ce4a71e`: n5:resume protocol
- Processing/archiving rules (meetings → Personal/Meetings)
- Markdown frontmatter requirements

### P3: LOW - Context-Specific
**Enforcement:** Apply only when condition matches.  
**Characteristics:**
- Domain-specific rules
- Conditional behaviors
- Specialized workflows

**Rules:**
- `cda609d1-7e88-499e-ab08-11129cdb12c5`: Careerspan spelling
- `6fde372c-f5c4-4f25-94f6-bac7bf927ef7`: /gfetch command
- Scheduled task protocol (when creating tasks)
- Debug logging (when DEBUG_LOG.jsonl exists)

## Enforcement Mechanisms

### For P0 Rules (Critical)
1. **Persona-Level:** P0 checklist at top of every persona
2. **System-Level:** Hardcoded in ALWAYS APPLIED rules section
3. **Verification:** Automated agent checks P0 compliance

### For P1 Rules (High Priority)
1. **Persona Integration:** Included in relevant persona self-checks
2. **Workflow Integration:** Built into process documentation
3. **Monitoring:** Track compliance in quality reviews

### For P2-P3 Rules (General/Contextual)
1. **Natural Integration:** Part of system prompt, applied contextually
2. **User Correction:** User can override in-conversation
3. **Documentation:** Reference guides for consistent application

## Adding New Rules

When creating a new rule, classify it:

```markdown
**P0:** Does failure break core functionality or safety?
  → Yes: P0 (add to persona checklists + ALWAYS APPLIED)
  
**P1:** Does it affect quality/reliability significantly?
  → Yes: P1 (integrate into persona self-checks)
  
**P2:** Is it general guidance that improves consistency?
  → Yes: P2 (keep in system prompt)
  
**P3:** Is it conditional/domain-specific?
  → Yes: P3 (apply when condition matches)
```

## Rule Audit Protocol

**Quarterly:** Review all rules and re-classify if needed
- Have P0 rules changed? Update personas immediately
- Are P1 rules being followed? Adjust if compliance low
- Are P3 rules still relevant? Archive if unused

## References

- Persona definitions: `list_personas`
- Current rules: `list_rules`
- Rule management: `create_rule`, `edit_rule`, `delete_rule`
- Priority changes: Update this document + relevant personas


