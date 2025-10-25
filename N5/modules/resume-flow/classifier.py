#!/usr/bin/env python3
"""
Resume Flow Module - Self-contained resume detection and routing

Part of N5 modular flow architecture. Each module is self-contained with:
- Detection logic
- Routing rules  
- Learning integration

Intersects with system via:
- N5/data/learned_patterns.json (reads patterns)
- N5/config/anchors.json (reads canonical paths)
- Called by file_flow_router.py
"""

import re
from pathlib import Path
from typing import Tuple, List, Optional

# Module config
MODULE_NAME = "resume-flow"
CONFIDENCE_BASE = 0.90
CANONICAL_DEST = "Documents/Resumes"


def detect_resume(filepath: Path) -> Tuple[bool, float]:
    """
    Detect if file is a resume.
    Returns: (is_resume, confidence)
    """
    name = filepath.name.lower()
    ext = filepath.suffix.lower()
    
    # High confidence indicators
    high_confidence_keywords = ['resume', 'cv', 'curriculum vitae']
    if any(kw in name for kw in high_confidence_keywords):
        return (True, 0.95)
    
    # Medium confidence: person name + .pdf/.docx
    if ext in ['.pdf', '.docx']:
        # Check for name patterns (FirstName LastName format)
        # Heuristic: contains underscore or hyphen separating words
        if '_' in name or '-' in name:
            # Check if it's not a common system file pattern
            if not any(kw in name for kw in ['meeting', 'notes', 'doc', 'report', 'analysis']):
                return (True, 0.75)
    
    return (False, 0.0)


def extract_candidate_name(filepath: Path) -> Optional[str]:
    """Extract candidate name from filename."""
    name = filepath.stem
    
    # Common patterns:
    # FirstName_LastName_Resume.pdf
    # LastName, FirstName Resume.docx
    # FirstName LastName CV.pdf
    
    # Remove common suffixes
    for suffix in ['resume', 'cv', 'curriculum', 'vitae', '#2', 'v1', 'v2', 'optimized']:
        name = re.sub(rf'\s*[_-]?\s*{suffix}\s*', '', name, flags=re.IGNORECASE)
    
    # Clean up
    name = name.strip('_- ')
    name = re.sub(r'[_-]', ' ', name)
    
    return name if name else None


def normalize_filename(filepath: Path) -> str:
    """Generate normalized filename for consistent naming."""
    candidate = extract_candidate_name(filepath)
    ext = filepath.suffix
    
    if candidate:
        # Format: FirstName_LastName_Resume.ext
        normalized = candidate.replace(' ', '_')
        return f"{normalized}_Resume{ext}"
    else:
        # Fallback: use original
        return filepath.name


def classify(filepath: Path, learned_patterns: dict) -> dict:
    """
    Main classification entry point.
    Returns routing decision dict.
    """
    is_resume, confidence = detect_resume(filepath)
    
    if not is_resume:
        return {
            'module': MODULE_NAME,
            'matched': False,
            'confidence': 0.0
        }
    
    # Apply learned patterns boost
    resume_patterns = learned_patterns.get('resume_name_patterns', {})
    if resume_patterns.get('accuracy', 0.0) > 0.90:
        confidence = min(0.98, confidence + 0.05)
    
    # Generate normalized destination
    normalized_name = normalize_filename(filepath)
    
    return {
        'module': MODULE_NAME,
        'matched': True,
        'file_type': 'resume',
        'confidence': confidence,
        'destination': CANONICAL_DEST,
        'normalized_filename': normalized_name,
        'metadata': {
            'candidate_name': extract_candidate_name(filepath)
        }
    }


# Test mode
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_file = Path(sys.argv[1])
        result = classify(test_file, {})
        import json
        print(json.dumps(result, indent=2))
