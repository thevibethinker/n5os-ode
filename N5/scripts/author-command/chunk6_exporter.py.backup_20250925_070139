#!/usr/bin/env python3
"""
Chunk 6: Safe Export and Integration Handler

Append to commands.jsonl, update commands.md, log changes.
Implements telemetry logging for diagnostics.
"""

import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import asyncio

# Configure logging (only to file when running as CLI)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
        handlers=[logging.FileHandler('/home/workspace/command_authoring.log', mode='a')]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler('/home/workspace/command_authoring.log', mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger('chunk6_exporter')


class SafeExporter:
    """Safely exports commands to N5 OS registry"""
    
    def __init__(self):
        self.export_execution_time = 0.0
        self.file_update_success = True
        self.command_registry_size_change = 0
        self.append_status = 'pending'
    
    def export_command(self, resolved_command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely export resolved command to N5 OS
        
        Args:
            resolved_command: Resolved command from Chunk 5
            
        Returns:
            Dict containing export results and telemetry
        """
        logger.info("Starting safe export process")
        start_time = time.time()
        
        export_results = {
            'commands_jsonl_updated': False,
            'commands_md_updated': False,
            'integration_successful': False,
            'file_changes': [],
            'errors': []
        }
        
        try:
            # Append to commands.jsonl
            jsonl_result = self._append_to_commands_jsonl(resolved_command)
            export_results['commands_jsonl_updated'] = jsonl_result['success']
            if jsonl_result['success']:
                export_results['file_changes'].append(jsonl_result['change_description'])
            else:
                export_results['errors'].extend(jsonl_result['errors'])
            
            # Update commands.md
            md_result = self._update_commands_md(resolved_command)
            export_results['commands_md_updated'] = md_result['success']
            if md_result['success']:
                export_results['file_changes'].append(md_result['change_description'])
            else:
                export_results['errors'].extend(md_result['errors'])
            
            # Check overall success
            export_results['integration_successful'] = (
                export_results['commands_jsonl_updated'] and 
                export_results['commands_md_updated']
            )
            
            self.file_update_success = export_results['integration_successful']
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            export_results['errors'].append(str(e))
            self.file_update_success = False
        
        self.export_execution_time = time.time() - start_time
        
        # Log results
        logger.info(f"Export completed in {self.export_execution_time:.2f}s")
        logger.info(f"Commands.jsonl updated: {export_results['commands_jsonl_updated']}")
        logger.info(f"Commands.md updated: {export_results['commands_md_updated']}")
        logger.info(f"Integration successful: {export_results['integration_successful']}")
        logger.info(f"File changes: {len(export_results['file_changes'])}")
        
        return {
            'export_results': export_results,
            'telemetry': {
                'export_execution_time': self.export_execution_time,
                'file_update_success': self.file_update_success,
                'command_registry_size_change': self.command_registry_size_change,
                'append_status': self.append_status
            }
        }
    
    def _append_to_commands_jsonl(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Append command to commands.jsonl with safety checks"""
        logger.info("Appending to commands.jsonl")
        
        commands_file = Path('/home/workspace/commands.jsonl')
        result = {
            'success': False,
            'change_description': '',
            'errors': []
        }
        
        try:
            # Check if file exists, create if not
            if not commands_file.exists():
                logger.info("commands.jsonl does not exist, creating new file")
                commands_file.touch()
            
            # Read existing commands to check for duplicates
            existing_commands = []
            with open(commands_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            existing_commands.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid JSON at line {line_num}: {e}")
            
            # Check for duplicate names
            new_command_name = command.get('name', '')
            duplicate_found = any(
                existing.get('name') == new_command_name 
                for existing in existing_commands
            )
            
            if duplicate_found:
                result['errors'].append(f"Command '{new_command_name}' already exists in registry")
                logger.error(f"Duplicate command name: {new_command_name}")
                return result
            
            # Append new command
            with open(commands_file, 'a') as f:
                json.dump(command, f)
                f.write('\n')
            
            result['success'] = True
            result['change_description'] = f"Appended command '{new_command_name}' to commands.jsonl"
            
            # Update registry size change
            self.command_registry_size_change = 1
            self.append_status = 'successful'
            
            logger.info(f"Successfully appended command '{new_command_name}' to commands.jsonl")
            
        except Exception as e:
            result['errors'].append(f"Failed to append to commands.jsonl: {str(e)}")
            self.append_status = 'failed'
            logger.error(f"Append failed: {e}")
        
        return result
    
    def _update_commands_md(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Update commands.md catalog"""
        logger.info("Updating commands.md catalog")
        
        commands_md_file = Path('/home/workspace/N5/commands.md')
        result = {
            'success': False,
            'change_description': '',
            'errors': []
        }
        
        try:
            # Check if commands.md exists
            if not commands_md_file.exists():
                logger.warning("commands.md does not exist, skipping update")
                result['errors'].append("commands.md file not found")
                return result
            
            # Read current content
            with open(commands_md_file, 'r') as f:
                content = f.read()
            
            # Find the table section
            lines = content.split('\n')
            table_start = -1
            table_end = -1
            
            for i, line in enumerate(lines):
                if line.startswith('| Name ') and 'Version' in line:
                    table_start = i
                elif table_start != -1 and line.startswith('| ---'):
                    table_end = i
                    break
            
            if table_start == -1:
                result['errors'].append("Could not find command table in commands.md")
                logger.error("Command table not found in commands.md")
                return result
            
            # Find insertion point (before closing |)
            insert_point = -1
            for i in range(table_end + 1, len(lines)):
                if lines[i].strip() == '' or not lines[i].startswith('|'):
                    insert_point = i
                    break
            
            if insert_point == -1:
                insert_point = len(lines)
            
            # Create new table row
            new_row = self._create_table_row(command)
            
            # Insert new row
            lines.insert(insert_point, new_row)
            
            # Write updated content
            with open(commands_md_file, 'w') as f:
                f.write('\n'.join(lines))
            
            result['success'] = True
            result['change_description'] = f"Added command '{command.get('name', '')}' to commands.md table"
            
            logger.info(f"Successfully updated commands.md with new command")
            
        except Exception as e:
            result['errors'].append(f"Failed to update commands.md: {str(e)}")
            logger.error(f"Update failed: {e}")
        
        return result
    
    def _create_table_row(self, command: Dict[str, Any]) -> str:
        """Create a markdown table row for the command"""
        name = command.get('name', 'Unknown')
        version = command.get('version', '0.1.0')
        workflow = command.get('workflow', 'general')
        
        # Create summary from description
        description = command.get('description', '')
        summary = description[:100] + '...' if len(description) > 100 else description
        
        # Determine side effects
        side_effects = ', '.join(command.get('side_effects', ['none']))
        
        # Determine permissions
        permissions = ', '.join(command.get('permissions', ['none']))
        
        return f"| {name} | {version} | {workflow} | {summary} | {side_effects} | {permissions} |"


async def main():
    """CLI interface for Chunk 6"""
    if len(sys.argv) != 2:
        print("Usage: python chunk6_exporter.py <resolved_command.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r') as f:
            command_data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    resolved_command = command_data.get('resolved_command', {})
    exporter = SafeExporter()
    result = exporter.export_command(resolved_command)
    
    # Output JSON result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())