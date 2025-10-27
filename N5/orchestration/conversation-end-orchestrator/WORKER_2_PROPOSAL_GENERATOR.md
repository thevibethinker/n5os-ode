# Worker 2: Proposal Generator

**Orchestrator:** con_O4rpz6MPrQXLbOlX  
**Task ID:** W2-PROPOSAL  
**Estimated Time:** 30 minutes  
**Dependencies:** Worker 1 (analyzer + schema)  
**Status:** Waiting for W1

---

## Mission

Transform analysis JSON into human-readable proposal with clear explanations and grouping.

---

## Context

Analyzer produces structured data. We need to transform it into a format that's easy for humans to review and approve. This includes:
- Clear visual hierarchy
- Grouped actions (by type, by destination)
- Explanations for each proposed action
- Impact preview
- Approval UI elements

---

## Dependencies

**Must Have:**
1. `/home/workspace/N5/scripts/conversation_end_analyzer.py` (from W1)
2. `/home/workspace/N5/schemas/conversation-end-proposal.schema.json` (from W1)

**Load for Context:**
1. `file 'N5/prefs/operations/conversation-end-cleanup-protocol.md'` (existing protocol)

---

## Deliverables

### 1. Proposal Generator Script
**Path:** `/home/workspace/N5/scripts/conversation_end_proposal.py`

**Functions:**
- Read analysis JSON (from W1)
- Generate human-readable markdown proposal
- Generate interactive selection UI (for terminal)
- Support --format (markdown|json|interactive)

### 2. Example Proposal Output
**Generated automatically** to demonstrate format

---

## Requirements

### Proposal Format (Markdown)

```markdown
# Conversation End Proposal

**Conversation:** con_XXXXX  
**Generated:** 2025-10-27 03:40 ET  

---

## Proposed Title

**✓ "Oct 27 | ✅ System Work Name"**

*Source: SESSION_STATE.md (Objective field)*

---

## Summary

- **Total Files:** 15
- **To Move:** 9
- **To Archive:** 4
- **To Ignore:** 2

---

## Actions

### 1. Deliverables → User Workspace (5 files)

**✓ FINAL_COMPLETION.md**
  → `/home/workspace/Documents/Archive/2025-10-27_con-O4rpz6MPrQXLbOlX/`
  *Reason: Final deliverable, substantial content (2.3 KB)*
  *Impact: Permanent archival*

**✓ README.md**
  → `/home/workspace/Documents/Archive/2025-10-27_con-O4rpz6MPrQXLbOlX/`
  *Reason: Documentation for this conversation*

[... more files ...]

### 2. Temporary Files → Archive (4 files)

**✓ TEMP_analysis.md**
  → `/home/workspace/Documents/Archive/2025-10-27_con-O4rpz6MPrQXLbOlX/scratch/`
  *Reason: Temporary working file*

[... more files ...]

### 3. Ignore (2 files)

**SESSION_STATE.md**
  *Reason: System file, keep in conversation workspace*

**CONTEXT.md**
  *Reason: Thread structure file*

---

## Conflicts

⚠️ **1 conflict detected:**

**FINAL_SUMMARY.md** → `/home/workspace/Documents/FINAL_SUMMARY.md`
  *Conflict: File already exists at destination*
  *Options:*
    - Rename to FINAL_SUMMARY_2025-10-27.md
    - Skip this action
    - Overwrite (not recommended)

---

## Review

Please review actions above. In interactive mode, you can select which actions to approve.

**Dry-Run Command:**
```bash
python3 N5/scripts/conversation_end_executor.py --proposal /tmp/proposal.json --dry-run
```
```

### Interactive UI (Terminal)

For terminal interaction, show checkboxes:

```
Actions to Execute:
  
[✓] 1. Move FINAL_COMPLETION.md → Documents/Archive/2025-10-27_.../
[✓] 2. Move README.md → Documents/Archive/2025-10-27_.../
[ ] 3. Archive TEMP_analysis.md → Archive/.../scratch/
[✓] 4. Ignore SESSION_STATE.md

Enter selection (1-4, space-separated, or 'all'): 
```

