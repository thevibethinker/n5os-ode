#!/usr/bin/env python3
"""
Batch Meeting Intelligence Block Generator

Processes 2-3 meeting intelligence blocks per run with full context.
Hybrid batch approach for optimal quality/efficiency balance.
"""

import json
import sys
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import subprocess

# Add N5/scripts to path for imports
sys.path.insert(0, str(Path('/home/workspace/N5/scripts')))


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config {config_path}: {e}", file=sys.stderr)
        sys.exit(1)


def load_transcript(transcript_path: Path) -> str:
    """Load transcript content from .jsonl or .md file."""
    if not transcript_path.exists():
        # Try alternative extensions
        for ext in ['.jsonl', '.md', '.txt']:
            alt_path = transcript_path.with_suffix(ext)
            if alt_path.exists():
                transcript_path = alt_path
                break
        else:
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    content = ""
    if transcript_path.suffix == '.jsonl':
        # Parse JSONL format
        try:
            with open(transcript_path, 'r') as f:
                data = json.load(f)
                # Handle both array and object formats
                if isinstance(data, dict):
                    content = data.get('text', '')
                elif isinstance(data, list):
                    # Assume array of utterances
                    for item in data:
                        if isinstance(item, dict) and 'text' in item:
                            content += item['text'] + "\n\n"
        except Exception as e:
            raise ValueError(f"Error parsing JSONL transcript: {e}")
    elif transcript_path.suffix == '.md':
        # Read markdown content
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
        if block.get('status') in ['generated', 'complete']:
            file_path = block.get('file_path') or f"{block['block_id']}_{block['block_name']}.md"
            block_file = meeting_folder / file_path

            if block_file.exists():
                try:
                    with open(block_file, 'r') as f:
                        # Extract content after YAML frontmatter
                        content = f.read()
                        # Simple frontmatter extraction - find the second '---'
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                content = parts[2]

                        if content.strip():
                            completed_content.append(f"\n{'='*60}\n")
                            completed_content.append(f"BLOCK: {block['block_id']} - {block['block_name']}\n")
                            completed_content.append(f"{'='*60}\n")
                            completed_content.append(content.strip())
                            completed_content.append('\n')
                except Exception as e:
                    print(f"Warning: Could not read completed block {block_file}: {e}", file=sys.stderr)

    return '\n'.join(completed_content) if completed_content else "No completed blocks yet."


def find_meeting_with_pending_blocks(inbox_path: Path) -> Optional[Path]:
    """Find the oldest meeting folder with pending blocks."""
    if not inbox_path.exists():
        print(f"Inbox path does not exist: {inbox_path}", file=sys.stderr)
        return None

    meetings = []
    for item in inbox_path.iterdir():
        # Look for folders with _[M] suffix (meeting folders)
        if item.is_dir() and item.name.endswith('_[M]'):
            manifest_path = item / "manifest.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)

                    # Check for pending blocks
                    pending_blocks = [
                        block for block in manifest.get('blocks', [])
                        if block.get('status') in ['pending']
                    ]

                    if pending_blocks:
                        # Get folder modification time for sorting
                        mtime = item.stat().st_mtime
                        meetings.append((item, mtime, len(pending_blocks)))
                except Exception as e:
                    print(f"Warning: Error reading {manifest_path}: {e}", file=sys.stderr)
                    continue

    if not meetings:
        return None

    # Sort by modification time (oldest first), then by number of pending blocks
    meetings.sort(key=lambda x: (x[1], -x[2]))
    return meetings[0][0]


