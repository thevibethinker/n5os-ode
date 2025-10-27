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
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Import timeline automation
sys.path.insert(0, str(Path(__file__).parent))
try:
    from timeline_automation_module import add_timeline_entry_from_workspace
    TIMELINE_AUTOMATION_AVAILABLE = True
except ImportError:
    TIMELINE_AUTOMATION_AVAILABLE = False

try:
    from conversation_registry import ConversationRegistry
    CONVERSATION_REGISTRY_AVAILABLE = True
except ImportError:
    CONVERSATION_REGISTRY_AVAILABLE = False

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


def propose_organization(files_by_category, auto_mode=False):
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
    
    if not auto_mode:
        proposal.append("\nProceed with moves and deletions? (Y/n)")
    else:
        proposal.append("\n→ Auto mode: Proceeding automatically")
    
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


def placeholder_scan(auto_mode=False):
    """
    Scan conversation files for placeholders, stubs, and incomplete code
    This is Phase 2.5 - enforces P16 (Accuracy) and P21 (Document Assumptions)
    """
    print("\n" + "="*70)
    print("PHASE 2.5: PLACEHOLDER & STUB DETECTION")
    print("="*70)
    print("\nScanning for incomplete code and placeholders...\n")
    
    scan_script = WORKSPACE / "N5/scripts/n5_placeholder_scan.py"
    
    if not scan_script.exists():
        print("⚠️  Placeholder scan script not found, skipping")
        print(f"   Expected: {scan_script}")
        return True
    
    try:
        # Run placeholder scan
        result = subprocess.run(
            [sys.executable, str(scan_script)],
            capture_output=True,
            text=True,
            check=False,
            timeout=60
        )
        
        # Print scan results
        if result.stdout:
            print(result.stdout)
        
        # Exit code: 0 = clean, 1 = issues found, 2 = error
        if result.returncode == 0:
            print("✓ No placeholders detected - all clear\n")
            return True
        
        elif result.returncode == 1:
            # Issues found
            print("\n" + "="*70)
            print("⚠️  RESOLUTION REQUIRED BEFORE CONVERSATION-END")
            print("="*70)
            print("\nYou must address these issues before closing the conversation.")
            print("\nOptions:")
            print("  1. Return to conversation and fix issues")
            print("  2. Document as intentional (add '# DOCUMENTED:' prefix to lines)")
            print("  3. Acknowledge and continue (will be logged for later)")
            
            # Check for auto mode
            if auto_mode:
                print("\n→ Auto mode: Logging issues and continuing...")
                log_action("Placeholder scan: issues detected but auto-acknowledged")
                return True
            
            print("\nHow would you like to proceed?")
            print("  [F]ix now (abort conversation-end)")
            print("  [A]cknowledge & continue (log issues)")
            print("  [Q]uit (abort conversation-end)")
            
            while True:
                response = input("\n> ").strip().lower()
                
                if response in ['f', 'fix']:
                    print("\n❌ Conversation-end aborted - return to fix issues")
                    log_action("Conversation-end aborted: placeholder scan issues")
                    return False
                
                elif response in ['a', 'acknowledge', 'ack']:
                    print("\n→ Issues acknowledged - logging for follow-up")
                    log_action("Placeholder scan: issues acknowledged, continuing")
                    return True
                
                elif response in ['q', 'quit', 'abort']:
                    print("\n❌ Conversation-end aborted by user")
                    return False
                
                else:
                    print("Invalid choice. Please enter F (fix), A (acknowledge), or Q (quit)")
        
        else:
            # Error in scan
            print(f"⚠️  Placeholder scan failed with error code {result.returncode}")
            if result.stderr:
                logger.error(f"Scan error: {result.stderr}")
            print("→ Continuing conversation-end despite scan error")
            return True
        
    except subprocess.TimeoutExpired:
        print("⚠️  Placeholder scan timed out (>60s), continuing...")
        return True
    
    except Exception as e:
        print(f"⚠️  Placeholder scan error: {e}")
        logger.debug("Scan error details", exc_info=True)
        return True


