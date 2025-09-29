import logging
# Cache System Integration (uncomment to use):
# from system_prep.cache_manager import CacheManager
import time
import json
import os
import shutil
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime


def safe_export_command(resolved_command: Dict[str, Any], 
                       commands_file: str = "N5/commands.jsonl",
                       backup_enabled: bool = True) -> Dict[str, Any]:
    """
    Append to commands.jsonl (create if absent). Trigger redistillation on conflicts.
    
    Args:
        resolved_command: Resolved command from conflict resolution
        commands_file: Path to commands.jsonl file
        backup_enabled: Whether to create backup before modifications
        
    Returns:
        Export result with success confirmation and metadata
    """
    start_time = time.time()
    
    try:
        if 'error' in resolved_command:
            logging.error(f"Cannot export errored command: {resolved_command['error']}")
            return {'error': resolved_command['error']}
        
        # Prepare export paths
        commands_path = Path(commands_file)
        backup_path = None
        
        # Create backup if file exists and backup is enabled
        if backup_enabled and commands_path.exists():
            backup_path = _create_backup(commands_path)
        
        # Prepare command for export
        export_command = _prepare_command_for_export(resolved_command)
        
        # Perform append operation
        append_result = _append_to_commands_file(export_command, commands_path)
        
        # Check if redistillation is needed
        redistillation_needed = _check_redistillation_trigger(resolved_command, commands_path)
        
        if redistillation_needed:
            redistillation_result = _trigger_redistillation(commands_path)
        else:
            redistillation_result = {'needed': False}
        
        # Prepare export result
        export_result = {
            'success': True,
            'command_id': export_command.get('id'),
            'command_name': export_command.get('command'),
            'export_timestamp': datetime.now().isoformat(),
            'file_path': str(commands_path),
            'backup_created': backup_path is not None,
            'backup_path': str(backup_path) if backup_path else None,
            'append_result': append_result,
            'redistillation': redistillation_result,
            'export_time': time.time() - start_time,
            'file_size_after': commands_path.stat().st_size if commands_path.exists() else 0
        }
        
        # Telemetry logging
        export_time = time.time() - start_time
        logging.info(f"Command exported successfully in {export_time:.3f}s")
        logging.info(f"Appended to commands.jsonl: {export_command.get('command', 'unknown')}")
        
        if backup_path:
            logging.debug(f"Backup created: {backup_path}")
        
        if redistillation_result.get('needed'):
            logging.info(f"Redistillation triggered: {redistillation_result.get('status', 'unknown')}")
        
        return export_result
        
    except Exception as e:
        logging.error(f"Export failed: {e}")
        
        # Attempt rollback if backup exists
        if backup_enabled and 'backup_path' in locals() and backup_path:
            try:
                _rollback_from_backup(commands_path, backup_path)
                logging.info("Rollback successful")
            except Exception as rollback_error:
                logging.error(f"Rollback failed: {rollback_error}")
        
        return {
            'success': False,
            'error': str(e),
            'rollback_attempted': backup_enabled,
            'export_time': time.time() - start_time
        }


def _create_backup(commands_path: Path) -> Path:
    """Create backup of commands file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = commands_path.with_suffix(f'.backup_{timestamp}.jsonl')
    
    try:
        shutil.copy2(commands_path, backup_path)
        logging.debug(f"Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        raise


def _prepare_command_for_export(command: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare command for export by cleaning and adding metadata."""
    export_command = command.copy()
    
    # Add export metadata
    export_metadata = {
        'exported_at': datetime.now().isoformat(),
        'export_version': '1.0.0',
        'source_system': 'command_authoring_system'
    }
    
    if 'metadata' not in export_command:
        export_command['metadata'] = {}
    
    export_command['metadata'].update(export_metadata)
    
    # Clean up internal processing data that shouldn't be exported
    fields_to_remove = [
        'validation',  # Internal validation results
        'conflict_resolution',  # Internal conflict resolution data
        'adaptations_applied'  # Keep this as it's part of command history
    ]
    
    for field in fields_to_remove:
        if field in export_command:
            # Move to metadata instead of removing completely
            if 'processing_history' not in export_command['metadata']:
                export_command['metadata']['processing_history'] = {}
            
            export_command['metadata']['processing_history'][field] = export_command.pop(field)
    
    return export_command


