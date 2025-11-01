#!/usr/bin/env python3
"""
Conversation-End Executor

Executes approved actions from a proposal JSON file.
Supports dry-run mode and rollback capability.
"""

import os
import json
import logging
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Supported action types"""
    MOVE = "move"
    ARCHIVE = "archive"
    DELETE = "delete"
    IGNORE = "ignore"


class ExecutionStatus(Enum):
    """Execution status for actions"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ConversationEndExecutor:
    """Execute conversation-end proposals with atomicity and rollback"""
    
    def __init__(self, proposal_path: Path, dry_run: bool = False):
        self.proposal_path = Path(proposal_path)
        self.dry_run = dry_run
        self.proposal = self._load_proposal()
        self.transaction_log: List[Dict[str, Any]] = []
        self.executed_actions: List[Dict[str, Any]] = []
        
    def _load_proposal(self) -> Dict[str, Any]:
        """Load and validate proposal JSON"""
        try:
            with open(self.proposal_path, 'r') as f:
                proposal = json.load(f)
            
            # Validate required fields
            required = ["conversation_id", "title", "actions"]
            missing = [f for f in required if f not in proposal]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")
            
            return proposal
        except Exception as e:
            logger.error(f"Failed to load proposal: {e}")
            raise
    
    def execute_proposal(self) -> int:
        """
        Execute all approved actions in the proposal
        
        Returns:
            0 on success, 1 on failure
        """
        try:
            logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Executing proposal for {self.proposal['conversation_id']}")
            logger.info(f"Title: {self.proposal['title']}")
            
            # Check for conflicts
            if self.proposal.get("requires_resolution", False):
                conflicts = self.proposal.get("conflicts", [])
                logger.error(f"Proposal has unresolved conflicts: {len(conflicts)}")
                for conflict in conflicts:
                    logger.error(f"  - {conflict['type']}: {conflict['description']}")
                return 1
            
            # Filter approved actions
            approved_actions = [
                action for action in self.proposal["actions"]
                if action.get("approved", False) and action["action_type"] != "ignore"
            ]
            
            if not approved_actions:
                logger.warning("No approved actions to execute")
                return 0
            
            logger.info(f"Executing {len(approved_actions)} approved actions")
            
            # Pre-flight checks
            if not self._verify_preconditions(approved_actions):
                logger.error("Pre-flight checks failed")
                return 1
            
            # Execute actions
            success_count = 0
            failed_count = 0
            
            for idx, action in enumerate(approved_actions, 1):
                logger.info(f"Action {idx}/{len(approved_actions)}: {action['action_type']} {Path(action['source']).name}")
                
                try:
                    result = self._execute_action(action)
                    if result:
                        success_count += 1
                        self.executed_actions.append(action)
                    else:
                        failed_count += 1
                        logger.warning(f"Action {idx} failed: {action['source']}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Action {idx} error: {e}", exc_info=True)
                    
                    # Fail fast - rollback on first error
                    if not self.dry_run:
                        logger.error("Error encountered, initiating rollback")
                        self.rollback()
                        return 1
            
            # Post-flight checks
            if not self.dry_run and not self._verify_postconditions():
                logger.error("Post-flight checks failed, initiating rollback")
                self.rollback()
                return 1
            
            # Write transaction log
            if not self.dry_run:
                self._write_transaction_log()
            
            logger.info(f"✓ Execution complete: {success_count} succeeded, {failed_count} failed")
            return 0 if failed_count == 0 else 1
            
        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            if not self.dry_run and self.executed_actions:
                logger.info("Attempting rollback due to exception")
                self.rollback()
            return 1
    
    def _verify_preconditions(self, actions: List[Dict[str, Any]]) -> bool:
        """
        Verify all preconditions before execution
        
        Checks:
        - Source files exist
        - Destinations don't exist (P5: anti-overwrite)
        - Parent directories can be created
        - No circular dependencies
        """
        logger.info("Verifying preconditions...")
        
        issues = []
        
        for action in actions:
            source = Path(action["source"])
            action_type = action["action_type"]
            
            # Check source exists
            if not source.exists():
                issues.append(f"Source does not exist: {source}")
                continue
            
            # For moves and archives, check destination
            if action_type in ["move", "archive"]:
                dest = Path(action["destination"])
                
                # P5: Check destination doesn't exist
                if dest.exists():
                    issues.append(f"Destination exists (P5 violation): {dest}")
                
                # Check parent directory is writable
                parent = dest.parent
                if parent.exists() and not os.access(parent, os.W_OK):
                    issues.append(f"Destination parent not writable: {parent}")
        
        # Check for duplicate destinations
        destinations = [
            action["destination"] for action in actions
            if action["action_type"] in ["move", "archive"]
        ]
        duplicates = [d for d in destinations if destinations.count(d) > 1]
        if duplicates:
            issues.append(f"Duplicate destinations detected: {set(duplicates)}")
        
        if issues:
            logger.error(f"Precondition check failed ({len(issues)} issues):")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        
        logger.info("✓ Preconditions verified")
        return True
    
    def _verify_postconditions(self) -> bool:
        """Verify state after execution"""
        logger.info("Verifying postconditions...")
        
        issues = []
        
        for action in self.executed_actions:
            source = Path(action["source"])
            action_type = action["action_type"]
            
            if action_type in ["move", "archive"]:
                dest = Path(action["destination"])
                
                # Check source no longer exists
                if source.exists():
                    issues.append(f"Source still exists after {action_type}: {source}")
                
                # Check destination exists
                if not dest.exists():
                    issues.append(f"Destination not created: {dest}")
                
                # Check file size matches (if applicable)
                # Note: Can't check original size since source was moved
            
            elif action_type == "delete":
                if source.exists():
                    issues.append(f"Source still exists after delete: {source}")
        
        if issues:
            logger.error(f"Postcondition check failed ({len(issues)} issues):")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        
        logger.info("✓ Postconditions verified")
        return True
    
    def _execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Execute a single action
        
        Returns:
            True on success, False on failure
        """
        action_type = action["action_type"]
        source = Path(action["source"])
        
        try:
            if action_type == "move":
                return self._execute_move(source, Path(action["destination"]), action)
            elif action_type == "archive":
                return self._execute_archive(source, Path(action["destination"]), action)
            elif action_type == "delete":
                return self._execute_delete(source, action)
            elif action_type == "ignore":
                return True  # No-op
            else:
                logger.error(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            return False
    
    def _execute_move(self, source: Path, dest: Path, action: Dict[str, Any]) -> bool:
        """
        Move file with verification
        
        P5: Check destination doesn't exist
        P19: Error handling with context
        """
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would move {source} → {dest}")
                return True
            
            # P5: Verify destination doesn't exist
            if dest.exists():
                logger.error(f"P5 violation: Destination exists: {dest}")
                return False
            
            # Create parent directory if needed
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Log transaction before execution
            self._log_transaction("move", source, dest, action)
            
            # Execute move
            shutil.move(str(source), str(dest))
            
            # Verify
            if not dest.exists():
                logger.error(f"Move failed verification: {dest} not created")
                return False
            
            logger.info(f"✓ Moved {source.name} → {dest}")
            return True
            
        except Exception as e:
            logger.error(f"Move failed: {source} → {dest}: {e}", exc_info=True)
            return False
    
    def _execute_archive(self, source: Path, dest: Path, action: Dict[str, Any]) -> bool:
        """
        Archive file (move to archive location)
        
        Same as move but typically to archive directory structure
        """
        return self._execute_move(source, dest, action)
    
    def _execute_delete(self, source: Path, action: Dict[str, Any]) -> bool:
        """
        Delete file with backup to transaction log location
        
        Creates safety backup before deletion for rollback capability
        """
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would delete {source}")
                return True
            
            # Create backup location
            backup_dir = Path(f"/tmp/conversation_end_backups/{self.proposal['conversation_id']}")
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / source.name
            
            # Make backup copy first
            shutil.copy2(str(source), str(backup_path))
            
            # Log transaction
            self._log_transaction("delete", source, backup_path, action)
            
            # Execute delete
            source.unlink()
            
            # Verify
            if source.exists():
                logger.error(f"Delete failed verification: {source} still exists")
                return False
            
            logger.info(f"✓ Deleted {source.name} (backup: {backup_path})")
            return True
            
        except Exception as e:
            logger.error(f"Delete failed: {source}: {e}", exc_info=True)
            return False
    
    def _log_transaction(self, operation: str, source: Path, dest: Optional[Path], action: Dict[str, Any]):
        """Log transaction for rollback capability"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "source": str(source),
            "destination": str(dest) if dest else None,
            "action": action
        }
        self.transaction_log.append(entry)
    
    def _write_transaction_log(self):
        """Write transaction log to disk"""
        log_path = Path(f"/tmp/conversation_end_transaction_{self.proposal['conversation_id']}.log")
        
        try:
            with open(log_path, 'w') as f:
                json.dump({
                    "conversation_id": self.proposal["conversation_id"],
                    "title": self.proposal["title"],
                    "executed_at": datetime.now().isoformat(),
                    "transactions": self.transaction_log
                }, f, indent=2)
            
            logger.info(f"✓ Transaction log written: {log_path}")
            
        except Exception as e:
            logger.error(f"Failed to write transaction log: {e}", exc_info=True)
    
    def rollback(self) -> bool:
        """
        Rollback all executed actions in reverse order
        
        Returns:
            True on success, False on failure
        """
        logger.warning(f"Rolling back {len(self.transaction_log)} transactions")
        
        if not self.transaction_log:
            logger.info("No transactions to rollback")
            return True
        
        success_count = 0
        failed_count = 0
        
        # Rollback in reverse order
        for entry in reversed(self.transaction_log):
            try:
                operation = entry["operation"]
                source = Path(entry["source"])
                dest = Path(entry["destination"]) if entry["destination"] else None
                
                if operation == "move" or operation == "archive":
                    # Reverse: move destination back to source
                    if dest and dest.exists():
                        shutil.move(str(dest), str(source))
                        logger.info(f"✓ Rolled back move: {dest} → {source}")
                        success_count += 1
                    else:
                        logger.warning(f"Cannot rollback move: destination missing: {dest}")
                        failed_count += 1
                
                elif operation == "delete":
                    # Reverse: restore from backup
                    if dest and dest.exists():
                        shutil.copy2(str(dest), str(source))
                        logger.info(f"✓ Rolled back delete: restored {source}")
                        success_count += 1
                    else:
                        logger.warning(f"Cannot rollback delete: backup missing: {dest}")
                        failed_count += 1
                        
            except Exception as e:
                logger.error(f"Rollback failed for entry: {e}", exc_info=True)
                failed_count += 1
        
        logger.info(f"Rollback complete: {success_count} succeeded, {failed_count} failed")
        return failed_count == 0


