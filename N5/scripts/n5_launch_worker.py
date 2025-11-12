#!/usr/bin/env python3
"""
N5 Launch Worker - Enhanced Worker Spawning Command

Purpose: Provide an enhanced CLI interface for spawning parallel worker threads
with support for worker types, interactive wizard, and optimal configuration.

Usage:
    n5 launch-worker --parent con_XXX --type build --instruction "Implement auth system"
    n5 launch-worker --parent con_XXX --wizard  # Interactive mode
    n5 launch-worker --parent con_XXX --type research  # Research-optimized worker
    n5 launch-worker --parent con_XXX --type writer --instruction "Write documentation"

Worker Types:
    build: Optimized for implementation, coding, building systems
    general: Default behavior, general-purpose worker
    research: Optimized for research, analysis, information gathering
    analysis: Optimized for comparative analysis, evaluation, synthesis
    writer: Optimized for content creation, writing, documentation

Author: Vibe Builder
Version: 1.1.0
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import json

# ANSI color codes for terminal output
COLORS = {
    'blue': '\033[94m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'bold': '\033[1m',
    'reset': '\033[0m'
}

WORKER_TYPES = {
    'build': {
        'description': 'Optimized for implementation, coding, building systems',
        'tags': ['#build', '#implementation'],
        'focus_prompt': 'Technical implementation and code building',
        'persona_hint': 'Consider routing to Vibe Builder for implementation tasks'
    },
    'general': {
        'description': 'Default behavior, general-purpose worker',
        'tags': [],
        'focus_prompt': 'General purpose tasks',
        'persona_hint': 'Use default Operator routing based on task type'
    },
    'research': {
        'description': 'Optimized for research, analysis, information gathering',
        'tags': ['#research', '#analysis'],
        'focus_prompt': 'Deep research and information synthesis',
        'persona_hint': 'Consider routing to Vibe Researcher for deep investigation'
    },
    'analysis': {
        'description': 'Optimized for comparative analysis, evaluation, synthesis',
        'tags': ['#analysis', '#synthesis'],
        'focus_prompt': 'Comparative analysis and evaluation',
        'persona_hint': 'Consider routing to Vibe Strategist for strategic analysis'
    },
    'writer': {
        'description': 'Optimized for content creation, writing, documentation',
        'tags': ['#writing', '#content', '#documentation'],
        'focus_prompt': 'Content creation and written communication',
        'persona_hint': 'Consider routing to Vibe Writer for content tasks'
    }
}


class LaunchWorker:
    """Enhanced worker launcher with wizard support and worker type optimization."""
    
    def __init__(self):
        self.script_path = Path(__file__).parent / "spawn_worker.py"
        self.records_dir = Path("/home/workspace/Records/Temporary")
        
    def print_colored(self, text: str, color: str, bold: bool = False):
        """Print colored text to terminal."""
        prefix = COLORS['bold'] if bold else ''
        print(f"{prefix}{COLORS[color]}{text}{COLORS['reset']}")
    
    def print_header(self):
        """Print the command header."""
        print()
        self.print_colored("=" * 70, 'blue')
        self.print_colored("N5 Worker Launcher v1.0.0", 'blue', bold=True)
        self.print_colored("Parallel Thread Orchestrator", 'blue')
        self.print_colored("=" * 70, 'blue')
        print()
    
    def validate_conversation_id(self, convo_id: str) -> bool:
        """Validate conversation ID format."""
        if not convo_id.startswith('con_'):
            self.print_colored("❌ Error: Invalid conversation ID format", 'red', bold=True)
            self.print_colored("   Must start with 'con_'", 'red')
            return False
        if len(convo_id) < 10:
            self.print_colored("❌ Error: Conversation ID too short", 'red', bold=True)
            return False
        return True
    
    def check_parent_exists(self, parent_id: str) -> bool:
        """Check if parent conversation workspace exists."""
        workspace = Path(f"/home/.z/workspaces/{parent_id}")
        if not workspace.exists():
            self.print_colored("❌ Error: Parent conversation workspace not found", 'red', bold=True)
            self.print_colored(f"   Path: {workspace}", 'red')
            return False
        return True
    
    def run_wizard(self, args: argparse.Namespace) -> Optional[Dict[str, Any]]:
        """Run interactive wizard to configure worker."""
        print()
        self.print_colored("🧙‍♂️ Interactive Worker Configuration Wizard", 'blue', bold=True)
        print()
        
        # Get parent conversation ID
        while True:
            parent = input(self.colored_text("Enter parent conversation ID: ", 'yellow'))
            if self.validate_conversation_id(parent) and self.check_parent_exists(parent):
                break
        
        # Get worker type
        print()
        self.print_colored("Select worker type:", 'blue', bold=True)
        for i, (wtype, config) in enumerate(WORKER_TYPES.items(), 1):
            print(f"  {i}. {wtype.upper()}")
            print(f"     {config['description']}")
        
        while True:
            try:
                choice = input(self.colored_text("\nSelect (1-4, default=4/general): ", 'yellow')).strip()
                if not choice:
                    worker_type = 'general'
                    break
                choice = int(choice)
                if 1 <= choice <= len(WORKER_TYPES):
                    worker_type = list(WORKER_TYPES.keys())[choice - 1]
                    break
                else:
                    self.print_colored("Invalid choice, try again", 'red')
            except ValueError:
                self.print_colored("Please enter a number", 'red')
        
        self.print_colored(f"✓ Selected: {worker_type}", 'green')
        
        # Get instruction
        print()
        self.print_colored("Worker Instruction", 'blue', bold=True)
        print("Describe what this worker should accomplish.")
        print("Leave empty to spawn agnostic (general-purpose) worker.")
        instruction = input(self.colored_text("\nInstruction: ", 'yellow')).strip() or None
        
        # Get estimated scope
        print()
        self.print_colored("Estimated Scope", 'blue', bold=True)
        scope_options = ['Small (1-2 hours)', 'Medium (1/2 day)', 'Large (1-2 days)', 'Unknown']
        for i, option in enumerate(scope_options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = input(self.colored_text("\nSelect (1-4, default=4): ", 'yellow')).strip()
                if not choice:
                    scope = 'Unknown'
                    break
                choice = int(choice)
                if 1 <= choice <= len(scope_options):
                    scope = scope_options[choice - 1]
                    break
                else:
                    self.print_colored("Invalid choice, try again", 'red')
            except ValueError:
                self.print_colored("Please enter a number", 'red')
        
        # Show preview
        print()
        self.print_colored("=" * 70, 'blue')
        self.print_colored("Worker Configuration Preview", 'blue', bold=True)
        self.print_colored("=" * 70, 'blue')
        print()
        
        print(f"Parent:        {parent}")
        print(f"Type:          {worker_type}")
        print(f"Description:   {WORKER_TYPES[worker_type]['description']}")
        print(f"Scope:         {scope}")
        
        if instruction:
            print(f"\nInstruction:\n  {instruction}")
        else:
            print(f"\nInstruction:   (agnostic - general purpose)")
        
        print()
        
        # Confirm
        while True:
            confirm = input(self.colored_text("\nLaunch worker? (y/n): ", 'yellow')).strip().lower()
            if confirm == 'y':
                return {
                    'parent': parent,
                    'worker_type': worker_type,
                    'instruction': instruction,
                    'scope': scope
                }
            elif confirm == 'n':
                self.print_colored("❌ Cancelled by user", 'red')
                return None
    
    def colored_text(self, text: str, color: str, bold: bool = False) -> str:
        """Return colored text string."""
        prefix = COLORS['bold'] if bold else ''
        return f"{prefix}{COLORS[color]}{text}{COLORS['reset']}"
    
    def enhance_instruction(self, instruction: str, worker_type: str) -> str:
        """Enhance instruction based on worker type."""
        if not instruction:
            return None
        
        type_config = WORKER_TYPES[worker_type]
        
        # Add type-specific context
        enhancements = {
            'build': f"{instruction}\n\nFocus on implementation with proper testing, error handling, and documentation.",
            'research': f"{instruction}\n\nConduct thorough research with citations, consider multiple sources, and synthesize findings.",
            'analysis': f"{instruction}\n\nProvide comparative analysis, consider alternatives, and include recommendations.",
            'general': instruction
        }
        
        return enhancements.get(worker_type, instruction)
    
    def spawn_worker(self, parent: str, instruction: Optional[str], 
                     dry_run: bool = False) -> tuple[int, str]:
        """Call spawn_worker.py with proper arguments."""
        cmd = [
            sys.executable, str(self.script_path),
            '--parent', parent
        ]
        
        if instruction:
            cmd.extend(['--instruction', instruction])
        
        if dry_run:
            cmd.append('--dry-run')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
            
            # Extract assignment file path
            assignment_path = None
            for line in output.split('\n'):
                if '.md' in line and ('assignment' in line.lower() or 'open this file' in line.lower()):
                    assignment_path = line
                    break
            
            return result.returncode, output
        except subprocess.TimeoutExpired:
            return 1, "❌ Error: Command timed out after 30 seconds"
        except Exception as e:
            return 1, f"❌ Error spawning worker: {e}"
    
    def display_success(self, returncode: int, output: str, config: Dict[str, Any]):
        """Display success message with next steps."""
        if returncode == 0:
            self.print_colored("✓ Worker spawned successfully!", 'green', bold=True)
            print()
            
            # Extract assignment file
            assignment_file = None
            for line in output.split('\n'):
                if 'WORKER_ASSIGNMENT' in line and '.md' in line:
                    if '/' in line:
                        assignment_file = line.split('/')[-1]
                        break
            
            if assignment_file:
                print("Next steps:")
                print(f"1. Open the worker assignment file:")
                self.print_colored(f"   Records/Temporary/{assignment_file}", 'blue')
                print()
                print(f"2. Launch a new conversation and load the file")
                print(f"3. The worker will automatically link to parent: {config['parent']}")
                print()
                self.print_colored("The worker is ready to work in parallel!", 'green')
            
            print()
            self.print_colored("=" * 70, 'blue')
        else:
            self.print_colored("❌ Failed to spawn worker", 'red', bold=True)
            print(f"Exit code: {returncode}")
            if output:
                print("\nOutput:")
                print(output)
    
    def run_cli(self, args: argparse.Namespace):
        """Run in CLI mode (non-interactive)."""
        # Validate parent
        if not self.validate_conversation_id(args.parent):
            return 1
        if not self.check_parent_exists(args.parent):
            return 1
        
        # Enhance instruction based on worker type
        instruction = self.enhance_instruction(args.instruction, args.type)
        
        # Show configuration
        print()
        self.print_colored("Worker Configuration", 'blue', bold=True)
        print(f"Parent:        {args.parent}")
        print(f"Type:          {args.type}")
        print(f"Description:   {WORKER_TYPES[args.type]['description']}")
        if instruction:
            print(f"Instruction:\n  {instruction}")
        else:
            print("Instruction:   (agnostic - general purpose)")
        print()
        
        # Spawn worker
        returncode, output = self.spawn_worker(args.parent, instruction, args.dry_run)
        
        # Display results
        config = {
            'parent': args.parent,
            'worker_type': args.type,
            'instruction': instruction
        }
        self.display_success(returncode, output, config)
        
        return returncode
    
    def run(self, args: argparse.Namespace) -> int:
        """Main entry point."""
        self.print_header()
        
        if args.wizard:
            config = self.run_wizard(args)
            if not config:
                return 1
            
            # Spawn worker with wizard config
            instruction = self.enhance_instruction(config['instruction'], config['worker_type'])
            returncode, output = self.spawn_worker(
                config['parent'], 
                instruction, 
                args.dry_run
            )
            
            self.display_success(returncode, output, config)
            return returncode
        else:
            return self.run_cli(args)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='N5 Launch Worker - Enhanced parallel worker spawning'
    )
    
    parser.add_argument(
        '--parent', '-p',
        help='Parent conversation ID (e.g., con_XXX)'
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=list(WORKER_TYPES.keys()),
        default='general',
        help='Worker type specialization (default: general)'
    )
    
    parser.add_argument(
        '--instruction', '-i',
        help='Specific instruction for the worker (optional)'
    )
    
    parser.add_argument(
        '--wizard', '-w',
        action='store_true',
        help='Run interactive wizard for worker configuration'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without actually spawning'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.wizard and not args.parent:
        print()
        launcher = LaunchWorker()
        launcher.print_colored("❌ Error: --parent is required (unless using --wizard)", 'red', bold=True)
        print()
        parser.print_help()
        return 1
    
    # Run launcher
    launcher = LaunchWorker()
    return launcher.run(args)


if __name__ == '__main__':
    sys.exit(main())



