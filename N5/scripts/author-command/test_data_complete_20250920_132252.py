#!/usr/bin/env python3
"""
Test Data Generator for Command Authoring System

Generates test conversation samples and validates system components.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger('test_data_generator')


class TestConversationGenerator:
    """Generates test conversation data for various scenarios"""
    
    def __init__(self):
        self.conversation_templates = [
            self._file_analysis_conversation,
            self._batch_processing_conversation,
            self._error_handling_conversation,
            self._complex_workflow_conversation,
            self._simple_task_conversation
        ]
    
    def generate_all_test_conversations(self, output_dir: str = "/home/workspace/N5/tmp_execution/test_data"):
        """Generate all test conversation samples"""
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        for i, template_func in enumerate(self.conversation_templates):
            conversation_data = template_func()
            filename = f"test_conversation_{i+1}_{conversation_data['scenario']}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(conversation_data['content'])
            
            generated_files.append({
                'file': filepath,
                'scenario': conversation_data['scenario'],
                'expected_tools': conversation_data['expected_tools'],
                'complexity': conversation_data['complexity']
            })
            
            logger.info(f"Generated test conversation: {filename}")
        
        # Create test manifest
        manifest_path = os.path.join(output_dir, "test_manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'conversations': generated_files
            }, f, indent=2)
        
        logger.info(f"Generated {len(generated_files)} test conversations")
        return generated_files
    
    def _file_analysis_conversation(self) -> Dict[str, Any]:
        """Generate file analysis conversation"""
        return {
            'scenario': 'file_analysis',
            'complexity': 'medium',
            'expected_tools': ['search_existing_commands', 'create_command_draft', 'validate_command'],
            'content': '''User: I need a command to analyze log files and extract error patterns.