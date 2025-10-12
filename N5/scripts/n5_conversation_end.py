#!/usr/bin/env python3
"""
N5 Conversation End-Step
Formal conversation close with AAR generation, file organization and cleanup

This is the "end step" (like Magic: The Gathering) where all conversation
effects are resolved - AAR generated, files reviewed, organized, and cleaned up.
"""

import os
import sys
import json
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")

# Detect conversation workspace from environment or by finding the workspace we're in
CONVERSATION_WS_ENV = os.getenv("CONVERSATION_WORKSPACE")
if CONVERSATION_WS_ENV:
    CONVERSATION_WS = Path(CONVERSATION_WS_ENV)
else:
    # Try to detect from common patterns
    workspaces_dir = Path("/home/.z/workspaces")
    if workspaces_dir.exists():
        # Find most recently modified workspace
        workspaces = [d for d in workspaces_dir.iterdir() if d.is_dir() and d.name.startswith("con_")]
        if workspaces:
            CONVERSATION_WS = max(workspaces, key=lambda d: d.stat().st_mtime)
        else:
            CONVERSATION_WS = None
    else:
        CONVERSATION_WS = None

DOCUMENT_INBOX = WORKSPACE / "Document Inbox/Temporary"
LOG_FILE = WORKSPACE / "N5/runtime/conversation_ends.log"


def log_action(message):
    """Log to file and print"""
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] {message}"
    print(message)
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + '\n')


def classify_file(filepath):
    """
    Classify file by type and content to determine destination
    
    Returns: (destination, action, reason)
        destination: Path or None
        action: "move" | "delete" | "ask"
        reason: Explanation
    """
    name = filepath.name.lower()
    ext = filepath.suffix.lower()
    
    # Classification rules
    
    # Images
    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
        if any(x in name for x in ['temp', 'test', 'chart', 'viz']):
            return (None, "delete", "Temporary visualization")
        else:
            dest = WORKSPACE / "Images" / filepath.name
            return (dest, "move", "Generated/downloaded image")
    
    # Meeting transcripts
    if any(x in name for x in ['transcript', 'meeting']):
        dest = DOCUMENT_INBOX.parent / "Company/meetings" / filepath.name
        return (dest, "move", "Meeting transcript for processing")
    
    # Analysis/reports
    if any(x in name for x in ['analysis', 'report', 'summary']):
        dest = WORKSPACE / "Documents" / filepath.name
        return (dest, "move", "Analysis/report document")
    
    # Scripts
    if ext in ['.py', '.sh', '.js']:
        if any(x in name for x in ['temp', 'test', 'tmp']):
            return (None, "delete", "Temporary script")
        else:
            return (None, "ask", "Script - determine if permanent")
    
    # Data exports
    if ext in ['.csv', '.json', '.jsonl']:
        if any(x in name for x in ['temp', 'test', 'intermediate']):
            return (None, "delete", "Temporary data file")
        else:
            dest = WORKSPACE / "Exports" / filepath.name
            return (dest, "move", "Data export")
    
    # Documents
    if ext in ['.md', '.txt', '.pdf', '.docx']:
        if any(x in name for x in ['temp', 'test', 'draft', 'scratch']):
            return (None, "delete", "Temporary document")
        else:
            # Default to Document Inbox for review
            dest = DOCUMENT_INBOX / filepath.name
            return (dest, "move", "Document for review")
    
    # Default: Ask user
    return (None, "ask", "Unknown file type")


def inventory_workspace():
    """
    Inventory all files in conversation workspace
    
    Returns: dict of {category: [files]}
    """
    if not CONVERSATION_WS.exists():
        print(f"⚠️  Conversation workspace not found: {CONVERSATION_WS}")
        print("   Using current directory for demonstration")
        return {}
    
    files_by_category = defaultdict(list)
    
    for filepath in CONVERSATION_WS.rglob("*"):
        if filepath.is_file():
            dest, action, reason = classify_file(filepath)
            category = f"{action.upper()}"
            files_by_category[category].append({
                "file": filepath,
                "dest": dest,
                "reason": reason
            })
    
    return files_by_category


