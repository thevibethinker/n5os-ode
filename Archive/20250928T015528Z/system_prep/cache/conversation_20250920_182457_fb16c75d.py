import logging
import time
import re
from datetime import datetime
from typing import List, Dict, Any


def parse_conversation(raw_text: str) -> List[Dict[str, Any]]:
    """
    Parse user input (e.g., pasted text or conversation) into structured segments.
    
    Args:
        raw_text: Raw text string from user input
        
    Returns:
        List of parsed segments (dicts with keys like 'type', 'content', 'timestamp')
    """
    start_time = time.time()
    
    if not raw_text or not isinstance(raw_text, str):
        logging.warning("Empty or invalid input provided to conversation parser")
        return []
    
    segments = []
    
    # Clean the input text
    cleaned_text = raw_text.strip()
    
    # Split into lines for processing
    lines = cleaned_text.split('\n')
    
    current_segment = {
        'type': 'unknown',
        'content': '',
        'timestamp': datetime.now().isoformat(),
        'line_start': 0,
        'line_end': 0
    }
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:
            continue
            
        # Detect command patterns
        if _is_command_line(line):
            if current_segment['content']:
                current_segment['line_end'] = i - 1
                segments.append(current_segment.copy())
                
            current_segment = {
                'type': 'command',
                'content': line,
                'timestamp': datetime.now().isoformat(),
                'line_start': i,
                'line_end': i
            }
            segments.append(current_segment.copy())
            
            current_segment = {
                'type': 'unknown',
                'content': '',
                'timestamp': datetime.now().isoformat(),
                'line_start': i + 1,
                'line_end': i + 1
            }
            
        # Detect task/instruction patterns
        elif _is_task_line(line):
            if current_segment['content']:
                current_segment['line_end'] = i - 1
                segments.append(current_segment.copy())
                
            current_segment = {
                'type': 'task',
                'content': line,
                'timestamp': datetime.now().isoformat(),
                'line_start': i,
                'line_end': i
            }
            
        # Detect context patterns
        elif _is_context_line(line):
            if current_segment['type'] != 'context':
                if current_segment['content']:
                    current_segment['line_end'] = i - 1
                    segments.append(current_segment.copy())
                    
                current_segment = {
                    'type': 'context',
                    'content': line,
                    'timestamp': datetime.now().isoformat(),
                    'line_start': i,
                    'line_end': i
                }
            else:
                current_segment['content'] += '\n' + line
                current_segment['line_end'] = i
                
        # Default: append to current segment
        else:
            if current_segment['content']:
                current_segment['content'] += '\n' + line
            else:
                current_segment['content'] = line
                current_segment['line_start'] = i
            current_segment['line_end'] = i
    
    # Add final segment if it has content
    if current_segment['content']:
        segments.append(current_segment)
    
    # Filter out segments with minimal content
    segments = [seg for seg in segments if len(seg['content'].strip()) > 3]
    
    # Telemetry logging
    parse_time = time.time() - start_time
    logging.info(f"Parsed {len(segments)} segments in {parse_time:.3f}s")
    
    # Log segment breakdown
    segment_types = {}
    for seg in segments:
        segment_types[seg['type']] = segment_types.get(seg['type'], 0) + 1
    
    logging.debug(f"Segment breakdown: {segment_types}")
    
    return segments


def _is_command_line(line: str) -> bool:
    """Check if line appears to be a command."""
    command_patterns = [
        r'^[a-zA-Z0-9_-]+\s+[a-zA-Z0-9_-]+',  # command subcommand
        r'^[a-zA-Z0-9_-]+\s*:',  # command:
        r'^\$\s*[a-zA-Z0-9_-]+',  # $ command
        r'^>\s*[a-zA-Z0-9_-]+',  # > command
    ]
    
    return any(re.match(pattern, line) for pattern in command_patterns)


def _is_task_line(line: str) -> bool:
    """Check if line appears to be a task or instruction."""
    task_patterns = [
        r'^(Task|TODO|Action|Step)\s*\d*\s*:',
        r'^\d+\.\s*[A-Z]',  # 1. Task
        r'^-\s*[A-Z]',  # - Task
        r'^(Implement|Create|Build|Add|Update|Fix)',
    ]
    
    return any(re.match(pattern, line, re.IGNORECASE) for pattern in task_patterns)


def _is_context_line(line: str) -> bool:
    """Check if line appears to be context or background info."""
    context_patterns = [
        r'^(Note|Context|Background|Info|Details?)\s*:',
        r'^(Given|Assuming|Consider|Remember)',
        r'^\*\*[A-Z]',  # **Context
    ]
    
    return any(re.match(pattern, line, re.IGNORECASE) for pattern in context_patterns)


def validate_segments(segments: List[Dict[str, Any]]) -> bool:
    """
    Validate parsed segments for completeness and correctness.
    
    Args:
        segments: List of parsed segments
        
    Returns:
        True if segments are valid, False otherwise
    """
    if not segments:
        logging.warning("No segments found in conversation")
        return False
    
    required_keys = {'type', 'content', 'timestamp'}
    
    for i, segment in enumerate(segments):
        if not all(key in segment for key in required_keys):
            logging.error(f"Segment {i} missing required keys: {required_keys - set(segment.keys())}")
            return False
            
        if not segment['content'].strip():
            logging.warning(f"Segment {i} has empty content")
            
        if segment['type'] not in ['command', 'task', 'context', 'unknown']:
            logging.warning(f"Segment {i} has unexpected type: {segment['type']}")
    
    logging.debug(f"Validated {len(segments)} segments successfully")
    return True