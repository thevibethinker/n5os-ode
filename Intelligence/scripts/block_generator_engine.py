#!/usr/bin/env python3
"""
Block Generator Engine - W3 Core Engine
Unified system for generating intelligence blocks from meeting transcripts.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from Intelligence.scripts import block_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


class BlockGeneratorEngine:
    """Core engine for generating intelligence blocks."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or block_db.DB_PATH
        logger.info(f"Initialized BlockGeneratorEngine with database: {self.db_path}")
    
    def list_blocks(
        self,
        category: Optional[str] = None,
        status: str = "active"
    ) -> List[Dict[str, Any]]:
        """List available blocks from the registry."""
        blocks = block_db.list_blocks(category=category, status=status)
        logger.info(f"Found {len(blocks)} blocks")
        return blocks
    
    def get_block_definition(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Get block definition from database."""
        block = block_db.get_block(block_id)
        if not block:
            logger.error(f"Block {block_id} not found in database")
            return None
        logger.info(f"Loaded block definition: {block_id} - {block.get('name', 'Unknown')}")
        return block
    
    def load_transcript(self, transcript_path: str) -> Optional[str]:
        """Load transcript content from file."""
        path = Path(transcript_path)
        if not path.exists():
            logger.error(f"Transcript file not found: {transcript_path}")
            return None
        try:
            content = path.read_text(encoding='utf-8')
            logger.info(f"Loaded transcript: {transcript_path} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error loading transcript: {e}", exc_info=True)
            return None
    
    def build_generation_prompt(
        self,
        block: Dict[str, Any],
        transcript: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the complete prompt for LLM generation."""
        block_id = block.get('block_id', 'Unknown')
        block_name = block.get('name', 'Unknown')
        description = block.get('description', 'No description available')
        input_reqs = block.get('input_requirements', '')
        output_format = block.get('output_format', 'Markdown')
        
        prompt = f"""# Block Generation Request

**Block ID:** {block_id}
**Block Name:** {block_name}
**Output Format:** {output_format}

## Description
{description}

## Input Requirements
{input_reqs if input_reqs else "Process the meeting transcript and extract relevant information."}

## Transcript
{transcript}

## Instructions
Generate the {block_name} block according to the specifications above.
Focus on accuracy, completeness, and following the output format exactly.

"""
        if context:
            prompt += f"\n## Additional Context\n{json.dumps(context, indent=2)}\n"
        
        return prompt
    
    def generate_with_llm(self, prompt: str, block_id: str) -> Optional[str]:
        """Generate block content using LLM (placeholder implementation)."""
        logger.info(f"LLM generation requested for {block_id}")
        logger.info(f"Prompt length: {len(prompt)} characters")
        
        placeholder_output = f"""# {block_id} - PLACEHOLDER OUTPUT

This is a placeholder output from the Block Generator Engine.

In production, this would be replaced with actual LLM-generated content.

**Status:** LLM integration pending
**Generated:** {datetime.utcnow().isoformat()}
"""
        logger.warning("Using placeholder LLM output - LLM integration not yet implemented")
        return placeholder_output
    
    def validate_output(self, output: str, block: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated output against block rubric."""
        block_id = block.get('block_id')
        rubric = block.get('validation_rubric', '')
        
        failures = []
        warnings = []
        
        if not output or len(output.strip()) < 10:
            failures.append("Output is empty or too short")
        
        if not rubric:
            warnings.append("No validation rubric defined for this block")
        
        passed = len(failures) == 0
        score = 1.0 if passed else 0.0
        
        return {
            'passed': passed,
            'score': score,
            'failures': failures,
            'warnings': warnings
        }
    
    def generate_block(
        self,
        block_id: str,
        transcript_path: str,
        meeting_id: str,
        output_dir: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Generate a single block."""
        logger.info(f"Starting generation: {block_id} for meeting {meeting_id}")
        
        block = self.get_block_definition(block_id)
        if not block:
            return {'success': False, 'error': f'Block {block_id} not found'}
        
        transcript = self.load_transcript(transcript_path)
        if not transcript:
            return {'success': False, 'error': f'Failed to load transcript: {transcript_path}'}
        
        if not dry_run:
            gen_id = block_db.log_generation(
                block_id=block_id,
                meeting_id=meeting_id,
                status='in_progress',
                input_context={
                    'transcript_path': transcript_path,
                    'transcript_hash': str(hash(transcript))
                }
            )
            logger.info(f"Logged generation attempt: {gen_id}")
        else:
            gen_id = 'dry-run'
            logger.info("DRY RUN: Skipping generation logging")
        
        try:
            prompt = self.build_generation_prompt(block, transcript, context)
            output = self.generate_with_llm(prompt, block_id)
            if not output:
                raise Exception("LLM generation returned no output")
            
            validation = self.validate_output(output, block)
            
            if output_dir:
                output_path = Path(output_dir) / f"{block_id}_{meeting_id}.md"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if not dry_run:
                    output_path.write_text(output, encoding='utf-8')
                    logger.info(f"Saved output: {output_path}")
                else:
                    logger.info(f"DRY RUN: Would save to {output_path}")
            else:
                output_path = None
            
            if not dry_run:
                block_db.update_generation(
                    generation_id=gen_id,
                    status='success' if validation['passed'] else 'failed',
                    output_path=str(output_path) if output_path else None
                )
                block_db.log_validation(
                    generation_id=gen_id,
                    block_id=block_id,
                    validation_type='rubric',
                    status='passed' if validation['passed'] else 'failed',
                    score=validation.get('score'),
                    failures=validation.get('failures'),
                    warnings=validation.get('warnings')
                )
                block_db.update_block_stats(block_id=block_id, success=validation['passed'])
            
            return {
                'success': validation['passed'],
                'output_path': str(output_path) if output_path else None,
                'generation_id': gen_id,
                'validation': validation,
                'output': output
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            if not dry_run:
                block_db.update_generation(generation_id=gen_id, status='failed', error_message=str(e))
                block_db.update_block_stats(block_id=block_id, success=False)
            return {'success': False, 'error': str(e), 'generation_id': gen_id}
    
    def generate_all(
        self,
        transcript_path: str,
        meeting_id: str,
        output_dir: Optional[str] = None,
        category: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Generate all required blocks for a meeting."""
        logger.info(f"Starting batch generation for meeting {meeting_id}")
        blocks = self.list_blocks(category=category, status='active')
        
        if not blocks:
            logger.warning("No blocks found to generate")
            return {'total': 0, 'succeeded': 0, 'failed': 0, 'results': []}
        
        results = []
        succeeded = 0
        failed = 0
        
        for block in blocks:
            block_id = block['block_id']
            logger.info(f"Generating {block_id} ({succeeded + failed + 1}/{len(blocks)})")
            result = self.generate_block(
                block_id=block_id,
                transcript_path=transcript_path,
                meeting_id=meeting_id,
                output_dir=output_dir,
                dry_run=dry_run
            )
            results.append({'block_id': block_id, **result})
            if result.get('success'):
                succeeded += 1
            else:
                failed += 1
        
        logger.info(f"Batch generation complete: {succeeded} succeeded, {failed} failed")
        return {'total': len(blocks), 'succeeded': succeeded, 'failed': failed, 'results': results}


def cmd_generate(args) -> int:
    """Generate a single block."""
    engine = BlockGeneratorEngine()
    result = engine.generate_block(
        block_id=args.block_id,
        transcript_path=args.transcript,
        meeting_id=args.meeting_id,
        output_dir=args.output_dir,
        dry_run=args.dry_run
    )
    if result.get('success'):
        print(f"✅ Generation succeeded: {result.get('output_path')}")
        print(f"   Generation ID: {result.get('generation_id')}")
        if result.get('validation', {}).get('warnings'):
            print(f"   Warnings: {', '.join(result['validation']['warnings'])}")
        return 0
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return 1


def cmd_generate_all(args) -> int:
    """Generate all blocks for a meeting."""
    engine = BlockGeneratorEngine()
    result = engine.generate_all(
        transcript_path=args.transcript,
        meeting_id=args.meeting_id,
        output_dir=args.output_dir,
        category=args.category,
        dry_run=args.dry_run
    )
    print(f"Batch generation complete:")
    print(f"  Total: {result['total']}")
    print(f"  ✅ Succeeded: {result['succeeded']}")
    print(f"  ❌ Failed: {result['failed']}")
    if result['failed'] > 0:
        print("\nFailed blocks:")
        for r in result['results']:
            if not r.get('success'):
                print(f"  - {r['block_id']}: {r.get('error', 'Unknown error')}")
    return 0 if result['failed'] == 0 else 1


def cmd_list_blocks(args) -> int:
    """List available blocks."""
    engine = BlockGeneratorEngine()
    blocks = engine.list_blocks(category=args.category, status=args.status)
    if not blocks:
        print("No blocks found")
        return 0
    print(f"Found {len(blocks)} blocks:\n")
    for block in blocks:
        print(f"  {block['block_id']}: {block.get('name', 'Unknown')}")
        print(f"    Category: {block.get('category', 'Unknown')}")
        print(f"    Status: {block.get('status', 'Unknown')}")
        if block.get('description'):
            desc = block['description'][:100] + "..." if len(block['description']) > 100 else block['description']
            print(f"    Description: {desc}")
        print()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Block Generator Engine")
    parser.add_argument('--version', action='version', version='1.0.0')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    generate_parser = subparsers.add_parser('generate', help='Generate a single block')
    generate_parser.add_argument('--block-id', required=True, help='Block ID (e.g., B01)')
    generate_parser.add_argument('--transcript', required=True, help='Path to transcript')
    generate_parser.add_argument('--meeting-id', required=True, help='Meeting ID')
    generate_parser.add_argument('--output-dir', help='Output directory')
    generate_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    generate_all_parser = subparsers.add_parser('generate-all', help='Generate all blocks')
    generate_all_parser.add_argument('--transcript', required=True, help='Path to transcript')
    generate_all_parser.add_argument('--meeting-id', required=True, help='Meeting ID')
    generate_all_parser.add_argument('--output-dir', help='Output directory')
    generate_all_parser.add_argument('--category', help='Filter by category')
    generate_all_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    list_parser = subparsers.add_parser('list-blocks', help='List available blocks')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--status', default='active', help='Filter by status')
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    try:
        if args.command == 'generate':
            return cmd_generate(args)
        elif args.command == 'generate-all':
            return cmd_generate_all(args)
        elif args.command == 'list-blocks':
            return cmd_list_blocks(args)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