def propose_organization(files_by_category):
    """
    Propose file organization to user
    
    Returns formatted proposal
    """
    proposal = []
    proposal.append("\n" + "="*70)
    proposal.append("CONVERSATION END-STEP: File Organization")
    proposal.append("="*70)
    
    total_files = sum(len(files) for files in files_by_category.values())
    proposal.append(f"\nFiles created this conversation: {total_files}\n")
    
    # Group by action
    for action in ["MOVE", "DELETE", "ASK"]:
        files = files_by_category.get(action, [])
        if not files:
            continue
        
        if action == "MOVE":
            proposal.append(f"\n📁 FILES TO MOVE ({len(files)} files)")
            proposal.append("-" * 70)
            
            # Group by destination
            by_dest = defaultdict(list)
            for item in files:
                dest_dir = item['dest'].parent if item['dest'] else "Unknown"
                by_dest[dest_dir].append(item)
            
            for dest_dir, items in sorted(by_dest.items()):
                proposal.append(f"\n  → {dest_dir}/")
                for item in sorted(items, key=lambda x: x['file'].name):
                    proposal.append(f"     ✓ {item['file'].name}")
                    proposal.append(f"        ({item['reason']})")
        
        elif action == "DELETE":
            proposal.append(f"\n🗑️  FILES TO DELETE ({len(files)} files)")
            proposal.append("-" * 70)
            for item in sorted(files, key=lambda x: x['file'].name):
                proposal.append(f"  ✗ {item['file'].name}")
                proposal.append(f"     ({item['reason']})")
        
        elif action == "ASK":
            proposal.append(f"\n❓ FILES NEEDING DECISION ({len(files)} files)")
            proposal.append("-" * 70)
            for item in sorted(files, key=lambda x: x['file'].name):
                proposal.append(f"  ? {item['file'].name}")
                proposal.append(f"     ({item['reason']})")
    
    # Summary
    move_count = len(files_by_category.get("MOVE", []))
    delete_count = len(files_by_category.get("DELETE", []))
    ask_count = len(files_by_category.get("ASK", []))
    
    proposal.append("\n" + "="*70)
    proposal.append(f"SUMMARY: {move_count} move, {delete_count} delete, {ask_count} need decision")
    proposal.append("="*70)
    proposal.append("\nProceed with moves and deletions? (Y/n)")
    
    return "\n".join(proposal)


def execute_organization(files_by_category, confirmed=True):
    """
    Execute file moves and deletions
    """
    if not confirmed:
        print("❌ Organization cancelled by user")
        return
    
    print("\n" + "="*70)
    print("EXECUTING FILE ORGANIZATION")
    print("="*70 + "\n")
    
    moved_count = 0
    deleted_count = 0
    errors = []
    
    # Execute moves
    for item in files_by_category.get("MOVE", []):
        try:
            # Create destination directory
            item['dest'].parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(item['file']), str(item['dest']))
            
            moved_count += 1
            log_action(f"Moved: {item['file'].name} → {item['dest'].relative_to(WORKSPACE)}")
            
        except Exception as e:
            errors.append(f"{item['file'].name}: {e}")
    
    # Execute deletions
    for item in files_by_category.get("DELETE", []):
        try:
            item['file'].unlink()
            deleted_count += 1
            log_action(f"Deleted: {item['file'].name} (temporary)")
        except Exception as e:
            errors.append(f"{item['file'].name}: {e}")
    
    # Report
    print(f"✓ Moved {moved_count} files")
    print(f"✗ Deleted {deleted_count} files")
    
    if errors:
        print(f"\n⚠️  {len(errors)} errors:")
        for err in errors[:10]:
            print(f"  - {err}")
    
    # Handle ASK files
    ask_files = files_by_category.get("ASK", [])
    if ask_files:
        print(f"\n❓ {len(ask_files)} files need manual decision")
        print("   Keeping in conversation workspace for now")
    
    return {
        "moved": moved_count,
        "deleted": deleted_count,
        "errors": len(errors),
        "pending": len(ask_files)
    }