def output_review_check(auto_mode=False):
    """Phase 2.75: Check output review tracking and remind about deliverables."""
    try:
        # Get conversation ID
        convo_id = os.getenv("ZO_CONVERSATION_ID") or CONVERSATION_WS.name
        
        # Import review manager
        sys.path.insert(0, str(WORKSPACE / "N5/scripts"))
        from review_manager import ReviewManager
        
        manager = ReviewManager()
        
        # Get outputs flagged in this conversation
        flagged_outputs = manager.list_reviews(conversation_id=convo_id)
        
        print(f"\n📊 Output Review Summary")
        print(f"   Flagged in this conversation: {len(flagged_outputs)}")
        
        if flagged_outputs:
            print(f"\n   Recent flagged outputs:")
            for out in flagged_outputs[-5:]:  # Show last 5
                status_emoji = {
                    "pending": "⏸️",
                    "in_review": "🔍",
                    "approved": "✅",
                    "issue": "⚠️ ",
                    "training": "📚",
                    "archived": "📦"
                }.get(out['review']['status'], "•")
                print(f"   {status_emoji} {out['title'][:60]}")
                if out.get('improvement_notes'):
                    print(f"      → Improve: {out['improvement_notes'][:70]}...")
        
        # Scan for major deliverables not flagged
        unflagged_candidates = []
        workspace_files = list(CONVERSATION_WS.rglob("*"))
        
        for file_path in workspace_files:
            if not file_path.is_file():
                continue
            
            # Skip system files
            name = file_path.name
            if name.startswith(("temp_", "test_", "scratch_", "BUILD_MAP", "SESSION_STATE", "AAR")):
                continue
            
            # Check if already flagged
            if any(out['reference'] == str(file_path) for out in flagged_outputs):
                continue
            
            # Check if substantial (>100 words for text files)
            if file_path.suffix in ['.md', '.txt', '.py', '.js', '.json', '.html']:
                try:
                    content = file_path.read_text()
                    word_count = len(content.split())
                    if word_count > 100:
                        unflagged_candidates.append((file_path, word_count))
                except:
                    pass
        
        if unflagged_candidates:
            print(f"\n   ⚠️  Found {len(unflagged_candidates)} substantial outputs NOT flagged for review:")
            for file_path, wc in unflagged_candidates[:5]:  # Show first 5
                rel_path = file_path.relative_to(CONVERSATION_WS)
                print(f"      • {rel_path} ({wc} words)")
            
            print(f"\n   💡 To flag for quality review:")
            print(f"      python3 N5/scripts/review_cli.py add <path> \\")
            print(f"        --improve \"What to change\" \\")
            print(f"        --optimal \"Ideal version description\"")
            
            if not auto_mode:
                print(f"\n   Press Enter to continue (outputs remain unflagged)")
                input(f"   > ")
            else:
                print(f"\n   → Auto mode: Continuing without flagging")
        else:
            print(f"   ✓ No substantial unflagged outputs detected")
        
        logger.info("Output review check complete")
        
    except Exception as e:
        print(f"   ⚠️  Output review check skipped: {e}")
        logger.debug(f"Output review check error details", exc_info=True)


def archive_build_tasks():
    """
    Archive completed tasks from build tracker (Phase 3.5).
    Closes build session and generates archive of completed tasks.
    """
    print("\n" + "="*70)
    print("PHASE 3.5: BUILD TRACKER ARCHIVAL")
    print("="*70)
    print("\nChecking for build tracking data to archive...\n")
    
    # Check if BUILD_MAP exists in conversation workspace
    if not CONVERSATION_WS:
        print("→ No conversation workspace detected, skipping build archival")
        return
    
    build_map = CONVERSATION_WS / "BUILD_MAP.md"
    if not build_map.exists():
        print("→ No BUILD_MAP found, skipping build archival")
        return
    
    # Import build tracker
    try:
        sys.path.insert(0, str(WORKSPACE / "N5/scripts"))
        from build_tracker import BuildTracker
    except ImportError as e:
        print(f"⚠️  Could not import BuildTracker: {e}")
        print("   Skipping build archival")
        return
    
    try:
        # Detect conversation ID
        convo_id = CONVERSATION_WS.name if CONVERSATION_WS else "unknown"
        tracker = BuildTracker(convo_id=convo_id)
        
        # Check if already closed
        if tracker.is_session_closed():
            print(f"✓ Build session already closed for {convo_id}")
            return
        
        # Close session and generate archive
        print(f"Closing build session: {convo_id}")
        
        # First, generate archive of completed tasks
        archive_file = tracker.generate_archive(dry_run=False)
        
        # Then close the session
        summary = tracker.close_session(dry_run=False)
        
        if summary.get("error"):
            print(f"⚠️  {summary['error']}")
            return
        
        # Report results
        print(f"\n✓ Build session closed successfully")
        print(f"  Total tasks: {summary['total']}")
        print(f"  Completed (archived): {summary['complete']}")
        print(f"  Active/Open: {summary['active'] + summary['open']}")
        
        if archive_file:
            print(f"  Archive: {archive_file.name}")
        
        # Refresh BUILD_MAP to show only active tasks
        if tracker.refresh():
            print(f"\n✓ BUILD_MAP updated to hide completed tasks")
        
    except Exception as e:
        print(f"⚠️  Build archival error: {e}")
        logger.debug("Build archival error details", exc_info=True)
        print("→ Continuing with conversation-end...")


def extract_lessons():
    """
    Extract lessons from this conversation (Phase -1)
    This runs before AAR to capture techniques, patterns, and troubleshooting
    """
    print("\n" + "="*70)
    print("PHASE -1: LESSON EXTRACTION")
    print("="*70)
    print("\nAnalyzing conversation for significant lessons...\n")
    
    lessons_script = WORKSPACE / "N5/scripts/n5_lessons_extract.py"
    
    if not lessons_script.exists():
        print("⚠️  Lessons extraction script not found. Skipping Phase -1.")
        print(f"   Expected: {lessons_script}")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, str(lessons_script), "--auto"],
            capture_output=True,
            text=True,
            check=False,
            timeout=180
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print("✓ Phase -1 complete (lessons extraction attempted)")
    except Exception as e:
        print(f"⚠️  Lessons extraction error: {e}")
        print("→ Continuing to Phase 0 (AAR)")

