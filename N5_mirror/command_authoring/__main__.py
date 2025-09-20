#!/usr/bin/env python3
"""
Command Authoring System for N5 OS
Main orchestration script that ties all modules together.
"""

import logging
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Import all modules
from .conversation_parser import parse_conversation, validate_segments
from .llm_scoping_agent import scope_and_clarify_segments
from .command_structure_generator import generate_command_structure
from .validation_enhancement import validate_and_enhance_command
from .conflict_resolution_engine import resolve_conflicts_and_suggest
from .safe_export_handler import safe_export_command, validate_export_integrity


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """Set up global logging configuration."""
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure basic logging
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=handlers
    )
    
    # Set module-specific log levels
    logging.getLogger('command_authoring').setLevel(numeric_level)
    
    logging.info(f"Logging initialized at {log_level} level")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='N5 OS Command Authoring System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input "Create a command to process files"
  %(prog)s --input-file conversation.txt --output-file custom_commands.jsonl
  %(prog)s --input "Parse logs and extract errors" --dry-run
  %(prog)s --input-file input.txt --log-level DEBUG --log-file authoring.log
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input', '-i',
        type=str,
        help='Input text/conversation directly'
    )
    input_group.add_argument(
        '--input-file', '-f',
        type=str,
        help='Path to file containing input text/conversation'
    )
    
    # Output options
    parser.add_argument(
        '--output-file', '-o',
        type=str,
        default='N5/commands.jsonl',
        help='Output commands file (default: N5/commands.jsonl)'
    )
    
    # Processing options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without actually exporting to file'
    )
    
    parser.add_argument(
        '--skip-conflicts',
        action='store_true',
        help='Skip conflict resolution step'
    )
    
    parser.add_argument(
        '--force-export',
        action='store_true',
        help='Force export even if validation fails'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log to file in addition to stdout'
    )
    
    # Utility options
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate input and show structure, do not export'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output (sets log level to DEBUG)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='N5 Command Authoring System 1.0.0'
    )
    
    return parser.parse_args()


def load_input(args: argparse.Namespace) -> str:
    """Load input text from arguments or file."""
    if args.input:
        return args.input
    
    elif args.input_file:
        try:
            input_path = Path(args.input_file)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {args.input_file}")
            
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logging.info(f"Loaded {len(content)} characters from {args.input_file}")
            return content
            
        except Exception as e:
            logging.error(f"Failed to load input file: {e}")
            sys.exit(1)
    
    else:
        logging.error("No input provided")
        sys.exit(1)