def cleanup_workspace_root():
    """
    Clean up workspace root files (conversation artifacts).
    This is Phase 2 of conversation-end cleanup.
    """
    print("\n" + "="*70)
    print("PHASE 2: WORKSPACE ROOT CLEANUP")
    print("="*70)
    print("\nScanning for conversation artifacts in workspace root...\n")
    
    cleanup_script = WORKSPACE / "N5/scripts/n5_workspace_root_cleanup.py"
    
    if not cleanup_script.exists():
        print("⚠️  Cleanup script not found, skipping workspace root cleanup")
        return
    
    try:
        # Run cleanup with auto-execute
        result = subprocess.run(
            [sys.executable, str(cleanup_script), "--execute"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Print output
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"⚠️  Cleanup completed with warnings")
            if result.stderr:
                print(f"Errors: {result.stderr}")
        
    except Exception as e:
        print(f"⚠️  Workspace root cleanup skipped: {e}")


def generate_aar():
    """
    Generate After-Action Report (AAR) for this conversation
    This is Phase 0 - captures conversation context before cleanup
    """
    print("\n" + "="*70)
    print("PHASE 0: AFTER-ACTION REPORT (AAR) GENERATION")
    print("="*70)
    print("\nCapturing conversation context and decisions...\n")
    
    aar_script = WORKSPACE / "N5/scripts/n5_thread_export.py"
    
    if not aar_script.exists():
        print("⚠️  AAR script not found, skipping AAR generation")
        print(f"   Expected: {aar_script}")
        return
    
    try:
        # Run AAR export with auto-detect and auto-confirm (--yes flag for non-interactive)
        result = subprocess.run(
            [sys.executable, str(aar_script), "--auto", "--yes"],
            capture_output=True,
            text=True,
            check=False,
            timeout=300  # 5 minute timeout
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print("\n✓ AAR generated successfully")
        else:
            print(f"\n⚠️  AAR generation completed with warnings")
            if result.stderr:
                print(f"Errors: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("⚠️  AAR generation timed out (>5min), continuing with cleanup...")
    except Exception as e:
        print(f"⚠️  AAR generation skipped: {e}")


def main():
    """Main execution"""
    
    # Check if we're in a real conversation context
    if not CONVERSATION_WS or not CONVERSATION_WS.exists():
        print("\n" + "="*70)
        print("❌ CONVERSATION WORKSPACE NOT FOUND")
        print("="*70)
        print(f"\nSearched: {CONVERSATION_WS}")
        print("\nThis command organizes files created during the conversation.")
        print("It appears no conversation workspace was detected.")
        print("\nPossible reasons:")
        print("  - Not running in a conversation context")
        print("  - Workspace directory doesn't exist")
        print("  - Environment variable CONVERSATION_WORKSPACE not set")
        return 1
    
    print("\n" + "="*70)
    print("N5 CONVERSATION END-STEP")
    print("="*70)
    print(f"\nConversation workspace: {CONVERSATION_WS}")
    
    # NEW: Phase 0 - Generate AAR
    generate_aar()
    
    # Step 1: Inventory
    print("\n" + "="*70)
    print("PHASE 1: FILE ORGANIZATION")
    print("="*70)
    print("\nStep 1: Inventorying files...")
    files_by_category = inventory_workspace()
    
    if not any(files_by_category.values()):
        print("\n✓ No files to organize - conversation workspace is clean")
        return
    
    # Step 2: Propose
    proposal = propose_organization(files_by_category)
    print(proposal)
    
    # Step 3: Get confirmation
    if "--auto" in sys.argv or "--yes" in sys.argv:
        confirmed = True
    else:
        response = input("\n> ").strip().lower()
        confirmed = response in ['y', 'yes', '']
    
    # Step 4: Execute
    if confirmed:
        result = execute_organization(files_by_category, confirmed=True)
        
        # Log conversation end
        log_action(f"Conversation ended: {result['moved']} moved, {result['deleted']} deleted")
        
        # NEW: Phase 2 - Workspace root cleanup
        print("\n" + "="*70)
        print("CONTINUING TO WORKSPACE ROOT CLEANUP...")
        print("="*70)
        cleanup_workspace_root()
        
        # Personal intelligence update (autonomous)
        print("\n" + "="*70)
        print("PHASE 3: PERSONAL INTELLIGENCE UPDATE")
        print("="*70)
        try:
            intelligence_script = WORKSPACE / "N5/scripts/update_personal_intelligence.py"
            if intelligence_script.exists():
                logger.info("Updating personal intelligence layer (autonomous)...")
                subprocess.run([sys.executable, str(intelligence_script)], check=False)
            else:
                print("⚠️  Personal intelligence script not found, skipping")
        except Exception as e:
            logger.warning(f"Personal intelligence update skipped: {e}")
        
        # Final summary
        print("\n" + "="*70)
        print("✅ CONVERSATION END-STEP COMPLETE")
        print("="*70)
    else:
        print("\n✓ Organization cancelled - files remain in conversation workspace")


if __name__ == "__main__":
    main()