def enrich_session_state():
    """
    Phase -0.5: Enrich SESSION_STATE.md with conversation context
    Analyzes workspace files and updates session state before AAR generation
    """
    print("\n" + "="*70)
    print("PHASE -0.5: SESSION STATE ENRICHMENT")
    print("="*70)
    print("\nAnalyzing conversation workspace...\n")
    
    session_file = CONVERSATION_WS / "SESSION_STATE.md"
    if not session_file.exists():
        logger.debug("No SESSION_STATE.md found, skipping enrichment")
        return
    
    try:
        content = session_file.read_text()
        
        # Extract current state
        lines = content.split('\n')
        
        # Check if already enriched (not placeholder text)
        if "What is this conversation specifically about?" not in content:
            logger.info("✓ SESSION_STATE.md already enriched")
            return
        
        # Analyze workspace files to infer context
        workspace_files = list(CONVERSATION_WS.glob("*"))
        
        # Infer focus from filenames and content
        focus_hints = []
        objective_hints = []
        completed_items = []
        
        # Look for deployment briefs, summaries, validation reports
        for f in workspace_files:
            if not f.is_file():
                continue
            name = f.name.lower()
            
            if 'deployment' in name or 'worker' in name:
                focus_hints.append("deployment")
                if 'complete' in name or 'validation' in name:
                    completed_items.append(f"Completed {f.stem}")
            
            if 'fix' in name or 'bug' in name:
                focus_hints.append("bug fix")
                objective_hints.append("Fix identified issue")
            
            if 'summary' in name or 'report' in name:
                completed_items.append(f"Generated {f.stem}")
        
        # Build enriched sections
        if focus_hints:
            focus = f"Conversation focused on: {', '.join(set(focus_hints))}"
        else:
            focus = "General build/implementation work"
        
        if objective_hints:
            objective = "; ".join(objective_hints)
        else:
            objective = "Complete assigned work"
        
        # Update SESSION_STATE.md
        updated_lines = []
        in_focus_section = False
        in_objective_section = False
        focus_replaced = False
        objective_replaced = False
        
        for line in lines:
            if line.startswith("**Focus:**"):
                updated_lines.append(f"**Focus:** {focus}")
                focus_replaced = True
                continue
            elif line.startswith("**Goal:**"):
                updated_lines.append(f"**Goal:** {objective}")
                objective_replaced = True
                continue
            elif "*What is this conversation specifically about?*" in line:
                continue  # Skip placeholder
            elif "*What are we trying to accomplish?*" in line:
                continue  # Skip placeholder
            
            updated_lines.append(line)
        
        # Write back
        session_file.write_text('\n'.join(updated_lines))
        
        print(f"✓ Enriched SESSION_STATE.md")
        print(f"  Focus: {focus}")
        print(f"  Goal: {objective}")
        if completed_items:
            print(f"  Completed: {len(completed_items)} items")
        
    except Exception as e:
        logger.error(f"Error enriching session state: {e}")
        print(f"⚠️  Could not enrich session state: {e}")
        print("   → Continuing with existing state")

