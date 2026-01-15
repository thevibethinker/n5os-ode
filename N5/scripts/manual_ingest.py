#!/usr/bin/env python3
"""
Manual Transcript Ingest CLI

Usage:
    python3 manual_ingest.py --file /path/to/transcript.txt
    python3 manual_ingest.py --text "Speaker: Hello..."
    python3 manual_ingest.py --file transcript.md --title "Weekly Sync" --date 2025-12-20
    
This script uses the Unified Intake Engine to process transcripts
from any source into the canonical N5 meeting folder structure.
"""

import argparse
import sys
import json
from pathlib import Path

# Add N5 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.intake.intake_engine import IntakeEngine
from services.intake.models import IntakeSource


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a transcript into the N5 meeting system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From a file
  python3 manual_ingest.py --file ~/Downloads/transcript.txt
  
  # With metadata
  python3 manual_ingest.py --file transcript.md --title "Team Sync" --date 2025-12-20
  
  # Direct text input
  python3 manual_ingest.py --text "John: Hello\nJane: Hi there"
  
  # From structured JSON (AI-parsed)
  python3 manual_ingest.py --json-input '{\"text\": \"...\", \"utterances\": [...]}'
  
  # Force re-ingest (skip dedup)
  python3 manual_ingest.py --file transcript.txt --force
        """
    )
    
    # Input source (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--file", "-f",
        type=str,
        help="Path to transcript file (txt, md, or json)"
    )
    input_group.add_argument(
        "--text", "-t",
        type=str,
        help="Direct transcript text"
    )
    input_group.add_argument(
        "--json-input",
        type=str,
        help="Structured JSON transcript (AI-parsed)"
    )
    
    # Optional metadata
    parser.add_argument(
        "--title",
        type=str,
        help="Meeting title (will be extracted from transcript if not provided)"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Meeting date (YYYY-MM-DD). If not provided: semantic detection → calendar → today"
    )
    parser.add_argument(
        "--participants",
        type=str,
        nargs="+",
        help="Participant names (will be extracted from transcript if not provided)"
    )
    
    # Options
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip deduplication check"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without creating files"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    # Get transcript content
    if args.json_input:
        try:
            transcript_data = json.loads(args.json_input)
            transcript_text = transcript_data.get("text", "")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        file_path = Path(args.file).expanduser()
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        transcript_text = file_path.read_text()
        
        # If JSON file, try to parse it
        if file_path.suffix == ".json":
            try:
                data = json.loads(transcript_text)
                # Extract text from common JSON formats
                if isinstance(data, dict):
                    transcript_text = data.get("transcript") or data.get("text") or json.dumps(data)
            except json.JSONDecodeError:
                pass  # Treat as plain text
    else:
        transcript_text = args.text
    
    # Dry run - just show analysis
    if args.dry_run:
        print("=== Dry Run Analysis ===\n")
        print(f"Input length: {len(transcript_text)} characters")
        print(f"Line count: {len(transcript_text.splitlines())}")
        
        # Quick analysis
        from services.intake.adapters.manual_adapter import ManualAdapter
        adapter = ManualAdapter()
        transcript = adapter.adapt({"transcript": transcript_text, "title": args.title, "date": args.date})
        
        print(f"\nExtracted:")
        print(f"  Title: {transcript.title or '(none - will use participant names)'}")
        print(f"  Date: {transcript.detected_date or '(none - will check calendar or use today)'}")
        print(f"  Participants: {', '.join(transcript.participants) if transcript.participants else '(none detected)'}")
        print(f"  Utterances: {len(transcript.utterances)}")
        
        if args.date:
            print(f"\nExplicit date override: {args.date}")
        if args.title:
            print(f"Explicit title override: {args.title}")
        
        print("\n[Dry run - no files created]")
        sys.exit(0)
    
    # Initialize engine and ingest
    engine = IntakeEngine()
    
    if args.json_input:
        # Structured input bypasses most adapter logic
        result = engine.ingest_json(
            transcript_data=json.loads(args.json_input),
            title=args.title,
            date_str=args.date,
            force=args.force,
        )
    else:
        result = engine.ingest_manual(
            transcript_text=transcript_text,
            title=args.title,
            date_str=args.date,
            participants=args.participants,
            force=args.force,
        )
    
    # Output result
    if args.json:
        output = {
            "success": result.success,
            "folder_path": result.folder_path,
            "meeting_date": result.folder_name,
            "error": result.error_message,
            "duplicate_of": result.duplicate_of,
            "validation_errors": [str(v) for v in result.validation_results],
        }
        print(json.dumps(output, indent=2))
    else:
        if result.success:
            print(f"✓ Successfully ingested transcript")
            print(f"  Folder: {result.folder_path}")
            print(f"  Date: {result.folder_name}")
            if result.validation_results:
                print(f"  Warnings: {', '.join(str(v) for v in result.validation_results)}")
        else:
            print(f"✗ Failed to ingest transcript", file=sys.stderr)
            print(f"  Error: {result.error_message}", file=sys.stderr)
            if result.duplicate_of:
                print(f"  Duplicate of: {result.duplicate_of}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()




