#!/usr/bin/env python3
"""
Conversation Parser Module for N5 Command Authoring System

Parses natural language input into structured segments for command generation.
"""

import re
from typing import List, Dict, Any
from datetime import datetime

def parse_conversation(input_text: str) -> List[Dict[str, Any]]:
    """
    Parse conversation text into structured segments.

    Args:
        input_text: Raw conversation or instruction text

    Returns:
        List of parsed segments with type, content, and timestamp
    """
    if not input_text or not input_text.strip():
        return []

    segments = []

    # Split into lines and process
    lines = input_text.strip().split('\n')
    current_segment = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect segment type based on patterns
        if re.match(r'^(create|make|build|implement)', line.lower()):
            # Start new task segment
            if current_segment:
                segments.append(current_segment)
            current_segment = {
                'type': 'task',
                'content': line,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        elif current_segment:
            # Continue current segment
            current_segment['content'] += ' ' + line
        else:
            # Start default segment
            current_segment = {
                'type': 'instruction',
                'content': line,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    # Add final segment
    if current_segment:
        segments.append(current_segment)

    return segments

def validate_segments(segments: List[Dict[str, Any]]) -> bool:
    """
    Validate parsed segments for required structure.

    Args:
        segments: Parsed segments to validate

    Returns:
        True if valid, False otherwise
    """
    if not segments:
        return False

    required_keys = ['type', 'content', 'timestamp']

    for segment in segments:
        if not isinstance(segment, dict):
            return False

        for key in required_keys:
            if key not in segment:
                return False

        if not segment['content'].strip():
            return False

    return True