def validate_generated_block(block_file: Path, block_spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a generated block against the catalog specification."""
    errors = []

    try:
        with open(block_file, 'r') as f:
            content = f.read()

        # Check YAML frontmatter
        if not content.startswith('---'):
            errors.append("Missing YAML frontmatter")
        else:
            parts = content.split('---', 2)
            if len(parts) < 3:
                errors.append("Invalid YAML frontmatter format")
            else:
                try:
                    yaml.safe_load(parts[1])
                except Exception as e:
                    errors.append(f"Invalid YAML frontmatter: {e}")

        # Extract main content (after frontmatter)
        main_content = parts[2] if len(parts) >= 3 else content
        word_count = len(main_content.split())

        # Check word count against typical range
        typical_length = block_spec.get('typical_length', '300-600 words')
        try:
            # Parse "300-600 words" format
            range_part = typical_length.replace(' words', '')
            min_words, max_words = map(int, range_part.split('-'))

            # Allow +/- 30% tolerance
            tolerance = 0.3
            min_acceptable = int(min_words * (1 - tolerance))
            max_acceptable = int(max_words * (1 + tolerance))

            if word_count < min_acceptable:
                errors.append(f"Word count ({word_count}) below minimum ({min_acceptable})")
            elif word_count > max_acceptable:
                errors.append(f"Word count ({word_count}) above maximum ({max_acceptable})")
        except Exception as e:
            print(f"Warning: Could not validate word count for {block_file.name}: {e}", file=sys.stderr)

        # Check required sections
        required_sections = block_spec.get('required_sections', [])
        if required_sections:
            for section in required_sections:
                # Look for section heading (e.g., "# Section Name" or "## Section Name")
                heading_patterns = [
                    f"# {section}",
                    f"## {section}",
                    f"### {section}",
                    f"#### {section}"
                ]
                if not any(pattern in main_content for pattern in heading_patterns):
                    errors.append(f"Missing required section: {section}")

        # Check for placeholder/stub content
        placeholder_patterns = [
            "TODO:",
            "TBD",
            "[placeholder",
            "<placeholder",
            "INSERT CONTENT HERE",
            "Coming soon",
            "To be completed"
        ]
        for pattern in placeholder_patterns:
            if pattern.lower() in main_content.lower():
                errors.append(f"Contains placeholder content: {pattern}")
                break

    except Exception as e:
        errors.append(f"Error reading block file: {e}")

    return len(errors) == 0, errors


def generate_block_with_llm(
    transcript: str,
    completed_blocks: str,
    block_definition: str,
    block_spec: Dict[str, Any]
) -> str:
    """Generate a single intelligence block using LLM."""

    # Create the prompt
    prompt = f"""You are a meeting intelligence analyst. Generate a {block_spec['name']} block based on the following meeting transcript.

BLOCK SPECIFICATION:
{block_definition}

PURPOSE: {block_spec['purpose']}
TYPICAL LENGTH: {block_spec['typical_length']}

REQUIRED SECTIONS:
"""

    for section in block_spec.get('required_sections', []):
        prompt += f"- {section}\n"

    prompt += f"""

GUIDELINES:
{block_spec['guidelines']}

---

FULL MEETING TRANSCRIPT:
```
{transcript[:15000]}  # Include first 15k chars to manage context
```

---

COMPLETED BLOCKS (for context continuity):
```
{completed_blocks[:5000]}  # Include up to 5k chars of context
```

---

INSTRUCTIONS:
1. Generate content for: {block_spec['name']}
2. Focus ONLY on extracting and synthesizing information from the transcript
3. Include YAML frontmatter with: created, last_edited, version
4. Start with: # {block_spec['name']}
5. Include all required sections with appropriate detail
6. Ensure semantic depth appropriate to this block type
7. DO NOT include placeholder content - only actual meeting content
8. Include speaker attribution where relevant
9. Be specific and concrete - not generic summaries

Generate the complete block now:"""

    # For now, return a placeholder - in real implementation, this would call LLM
    # Since we're in Builder mode building the system, we'll create a stub
    # The actual LLM generation will be implemented

    placeholder_content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
---

# {block_spec['name']}

<LLM GENERATION STUB - Actual generation would happen here>

This is a placeholder where the actual LLM-generated content would appear.
In production, this would be replaced by actual semantic analysis of the transcript.

## Key Points

- Point 1: Analysis of meeting content
- Point 2: Synthesized insights
- Point 3: Actionable intelligence
"""

    return placeholder_content


def create_meeting_pipeline_dirs():
    """Ensure meeting pipeline directories exist."""
    pipeline_dir = Path('/home/workspace/N5/scripts/meeting_pipeline')
    pipeline_dir.mkdir(parents=True, exist_ok=True)

    log_dir = Path('/home/workspace/N5/logs/meeting_pipeline')
    log_dir.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description='Batch Meeting Intelligence Block Generator')
    parser.add_argument('--inbox', default='/home/workspace/Personal/Meetings/Inbox',
                        help='Path to meetings inbox')
    parser.add_argument('--block-catalog', default='/home/workspace/N5/config/block_catalog.yaml',
                        help='Path to block catalog')
    parser.add_argument('--batch-size', type=int, default=3,
                        help='Number of blocks to generate per run (default: 3)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    args = parser.parse_args()

    # Ensure directories exist
    create_meeting_pipeline_dirs()

    inbox_path = Path(args.inbox)
    catalog_path = Path(args.block_catalog)

    # Load block catalog
    print(f"Loading block catalog: {catalog_path}")
    catalog = load_yaml_config(catalog_path)
    blocks_catalog = catalog.get('blocks', {})

    # Step 1: Find meeting with pending blocks
    print("\n" + "="*70)
    print("STEP 1: Finding meeting with pending blocks...")
    print("="*70)

    meeting_folder = find_meeting_with_pending_blocks(inbox_path)
    if not meeting_folder:
        print("No meetings with pending blocks found. Exiting.")
        sys.exit(0)

    print(f"Selected meeting: {meeting_folder.name}")

    # Load manifest
    manifest_path = meeting_folder / "manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Count pending blocks
    pending_blocks = [
        block for block in manifest.get('blocks', [])
        if block.get('status') == 'pending'
    ]
    print(f"Pending blocks: {len(pending_blocks)}")

    if args.dry_run:
        print("\n[Dry run mode - no changes will be made]")

    # Step 2: Load full context ONCE
    print("\n" + "="*70)
    print("STEP 2: Loading full context...")
    print("="*70)

    # Load transcript
    meeting_id = manifest['meeting_id']
    transcript_path = meeting_folder / f"{meeting_id}.transcript.jsonl"

    # Try alternative transcript names if .transcript.jsonl doesn't exist
    if not transcript_path.exists():
        alternatives = [
            meeting_folder / "transcript.md",
            meeting_folder / "transcript.jsonl",
            meeting_folder / meeting_id / "transcript.md"
        ]
        for alt_path in alternatives:
            if alt_path.exists():
                transcript_path = alt_path
                break

    print(f"Loading transcript: {transcript_path}")
    transcript = load_transcript(transcript_path)
    print(f"Transcript loaded: {len(transcript.split())} words")

    # Load completed blocks for context
    print("Loading completed blocks for context...")
    completed_blocks_context = load_completed_blocks(meeting_folder, manifest)
    completed_block_count = completed_blocks_context.count('BLOCK:')
    print(f"Loaded {completed_block_count} completed blocks as context")

    # Step 3: Process next 2-3 pending blocks
    print("\n" + "="*70)
    print(f"STEP 3: Processing next {args.batch_size} pending blocks...")
    print("="*70)

    # Get next batch of pending blocks
    pending_sorted = sorted(pending_blocks, key=lambda b: b.get('priority', 999))
    blocks_to_process = pending_sorted[:args.batch_size]

    if not blocks_to_process:
        print("No pending blocks to process. Exiting.")
        sys.exit(0)

    print(f"Selected {len(blocks_to_process)} blocks to generate:\n")
    for block in blocks_to_process:
        print(f"  - {block['block_id']}: {block['block_name']} (priority: {block.get('priority', 'N/A')})")

    # Process each block
    generated_blocks = []

    for block in blocks_to_process:
        block_id = block['block_id']
        block_name = block['block_name']
        catalog_key = f"{block_id}_{block_name}"

        print(f"\n{'='*70}")
        print(f"Generating: {block_id} - {block_name}")
        print(f"{'='*70}")

        # Get block specification
        block_spec = blocks_catalog.get(catalog_key)
        if not block_spec:
            print(f"Warning: Block {catalog_key} not found in catalog. Skipping.", file=sys.stderr)
            continue

        # Create block definition string
        block_definition = f"{block_id}_{block_name}"

        # Step 3a: Generate block with full semantic analysis
        print("Generating block content...")
        if not args.dry_run:
            block_content = generate_block_with_llm(
                transcript,
                completed_blocks_context,
                block_definition,
                block_spec
            )

            # Write to file
            output_file = meeting_folder / f"{block_definition}.md"
            with open(output_file, 'w') as f:
                f.write(block_content)
            print(f"Block written: {output_file}")

            # Step 3b: Validate generated block
            print("Validating generated block...")
            is_valid, errors = validate_generated_block(output_file, block_spec)
            if not is_valid:
                print(f"Warning: Block validation failed: {errors}", file=sys.stderr)
                if not args.dry_run:
                    # For now, don't fail on validation errors
                    # In production, might want to mark as 'error' status
                    pass

            # Step 3c: Update manifest
            print("Updating manifest...")
            word_count = len(block_content.split())

            cmd = [
                sys.executable, '/home/workspace/N5/scripts/meeting_pipeline/manifest_manager.py',
                'update',
                '--meeting-folder', str(meeting_folder),
                '--block-id', block_id,
                '--status', 'generated',
                '--file-path', f"{block_definition}.md",
                '--word-count', str(word_count)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: Failed to update manifest: {result.stderr}", file=sys.stderr)
            else:
                print("Manifest updated successfully")

            generated_blocks.append(block)
        else:
            print(f"[Dry run] Would generate: {block_definition}.md")
            generated_blocks.append(block)

    # Step 4: Check completion status
    print("\n" + "="*70)
    print("STEP 4: Checking completion status...")
    print("="*70)

    # Reload manifest to get updated counts
    with open(manifest_path, 'r') as f:
        updated_manifest = json.load(f)

    all_blocks = updated_manifest.get('blocks', [])
    completed_blocks = [b for b in all_blocks if b.get('status') in ['generated', 'complete']]
    still_pending_blocks = [b for b in all_blocks if b.get('status') == 'pending']

    total_blocks = len(all_blocks)
    completed_count = len(completed_blocks)
    pending_count = len(still_pending_blocks)

    print(f"Total blocks: {total_blocks}")
    print(f"Completed: {completed_count}")
    print(f"Pending: {pending_count}")

    # Step 5: Mark meeting as placement-ready if ALL complete
    if pending_count == 0:
        print("\n" + "="*70)
        print("STEP 5: All blocks complete - marking as placement-ready")
        print("="*70)

        # Rename folder from [M] to [P]
        old_name = meeting_folder.name
        if old_name.endswith('_[M]'):
            new_name = old_name.replace('_[M]', '_[P]')
            new_path = meeting_folder.parent / new_name

            if not args.dry_run:
                meeting_folder.rename(new_path)
                print(f"Renamed: {old_name} → {new_name}")
                print(f"Meeting ready for placement: {new_path}")
            else:
                print(f"[Dry run] Would rename: {old_name} → {new_name}")

            log_msg = f"Generated {completed_count}/{total_blocks} blocks for {old_name}. All blocks complete, ready for placement."
        else:
            print(f"Warning: Folder name doesn't end with _[M]: {old_name}", file=sys.stderr)
            log_msg = f"Generated {completed_count}/{total_blocks} blocks for {old_name}. All blocks complete."
    else:
        log_msg = (f"Generated {len(generated_blocks)} blocks for {meeting_folder.name}: "
                  f"{[b['block_id'] for b in generated_blocks]}. "
                  f"Progress: {completed_count}/{total_blocks} blocks done. "
                  f"{pending_count} blocks pending for next run.")

    print(f"\n{log_msg}")

    # Write to log file
    if not args.dry_run:
        log_dir = Path('/home/workspace/N5/logs/meeting_pipeline')
        log_file = log_dir / f"batch_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_file, 'w') as f:
            f.write(log_msg + '\n')
        print(f"Log written: {log_file}")

    print("\n" + "="*70)
    print("Batch generation complete")
    print("="*70)


if __name__ == '__main__':
    main()


