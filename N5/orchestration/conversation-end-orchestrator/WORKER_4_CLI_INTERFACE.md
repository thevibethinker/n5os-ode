# Worker 4: CLI Interface & Orchestrator

**Orchestrator:** con_O4rpz6MPrQXLbOlX  
**Task ID:** W4-CLI  
**Estimated Time:** 30 minutes  
**Dependencies:** Workers 1, 2, 3 (all components)  
**Status:** Waiting for W1-W3

---

## Mission

Update `n5_conversation_end.py` to orchestrate analyzer → proposal → executor workflow with multiple interaction modes.

---

## Context

Now that we have modular components (analyzer, proposal generator, executor), we need the orchestrator script that:
1. Calls components in sequence
2. Displays proposals to user
3. Handles approval/selection
4. Supports multiple modes (interactive, auto, email)
5. Maintains backward compatibility where possible

---

## Dependencies

**Must Have:**
1. `/home/workspace/N5/scripts/conversation_end_analyzer.py` (W1)
2. `/home/workspace/N5/scripts/conversation_end_proposal.py` (W2)
3. `/home/workspace/N5/scripts/conversation_end_executor.py` (W3)

**Load:**
1. `file 'N5/prefs/operations/conversation-end-cleanup-protocol.md'`

---

## Deliverables

**Path:** `/home/workspace/N5/scripts/n5_conversation_end.py` (updated)

**New Modes:**
- Interactive: Show proposal, accept selections
- Auto: Use defaults, execute immediately
- Email: Generate proposal, email to V, await response
- Dry-run: Show what would happen

---

## Requirements

### CLI Flow

```
1. Parse args (--auto, --email, --dry-run)
2. Run analyzer → get analysis JSON
3. Run proposal generator → get proposal
4. Display proposal to user
5. If interactive: accept user input
6. If auto: approve all with confidence >medium
7. If email: send proposal, exit (separate approval workflow)
8. Run executor with approved actions
9. Display results
```

### Interactive Mode UI

```bash
# Clean, colorful display
================================================
Conversation End Proposal
================================================

Title: Oct 27 | ✅ Orchestrator Audit Plan

Actions (select with space, Enter to confirm):

Deliverables (5):
  [✓] 1. FINAL_COMPLETION.md → Documents/Archive/2025-10-27.../
  [✓] 2. README.md → Documents/Archive/2025-10-27.../
  [✓] 3. SUMMARY.md → Documents/Archive/2025-10-27.../

Temporary (3):
  [ ] 4. TEMP_notes.md → Archive/.../scratch/
  [✓] 5. draft_v2.py → Archive/.../scratch/

Conflicts:
  ⚠️  FINAL_SUMMARY.md already exists
      Options: [R]ename | [S]kip | [O]verwrite
      Your choice: 

Enter selections (space-separated, or 'all'): all
Confirm? (Y/n): 
```

### Auto Mode Behavior

```python
def auto_approve(actions: List[Dict]) -> List[Dict]:
    """
    Auto-approve actions with:
    - confidence == "high"
    - action_type in ["move", "archive", "ignore"]
    - No conflicts
    
    Skip:
    - confidence == "low"
    - action_type == "delete"
    - Has conflicts
    """
    approved = []
    for action in actions:
        if (action["confidence"] == "high" and 
            action["action_type"] != "delete" and
            not action.get("conflict")):
            action["approved"] = True
            approved.append(action)
    return approved
```

### Email Mode

```python
def email_proposal(proposal_md: str, proposal_json: Path):
    """
    Email proposal to V for approval
    """
    # 1. Generate email with proposal markdown
    # 2. Include approval link or reply format
    # 3. Save proposal JSON for later execution
    # 4. Send email
    # 5. Exit (execution happens when V replies)
```

---

## Implementation Pattern

```python
#!/usr/bin/env python3
"""
N5 Conversation End Orchestrator
Coordinates analysis → proposal → execution workflow
"""

import sys
import json
import logging
import argparse
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main():
    args = parse_args()
    
    # Phase 1: Analysis
    logger.info("Phase 1: Analyzing conversation workspace...")
    analysis_json = run_analyzer(args.workspace, args.convo_id)
    if not analysis_json:
        logger.error("Analysis failed")
        return 1
    
    # Phase 2: Proposal Generation
    logger.info("Phase 2: Generating proposal...")
    proposal_md, proposal_json = generate_proposal(analysis_json, args.format)
    
    # Phase 3: User Interaction (mode-dependent)
    if args.email:
        send_proposal_email(proposal_md, proposal_json)
        logger.info("✓ Proposal emailed, awaiting approval")
        return 0
    
    if args.auto:
        approved_proposal = auto_approve_proposal(proposal_json)
    else:
        # Interactive
        display_proposal(proposal_md)
        approved_proposal = get_user_selections(proposal_json)
    
    # Phase 4: Execution
    logger.info("Phase 3: Executing approved actions...")
    success = execute_proposal(approved_proposal, dry_run=args.dry_run)
    
    if success:
        logger.info("✓ Conversation-end complete")
        return 0
    else:
        logger.error("❌ Execution failed")
        return 1

def run_analyzer(workspace: str, convo_id: str) -> Path:
    """Run analyzer, return path to analysis JSON"""
    cmd = [
        sys.executable,
        "/home/workspace/N5/scripts/conversation_end_analyzer.py",
        "--workspace", workspace,
        "--convo-id", convo_id,
        "--output", "/tmp/conversation-analysis.json"
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        logger.error(f"Analyzer failed: {result.stderr}")
        return None
    return Path("/tmp/conversation-analysis.json")

def generate_proposal(analysis_json: Path, format_type: str) -> tuple:
    """Generate proposal, return (markdown_str, json_path)"""
    # Call conversation_end_proposal.py
    pass

def display_proposal(proposal_md: str):
    """Display proposal in terminal"""
    print("\n" + "="*70)
    print(proposal_md)
    print("="*70 + "\n")

def get_user_selections(proposal_json: Path) -> Path:
    """Interactive selection, return modified proposal with approvals"""
    # Show checkboxes, accept input, update JSON
    pass

def auto_approve_proposal(proposal_json: Path) -> Path:
    """Auto-approve based on confidence rules"""
    pass

def send_proposal_email(proposal_md: str, proposal_json: Path):
    """Email proposal to V"""
    # Use send_email_to_user tool
    pass

def execute_proposal(proposal_json: Path, dry_run: bool) -> bool:
    """Execute approved actions via executor"""
    cmd = [
        sys.executable,
        "/home/workspace/N5/scripts/conversation_end_executor.py",
        "--proposal", str(proposal_json)
    ]
    if dry_run:
        cmd.append("--dry-run")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Auto mode")
    parser.add_argument("--email", action="store_true", help="Email proposal mode")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run")
    parser.add_argument("--workspace", help="Conversation workspace")
    parser.add_argument("--convo-id", help="Conversation ID")
    return parser.parse_args()

if __name__ == "__main__":
    sys.exit(main())
```

---

## Report Back

✅ Script updated and tested  
✅ All modes working (interactive, auto, email, dry-run)  
✅ Backward compatible  
✅ Ready for W5 integration testing  

**Conv ID:** [your_id]  
**Completed:** [timestamp]

---

**Created:** 2025-10-27 03:42 ET  
**Orchestrator:** con_O4rpz6MPrQXLbOlX
