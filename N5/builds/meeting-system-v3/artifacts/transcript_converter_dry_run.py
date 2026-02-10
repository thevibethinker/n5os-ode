#!/usr/bin/env python3
"""
Simple JSONL to Markdown Transcript Converter (DRY-RUN ONLY)
Build: meeting-system-v3, Drop: D5.2

Shows what would happen during JSONL transcript conversion.
CRITICAL: This script only previews changes, never modifies files.
"""

import json
import sys
from pathlib import Path


def convert_jsonl_to_markdown_preview(jsonl_path):
    """Preview JSONL to markdown conversion without writing files."""
    
    md_lines = []
    total_entries = 0
    speakers = set()
    
    try:
        with open(jsonl_path, 'r') as f:
            for line in f:
                if line.strip():
                    total_entries += 1
                    try:
                        entry = json.loads(line.strip())
                        
                        # Extract speaker and text
                        speaker = entry.get('speaker', 'Unknown')
                        text = entry.get('text', '').strip()
                        timestamp = entry.get('timestamp', '')
                        
                        speakers.add(speaker)
                        
                        # Format as markdown
                        if timestamp:
                            md_lines.append(f"**{speaker}** ({timestamp}): {text}")
                        else:
                            md_lines.append(f"**{speaker}**: {text}")
                            
                    except json.JSONDecodeError:
                        md_lines.append(f"[Invalid JSON entry at line {total_entries}]")
                        
    except FileNotFoundError:
        return None, f"File not found: {jsonl_path}"
    
    # Join all lines
    markdown_content = "\n\n".join(md_lines)
    
    stats = {
        "total_entries": total_entries,
        "unique_speakers": len(speakers),
        "speakers_list": list(speakers),
        "output_length_chars": len(markdown_content),
        "output_lines": len(md_lines),
        "preview_first_200_chars": markdown_content[:200] + "..." if len(markdown_content) > 200 else markdown_content
    }
    
    return markdown_content, stats


def main():
    """Test conversion on the known JSONL transcript."""
    
    test_jsonl = Path("/home/workspace/Personal/Meetings/Inbox/2026-01-26_Collateral-Blitz_Logan/transcript.jsonl")
    
    print("=" * 60)
    print("🔄 JSONL to Markdown Conversion Preview")
    print("=" * 60)
    print(f"Test File: {test_jsonl}")
    print()
    
    if not test_jsonl.exists():
        print(f"❌ Test file not found: {test_jsonl}")
        return 1
    
    # Get file size
    file_size_kb = test_jsonl.stat().st_size / 1024
    
    print(f"📄 Input File: {test_jsonl.name}")
    print(f"📏 File Size: {file_size_kb:.1f} KB")
    print()
    
    # Preview conversion
    print("🔄 Running conversion preview...")
    markdown_content, stats = convert_jsonl_to_markdown_preview(test_jsonl)
    
    if isinstance(stats, str):  # Error case
        print(f"❌ Error: {stats}")
        return 1
    
    print("✅ Conversion preview successful!")
    print()
    
    print("📊 Conversion Statistics:")
    print(f"  • JSONL entries: {stats['total_entries']}")
    print(f"  • Unique speakers: {stats['unique_speakers']}")
    print(f"  • Speakers: {', '.join(stats['speakers_list'])}")
    print(f"  • Output length: {stats['output_length_chars']:,} characters")
    print(f"  • Output lines: {stats['output_lines']}")
    print(f"  • Estimated MD size: {stats['output_length_chars'] / 1024:.1f} KB")
    print()
    
    print("📖 Preview (first 200 chars):")
    print("-" * 40)
    print(stats['preview_first_200_chars'])
    print("-" * 40)
    print()
    
    print("✅ DRY-RUN COMPLETE - NO FILES MODIFIED")
    print("📝 This would create transcript.md alongside transcript.jsonl")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())