"""
Context Bundle Module

Provides utilities for creating and managing context bundles used by worker threads.
This is a critical component for the N5 worker system.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json


def create_context_bundle(
    parent_id: str,
    instruction: str,
    worker_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a context bundle for worker thread execution.
    
    Args:
        parent_id: The parent conversation ID
        instruction: The worker instruction
        worker_type: Type of worker (build, research, analysis, general)
        metadata: Optional additional metadata
        
    Returns:
        Dictionary containing the context bundle
    """
    bundle = {
        "parent_id": parent_id,
        "instruction": instruction,
        "worker_type": worker_type,
        "metadata": metadata or {}
    }
    return bundle


def save_context_bundle(bundle: Dict[str, Any], filepath: Path) -> None:
    """
    Save a context bundle to a JSON file.
    
    Args:
        bundle: The context bundle dictionary
        filepath: Path where to save the bundle
    """
    with open(filepath, 'w') as f:
        json.dump(bundle, f, indent=2)


def load_context_bundle(filepath: Path) -> Dict[str, Any]:
    """
    Load a context bundle from a JSON file.
    
    Args:
        filepath: Path to the bundle file
        
    Returns:
        Dictionary containing the context bundle
    """
    with open(filepath, 'r') as f:
        return json.load(f)

