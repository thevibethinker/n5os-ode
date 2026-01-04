#!/usr/bin/env python3
"""Unified Participant Extraction - Single source of truth for participant data.

Consolidates logic from:
- meeting_crm_linker.py (extract_participants_from_b03, extract_participants_from_folder_name)
- consolidated_transcript_workflow.py (_extract_participants, _extract_explicit_participants)
- meeting_normalizer.py (normalize_participant_name)

Part of N5 System Optimization - Workstream 2.

Usage:
    # In code:
    from participant_extractor import ParticipantExtractor
    extractor = ParticipantExtractor()
    result = extractor.extract_best_available(meeting_folder)

    # CLI:
    python participant_extractor.py /path/to/meeting/folder
"""

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import canonical paths
import sys
sys.path.insert(0, str(Path(__file__).parent))
from crm_paths import MEETINGS_ROOT

# Try to import CRM lookup for slug resolution
try:
    from crm_lookup import CRMLookupService
    _CRM_LOOKUP_AVAILABLE = True
except ImportError:
    _CRM_LOOKUP_AVAILABLE = False


@dataclass
class Participant:
    """Canonical participant representation."""
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    role_in_meeting: Optional[str] = None
    crm_slug: Optional[str] = None
    is_host: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, omitting None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ExtractionResult:
    """Result of participant extraction with metadata."""
    entries: List[Participant]
    extraction_source: str
    extracted_at: str
    confidence: float  # 0.0-1.0

    def to_manifest_dict(self) -> Dict[str, Any]:
        """Convert to format suitable for manifest.json."""
        return {
            "extracted_at": self.extracted_at,
            "extraction_source": self.extraction_source,
            "entries": [p.to_dict() for p in self.entries]
        }


