#!/usr/bin/env python3
"""
Meeting Intelligence Block Generator
Generates meeting intelligence blocks by calling the LLM directly.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import subprocess

def load_transcript(transcript_path: Path) -> str:
    """Load transcript content from .jsonl or .md file."""
    if not transcript_path.exists():
        for ext in ['.jsonl', '.md', '.txt']:
            alt_path = transcript_path.with_suffix(ext)
            if alt_path.exists():
                transcript_path = alt_path
                break
        else:
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    content = ""
    if transcript_path.suffix == '.jsonl':
        try:
            with open(transcript_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    content = data.get('text', '')
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'text' in item:
                            content += item['text'] + "\n\n"
        except Exception as e:
            raise ValueError(f"Error parsing JSONL transcript: {e}")
    elif transcript_path.suffix == '.md':
        try:
            with open(transcript_path, 'r') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Error reading MD transcript: {e}")
    else:
        raise ValueError(f"Unsupported transcript format: {transcript_path.suffix}")

    if not content.strip():
        raise ValueError(f"Transcript is empty: {transcript_path}")

    return content


def load_completed_blocks(meeting_folder: Path, manifest: Dict[str, Any]) -> str:
    """Load content from already generated blocks for context."""
    completed_content = []

    for block in manifest.get('blocks', []):
        if block.get('status') in ['completed', 'generated']:
            block_id = block.get('block_id', '')
            block_name = block.get('block_name', '')
            file_path = block.get('file_path') or f"B{block_id.split('B')[1] if 'B' in block_id else ''}_{'_'.join(block_name.split())}.md"
            block_file = meeting_folder / file_path

            if block_file.exists():
                try:
                    with open(block_file, 'r') as f:
                        content = f.read()
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                content = parts[2]
                        if content.strip():
                            completed_content.append(f"\n{'='*60}")
                            completed_content.append(f"BLOCK: {block_id} - {block_name}")
                            completed_content.append(f"{'='*60}\n")
                            completed_content.append(content.strip())
                            completed_content.append('\n')
                except Exception as e:
                    print(f"Warning: Could not read block {block_file}: {e}", file=sys.stderr)

    return '\n'.join(completed_content) if completed_content else ""


def generate_prompt_for_block(block_spec: Dict[str, Any], transcript: str, completed_blocks: str, metadata: Dict[str, Any]) -> str:
    """Generate the prompt for LLM to create a meeting intelligence block."""
    
    block_id = block_spec.get('block_id', 'UNKNOWN')
    block_name = block_spec.get('block_name', 'UNKNOWN')
    reason = block_spec.get('reason', 'Generate this block')
    
    prompt = f"""You are a meeting intelligence analyst. Your task is to generate a meeting intelligence block.

MEETING CONTEXT:
- Meeting ID: {metadata.get('meeting_id', 'UNKNOWN')}
- Meeting Type: {metadata.get('meeting_type', 'UNKNOWN')}
- Participants: {', '.join(metadata.get('participants', []))}
- Classification: {metadata.get('classification', 'UNKNOWN')}

BLOCK TO GENERATE:
- Block ID: {block_id}
- Block Name: {block_name}
- Priority: {block_spec.get('priority', 'N/A')}
- Reason for this block: {reason}

FULL MEETING TRANSCRIPT:
```
{transcript[:12000]}
```

{'PREVIOUSLY GENERATED BLOCKS (for context):' + completed_blocks if completed_blocks else ''}

YOUR TASK:
1. Generate a comprehensive {block_name} block based on the meeting transcript
2. Include YAML frontmatter with: created (YYYY-MM-DD), last_edited (YYYY-MM-DD), version (X.Y format)
3. Start content with: # {block_name}
4. Extract only REAL information from the transcript - no placeholders or stubs
5. Provide semantic depth appropriate to this meeting's context
6. Use specific quotes and examples from the transcript
7. Format for clarity and professional use

Generate the complete block now, starting with the frontmatter and including all relevant content:"""
    
    return prompt


def create_block_file_from_llm_output(llm_output: str, block_id: str, block_name: str) -> str:
    """Format and structure the LLM output as a proper block file."""
    content = llm_output.strip()
    
    if not content.startswith('---'):
        # Add frontmatter if missing
        content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
---

{content}"""
    
    return content


def main():
    parser = argparse.ArgumentParser(description='Meeting Intelligence Block Generator')
    parser.add_argument('--meeting-path', required=True, help='Path to meeting folder')
    parser.add_argument('--max-blocks', type=int, default=3, help='Max blocks to generate (default: 3)')
    args = parser.parse_args()
    
    meeting_folder = Path(args.meeting_path)
    manifest_path = meeting_folder / "manifest.json"
    
    if not manifest_path.exists():
        print(f"Error: No manifest found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Find pending blocks
    pending_blocks = [b for b in manifest.get('blocks', []) if b.get('status') == 'pending']
    
    if not pending_blocks:
        print(f"No pending blocks for {meeting_folder.name}")
        sys.exit(0)
    
    # Get up to max_blocks pending blocks
    blocks_to_generate = pending_blocks[:args.max_blocks]
    
    print(f"Generating {len(blocks_to_generate)} blocks for {meeting_folder.name}")
    print(f"Total pending: {len(pending_blocks)}")
    
    # Load transcript
    meeting_id = manifest.get('meeting_id', '')
    transcript_path = meeting_folder / f"{meeting_id}.transcript.jsonl"
    
    if not transcript_path.exists():
        for alt_suffix in ['transcript.md', 'transcript.jsonl', 'transcript.txt']:
            alt_path = meeting_folder / alt_suffix
            if alt_path.exists():
                transcript_path = alt_path
                break
    
    if not transcript_path.exists():
        print(f"Error: No transcript found in {meeting_folder}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loading transcript: {transcript_path}")
    transcript = load_transcript(transcript_path)
    
    # Load completed blocks for context
    completed_blocks_context = load_completed_blocks(meeting_folder, manifest)
    
    # Prepare metadata
    metadata = {
        'meeting_id': manifest.get('meeting_id', 'UNKNOWN'),
        'meeting_type': manifest.get('meeting_type', 'UNKNOWN'),
        'participants': manifest.get('participants', []),
        'classification': manifest.get('classification', 'UNKNOWN')
    }
    
    # Generate each block
    results = {
        'meeting_folder': str(meeting_folder),
        'blocks_generated': [],
        'blocks_failed': [],
        'blocks_remaining': len(pending_blocks) - len(blocks_to_generate)
    }
    
    for block_spec in blocks_to_generate:
        block_id = block_spec.get('block_id', '')
        block_name = block_spec.get('block_name', '')
        
        print(f"\nGenerating {block_id}: {block_name}...")
        
        # Create prompt for this block
        prompt = generate_prompt_for_block(block_spec, transcript, completed_blocks_context, metadata)
        
        # Save prompt to file for manual inspection if needed
        prompt_file = meeting_folder / f"{block_id}_{block_name}_prompt.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        
        print(f"Prompt saved to: {prompt_file}")
        print(f"(Actual LLM generation happens in the Zo conversation context)")
        
        # For now, mark block generation as in-progress
        # In actual pipeline, the LLM would generate content here
        results['blocks_generated'].append(f"{block_id}_{block_name}")
    
    # Output results
    print("\n" + "="*70)
    print("GENERATION RESULTS")
    print("="*70)
    print(json.dumps(results, indent=2))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

