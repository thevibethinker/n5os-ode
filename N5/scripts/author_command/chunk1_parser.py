#!/usr/bin/env python3
"""
Chunk 1: Conversation Parser Module

Parses conversation transcripts into structured JSON segments.
Implements telemetry logging for diagnostics.
"""

import json
import logging
import os
import re
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
    
    def _validate_file_path(self, file_path: str) -> bool:
        """Validate file path for security"""
        try:
            # Normalize and resolve path
            resolved_path = Path(file_path).resolve()
            
            # Check for path traversal attempts  
            if '..' in str(resolved_path):
                logger.warning(f"Path traversal attempt detected: {file_path}")
                return False
            
            # Check if path is within allowed directories
            allowed_dirs = [
                Path("/home/workspace/N5/tmp_execution").resolve(),
                Path("/home/workspace/N5/test").resolve()
            ]
            
            if not any(str(resolved_path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs):
                logger.warning(f"File path outside allowed directories: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False
    
    def _check_file_size(self, file_path: str, max_size_mb: int = 10) -> bool:
        """Check if file size is within limits"""
        try:
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                logger.warning(f"File too large: {file_size} bytes (max: {max_size_bytes})")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File size check error: {e}")
            return False
    
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
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Identify segment boundaries
            if self._is_new_segment(line):
                # Finalize previous segment
                if current_segment and current_content:
                    current_segment.content = '\n'.join(current_content)
                    # Parse tool parameters if it's a tool call
                    if current_segment.segment_type == 'tool_call':
                        current_segment.parameters = self._extract_tool_parameters(current_segment.content)
                        current_segment.tool_name = self._extract_tool_name(current_segment.content)
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
        
        # Add final segment
        if current_segment and current_content:
            current_segment.content = '\n'.join(current_content)
            if current_segment.segment_type == 'tool_call':
                current_segment.parameters = self._extract_tool_parameters(current_segment.content)
                current_segment.tool_name = self._extract_tool_name(current_segment.content)
            segments.append(current_segment)
        
        return segments
    
    def _is_new_segment(self, line: str) -> bool:
        """Determine if line starts a new segment"""
        segment_patterns = [
            r'^User:',
            r'^Assistant:',
            r'^Human:',
            r'^AI:',
            r'^Tool:',
            r'function_call',
            r'^\[\d{2}:\d{2}:\d{2}\]',  # Timestamp format [HH:MM:SS]
            r'^\d{4}-\d{2}-\d{2}',      # Date format YYYY-MM-DD
        ]
        
        for pattern in segment_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _classify_segment(self, line: str) -> tuple[str, Optional[str]]:
        """Classify segment type and extract tool name if applicable"""
        line_lower = line.lower()
        
        if re.match(r'^(user|human):', line, re.IGNORECASE):
            return 'user_query', None
        elif re.match(r'^(assistant|ai):', line, re.IGNORECASE):
            return 'assistant_response', None
        elif re.match(r'^tool:', line, re.IGNORECASE) or 'function_call' in line_lower:
            return 'tool_call', None  # Tool name extracted later
        elif re.match(r'^\[\d{2}:\d{2}:\d{2}\]', line):
            return 'timestamp_marker', None
        elif re.match(r'^\d{4}-\d{2}-\d{2}', line):
            return 'date_marker', None
        elif line.startswith('#') or line.startswith('##'):
            return 'section_header', None
        else:
            return 'continuation', None  # Content continuing previous segment
    
    def _extract_tool_name(self, content: str) -> Optional[str]:
        """Extract tool name from tool call content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Tool:'):
                # Extract tool name from "Tool: tool_name" format
                tool_part = line[5:].strip()  # Remove "Tool: " prefix
                return tool_part
        return None
    
    def _extract_tool_parameters(self, content: str) -> Dict[str, Any]:
        """Extract parameters from tool call content"""
        parameters = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('Parameters:'):
                # Extract JSON parameters
                param_part = line[11:].strip()  # Remove "Parameters: " prefix
                try:
                    parameters = json.loads(param_part)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse tool parameters: {e}")
                    parameters = {'raw_parameters': param_part}
                break
        
        return parameters
    
    def process_large_document(self, input_text: str, source_name: str) -> Dict[str, Any]:
        """Process large document content for knowledge extraction"""
        logger.info(f"Processing document from source: {source_name}")
        
        # For now, treat the input text as a conversation file
        # Write to temp file and parse
        temp_path = f"/tmp/{source_name}_temp.txt"
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(input_text)
        
        try:
            result = self.parse_conversation(temp_path)
            # Add source metadata
            result['source_name'] = source_name
            result['processed_at'] = datetime.now().isoformat()
            return result
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def save_to_reservoirs(self, structured_data: Dict[str, Any]):
        """Save processed data to knowledge reservoirs"""
        self.knowledge_dir = Path("/home/workspace/Knowledge_reservoirs")
        self.knowledge_dir.mkdir(exist_ok=True)
        
        source_name = structured_data.get('source_name', 'unknown')
        
        # Save segments as JSON
        segments_file = self.knowledge_dir / f"{source_name}_segments.json"
        with open(segments_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2)
        
        logger.info(f"Saved knowledge to: {segments_file}")


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