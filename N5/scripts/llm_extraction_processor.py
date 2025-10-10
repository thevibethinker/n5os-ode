#!/usr/bin/env python3
"""
LLM Extraction Processor for Meeting Intelligence Orchestrator
This script is designed to be called within Zo's conversational context
to process extraction requests using Zo's built-in LLM capabilities.
"""

import json
import sys
from pathlib import Path

def process_extraction_request(request_file: str, output_file: str):
    """
    Process an LLM extraction request and write results.
    
    This script is meant to be invoked by the orchestrator and processed
    by Zo's LLM in the conversational context.
    
    Args:
        request_file: Path to JSON file containing extraction request
        output_file: Path where extraction results should be written
    """
    # Load the request
    with open(request_file, 'r') as f:
        request = json.load(f)
    
    system_prompt = request.get('system_prompt', '')
    user_prompt = request.get('user_prompt', '')
    
    # Create an instruction for Zo's LLM
    instruction = f"""
EXTRACTION REQUEST
==================

{system_prompt}

{user_prompt}

Please analyze the above request and transcript, then output ONLY valid JSON matching the requested structure.
Write the JSON response to: {output_file}
"""
    
    # Output the instruction
    print(instruction)
    print(f"\n📝 Extraction request prepared. Output should be written to: {output_file}")
    
    return instruction

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 llm_extraction_processor.py <request_file> <output_file>")
        sys.exit(1)
    
    request_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_extraction_request(request_file, output_file)