def generate_thread_export():
    """
    Phase 0: Generate after-action report using n5_thread_export.py
    """
    print("\n" + "="*70)
    print("PHASE 0: AFTER-ACTION REPORT (AAR) GENERATION")
    print("="*70)
    print("\nCapturing conversation context and decisions...\n")
    
    cmd = [
        sys.executable,
        str(WORKSPACE / "N5/scripts/n5_thread_export.py"),
        "--auto",
        "--yes"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ AAR generated successfully")
        
        # NEW: Extract and save proposed title
        save_proposed_title()
        
        return True
    else:
        print(f"⚠️  AAR generation had issues:\n{result.stderr}")
        print("→ Continuing with next phase...")
        return False

def save_proposed_title():
    """
    Phase 0.5: Extract generated title and save to conversation workspace
    Uses conversation-specific AAR, not "most recent"
    """
    try:
        from n5_title_generator import TitleGenerator
        
        # Extract conversation ID from workspace path
        if not CONVERSATION_WS:
            logger.debug("No conversation workspace available")
            return
            
        convo_id = CONVERSATION_WS.name  # e.g., "con_W9jH5cVRjYPHve2j"
        
        # Find thread archive for THIS conversation
        threads_dir = WORKSPACE / "N5/logs/threads"
        if not threads_dir.exists():
            logger.debug("No threads directory found")
            return
        
        # Look for directory containing this conversation ID
        matching_archives = [
            d for d in threads_dir.iterdir() 
            if d.is_dir() and convo_id in d.name
        ]
        
        if not matching_archives:
            logger.debug(f"No thread archive found for conversation {convo_id}, using fallback")
            # Fallback: generate from SESSION_STATE.md
            return generate_title_from_session_state()
        
        # Use the most recent match (in case there are multiple from same conversation)
        latest_archive = max(matching_archives, key=lambda x: x.stat().st_mtime)
        aar_file = latest_archive / f"aar-{datetime.now().strftime('%Y-%m-%d')}.json"
        
        if not aar_file.exists():
            logger.debug(f"No AAR file found: {aar_file}, using fallback")
            return generate_title_from_session_state()
        
        # Load AAR data
        with open(aar_file) as f:
            aar_data = json.load(f)
        
        # Collect artifacts from conversation workspace
        artifacts = []
        if CONVERSATION_WS and CONVERSATION_WS.exists():
            for item in CONVERSATION_WS.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    artifacts.append({
                        "path": str(item.relative_to(CONVERSATION_WS.parent)),
                        "filename": item.name,
                        "relative_path": str(item.relative_to(CONVERSATION_WS)),
                        "size_bytes": item.stat().st_size
                    })
        
        # Generate title
        generator = TitleGenerator()
        titles = generator.generate_titles(aar_data, artifacts)
        
        if not titles:
            logger.debug("No titles generated from AAR, using fallback")
            return generate_title_from_session_state()
        
        # Write and display title
        write_and_display_title(titles, convo_id)
        
    except Exception as e:
        logger.error(f"Error generating title: {e}")
        logger.debug(f"Stack trace:", exc_info=True)


def generate_title_from_session_state():
    """
    Fallback: Generate title from SESSION_STATE.md when no AAR exists
    """
    try:
        if not CONVERSATION_WS or not CONVERSATION_WS.exists():
            logger.debug("No conversation workspace for fallback")
            return
        
        session_state = CONVERSATION_WS / "SESSION_STATE.md"
        if not session_state.exists():
            logger.debug("No SESSION_STATE.md found for fallback")
            return
        
        content = session_state.read_text()
        
        # Extract key fields with simple parsing
        def extract_field(text, field_name):
            """Extract field value from markdown"""
            for line in text.split('\n'):
                if line.startswith(f"**{field_name}**"):
                    # Get everything after the field marker
                    value = line.split(f"**{field_name}**", 1)[1].strip()
                    # Remove any markdown formatting
                    value = value.strip('*').strip()
                    if value and value != "*What is this conversation specifically about?*":
                        return value
            return None
        
        focus = extract_field(content, "Focus:")
        objective = extract_field(content, "Goal:")
        phase = extract_field(content, "Current Phase:")
        conv_type = extract_field(content, "Primary Type:")
        
        # Build AAR-like data from session state
        from n5_title_generator import TitleGenerator
        generator = TitleGenerator()
        
        aar_data = {
            "primary_objective": objective or focus or "Work session",
            "final_state": {
                "summary": f"{conv_type or 'build'} session: {phase or 'in progress'}"
            },
            "key_events": []
        }
        
        # Try to extract outputs from session state
        artifacts = []
        outputs_section = False
        for line in content.split('\n'):
            if "## Outputs" in line:
                outputs_section = True
            elif outputs_section and line.startswith('- `'):
                # Parse: - `path/to/file` - Description
                artifacts.append({"filename": line.split('`')[1] if '`' in line else "file"})
        
        titles = generator.generate_titles(aar_data, artifacts)
        
        if not titles:
            logger.debug("No titles generated from session state either")
            return
        
        # Write and display title
        convo_id = CONVERSATION_WS.name
        write_and_display_title(titles, convo_id)
        
    except Exception as e:
        logger.error(f"Error in fallback title generation: {e}")
        logger.debug(f"Stack trace:", exc_info=True)


def write_and_display_title(titles, convo_id):
    """
    Write PROPOSED_TITLE.md and display to user
    """
    if not CONVERSATION_WS:
        return
        
    title_file = CONVERSATION_WS / "PROPOSED_TITLE.md"
    
    md = []
    md.append("# Proposed Conversation Title\n")
    md.append("## Recommended Title\n")
    md.append(f"**{titles[0]['title']}**\n")
    md.append(f"\n**Reasoning:** {titles[0]['reasoning']}\n")
    
    if len(titles) > 1:
        md.append("\n## Alternative Options\n")
        for i, opt in enumerate(titles[1:4], 2):
            md.append(f"\n### Option {i}: {opt['title']}")
            md.append(f"- Reasoning: {opt['reasoning']}\n")
    
    md.append("\n---\n")
    md.append("*Generated by n5_title_generator*\n")
    
    title_file.write_text("\n".join(md))
    
    # Display prominently
    print("\n" + "="*70)
    print("PROPOSED CONVERSATION TITLE")
    print("="*70)
    print(f"\n✨ Recommended: {titles[0]['title']}\n")
    
    if len(titles) > 1:
        print("Alternatives:")
        for i, opt in enumerate(titles[1:4], 2):
            print(f"  {i}. {opt['title']}")
    
    print(f"\n📄 Full details: {title_file.relative_to(WORKSPACE.parent)}")
    print("\n" + "="*70)
    
    # Update conversation database if available
    if CONVERSATION_REGISTRY_AVAILABLE:
        registry = ConversationRegistry()
        
        if registry.update(convo_id, title=titles[0]['title']):
            logger.info(f"✓ Updated conversation registry with title")
        else:
            logger.debug(f"Conversation not in registry or update failed")


def git_status_check():
    """
    Check git status and prompt for commit if there are uncommitted changes
    This is Phase 4 - ensures work is saved before conversation ends
    """
    print("\n" + "="*70)
    print("PHASE 4: GIT STATUS CHECK")
    print("="*70)
    print("\nChecking for uncommitted changes...\n")
    
    try:
        # Check git status
        status_result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            check=False
        )
        
        if status_result.returncode != 0:
            print("⚠️  Git status check failed - not a git repository or git error")
            return
        
        changes = status_result.stdout.strip()
        
        if not changes:
            print("✅ No uncommitted changes - git is clean")
            return
        
        # There are changes - show them
        print("📝 Uncommitted changes detected:\n")
        print(changes)
        print()
        
        # Run git-check to audit staged changes
        git_check_script = WORKSPACE / "N5/scripts/n5_git_check.py"
        if git_check_script.exists():
            print("-" * 70)
            print("Running git-check audit...\n")
            audit_result = subprocess.run(
                [sys.executable, str(git_check_script)],
                capture_output=True,
                text=True,
                check=False
            )
            if audit_result.stdout:
                print(audit_result.stdout)
            print("-" * 70)
            print()
        
        # Prompt user to commit
        print("⚠️  You have uncommitted changes.")
        
        # Check for --auto flag (skip prompt in auto mode)
        if "--auto" in sys.argv or "--yes" in sys.argv:
            print("   (Auto mode: skipping commit prompt)")
            return
        
        response = input("Commit changes before ending conversation? (Y/n): ").strip().lower()
        
        if response not in ['y', 'yes', '']:
            print("→ Skipping commit - changes remain uncommitted")
            return
        
        # User wants to commit - get commit message
        print("\nEnter commit message (or press Enter for default):")
        commit_msg = input("> ").strip()
        
        if not commit_msg:
            commit_msg = "conversation-end: save progress"
        
        # Stage all changes
        print("\nStaging all changes...")
        add_result = subprocess.run(
            ["git", "add", "-A"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            check=False
        )
        
        if add_result.returncode != 0:
            print(f"❌ Failed to stage changes: {add_result.stderr}")
            return
        
        print("✓ Changes staged")
        
        # Commit
        print(f"Committing with message: '{commit_msg}'...")
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            check=False
        )
        
        if commit_result.returncode != 0:
            print(f"❌ Commit failed: {commit_result.stderr}")
            return
        
        # Show commit summary
        print("✅ Changes committed successfully\n")
        print(commit_result.stdout)
        
        # Log the commit
        log_action(f"Git commit: {commit_msg}")
        
    except Exception as e:
        print(f"⚠️  Git status check failed: {e}")
        logger.debug("Git check error details", exc_info=True)