def _append_to_commands_file(command: Dict[str, Any], commands_path: Path) -> Dict[str, Any]:
    """Append command to commands.jsonl file with atomic operation."""
    append_result = {
        'bytes_written': 0,
        'line_number': 0,
        'integrity_check': False
    }
    
    try:
        # Ensure directory exists
        commands_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Count existing lines if file exists
        line_count = 0
        if commands_path.exists():
            with open(commands_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
        
        # Prepare JSON line
        json_line = json.dumps(command, ensure_ascii=False, separators=(',', ':'))
        
        # Atomic append operation
        temp_path = commands_path.with_suffix('.tmp')
        
        # Copy existing content if file exists
        if commands_path.exists():
            shutil.copy2(commands_path, temp_path)
        
        # Append new command
        with open(temp_path, 'a', encoding='utf-8') as f:
            if commands_path.exists() and commands_path.stat().st_size > 0:
                f.write('\n')  # Add newline before new entry
            f.write(json_line)
            bytes_written = len(json_line.encode('utf-8'))
        
        # Atomic replace
        temp_path.replace(commands_path)
        
        append_result['bytes_written'] = bytes_written
        append_result['line_number'] = line_count + 1
        append_result['integrity_check'] = _verify_file_integrity(commands_path)
        
        logging.debug(f"Appended {bytes_written} bytes to line {append_result['line_number']}")
        
        return append_result
        
    except Exception as e:
        logging.error(f"Append operation failed: {e}")
        
        # Clean up temp file if it exists
        temp_path = commands_path.with_suffix('.tmp')
        if temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
        
        raise


def _verify_file_integrity(commands_path: Path) -> bool:
    """Verify that the commands file is valid JSON Lines format."""
    try:
        if not commands_path.exists():
            return False
        
        with open(commands_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        json.loads(line)
                    except json.JSONDecodeError:
                        logging.error(f"Invalid JSON at line {line_num}")
                        return False
        
        return True
        
    except Exception as e:
        logging.error(f"Integrity check failed: {e}")
        return False


def _check_redistillation_trigger(command: Dict[str, Any], commands_path: Path) -> bool:
    """Check if redistillation should be triggered based on conflicts or file size."""
    try:
        # Check conflict resolution results
        conflict_resolution = command.get('conflict_resolution', {})
        scan_results = conflict_resolution.get('scan_results', {})
        
        # Trigger if there were significant conflicts
        conflicts_found = scan_results.get('conflicts_found', 0)
        if conflicts_found > 3:
            logging.debug(f"Redistillation triggered by high conflict count: {conflicts_found}")
            return True
        
        # Trigger if there were critical conflicts
        critical_conflicts = scan_results.get('critical_conflicts', [])
        if critical_conflicts:
            logging.debug(f"Redistillation triggered by critical conflicts: {len(critical_conflicts)}")
            return True
        
        # Check file size (trigger redistillation every 100 commands approximately)
        if commands_path.exists():
            try:
                with open(commands_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f if line.strip())
                
                if line_count > 0 and line_count % 100 == 0:
                    logging.debug(f"Redistillation triggered by command count: {line_count}")
                    return True
            except Exception as e:
                logging.warning(f"Could not count lines for redistillation check: {e}")
        
        return False
        
    except Exception as e:
        logging.error(f"Redistillation check failed: {e}")
        return False


def _trigger_redistillation(commands_path: Path) -> Dict[str, Any]:
    """Trigger redistillation process to optimize command storage."""
    redistillation_result = {
        'needed': True,
        'triggered': False,
        'status': 'failed',
        'commands_processed': 0,
        'duplicates_removed': 0,
        'optimization_applied': False
    }
    
    try:
        # Load all commands
        commands = []
        with open(commands_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        commands.append(json.loads(line))
                    except json.JSONDecodeError:
                        logging.warning(f"Skipping invalid JSON line during redistillation")
        
        original_count = len(commands)
        
        # Remove duplicates based on command name and ID
        seen_ids = set()
        seen_names = set()
        unique_commands = []
        
        for command in commands:
            command_id = command.get('id', '')
            command_name = command.get('command', '')
            
            # Skip if we've seen this ID or name before
            if command_id in seen_ids:
                continue
            
            # For name duplicates, keep the newer one (later in the file)
            if command_name in seen_names:
                # Remove the older one with same name
                unique_commands = [cmd for cmd in unique_commands 
                                 if cmd.get('command') != command_name]
            
            unique_commands.append(command)
            seen_ids.add(command_id)
            seen_names.add(command_name)
        
        # Sort commands for better organization
        unique_commands.sort(key=lambda x: (
            x.get('category', 'zzz'),  # Sort by category
            x.get('command', '')       # Then by name
        ))
        
        # Write redistilled commands
        backup_path = _create_backup(commands_path)
        
        with open(commands_path, 'w', encoding='utf-8') as f:
            for i, command in enumerate(unique_commands):
                if i > 0:
                    f.write('\n')
                json_line = json.dumps(command, ensure_ascii=False, separators=(',', ':'))
                f.write(json_line)
        
        redistillation_result.update({
            'triggered': True,
            'status': 'completed',
            'commands_processed': original_count,
            'duplicates_removed': original_count - len(unique_commands),
            'optimization_applied': True,
            'backup_path': str(backup_path)
        })
        
        logging.info(f"Redistillation completed: {original_count} -> {len(unique_commands)} commands "
                    f"({original_count - len(unique_commands)} duplicates removed)")
        
        return redistillation_result
        
    except Exception as e:
        logging.error(f"Redistillation failed: {e}")
        redistillation_result['error'] = str(e)
        return redistillation_result


def _rollback_from_backup(commands_path: Path, backup_path: Path) -> None:
    """Rollback commands file from backup."""
    try:
        if backup_path.exists():
            shutil.copy2(backup_path, commands_path)
            logging.info(f"Rolled back from backup: {backup_path}")
        else:
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
    except Exception as e:
        logging.error(f"Rollback failed: {e}")
        raise


def validate_export_integrity(commands_path: Path, expected_command_id: str) -> Dict[str, Any]:
    """Validate that the export was successful and the file is intact."""
    validation_result = {
        'file_exists': False,
        'file_valid': False,
        'command_found': False,
        'total_commands': 0,
        'last_command_id': None
    }
    
    try:
        if not commands_path.exists():
            return validation_result
        
        validation_result['file_exists'] = True
        
        # Check file integrity
        if not _verify_file_integrity(commands_path):
            return validation_result
        
        validation_result['file_valid'] = True
        
        # Check if our command was added
        with open(commands_path, 'r', encoding='utf-8') as f:
            commands = []
            for line in f:
                line = line.strip()
                if line:
                    try:
                        command = json.loads(line)
                        commands.append(command)
                        if command.get('id') == expected_command_id:
                            validation_result['command_found'] = True
                    except json.JSONDecodeError:
                        pass
        
        validation_result['total_commands'] = len(commands)
        if commands:
            validation_result['last_command_id'] = commands[-1].get('id')
        
        return validation_result
        
    except Exception as e:
        logging.error(f"Export validation failed: {e}")
        validation_result['error'] = str(e)
        return validation_result


def cleanup_old_backups(commands_path: Path, keep_count: int = 10) -> Dict[str, Any]:
    """Clean up old backup files, keeping only the most recent ones."""
    cleanup_result = {
        'backups_found': 0,
        'backups_removed': 0,
        'bytes_freed': 0
    }
    
    try:
        # Find backup files
        backup_pattern = f"{commands_path.stem}.backup_*.jsonl"
        backup_files = []
        
        for file_path in commands_path.parent.glob(backup_pattern):
            if file_path.is_file():
                backup_files.append({
                    'path': file_path,
                    'mtime': file_path.stat().st_mtime,
                    'size': file_path.stat().st_size
                })
        
        backup_files.sort(key=lambda x: x['mtime'], reverse=True)
        cleanup_result['backups_found'] = len(backup_files)
        
        # Remove old backups beyond keep_count
        if len(backup_files) > keep_count:
            for backup in backup_files[keep_count:]:
                try:
                    cleanup_result['bytes_freed'] += backup['size']
                    backup['path'].unlink()
                    cleanup_result['backups_removed'] += 1
                except Exception as e:
                    logging.warning(f"Could not remove backup {backup['path']}: {e}")
        
        if cleanup_result['backups_removed'] > 0:
            logging.info(f"Cleaned up {cleanup_result['backups_removed']} old backups, "
                        f"freed {cleanup_result['bytes_freed']} bytes")
        
        return cleanup_result
        
    except Exception as e:
        logging.error(f"Backup cleanup failed: {e}")
        cleanup_result['error'] = str(e)
        return cleanup_result