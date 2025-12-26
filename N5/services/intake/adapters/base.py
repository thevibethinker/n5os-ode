"""
Base Adapter for Unified Meeting Intake

All source-specific adapters inherit from this.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models import UnifiedTranscript, IntakeSource


class BaseAdapter(ABC):
    """
    Abstract base class for transcript source adapters.
    
    Each adapter transforms source-specific data → UnifiedTranscript.
    The adapter is responsible for:
    - Parsing the source format
    - Extracting participants
    - Detecting date (semantic analysis)
    - Normalizing to UnifiedTranscript shape
    """
    
    source: IntakeSource  # Must be set by subclass
    
    @abstractmethod
    def adapt(self, payload: Dict[str, Any]) -> UnifiedTranscript:
        """
        Transform source payload to UnifiedTranscript.
        
        Args:
            payload: Source-specific data (webhook payload, file content, etc.)
            
        Returns:
            UnifiedTranscript ready for intake engine
        """
        pass
    
    @abstractmethod
    def extract_participants(self, payload: Dict[str, Any]) -> list:
        """Extract participant names from source data"""
        pass
    
    @abstractmethod
    def detect_date_semantic(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Attempt to detect meeting date from transcript content.
        
        This is the first step in the V Priority Order:
        1. Check semantically (this method)
        2. Check against calendar
        3. Assume today
        
        Returns:
            ISO date string if detected, None otherwise
        """
        pass
    
    def get_source_id(self, payload: Dict[str, Any]) -> Optional[str]:
        """Get unique ID from source for deduplication"""
        return None