def rollback_from_log(log_path: Path) -> int:
    """Rollback from a transaction log file"""
    try:
        with open(log_path, 'r') as f:
            log_data = json.load(f)
        
        logger.info(f"Rolling back from log: {log_path}")
        logger.info(f"Conversation: {log_data['conversation_id']}")
        logger.info(f"Executed at: {log_data['executed_at']}")
        
        transaction_log = log_data.get("transactions", [])
        
        success_count = 0
        failed_count = 0
        
        for entry in reversed(transaction_log):
            try:
                operation = entry["operation"]
                source = Path(entry["source"])
                dest = Path(entry["destination"]) if entry["destination"] else None
                
                if operation in ["move", "archive"] and dest and dest.exists():
                    shutil.move(str(dest), str(source))
                    logger.info(f"✓ Rolled back {operation}: {dest} → {source}")
                    success_count += 1
                
                elif operation == "delete" and dest and dest.exists():
                    shutil.copy2(str(dest), str(source))
                    logger.info(f"✓ Restored deleted file: {source}")
                    success_count += 1
                
                else:
                    logger.warning(f"Cannot rollback {operation}: missing files")
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Rollback failed: {e}", exc_info=True)
                failed_count += 1
        
        logger.info(f"Rollback complete: {success_count} succeeded, {failed_count} failed")
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed to load transaction log: {e}", exc_info=True)
        return 1


