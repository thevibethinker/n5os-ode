---
created: 2025-12-10
last_edited: 2025-12-10
version: 1.0
---

# Spawn Worker v2 - LLM-First Design

## Core Insight

**The LLM already has all the context.** The current design inverts responsibility:
- ❌ Script tries to parse/infer context → Fails with regex on messy data
- ✅ LLM provides rich context → Script just handles file mechanics

## New Design

### Invocation Pattern

Instead of:
```bash
python3 spawn_worker.py --parent con_XXX --instruction "Do the thing"
```

The LLM provides the context directly:
```bash
python3 spawn_worker.py \
    --parent con_XXX \
    --instruction "Research OAuth2 alternatives" \
    --parent-focus "Building authentication system for N5 services" \
    --parent-objective "Implement secure, user-friendly auth with SSO support" \
    --parent-status "Database schema complete, starting OAuth integration" \
    --parent-type "build"
```

Or even better - JSON input for complex context:
```bash
python3 spawn_worker.py --parent con_XXX --context-json '{
    "instruction": "Research OAuth2 alternatives",
    "parent_context": {
        "focus": "Building authentication system for N5 services",
        "objective": "Implement secure, user-friendly auth with SSO support", 
        "status": "Database schema complete, starting OAuth integration",
        "type": "build",
        "key_decisions": [
            "Using SQLite for credential storage",
            "JWT tokens for session management"
        ],
        "relevant_files": [
            "N5/services/auth/schema.sql",
            "N5/services/auth/README.md"
        ]
    }
}'
```

### Script Responsibilities (Minimal)

The script ONLY does:
1. Generate timestamp/ID
2. Create worker assignment file from template + LLM-provided context
3. Update parent SESSION_STATE with worker reference
4. Create worker_updates/ directory
5. Return file path

The script does NOT:
- Parse SESSION_STATE
- Infer context from file analysis
- Use regex to extract anything semantic

### Template

```markdown
# Worker Assignment - Parallel Thread

**Generated:** {{timestamp}}
**Parent Conversation:** {{parent_id}}
**Worker ID:** {{worker_id}}

---

## Your Mission

{{instruction}}

---

## Parent Context

**What parent is working on:**  
{{parent_focus}}

**Parent objective:**  
{{parent_objective}}

**Parent status:**  
{{parent_status}}

**Parent conversation type:**  
{{parent_type}}

{{#if key_decisions}}
**Key decisions already made:**
{{#each key_decisions}}
- {{this}}
{{/each}}
{{/if}}

{{#if relevant_files}}
**Relevant files:**
{{#each relevant_files}}
- `{{this}}`
{{/each}}
{{/if}}

---

## Communication Protocol

[standard boilerplate]
```

### When LLM Doesn't Have Context

For "agnostic" spawns where the LLM hasn't been told what the parent is doing:
1. LLM reads SESSION_STATE.md itself
2. LLM reads recent workspace files
3. LLM synthesizes context
4. LLM provides that context to the script

This keeps the semantic understanding in the LLM, not in regex patterns.

## Alternative: Pure Prompt-Based Spawning

Even simpler - no script at all for the context part:

### Prompt: Spawn Worker

When I need to spawn a worker:

1. **I create the worker assignment file directly** with full context
2. **I update SESSION_STATE** with worker reference
3. **I tell user** to open it in new conversation

The "script" becomes just a helper for generating timestamps/IDs:
```bash
# Just get IDs
python3 spawn_worker.py --generate-ids --parent con_XXX
# Output: {"worker_id": "WORKER_Kenj_20251211", "timestamp": "2025-12-11T03:38:49Z", "output_path": "Records/Temporary/WORKER_ASSIGNMENT_...md"}
```

Then I write the file with my own semantic understanding.

## Recommendation

**Option B (Pure Prompt-Based)** is cleaner because:
1. All semantic work stays with the LLM
2. Script is trivial (just ID generation)
3. No impedance mismatch between script expectations and actual data
4. Works regardless of SESSION_STATE format changes
5. Leverages what LLMs are good at (understanding context)

## Migration Path

1. Keep spawn_worker.py for backwards compatibility
2. Add `--llm-provided` flag that just takes all context as args
3. Update Spawn Worker prompt to have LLM provide context
4. Eventually deprecate auto-extraction mode