def timeline_update_check():
    """
    Check for timeline-worthy changes and auto-write timeline entry
    This is Phase 4.5 - captures system changes in timeline (AUTOMATIC, no prompts)
    """
    print("\n" + "="*70)
    print("PHASE 4.5: SYSTEM TIMELINE AUTO-UPDATE")
    print("="*70)
    print("\nScanning for timeline-worthy changes...\n")
    
    if not TIMELINE_AUTOMATION_AVAILABLE:
        print("  → Timeline automation not available, skipping")
        return
    
    try:
        # Use git status to find recently changed files (more accurate than time-based)
        import subprocess
        
        # Get uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            check=False
        )
        
        if status_result.returncode != 0:
            print("  → No git repository, using workspace scan")
            # Fallback to workspace-based detection
            from timeline_automation_module import TimelineDetector
            detector = TimelineDetector()
            
            is_worthy, suggested_entry = detector.analyze_file_changes(WORKSPACE)
            
            if not is_worthy:
                print("  → No timeline-worthy changes detected")
                return
            
            # Auto-write (no prompt)
            entry = detector.create_entry(**suggested_entry)
            success = detector.write_entry(entry)
            
            if success:
                print(f"  ✅ Timeline updated: {entry['title']}")
                print(f"     Category: {entry['category']} | Impact: {entry['impact']}")
                print(f"     Entry ID: {entry['entry_id']}")
            return
        
        # Parse git status output for N5-relevant files
        changes = status_result.stdout.strip()
        
        if not changes:
            print("  → No changes detected")
            return
        
        # Scan for high-signal N5 file changes
        new_commands = []
        modified_scripts = []
        
        for line in changes.split('\n'):
            if not line.strip():
                continue
            
            # Format: "XY filename"
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            
            status_code = parts[0]
            filepath = parts[1]
            
            # New command files
            if 'Recipes/' in filepath and filepath.endswith('.md'):
                if status_code.startswith('?') or status_code.startswith('A'):
                    cmd_name = Path(filepath).stem
                    new_commands.append(cmd_name)
            
            # Modified scripts
            if 'N5/scripts/' in filepath and filepath.startswith('n5_') and filepath.endswith('.py'):
                if status_code.startswith('M') or status_code.startswith('A'):
                    modified_scripts.append(Path(filepath).name)
        
        # Determine if timeline-worthy
        has_new_commands = len(new_commands) > 0
        has_multiple_scripts = len(modified_scripts) >= 2
        
        if not (has_new_commands or has_multiple_scripts):
            print("  → No timeline-worthy changes detected")
            return
        
        # Generate entry automatically
        from timeline_automation_module import TimelineDetector
        detector = TimelineDetector()
        
        if has_new_commands:
            title = f"New command(s): {', '.join(new_commands)}"
            description = f"Created {len(new_commands)} new command(s): {', '.join(new_commands[:3])}"
            category = "command"
            components = [f"Recipes/{category}/{cmd}.md" for cmd in new_commands]
            impact = "medium"
            tags = ["automation"]
        else:
            title = "System script updates"
            description = f"Updated {len(modified_scripts)} system scripts: {', '.join(modified_scripts[:3])}"
            category = "infrastructure"
            components = modified_scripts
            impact = "low"
            tags = ["maintenance"]
        
        # Create and write entry (no prompt)
        entry = detector.create_entry(
            title=title,
            description=description,
            category=category,
            components=components,
            impact=impact,
            status='completed',
            tags=tags
        )
        
        success = detector.write_entry(entry)
        
        if success:
            print(f"  ✅ Timeline updated: {entry['title']}")
            print(f"     Category: {entry['category']} | Impact: {entry['impact']}")
            if components:
                print(f"     Components: {len(components)} file(s)")
            print(f"     Entry ID: {entry['entry_id']}")
        
    except Exception as e:
        print(f"  ⚠️  Timeline check skipped: {e}")
        logger.debug(f"Timeline check error details", exc_info=True)


