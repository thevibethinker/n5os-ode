#!/usr/bin/env python3
"""
Semantic filename normalization for meeting transcripts.

Don't use regex gymnastics - just understand what makes a meeting filename unique.
A meeting's canonical filename is: <title>-transcript-<YYYY-MM-DDTHH-MM-SS>.transcript.md

All the weird variations (dots vs dashes in milliseconds, underscores vs dashes, etc)
get normalized to the same canonical form.
"""

def normalize_meeting_filename(original: str) -> str:
    """
    Convert any meeting transcript filename variant to canonical form.
    
    Examples:
        Acquisition_War_Room-transcript-2025-11-03T19-48-05.399Z.transcript.md
        Acquisition_War_Room-transcript-2025-11-03T19-48-05_399Z.transcript.md  
        Acquisition_War_Room-transcript-2025-11-03T19-48-05-399Z.transcript.md
        Acquisition_War_Room_2025-11-03T19-48-05.transcript.md
        
    All become:
        Acquisition_War_Room-transcript-2025-11-03T19-48-05.transcript.md
    """
    # Remove any .transcript.md extension variants
    name = original.replace('.transcript.md', '').replace('.md', '')
    
    # Find the year (2025 or any 20XX)
    if '2025-' not in name and '2024-' not in name and '2026-' not in name:
        # No recognizable timestamp, return as-is with suffix
        return name + '.transcript.md'
    
    # Split on the year
    parts = []
    for year_marker in ['2025-', '2024-', '2026-', '2027-']:
        if year_marker in name:
            parts = name.split(year_marker)
            year = year_marker.rstrip('-')
            break
    
    if len(parts) < 2:
        return name + '.transcript.md'
    
    # Title is everything before the year, strip trailing separators
    title = parts[0].rstrip('-_. ')
    
    # Timestamp is everything after the year marker
    timestamp_raw = year + '-' + parts[1]
    
    # Keep only YYYY-MM-DDTHH-MM-SS (19 chars starting from the year)
    # This strips milliseconds, Z, and all weird variations
    timestamp_normalized = timestamp_raw[:19]  
    
    # Ensure we have -transcript- connecting them
    if '-transcript-' not in title:
        if title.endswith('-transcript'):
            pass  # Already have it
        else:
            title = title + '-transcript'
    
    return f"{title}-{timestamp_normalized}.transcript.md"


def get_meeting_id(filename: str) -> str:
    """
    Extract meeting_id from filename.
    
    meeting_id is the canonical filename without .transcript.md suffix.
    This is what we use for deduplication.
    """
    canonical = normalize_meeting_filename(filename)
    return canonical.replace('.transcript.md', '')


if __name__ == '__main__':
    # Test cases
    test_cases = [
        "Acquisition_War_Room-transcript-2025-11-03T19-48-05.399Z.transcript.md",
        "Acquisition_War_Room-transcript-2025-11-03T19-48-05_399Z.transcript.md",
        "Acquisition_War_Room-transcript-2025-11-03T19-48-05-399Z.transcript.md",
        "Acquisition_War_Room_2025-11-03T19-48-05.transcript.md",
        "Daily_team_stand-up-transcript-2025-10-29T14-38-58.996Z.transcript.md",
        "Daily_team_stand-up-transcript-2025-10-29T14-38-58-996Z.transcript.md",
    ]
    
    for tc in test_cases:
        normalized = normalize_meeting_filename(tc)
        meeting_id = get_meeting_id(tc)
        print(f"{tc}")
        print(f"  → {normalized}")
        print(f"  ID: {meeting_id}")
        print()
