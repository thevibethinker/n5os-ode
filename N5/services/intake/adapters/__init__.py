"""
Source Adapters for Unified Meeting Intake

Each adapter transforms source-specific format → UnifiedTranscript
"""

from .base import BaseAdapter
from .fireflies_adapter import FirefliesAdapter
from .fathom_adapter import FathomAdapter
from .manual_adapter import ManualAdapter

__all__ = ["BaseAdapter", "FirefliesAdapter", "FathomAdapter", "ManualAdapter"]

