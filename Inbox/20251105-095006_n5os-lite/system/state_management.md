# N5OS Lite State Management

**Version:** 1.0  
**Purpose:** Maintain conversation state and progress tracking  
**Status:** Core system component

---

## Overview

State management keeps track of what's happening in each conversation: objectives, progress, artifacts, and decisions. It's the conversational memory system.

## The SESSION_STATE.md File

Every conversation gets a `SESSION_STATE.md` file in its workspace that tracks:
- What we're trying to accomplish
- What's been completed
- What artifacts were created
- Key decisions made

**Location:** `<conversation_workspace>/SESSION_STATE.md`

---

## Structure

```markdown
# Session State

**Conversation ID:** con_XXXXXXXXXXXXXXXX  
**Type:** [build/research/discussion/planning]  
**Created:** YYYY-MM-DD HH:MM  
**Last Updated:** YYYY-MM-DD HH:MM

## Focus

[Current primary objective - one sentence]

## Objective

[Detailed goal for this conversation]

## Progress

### Completed
- [x] Task 1
- [x] Task 2

### In Progress
- [ ] Task 3 (blocked by X)

### Pending
- [ ] Task 4
- [ ] Task 5

## Topics Covered

- Topic 1: Brief summary
- Topic 2: Brief summary

## Artifacts

### Temporary (conversation workspace)
- artifact1.py - Description
- artifact2.md - Description

### Permanent (user workspace)
- /home/workspace/path/to/file.py - Description

## Key Decisions

- Decision 1: Rationale
- Decision 2: Rationale

## Blockers

- Blocker 1: Description and potential resolution
```

---

## When to Update

**Update SESSION_STATE.md:**
- After completing significant tasks
- When creating new artifacts
- When making architectural decisions
- Every 3-5 exchanges minimum
- Before ending conversation

**Don't spam updates:**
- Not after every single message
- Not for trivial clarifications
- Use judgment - meaningful progress only

---

## State Management Scripts

### 1. Initialize State

```bash
python3 scripts/state_manager.py init --convo-id con_XXXXX --type build
```

Creates SESSION_STATE.md with:
- Conversation metadata
- Initial empty structure
- Timestamp

### 2. Update State

```bash
# Update focus
python3 scripts/state_manager.py update --field focus --value "Building API endpoints"

# Add completed task
python3 scripts/state_manager.py complete --task "Implemented user schema"

# Add artifact
python3 scripts/state_manager.py artifact --path "/home/workspace/api.py" --description "REST API implementation"
```

### 3. Check State

```bash
python3 scripts/state_manager.py status
```

Shows:
- Current focus
- Completion percentage
- Recent updates
- Active blockers

---

## Conversation Types

### Build
- **Focus:** System implementation
- **Track:** Components completed, tests passing
- **Artifacts:** Code, configs, docs

### Research
- **Focus:** Information gathering
- **Track:** Sources reviewed, insights extracted
- **Artifacts:** Notes, summaries, references

### Discussion
- **Focus:** Decision-making
- **Track:** Options explored, decisions made
- **Artifacts:** Decision records, action items

### Planning
- **Focus:** Strategy/architecture
- **Track:** Plans created, alternatives evaluated
- **Artifacts:** Design docs, proposals

---

## Integration with Workflows

### Close Conversation

The `close-conversation.md` prompt:
1. Reads SESSION_STATE.md
2. Generates summary based on state
3. Archives artifacts listed in state
4. Validates completion against objectives

### Build Orchestrator

Orchestrator uses state to:
- Track worker progress
- Validate deliverables
- Monitor blockers
- Report overall status

### Review Work

Debugger persona checks:
- Are stated objectives met?
- Do artifacts match state tracking?
- Are completion claims accurate (P15)?

---

## Best Practices

### DO:
✅ Update state after meaningful progress  
✅ Be specific about what's complete  
✅ Track all created artifacts  
✅ Document key decisions with rationale  
✅ Note blockers early

### DON'T:
❌ Claim tasks complete when they're 60% done (P15)  
❌ Forget to update state for hours  
❌ Leave artifacts section empty  
❌ Track trivial conversation details  
❌ Update state multiple times per message

---

## Artifact Classification

### Temporary
- Intermediate outputs
- Test files
- Scratch work
- Conversation-specific tools

**Action:** Stay in conversation workspace

### Permanent
- Production code
- Documentation
- Reusable workflows
- Knowledge artifacts

**Action:** Move to user workspace with proper location

---

## Schema

```yaml
conversation_id: string (required)
type: enum [build, research, discussion, planning] (required)
focus: string (1 sentence, updated frequently)
objective: string (detailed goal)
progress:
  completed: array of strings
  in_progress: array of strings
  pending: array of strings
artifacts:
  temporary: array of objects {path, description}
  permanent: array of objects {path, description}
topics_covered: array of strings
key_decisions: array of objects {decision, rationale}
blockers: array of objects {blocker, resolution}
```

---

## Example State File

```markdown
# Session State

**Conversation ID:** con_ABC123DEF456  
**Type:** build  
**Created:** 2025-11-03 08:00  
**Last Updated:** 2025-11-03 10:30

## Focus

Building user authentication API with JWT tokens

## Objective

Create complete authentication system with:
- User registration/login endpoints
- JWT token generation/validation
- Password hashing (bcrypt)
- Rate limiting
- Unit tests

## Progress

### Completed
- [x] Database schema (users table)
- [x] Password hashing utilities
- [x] JWT token generation
- [x] Registration endpoint

### In Progress
- [ ] Login endpoint (90% - needs rate limiting)

### Pending
- [ ] Token refresh endpoint
- [ ] Unit tests
- [ ] Documentation

## Topics Covered

- Security: bcrypt rounds (12), JWT secret rotation
- Architecture: Stateless auth, no sessions
- Testing: Pytest fixtures for auth testing

## Artifacts

### Temporary (conversation workspace)
- test_auth.py - Unit tests (draft)

### Permanent (user workspace)
- /home/workspace/api/auth.py - Auth endpoints
- /home/workspace/api/models/user.py - User model
- /home/workspace/api/utils/jwt.py - JWT utilities

## Key Decisions

- JWT over sessions: Stateless, scalable
- bcrypt rounds=12: Balance security/performance
- No email verification (Phase 2): Ship faster

## Blockers

None currently
```

---

## Related

- System: `build_orchestrator.md` - Multi-worker coordination
- Principles: P15 (Complete Before Claiming)
- Principles: P18 (State Verification)
- Prompt: `close-conversation.md` - Uses state for summary

---

**State management prevents memory loss and enables progress tracking across long conversations.**

*Last Updated: 2025-11-03*