def registry_closure():
    """
    Phase 5: Close conversation in registry
    - Mark conversation as completed
    - Link AAR file if generated
    - Import learnings from lessons system
    """
    print("\n" + "="*70)
    print("PHASE 5: REGISTRY CLOSURE")
    print("="*70)
    
    if not CONVERSATION_REGISTRY_AVAILABLE:
        print("⚠️  Conversation registry not available, skipping")
        return
    
    if not CONVERSATION_WS:
        print("⚠️  Conversation workspace not detected, skipping")
        return
    
    try:
        convo_id = CONVERSATION_WS.name
        if not convo_id.startswith("con_"):
            print(f"⚠️  Invalid conversation ID: {convo_id}")
            return
        
        registry = ConversationRegistry()
        
        # Check if conversation exists in registry
        convo = registry.get(convo_id)
        if not convo:
            print(f"⚠️  Conversation {convo_id} not found in registry")
            print("   (It will be tracked in future conversations)")
            return
        
        print(f"\nClosing conversation: {convo_id}")
        
        # Find AAR file
        aar_path = None
        aar_candidates = list(CONVERSATION_WS.glob("*AAR*.md")) + list(CONVERSATION_WS.glob("*aar*.md"))
        if aar_candidates:
            aar_path = str(aar_candidates[0].relative_to(Path("/home")))
            print(f"  Found AAR: {aar_path}")
        
        # Close conversation
        success = registry.close_conversation(convo_id, aar_path=aar_path)
        
        if success:
            print(f"✓ Conversation closed in registry")
            print(f"  Status: completed")
            print(f"  Timestamp: {datetime.now().isoformat()}")
            
            # Try to import learnings
            lessons_dir = WORKSPACE / "Knowledge/lessons"
            if lessons_dir.exists():
                print("\n  Checking for related learnings...")
                lesson_files = list(lessons_dir.glob(f"*{convo_id}*.json")) + list(lessons_dir.glob(f"*{convo_id}*.md"))
                
                if lesson_files:
                    print(f"  Found {len(lesson_files)} lesson file(s)")
                    for lesson_file in lesson_files[:3]:  # Import up to 3
                        print(f"    • {lesson_file.name}")
                else:
                    print("  No lesson files found for this conversation")
        else:
            print("⚠️  Failed to close conversation in registry")
            
    except Exception as e:
        logger.warning(f"Registry closure failed: {e}")
        logger.debug("Registry closure error", exc_info=True)


