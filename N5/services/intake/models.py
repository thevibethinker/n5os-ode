"""
Unified Meeting Intake Models

Defines the canonical data structures for meeting transcript ingestion.
All adapters must produce a UnifiedTranscript that passes validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class IntakeSource(Enum):
    """Supported transcript sources"""
    FIREFLIES = "fireflies"
    FATHOM = "fathom"
    MANUAL = "manual"
    GRANOLA = "granola"  # Future


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    ERROR = "error"      # Blocks ingestion
    WARNING = "warning"  # Logs but proceeds
    INFO = "info"        # Informational only


@dataclass
class Utterance:
    """Single speaker turn in transcript"""
    speaker: str
    text: str
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None


@dataclass
class UnifiedTranscript:
    """
    Canonical transcript shape - all adapters MUST produce this.
    
    The output validation layer checks this shape before intake proceeds.
    """
    # Required fields
    source: IntakeSource
    full_text: str
    detected_date: Optional[datetime]
    
    # Participant info
    participants: List[str] = field(default_factory=list)
    host: Optional[str] = None
    
    # Structured content (if available)
    utterances: List[Utterance] = field(default_factory=list)
    
    # Metadata
    title: Optional[str] = None
    duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    source_id: Optional[str] = None  # e.g., Fireflies transcript_id
    
    # Summary (from source if available)
    summary: Optional[str] = None
    
    # Raw payload for debugging
    raw_payload: Optional[Dict[str, Any]] = None
    
    def to_transcript_jsonl(self) -> Dict[str, Any]:
        """Convert to the standard transcript.jsonl format"""
        utterance_dicts = []
        for u in self.utterances:
            ud = {"speaker": u.speaker, "text": u.text}
            if u.start_ms is not None:
                ud["start"] = u.start_ms
            if u.end_ms is not None:
                ud["end"] = u.end_ms
            utterance_dicts.append(ud)
        
        return {
            "text": self.full_text,
            "utterances": utterance_dicts,
            "chunks": utterance_dicts,  # Same as utterances for now
            "source": self.source.value,
            "source_id": self.source_id,
            "duration_seconds": self.duration_seconds,
            "recording_url": self.recording_url,
        }
    
    def to_manifest_seed(self) -> Dict[str, Any]:
        """Generate seed data for manifest.json"""
        return {
            "source": self.source.value,
            "source_id": self.source_id,
            "detected_date": self.detected_date.isoformat() if self.detected_date else None,
            "participants": self.participants,
            "host": self.host,
            "title": self.title,
            "duration_seconds": self.duration_seconds,
            "summary": self.summary,
            "ingested_at": datetime.now().isoformat(),
        }


@dataclass
class ValidationResult:
    """Result of validating a UnifiedTranscript"""
    field: str
    message: str
    severity: ValidationSeverity
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.field}: {self.message}"


@dataclass
class IntakeResult:
    """Result of the full intake process"""
    success: bool
    folder_path: Optional[str] = None
    folder_name: Optional[str] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    error_message: Optional[str] = None
    duplicate_of: Optional[str] = None  # If dedupe detected
    
    @property
    def has_errors(self) -> bool:
        return any(v.severity == ValidationSeverity.ERROR for v in self.validation_results)
    
    @property
    def has_warnings(self) -> bool:
        return any(v.severity == ValidationSeverity.WARNING for v in self.validation_results)


class TranscriptValidator:
    """
    Output validation layer (Level Upper recommendation #1)
    
    Validates UnifiedTranscript before intake proceeds.
    Catches adapter bugs early.
    """
    
    @staticmethod
    def validate(transcript: UnifiedTranscript) -> List[ValidationResult]:
        """Validate a UnifiedTranscript, return list of issues"""
        results = []
        
        # Required: full_text must exist and have content
        if not transcript.full_text:
            results.append(ValidationResult(
                "full_text", "Transcript text is empty", ValidationSeverity.ERROR
            ))
        elif len(transcript.full_text) < 50:
            results.append(ValidationResult(
                "full_text", f"Transcript suspiciously short ({len(transcript.full_text)} chars)", 
                ValidationSeverity.WARNING
            ))
        
        # Required: source must be valid
        if not isinstance(transcript.source, IntakeSource):
            results.append(ValidationResult(
                "source", f"Invalid source type: {type(transcript.source)}", 
                ValidationSeverity.ERROR
            ))
        
        # Warning: no participants detected
        if not transcript.participants:
            results.append(ValidationResult(
                "participants", "No participants detected - folder naming may be generic",
                ValidationSeverity.WARNING
            ))
        
        # Warning: no date detected
        if not transcript.detected_date:
            results.append(ValidationResult(
                "detected_date", "No date detected - will use today's date",
                ValidationSeverity.WARNING
            ))
        
        # Info: no utterances (acceptable for some sources)
        if not transcript.utterances:
            results.append(ValidationResult(
                "utterances", "No structured utterances - only full text available",
                ValidationSeverity.INFO
            ))
        
        # Validate utterances if present
        for i, utterance in enumerate(transcript.utterances):
            if not utterance.speaker:
                results.append(ValidationResult(
                    f"utterances[{i}].speaker", "Missing speaker name",
                    ValidationSeverity.WARNING
                ))
            if not utterance.text:
                results.append(ValidationResult(
                    f"utterances[{i}].text", "Empty utterance text",
                    ValidationSeverity.WARNING
                ))
        
        return results
    
    @staticmethod
    def is_valid(transcript: UnifiedTranscript) -> bool:
        """Quick check: does transcript pass validation (no errors)?"""
        results = TranscriptValidator.validate(transcript)
        return not any(r.severity == ValidationSeverity.ERROR for r in results)