---

## Implementation Guide

### Class Structure

```python
#!/usr/bin/env python3
"""
Conversation-End Proposal Generator
Transforms analysis JSON into human-readable proposals
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

class ProposalGenerator:
    def __init__(self, analysis_path: Path):
        self.analysis = json.loads(Path(analysis_path).read_text())
        
    def generate_markdown(self) -> str:
        """Generate human-readable markdown proposal"""
        sections = [
            self._header(),
            self._title_section(),
            self._summary(),
            self._actions_by_type(),
            self._conflicts(),
            self._review_footer()
        ]
        return "\n\n".join(sections)
    
    def generate_json(self) -> str:
        """Generate executable JSON proposal"""
        # Add approval flags, execution metadata
        pass
    
    def generate_interactive(self) -> str:
        """Generate terminal UI for interactive selection"""
        # Terminal-friendly checkbox format
        pass
    
    def _header(self) -> str:
        """Generate header section"""
        pass
    
    def _title_section(self) -> str:
        """Generate title proposal"""
        pass
    
    def _summary(self) -> str:
        """Generate summary stats"""
        pass
    
    def _actions_by_type(self) -> str:
        """Group and format actions"""
        # Group by: deliverables, finals, temp, ignore
        pass
    
    def _conflicts(self) -> str:
        """Format conflicts with resolution options"""
        pass
    
    def _review_footer(self) -> str:
        """Add review instructions"""
        pass

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", required=True, help="Analysis JSON from W1")
    parser.add_argument("--format", choices=["markdown", "json", "interactive"], default="markdown")
    parser.add_argument("--output", default=None, help="Output file")
    parser.add_argument("--demo", action="store_true", help="Generate demo proposal")
    args = parser.parse_args()
    
    if args.demo:
        # Generate demo with mock data
        generate_demo()
        return 0
    
    generator = ProposalGenerator(args.analysis)
    
    if args.format == "markdown":
        output = generator.generate_markdown()
    elif args.format == "json":
        output = generator.generate_json()
    else:
        output = generator.generate_interactive()
    
    if args.output:
        Path(args.output).write_text(output)
        logger.info(f"✓ Proposal written: {args.output}")
    else:
        print(output)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

---

## Testing

### Test Case 1: Basic Proposal
```bash
# Create mock analysis
echo '{"conversation":{"id":"con_TEST"},"analysis":{"total_files":5,"classified":{"deliverables":["FINAL.md"],"temp":["TEMP.md"]}},"proposed_actions":[]}' > /tmp/test-analysis.json

# Generate proposal
python3 /home/workspace/N5/scripts/conversation_end_proposal.py \
  --analysis /tmp/test-analysis.json \
  --format markdown

# Should produce readable output
```

### Test Case 2: With Conflicts
```bash
# Analysis with conflicts
# Generate and verify conflict section appears
```

### Test Case 3: Interactive UI
```bash
python3 /home/workspace/N5/scripts/conversation_end_proposal.py \
  --analysis /tmp/test-analysis.json \
  --format interactive
```

---

## Report Back

When complete, report to orchestrator (con_O4rpz6MPrQXLbOlX):

✅ **Deliverables Created:**
1. `/home/workspace/N5/scripts/conversation_end_proposal.py`

✅ **Tests Passed:**
- Markdown format generation: [pass/fail]
- JSON format generation: [pass/fail]
- Interactive format generation: [pass/fail]
- Demo generation: [pass/fail]

✅ **Ready for Next Phase:**
- Proposal format is validated
- Worker 3 (Executor) can use JSON output
- Worker 4 (CLI) can use markdown + interactive

**Conversation ID:** [your worker conversation ID]  
**Completion Time:** [timestamp]

---

**Status:** Ready for Launch (after W1 completes)  
**Orchestrator Contact:** con_O4rpz6MPrQXLbOlX  
**Created:** 2025-10-27 03:38 ET