def orchestrate_command_authoring(input_text: str, 
                                 output_file: str,
                                 skip_conflicts: bool = False,
                                 dry_run: bool = False,
                                 validate_only: bool = False,
                                 force_export: bool = False) -> Dict[str, Any]:
    """
    Main orchestration function that coordinates all modules.
    
    Args:
        input_text: Raw input text from user
        output_file: Path to output commands file
        skip_conflicts: Skip conflict resolution step
        dry_run: Perform dry run without exporting
        validate_only: Only validate, don't export
        force_export: Force export even if validation fails
        
    Returns:
        Result dictionary with processing information
    """
    start_time = time.time()
    
    result = {
        'success': False,
        'stages_completed': [],
        'total_time': 0,
        'final_command': None,
        'export_result': None
    }
    
    try:
        # Stage 1: Parse conversation
        logging.info("Stage 1: Parsing conversation...")
        stage_start = time.time()
        
        segments = parse_conversation(input_text)
        if not validate_segments(segments):
            raise ValueError("Conversation parsing validation failed")
        
        result['stages_completed'].append({
            'stage': 'conversation_parsing',
            'time': time.time() - stage_start,
            'segments_count': len(segments)
        })
        logging.info(f"Conversation parsing completed: {len(segments)} segments")
        
        # Stage 2: LLM Scoping and Clarification
        logging.info("Stage 2: LLM scoping and clarification...")
        stage_start = time.time()
        
        scoped_draft = scope_and_clarify_segments(segments)
        if 'error' in scoped_draft:
            raise ValueError(f"LLM scoping failed: {scoped_draft['error']}")
        
        result['stages_completed'].append({
            'stage': 'llm_scoping',
            'time': time.time() - stage_start,
            'confidence': scoped_draft.get('confidence', 0),
            'clarification_loops': scoped_draft.get('clarification_loops', 0)
        })
        logging.info("LLM scoping completed")
        
        # Stage 3: Command Structure Generation
        logging.info("Stage 3: Generating command structure...")
        stage_start = time.time()
        
        structured_command = generate_command_structure(scoped_draft)
        if 'error' in structured_command:
            raise ValueError(f"Command structure generation failed: {structured_command['error']}")
        
        result['stages_completed'].append({
            'stage': 'structure_generation',
            'time': time.time() - stage_start,
            'steps_count': len(structured_command.get('steps', [])),
            'complexity': structured_command.get('complexity', 'unknown')
        })
        logging.info(f"Command structure generated: {structured_command.get('command', 'unknown')}")
        
        # Stage 4: Validation and Enhancement
        logging.info("Stage 4: Validating and enhancing command...")
        stage_start = time.time()
        
        validated_command = validate_and_enhance_command(structured_command)
        if 'error' in validated_command:
            if not force_export:
                raise ValueError(f"Command validation failed: {validated_command['error']}")
            else:
                logging.warning(f"Validation failed but proceeding due to --force-export: {validated_command['error']}")
        
        validation_status = validated_command.get('validation', {}).get('status', 'unknown')
        result['stages_completed'].append({
            'stage': 'validation_enhancement',
            'time': time.time() - stage_start,
            'validation_status': validation_status,
            'enhancements_applied': len(validated_command.get('validation', {}).get('results', {}).get('enhancements', []))
        })
        logging.info(f"Validation completed with status: {validation_status}")
        
        # Stop here if validate-only mode
        if validate_only:
            result['success'] = True
            result['final_command'] = validated_command
            result['total_time'] = time.time() - start_time
            logging.info("Validation-only mode: stopping here")
            return result
        
        # Stage 5: Conflict Resolution (optional)
        resolved_command = validated_command
        if not skip_conflicts:
            logging.info("Stage 5: Resolving conflicts...")
            stage_start = time.time()
            
            resolved_command = resolve_conflicts_and_suggest(validated_command, output_file)
            if 'error' in resolved_command:
                logging.warning(f"Conflict resolution failed, proceeding with unresolved command: {resolved_command['error']}")
                resolved_command = validated_command
            
            conflicts_found = resolved_command.get('conflict_resolution', {}).get('scan_results', {}).get('conflicts_found', 0)
            result['stages_completed'].append({
                'stage': 'conflict_resolution',
                'time': time.time() - stage_start,
                'conflicts_found': conflicts_found,
                'resolution_status': resolved_command.get('conflict_resolution', {}).get('status', 'unknown')
            })
            logging.info(f"Conflict resolution completed: {conflicts_found} conflicts found")
        else:
            logging.info("Stage 5: Skipping conflict resolution")
        
        result['final_command'] = resolved_command
        
        # Stage 6: Export (optional)
        if not dry_run:
            logging.info("Stage 6: Exporting command...")
            stage_start = time.time()
            
            export_result = safe_export_command(resolved_command, output_file)
            if not export_result.get('success', False):
                raise ValueError(f"Export failed: {export_result.get('error', 'Unknown error')}")
            
            # Validate export
            command_id = resolved_command.get('id', '')
            validation_result = validate_export_integrity(Path(output_file), command_id)
            
            result['stages_completed'].append({
                'stage': 'export',
                'time': time.time() - stage_start,
                'export_success': export_result['success'],
                'file_path': export_result['file_path'],
                'backup_created': export_result.get('backup_created', False)
            })
            result['export_result'] = export_result
            logging.info(f"Export completed successfully to {output_file}")
        else:
            logging.info("Stage 6: Dry run mode - skipping export")
            result['export_result'] = {'dry_run': True}
        
        # Success!
        result['success'] = True
        result['total_time'] = time.time() - start_time
        
        logging.info(f"Command authoring completed successfully in {result['total_time']:.3f}s")
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        result['total_time'] = time.time() - start_time
        logging.error(f"Command authoring failed: {e}")
        return result


