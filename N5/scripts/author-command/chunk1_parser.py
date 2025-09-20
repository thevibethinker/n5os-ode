#!/usr/bin/env python3
"""
Chunk 1: Conversation Parser Module

Parses conversation transcripts into structured JSON segments.
Implements telemetry logging for diagnostics.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging (only to file when running as CLI)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
        handlers=[logging.FileHandler('/home/workspace/command_authoring.log', mode='a')]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler('/home/workspace/command_authoring.log', mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger('chunk1_parser')


class ConversationSegment:
    """Represents a parsed segment of a conversation"""
    
    def __init__(self, id: str, timestamp: datetime, content: str, segment_type: str, 
                 tool_name: Optional[str] = None, parameters: Optional[Dict] = None):
        self.id = id
        self.timestamp = timestamp
        self.content = content
        self.segment_type = segment_type
        self.tool_name = tool_name
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'content': self.content,
            'segment_type': self.segment_type,
            'tool_name': self.tool_name,
            'parameters': self.parameters
        }


class ConversationParser:
    """Parses conversation logs to identify workflow patterns"""
    
    def __init__(self):
        self.segment_count = 0
        self.parse_time = 0.0
        self.error_count = 0
        self.input_size = 0
    
    def parse_conversation(self, conversation_path: str) -> Dict[str, Any]:
        """
        Parse a single conversation file
        
        Args:
            conversation_path: Path to conversation file
            
        Returns:
            Dict containing segments and telemetry data
        """
        logger.info(f"Parsing conversation: {conversation_path}")
        start_time = time.time()
        
        segments = []
        
        try:
            if not os.path.exists(conversation_path):
                raise FileNotFoundError(f"Conversation file not found: {conversation_path}")
            
            with open(conversation_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.input_size = len(content)
            
            # Parse conversation into segments
            segments = self._parse_segments(content)
            
        except Exception as e:
            logger.error(f"Failed to parse conversation {conversation_path}: {e}")
            self.error_count += 1
            segments = []
        
        self.segment_count = len(segments)
        self.parse_time = time.time() - start_time
        
        # Log telemetry
        logger.info(f"Parsed {self.segment_count} segments in {self.parse_time:.2f}s")
        logger.info(f"Input size: {self.input_size} characters")
        if self.error_count > 0:
            logger.warning(f"Encountered {self.error_count} errors during parsing")
        
        return {
            'segments': [seg.to_dict() for seg in segments],
            'telemetry': {
                'segment_count': self.segment_count,
                'parse_time': self.parse_time,
                'error_count': self.error_count,
                'input_size': self.input_size
            }
        }
    
    def _parse_segments(self, content: str) -> List[ConversationSegment]:
        """Parse content into segments based on conversation format"""
        segments = []
        lines = content.split('\n')
        
        current_segment = None
        current_content = []
        segment_id_counter = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify segment boundaries
            if self._is_new_segment(line):
                if current_segment:
                    segments.append(current_segment)
                
                segment_type, tool_name = self._classify_segment(line)
                current_segment = ConversationSegment(
                    id=f"seg_{segment_id_counter}",
                    timestamp=datetime.now(),  # Placeholder - extract from actual format if available
                    content="",
                    segment_type=segment_type,
                    tool_name=tool_name
                )
                current_content = [line]
                segment_id_counter += 1
                
            elif current_segment:
                current_content.append(line)
                current_segment.content = '\n'.join(current_content)
        
        # Add final segment
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def _is_new_segment(self, line: str) -> bool:
        """Determine if line starts a new segment"""
        return (
            line.startswith('User:') or 
            line.startswith('Assistant:') or
            line.startswith('Human:') or
            line.startswith('AI:') or
            line.startswith('Tool:') or
            'function_call' in line.lower()
        )
    
    def _classify_segment(self, line: str) -> tuple[str, Optional[str]]:
        """Classify segment type and extract tool name if applicable"""
        if 'User:' in line or 'Human:' in line:
            return 'user_query', None
        elif 'Assistant:' in line or 'AI:' in line:
            return 'assistant_response', None
        elif 'Tool:' in line or 'function_call' in line.lower():
            # Extract tool name from line
            tool_name = self._extract_tool_name(line)
            return 'tool_call', tool_name
        else:
            return 'unknown', None
    
    def _extract_tool_name(self, line: str) -> Optional[str]:
        """Extract tool name from tool call line"""
        # Simple extraction - adjust based on actual format
        if 'name=' in line:
            # Assume format like: function_call name="tool_name"
            parts = line.split('name=')
            if len(parts) > 1:
                tool_part = parts[1].split()[0].strip('"\'')
                return tool_part
        return None


def main():
    """CLI interface for Chunk 1"""
    if len(sys.argv) != 2:
        print("Usage: python chunk1_parser.py <conversation_file>")
        sys.exit(1)
    
    conversation_path = sys.argv[1]
    
    parser = ConversationParser()
    result = parser.parse_conversation(conversation_path)
    
    # Output JSON result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()