def test_rollback() -> int:
    """Test rollback capability with synthetic data"""
    import tempfile
    
    logger.info("Testing rollback capability...")
    
    try:
        # Create test environment
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create test files
            source_dir = tmp / "source"
            dest_dir = tmp / "dest"
            source_dir.mkdir()
            dest_dir.mkdir()
            
            test_file = source_dir / "test.txt"
            test_file.write_text("Test content")
            
            # Create proposal
            proposal = {
                "conversation_id": "con_TEST0000000000",
                "title": "Rollback Test",
                "actions": [
                    {
                        "action_type": "move",
                        "source": str(test_file),
                        "destination": str(dest_dir / "test.txt"),
                        "approved": True,
                        "reason": "Test move",
                        "confidence": "high"
                    }
                ],
                "requires_resolution": False
            }
            
            proposal_path = tmp / "proposal.json"
            proposal_path.write_text(json.dumps(proposal))
            
            # Execute
            executor = ConversationEndExecutor(proposal_path, dry_run=False)
            result = executor.execute_proposal()
            
            if result != 0:
                logger.error("Test execution failed")
                return 1
            
            # Verify file moved
            if test_file.exists():
                logger.error("Test failed: source still exists")
                return 1
            
            if not (dest_dir / "test.txt").exists():
                logger.error("Test failed: destination not created")
                return 1
            
            logger.info("✓ Execution test passed")
            
            # Test rollback
            success = executor.rollback()
            
            if not success:
                logger.error("Rollback failed")
                return 1
            
            # Verify rollback
            if not test_file.exists():
                logger.error("Test failed: source not restored")
                return 1
            
            if (dest_dir / "test.txt").exists():
                logger.error("Test failed: destination not removed")
                return 1
            
            logger.info("✓ Rollback test passed")
            
        return 0
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1


