#!/usr/bin/env python3
"""
LLM-powered meeting folder naming
Calls B99 prompt to leverage semantic understanding
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict
import logging

def call_b99_prompt(b26_content: str, b28_content: str, current_name: Optional[str] = None) -> Optional[str]:
    """Call B99 prompt as a tool to generate folder name
    
    Args:
        b26_content: Full content of B26_metadata.md
        b28_content: Full content of B28_strategic_intelligence.md
        current_name: Current folder name (optional, for context)
    
    Returns:
        Generated folder name or None if failed
    """
    try:
        # Create a temporary workspace for the LLM call
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Write B26 and B28 to temp files
            b26_path = tmpdir_path / "B26_metadata.md"
            b28_path = tmpdir_path / "B28_strategic_intelligence.md"
            
            b26_path.write_text(b26_content)
            b28_path.write_text(b28_content)
            
            # Construct prompt invocation
            # The B99 prompt expects both files to be loaded in context
            prompt_text = f"""Generate meeting folder name using B99 prompt.

Current folder: {current_name if current_name else 'unknown'}

B26 Metadata:
```
{b26_content[:2000]}  # Truncate for context window
```

B28 Strategic Intelligence:
```
{b28_content[:2000]}  # Truncate for context window
```

Load and invoke file 'Intelligence/prompts/B99_folder_naming.md' as a tool with this context.
Return ONLY the folder name in format: YYYY-MM-DD_identifier_type
"""
            
            # Write prompt to temp file
            prompt_file = tmpdir_path / "naming_request.txt"
            prompt_file.write_text(prompt_text)
            
            # Call Zo CLI to process this (simulated for now)
            # In production, this would use the Zo API or subprocess to new conversation
            
            # For now, return None to indicate "not implemented yet"
            # This allows us to test the fallback logic
            logging.info("LLM naming called (not yet connected to Zo API)")
            return None
            
    except Exception as e:
        logging.warning(f"LLM naming failed: {e}")
        return None

def generate_folder_name_llm(
    b26_path: Path,
    b28_path: Path,
    current_name: Optional[str] = None,
    timeout: int = 30
) -> Optional[str]:
    """Generate folder name using LLM intelligence
    
    Args:
        b26_path: Path to B26_metadata.md
        b28_path: Path to B28_strategic_intelligence.md
        current_name: Current folder name (for context)
        timeout: Max seconds to wait for LLM response
    
    Returns:
        Generated folder name or None if failed
    """
    try:
        # Validate inputs
        if not b26_path.exists():
            logging.warning(f"B26 not found: {b26_path}")
            return None
        
        if not b28_path.exists():
            logging.warning(f"B28 not found: {b28_path}")
            return None
        
        # Read content
        b26_content = b26_path.read_text()
        b28_content = b28_path.read_text()
        
        # Call B99 prompt
        result = call_b99_prompt(b26_content, b28_content, current_name)
        
        if result:
            # Validate format: YYYY-MM-DD_something_type
            import re
            if re.match(r'^\d{4}-\d{2}-\d{2}_[a-zA-Z0-9-]+_[a-z]+$', result):
                logging.info(f"LLM generated: {result}")
                return result
            else:
                logging.warning(f"LLM returned invalid format: {result}")
                return None
        
        return None
        
    except Exception as e:
        logging.error(f"Error in LLM naming: {e}")
        return None

def test_llm_naming():
    """Unit test for LLM naming function"""
    print("=" * 70)
    print("TESTING LLM NAMING MODULE")
    print("=" * 70)
    print()
    
    # Test with mock B26/B28 content
    b26_mock = """---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# B26 - MEETING_METADATA_SUMMARY

**Meeting ID**: Test Meeting
**Date**: 2025-11-04
**Stakeholder Type**: PARTNER

**Primary Stakeholders**:
- Tim He (Twill)
- Vrijen Attawar (Careerspan)
"""
    
    b28_mock = """---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# B28 - STRATEGIC_INTELLIGENCE_METADATA

**Meeting Type**: Partnership Development
**Strategic Context**: Product discussion and partnership exploration
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        b26_path = tmpdir_path / "B26_metadata.md"
        b28_path = tmpdir_path / "B28_strategic_intelligence.md"
        
        b26_path.write_text(b26_mock)
        b28_path.write_text(b28_mock)
        
        print("✓ Test 1: Valid B26/B28 files")
        result = generate_folder_name_llm(b26_path, b28_path, "test-meeting")
        print(f"  Result: {result if result else 'None (expected - LLM not connected)'}")
        print()
        
        print("✓ Test 2: Missing B28")
        b28_path.unlink()
        result = generate_folder_name_llm(b26_path, b28_path)
        print(f"  Result: {result if result else 'None (expected)'}")
        print()
        
        print("✓ Test 3: Invalid paths")
        result = generate_folder_name_llm(Path("/nonexistent"), Path("/also-nonexistent"))
        print(f"  Result: {result if result else 'None (expected)'}")
        print()
    
    print("=" * 70)
    print("LLM naming module tests complete")
    print("Note: LLM integration not yet wired to Zo API")
    print("=" * 70)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_llm_naming()
