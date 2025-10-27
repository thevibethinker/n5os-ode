# Worker 1: Conversation-End Analysis Engine

**Orchestrator:** con_O4rpz6MPrQXLbOlX\
**Task ID:** W1-ANALYZER\
**Estimated Time:** 45 minutes\
**Dependencies:** None\
**Status:** Ready for Launch

---

## Mission

Build intelligent conversation workspace analyzer that classifies files, generates titles, and proposes file destinations.

---

## Context

Current conversation-end script makes immediate decisions without analysis or user review. We need an analysis phase that:

1. Scans conversation workspace intelligently
2. Classifies files by purpose (temp/final/deliverable)
3. Generates smart conversation titles
4. Proposes destinations with explanations
5. Detects conflicts and safety issues

This analyzer is the foundation - all other workers depend on its output format.

---

## Dependencies

**Files to Load:**

1. `file Knowledge/architectural/planning_prompt.md` (design values)
2. `file Knowledge/architectural/architectural_principles.md` (P5, P7, P19, P20)

**System Access:**

- Conversation workspace (read-only during analysis)
- SESSION_STATE.md (for title generation)
- AAR files (for context)

**No External Dependencies** - This is foundational worker

---

## Deliverables

### 1. Conversation Analyzer Script

**Path:** `file N5/scripts/conversation_end_analyzer.py`

**Must Include:**

- `ConversationAnalyzer` class
- File classification logic (temp/final/deliverable/ignore)
- Title generation from SESSION_STATE + AAR
- Destination mapping (intelligent routing)
- Conflict detection
- JSON output matching schema

### 2. JSON Schema

**Path:** `file N5/schemas/conversation-end-proposal.schema.json`

**Must Define:**

```json
{
  "conversation": {
    "id": "string",
    "proposed_title": "string",
    "title_source": "string",
    "workspace_path": "string"
  },
  "analysis": {
    "total_files": "number",
    "classified": {
      "deliverables": ["array"],
      "finals": ["array"],
      "temp": ["array"],
      "ignore": ["array"]
    },
    "conflicts": ["array"],
    "warnings": ["array"]
  },
  "proposed_actions": [{
    "action_type": "move|archive|delete|ignore",
    "source": "string",
    "destination": "string",
    "reason": "string",
    "confidence": "high|medium|low",
    "impacts": ["array"]
  }]
}
```

### 3. Test Suite

Embedded in script with `--test` flag:

- Test file classification (various patterns)
- Test title generation (with/without SESSION_STATE)
- Test destination mapping
- Test conflict detection
- Test JSON output validity

---

## Requirements

### File Classification Logic

**Deliverables** (move to user workspace):

