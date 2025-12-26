"""
Unified Meeting Intake Service

Canonical entry point for all meeting transcript ingestion.
Sources: Fathom, Fireflies, Manual, Granola (future)
"""

from .models import UnifiedTranscript, IntakeResult, ValidationResult
from .intake_engine import IntakeEngine

__all__ = ["UnifiedTranscript", "IntakeResult", "ValidationResult", "IntakeEngine"]