# New function for normalization
def normalize_transients(output_text: str) -> str:
    output_text = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '<TIMESTAMP>', output_text)
    output_text = re.sub(r'con_[A-Za-z0-9]{16}', 'CONV_ID', output_text)
    output_text = re.sub(r'\b\d+\b', '<COUNT>', output_text)  # Naive, consider context
    return output_text


# Validation function to check output conformity

def validate_output(output_text: str, template_path: str) -> bool:
    with open(template_path, 'r') as f:
        template = f.read()

    # Basic validation: all headings must appear
    headings = ['✅ Conversation Closed Successfully', 'Summary', 'What Was Built / Accomplished', 'Debugger Verification Results', 'Known Limitations', 'Artifacts Archived', 'Key Files Created', 'System Status']
    return all(h in output_text for h in headings)


# Wrap existing presentation logic
def present_final_output(output_text: str, args) -> None:
    output_text = normalize_transients(output_text)

    if not validate_output(output_text, '/home/workspace/N5/prefs/operations/conversation-end-output-template.md'):
        raise ValueError('Final output does not conform to template - aborting presentation')

    # Handle --require-confirm flag
    if args.require_confirm:
        confirmed = input('Confirm archival and closure? (yes/no): ')
        if confirmed.lower() != 'yes':
            print('User declined, aborting.')
            return

    print(output_text)


def normalize_transient_data(output_str: str) -> str:
    # Normalize timestamps
    output_str = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([^ ]*)', '<TIMESTAMP>', output_str)
    # Normalize session IDs
    output_str = re.sub(r'con_[A-Za-z0-9]{16}', '<CONVO_ID>', output_str)
    # Normalize counts (e.g., file counts)
    output_str = re.sub(r'\b\d+ files\b', '<FILE_COUNT> files', output_str)
    return output_str


def main(dry_run: bool = False, proposal: Optional[str] = None, 
         rollback: Optional[str] = None, test: bool = False) -> int:
    """Main entry point"""
    try:
        if test:
            return test_rollback()
        
        if rollback:
            return rollback_from_log(Path(rollback))
        
        if not proposal:
            logger.error("Must provide --proposal or --rollback or --test-rollback")
            return 1
        
        executor = ConversationEndExecutor(Path(proposal), dry_run=dry_run)
        return executor.execute_proposal()
        
    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import os
    
    parser = argparse.ArgumentParser(description="Execute conversation-end proposals")
    parser.add_argument("--proposal", help="Path to proposal JSON")
    parser.add_argument("--dry-run", action="store_true", help="Preview without execution")
    parser.add_argument("--rollback", help="Path to transaction log for rollback")
    parser.add_argument("--test-rollback", action="store_true", help="Test rollback capability")
    
    args = parser.parse_args()
    
    exit(main(
        dry_run=args.dry_run,
        proposal=args.proposal,
        rollback=args.rollback,
        test=args.test_rollback
    ))
