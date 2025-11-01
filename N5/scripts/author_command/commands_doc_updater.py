#!/usr/bin/env python3
"""
Commands Documentation Auto-Updater

Automatically updates commands.md from executables.db with authored command examples.
Adds cross-references to knowledge reservoirs and maintains consistent documentation.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger('commands_doc_updater')


class CommandsDocUpdater:
    """Updates commands.md documentation from executables.db"""
    
    def __init__(self, commands_jsonl_path: str = "/home/workspace/N5/executables.db",
                 commands_md_path: str = "/home/workspace/N5/commands.md"):
        self.commands_jsonl_path = Path(commands_jsonl_path)
        self.commands_md_path = Path(commands_md_path)
        self.knowledge_base_path = Path("/home/workspace/Knowledge")
        self.commands_dir = Path("/home/workspace/N5/commands")
    
    def update_commands_documentation(self) -> Dict[str, Any]:
        """Update commands.md from executables.db"""
        try:
            logger.info("Starting commands documentation update")
            
            # Load commands from JSONL
            commands = self._load_commands_from_jsonl()
            if not commands:
                return {'error': 'No commands found in JSONL file'}
            
            # Generate markdown documentation
            markdown_content = self._generate_markdown_documentation(commands)
            
            # Write to commands.md
            self._write_markdown_file(markdown_content)
            
            # Update individual command files
            self._update_individual_command_files(commands)
            
            result = {
                'success': True,
                'commands_processed': len(commands),
                'updated_at': datetime.now().isoformat(),
                'output_file': str(self.commands_md_path)
            }
            
            logger.info(f"Commands documentation updated successfully: {len(commands)} commands processed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update commands documentation: {e}")
            return {'error': str(e)}
    
    def _load_commands_from_jsonl(self) -> List[Dict[str, Any]]:
        """Load commands from JSONL file"""
        commands = []
        
        if not self.commands_jsonl_path.exists():
            logger.warning(f"Commands file not found: {self.commands_jsonl_path}")
            return commands
        
        try:
            with open(self.commands_jsonl_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            command = json.loads(line)
                            commands.append(command)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid JSON on line {line_num}: {e}")
            
            logger.info(f"Loaded {len(commands)} commands from JSONL")
            return commands
            
        except Exception as e:
            logger.error(f"Failed to load commands from JSONL: {e}")
            return []
    
    def _generate_markdown_documentation(self, commands: List[Dict[str, Any]]) -> str:
        """Generate comprehensive markdown documentation"""
        
        # Sort commands by category and name
        commands_by_category = self._categorize_commands(commands)
        
        # Generate header
        content = [
            "# N5 Commands Reference",
            "",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} from executables.db*",
            "",
            "This document provides a comprehensive reference for all available N5 commands, ",
            "including those created through the Command Authoring System.",
            "",
            "## Table of Contents",
            ""
        ]
        
        # Generate table of contents
        for category in sorted(commands_by_category.keys()):
            content.append(f"- [{category.title()}](#{category.lower().replace(' ', '-')})")
        content.extend(["", "---", ""])
        
        # Generate command sections by category
        for category in sorted(commands_by_category.keys()):
            content.extend(self._generate_category_section(category, commands_by_category[category]))
        
        # Add footer with metadata
        content.extend([
            "---",
            "",
            "## Metadata",
            "",
            f"- **Total Commands**: {len(commands)}",
            f"- **Categories**: {len(commands_by_category)}",
            f"- **Last Updated**: {datetime.now().isoformat()}",
            f"- **Source**: `{self.commands_jsonl_path.name}`",
            "",
            "## Related Documentation",
            "",
            "- [Knowledge Base](/knowledge/README.md)",
            "- [Command Authoring Guide](/docs/command-authoring-guide.md)",
            "- [System Architecture](/docs/architecture.md)",
            ""
        ])
        
        return "\n".join(content)
    
    def _categorize_commands(self, commands: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize commands by their category or inferred category"""
        categories = {}
        
        for command in commands:
            category = command.get('category', 'Other')
            
            # Infer category from command name if not specified
            if category == 'Other' or not category:
                category = self._infer_category(command)
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(command)
        
        return categories
    
    def _infer_category(self, command: Dict[str, Any]) -> str:
        """Infer command category from name and description"""
        name = command.get('command', '').lower()
        description = command.get('description', '').lower()
        
        # Category inference rules
        if any(keyword in name for keyword in ['knowledge', 'ingest', 'find']):
            return 'Knowledge Management'
        elif any(keyword in name for keyword in ['list', 'add', 'create', 'move']):
            return 'List Management'  
        elif any(keyword in name for keyword in ['index', 'rebuild', 'update']):
            return 'Index Management'
        elif any(keyword in name for keyword in ['git', 'audit', 'check']):
            return 'Version Control'
        elif any(keyword in name for keyword in ['system', 'upgrade', 'config']):
            return 'System Management'
        elif any(keyword in name for keyword in ['doc', 'generate', 'export']):
            return 'Documentation'
        elif any(keyword in name for keyword in ['test', 'validate', 'monitor']):
            return 'Testing & Monitoring'
        elif any(keyword in description for keyword in ['analyze', 'process', 'transform']):
            return 'Data Processing'
        else:
            return 'General'
    
    def _generate_category_section(self, category: str, commands: List[Dict[str, Any]]) -> List[str]:
        """Generate markdown section for a command category"""
        content = [
            f"## {category.title()}",
            ""
        ]
        
        # Sort commands within category
        commands.sort(key=lambda x: x.get('command', ''))
        
        for command in commands:
            content.extend(self._generate_command_documentation(command))
        
        content.append("")
        return content
    
    def _generate_command_documentation(self, command: Dict[str, Any]) -> List[str]:
        """Generate documentation for a single command"""
        cmd_name = command.get('command', 'unnamed')
        description = command.get('description', 'No description available')
        
        content = [
            f"### `{cmd_name}`",
            "",
            f"**Description**: {description}",
            ""
        ]
        
        # Add usage example
        if 'usage' in command:
            content.extend([
                "**Usage**:",
                f"```bash",
                f"{command['usage']}",
                f"```",
                ""
            ])
        
        # Add parameters if available
        parameters = command.get('parameters', [])
        if parameters:
            content.extend([
                "**Parameters**:",
                ""
            ])
            for param in parameters:
                if isinstance(param, str):
                    content.append(f"- `{param}`: Parameter description")
                elif isinstance(param, dict):
                    param_name = param.get('name', 'unknown')
                    param_desc = param.get('description', 'No description')
                    param_type = param.get('type', 'string')
                    required = param.get('required', False)
                    req_text = " *(required)*" if required else " *(optional)*"
                    content.append(f"- `{param_name}` ({param_type}){req_text}: {param_desc}")
            content.append("")
        
        # Add steps if this is an authored command
        steps = command.get('steps', [])
        if steps:
            content.extend([
                "**Process Steps**:",
                ""
            ])
            for i, step in enumerate(steps, 1):
                if isinstance(step, str):
                    content.append(f"{i}. {step}")
                elif isinstance(step, dict):
                    step_name = step.get('name', f'Step {i}')
                    step_desc = step.get('description', 'No description')
                    content.append(f"{i}. **{step_name}**: {step_desc}")
            content.append("")
        
        # Add knowledge links
        knowledge_links = self._find_knowledge_links(command)
        if knowledge_links:
            content.extend([
                "**Related Knowledge**:",
                ""
            ])
            for link in knowledge_links:
                content.append(f"- [{link['title']}]({link['path']})")
            content.append("")
        
        # Add metadata
        metadata_items = []
        if 'version' in command:
            metadata_items.append(f"Version: {command['version']}")
        if 'created_at' in command:
            created_date = command['created_at'][:10] if len(command['created_at']) > 10 else command['created_at']
            metadata_items.append(f"Created: {created_date}")
        if 'source' in command:
            metadata_items.append(f"Source: {command['source']}")
        
        if metadata_items:
            content.extend([
                f"*{' | '.join(metadata_items)}*",
                ""
            ])
        
        content.extend(["---", ""])
        return content
    
    def _find_knowledge_links(self, command: Dict[str, Any]) -> List[Dict[str, str]]:
        """Find relevant knowledge base links for a command"""
        links = []
        cmd_name = command.get('command', '').lower()
        description = command.get('description', '').lower()
        
        # Search for relevant knowledge files
        if self.knowledge_base_path.exists():
            for knowledge_file in self.knowledge_base_path.rglob('*.md'):
                if knowledge_file.name == 'README.md':
                    continue
                
                file_name = knowledge_file.stem.lower()
                
                # Check if command name or keywords match knowledge file
                if (cmd_name in file_name or file_name in cmd_name or 
                    any(keyword in file_name for keyword in cmd_name.split('-'))):
                    
                    relative_path = knowledge_file.relative_to(Path("/home/workspace/N5"))
                    links.append({
                        'title': knowledge_file.stem.replace('_', ' ').replace('-', ' ').title(),
                        'path': f"/{relative_path}"
                    })
        
        return links[:3]  # Limit to 3 most relevant links
    
    def _write_markdown_file(self, content: str):
        """Write markdown content to commands.md"""
        try:
            # Create backup of existing file
            if self.commands_md_path.exists():
                backup_path = self.commands_md_path.with_suffix(f'.md.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                self.commands_md_path.rename(backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Write new content
            with open(self.commands_md_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Updated commands documentation: {self.commands_md_path}")
            
        except Exception as e:
            logger.error(f"Failed to write markdown file: {e}")
            raise
    
    def _update_individual_command_files(self, commands: List[Dict[str, Any]]):
        """Update individual command documentation files"""
        if not self.commands_dir.exists():
            logger.warning(f"Commands directory not found: {self.commands_dir}")
            return
        
        for command in commands:
            cmd_name = command.get('command', '')
            if cmd_name:
                self._update_single_command_file(command)
    
    def _update_single_command_file(self, command: Dict[str, Any]):
        """Update individual command documentation file"""
        try:
            cmd_name = command.get('command', '')
            cmd_file = self.commands_dir / f"{cmd_name}.md"
            
            # Generate individual command documentation
            content = [
                f"# {cmd_name}",
                "",
                f"**Description**: {command.get('description', 'No description available')}",
                ""
            ]
            
            # Add detailed sections for individual files
            if 'usage' in command:
                content.extend([
                    "## Usage",
                    "",
                    f"```bash",
                    f"{command['usage']}",
                    f"```",
                    ""
                ])
            
            # Add examples if available
            if 'examples' in command:
                content.extend([
                    "## Examples",
                    ""
                ])
                for example in command['examples']:
                    if isinstance(example, str):
                        content.extend([
                            f"```bash",
                            f"{example}",
                            f"```",
                            ""
                        ])
                    elif isinstance(example, dict):
                        content.extend([
                            f"### {example.get('title', 'Example')}",
                            "",
                            f"```bash",
                            f"{example.get('command', '')}",
                            f"```",
                            ""
                        ])
                        if 'description' in example:
                            content.extend([
                                f"{example['description']}",
                                ""
                            ])
            
            # Write individual command file
            with open(cmd_file, 'w') as f:
                f.write("\n".join(content))
            
            logger.debug(f"Updated individual command file: {cmd_file}")
            
        except Exception as e:
            logger.error(f"Failed to update individual command file for {command.get('command', 'unknown')}: {e}")


def main():
    """CLI interface for commands documentation updater"""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    updater = CommandsDocUpdater()
    result = updater.update_commands_documentation()
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    else:
        print(f"Successfully updated commands documentation:")
        print(f"  Commands processed: {result['commands_processed']}")
        print(f"  Output file: {result['output_file']}")
        print(f"  Updated at: {result['updated_at']}")


if __name__ == "__main__":
    main()