- Starts with `DELIVERABLE_` or `FINAL_COMPLETION`
- [README.md](http://README.md), [SOLUTION.md](http://SOLUTION.md), [SUMMARY.md](http://SUMMARY.md) in root
- Files explicitly marked for delivery

**Finals** (move to Documents/ or Archive/):

- Starts with `FINAL_`, `COMPLETE_`, `SUMMARY_`
- `file .md` files with substantial content (&gt;500 chars)
- Documentation files

**Temp** (archive or delete):

- Starts with `TEMP_`, `DRAFT_`, `TEST_`, `SCRATCH_`
- Files with `_v1`, `_v2`, `_old`, `_backup` suffixes
- Small files (&lt;100 chars) unless code

**Ignore** (leave in place):

- SESSION_STATE.md
- [CONTEXT.md](http://CONTEXT.md), [INDEX.md](http://INDEX.md) (thread structure)
- Hidden files (`.git/`, `.cache/`)
- Python **pycache**

### Title Generation

**Priority Order:**

1. SESSION_STATE.md → `Objective` or `Focus` field
2. AAR file → `Title` or `Summary` section
3. Conversation workspace files → Most substantial `file .md` filename
4. Fallback → `"Conversation {date}"`

**Format:**

- Max 80 chars
- Use emojis from existing pattern (✅, 📰, 🗂️, etc.)
- Follow existing naming conventions

### Destination Mapping

```python
DESTINATION_RULES = {
    "deliverables": "/home/workspace/{appropriate-location}/",
    "finals": "/home/workspace/Documents/Archive/{YYYY-MM-DD}_{convo-id}/",
    "temp": "/home/workspace/Documents/Archive/{YYYY-MM-DD}_{convo-id}/scratch/",
    "ignore": "{original-location}"
}
```

Smart routing considers:

- File content/purpose
- Existing directory structure
- Related files (keep together)
- Conflict avoidance

### Conflict Detection

Flag conflicts when:

- Destination file already exists (P5)
- Multiple files want same destination
- Circular dependencies
- Permissions issues

### Safety Checks

Before proposing actions:

- [ ]  No overwrites without explicit user approval

- [ ]  All sources exist

- [ ]  All destinations are valid paths

- [ ]  No deletes of important files

- [ ]  Archive directories are writable

---

## Implementation Guide

### Script Structure

```python
#!/usr/bin/env python3
"""
Conversation-End Analysis Engine
Analyzes conversation workspace and generates action proposals
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

class ConversationAnalyzer:
    def __init__(self, workspace_path: Path, convo_id: str = None):
        self.workspace = Path(workspace_path)
        self.convo_id = convo_id or self._detect_convo_id()
        
    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return structured result"""
        try:
            files = self._scan_workspace()
            classified = self._classify_files(files)
            title = self._generate_title()
            actions = self._propose_actions(classified)
            conflicts = self._detect_conflicts(actions)
            
            return {
                "conversation": {
                    "id": self.convo_id,
                    "proposed_title": title,
                    "title_source": self._title_source,
                    "workspace_path": str(self.workspace)
                },
                "analysis": {
                    "total_files": len(files),
                    "classified": classified,
                    "conflicts": conflicts,
                    "warnings": []
                },
                "proposed_actions": actions
            }
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            raise
    
    def _scan_workspace(self) -> List[Path]:
        """Scan workspace, return all relevant files"""
        # Implement: recursive scan, exclude hidden, respect .gitignore
        pass
    
    def _classify_files(self, files: List[Path]) -> Dict[str, List[str]]:
        """Classify files into categories"""
        # Implement: classification logic from requirements
        pass
    
    def _generate_title(self) -> str:
        """Generate conversation title"""
        # Implement: title generation from SESSION_STATE/AAR/files
        pass
    
    def _propose_actions(self, classified: Dict) -> List[Dict[str, Any]]:
        """Generate proposed actions for each file"""
        # Implement: destination mapping with reasons
        pass
    
    def _detect_conflicts(self, actions: List[Dict]) -> List[Dict[str, str]]:
        """Detect conflicts in proposed actions"""
        # Implement: conflict detection (P5)
        pass

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=None, help="Workspace path")
    parser.add_argument("--convo-id", default=None, help="Conversation ID")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()
    
    if args.test:
        run_tests()
        return 0
    
    workspace = args.workspace or os.getenv("CONVERSATION_WORKSPACE")
    if not workspace:
        logger.error("No workspace specified")
        return 1
    
    analyzer = ConversationAnalyzer(workspace, args.convo_id)
    result = analyzer.analyze()
    
    output_file = args.output or "/tmp/conversation-analysis.json"
    Path(output_file).write_text(json.dumps(result, indent=2))
    logger.info(f"✓ Analysis complete: {output_file}")
    
    return 0

def run_tests():
    """Embedded test suite"""
    # Implement: classification tests, title tests, mapping tests
    pass

if __name__ == "__main__":
    sys.exit(main())
```

### Classification Patterns

```python
DELIVERABLE_PATTERNS = [
    r"^DELIVERABLE_",
    r"^FINAL_COMPLETION",
    r"README\.md$",
    r"SOLUTION\.md$",
    r"SUMMARY\.md$"
]

FINAL_PATTERNS = [
    r"^FINAL_",
    r"^COMPLETE_",
    r"^SUMMARY_",
    r".*_FINAL\.md$"
]

TEMP_PATTERNS = [
    r"^TEMP_",
    r"^DRAFT_",
    r"^TEST_",
    r"^SCRATCH_",
    r".*_v\d+\.",
    r".*_old\.",
    r".*_backup\."
]

IGNORE_PATTERNS = [
    r"SESSION_STATE\.md$",
    r"CONTEXT\.md$",
    r"INDEX\.md$",
    r"^\.",  # Hidden files
    r"__pycache__"
]
```

---

## Testing

### Test Cases

1. **File Classification**

   ```python
   # Test deliverable detection
   assert classify("DELIVERABLE_report.md") == "deliverable"
   assert classify("README.md") == "deliverable"
   
   # Test temp detection
   assert classify("TEMP_notes.md") == "temp"
   assert classify("draft_v3.py") == "temp"
   
   # Test ignore
   assert classify("SESSION_STATE.md") == "ignore"
   assert classify(".git/config") == "ignore"
   ```

2. **Title Generation**

   ```python
   # With SESSION_STATE
   assert generate_title_from_session_state() == "Expected Title"
   
   # From AAR
   assert generate_title_from_aar() == "AAR Title"
   
   # Fallback
   assert generate_title_fallback() == "Conversation 2025-10-27"
   ```

3. **Conflict Detection**

   ```python
   # Detect overwrite conflict
   actions = [{"destination": "/path/to/existing/file.md"}]
   conflicts = detect_conflicts(actions)
   assert len(conflicts) > 0
   ```

### Validation

```bash
# Run tests
python3 /home/workspace/N5/scripts/conversation_end_analyzer.py --test

# Test on current conversation
python3 /home/workspace/N5/scripts/conversation_end_analyzer.py \
  --workspace /home/.z/workspaces/con_O4rpz6MPrQXLbOlX \
  --convo-id con_O4rpz6MPrQXLbOlX \
  --output /tmp/analysis.json

# Validate JSON schema
cat /tmp/analysis.json | jq . > /dev/null && echo "✓ Valid JSON"

# Check classification accuracy
cat /tmp/analysis.json | jq '.analysis.classified'
```

---

## Report Back

When complete, report to orchestrator (con_O4rpz6MPrQXLbOlX):

✅ **Deliverables Created:**

1. `file N5/scripts/conversation_end_analyzer.py`
2. `file N5/schemas/conversation-end-proposal.schema.json`

✅ **Tests Passed:**

- File classification: \[results\]
- Title generation: \[results\]
- Conflict detection: \[results\]
- JSON schema validation: \[results\]

✅ **Ready for Next Phase:**

- Schema is stable and documented
- Output format is validated
- Worker 2 (Proposal Generator) can begin

**Conversation ID:** \[your worker conversation ID\]\
**Completion Time:** \[timestamp\]

---

## Architectural Principles Applied

- **P5 (Anti-Overwrite):** Conflict detection prevents overwrites
- **P7 (Dry-Run):** Analysis is read-only, no side effects
- **P19 (Error Handling):** Comprehensive try/except with logging
- **P20 (Modular):** Clean class structure, single responsibility
- **P22 (Language):** Python for data processing + LLM corpus

---

**Status:** Ready for Launch\
**Orchestrator Contact:** con_O4rpz6MPrQXLbOlX\
**Created:** 2025-10-27 03:36 ET