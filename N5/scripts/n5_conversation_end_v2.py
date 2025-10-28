#!/usr/bin/env python3
"""
N5 Conversation End Orchestrator (v2)
Coordinates analysis → proposal → execution workflow with multiple interaction modes

Orchestrates modular components:
- W1: conversation_end_analyzer.py
- W2: conversation_end_proposal.py  
- W3: conversation_end_executor.py
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
SCRIPTS_DIR = WORKSPACE / "N5/scripts"

# Detect conversation workspace
CONVERSATION_WS_ENV = os.getenv("CONVERSATION_WORKSPACE")
if CONVERSATION_WS_ENV:
    CONVERSATION_WS = Path(CONVERSATION_WS_ENV)
else:
    workspaces_dir = Path("/home/.z/workspaces")
    if workspaces_dir.exists():
        workspaces = [d for d in workspaces_dir.iterdir() if d.is_dir() and d.name.startswith("con_")]
        if workspaces:
            CONVERSATION_WS = max(workspaces, key=lambda d: d.stat().st_mtime)
        else:
            CONVERSATION_WS = None
    else:
        CONVERSATION_WS = None


def run_analyzer(workspace: Path, convo_id: str) -> Path:
    """
    Run analyzer (W1), return path to analysis JSON
    
    Returns: Path to analysis JSON or None on failure
    """
    logger.info("Phase 1: Analyzing conversation workspace...")
    
    output_path = Path("/tmp/conversation-analysis.json")
    
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "conversation_end_analyzer.py"),
        "--workspace", str(workspace),
        "--convo-id", convo_id,
        "--output", str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if output_path.exists() and output_path.stat().st_size > 0:
            logger.info(f"✓ Analysis complete: {output_path}")
            return output_path
        else:
            logger.error("❌ Analyzer produced no output")
            return None
            
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Analyzer failed: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"❌ Analyzer error: {e}")
        return None


def generate_proposal(analysis_json: Path, format_type: str = "markdown") -> tuple:
    """
    Generate proposal (W2), return (markdown_str, json_path)
    
    Returns: (proposal_markdown, proposal_json_path) or (None, None) on failure
    """
    logger.info("Phase 2: Generating proposal...")
    
    # Generate both markdown (for display) and JSON (for execution)
    proposal_md_path = Path("/tmp/conversation-proposal.md")
    proposal_json_path = Path("/tmp/conversation-proposal.json")
    
    # Generate markdown
    cmd_md = [
        sys.executable,
        str(SCRIPTS_DIR / "conversation_end_proposal.py"),
        "--analysis", str(analysis_json),
        "--format", "markdown",
        "--output", str(proposal_md_path)
    ]
    
    # Generate JSON
    cmd_json = [
        sys.executable,
        str(SCRIPTS_DIR / "conversation_end_proposal.py"),
        "--analysis", str(analysis_json),
        "--format", "json",
        "--output", str(proposal_json_path)
    ]
    
    try:
        # Generate markdown
        subprocess.run(cmd_md, capture_output=True, text=True, check=True)
        
        # Generate JSON
        subprocess.run(cmd_json, capture_output=True, text=True, check=True)
        
        if not proposal_md_path.exists():
            logger.error("❌ Proposal markdown not generated")
            return (None, None)
            
        if not proposal_json_path.exists():
            logger.error("❌ Proposal JSON not generated")
            return (None, None)
        
        proposal_md = proposal_md_path.read_text()
        logger.info(f"✓ Proposal generated ({len(proposal_md)} chars)")
        
        return (proposal_md, proposal_json_path)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Proposal generation failed: {e.stderr}")
        return (None, None)
    except Exception as e:
        logger.error(f"❌ Proposal generation error: {e}")
        return (None, None)


def display_proposal(proposal_md: str):
    """Display proposal in terminal with formatting"""
    print("\n" + "="*70)
    print(proposal_md)
    print("="*70 + "\n")


def get_user_selections(proposal_json: Path) -> Path:
    """
    Interactive selection mode - show proposal and accept user input
    
    Returns: Modified proposal JSON with approval flags
    """
    # Load proposal
    proposal_data = json.loads(proposal_json.read_text())
    
    # Extract actions
    actions = proposal_data.get("proposed_actions", [])
    
    if not actions:
        logger.info("No actions to approve")
        return proposal_json
    
    # Simple selection UI
    print("\n" + "="*70)
    print("ACTION SELECTION")
    print("="*70)
    print("\nEnter action numbers to approve (space-separated), or 'all':")
    print("Example: 1 2 5  (or 'all' for all actions)\n")
    
    for idx, action in enumerate(actions, 1):
        file_path = action.get("file_path", "unknown")
        action_type = action.get("action_type", "unknown")
        dest = action.get("destination", "N/A")
        reason = action.get("reason", "")
        
        print(f"  [{idx}] {action_type.upper()}: {file_path}")
        if dest != "N/A":
            print(f"      → {dest}")
        print(f"      Reason: {reason}")
        print()
    
    # Get user input
    selection = input("> ").strip().lower()
    
    if selection == "all":
        # Approve all
        for action in actions:
            action["approved"] = True
        logger.info(f"✓ Approved all {len(actions)} actions")
    else:
        # Parse selections
        try:
            selected_indices = [int(x) for x in selection.split()]
            approved_count = 0
            
            for idx in selected_indices:
                if 1 <= idx <= len(actions):
                    actions[idx - 1]["approved"] = True
                    approved_count += 1
                else:
                    logger.warning(f"Invalid index: {idx}")
            
            logger.info(f"✓ Approved {approved_count}/{len(actions)} actions")
            
        except ValueError:
            logger.error("❌ Invalid input format")
            return None
    
    # Write updated proposal
    updated_proposal_path = Path("/tmp/conversation-proposal-approved.json")
    proposal_data["proposed_actions"] = actions
    updated_proposal_path.write_text(json.dumps(proposal_data, indent=2))
    
    return updated_proposal_path


def auto_approve_proposal(proposal_json: Path) -> Path:
    """
    Auto-approve based on confidence rules
    
    Auto-approve actions with:
    - confidence == "high"
    - action_type in ["move", "archive", "ignore"]
    - No conflicts
    
    Skip:
    - confidence == "low"
    - action_type == "delete"
    - Has conflicts
    """
    logger.info("Auto-approving actions based on confidence...")
    
    proposal_data = json.loads(proposal_json.read_text())
    actions = proposal_data.get("proposed_actions", [])
    
    approved_count = 0
    skipped_count = 0
    
    for action in actions:
        confidence = action.get("confidence", "medium")
        action_type = action.get("action_type", "")
        has_conflict = action.get("conflict", False)
        
        if (confidence == "high" and 
            action_type in ["move", "archive", "ignore"] and
            not has_conflict):
            action["approved"] = True
            approved_count += 1
        else:
            action["approved"] = False
            skipped_count += 1
    
    logger.info(f"✓ Auto-approved: {approved_count}, Skipped: {skipped_count}")
    
    # Write updated proposal
    updated_proposal_path = Path("/tmp/conversation-proposal-auto.json")
    proposal_data["proposed_actions"] = actions
    updated_proposal_path.write_text(json.dumps(proposal_data, indent=2))
    
    return updated_proposal_path


def send_proposal_email(proposal_md: str, proposal_json: Path):
    """Email proposal to V for approval"""
    logger.info("Emailing proposal for approval...")
    
    # Save proposal for later execution
    saved_proposal = WORKSPACE / "N5/data" / f"pending-proposal-{datetime.now():%Y%m%d-%H%M%S}.json"
    saved_proposal.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy proposal
    import shutil
    shutil.copy(proposal_json, saved_proposal)
    
    logger.info(f"✓ Proposal saved: {saved_proposal}")
    logger.info("Note: Email sending requires send_email_to_user tool (not available in script)")
    logger.info("Manual action: Review proposal and approve via follow-up conversation")
    
    # Print proposal for manual review
    print("\n" + "="*70)
    print("PROPOSAL FOR EMAIL")
    print("="*70)
    print(proposal_md)
    print("\n" + "="*70)
    print(f"\nProposal saved to: {saved_proposal}")
    print("To execute later:")
    print(f"  python3 {SCRIPTS_DIR}/conversation_end_executor.py --proposal {saved_proposal}")


def execute_proposal(proposal_json: Path, dry_run: bool = False) -> bool:
    """
    Execute approved actions via executor (W3)
    
    Returns: True on success, False on failure
    """
    phase_label = "DRY-RUN" if dry_run else "EXECUTION"
    logger.info(f"Phase 3: {phase_label}...")
    
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "conversation_end_executor.py"),
        "--proposal", str(proposal_json)
    ]
    
    if dry_run:
        cmd.append("--dry-run")
    
    try:
        result = subprocess.run(cmd, check=True)
        logger.info(f"✓ {phase_label} complete")
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {phase_label} failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {phase_label} error: {e}")
        return False


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="N5 Conversation End Orchestrator - Modular file organization"
    )
    parser.add_argument("--auto", action="store_true",
                       help="Auto mode: approve high-confidence actions automatically")
    parser.add_argument("--email", action="store_true",
                       help="Email mode: send proposal for async approval")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry-run: preview actions without executing")
    parser.add_argument("--workspace", 
                       help="Conversation workspace path (auto-detected if not provided)")
    parser.add_argument("--convo-id",
                       help="Conversation ID (derived from workspace if not provided)")
    
    return parser.parse_args()


def main():
    """Main orchestration"""
    args = parse_args()
    
    # Validate workspace
    workspace = Path(args.workspace) if args.workspace else CONVERSATION_WS
    
    if not workspace or not workspace.exists():
        print("\n" + "="*70)
        print("❌ CONVERSATION WORKSPACE NOT FOUND")
        print("="*70)
        print(f"\nSearched: {workspace}")
        print("\nThis command organizes files created during the conversation.")
        print("No conversation workspace was detected.")
        return 1
    
    # Derive conversation ID
    convo_id = args.convo_id or workspace.name
    
    print("\n" + "="*70)
    print("N5 CONVERSATION END ORCHESTRATOR (v2)")
    print("="*70)
    print(f"\nWorkspace: {workspace}")
    print(f"Conversation ID: {convo_id}")
    print(f"Mode: {'AUTO' if args.auto else 'EMAIL' if args.email else 'INTERACTIVE'}")
    if args.dry_run:
        print("Dry-run: ENABLED")
    print()
    
    # ===================================================================
    # PHASE 1: ANALYSIS
    # ===================================================================
    analysis_json = run_analyzer(workspace, convo_id)
    if not analysis_json:
        logger.error("❌ Analysis phase failed")
        return 1
    
    # ===================================================================
    # PHASE 2: PROPOSAL GENERATION
    # ===================================================================
    proposal_md, proposal_json = generate_proposal(analysis_json)
    if not proposal_md or not proposal_json:
        logger.error("❌ Proposal generation failed")
        return 1
    
    # ===================================================================
    # PHASE 2.5: USER INTERACTION (MODE-DEPENDENT)
    # ===================================================================
    
    if args.email:
        # Email mode: send proposal and exit
        send_proposal_email(proposal_md, proposal_json)
        logger.info("✓ Proposal emailed, awaiting approval")
        return 0
    
    # Display proposal
    display_proposal(proposal_md)
    
    if args.auto:
        # Auto mode: approve based on confidence
        approved_proposal = auto_approve_proposal(proposal_json)
    else:
        # Interactive mode: user selection
        approved_proposal = get_user_selections(proposal_json)
    
    if not approved_proposal:
        logger.error("❌ Approval step failed")
        return 1
    
    # ===================================================================
    # PHASE 3: EXECUTION
    # ===================================================================
    success = execute_proposal(approved_proposal, dry_run=args.dry_run)
    
    if success:
        print("\n" + "="*70)
        print("✅ CONVERSATION-END COMPLETE")
        print("="*70)
        return 0
    else:
        print("\n" + "="*70)
        print("❌ EXECUTION FAILED")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