def print_summary(result: Dict[str, Any], args: argparse.Namespace) -> None:
    """Print a summary of the processing results."""
    print("\n" + "="*60)
    print("N5 COMMAND AUTHORING SUMMARY")
    print("="*60)
    
    if result['success']:
        print("✅ Status: SUCCESS")
    else:
        print("❌ Status: FAILED")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    print(f"⏱️  Total Time: {result['total_time']:.3f}s")
    print(f"📝 Stages Completed: {len(result['stages_completed'])}")
    
    # Show stage breakdown
    print("\nStage Breakdown:")
    for i, stage in enumerate(result['stages_completed'], 1):
        stage_name = stage['stage'].replace('_', ' ').title()
        print(f"  {i}. {stage_name}: {stage['time']:.3f}s")
        
        # Show stage-specific details
        if stage['stage'] == 'conversation_parsing':
            print(f"     └── Segments: {stage['segments_count']}")
        elif stage['stage'] == 'llm_scoping':
            print(f"     └── Confidence: {stage['confidence']:.2f}")
            if stage['clarification_loops'] > 0:
                print(f"     └── Clarification loops: {stage['clarification_loops']}")
        elif stage['stage'] == 'structure_generation':
            print(f"     └── Steps: {stage['steps_count']}, Complexity: {stage['complexity']}")
        elif stage['stage'] == 'validation_enhancement':
            print(f"     └── Status: {stage['validation_status']}")
            if stage['enhancements_applied'] > 0:
                print(f"     └── Enhancements: {stage['enhancements_applied']}")
        elif stage['stage'] == 'conflict_resolution':
            print(f"     └── Conflicts found: {stage['conflicts_found']}")
        elif stage['stage'] == 'export':
            print(f"     └── Exported to: {stage['file_path']}")
            if stage['backup_created']:
                print(f"     └── Backup created: Yes")
    
    # Show final command info
    if result.get('final_command'):
        command = result['final_command']
        print(f"\nGenerated Command:")
        print(f"  📛 Name: {command.get('command', 'Unknown')}")
        print(f"  🆔 ID: {command.get('id', 'Unknown')}")
        print(f"  📂 Category: {command.get('category', 'Unknown')}")
        print(f"  📄 Description: {command.get('description', 'No description')[:100]}...")
        if command.get('tags'):
            print(f"  🏷️  Tags: {', '.join(command['tags'])}")
    
    # Show export info
    if not args.dry_run and result.get('export_result') and result['export_result'].get('success'):
        export = result['export_result']
        print(f"\nExport Details:")
        print(f"  📁 File: {export['file_path']}")
        print(f"  📊 File size: {export.get('file_size_after', 0)} bytes")
        if export.get('redistillation', {}).get('needed'):
            redistill = export['redistillation']
            print(f"  🔄 Redistillation: {redistill.get('duplicates_removed', 0)} duplicates removed")
    
    elif args.dry_run:
        print(f"\n🧪 Dry Run: Command structure generated but not exported")
    elif args.validate_only:
        print(f"\n✅ Validation Only: Command validated successfully")
    
    print("="*60)


def main() -> int:
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Set up logging
        log_level = 'DEBUG' if args.verbose else args.log_level
        setup_logging(log_level, args.log_file)
        
        logging.info("N5 Command Authoring System starting...")
        logging.debug(f"Arguments: {vars(args)}")
        
        # Load input
        input_text = load_input(args)
        if not input_text.strip():
            logging.error("Input text is empty")
            return 1
        
        logging.info(f"Processing input: {len(input_text)} characters")
        
        # Orchestrate the process
        result = orchestrate_command_authoring(
            input_text=input_text,
            output_file=args.output_file,
            skip_conflicts=args.skip_conflicts,
            dry_run=args.dry_run,
            validate_only=args.validate_only,
            force_export=args.force_export
        )
        
        # Print summary
        if not args.log_level == 'DEBUG':  # Don't print summary in debug mode to avoid clutter
            print_summary(result, args)
        
        # Return appropriate exit code
        return 0 if result['success'] else 1
        
    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
        return 130
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())