def archive_promotion():
    """
    Phase 6: Archive Promotion
    Auto-promote significant conversations to Documents/Archive based on rules
    See: N5/prefs/operations/archive-promotion.md
    """
    print("\n" + "="*70)
    print("PHASE 6: ARCHIVE PROMOTION CHECK")
    print("="*70)
    
    if not CONVERSATION_REGISTRY_AVAILABLE:
        print("⚠️  Conversation registry not available, skipping promotion")
        return
    
    if not CONVERSATION_WS:
        print("⚠️  Conversation workspace not detected, skipping promotion")
        return
    
    try:
        convo_id = CONVERSATION_WS.name
        if not convo_id.startswith("con_"):
            print(f"⚠️  Invalid conversation ID: {convo_id}")
            return
        
        registry = ConversationRegistry()
        convo = registry.get(convo_id)
        
        if not convo:
            print(f"⚠️  Conversation {convo_id} not in registry, skipping promotion")
            return
        
        # Check promotion rules
        should_promote = False
        promotion_reason = None
        
        # Rule 1: Worker tag
        tags = convo.get('tags', '').split(',') if convo.get('tags') else []
        tags = [t.strip().lower() for t in tags]
        
        if 'worker' in tags:
            should_promote = True
            promotion_reason = "worker completion"
        
        # Rule 2: Deliverable tag
        if 'deliverable' in tags:
            should_promote = True
            promotion_reason = "explicit deliverable tag"
        
        # Rule 3: Check deliverables registry (future)
        # TODO: Implement when deliverables registry API available
        
        if not should_promote:
            print("  No promotion criteria met")
            print("  → Archive remains in N5/logs/threads only")
            return
        
        print(f"\n✨ Promotion criteria met: {promotion_reason}")
        
        # Find source archive in N5/logs/threads
        threads_dir = WORKSPACE / "N5/logs/threads"
        if not threads_dir.exists():
            print("⚠️  N5/logs/threads directory not found")
            return
        
        # Find most recent archive matching conversation
        archives = sorted(threads_dir.glob(f"*_{convo_id[:4]}"), reverse=True)
        if not archives:
            print(f"⚠️  No archive found in N5/logs/threads for {convo_id}")
            return
        
        source_archive = archives[0]
        print(f"  Source: {source_archive.name}")
        
        # Generate target path in Documents/Archive
        archive_name = source_archive.name
        # Extract date and title parts
        parts = archive_name.split('_', 2)
        if len(parts) >= 3:
            date_part = parts[0]  # YYYY-MM-DD-HHMM
            title_part = parts[1]  # Title with emoji
            # Clean for Documents/Archive (remove time, keep date)
            clean_date = date_part[:10]  # YYYY-MM-DD only
            target_name = f"{clean_date}-{title_part}"
        else:
            target_name = archive_name
        
        target_archive = WORKSPACE / "Documents/Archive" / target_name
        
        # Check if already promoted
        if target_archive.exists():
            print(f"  ✓ Already promoted to: {target_name}")
            return
        
        print(f"  Target: Documents/Archive/{target_name}")
        print(f"\n  Copying archive...")
        
        # Copy archive
        shutil.copytree(source_archive, target_archive, dirs_exist_ok=False)
        
        # Update README with promotion metadata
        readme_path = target_archive / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Add promotion metadata at top
            metadata = f"""---
promoted_from: N5/logs/threads/{source_archive.name}
promoted_date: {datetime.now().isoformat()}
promotion_reason: {promotion_reason}
conversation_id: {convo_id}
---

"""
            with open(readme_path, 'w') as f:
                f.write(metadata + content)
        
        print(f"\n✅ Archive promoted successfully!")
        print(f"   Location: Documents/Archive/{target_name}")
        print(f"   Reason: {promotion_reason}")
        print(f"   SSOT remains: N5/logs/threads/{source_archive.name}")
        
    except Exception as e:
        logger.error(f"Archive promotion failed: {e}", exc_info=True)
        print(f"⚠️  Archive promotion error: {e}")
        print("   → Continuing without promotion")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="N5 Conversation End-Step")
    parser.add_argument("--auto", action="store_true", 
                       help="Auto-approve all prompts (non-interactive mode)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without executing")
    parser.add_argument("--skip-cleanup", action="store_true",
                       help="Skip workspace root cleanup phase")
    parser.add_argument("--skip-placeholder-scan", action="store_true",
                       help="Skip placeholder detection phase")
    
    args = parser.parse_args()
    
    # Auto-enable --auto if in automated environment
    if os.getenv("ZO_AUTOMATED") == "true" or os.getenv("CI") == "true":
        args.auto = True
        logger.info("Auto mode enabled via environment")
    
    return args


