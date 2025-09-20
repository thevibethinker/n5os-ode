#!/usr/bin/env python3
"""
N5 OS Command Authoring: Essential Links Add Command
Command for adding essential links with categories and descriptions to private list.

This module implements the essential-links-add command following N5 OS Command Authoring patterns:
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

class EssentialLinksAddCommand:
    """
    Essential Links add command with full Command Authoring framework integration.

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
        self.logger = logging.getLogger('essential_links_add')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Set target file path
        self.target_file = Path('/home/workspace/N5/essential_links/lists/essential_links.jsonl')

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

    def parse_link_string(self, link_string: str) -> Dict[str, Any]:
        """
        Parse link string into structured components.

        Expected format: "URL|Category|Title|Description"
        Or: "URL|Category|Title" (description optional)

        Args:
            link_string: Raw link string to parse

        Returns:
            Parsed link components with validation status
        """
        self.log_stage_start('parse_link_string')

        parse_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'link_data': {}
        }

        if not link_string or not link_string.strip():
            parse_result['valid'] = False
            parse_result['errors'].append("Link string is empty")
            return parse_result

        link_string = link_string.strip()

        # Split by | separator
        parts = link_string.split('|', 3)  # Allow up to 4 parts
        if len(parts) < 3:
            parse_result['valid'] = False
            parse_result['errors'].append("Link string must contain at least 3 parts separated by '|': URL|Category|Title [|Description]")
            return parse_result

        url = parts[0].strip()
        category = parts[1].strip()
        title = parts[2].strip()
        description = parts[3].strip() if len(parts) > 3 else ""

        # Basic URL validation
        if not url:
            parse_result['valid'] = False
            parse_result['errors'].append("URL cannot be empty")
        elif not url.startswith(('http://', 'https://')):
            parse_result['warnings'].append("URL should start with http:// or https://")

        if not category:
            parse_result['valid'] = False
            parse_result['errors'].append("Category cannot be empty")

        if not title:
            parse_result['valid'] = False
            parse_result['errors'].append("Title cannot be empty")

        # Validation warnings
        if len(title) > 200:
            parse_result['warnings'].append("Title is unusually long (>200 characters)")

        if len(category) > 100:
            parse_result['warnings'].append("Category name is unusually long")

        if description and len(description) > 500:
            parse_result['warnings'].append("Description is unusually long (>500 characters)")

        parse_result['link_data'] = {
            'url': url,
            'category': category,
            'title': title,
            'description': description
        }

        self.log_stage_complete('parse_link_string', {
            'url_length': len(url),
            'category_length': len(category),
            'title_length': len(title),
            'has_description': bool(description)
        })

        return parse_result

    def create_link_record(self, link_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a complete link record with metadata.

        Args:
            link_data: Parsed link data

        Returns:
            Complete link record
        """
        self.log_stage_start('create_link_record')

        link_record = {
            'uid': str(uuid.uuid4()),
            'url': link_data['url'],
            'category': link_data['category'],
            'title': link_data['title'],
            'description': link_data.get('description', ''),
            'status': 'active',  # Following links system convention
            'source': 'manual_add',
            'captured_at': datetime.utcnow().isoformat() + 'Z',
            'added_by_command': self.command_id,
            'metadata': {
                'entry_method': 'essential-links-add-command',
                'version': '1.0.0',
                'original_string': f"{link_data['url']}|{link_data['category']}|{link_data['title']}|{link_data.get('description', '')}".strip('|')
            }
        }

        self.log_stage_complete('create_link_record', {
            'link_uid': link_record['uid'],
            'has_metadata': bool(link_record.get('metadata'))
        })

        return link_record

    def validate_link_record(self, link_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the link record before saving.

        Args:
            link_record: Link record to validate

        Returns:
            Validation result
        """
        self.log_stage_start('validate_link_record')

        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'risk_assessment': 'low'
        }

        # Required fields validation
        required_fields = ['uid', 'url', 'category', 'title', 'status', 'captured_at']
        for field in required_fields:
            if not link_record.get(field):
                validation_result['valid'] = False
                validation_result['errors'].append(f"Required field missing: {field}")

        # Data type validation
        if 'uid' in link_record and not isinstance(link_record['uid'], str):
            validation_result['valid'] = False
            validation_result['errors'].append("UID must be string")

        # URL validation
        url = link_record.get('url', '')
        if url and not url.startswith(('http://', 'https://')):
            validation_result['warnings'].append("URL should use HTTPS for security")

        # Business logic validation
        if link_record.get('title') and len(link_record['title']) > 200:
            validation_result['warnings'].append("Title is unusually long")
            validation_result['risk_assessment'] = 'medium'

        if link_record.get('category') and len(link_record['category']) > 100:
            validation_result['warnings'].append("Category name is unusually long")

        # Check for duplicate prevention (basic)
        try:
            if self.target_file.exists():
                with open(self.target_file, 'r') as f:
                    existing_links = [json.loads(line) for line in f if line.strip()]

                # Simple duplicate check based on url
                for existing in existing_links:
                    if existing.get('url', '').lower() == link_record.get('url', '').lower():
                        validation_result['warnings'].append("Potential duplicate URL detected")
                        validation_result['risk_assessment'] = 'medium'
                        break
        except Exception as e:
            self.log_warning(f"Could not check for duplicates: {str(e)}", 'validate_link_record')

        self.log_stage_complete('validate_link_record', {
            'valid': validation_result['valid'],
            'errors_count': len(validation_result['errors']),
            'warnings_count': len(validation_result['warnings']),
            'risk_level': validation_result['risk_assessment']
        })

        return validation_result

    def dry_run_simulation(self, link_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive dry-run simulation.

        Args:
            link_record: Link record to simulate adding

        Returns:
            Dry run results with impact assessment
        """
        self.log_stage_start('dry_run_simulation')

        dry_run_result = {
            'would_add_link': True,
            'target_file': str(self.target_file),
            'file_exists': self.target_file.exists(),
            'current_file_size': 0,
            'estimated_new_size': 0,
            'backup_required': False,
            'risk_assessment': 'low',
            'preview_record': link_record
        }

        # File analysis
        if self.target_file.exists():
            try:
                file_stats = self.target_file.stat()
                dry_run_result['current_file_size'] = file_stats.st_size
                dry_run_result['backup_required'] = True

                # Estimate new size
                record_size = len(json.dumps(link_record)) + 1  # +1 for newline
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
            dry_run_result['would_add_link'] = False
            dry_run_result['risk_assessment'] = 'high'
            dry_run_result['error'] = f"No write permission for directory: {target_dir}"

        self.log_stage_complete('dry_run_simulation', {
            'would_add': dry_run_result['would_add_link'],
            'file_exists': dry_run_result['file_exists'],
            'estimated_size': dry_run_result['estimated_new_size']
        })

        return dry_run_result

    def safe_append_link(self, link_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely append link to target file with atomic operations.

        Args:
            link_record: Link record to append

        Returns:
            Append operation result
        """
        self.log_stage_start('safe_append_link')

        append_result = {
            'success': True,
            'backup_created': False,
            'backup_path': None,
            'bytes_written': 0,
            'error': None
        }

        try:
            # Ensure directory exists
            self.target_file.parent.mkdir(parents=True, exist_ok=True)

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
                link_json = json.dumps(link_record)
                temp_file.write(link_json + '\n')
                append_result['bytes_written'] = len(link_json) + 1

                temp_file.flush()
                os.fsync(temp_file.fileno())
                temp_path = temp_file.name

            # Atomic rename
            os.rename(temp_path, self.target_file)
            self.logger.info(f"Link record successfully appended to {self.target_file}")

        except Exception as e:
            append_result['success'] = False
            append_result['error'] = str(e)
            self.log_error(f"Failed to append link: {str(e)}", 'safe_append_link')

            # Attempt rollback if backup was created
            if append_result['backup_created'] and append_result['backup_path']:
                try:
                    backup_path = Path(append_result['backup_path'])
                    if backup_path.exists():
                        import shutil
                        shutil.copy2(backup_path, self.target_file)
                        self.logger.info("Rollback completed using backup")
                except Exception as rollback_error:
                    self.log_error(f"Rollback failed: {str(rollback_error)}", 'safe_append_link')

        self.log_stage_complete('safe_append_link', {
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

    def run(self, link_string: str, dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """
        Main execution entry point for the essential links add command.

        Args:
            link_string: Link string to parse and add
            dry_run: Whether to perform dry run only
            verbose: Enable verbose logging

        Returns:
            Command execution results
        """
        if verbose:
            self.logger.setLevel(logging.DEBUG)

        self.logger.info(f"Starting essential links add command (ID: {self.command_id})")

        # Stage 1: Parse Link String
        parse_result = self.parse_link_string(link_string)
        if not parse_result['valid']:
            error_msg = f"Link parsing failed: {parse_result['errors']}"
            self.log_error(error_msg, 'parse_link_string')
            return {
                'success': False,
                'error': error_msg,
                'telemetry': self.finalize_telemetry()
            }

        # Stage 2: Create Link Record
        link_record = self.create_link_record(parse_result['link_data'])

        # Stage 3: Validate Link Record
        validation_result = self.validate_link_record(link_record)
        if not validation_result['valid']:
            error_msg = f"Link validation failed: {validation_result['errors']}"
            self.log_error(error_msg, 'validate_link_record')
            return {
                'success': False,
                'error': error_msg,
                'validation_result': validation_result,
                'telemetry': self.finalize_telemetry()
            }

        # Stage 4: Dry Run Simulation
        dry_run_result = self.dry_run_simulation(link_record)

        if dry_run:
            self.logger.info("Dry run completed - no actual link added")
            return {
                'success': True,
                'dry_run': True,
                'link_record': link_record,
                'simulation_result': dry_run_result,
                'validation_result': validation_result,
                'telemetry': self.finalize_telemetry()
            }

        # Stage 5: Safe Append
        if not dry_run_result['would_add_link']:
            error_msg = f"Cannot add link: {dry_run_result.get('error', 'Unknown dry run issue')}"
            self.log_error(error_msg, 'safe_append_link')
            return {
                'success': False,
                'error': error_msg,
                'dry_run_result': dry_run_result,
                'telemetry': self.finalize_telemetry()
            }

        append_result = self.safe_append_link(link_record)

        # Stage 6: Finalize and Return
        final_telemetry = self.finalize_telemetry(append_result)

        self.logger.info(f"Essential links add command completed (Duration: {final_telemetry['duration_seconds']:.2f}s)")

        return {
            'success': append_result['success'],
            'link_record': link_record,
            'append_result': append_result,
            'validation_result': validation_result,
            'telemetry': final_telemetry
        }

# Command entry point for N5 OS Command system
def essential_links_add_command_entry(link_string: str, dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Entry point for the essential-links-add command following N5 OS Command Authoring conventions.

    This function serves as the canonical entry point for the command system and
    provides the interface expected by commands.jsonl entries.
    """
    command = EssentialLinksAddCommand()
    return command.run(link_string, dry_run, verbose)

# CLI compatibility layer
def main():
    """CLI entry point for backward compatibility."""
    import argparse

    parser = argparse.ArgumentParser(description="Add essential link to private list (Command Authoring version)")
    parser.add_argument("link_string", help="URL|Category|Title|Description")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    result = essential_links_add_command_entry(args.link_string, args.dry_run, args.verbose)

    if result['success']:
        if result.get('dry_run'):
            print("Dry run - would add:")
            print(json.dumps(result['link_record'], indent=2))
        else:
            print("Link added successfully:")
            print(json.dumps(result['link_record'], indent=2))
    else:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()