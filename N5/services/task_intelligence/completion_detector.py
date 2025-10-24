#!/usr/bin/env python3
"""
Task completion detection service.
Monitors user actions and detects when tasks are completed.
"""
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
TASK_REGISTRY = WORKSPACE / "N5/data/task_registry.jsonl"
DETECTION_LOG = WORKSPACE / "N5/logs/task_completions.log"

class TaskRegistry:
    """Track all tasks created by Zo."""
    
    def __init__(self):
        self.registry_file = TASK_REGISTRY
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
    def add_task(self, task: Dict):
        """Add newly created task to registry."""
        task['created_at'] = datetime.now().isoformat()
        task['status'] = 'pending'
        task['completion_detected_at'] = None
        
        with open(self.registry_file, 'a') as f:
            f.write(json.dumps(task) + '\n')
        
        logger.info(f"Registered task: {task['title']}")
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks."""
        if not self.registry_file.exists():
            return []
        
        tasks = []
        with open(self.registry_file, 'r') as f:
            for line in f:
                task = json.loads(line)
                if task.get('status') == 'pending':
                    tasks.append(task)
        
        return tasks
    
    def mark_complete(self, task_id: str, reason: str):
        """Mark task as complete."""
        # Read all tasks
        tasks = []
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                tasks = [json.loads(line) for line in f]
        
        # Update target task
        for task in tasks:
            if task.get('id') == task_id:
                task['status'] = 'completed'
                task['completion_detected_at'] = datetime.now().isoformat()
                task['completion_reason'] = reason
                break
        
        # Rewrite file
        with open(self.registry_file, 'w') as f:
            for task in tasks:
                f.write(json.dumps(task) + '\n')
        
        logger.info(f"Marked complete: {task_id} - {reason}")

class CompletionDetector:
    """Detect when tasks are completed based on user actions."""
    
    def __init__(self):
        self.registry = TaskRegistry()
    
    def check_gmail_actions(self, task: Dict) -> Optional[str]:
        """Check if task completion signals exist in Gmail."""
        title_lower = task['title'].lower()
        
        # Detection patterns
        patterns = {
            'send': ('email sent', 'from:vrijen OR from:attawar'),
            'draft': ('draft created', 'in:drafts'),
            'review': ('replied', 'from:vrijen'),
            'reach out': ('email sent', 'from:vrijen'),
            'follow up': ('email sent', 'from:vrijen'),
            'connect': ('intro sent', 'from:vrijen')
        }
        
        for keyword, (action, query) in patterns.items():
            if keyword in title_lower:
                # Check if action happened in Gmail
                # This would use use_app_gmail to search
                # For now, return pattern for structure
                return f"Detected: {action} (would check Gmail with: {query})"
        
        return None
    
    def check_calendar_events(self, task: Dict) -> Optional[str]:
        """Check if task-related calendar event occurred."""
        # Look for calendar events matching task
        # This would use use_app_google_calendar
        return None
    
    def check_file_changes(self, task: Dict) -> Optional[str]:
        """Check if related files were modified."""
        title_lower = task['title'].lower()
        
        # Extract potential file/document references
        if 'recap' in title_lower or 'document' in title_lower:
            # Check for recent files created/modified
            # Look in Records/Company for new .md files
            return None
        
        return None
    
    def detect_completion(self, task: Dict) -> Optional[str]:
        """
        Check all signals to detect if task is complete.
        Returns reason string if completed, None otherwise.
        """
        # Check multiple sources
        gmail_signal = self.check_gmail_actions(task)
        if gmail_signal:
            return gmail_signal
        
        calendar_signal = self.check_calendar_events(task)
        if calendar_signal:
            return calendar_signal
        
        file_signal = self.check_file_changes(task)
        if file_signal:
            return file_signal
        
        return None
    
    def scan_pending_tasks(self):
        """Scan all pending tasks for completion signals."""
        pending = self.registry.get_pending_tasks()
        
        logger.info(f"Scanning {len(pending)} pending tasks")
        
        for task in pending:
            reason = self.detect_completion(task)
            if reason:
                logger.info(f"✓ Completion detected: {task['title']}")
                logger.info(f"  Reason: {reason}")
                
                # Mark as complete
                self.registry.mark_complete(task.get('id'), reason)
                
                # TODO: Send completion to Aki
                # Email: "Complete: [task title]"
                logger.info(f"  Would send to Aki: Complete task")

def run_detection_loop(interval_seconds: int = 300):
    """Run continuous detection loop."""
    detector = CompletionDetector()
    
    logger.info(f"✓ Starting completion detector (interval: {interval_seconds}s)")
    
    while True:
        try:
            detector.scan_pending_tasks()
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("\n✓ Detector stopped")
            break
        except Exception as e:
            logger.error(f"Detection error: {e}", exc_info=True)
            time.sleep(interval_seconds)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Task completion detector')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    args = parser.parse_args()
    
    run_detection_loop(args.interval)
