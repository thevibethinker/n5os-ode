#!/usr/bin/env python3
"""
N5OS Bootstrap Personalization Engine

Personalizes N5OS installation for specific instances by:
1. Loading and merging instance config with defaults
2. Processing Jinja2 templates 
3. Replacing placeholders in installed files
4. Generating instance-specific CLAUDE.md and session-context.md
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any
import re


def deep_merge(base: Dict[Any, Any], override: Dict[Any, Any]) -> Dict[Any, Any]:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def load_config(config_path: Path, skill_root: Path) -> Dict[str, Any]:
    """Load and merge instance config with defaults."""
    defaults_path = skill_root / 'config/defaults.yaml'
    
    # Load defaults
    with open(defaults_path, 'r') as f:
        defaults = yaml.safe_load(f)
    
    # Load instance config
    with open(config_path, 'r') as f:
        instance = yaml.safe_load(f)
    
    # Deep merge
    config = deep_merge(defaults, instance)
    
    return config


def render_template(template_content: str, config: Dict[str, Any]) -> str:
    """Render template using simple string replacement (avoiding Jinja2 dependency)."""
    result = template_content
    
    # Handle conditional blocks first
    def process_conditionals(text):
        # Process {% if condition %}...{% endif %} blocks
        import re
        
        # Find all if blocks
        if_pattern = r'\{\%\s*if\s+([^%}]+)\s*\%\}(.*?)\{\%\s*endif\s*\%\}'
        
        def replace_if_block(match):
            condition = match.group(1).strip()
            content = match.group(2)
            
            # Evaluate condition
            try:
                # Simple condition evaluation for basic cases
                if '.' in condition:
                    parts = condition.split('.')
                    value = config
                    for part in parts:
                        value = value[part]
                    
                    # Check truthiness
                    if value and value != [] and value != '':
                        return content
                    else:
                        return ''
                elif condition in config:
                    if config[condition]:
                        return content
                    else:
                        return ''
                else:
                    return ''  # Unknown condition, skip block
            except (KeyError, TypeError):
                return ''  # Condition evaluation failed, skip block
        
        return re.sub(if_pattern, replace_if_block, text, flags=re.DOTALL)
    
    # Handle for loops
    def process_loops(text):
        # Process {% for item in list %}...{% endfor %} blocks
        import re
        
        for_pattern = r'\{\%\s*for\s+(\w+)\s+in\s+([^%}]+)\s*\%\}(.*?)\{\%\s*endfor\s*\%\}'
        
        def replace_for_block(match):
            var_name = match.group(1).strip()
            list_path = match.group(2).strip()  
            content = match.group(3)
            
            try:
                # Get the list value
                if '.' in list_path:
                    parts = list_path.split('.')
                    value = config
                    for part in parts:
                        value = value[part]
                else:
                    value = config.get(list_path, [])
                
                if not isinstance(value, list):
                    return ''
                
                # Render content for each item
                result_parts = []
                for item in value:
                    item_content = content
                    
                    # Handle {{ var_name | filter }} patterns within loop content
                    var_with_filter_pattern = rf'\{{\{{\s*{var_name}\s*(\|\s*[^}}]+)?\s*\}}}}'
                    
                    def replace_loop_var(inner_match):
                        filter_part = inner_match.group(1)
                        item_str = str(item)
                        
                        if filter_part:
                            # Process filters
                            filters = [f.strip() for f in filter_part.split('|')[1:]]  # Skip first empty element
                            for filter_name in filters:
                                if filter_name == 'title':
                                    item_str = item_str.title()
                                elif filter_name == 'upper':
                                    item_str = item_str.upper()
                                elif filter_name == 'lower':
                                    item_str = item_str.lower()
                                elif filter_name.startswith('replace('):
                                    # Extract replace arguments
                                    import ast
                                    try:
                                        args = filter_name[8:-1]  # Remove 'replace(' and ')'
                                        old, new = ast.literal_eval(f"({args})")
                                        item_str = item_str.replace(old, new)
                                    except:
                                        pass  # Skip if parsing fails
                        
                        return item_str
                    
                    item_content = re.sub(var_with_filter_pattern, replace_loop_var, item_content)
                    
                    # Also handle simple variable references without {{ }}
                    item_content = item_content.replace(f'{var_name}', str(item))
                    
                    result_parts.append(item_content)
                
                return ''.join(result_parts)
                
            except (KeyError, TypeError):
                return ''  # Loop evaluation failed
        
        return re.sub(for_pattern, replace_for_block, text, flags=re.DOTALL)
    
    # Process template blocks
    result = process_conditionals(result)
    result = process_loops(result)
    
    # Replace simple variable patterns like {{ instance.name }}
    def replace_var(match):
        var_path = match.group(1).strip()
        
        # Handle filters
        if ' | ' in var_path:
            parts = var_path.split(' | ')
            var_path = parts[0].strip()
            filters = [f.strip() for f in parts[1:]]
        else:
            filters = []
        
        # Get variable value
        var_parts = var_path.split('.')
        
        try:
            value = config
            for part in var_parts:
                value = value[part]
            
            # Handle list formatting
            if isinstance(value, list):
                if any('join(' in f for f in filters):
                    separator = ', '  # Default separator
                    return separator.join(str(v) for v in value)
                else:
                    return str(value)
            
            # Apply filters
            result_val = str(value)
            for filter_name in filters:
                if filter_name == 'title':
                    result_val = result_val.title()
                elif filter_name == 'upper':
                    result_val = result_val.upper()
                elif filter_name == 'lower':  
                    result_val = result_val.lower()
                elif filter_name.startswith('replace('):
                    # Extract replace arguments
                    import ast
                    try:
                        # Parse replace('_', ' ') format
                        args = filter_name[8:-1]  # Remove 'replace(' and ')'
                        old, new = ast.literal_eval(f"({args})")
                        result_val = result_val.replace(old, new)
                    except:
                        pass  # Skip if parsing fails
                elif filter_name.startswith('join('):
                    # This should have been handled above for lists
                    pass
                elif filter_name.startswith('default('):
                    # Extract default value
                    try:
                        default_val = filter_name[8:-1]  # Remove 'default(' and ')'
                        if not result_val or result_val == 'None':
                            result_val = default_val.strip('\'"')
                    except:
                        pass
            
            return result_val
            
        except (KeyError, TypeError):
            # Return original if variable not found
            return match.group(0)
    
    # Replace {{ variable }} patterns
    result = re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_var, result)
    
    return result


def write_file(filepath: Path, content: str, dry_run: bool = False, verbose: bool = False):
    """Write file with optional dry-run mode."""
    if dry_run:
        print(f"[DRY-RUN] Would write {filepath}")
        if verbose:
            print(f"Content preview:\n{content[:200]}...")
        return
    
    # Create parent directories
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    with open(filepath, 'w') as f:
        f.write(content)
    
    if verbose:
        print(f"Wrote {filepath}")


def find_installed_files() -> list[Path]:
    """Find files that may need placeholder replacement."""
    workspace = Path('/home/workspace')
    
    # Look for markdown files in key locations
    patterns = [
        'N5/prefs/**/*.md',
        'Personal/Knowledge/**/*.md', 
        'Documents/System/**/*.md',
        '.claude/*.md'
    ]
    
    files = []
    for pattern in patterns:
        files.extend(workspace.glob(pattern))
    
    return files


def main():
    parser = argparse.ArgumentParser(description='Personalize N5OS Bootstrap installation')
    parser.add_argument('config', help='Path to instance config (e.g., instances/zoputer.yaml)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without writing')
    parser.add_argument('--output-dir', help='Write generated files to DIR instead of destinations')
    parser.add_argument('--verbose', action='store_true', help='Show detailed progress')
    
    args = parser.parse_args()
    
    # Determine skill root
    skill_root = Path(__file__).parent.parent
    
    # Load configuration
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = skill_root / config_path
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    if args.verbose:
        print(f"Loading config from {config_path}")
    
    config = load_config(config_path, skill_root)
    
    if args.verbose:
        print(f"Merged config: {config}")
    
    # Set output directory
    if args.output_dir:
        output_root = Path(args.output_dir)
    else:
        output_root = Path('/home/workspace')
    
    # Generate CLAUDE.md
    claude_template_path = skill_root / 'templates/CLAUDE.md.j2'
    if claude_template_path.exists():
        if args.verbose:
            print("Generating CLAUDE.md...")
        
        with open(claude_template_path, 'r') as f:
            template_content = f.read()
        
        claude_content = render_template(template_content, config)
        claude_output = output_root / '.claude/CLAUDE.md'
        
        write_file(claude_output, claude_content, args.dry_run, args.verbose)
    
    # Generate session-context.md
    session_template_path = skill_root / 'templates/session-context.j2'
    if session_template_path.exists():
        if args.verbose:
            print("Generating session-context.md...")
        
        with open(session_template_path, 'r') as f:
            template_content = f.read()
        
        session_content = render_template(template_content, config)
        session_output = output_root / '.claude/session-context.md'
        
        write_file(session_output, session_content, args.dry_run, args.verbose)
    
    # Replace placeholders in installed files
    if args.verbose:
        print("Processing installed files for placeholder replacement...")
    
    placeholder_map = {
        '{{WORKSPACE}}': '/home/workspace',
        '{{INSTANCE}}': config['instance']['name'],
        '{{OWNER}}': config['instance']['owner'],
        '{{HANDLE}}': config['instance']['handle']
    }
    
    installed_files = find_installed_files()
    
    for file_path in installed_files:
        if not file_path.exists() or not file_path.is_file():
            continue
            
        try:
            content = file_path.read_text()
            original_content = content
            
            # Apply replacements
            for placeholder, replacement in placeholder_map.items():
                content = content.replace(placeholder, replacement)
            
            # Only write if content changed
            if content != original_content:
                if args.dry_run:
                    print(f"[DRY-RUN] Would update placeholders in {file_path}")
                else:
                    file_path.write_text(content)
                    if args.verbose:
                        print(f"Updated placeholders in {file_path}")
        
        except Exception as e:
            if args.verbose:
                print(f"Warning: Could not process {file_path}: {e}")
    
    print(f"Personalization complete for {config['instance']['name']}")
    
    if args.dry_run:
        print("\n[DRY-RUN] No files were actually modified. Run without --dry-run to apply changes.")


if __name__ == '__main__':
    main()