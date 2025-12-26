---
created: 2025-12-10
last_edited: 2025-12-10
version: 1.0
---

# Spawn Worker Analysis & Improvement Plan

## Problem Statement

The spawn_worker.py script produces worker assignments with empty "Parent Context" sections:
```markdown
## Parent Context

**What parent is working on:**  
Not specified

**Parent objective:**  
Not specified

**Parent status:**  
Not specified

**Parent conversation type:**  
Not specified
```

This happens even when the parent conversation has meaningful context available.

## Root Causes Identified

### 1. Field Name Mismatch
**SESSION_STATE.md uses:**
- `**Type:** Build`
- `**Mode:** general`
- `**Focus:** TBD`

**spawn_worker.py looks for:**
- `**Primary Type:**` (doesn't exist)
- `**Focus:**` (matches but gets "TBD")
- `**Objective:**` (matches but gets "TBD")

### 2. Placeholder Values Not Properly Handled
When SESSION_STATE has `TBD` values, the script reports "Not specified" but doesn't extract the actually useful information that IS present, like the **Progress:** field.

### 3. Progress Field Contains Real Information But Is Ignored
The parent SESSION_STATE has:
```
- **Progress:** Complete: Database, CLI, 5 adaptive conversational reflection prompts (morning pages, evening, weekly, gratitude, temptation)
```
This is the BEST context available but is completely ignored!

### 4. Inferred Context Is Too Generic
The workspace inference produces generic output like "Configuration/data work" and file type analysis, missing semantic understanding of what the parent is actually doing.

## Recommended Fixes

### Fix 1: Multi-Source Field Extraction
Extract from multiple possible field names:

```python
def _extract_field_multi(self, content: str, field_names: list) -> str:
    """Try multiple field names, return first non-TBD match."""
    for field in field_names:
        pattern = rf"^\*\*{re.escape(field)}:\*\*\s*(.+)$"
        for line in content.split("\n"):
            m = re.match(pattern, line.strip())
            if m:
                val = self._clean_value(m.group(1))
                if val and val.upper() != "TBD":
                    return val
    return "Not specified"

# Usage:
focus = self._extract_field_multi(content, ["Focus", "Working On", "Topic"])
conv_type = self._extract_field_multi(content, ["Primary Type", "Type", "Conversation Type"])
```

### Fix 2: Extract Progress Field
Always extract **Progress:** as rich context since it often contains the best summary:

```python
def _extract_progress(self, content: str) -> str:
    """Extract Progress field which often has the best context."""
    pattern = r"^\*\*Progress:\*\*\s*(.+)$"
    for line in content.split("\n"):
        m = re.match(pattern, line.strip())
        if m:
            val = self._clean_value(m.group(1))
            if val and val.upper() != "TBD":
                return val
    return ""
```

### Fix 3: Read Recent Markdown Files for Semantic Context
When SESSION_STATE has placeholders, read the first few hundred characters of recent .md files in the workspace to get actual semantic context:

```python
def _read_workspace_context(self) -> str:
    """Read recent markdown files to get semantic understanding."""
    md_files = sorted(
        self.parent_workspace.glob("**/*.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )[:5]
    
    context_snippets = []
    for f in md_files:
        if "SESSION_STATE" in f.name:
            continue
        try:
            content = f.read_text()[:500]
            context_snippets.append(f"### {f.name}\n{content}...")
        except:
            pass
    
    return "\n\n".join(context_snippets)
```

### Fix 4: Pass Instruction Context Back to Worker
When spawning with an instruction, that instruction itself often contains the best context about what the parent is working on. Parse it and include it.

### Fix 5: Better Output Format
Instead of just "Not specified", show what WAS found:

```markdown
## Parent Context

**What parent is working on:**  
[From Progress: Complete: Database, CLI, 5 adaptive conversational reflection prompts]

**Parent objective:**  
Not explicitly set in SESSION_STATE

**Parent status:**  
active (build phase)

**Parent conversation type:**  
Build
```

## build_orchestrator.py Issues

The build_orchestrator.py is quite basic and could use improvements:

1. **No Context Passing** - Workers get just a description string, not the full parent context
2. **No Progress Tracking Integration** - STATUS updates aren't tied to SESSION_STATE
3. **No Worker Communication Protocol** - No standard way for workers to report back
4. **Hardcoded for One Project** - The Content Library build is hardcoded

### Recommended Improvements:

1. **Generalize to Any Project**
2. **Integrate with spawn_worker.py** for actual thread spawning
3. **Add worker status webhook/file-based updates**
4. **Connect to conversation-end workflow**

## Next Steps

1. [ ] Fix spawn_worker.py field extraction (Fix 1-3)
2. [ ] Add Progress field extraction (Fix 2)
3. [ ] Improve inferred context (Fix 3)
4. [ ] Update build_orchestrator.py to use spawn_worker.py
5. [ ] Add integration tests


