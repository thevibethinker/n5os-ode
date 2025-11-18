#!/usr/bin/env python3
"""
Meeting Manifest Manager

Handles CRUD operations for meeting manifest.json files.
Updates block status, tracks generation progress, and maintains manifest integrity.
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def load_manifest(meeting_folder: Path) -> Dict[str, Any]:
    """Load manifest.json from meeting folder."""
    manifest_path = meeting_folder / "manifest.json"

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    try:
        with open(manifest_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest: {manifest_path}") from e


def save_manifest(meeting_folder: Path, manifest: Dict[str, Any]) -> None:
    """Save manifest.json to meeting folder."""
    manifest_path = meeting_folder / "manifest.json"

    # Backup existing manifest
    if manifest_path.exists():
        backup_path = meeting_folder / f"manifest.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        manifest_path.rename(backup_path)
        print(f"Backed up existing manifest to: {backup_path}")

    # Write new manifest
    try:
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"Updated manifest: {manifest_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to save manifest: {e}")


def update_block_status(
    manifest: Dict[str, Any],
    block_id: str,
    status: str,
    file_path: Optional[str] = None,
    word_count: Optional[int] = None
) -> Dict[str, Any]:
    """Update status and metadata for a specific block in the manifest."""

    if 'blocks' not in manifest:
        raise ValueError("Manifest missing 'blocks' array")

    block_found = False
    for block in manifest['blocks']:
        if block.get('block_id') == block_id:
            block_found = True

            # Update status
            old_status = block.get('status')
            block['status'] = status

            # Add timestamp
            block['updated_at'] = datetime.now().isoformat()

            # If completing the block, add completion timestamp
            if status == 'generated' and old_status != 'generated':
                block['generated_at'] = datetime.now().isoformat()

            # Update file path if provided
            if file_path:
                block['file_path'] = file_path

            # Update word count if provided
            if word_count is not None:
                block['word_count'] = word_count

            print(f"Updated block {block_id}: {old_status} → {status}")
            break

    if not block_found:
        raise ValueError(f"Block ID '{block_id}' not found in manifest")

    return manifest


def get_pending_blocks(manifest: Dict[str, Any]) -> list:
    """Get list of pending blocks from manifest."""
    if 'blocks' not in manifest:
        return []

    return [block for block in manifest['blocks'] if block.get('status') == 'pending']


def get_completed_blocks(manifest: Dict[str, Any]) -> list:
    """Get list of completed/generated blocks from manifest."""
    if 'blocks' not in manifest:
        return []

    return [block for block in manifest['blocks'] if block.get('status') in ['generated', 'complete']]


def get_next_pending_blocks(manifest: Dict[str, Any], batch_size: int = 3) -> list:
    """Get the next batch of pending blocks sorted by priority."""
    pending = get_pending_blocks(manifest)

    # Sort by priority (lower number = higher priority)
    pending_sorted = sorted(pending, key=lambda b: b.get('priority', 999))

    return pending_sorted[:batch_size]


def validate_manifest(manifest: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate manifest structure and return (is_valid, errors)."""
    errors = []

    required_fields = ['meeting_id', 'blocks']
    for field in required_fields:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    if 'blocks' in manifest:
        if not isinstance(manifest['blocks'], list):
            errors.append("'blocks' must be an array")
        else:
            for i, block in enumerate(manifest['blocks']):
                if 'block_id' not in block:
                    errors.append(f"Block {i} missing 'block_id'")
                if 'block_name' not in block:
                    errors.append(f"Block {i} missing 'block_name'")
                if 'status' not in block:
                    errors.append(f"Block {i} missing 'status'")

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description='Meeting Manifest Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update block status')
    update_parser.add_argument('--meeting-folder', required=True, help='Path to meeting folder')
    update_parser.add_argument('--block-id', required=True, help='Block ID to update')
    update_parser.add_argument('--status', required=True, choices=['pending', 'generating', 'generated', 'error'],
                               help='New status')
    update_parser.add_argument('--file-path', help='Path to generated block file (relative to meeting folder)')
    update_parser.add_argument('--word-count', type=int, help='Word count of generated content')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query manifest information')
    query_parser.add_argument('--meeting-folder', required=True, help='Path to meeting folder')
    query_parser.add_argument('--query', required=True,
                              choices=['pending-count', 'completed-count', 'next-batch', 'validation'],
                              help='What to query')
    query_parser.add_argument('--batch-size', type=int, default=3, help='Batch size for next-batch query')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        meeting_folder = Path(args.meeting_folder)
        if not meeting_folder.exists():
            print(f"Error: Meeting folder does not exist: {meeting_folder}", file=sys.stderr)
            sys.exit(1)

        if args.command == 'update':
            # Load manifest
            manifest = load_manifest(meeting_folder)

            # Update block
            updated_manifest = update_block_status(
                manifest,
                args.block_id,
                args.status,
                args.file_path,
                args.word_count
            )

            # Save manifest
            save_manifest(meeting_folder, updated_manifest)

        elif args.command == 'query':
            # Load manifest
            manifest = load_manifest(meeting_folder)

            # Validate first
            is_valid, errors = validate_manifest(manifest)
            if not is_valid:
                print(f"Manifest validation errors: {errors}", file=sys.stderr)
                sys.exit(1)

            if args.query == 'pending-count':
                pending = get_pending_blocks(manifest)
                print(len(pending))

            elif args.query == 'completed-count':
                completed = get_completed_blocks(manifest)
                print(len(completed))

            elif args.query == 'next-batch':
                next_blocks = get_next_pending_blocks(manifest, args.batch_size)
                # Output as JSON for programmatic use
                output = []
                for block in next_blocks:
                    output.append({
                        'block_id': block['block_id'],
                        'block_name': block['block_name'],
                        'priority': block.get('priority'),
                        'reason': block.get('reason', '')
                    })
                print(json.dumps(output))

            elif args.query == 'validation':
                is_valid, errors = validate_manifest(manifest)
                if is_valid:
                    print("valid")
                else:
                    print("invalid")
                    for error in errors:
                        print(f"Error: {error}", file=sys.stderr)
                    sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