def main():
    """Main execution"""
    args = parse_args()
    
    logger.info(f"Starting conversation-end (auto={args.auto}, dry_run={args.dry_run})")
    
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
    
    # NEW: Phase -0.5 - Enrich session state
    enrich_session_state()
    
    # NEW: Phase -1 - Extract lessons
    extract_lessons()
    
    # NEW: Phase 0 - Generate AAR with title generation
    generate_thread_export()
    
    # Step 1: Inventory
    print("\n" + "="*70)
    print("PHASE 1: FILE ORGANIZATION")
    print("="*70)
    print("\nStep 1: Inventorying files...")
    files_by_category = inventory_workspace()
    
    if not any(files_by_category.values()):
        print("\n✓ No files to organize - conversation workspace is clean")
        # Continue to subsequent phases even when no files to organize
        confirmed = True  # Skip to cleanup phases
    else:
        # Step 2: Propose
        proposal = propose_organization(files_by_category, auto_mode=args.auto)
        print(proposal)
        
        # Step 3: Get confirmation
        if args.auto:
            confirmed = True
        else:
            response = input("\n> ").strip().lower()
            confirmed = response in ['y', 'yes', '']
    
    # Step 4: Execute (or skip if no files)
    if confirmed:
        if any(files_by_category.values()):
            result = execute_organization(files_by_category, confirmed=True)
            
            # Log conversation end
            log_action(f"Conversation ended: {result['moved']} moved, {result['deleted']} deleted")
        
        # NEW: Phase 2 - Workspace root cleanup
        print("\n" + "="*70)
        print("CONTINUING TO WORKSPACE ROOT CLEANUP...")
        print("="*70)
        cleanup_workspace_root()
        
        # NEW: Phase 2.5 - Placeholder scan
        print("\n" + "="*70)
        print("SCANNING FOR PLACEHOLDERS & STUBS...")
        print("="*70)
        if not placeholder_scan(auto_mode=args.auto):
            sys.exit(1)
        
        # NEW: Phase 2.75 - Output review summary
        print("\n" + "="*70)
        print("PHASE 2.75: OUTPUT REVIEW SUMMARY")
        print("="*70)
        try:
            from review_manager import ReviewManager
            manager = ReviewManager()
            # Attempt to detect conversation id
            convo_id = os.getenv("N5_CONVERSATION_ID")
            if not convo_id and CONVERSATION_WS:
                convo_id = CONVERSATION_WS.name
            tracked = manager.list_reviews(conversation_id=convo_id) if convo_id else []
            if tracked:
                print(f"\n📋 {len(tracked)} output(s) flagged for review in this conversation:\n")
                for r in tracked[:10]:
                    title = r.get('title') or r.get('reference')
                    status = r['review'].get('status')
                    sent = r['review'].get('sentiment') or '-'
                    imp = r['review'].get('improvement_notes') or {}
                    change = imp.get('what_to_change')
                    optimal = imp.get('optimal_state')
                    print(f" • {title}\n   Status: {status} | Sentiment: {sent}")
                    if change:
                        print(f"   📝 Change: {change}")
                    if optimal:
                        print(f"   📝 Optimal: {optimal}")
                if len(tracked) > 10:
                    print(f"   … and {len(tracked)-10} more")
            else:
                # No tracked outputs; scan for likely deliverables
                candidates = []
                patterns = [
                    ("*.md", 100),
                    ("*email*.md", 50),
                    ("*follow*up*.md", 50),
                    ("*report*.md", 500),
                    ("*analysis*.md", 300),
                    ("*.png", 0),
                    ("*.jpg", 0),
                ]
                exclude = ["temp_", "test_", "scratch_", "BUILD_MAP", "SESSION_STATE"]
                if CONVERSATION_WS and CONVERSATION_WS.exists():
                    for ptn, min_words in patterns:
                        for f in CONVERSATION_WS.rglob(ptn):
                            if not f.is_file():
                                continue
                            name = f.name
                            if any(x in name for x in exclude):
                                continue
                            if f.suffix.lower() == ".md":
                                try:
                                    text = f.read_text()
                                    words = len(text.split())
                                    if words < min_words:
                                        continue
                                except Exception:
                                    continue
                            candidates.append((f, min_words))
                if candidates:
                    print("\n⚠️  DELIVERABLE REVIEW REMINDER\n")
                    print("Found potential outputs to flag for review:")
                    for f, _ in candidates[:5]:
                        print(f" • {f}")
                    if len(candidates) > 5:
                        print(f"   … and {len(candidates)-5} more")
                    print("\nTip: Flag now to capture improvement notes while context is fresh:")
                    print("   n5 review add <file> --sentiment <rating> \\")
                    print("     --improve '<what to change>' \\")
                    print("     --optimal '<ideal state>'")
                    if not args.auto:
                        choice = input("\nSkip reminder and continue? (Y/n): ").strip().lower()
                        if choice not in ["", "y", "yes"]:
                            print("Continuing without reminder acknowledged.")
                else:
                    print("\nNo tracked outputs and no deliverables detected.")
        except Exception as e:
            print(f"⚠️  Review summary skipped: {e}")
            logger.debug("Review summary error", exc_info=True)
        
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
        
        # NEW: Phase 3.5 - Build tracker archival
        archive_build_tasks()
        
        # NEW: Phase 4 - Git status check
        git_status_check()
        
        # NEW: Phase 4.5 - Timeline update check
        timeline_update_check()
        
        # NEW: Phase 5 - Registry closure
        registry_closure()
        
        # NEW: Phase 6 - Archive promotion
        archive_promotion()
        
        # Final summary
        print("\n" + "="*70)
        print("✅ CONVERSATION END-STEP COMPLETE")
        print("="*70)
    else:
        print("\n✓ Organization cancelled - files remain in conversation workspace")


if __name__ == "__main__":
    main()
