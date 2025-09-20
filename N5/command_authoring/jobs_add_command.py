#!/usr/bin/env python3
"""
N5 OS Command Authoring: Jobs Add Command
Command for adding one-off jobs to private list with Command Authoring framework integration.

This module implements the jobs-add command following N5 OS Command Authoring patterns:
- Full telemetry and logging integration
- Dry-run capabilities with validation
- Error handling with atomic operations
- Safe export with backup and rollback
- Input parsing and validation
"""

import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import sys

class JobsAddCommand:
    """
    Jobs add command with full Command Authoring framework integration.
    
    Implements comprehensive telemetry, validation, error handling, and safe export
    following N5 OS Command Authoring patterns and preferences.
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
            'stages': {}
        }
        
        # Setup logging
        self.logger = logging.getLogger('jobs_add')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Set target file path
        self.target_file = Path('/home/workspace/N5/jobs/lists/jobs-private.jsonl')
    
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
    
    def parse_job_string(self, job_string: str) -> Dict[str, Any]:
        """
        Parse job string into structured components.
        
        Expected format: "Title@Company [location] [salary]"
        
        Args:
            job_string: Raw job string to parse
            
        Returns:
            Parsed job components with validation status
        """
        self.log_stage_start('parse_job_string')
        
        parse_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'job_data': {}
        }
        
        if not job_string or not job_string.strip():
            parse_result['valid'] = False
            parse_result['errors'].append("Job string is empty")
            return parse_result
        
        job_string = job_string.strip()
        
        # Split by @ to separate title and company info
        if '@' not in job_string:
            parse_result['valid'] = False
            parse_result['errors'].append("Job string must contain '@' separator (format: Title@Company [location] [salary])")
            return parse_result
        
        parts = job_string.split('@', 1)  # Split only on first @
        title = parts[0].strip()
        company_part = parts[1].strip()
        
        if not title:
            parse_result['valid'] = False
            parse_result['errors'].append("Job title cannot be empty")
            return parse_result
        
        if not company_part:
            parse_result['valid'] = False
            parse_result['errors'].append("Company information cannot be empty")
            return parse_result
        
        # Parse company part - first word is company, rest are optional location and salary
        company_tokens = company_part.split()
        company = company_tokens[0] if company_tokens else ""
        location = company_tokens[1] if len(company_tokens) > 1 else ""
        salary = company_tokens[2] if len(company_tokens) > 2 else ""
        
        # Additional parsing for combined location/salary if more tokens
        if len(company_tokens) > 3:
            # Join remaining tokens for salary (e.g., "200k USD" or "150k-200k")
            salary = " ".join(company_tokens[2:])
        
        # Validation warnings
        if len(title) < 3:
            parse_result['warnings'].append("Job title seems very short")
        
        if len(company) < 2:
            parse_result['warnings'].append("Company name seems very short")
        
        if location and len(location) < 2:
            parse_result['warnings'].append("Location seems very short")
        
        if salary and not any(c.isdigit() for c in salary):
            parse_result['warnings'].append("Salary does not contain numbers")
        
        parse_result['job_data'] = {
            'title': title,
            'company': company,
            'location': location,
            'salary': salary
        }
        
        self.log_stage_complete('parse_job_string', {
            'title_length': len(title),
            'company_length': len(company),
            'has_location': bool(location),
            'has_salary': bool(salary)
        })
        
        return parse_result
    
    def create_job_record(self, job_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a complete job record with metadata.
        
        Args:
            job_data: Parsed job data
            
        Returns:
            Complete job record
        """
        self.log_stage_start('create_job_record')
        
        job_record = {
            'uid': str(uuid.uuid4()),
            'title': job_data['title'],
            'company': job_data['company'],
            'location': job_data.get('location', ''),
            'salary': job_data.get('salary', ''),
            'status': 'PENDING',  # Following jobs system convention
            'source': 'manual_add',
            'captured_at': datetime.utcnow().isoformat() + 'Z',
            'added_by_command': self.command_id,
            'metadata': {
                'entry_method': 'jobs-add-command',
                'version': '1.0.0',
                'original_string': f"{job_data['title']}@{job_data['company']} {job_data.get('location', '')} {job_data.get('salary', '')}".strip()
            }
        }
        
        self.log_stage_complete('create_job_record', {
            'job_uid': job_record['uid'],
            'has_metadata': bool(job_record.get('metadata'))
        })
        
        return job_record
    
    def validate_job_record(self, job_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the job record before saving.
        
        Args:
            job_record: Job record to validate
            
        Returns:
            Validation result
        """
        self.log_stage_start('validate_job_record')
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'risk_assessment': 'low'
        }
        
        # Required fields validation
        required_fields = ['uid', 'title', 'company', 'status', 'captured_at']
        for field in required_fields:
            if not job_record.get(field):
                validation_result['valid'] = False
                validation_result['errors'].append(f"Required field missing: {field}")
        
        # Data type validation
        if 'uid' in job_record and not isinstance(job_record['uid'], str):
            validation_result['valid'] = False
            validation_result['errors'].append("UID must be string")
        
        # Business logic validation
        if job_record.get('title') and len(job_record['title']) > 200:
            validation_result['warnings'].append("Job title is unusually long")
            validation_result['risk_assessment'] = 'medium'
        
        if job_record.get('company') and len(job_record['company']) > 100:
            validation_result['warnings'].append("Company name is unusually long")
        
        # Check for duplicate prevention (basic)
        try:
            if self.target_file.exists():
                with open(self.target_file, 'r') as f:
                    existing_jobs = [json.loads(line) for line in f if line.strip()]
                
                # Simple duplicate check based on title+company
                for existing in existing_jobs:
                    if (existing.get('title', '').lower() == job_record.get('title', '').lower() and
                        existing.get('company', '').lower() == job_record.get('company', '').lower()):
                        validation_result['warnings'].append("Potential duplicate job detected")
                        validation_result['risk_assessment'] = 'medium'
                        break
        except Exception as e:
            self.log_warning(f"Could not check for duplicates: {str(e)}", 'validate_job_record')
        
        self.log_stage_complete('validate_job_record', {
            'valid': validation_result['valid'],
            'errors_count': len(validation_result['errors']),
            'warnings_count': len(validation_result['warnings']),
            'risk_level': validation_result['risk_assessment']
        })
        
        return validation_result
    
    def dry_run_simulation(self, job_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive dry-run simulation.
        
        Args:
            job_record: Job record to simulate adding
            
        Returns:
            Dry run results with impact assessment
        """
        self.log_stage_start('dry_run_simulation')
        
        dry_run_result = {
            'would_add_job': True,
            'target_file': str(self.target_file),
            'file_exists': self.target_file.exists(),
            'current_file_size': 0,
            'estimated_new_size': 0,
            'backup_required': False,
            'risk_assessment': 'low',
            'preview_record': job_record
        }
        
        # File analysis
        if self.target_file.exists():
            try:
                file_stats = self.target_file.stat()
                dry_run_result['current_file_size'] = file_stats.st_size
                dry_run_result['backup_required'] = True
                
                # Estimate new size
                record_size = len(json.dumps(job_record)) + 1  # +1 for newline
                dry_run_result['estimated_new_size'] = dry_run_result['current_file_size'] + record_size
                
                # Count existing records
                with open(self.target_file, 'r') as f:
                    existing_count = sum(1 for line in f if line.strip())
                dry_run_result['existing_records_count'] = existing_count
                
            except Exception as e:
                self.log_warning(f"Could not analyze target file: {str(e)}", 'dry_run_simulation')
                dry_run_result['risk_assessment'] = 'medium'
        else:
            dry_run_result['would_create_file'] = True
        
        # Directory permissions check
        target_dir = self.target_file.parent
        if not os.access(target_dir, os.W_OK):
            dry_run_result['would_add_job'] = False
            dry_run_result['risk_assessment'] = 'high'
            dry_run_result['error'] = f"No write permission for directory: {target_dir}"
        
        self.log_stage_complete('dry_run_simulation', {
            'would_add': dry_run_result['would_add_job'],
            'file_exists': dry_run_result['file_exists'],
            'estimated_size': dry_run_result['estimated_new_size']
        })
        
        return dry_run_result
    
    def safe_append_job(self, job_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely append job to target file with atomic operations.
        
        Args:
            job_record: Job record to append
            
        Returns:
            Append operation result
        """
        self.log_stage_start('safe_append_job')
        
        append_result = {
            'success': True,
            'backup_created': False,
            'backup_path': None,
            'bytes_written': 0,
            'error': None
        }
        
        try:
            # Create backup if file exists
            if self.target_file.exists():
                backup_path = self.target_file.with_suffix('.jsonl.bak')
                import shutil
                shutil.copy2(self.target_file, backup_path)
                append_result['backup_created'] = True
                append_result['backup_path'] = str(backup_path)
                self.logger.info(f"Backup created: {backup_path}")
            
            # Atomic write using temporary file
            with tempfile.NamedTemporaryFile(
                mode='w', 
                dir=self.target_file.parent, 
                delete=False,
                suffix='.tmp'
            ) as temp_file:
                
                # Copy existing content if file exists
                if self.target_file.exists():
                    with open(self.target_file, 'r') as existing_file:
                        for line in existing_file:
                            temp_file.write(line)
                
                # Append new record
                job_json = json.dumps(job_record)
                temp_file.write(job_json + '\n')
                append_result['bytes_written'] = len(job_json) + 1
                
                temp_file.flush()
                os.fsync(temp_file.fileno())
                temp_path = temp_file.name
            
            # Atomic rename
            os.rename(temp_path, self.target_file)
            self.logger.info(f"Job record successfully appended to {self.target_file}")
            
        except Exception as e:
            append_result['success'] = False
            append_result['error'] = str(e)
            self.log_error(f"Failed to append job: {str(e)}", 'safe_append_job')
            
            # Attempt rollback if backup was created
            if append_result['backup_created'] and append_result['backup_path']:
                try:
                    backup_path = Path(append_result['backup_path'])
                    if backup_path.exists():
                        import shutil
                        shutil.copy2(backup_path, self.target_file)
                        self.logger.info("Rollback completed using backup")
                except Exception as rollback_error:
                    self.log_error(f"Rollback failed: {str(rollback_error)}", 'safe_append_job')
        
        self.log_stage_complete('safe_append_job', {
            'success': append_result['success'],
            'backup_created': append_result['backup_created'],
            'bytes_written': append_result['bytes_written']
        })
        
        return append_result
    
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
        
        if execution_result:
            self.telemetry['execution_summary'] = execution_result
        
        self.telemetry['final_status'] = 'success' if not self.telemetry['errors'] else 'error'
        
        return self.telemetry
    
    def run(self, job_string: str, dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """
        Main execution entry point for the jobs add command.
        
        Args:
            job_string: Job string to parse and add
            dry_run: Whether to perform dry run only
            verbose: Enable verbose logging
            
        Returns:
            Command execution results
        """
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        
        self.logger.info(f"Starting jobs add command (ID: {self.command_id})")
        
        # Stage 1: Parse Job String
        parse_result = self.parse_job_string(job_string)
        if not parse_result['valid']:
            error_msg = f"Job parsing failed: {parse_result['errors']}"
            self.log_error(error_msg, 'parse_job_string')
            return {
                'success': False,
                'error': error_msg,
                'telemetry': self.finalize_telemetry()
            }
        
        # Stage 2: Create Job Record
        job_record = self.create_job_record(parse_result['job_data'])
        
        # Stage 3: Validate Job Record
        validation_result = self.validate_job_record(job_record)
        if not validation_result['valid']:
            error_msg = f"Job validation failed: {validation_result['errors']}"
            self.log_error(error_msg, 'validate_job_record')
            return {
                'success': False,
                'error': error_msg,
                'validation_result': validation_result,
                'telemetry': self.finalize_telemetry()
            }
        
        # Stage 4: Dry Run Simulation
        dry_run_result = self.dry_run_simulation(job_record)
        
        if dry_run:
            self.logger.info("Dry run completed - no actual job added")
            return {
                'success': True,
                'dry_run': True,
                'job_record': job_record,
                'simulation_result': dry_run_result,
                'validation_result': validation_result,
                'telemetry': self.finalize_telemetry()
            }
        
        # Stage 5: Safe Append
        if not dry_run_result['would_add_job']:
            error_msg = f"Cannot add job: {dry_run_result.get('error', 'Unknown dry run issue')}"
            self.log_error(error_msg, 'safe_append_job')
            return {
                'success': False,
                'error': error_msg,
                'dry_run_result': dry_run_result,
                'telemetry': self.finalize_telemetry()
            }
        
        append_result = self.safe_append_job(job_record)
        
        # Stage 6: Finalize and Return
        final_telemetry = self.finalize_telemetry(append_result)
        
        self.logger.info(f"Jobs add command completed (Duration: {final_telemetry['duration_seconds']:.2f}s)")
        
        return {
            'success': append_result['success'],
            'job_record': job_record,
            'append_result': append_result,
            'validation_result': validation_result,
            'telemetry': final_telemetry
        }

# Command entry point for N5 OS Command system
def jobs_add_command_entry(job_string: str, dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Entry point for the jobs-add command following N5 OS Command Authoring conventions.
    
    This function serves as the canonical entry point for the command system and
    provides the interface expected by commands.jsonl entries.
    """
    command = JobsAddCommand()
    return command.run(job_string, dry_run, verbose)

# CLI compatibility layer
def main():
    """CLI entry point for backward compatibility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Add one-off job to private list (Command Authoring version)")
    parser.add_argument("job_string", help="Title@Company [location] [salary]")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    result = jobs_add_command_entry(args.job_string, args.dry_run, args.verbose)
    
    if result['success']:
        if result.get('dry_run'):
            print("Dry run - would add:")
            print(json.dumps(result['job_record'], indent=2))
        else:
            print("Job added successfully:")
            print(json.dumps(result['job_record'], indent=2))
    else:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()