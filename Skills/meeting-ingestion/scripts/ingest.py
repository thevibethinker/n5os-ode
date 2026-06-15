#!/usr/bin/env python3
"""
Ingest Module for Meeting System v3

Normalizes various transcript formats and creates v3 manifests with microsummaries.
Handles .md, .txt, .docx, .jsonl formats.

Usage:
    python3 ingest.py <file_or_folder> [--dry-run]

Examples:
    python3 ingest.py /path/to/transcript.md
    python3 ingest.py /path/to/inbox_folder --dry-run
    python3 ingest.py transcript.jsonl
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import requests
import logging
import shutil as _shutil
import uuid as _uuid

# Add workspace to path for imports
sys.path.insert(0, '/home/workspace')

# For docx handling
try:
    from docx import Document
except ImportError:
    Document = None

# D4: shared extraction + rejected-lane routing
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
from quality_gate import extract_conversation_content  # noqa: E402
from paths import REJECTED_DIR, ensure_rejected_dir, ACTIVE_DIR, MEETINGS_ROOT  # noqa: E402


class IngestError(Exception):
    """Custom exception for ingest errors"""
    pass


class TranscriptIngestor:
    """Main ingest class that handles various transcript formats"""
    
    def __init__(self):
        self.zo_api_url = "https://api.zo.computer/zo/ask"
        self.zo_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
        if not self.zo_token:
            raise IngestError("ZO_CLIENT_IDENTITY_TOKEN environment variable not set")
        
        self.supported_formats = ['.md', '.txt', '.docx', '.jsonl']
    
    def ingest_file(self, file_path: str, dry_run: bool = False) -> Dict:
        """
        Ingest a single file and create a meeting folder with v3 manifest
        
        Args:
            file_path: Path to the transcript file
            dry_run: If True, don't create files, just show what would be done
            
        Returns:
            Dictionary with ingest results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise IngestError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise IngestError(f"Unsupported format: {file_path.suffix}. Supported: {self.supported_formats}")
        
        print(f"Ingesting: {file_path}")
        
        # Extract transcript text based on format
        transcript_text = self._extract_transcript(file_path)
        
        # D4: Rule A — transcript too short (post-extraction clean content)
        clean_text = extract_conversation_content(transcript_text or "")
        clean_char_count = len(clean_text)
        clean_word_count = len(clean_text.split())
        if clean_char_count < 300:
            if dry_run:
                print(f"[DRY-RUN] Would reject (transcript_too_short): {clean_char_count} chars < 300")
                return {
                    "status": "dry_run_rejected",
                    "rejection_reason": "transcript_too_short",
                    "clean_char_count": clean_char_count,
                    "clean_word_count": clean_word_count,
                }
            return self._route_to_rejected(
                file_path=file_path,
                reason="transcript_too_short",
                detail=f"extracted {clean_char_count} chars (min 300)",
                clean_char_count=clean_char_count,
                clean_word_count=clean_word_count,
                duration_minutes=None,
            )

        # Extract metadata early so Rule B can check duration
        meeting_metadata = self._extract_meeting_metadata(transcript_text, file_path)
        duration_minutes = None
        dur_raw = meeting_metadata.get("duration_minutes")
        if dur_raw is None:
            dur_raw = meeting_metadata.get("duration")
        try:
            duration_minutes = float(dur_raw) if dur_raw is not None else None
        except (TypeError, ValueError):
            duration_minutes = None

        # D4: Rule B — tiny words for long meeting
        if duration_minutes and duration_minutes >= 15:
            expected_min = 0.2 * duration_minutes * 130
            if clean_word_count < expected_min:
                if dry_run:
                    print(f"[DRY-RUN] Would reject (tiny_words_for_long_meeting): {clean_word_count} words for {duration_minutes}-min meeting (expected >= {expected_min:.0f})")
                    return {
                        "status": "dry_run_rejected",
                        "rejection_reason": "tiny_words_for_long_meeting",
                        "clean_char_count": clean_char_count,
                        "clean_word_count": clean_word_count,
                        "duration_minutes": duration_minutes,
                    }
                return self._route_to_rejected(
                    file_path=file_path,
                    reason="tiny_words_for_long_meeting",
                    detail=f"{clean_word_count} words for {duration_minutes:.0f}-min meeting (expected >= {expected_min:.0f})",
                    clean_char_count=clean_char_count,
                    clean_word_count=clean_word_count,
                    duration_minutes=duration_minutes,
                )

        # Generate microsummary via /zo/ask
        microsummary = self._generate_microsummary(transcript_text)
        
        # Assess metadata quality (detect bare transcripts)
        metadata_quality = self._assess_metadata_quality(transcript_text, file_path)
        if metadata_quality["is_bare_transcript"]:
            missing = ", ".join(metadata_quality["missing"])
            print(f"⚠️  BARE TRANSCRIPT detected — missing: {missing}")
            print(f"   This transcript lacks speaker labels and participant context.")
            print(f"   The pipeline will flag it for manual clarification (HITL).")
            print(f"   To provide context, rename the file with participant names")
            print(f"   (e.g., 'John-x-Jane_Product-Discussion.md') or add a header:")
            print(f"   **Participants:** Name1, Name2")
        elif metadata_quality["missing"]:
            missing = ", ".join(metadata_quality["missing"])
            print(f"ℹ️  Partial metadata — missing: {missing} (confidence: {metadata_quality['confidence']})")

        # Extract meeting metadata from transcript
        meeting_metadata = meeting_metadata  # already extracted above for D4 Rule B
        
        # Generate meeting ID
        meeting_id = self._generate_meeting_id(meeting_metadata, file_path)

        # Duplicate guard: exact slug already exists anywhere canonical.
        existing_candidates = [
            ACTIVE_DIR / meeting_id,
            REJECTED_DIR / meeting_id,
            *list(MEETINGS_ROOT.glob(f"20??/*/week-*/{meeting_id}")),
            *list((MEETINGS_ROOT / 'archive').glob(f"**/{meeting_id}")),
        ]
        existing_meeting = next((p for p in existing_candidates if p.exists()), None)
        if existing_meeting is not None:
            print(f"⚠️  Duplicate intake suppressed — existing meeting: {existing_meeting}")
            return {
                "status": "duplicate_skipped",
                "meeting_id": meeting_id,
                "existing_path": str(existing_meeting),
                "folder_path": str(existing_meeting),
                "transcript_chars": len(transcript_text),
            }

        # Create meeting folder structure
        meeting_folder = file_path.parent / meeting_id
        
        if dry_run:
            print(f"[DRY-RUN] Would create folder: {meeting_folder}")
            print(f"[DRY-RUN] Would write transcript.md")
            print(f"[DRY-RUN] Would write manifest.json")
            print(f"[DRY-RUN] Microsummary: {microsummary[:100]}...")
            print(f"[DRY-RUN] Metadata quality: {metadata_quality['confidence']} (bare={metadata_quality['is_bare_transcript']})")
            return {
                "status": "dry_run",
                "meeting_id": meeting_id,
                "folder_path": str(meeting_folder),
                "microsummary": microsummary,
                "metadata_quality": metadata_quality,
            }
        
        # Create folder
        meeting_folder.mkdir(exist_ok=True)
        
        # Write normalized transcript
        transcript_path = meeting_folder / "transcript.md"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript_text)
        
        # Create v3 manifest
        manifest = self._create_v3_manifest(
            meeting_id=meeting_id,
            meeting_metadata=meeting_metadata,
            microsummary=microsummary,
            original_filename=file_path.name
        )

        # Attach metadata quality assessment
        manifest["metadata_quality"] = metadata_quality
        if metadata_quality["is_bare_transcript"]:
            manifest["hitl"]["reason"] = "bare_transcript"
            manifest["hitl"]["missing_metadata"] = metadata_quality["missing"]
        
        manifest_path = meeting_folder / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✓ Created meeting folder: {meeting_folder}")
        print(f"✓ Wrote transcript.md ({len(transcript_text)} chars)")
        print(f"✓ Wrote manifest.json")
        print(f"✓ Status: ingested")
        
        return {
            "status": "completed",
            "meeting_id": meeting_id,
            "folder_path": str(meeting_folder),
            "transcript_chars": len(transcript_text),
            "microsummary": microsummary
        }
    
    def ingest_folder(self, folder_path: str, dry_run: bool = False) -> Dict:
        """
        Ingest all supported files in a folder
        
        Args:
            folder_path: Path to folder containing transcript files
            dry_run: If True, don't create files, just show what would be done
            
        Returns:
            Dictionary with ingest results for all files
        """
        folder_path = Path(folder_path)
        
        if not folder_path.is_dir():
            raise IngestError(f"Not a directory: {folder_path}")
        
        # Find all supported files
        files_to_ingest = []
        for ext in self.supported_formats:
            files_to_ingest.extend(folder_path.glob(f"*{ext}"))
        
        if not files_to_ingest:
            print(f"No supported files found in {folder_path}")
            print(f"Looking for: {self.supported_formats}")
            return {"status": "no_files", "files_processed": 0}
        
        print(f"Found {len(files_to_ingest)} files to ingest")
        
        results = []
        for file_path in files_to_ingest:
            try:
                result = self.ingest_file(file_path, dry_run)
                results.append(result)
            except IngestError as e:
                print(f"✗ Failed to ingest {file_path}: {e}")
                results.append({
                    "status": "failed",
                    "file": str(file_path),
                    "error": str(e)
                })
        
        successful = [r for r in results if r["status"] in ["completed", "dry_run"]]
        failed = [r for r in results if r["status"] == "failed"]
        
        print(f"\nIngest summary:")
        print(f"✓ Successful: {len(successful)}")
        print(f"✗ Failed: {len(failed)}")
        
        return {
            "status": "completed",
            "files_processed": len(files_to_ingest),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }
    
    def _extract_transcript(self, file_path: Path) -> str:
        """Extract transcript text from various formats"""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.md', '.txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif suffix == '.docx':
            if Document is None:
                raise IngestError("python-docx not available. Install with: pip install python-docx")
            
            doc = Document(file_path)
            text_parts = []
            for paragraph in doc.paragraphs:
                text_parts.append(paragraph.text)
            return '\n'.join(text_parts)
        
        elif suffix == '.jsonl':
            # Convert JSONL to markdown format (speaker: text)
            lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if isinstance(data, dict):
                            # Try common jsonl formats
                            speaker = data.get('speaker', data.get('name', data.get('user', 'Unknown')))
                            text = data.get('text', data.get('content', data.get('message', '')))
                            if text:
                                lines.append(f"{speaker}: {text}")
                        else:
                            # If it's just text, add it as is
                            lines.append(str(data))
                    except json.JSONDecodeError:
                        # If line isn't valid JSON, treat as plain text
                        line = line.strip()
                        if line:
                            lines.append(line)
            
            return '\n'.join(lines)
        
        else:
            raise IngestError(f"Unsupported format: {suffix}")
    
    def _generate_microsummary(self, transcript_text: str) -> str:
        """Generate a one-paragraph microsummary using /zo/ask"""
        # Truncate transcript if too long (to stay within token limits)
        if len(transcript_text) > 8000:
            transcript_text = transcript_text[:8000] + "...\n[Transcript truncated for summarization]"
        
        prompt = f"""Please read this meeting transcript and generate a concise one-paragraph microsummary.

The summary should:
- Be exactly one paragraph (no line breaks)
- Be 2-4 sentences long
- Capture the main topic, key participants, and primary outcomes
- Use clear, professional language
- Focus on what was discussed and decided, not who said what

Transcript:
{transcript_text}

Respond with just the microsummary paragraph, nothing else."""
        
        try:
            response = requests.post(
                self.zo_api_url,
                headers={
                    "authorization": self.zo_token,
                    "content-type": "application/json"
                },
                json={"input": prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("output", "").strip()
                
                # Basic validation
                if len(summary) < 50:
                    return "Meeting summary could not be generated - transcript may be too short or unclear."
                
                # Ensure it's one paragraph
                summary = ' '.join(summary.split('\n'))
                
                return summary
            else:
                print(f"Warning: Failed to generate microsummary (HTTP {response.status_code})")
                return "Meeting summary could not be generated due to API error."
        
        except Exception as e:
            print(f"Warning: Failed to generate microsummary: {e}")
            return "Meeting summary could not be generated."
    
    def _extract_meeting_metadata(self, transcript_text: str, file_path: Path) -> Dict:
        """Extract meeting metadata from transcript and filename"""
        
        # Try to extract date from filename first
        filename = file_path.stem
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}-\d{2}-\d{4})',  # MM-DD-YYYY  
            r'(\d{1,2}/\d{1,2}/\d{4})',  # M/D/YYYY
        ]
        
        extracted_date = None
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1)
                try:
                    if '-' in date_str and len(date_str.split('-')[0]) == 4:
                        extracted_date = date_str  # Already YYYY-MM-DD
                    elif '-' in date_str:
                        # MM-DD-YYYY to YYYY-MM-DD
                        parts = date_str.split('-')
                        extracted_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                    elif '/' in date_str:
                        # M/D/YYYY to YYYY-MM-DD
                        parts = date_str.split('/')
                        extracted_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                    break
                except:
                    continue
        
        # Default to today if no date found
        if not extracted_date:
            extracted_date = datetime.now().strftime('%Y-%m-%d')
        
        # Extract basic info from transcript (simplified - real implementation might use LLM)
        duration = 30  # Default duration in minutes
        
        # Try to estimate duration from transcript length (rough heuristic)
        word_count = len(transcript_text.split())
        if word_count > 0:
            # Rough estimate: 150 words per minute of speech
            estimated_minutes = max(15, min(120, word_count // 150))
            duration = estimated_minutes
        
        # Try to extract title from filename
        title_parts = []
        for part in filename.split('_'):
            # Skip date-like parts
            if not re.match(r'(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})', part):
                # Clean up part (replace hyphens with spaces, title case)
                clean_part = part.replace('-', ' ').replace('_', ' ')
                if clean_part and not clean_part.isdigit():
                    title_parts.append(clean_part)
        
        title = ' '.join(title_parts) if title_parts else "Meeting"
        
        # Convert title to proper case
        title = ' '.join(word.capitalize() for word in title.split())
        
        return {
            "date": extracted_date,
            "time_utc": "12:00:00",  # Default time
            "duration_minutes": duration,
            "title": title,
            "type": "external"  # Default type, will be determined later
        }
    
    def _generate_meeting_id(self, meeting_metadata: Dict, file_path: Path) -> str:
        """Generate a meeting ID in format YYYY-MM-DD_Meeting-Name"""
        date = meeting_metadata["date"]
        title = meeting_metadata["title"]
        
        # Clean title for use in ID
        title_clean = re.sub(r'[^\w\s-]', '', title)  # Remove special chars
        title_clean = re.sub(r'\s+', '-', title_clean.strip())  # Replace spaces with hyphens
        title_clean = title_clean.lower()
        
        # Ensure title isn't too long
        if len(title_clean) > 40:
            title_clean = title_clean[:40].rstrip('-')
        
        # Ensure title isn't empty
        if not title_clean:
            title_clean = file_path.stem.lower()
            title_clean = re.sub(r'[^\w\s-]', '', title_clean)
            title_clean = re.sub(r'\s+', '-', title_clean)[:40]
        
        if not title_clean:
            title_clean = "meeting"
        
        meeting_id = f"{date}_{title_clean}"
        
        # Ensure ID is valid (no double hyphens, etc.)
        meeting_id = re.sub(r'-+', '-', meeting_id)
        meeting_id = meeting_id.strip('-')
        
        return meeting_id
    
    def _assess_metadata_quality(self, transcript_text: str, file_path: Path) -> Dict:
        """Assess whether a transcript has sufficient metadata for pipeline processing.

        Checks for speaker labels, participant context, date/time info, and
        meeting context. Returns a quality report with flags for what's missing.
        Bare transcripts (no speakers, no context) get flagged for Socratic dialogue.
        """
        assessment = {
            "has_speaker_labels": False,
            "has_date_context": False,
            "has_participant_names": False,
            "has_meeting_context": False,
            "speaker_count": 0,
            "speakers_found": [],
            "is_bare_transcript": False,
            "missing": [],
            "confidence": 0.0,
        }

        lines = transcript_text.split("\n")
        speaker_pattern = re.compile(r'^\*\*(.+?):\*\*|^([A-Z][a-zA-Z\s\.]+):\s')
        speakers = set()
        speaker_lines = 0

        for line in lines:
            m = speaker_pattern.match(line.strip())
            if m:
                speaker = (m.group(1) or m.group(2) or "").strip()
                if speaker and len(speaker) < 40:
                    speakers.add(speaker)
                    speaker_lines += 1

        assessment["speakers_found"] = sorted(speakers)
        assessment["speaker_count"] = len(speakers)
        assessment["has_speaker_labels"] = speaker_lines >= 3

        # Check for date context in filename or first 500 chars
        date_patterns = [r'\d{4}-\d{2}-\d{2}', r'\d{1,2}/\d{1,2}/\d{4}', r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}']
        header_text = transcript_text[:500] + " " + file_path.name
        assessment["has_date_context"] = any(re.search(p, header_text, re.IGNORECASE) for p in date_patterns)

        # Check for participant names (in header/frontmatter or filename)
        participant_signals = ["participants:", "attendees:", "present:", "speakers:"]
        assessment["has_participant_names"] = (
            any(s in transcript_text[:1000].lower() for s in participant_signals)
            or len(speakers) >= 2
            or bool(re.search(r'[A-Z][a-z]+\s+(?:x|and|&|with)\s+[A-Z][a-z]+', file_path.stem))
        )

        # Check for meeting context (title, purpose, agenda)
        context_signals = ["agenda", "purpose", "topic", "meeting", "call", "discussion"]
        assessment["has_meeting_context"] = (
            any(s in transcript_text[:1000].lower() for s in context_signals)
            or any(s in file_path.stem.lower() for s in context_signals)
        )

        # Calculate overall confidence
        checks = ["has_speaker_labels", "has_date_context", "has_participant_names", "has_meeting_context"]
        passed = sum(1 for c in checks if assessment[c])
        assessment["confidence"] = round(passed / len(checks), 2)

        # Flag what's missing
        if not assessment["has_speaker_labels"]:
            assessment["missing"].append("speaker_labels")
        if not assessment["has_date_context"]:
            assessment["missing"].append("date")
        if not assessment["has_participant_names"]:
            assessment["missing"].append("participant_names")
        if not assessment["has_meeting_context"]:
            assessment["missing"].append("meeting_context")

        # A transcript is "bare" if it lacks both speakers and participant context
        assessment["is_bare_transcript"] = (
            not assessment["has_speaker_labels"] and not assessment["has_participant_names"]
        )

        return assessment

    def _extract_participants_from_filename(self, filename: str) -> List[str]:
        """Extract participant names from filename using LLM"""
        
        # Clean up filename for parsing
        clean_filename = re.sub(r'\.(md|txt|docx|jsonl)$', '', filename, flags=re.IGNORECASE)
        clean_filename = re.sub(r'-transcript.*$', '', clean_filename, flags=re.IGNORECASE)
        
        prompt = f"""Extract participant names from this meeting filename.

Filename: {clean_filename}

Rules:
- The primary user should be normalized to "V"
- Look for names separated by "_x_", "-x-", "_and_", "_", or "-"
- Common patterns: "YYYY-MM-DD_Name-x-Name" or "Name_x_Name_transcript"
- Ignore date prefixes (2024-01-15, etc.)
- Ignore words like "transcript", "meeting", "call", "zoom"
- Return ONLY a JSON array of names

Examples:
- "2024-01-15_Alex-x-V" → ["Alex", "V"]
- "Jordan_Lee_and_V" → ["Jordan Lee", "V"]
- "John_Smith_x_V_transcript" → ["John Smith", "V"]
- "2026-01-26_Product-Review_Team" → ["Product Review Team", "V"]
- "Sam_x_V_Wisdom_Partners" → ["Sam", "V"]

Respond with ONLY a JSON array like: ["Name1", "Name2"]"""
        
        try:
            response = requests.post(
                self.zo_api_url,
                headers={
                    "authorization": self.zo_token,
                    "content-type": "application/json"
                },
                json={"input": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                output = result.get("output", "[]").strip()
                
                # Handle markdown code blocks
                if output.startswith('```'):
                    lines = output.split('\n')
                    json_lines = [l for l in lines if not l.startswith('```')]
                    output = '\n'.join(json_lines)
                
                participants = json.loads(output)
                if isinstance(participants, list) and len(participants) > 0:
                    return participants
        except Exception as e:
            print(f"Warning: Failed to extract participants from filename: {e}")
        
        # Fallback: extract from filename heuristics
        return self._fallback_participant_extraction(clean_filename)
    
    def _fallback_participant_extraction(self, filename: str) -> List[str]:
        """Fallback heuristic extraction when LLM fails"""
        # Remove dates
        clean = re.sub(r'\d{4}-\d{2}-\d{2}', '', filename)
        clean = re.sub(r'\d{2}/\d{2}/\d{4}', '', clean)
        
        # Split on common separators
        parts = re.split(r'[_\-]', clean)
        parts = [p.strip() for p in parts if p.strip()]
        
        # Filter out common noise words
        noise = ['transcript', 'meeting', 'call', 'zoom', 'recording', 'transcript']
        parts = [p for p in parts if p.lower() not in noise and len(p) > 2]
        
        # Convert title case names
        participants = []
        for part in parts:
            if part.lower() in ['v', 'primaryuser', 'primary_user']:
                participants.append('V')
            else:
                participants.append(part.replace('-', ' ').title())
        
        return participants if participants else ['Unknown']

    def _create_v3_manifest(self, meeting_id: str, meeting_metadata: Dict, microsummary: str, original_filename: str) -> Dict:
        """Create a v3 manifest with initial state and extracted participants"""
        now = datetime.now(timezone.utc).isoformat()
        
        # Extract participants from filename
        extracted_names = self._extract_participants_from_filename(original_filename)
        
        # Build participant objects
        identified_participants = []
        for name in extracted_names:
            if name and name != 'Unknown':
                identified_participants.append({
                    "name": name,
                    "email": None,
                    "crm_id": None,
                    "role": "host" if name == "V" else "attendee",
                    "confidence": 0.8  # LLM extraction confidence
                })
        
        # Calculate confidence based on extraction success
        participant_confidence = 0.8 if len(identified_participants) > 0 else 0.0
        
        manifest = {
            "$schema": "manifest-v3",
            "meeting_id": meeting_id,
            "status": "ingested",
            "status_history": [
                {"status": "raw", "at": now},
                {"status": "ingested", "at": now}
            ],
            "source": {
                "type": "manual",
                "original_filename": original_filename,
                "ingested_at": now
            },
            "meeting": {
                "date": meeting_metadata["date"],
                "time_utc": meeting_metadata["time_utc"],
                "duration_minutes": meeting_metadata["duration_minutes"],
                "title": meeting_metadata["title"],
                "type": meeting_metadata["type"],
                "summary": microsummary
            },
            "participants": {
                "identified": identified_participants,
                "unidentified": [],
                "confidence": participant_confidence
            },
            "calendar_match": None,
            "quality_gate": {
                "passed": participant_confidence > 0.6,
                "checks": {
                    "has_transcript": True,
                    "participants_identified": participant_confidence > 0.6,
                    "meeting_type_determined": False,
                    "no_hitl_pending": participant_confidence > 0.6
                },
                "score": 0.5 + (participant_confidence * 0.25)
            },
            "blocks": {
                "policy": "external_standard",
                "requested": [],
                "generated": [],
                "failed": [],
                "skipped": []
            },
            "hitl": {
                "queue_id": None,
                "reason": None if participant_confidence > 0.6 else "low_participant_confidence",
                "resolved_at": None
            },
            "timestamps": {
                "created_at": now,
                "ingested_at": now,
                "identified_at": None,
                "gated_at": None,
                "processed_at": None,
                "archived_at": None
            }
        }
        
        return manifest

    def _route_to_rejected(
        self,
        file_path: Path,
        reason: str,
        detail: str,
        clean_char_count: int,
        clean_word_count: int,
        duration_minutes,
    ) -> Dict:
        """D4: Route a failed-intake raw file to Personal/Meetings/Rejected/<slug>/."""
        from datetime import datetime as _dt, timezone as _tz
        ensure_rejected_dir()
        slug_base = file_path.stem[:80]
        meeting_slug = f"{_dt.now(_tz.utc).strftime('%Y-%m-%d')}_rejected_{slug_base}"
        # Guarantee uniqueness if retried
        target = REJECTED_DIR / meeting_slug
        i = 1
        while target.exists():
            target = REJECTED_DIR / f"{meeting_slug}_{i}"
            i += 1
        target.mkdir(parents=True, exist_ok=False)
        # Copy the raw source into the folder
        try:
            _shutil.copy2(file_path, target / file_path.name)
        except Exception as e:
            print(f"Warning: could not copy raw source to rejected folder: {e}", file=sys.stderr)
        rejected_manifest = {
            "meeting_id": str(_uuid.uuid4()),
            "status": "rejected_intake",
            "rejection_reason": reason,
            "rejection_detail": detail,
            "created_at": _dt.now(_tz.utc).isoformat(),
            "source_path": str(file_path),
            "clean_char_count": clean_char_count,
            "clean_word_count": clean_word_count,
            "duration_minutes": duration_minutes,
        }
        with open(target / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(rejected_manifest, f, indent=2)
        print(f"[intake-reject] {target.name}: {reason} — {detail}", file=sys.stderr)
        return {
            "status": "rejected",
            "rejection_reason": reason,
            "folder_path": str(target),
            "clean_char_count": clean_char_count,
            "clean_word_count": clean_word_count,
            "duration_minutes": duration_minutes,
        }


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Ingest meeting transcripts and create v3 manifests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s /path/to/transcript.md
    %(prog)s /path/to/inbox_folder --dry-run
    %(prog)s transcript.jsonl
        """
    )
    
    parser.add_argument(
        'path',
        help='File or folder to ingest'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without creating files'
    )
    
    args = parser.parse_args()
    
    try:
        ingestor = TranscriptIngestor()
        
        input_path = Path(args.path)
        
        if input_path.is_file():
            result = ingestor.ingest_file(args.path, args.dry_run)
            print(f"\nResult: {result['status']}")
            if result['status'] == 'completed':
                print(f"Meeting ID: {result['meeting_id']}")
                print(f"Folder: {result['folder_path']}")
        
        elif input_path.is_dir():
            result = ingestor.ingest_folder(args.path, args.dry_run)
            print(f"\nOverall result: {result['status']}")
            
        else:
            print(f"Error: Path not found: {args.path}")
            sys.exit(1)
    
    except IngestError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()