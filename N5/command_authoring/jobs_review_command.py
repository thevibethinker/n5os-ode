#!/usr/bin/env python3
"""
N5 OS Command Authoring: Jobs Review Command
Interactive TUI command for reviewing and approving PENDING jobs with Command Authoring framework integration.

This module implements the jobs-review command following N5 OS Command Authoring patterns:
- Full telemetry and logging integration
- Interactive TUI with error handling
- Safe state management with atomic operations
- Comprehensive audit trail
- Rollback capabilities
"""

import json
import logging
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

class JobsReviewCommand:
    """
    Jobs review command with full Command Authoring framework integration.
    
    Implements interactive review process with comprehensive telemetry, validation,
    error handling, and safe state management following N5 OS Command Authoring patterns.
    """
    
    def __init__(self):
        """Initialize command with telemetry and configuration."""
        self.command_id = str(uuid.uuid4())
        self.start_time = datetime.utcnow()
        self.telemetry = {
            'command_id': self.command_id,
            'start_time': self.start_time.isoformat() + 'Z',
            'metrics': {},
            'errors': [],
            'warnings': [],
            'stages': {},
            'review_actions': []
        }
        
        # Setup logging
        self.logger = logging.getLogger('jobs_review')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Set target file paths
        self.scraped_jobs_file = Path('/home/workspace/N5/jobs/lists/jobs-scraped.jsonl')
        self.private_jobs_file = Path('/home/workspace/N5/jobs/lists/jobs-private.jsonl')
        
        # Review session state
        self.session_state = {
            'jobs_reviewed': 0,
            'jobs_approved': 0,
            'jobs_rejected': 0,
            'jobs_skipped': 0,
            'review_actions': [],
            'modified_files': []
        }
    
    def log_stage_start(self, stage: str) -> None:
        """Log the start of a processing stage."""
        self.telemetry['stages'][stage] = {
            'start_time': datetime.utcnow().isoformat() + 'Z',
            'status': 'in_progress'
        }
        self.logger.info(f"Stage started: {stage}")
    
    def log_stage_complete(self, stage: str, metrics: Dict[str, Any] = None) -> None:
        """Log completion of a processing stage."""
        if stage in self.telemetry['stages']:
            self.telemetry['stages'][stage]['end_time'] = datetime.utcnow().isoformat() + 'Z'
            self.telemetry['stages'][stage]['status'] = 'completed'
            if metrics:
                self.telemetry['stages'][stage]['metrics'] = metrics
        self.logger.info(f"Stage completed: {stage}")
    
    def log_error(self, error: str, stage: str = None) -> None:
        """Log an error with context."""
        error_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': error,
            'stage': stage,
            'command_id': self.command_id
        }
        self.telemetry['errors'].append(error_entry)
        self.logger.error(f"Error in {stage or 'unknown'}: {error}")
    
    def log_warning(self, warning: str, stage: str = None) -> None:
        """Log a warning with context."""
        warning_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'warning': warning,
            'stage': stage,
            'command_id': self.command_id
        }
        self.telemetry['warnings'].append(warning_entry)
        self.logger.warning(f"Warning in {stage or 'unknown'}: {warning}")
    
    def log_review_action(self, action: str, job_uid: str, job_title: str, job_company: str) -> None:
        """Log a review action for audit trail."""
        action_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'action': action,  # 'approve', 'reject', 'skip'
            'job_uid': job_uid,
            'job_title': job_title,
            'job_company': job_company,
            'command_id': self.command_id
        }
        self.telemetry['review_actions'].append(action_entry)
        self.session_state['review_actions'].append(action_entry)
        self.logger.info(f"Review action: {action} for {job_title} @ {job_company}")
    
    def load_jobs_for_review(self) -> Dict[str, Any]:
        """
        Load and analyze jobs available for review.
        
        Returns:
            Load results with jobs data and statistics
        """
        self.log_stage_start('load_jobs_for_review')
        
        load_result = {
            'success': True,
            'scraped_jobs': [],
            'private_jobs': [],
            'pending_scraped': [],
            'pending_private': [],
            'total_pending': 0,
            'files_found': {'scraped': False, 'private': False},
            'errors': []
        }
        
        # Load scraped jobs
        if self.scraped_jobs_file.exists():
            try:
                with open(self.scraped_jobs_file, 'r') as f:
                    scraped_jobs = [json.loads(line) for line in f if line.strip()]
                    load_result['scraped_jobs'] = scraped_jobs
                    load_result['files_found']['scraped'] = True
                    
                    # Filter pending jobs
                    pending_scraped = [job for job in scraped_jobs if job.get('status') == 'PENDING']
                    load_result['pending_scraped'] = pending_scraped
                    
                    self.logger.info(f"Loaded {len(scraped_jobs)} scraped jobs, {len(pending_scraped)} pending")
                    
            except Exception as e:
                load_result['errors'].append(f"Error loading scraped jobs: {str(e)}")
                self.log_error(f"Error loading scraped jobs: {str(e)}", 'load_jobs_for_review')
        else:
            self.log_warning("Scraped jobs file not found", 'load_jobs_for_review')
        
        # Load private jobs (for reference/context, typically these start as PENDING too)
        if self.private_jobs_file.exists():
            try:
                with open(self.private_jobs_file, 'r') as f:
                    private_jobs = [json.loads(line) for line in f if line.strip()]
                    load_result['private_jobs'] = private_jobs
                    load_result['files_found']['private'] = True
                    
                    # Filter pending jobs
                    pending_private = [job for job in private_jobs if job.get('status') == 'PENDING']
                    load_result['pending_private'] = pending_private
                    
                    self.logger.info(f"Loaded {len(private_jobs)} private jobs, {len(pending_private)} pending")
                    
            except Exception as e:
                load_result['errors'].append(f"Error loading private jobs: {str(e)}")
                self.log_error(f"Error loading private jobs: {str(e)}", 'load_jobs_for_review')
        else:
            self.log_warning("Private jobs file not found", 'load_jobs_for_review')
        
        # Calculate totals
        total_pending = len(load_result['pending_scraped']) + len(load_result['pending_private'])
        load_result['total_pending'] = total_pending
        
        if total_pending == 0:
            load_result['success'] = True  # Not an error, just no work to do
            self.log_warning("No pending jobs found for review", 'load_jobs_for_review')
        
        if load_result['errors']:
            load_result['success'] = False
        
        self.log_stage_complete('load_jobs_for_review', {
            'scraped_jobs_count': len(load_result['scraped_jobs']),
            'private_jobs_count': len(load_result['private_jobs']),
            'total_pending': total_pending,
            'files_found': load_result['files_found']
        })
        
        return load_result
    
    def display_job_for_review(self, job: Dict[str, Any], index: int, total: int) -> None:
        """
        Display a job in a user-friendly format for review.
        
        Args:
            job: Job record to display
            index: Current job index (1-based)
            total: Total number of jobs
        """
        print(f"\n{'='*60}")
        print(f"Job {index}/{total} - Review Required")
        print(f"{'='*60}")
        print(f"Title:    {job.get('title', 'N/A')}")
        print(f"Company:  {job.get('company', 'N/A')}")
        
        if job.get('location'):
            print(f"Location: {job.get('location')}")
        
        if job.get('salary'):
            print(f"Salary:   {job.get('salary')}")
        
        if job.get('url'):
            print(f"URL:      {job.get('url')}")
        
        print(f"Source:   {job.get('source', 'unknown')}")
        print(f"Captured: {job.get('captured_at', 'N/A')}")
        
        if job.get('description'):
            desc = job['description'][:200] + "..." if len(job.get('description', '')) > 200 else job.get('description', '')
            print(f"Description: {desc}")
        
        print(f"UID:      {job.get('uid', 'N/A')}")
        print("-" * 60)
    
    def get_review_decision(self, job: Dict[str, Any]) -> str:
        """
        Get user's review decision for a job.
        
        Args:
            job: Job record being reviewed
            
        Returns:
            User's decision: 'approve', 'reject', 'skip', 'quit'
        """
        while True:
            try:
                print("Actions:")
                print("  [a] Approve (status: PENDING -> OK)")
                print("  [r] Reject  (status: PENDING -> REJECTED)")
                print("  [s] Skip    (leave unchanged for later)")
                print("  [q] Quit    (save changes and exit)")
                print("  [?] Show job details again")
                
                choice = input("Your choice [a/r/s/q/?]: ").strip().lower()
                
                if choice in ['a', 'approve']:
                    return 'approve'
                elif choice in ['r', 'reject']:
                    return 'reject'
                elif choice in ['s', 'skip']:
                    return 'skip'
                elif choice in ['q', 'quit']:
                    return 'quit'
                elif choice in ['?', 'help']:
                    return 'show_details'
                else:
                    print("Invalid choice. Please enter 'a', 'r', 's', 'q', or '?' for help.")
                    
            except KeyboardInterrupt:
                print("\nInterrupted. Saving progress...")
                return 'quit'
            except EOFError:
                print("\nEnd of input. Saving progress...")
                return 'quit'
    
    def process_review_decision(self, job: Dict[str, Any], decision: str) -> Dict[str, Any]:
        """
        Process a review decision and update job status.
        
        Args:
            job: Job record to update
            decision: Review decision
            
        Returns:
            Processing result
        """
        process_result = {
            'success': True,
            'action_taken': decision,
            'old_status': job.get('status'),
            'new_status': job.get('status'),
            'updated_job': job.copy()
        }
        
        if decision == 'approve':
            process_result['updated_job']['status'] = 'OK'
            process_result['updated_job']['reviewed_at'] = datetime.utcnow().isoformat() + 'Z'
            process_result['updated_job']['reviewed_by'] = self.command_id
            process_result['new_status'] = 'OK'
            self.session_state['jobs_approved'] += 1
            
        elif decision == 'reject':
            process_result['updated_job']['status'] = 'REJECTED'
            process_result['updated_job']['reviewed_at'] = datetime.utcnow().isoformat() + 'Z'
            process_result['updated_job']['reviewed_by'] = self.command_id
            process_result['new_status'] = 'REJECTED'
            self.session_state['jobs_rejected'] += 1
            
        elif decision == 'skip':
            self.session_state['jobs_skipped'] += 1
            process_result['action_taken'] = 'skip'
        
        self.session_state['jobs_reviewed'] += 1
        
        # Log the review action
        self.log_review_action(
            decision, 
            job.get('uid', 'unknown'), 
            job.get('title', 'Unknown'), 
            job.get('company', 'Unknown')
        )
        
        return process_result
    
    def save_updated_jobs(self, jobs_data: Dict[str, Any], updated_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save updated jobs back to files with atomic operations.
        
        Args:
            jobs_data: Original jobs data structure
            updated_jobs: List of jobs that were updated
            
        Returns:
            Save operation result
        """
        self.log_stage_start('save_updated_jobs')
        
        save_result = {
            'success': True,
            'files_updated': [],
            'backups_created': [],
            'errors': []
        }
        
        try:
            # Update scraped jobs if any were modified
            scraped_updates = [job for job in updated_jobs if job.get('source', '').startswith('scrape') or 
                             job.get('uid') in [j.get('uid') for j in jobs_data['scraped_jobs']]]
            
            if scraped_updates and self.scraped_jobs_file.exists():
                # Create backup
                backup_path = self.scraped_jobs_file.with_suffix('.jsonl.bak')
                import shutil
                shutil.copy2(self.scraped_jobs_file, backup_path)
                save_result['backups_created'].append(str(backup_path))
                
                # Create updated jobs list
                updated_scraped = jobs_data['scraped_jobs'].copy()
                for update in scraped_updates:
                    for i, job in enumerate(updated_scraped):
                        if job.get('uid') == update.get('uid'):
                            updated_scraped[i] = update
                            break
                
                # Atomic write
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    dir=self.scraped_jobs_file.parent, 
                    delete=False,
                    suffix='.tmp'
                ) as temp_file:
                    for job in updated_scraped:
                        temp_file.write(json.dumps(job) + '\n')
                    temp_file.flush()
                    os.fsync(temp_file.fileno())
                    temp_path = temp_file.name
                
                os.rename(temp_path, self.scraped_jobs_file)
                save_result['files_updated'].append(str(self.scraped_jobs_file))
                self.session_state['modified_files'].append(str(self.scraped_jobs_file))
            
            # Update private jobs if any were modified
            private_updates = [job for job in updated_jobs if job.get('source') == 'manual_add' or
                             job.get('uid') in [j.get('uid') for j in jobs_data['private_jobs']]]
            
            if private_updates and self.private_jobs_file.exists():
                # Create backup
                backup_path = self.private_jobs_file.with_suffix('.jsonl.bak')
                import shutil
                shutil.copy2(self.private_jobs_file, backup_path)
                save_result['backups_created'].append(str(backup_path))
                
                # Create updated jobs list
                updated_private = jobs_data['private_jobs'].copy()
                for update in private_updates:
                    for i, job in enumerate(updated_private):
                        if job.get('uid') == update.get('uid'):
                            updated_private[i] = update
                            break
                
                # Atomic write
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    dir=self.private_jobs_file.parent, 
                    delete=False,
                    suffix='.tmp'
                ) as temp_file:
                    for job in updated_private:
                        temp_file.write(json.dumps(job) + '\n')
                    temp_file.flush()
                    os.fsync(temp_file.fileno())
                    temp_path = temp_file.name
                
                os.rename(temp_path, self.private_jobs_file)
                save_result['files_updated'].append(str(self.private_jobs_file))
                self.session_state['modified_files'].append(str(self.private_jobs_file))
        
        except Exception as e:
            save_result['success'] = False
            save_result['errors'].append(f"Error saving jobs: {str(e)}")
            self.log_error(f"Error saving jobs: {str(e)}", 'save_updated_jobs')
        
        self.log_stage_complete('save_updated_jobs', {
            'files_updated': len(save_result['files_updated']),
            'backups_created': len(save_result['backups_created']),
            'errors': len(save_result['errors'])
        })
        
        return save_result
    
    def run_interactive_review(self, jobs_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the interactive review session.
        
        Args:
            jobs_data: Jobs data loaded from files
            
        Returns:
            Review session results
        """
        self.log_stage_start('run_interactive_review')
        
        # Combine all pending jobs for review
        all_pending = jobs_data['pending_scraped'] + jobs_data['pending_private']
        
        if not all_pending:
            return {
                'success': True,
                'message': 'No pending jobs to review',
                'session_state': self.session_state
            }
        
        print(f"\nStarting job review session")
        print(f"Found {len(all_pending)} pending jobs to review")
        print(f"Session ID: {self.command_id}")
        
        updated_jobs = []
        
        try:
            for i, job in enumerate(all_pending, 1):
                while True:  # Loop for handling 'show_details' action
                    self.display_job_for_review(job, i, len(all_pending))
                    decision = self.get_review_decision(job)
                    
                    if decision == 'show_details':
                        continue  # Show job details again
                    elif decision == 'quit':
                        print(f"\nQuitting review session. Progress saved.")
                        break
                    else:
                        # Process the decision
                        process_result = self.process_review_decision(job, decision)
                        if process_result['action_taken'] in ['approve', 'reject']:
                            updated_jobs.append(process_result['updated_job'])
                        
                        print(f"Action: {decision.upper()} - Status: {process_result['old_status']} -> {process_result['new_status']}")
                        break
                
                if decision == 'quit':
                    break
        
        except KeyboardInterrupt:
            print("\nReview interrupted. Saving progress...")
        except Exception as e:
            self.log_error(f"Error during interactive review: {str(e)}", 'run_interactive_review')
            return {
                'success': False,
                'error': str(e),
                'session_state': self.session_state,
                'updated_jobs': updated_jobs
            }
        
        self.log_stage_complete('run_interactive_review', {
            'jobs_reviewed': self.session_state['jobs_reviewed'],
            'jobs_approved': self.session_state['jobs_approved'],
            'jobs_rejected': self.session_state['jobs_rejected'],
            'jobs_skipped': self.session_state['jobs_skipped']
        })
        
        return {
            'success': True,
            'session_state': self.session_state,
            'updated_jobs': updated_jobs
        }
    
    def finalize_telemetry(self, execution_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Finalize telemetry data with execution summary.
        
        Args:
            execution_result: Optional execution results to include
            
        Returns:
            Final telemetry data
        """
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        self.telemetry['end_time'] = end_time.isoformat() + 'Z'
        self.telemetry['duration_seconds'] = duration
        self.telemetry['session_metrics'] = self.session_state
        
        if execution_result:
            self.telemetry['execution_summary'] = execution_result
        
        self.telemetry['final_status'] = 'success' if not self.telemetry['errors'] else 'error'
        
        return self.telemetry
    
    def run(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Main execution entry point for the jobs review command.
        
        Args:
            verbose: Enable verbose logging
            
        Returns:
            Command execution results
        """
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        
        self.logger.info(f"Starting jobs review command (ID: {self.command_id})")
        
        # Stage 1: Load jobs for review
        jobs_data = self.load_jobs_for_review()
        if not jobs_data['success']:
            error_msg = f"Failed to load jobs: {jobs_data['errors']}"
            self.log_error(error_msg, 'load_jobs_for_review')
            return {
                'success': False,
                'error': error_msg,
                'telemetry': self.finalize_telemetry()
            }
        
        if jobs_data['total_pending'] == 0:
            self.logger.info("No pending jobs found - review session complete")
            return {
                'success': True,
                'message': 'No pending jobs to review',
                'telemetry': self.finalize_telemetry()
            }
        
        # Stage 2: Run interactive review
        review_result = self.run_interactive_review(jobs_data)
        if not review_result['success']:
            error_msg = review_result.get('error', 'Interactive review failed')
            self.log_error(error_msg, 'run_interactive_review')
        
        # Stage 3: Save updates
        if review_result.get('updated_jobs'):
            save_result = self.save_updated_jobs(jobs_data, review_result['updated_jobs'])
            if not save_result['success']:
                self.log_error(f"Failed to save updates: {save_result['errors']}", 'save_updated_jobs')
                return {
                    'success': False,
                    'error': f"Review completed but save failed: {save_result['errors']}",
                    'review_result': review_result,
                    'telemetry': self.finalize_telemetry()
                }
        else:
            save_result = {'success': True, 'message': 'No updates to save'}
        
        # Stage 4: Finalize and return
        final_telemetry = self.finalize_telemetry({
            'review_result': review_result,
            'save_result': save_result
        })
        
        self.logger.info(f"Jobs review command completed (Duration: {final_telemetry['duration_seconds']:.2f}s)")
        
        # Print session summary
        print(f"\n{'='*50}")
        print("Review Session Summary")
        print(f"{'='*50}")
        print(f"Jobs Reviewed:  {self.session_state['jobs_reviewed']}")
        print(f"Jobs Approved:  {self.session_state['jobs_approved']}")
        print(f"Jobs Rejected:  {self.session_state['jobs_rejected']}")
        print(f"Jobs Skipped:   {self.session_state['jobs_skipped']}")
        print(f"Duration:       {final_telemetry['duration_seconds']:.1f} seconds")
        
        if self.session_state['modified_files']:
            print(f"Files Updated:  {', '.join(self.session_state['modified_files'])}")
        
        return {
            'success': review_result['success'],
            'session_summary': self.session_state,
            'review_result': review_result,
            'save_result': save_result,
            'telemetry': final_telemetry
        }

# Command entry point for N5 OS Command system
def jobs_review_command_entry(verbose: bool = False) -> Dict[str, Any]:
    """
    Entry point for the jobs-review command following N5 OS Command Authoring conventions.
    
    This function serves as the canonical entry point for the command system and
    provides the interface expected by commands.jsonl entries.
    """
    command = JobsReviewCommand()
    return command.run(verbose)

# CLI compatibility layer
def main():
    """CLI entry point for backward compatibility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive TUI to review and approve pending jobs (Command Authoring version)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        result = jobs_review_command_entry(args.verbose)
        
        if not result['success']:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nReview interrupted by user.")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()