class ParticipantExtractor:
    """Unified participant extraction from multiple sources.

    Provides a single interface for extracting participants from:
    - manifest.json (already extracted)
    - B03/B08 stakeholder intelligence blocks
    - Meeting folder names

    Example:
        extractor = ParticipantExtractor()
        result = extractor.extract_best_available(Path("/path/to/meeting"))
        result = extractor.resolve_crm_slugs(result)
        extractor.save_to_manifest(manifest_path, result)
    """

    # Consolidated skip keywords from meeting_crm_linker.py
    SKIP_KEYWORDS = {
        'participants', 'group dynamics', 'stakeholder intelligence', 'stakeholder_intelligence',
        'meeting context', 'relationship with v', 'relationship dynamics', 'identity',
        'professional intelligence', 'interaction history', 'quick reference',
        'auto-generated metadata', 'intelligence log', 'enrichment data',
        'gmail intelligence', 'linkedin intelligence', 'founder profiles',
        'dynamic between', 'threat assessment', 'information asymmetries',
        'knowledge gaps', 'market influencer', 'potential acquirer', 'foundational profile',
        'what resonated', 'crm integration', 'howie integration', 'domain authority',
        'source credibility', 'internal stakeholders', 'external stakeholders',
        'communication patterns', 'relationship notes', 'integration points',
        'team dynamics', 'interpersonal patterns', 'cultural observations',
        'conflict zones', 'intelligence gaps', 'follow-up trigger', 'relationship intelligence',
        'meeting recap', 'key takeaways', 'action items', 'next steps', 'summary',
        'context', 'background', 'overview', 'agenda', 'notes', 'discussion',
        # Block titles
        'b03', 'b08', 'external brief', 'detailed recap', 'decisions', 'deliverables',
    }

    # Internal name indicators
    INTERNAL_INDICATORS = {'careerspan', 'vrijen', 'attawar', 'mycareerspan'}

    # Patterns for folder name parsing
    FOLDER_NAME_PATTERN = re.compile(
        r'^(\d{4}-\d{2}-\d{2})_(.+?)(?:_\[([MP])\])?$'
    )
    FOLDER_SEPARATOR_PATTERN = re.compile(
        r'[-_](?:and|x|&)[-_]|[-_]',
        re.IGNORECASE
    )

    # Patterns for B03/B08 extraction
    B03_NAME_FIELD_PATTERN = re.compile(r'\*\*Name:\*\*\s*([^\n]+)')
    # Only match level-2 headers (##), NOT level-3 (###) which are subsections
    B03_HEADER_PATTERN = re.compile(r'^##\s+(?!\#)([^#\n]+)', re.MULTILINE)

    def __init__(self, crm_lookup_service: Optional[Any] = None):
        """Initialize with optional CRM lookup for slug resolution.

        Args:
            crm_lookup_service: Optional CRMLookupService instance.
                If None and available, creates one automatically.
        """
        self._crm_lookup = crm_lookup_service
        if self._crm_lookup is None and _CRM_LOOKUP_AVAILABLE:
            self._crm_lookup = CRMLookupService()

    def extract_from_manifest(self, manifest_path: Path) -> Optional[ExtractionResult]:
        """Check if manifest already has canonical participants.

        Args:
            manifest_path: Path to manifest.json file.

        Returns:
            ExtractionResult if participants found in manifest, None otherwise.
        """
        try:
            manifest = json.loads(manifest_path.read_text())
            participants_data = manifest.get('participants')

            if participants_data and participants_data.get('entries'):
                entries = [
                    Participant(**{k: v for k, v in p.items() if k in Participant.__dataclass_fields__})
                    for p in participants_data['entries']
                ]
                return ExtractionResult(
                    entries=entries,
                    extraction_source=participants_data.get('extraction_source', 'manifest'),
                    extracted_at=participants_data.get('extracted_at', ''),
                    confidence=1.0
                )
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            pass
        return None

    def extract_from_b03(self, b03_path: Path) -> ExtractionResult:
        """Extract participants from B03/B08 block markdown.

        Handles two formats:
        1. **Name:** field (B08 format)
        2. ## or ### headers (B03 format)

        Args:
            b03_path: Path to B03 or B08 markdown file.

        Returns:
            ExtractionResult with extracted participants.
        """
        if not b03_path.exists():
            return ExtractionResult(
                entries=[],
                extraction_source="B03_not_found",
                extracted_at=datetime.utcnow().isoformat() + "Z",
                confidence=0.0
            )

        content = b03_path.read_text(encoding='utf-8')
        participants = []

        # Method 1: Extract from **Name:** field (B08 format)
        for match in self.B03_NAME_FIELD_PATTERN.finditer(content):
            name = match.group(1).strip()
            if self._is_valid_name(name):
                p = Participant(name=self._normalize_name(name))
                if not self._is_duplicate(p, participants):
                    participants.append(p)

        # Method 2: Extract from headers (B03 format) - only if Method 1 found nothing
        if not participants:
            for match in self.B03_HEADER_PATTERN.finditer(content):
                header_text = match.group(1).strip()
                if self._is_skip_keyword(header_text):
                    continue

                # Parse "Name – Organization" or "Name - Organization" format
                name, company = self._parse_header_name(header_text)
                if self._is_valid_name(name):
                    p = Participant(
                        name=self._normalize_name(name),
                        company=company
                    )
                    if not self._is_duplicate(p, participants):
                        participants.append(p)

        # Mark internal participants
        for p in participants:
            p.is_host = self._is_internal(p.name)

        source = "B08_regex" if "B08" in b03_path.name else "B03_regex"
        return ExtractionResult(
            entries=participants,
            extraction_source=source,
            extracted_at=datetime.utcnow().isoformat() + "Z",
            confidence=0.85 if participants else 0.0
        )

    def extract_from_folder_name(self, folder_path: Path) -> ExtractionResult:
        """Extract participants from meeting folder name.

        Parses names from folder patterns like:
        - 2025-12-16_Victor-hu-Lumos-capital
        - 2025-11-17_Vrijen-Attawar-And-Paula-Mcmahon

        Args:
            folder_path: Path to meeting folder.

        Returns:
            ExtractionResult with extracted participants.
        """
        folder_name = folder_path.name
        match = self.FOLDER_NAME_PATTERN.match(folder_name)

        participants = []
        if match:
            names_part = match.group(2)

            # Split on common separators
            segments = self.FOLDER_SEPARATOR_PATTERN.split(names_part)

            for segment in segments:
                segment = segment.strip()
                if not segment:
                    continue

                # Convert to title case and clean up
                name = self._folder_segment_to_name(segment)
                if self._is_valid_name(name):
                    p = Participant(name=name)
                    p.is_host = self._is_internal(name)
                    if not self._is_duplicate(p, participants):
                        participants.append(p)

        return ExtractionResult(
            entries=participants,
            extraction_source="folder_name",
            extracted_at=datetime.utcnow().isoformat() + "Z",
            confidence=0.6 if participants else 0.0
        )

    def extract_best_available(self, meeting_folder: Path) -> ExtractionResult:
        """Extract participants using best available source.

        Priority: manifest > B03 > B08 > folder_name

        Args:
            meeting_folder: Path to meeting folder.

        Returns:
            ExtractionResult from the best available source.
        """
        manifest_path = meeting_folder / "manifest.json"

        # 1. Check manifest first (already extracted)
        result = self.extract_from_manifest(manifest_path)
        if result and result.entries:
            return result

        # 2. Try B03 files
        b03_patterns = [
            "B03_STAKEHOLDER_INTELLIGENCE.md",
            "B03_STAKE_HOLDER_INTELLIGENCE.md",
            "B03_EXTERNAL_BRIEF.md",
        ]
        for pattern in b03_patterns:
            b03_path = meeting_folder / pattern
            if b03_path.exists():
                result = self.extract_from_b03(b03_path)
                if result.entries:
                    return result

        # 3. Try B08 files
        b08_patterns = [
            "B08_STAKEHOLDER_INTELLIGENCE.md",
        ]
        for pattern in b08_patterns:
            b08_path = meeting_folder / pattern
            if b08_path.exists():
                result = self.extract_from_b03(b08_path)  # Same parsing logic
                if result.entries:
                    return result

        # 4. Fall back to folder name
        return self.extract_from_folder_name(meeting_folder)

    def resolve_crm_slugs(self, result: ExtractionResult) -> ExtractionResult:
        """Enrich participants with CRM slugs using lookup service.

        Args:
            result: ExtractionResult to enrich.

        Returns:
            Same ExtractionResult with crm_slug fields populated.
        """
        if not self._crm_lookup:
            return result

        for participant in result.entries:
            if not participant.crm_slug:
                lookup_result = self._crm_lookup.lookup_participant(
                    participant.name,
                    participant.email
                )
                if lookup_result:
                    participant.crm_slug = lookup_result.slug

        return result

    def save_to_manifest(self, manifest_path: Path, result: ExtractionResult) -> None:
        """Save extraction result to manifest.json.

        Args:
            manifest_path: Path to manifest.json file.
            result: ExtractionResult to save.
        """
        try:
            manifest = json.loads(manifest_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            manifest = {}

        manifest['participants'] = result.to_manifest_dict()
        manifest_path.write_text(json.dumps(manifest, indent=2))

    # -------------------------------------------------------------------------
    # Private helper methods
    # -------------------------------------------------------------------------

    def _normalize_name(self, name: str) -> str:
        """Normalize participant name."""
        if not name:
            return ""

        # Remove email if accidentally included
        name = re.sub(r'@[\w.-]+', '', name)

        # Remove numbered prefixes (e.g., "1. John Smith" -> "John Smith")
        name = re.sub(r'^\d+\.\s*', '', name)

        # Title case and strip
        name = ' '.join(word.capitalize() for word in name.split())

        return name.strip()

    def _parse_header_name(self, header_text: str) -> tuple:
        """Parse header like 'Name – Organization' or 'Name - Organization (role)'.

        Returns:
            Tuple of (name, company) where company may be None.
        """
        # Handle various dash/separator formats
        # "Victor Hu – Lumos Capital Group"
        # "Vrijen Attawar – Careerspan (Self)"

        separators = [' – ', ' - ', ' — ', ' | ']
        for sep in separators:
            if sep in header_text:
                parts = header_text.split(sep, 1)
                name = parts[0].strip()
                company = parts[1].strip() if len(parts) > 1 else None

                # Remove parenthetical suffixes from company like "(Self)"
                if company:
                    company = re.sub(r'\s*\([^)]*\)\s*$', '', company).strip()
                    if not company:
                        company = None

                return name, company

        # No separator found, whole thing is the name
        return header_text.strip(), None

    def _folder_segment_to_name(self, segment: str) -> str:
        """Convert folder name segment to proper name."""
        # Replace hyphens with spaces (except for hyphenated names)
        # "Victor-hu" -> "Victor Hu" but "O'Brien" stays intact

        # First, handle email-like patterns (remove domain)
        segment = re.sub(r'@[\w.-]+', '', segment)

        # Handle CamelCase or lowercase email prefixes
        # "victorhu" -> harder to parse, just capitalize
        if '-' in segment:
            words = segment.split('-')
            segment = ' '.join(w.capitalize() for w in words if w)
        else:
            segment = segment.capitalize()

        return segment.strip()

    def _is_valid_name(self, name: str) -> bool:
        """Check if name looks like a valid person name."""
        if not name:
            return False

        # Must be at least 2 characters
        if len(name) < 2:
            return False

        # Should have at least one letter
        if not any(c.isalpha() for c in name):
            return False

        # Reject if too long (likely a phrase)
        if len(name.split()) > 5:
            return False

        return True

    def _is_skip_keyword(self, name: str) -> bool:
        """Check if name matches a section header keyword."""
        name_lower = name.lower()
        return any(kw in name_lower for kw in self.SKIP_KEYWORDS)

    def _is_internal(self, name: str) -> bool:
        """Check if participant is internal (Careerspan team)."""
        name_lower = name.lower()
        return any(ind in name_lower for ind in self.INTERNAL_INDICATORS)

    def _is_duplicate(self, new: Participant, existing: List[Participant]) -> bool:
        """Check if participant already in list."""
        new_normalized = self._normalize_name(new.name).lower()
        for p in existing:
            if self._normalize_name(p.name).lower() == new_normalized:
                return True
            if new.email and p.email and new.email.lower() == p.email.lower():
                return True
        return False


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract participants from meeting folder"
    )
    parser.add_argument(
        'meeting_folder',
        type=Path,
        help="Path to meeting folder"
    )
    parser.add_argument(
        '--resolve-crm',
        action='store_true',
        help="Resolve CRM slugs for participants"
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help="Save results to manifest.json"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help="Output as JSON"
    )
    args = parser.parse_args()

    extractor = ParticipantExtractor()

    # Extract participants
    result = extractor.extract_best_available(args.meeting_folder)

    # Optionally resolve CRM slugs
    if args.resolve_crm:
        result = extractor.resolve_crm_slugs(result)

    # Optionally save to manifest
    if args.save:
        manifest_path = args.meeting_folder / "manifest.json"
        extractor.save_to_manifest(manifest_path, result)
        print(f"Saved to {manifest_path}")

    # Output results
    if args.json:
        print(json.dumps(result.to_manifest_dict(), indent=2))
    else:
        print(f"Source: {result.extraction_source}")
        print(f"Confidence: {result.confidence}")
        print(f"Extracted at: {result.extracted_at}")
        print(f"Participants ({len(result.entries)}):")
        for p in result.entries:
            internal_marker = " [internal]" if p.is_host else ""
            slug_marker = f" -> {p.crm_slug}" if p.crm_slug else ""
            print(f"  - {p.name}{internal_marker}{slug_marker}")


if __name__ == "__main__":
    main()
