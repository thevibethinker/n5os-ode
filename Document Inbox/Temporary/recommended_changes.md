# Recommended System Changes
**Date:** 2025-10-20  
**Purpose:** Prevent future protocol bypass incidents

---

## Change 1: Add Reflection Protocol Conditional Rule

**File:** `N5/prefs/prefs.md`  
**Location:** After "Command-First Operations" section (around line 48)

**Add:**

```markdown
### Reflection Processing
**When email subject contains "reflection-ingest", "[Reflect]", or "reflection-pipeline" OR when processing voice reflections:**

1. STOP and load `file 'N5/commands/reflection-ingest.md'`
2. Check for email attachments in conversation workspace (`/home/.z/workspaces/*/email_attachment/`)
3. Stage files to `N5/records/reflections/incoming/`:
   - For text files (.txt, .md): Create `.transcript.jsonl` wrapper if needed
   - For audio files: Use transcribe_audio tool first
4. Execute: `python3 /home/workspace/N5/scripts/reflection_ingest.py`
5. Follow established approval workflow
6. **DO NOT improvise alternate analysis approaches**

**Rationale:** Reflections have established pipeline with registry, approval workflow, and synthesis protocols. Bypassing creates inconsistency and loses system benefits.
```

---

## Change 2: Broaden Command-First Rule

**File:** `N5/prefs/prefs.md`  
**Location:** Update existing "Command-First Operations" section

**Current:**
```markdown
### Command-First Operations
**CRITICAL:** Always check for registered commands...
**Specific Rules:**
- Thread closure
- Thread exports
- System operations
```

**Proposed:**
```markdown
### Command-First Operations
**CRITICAL:** Before ANY workflow-related operation, check for registered commands in `file 'N5/config/commands.jsonl'` OR search `N5/commands/*.md` for relevant protocols.

**Scope:** System operations, content processing, knowledge management, reflections, automation, scheduled tasks, integrations, etc.

**Priority order:**
1. Registered command in commands.jsonl
2. Protocol documentation in N5/commands/
3. Manual script execution
4. Direct file operations
5. Improvisation (last resort after confirming no protocol exists)

**Specific Rules:**
[... existing rules ...]
- **Reflections:** Subject "reflection-ingest" or "[Reflect]" → `reflection-ingest` command
- **Content workflows:** Always search N5/commands/ before creating ad-hoc processes
```

---

## Change 3: Update reflection-ingest.md Documentation

**File:** `N5/commands/reflection-ingest.md`  
**Location:** Add new section after "Sources"

**Add:**

```markdown
## Email-Triggered Invocation (For AI)

When V emails Zo with subject containing "reflection-ingest" or "[Reflect]":

### Workflow

1. **Locate attachment**: Check conversation workspace at `/home/.z/workspaces/con_zHxCoEAM2bJfYMpJ/email_attachment/` (or current conversation ID)

2. **Stage file**: Copy to `N5/records/reflections/incoming/` with descriptive, datestamped filename:
   ```bash
   cp "/home/.z/workspaces/[CONVO_ID]/email_attachment/[file]" \
      "/home/workspace/N5/records/reflections/incoming/YYYY-MM-DD_descriptive-name.ext"
   ```

3. **Handle text transcripts**: If file is .txt/.md (already transcribed), create `.transcript.jsonl` wrapper:
   ```python
   import json
   from pathlib import Path
   
   txt_file = Path("path/to/file.txt")
   transcript_file = Path(str(txt_file) + ".transcript.jsonl")
   
   transcript_data = {
       "text": txt_file.read_text(),
       "source_file": str(txt_file),
       "mime_type": "text/plain"
   }
   
   transcript_file.write_text(json.dumps(transcript_data))
   ```

4. **Handle audio files**: Use Zo's `transcribe_audio` tool before running pipeline

5. **Run pipeline**: 
   ```bash
   python3 /home/workspace/N5/scripts/reflection_ingest.py
   ```

6. **Synthesize content**: Don't leave placeholders—create actual summary and analysis from reflection content

7. **Follow approval workflow**: System creates registry entry with status `awaiting-approval`. V selects desired outputs.

### DO NOT

- Create ad-hoc analysis documents in conversation workspace
- Manually add items to lists before approval workflow
- Skip the reflection pipeline and improvise alternate processing
- Leave placeholder content in summary/detail files

### Rationale

The reflection pipeline provides:
- Consistent processing and classification
- Registry tracking with approval workflow
- Standardized output formats
- Integration with knowledge management
- Audit trail of processed reflections
```

---

## Change 4: Enhance reflection_worker.py

**File:** `N5/scripts/reflection_worker.py`  
**Purpose:** Handle text files natively without requiring audio

**Changes needed:**

1. Detect file type (audio vs. text)
2. If text file, auto-create transcript.jsonl if missing
3. Update docstring to document text file support

**Implementation:**

```python
def transcribe(file_path: Path) -> Path:
    """Transcribe audio file or wrap text file. Handles both audio and text reflections."""
    out = Path(str(file_path) + ".transcript.jsonl")
    if out.exists():
        logger.info(f"✓ Transcript found: {out}")
        return out
    
    # Handle text files
    if file_path.suffix.lower() in {'.txt', '.md'}:
        logger.info(f"Text file detected, creating transcript wrapper")
        transcript_data = {
            "text": file_path.read_text(),
            "source_file": str(file_path),
            "mime_type": "text/plain"
        }
        out.write_text(json.dumps(transcript_data))
        return out
    
    # Handle audio files (existing logic)
    logger.error(f"Missing transcript: {out}")
    logger.error("Run: transcribe_audio tool on this file first")
    raise FileNotFoundError(f"Transcript required: {out}")
```

---

## Summary of Benefits

**Prevents:**
- AI bypassing established workflows
- Creating duplicate/inconsistent outputs
- Loss of system audit trail and registry
- Violating SSOT principle

**Ensures:**
- Consistent processing via registered protocols
- Proper approval workflows followed
- Knowledge integration happens correctly
- System benefits (registry, tracking, synthesis) are utilized

**Makes explicit:**
- Email subjects as protocol triggers
- Command-first applies to ALL workflows
- Text vs. audio handling in reflection system
- Improvisation is last resort, not first choice

---

## Implementation Priority

1. **Immediate:** Add reflection conditional rule to prefs.md (prevents recurrence)
2. **High:** Broaden command-first rule (systemic fix)
3. **Medium:** Update reflection-ingest.md (documentation/training)
4. **Medium:** Enhance reflection_worker.py (technical improvement)

---

**Request:** Review and approve changes, or provide feedback for revision.
