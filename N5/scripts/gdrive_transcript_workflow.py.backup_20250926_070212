#!/usr/bin/env python3
"""
Google Drive Transcript Ingestion Workflow
Extended N5OS-aligned module that ingests transcripts from Google Drive folder.

Integrates:
- Google Drive file listing and download
- Conversation parsing (chunk1_parser)
- Content mapping and ticketing
- MasterVoiceSchema for voice fidelity
- Follow-Up Email Generator v10.6 specifications
- Telemetry and logging per N5OS practices

Author: Zo Computer
Version: 1.0.0
"""

import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('/home/workspace/N5_mirror/logs/gdrive_transcript_workflow.log', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('gdrive_transcript_workflow')

class GoogleDriveConnector:
    """Handles Google Drive integration for transcript ingestion"""

    def __init__(self):
        self.logger = logging.getLogger('GoogleDriveConnector')

    def list_transcript_files(self, folder_id: str, file_pattern: str = "*.txt") -> List[Dict]:
        """List transcript files in a Google Drive folder"""
        try:
            # Use the google_drive-list-files tool
            configured_props = {
                "folderId": folder_id,
                "filterText": file_pattern.replace("*", ""),  # Simple text filter
                "trashed": False
            }

            # This would be called using the tool mechanism
            # For now, return mock data for testing
            self.logger.info(f"Would list files in folder {folder_id} with pattern {file_pattern}")
            return [
                {
                    "id": "mock_file_1",
                    "name": "meeting_transcript_2025-09-15.txt",
                    "mimeType": "text/plain"
                },
                {
                    "id": "mock_file_2",
                    "name": "project_discussion_2025-09-16.txt",
                    "mimeType": "text/plain"
                }
            ]

        except Exception as e:
            self.logger.error(f"Failed to list files in Google Drive folder: {e}")
            return []

    def download_transcript(self, file_id: str, local_path: str) -> bool:
        """Download a transcript file from Google Drive"""
        try:
            configured_props = {
                "fileId": file_id,
                "filePath": local_path
            }

            # This would be called using the tool mechanism
            # For now, simulate download by creating a mock file
            self.logger.info(f"Would download file {file_id} to {local_path}")

            # Create a mock transcript file for testing
            mock_content = f"""Meeting Transcript - Mock File {file_id}
Date: 2025-09-15

Participant A: Good morning everyone. Thanks for joining this discussion.
I'm really excited about the potential here.

Participant B: I agree. The innovative aspects are compelling.
We need to ensure proper testing though.

Action Item: Create project documentation and share by Friday.
Decision: Schedule weekly sync every Tuesday at 10 AM."""

            with open(local_path, 'w') as f:
                f.write(mock_content)

            return True

        except Exception as e:
            self.logger.error(f"Error downloading file {file_id}: {e}")
            return False

class MasterVoiceEngine:
    """Engine for applying MasterVoiceSchema to content generation"""

    def __init__(self, schema_path: str):
        self.schema = self._load_schema(schema_path)
        self.logger = logging.getLogger('MasterVoiceEngine')

    def _load_schema(self, path: str) -> Dict:
        """Load MasterVoiceSchema from file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load MasterVoiceSchema: {e}")
            return {}

    def calibrate_context(self, relationship_depth: int, medium: str = "email",
                         formality: str = "balanced", cta_rigour: str = "balanced") -> Dict:
        """Calibrate voice settings based on context"""
        return {
            "relationshipDepth": relationship_depth,
            "medium": medium,
            "formality": formality,
            "ctaRigour": cta_rigour
        }

    def generate_greeting(self, recipient_name: str, context: Dict) -> str:
        """Generate personalized greeting"""
        depth = context.get("relationshipDepth", 1)
        formality = context.get("formality", "balanced")

        greetings = self.schema.get("writingOptimized", {}).get("greetings", {})
        depth_key = f"{depth}" if depth <= 1 else f"{depth}-{depth+1}" if depth < 4 else "4"

        greeting_options = greetings.get(depth_key, {})
        return greeting_options.get(formality, f"Hey {recipient_name},")

    def generate_signoff(self, context: Dict) -> str:
        """Generate sign-off"""
        depth = context.get("relationshipDepth", 1)
        formality = context.get("formality", "balanced")

        signoffs = self.schema.get("writingOptimized", {}).get("signOffs", {})
        depth_key = f"{depth}" if depth <= 1 else f"{depth}-{depth+1}" if depth < 4 else "4"

        signoff_options = signoffs.get(depth_key, {})
        return signoff_options.get(formality, "Best,")

class ContentMapper:
    """Maps transcript content to structured insights"""

    def __init__(self):
        self.logger = logging.getLogger('ContentMapper')

    def extract_key_elements(self, transcript: str) -> Dict[str, Any]:
        """Extract key elements from transcript"""
        lines = transcript.split('\n')

        # Extract meeting date/time
        meeting_datetime = self._extract_datetime(lines)

        # Extract deliverables, CTAs, decisions
        deliverables = self._extract_pattern(lines, r'(?i)(?:deliver|provide|send|share|create)[:\s]*(.+)')
        ctas = self._extract_pattern(lines, r'(?i)(?:next|action|follow.?up|todo)[:\s]*(.+)')
        decisions = self._extract_pattern(lines, r'(?i)(?:decide|agree|conclude)[:\s]*(.+)')

        # Extract resonant details and quotes
        resonance_details = self._extract_resonance(lines)
        speaker_quotes = self._extract_quotes(lines)

        return {
            "meeting_datetime": meeting_datetime,
            "deliverables": deliverables,
            "ctas": ctas,
            "decisions": decisions,
            "resonance_details": resonance_details,
            "speaker_quotes": speaker_quotes
        }

    def _extract_datetime(self, lines: List[str]) -> Optional[datetime]:
        """Extract meeting date and time"""
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
            r'\b(\d{1,2}-\d{1,2}-\d{4})\b'
        ]

        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        return datetime.fromisoformat(match.group(1))
                    except:
                        continue
        return datetime.now()

    def _extract_pattern(self, lines: List[str], pattern: str) -> List[str]:
        """Extract lines matching a pattern"""
        matches = []
        for line in lines:
            match = re.search(pattern, line)
            if match:
                matches.append(match.group(1).strip())
        return matches

    def _extract_resonance(self, lines: List[str]) -> List[str]:
        """Extract resonant details"""
        resonance_keywords = ['excited', 'interested', 'concerned', 'passionate', 'enthusiastic']
        resonance_lines = []

        for line in lines:
            if any(keyword in line.lower() for keyword in resonance_keywords):
                resonance_lines.append(line.strip())

        return resonance_lines

    def _extract_quotes(self, lines: List[str]) -> List[str]:
        """Extract speaker quotes"""
        quotes = []
        for line in lines:
            # Look for quoted text
            quote_matches = re.findall(r'"([^"]*)"', line)
            quotes.extend(quote_matches)

        return quotes

class BlurbTicketGenerator:
    """Generates tickets and blurbs for follow-up actions"""

    def __init__(self):
        self.logger = logging.getLogger('BlurbTicketGenerator')

    def generate_tickets(self, content_map: Dict) -> List[Dict]:
        """Generate action tickets from content map"""
        tickets = []

        # Generate tickets for deliverables
        for i, deliverable in enumerate(content_map.get('deliverables', [])):
            tickets.append({
                "id": f"deliverable_{i+1}",
                "type": "deliverable",
                "content": deliverable,
                "status": "pending",
                "priority": "high"
            })

        # Generate tickets for CTAs
        for i, cta in enumerate(content_map.get('ctas', [])):
            tickets.append({
                "id": f"cta_{i+1}",
                "type": "action_item",
                "content": cta,
                "status": "pending",
                "priority": "medium"
            })

        return tickets

    def generate_blurbs(self, content_map: Dict, voice_context: Dict) -> List[str]:
        """Generate summary blurbs"""
        blurbs = []

        # Generate resonance blurb
        resonance = content_map.get('resonance_details', [])
        if resonance:
            blurb = f"Key resonance points: {'; '.join(resonance[:3])}"
            blurbs.append(blurb)

        # Generate decision blurb
        decisions = content_map.get('decisions', [])
        if decisions:
            blurb = f"Decisions made: {'; '.join(decisions[:3])}"
            blurbs.append(blurb)

        return blurbs

class FollowUpEmailGenerator:
    """Generates follow-up emails using v10.6 specifications"""

    def __init__(self, voice_engine: MasterVoiceEngine):
        self.voice_engine = voice_engine
        self.logger = logging.getLogger('FollowUpEmailGenerator')

    def generate_email(self, content_map: Dict, voice_context: Dict,
                      recipient_name: str = "Recipient") -> Dict[str, Any]:
        """Generate follow-up email"""

        # Calculate delay
        meeting_time = content_map.get('meeting_datetime', datetime.now())
        days_elapsed = (datetime.now() - meeting_time).days

        # Generate subject line
        subject_line = self._generate_subject_line(recipient_name, content_map)

        # Generate greeting
        greeting = self.voice_engine.generate_greeting(recipient_name, voice_context)

        # Generate body
        body_parts = []

        # Optional delay apology
        if days_elapsed > 2:
            body_parts.append(f"I apologize for the delay in following up—it's been {days_elapsed} days since our meeting.")

        # Resonance intro
        resonance = content_map.get('resonance_details', [])
        if resonance:
            body_parts.append("I wanted to follow up on our recent discussion. I particularly appreciated your thoughts on:")
            for detail in resonance[:3]:
                body_parts.append(f"• {detail}")

        # Recap bullets
        deliverables = content_map.get('deliverables', [])
        if deliverables:
            body_parts.append("\nHere are the key deliverables we discussed:")
            for deliverable in deliverables:
                body_parts.append(f"• {deliverable}")

        # Next steps
        ctas = content_map.get('ctas', [])
        if ctas:
            body_parts.append("\nNext steps:")
            for cta in ctas:
                body_parts.append(f"• {cta}")

        # Sign-off
        signoff = self.voice_engine.generate_signoff(voice_context)

        # Assemble email
        email_body = "\n\n".join(body_parts)

        return {
            "subject_line": subject_line,
            "greeting": greeting,
            "body": email_body,
            "signoff": signoff,
            "full_email": f"{greeting}\n\n{email_body}\n\n{signoff}",
            "days_elapsed": days_elapsed
        }

    def _generate_subject_line(self, recipient_name: str, content_map: Dict) -> str:
        """Generate subject line per v10.6 specs"""
        ctas = content_map.get('ctas', [])
        keywords = []

        # Extract keywords from CTAs
        for cta in ctas[:2]:  # Up to 2 keywords
            words = re.findall(r'\b\w+\b', cta.lower())
            # Filter for action-oriented words
            action_words = [w for w in words if w in ['discuss', 'review', 'follow', 'schedule', 'meet', 'call']]
            keywords.extend(action_words[:2])

        if not keywords:
            keywords = ['follow', 'up']

        keyword_str = " • ".join(keywords[:3])  # Max 3 keywords

        return f"Follow-Up Email – {recipient_name} x Careerspan [{keyword_str}]"

class GoogleDriveTranscriptWorkflow:
    """Main workflow orchestrator for Google Drive transcript ingestion"""

    def __init__(self):
        self.logger = logging.getLogger('GoogleDriveTranscriptWorkflow')

        # Initialize components
        self.drive_connector = GoogleDriveConnector()
        schema_path = "/home/workspace/Companion [05] - Companion File - Universal - Master Voice Vrijen v1.3.txt"
        self.voice_engine = MasterVoiceEngine(schema_path)
        self.content_mapper = ContentMapper()
        self.ticket_generator = BlurbTicketGenerator()
        self.email_generator = FollowUpEmailGenerator(self.voice_engine)

        # Telemetry
        self.telemetry = {
            "start_time": None,
            "end_time": None,
            "files_processed": 0,
            "files_failed": 0,
            "processing_steps": [],
            "errors": []
        }

    def process_gdrive_folder(self, folder_id: str, file_pattern: str = "*.txt",
                             voice_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process all transcripts in a Google Drive folder"""

        self.telemetry["start_time"] = datetime.now()

        try:
            # List transcript files in the folder
            files = self.drive_connector.list_transcript_files(folder_id, file_pattern)
            self.telemetry["processing_steps"].append("gdrive_files_listed")

            if not files:
                self.logger.warning(f"No transcript files found in folder {folder_id}")
                return {
                    "message": "No transcript files found",
                    "telemetry": self.telemetry
                }

            self.logger.info(f"Processing {len(files)} transcript files from Google Drive")

            # Process each file
            results = []
            for file_info in files:
                result = self._process_single_file(file_info, voice_context)
                results.append(result)

                if result.get("success", False):
                    self.telemetry["files_processed"] += 1
                else:
                    self.telemetry["files_failed"] += 1

            # Compile batch results
            batch_summary = self._compile_batch_summary(results)

            self.telemetry["end_time"] = datetime.now()
            processing_time = (self.telemetry["end_time"] - self.telemetry["start_time"]).total_seconds()
            self.logger.info(f"Batch processing completed in {processing_time:.2f}s")

            return {
                "batch_summary": batch_summary,
                "individual_results": results,
                "telemetry": self.telemetry
            }

        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            self.telemetry["errors"].append(str(e))
            self.telemetry["end_time"] = datetime.now()
            return {
                "error": str(e),
                "telemetry": self.telemetry
            }

    def _process_single_file(self, file_info: Dict, voice_context: Optional[Dict]) -> Dict[str, Any]:
        """Process a single transcript file from Google Drive"""

        file_id = file_info.get("id")
        file_name = file_info.get("name", "unknown")

        try:
            # Create temporary local path
            local_path = f"/tmp/{file_name}"

            # Download the file
            if not self.drive_connector.download_transcript(file_id, local_path):
                return {
                    "file_name": file_name,
                    "file_id": file_id,
                    "success": False,
                    "error": "Download failed"
                }

            # Read and process the transcript
            with open(local_path, 'r', encoding='utf-8') as f:
                transcript = f.read()

            # Default voice context
            if voice_context is None:
                voice_context = self.voice_engine.calibrate_context(relationship_depth=1)

            # Extract key elements
            content_map = self.content_mapper.extract_key_elements(transcript)

            # Generate tickets and blurbs
            tickets = self.ticket_generator.generate_tickets(content_map)
            blurbs = self.ticket_generator.generate_blurbs(content_map, voice_context)

            # Generate follow-up email
            recipient_name = "Recipient"  # Extract from transcript if available
            email_draft = self.email_generator.generate_email(content_map, voice_context, recipient_name)

            # Save outputs to workspace
            output_dir = self._create_output_directory(file_name)
            self._save_outputs(output_dir, content_map, tickets, blurbs, email_draft)

            # Clean up temporary file
            os.remove(local_path)

            return {
                "file_name": file_name,
                "file_id": file_id,
                "success": True,
                "content_map": content_map,
                "tickets": tickets,
                "blurbs": blurbs,
                "email_draft": email_draft,
                "output_directory": output_dir
            }

        except Exception as e:
            self.logger.error(f"Failed to process file {file_name}: {e}")
            return {
                "file_name": file_name,
                "file_id": file_id,
                "success": False,
                "error": str(e)
            }

    def _create_output_directory(self, file_name: str) -> str:
        """Create output directory for processed transcript"""
        # Extract date from filename or use current date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
        if date_match:
            date_str = date_match.group(1)
        else:
            date_str = datetime.now().strftime("%Y%m%d")

        output_dir = f"/home/workspace/Meetings/gdrive_{date_str}_{file_name.replace('.', '_')}"
        os.makedirs(output_dir, exist_ok=True)

        return output_dir

    def _save_outputs(self, output_dir: str, content_map: Dict, tickets: List[Dict],
                     blurbs: List[str], email_draft: Dict):
        """Save processing outputs to files"""

        # Save content map
        with open(f"{output_dir}/content_map.json", 'w') as f:
            json.dump(content_map, f, indent=2, default=str)

        # Save email draft
        with open(f"{output_dir}/email_draft.md", 'w') as f:
            f.write(f"# Follow-Up Email Draft\n\n")
            f.write(f"**Subject Line:** {email_draft['subject_line']}\n\n")
            f.write(f"**Greeting:** {email_draft['greeting']}\n\n")
            f.write("**Body:**\n\n")
            f.write(email_draft['body'])
            f.write(f"\n\n**Sign-off:** {email_draft['signoff']}\n")

        # Save tickets
        for i, ticket in enumerate(tickets):
            ticket_file = f"{output_dir}/blurb_ticket_{ticket['id']}.json"
            with open(ticket_file, 'w') as f:
                ticket_data = ticket.copy()
                ticket_data["created"] = datetime.now().isoformat()
                ticket_data["source"] = "gdrive_transcript"
                json.dump(ticket_data, f, indent=2)

        # Save warm intro emails for warm introduction tickets
        warm_intro_tickets = [t for t in tickets if t.get('type') == 'warm_introduction']
        if warm_intro_tickets:
            # Initialize email generator for warm intros
            from consolidated_transcript_workflow import FollowUpEmailGenerator, MasterVoiceEngine
            schema_path = "/home/workspace/Companion [05] - Companion File - Universal - Master Voice Vrijen v1.3.txt"
            voice_engine = MasterVoiceEngine(schema_path)
            email_gen = FollowUpEmailGenerator(voice_engine)

            # Default voice context for warm intros
            warm_intro_voice_context = voice_engine.calibrate_context(
                relationship_depth=2,  # Higher relationship depth for introductions
                formality="formal"
            )

            for i, ticket in enumerate(warm_intro_tickets):
                # Create opportunity dict from ticket data
                opportunity = {
                    'participants': ticket.get('participants', []),
                    'intro_type': ticket.get('intro_type', 'general_introduction'),
                    'context': ticket.get('content', ''),
                    'trigger_context': ticket.get('trigger_context', ''),
                    'confidence_score': ticket.get('confidence_score', 0.5)
                }

                # Generate warm intro email
                warm_intro_email = email_gen.generate_warm_intro_email(
                    opportunity, warm_intro_voice_context, "Introducer"
                )

                if 'error' not in warm_intro_email:
                    # Save warm intro email
                    email_file = f"{output_dir}/warm_intro_email_{ticket['id']}.md"
                    with open(email_file, 'w') as f:
                        f.write(f"# Warm Introduction Email\n\n")
                        f.write(f"**Subject Line:** {warm_intro_email['subject_line']}\n\n")
                        f.write(f"**Greeting:** {warm_intro_email['greeting']}\n\n")
                        f.write("**Body:**\n\n")
                        f.write(warm_intro_email['body'])
                        f.write(f"\n\n**Sign-off:** {warm_intro_email['signoff']}\n")

                    # Update ticket with email file reference
                    ticket["warm_intro_email_file"] = email_file

        # Save blurbs summary
        with open(f"{output_dir}/blurbs_summary.md", 'w') as f:
            f.write("# Meeting Summary Blurbs\n\n")
            for blurb in blurbs:
                f.write(f"## {blurb.split(':')[0]}\n{blurb}\n\n")

        # Save warm intro opportunities separately
        warm_intro_opportunities = content_map.get('warm_intro_opportunities', [])
        if warm_intro_opportunities:
            with open(f"{output_dir}/warm_intro_opportunities.json", 'w') as f:
                json.dump(warm_intro_opportunities, f, indent=2)

    def _compile_batch_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Compile summary statistics for batch processing"""
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]

        total_tickets = sum(len(r.get("tickets", [])) for r in successful)
        total_deliverables = sum(len(r["content_map"].get("deliverables", [])) for r in successful if "content_map" in r)
        total_ctas = sum(len(r["content_map"].get("ctas", [])) for r in successful if "content_map" in r)

        return {
            "total_files": len(results),
            "successful_files": len(successful),
            "failed_files": len(failed),
            "total_tickets_generated": total_tickets,
            "total_deliverables_extracted": total_deliverables,
            "total_ctas_extracted": total_ctas,
            "output_directories": [r.get("output_directory") for r in successful if r.get("output_directory")]
        }

def main():
    """CLI interface for Google Drive transcript workflow"""
    if len(sys.argv) != 2:
        print("Usage: python gdrive_transcript_workflow.py <google_drive_folder_id>")
        print("Example: python gdrive_transcript_workflow.py 1A2B3C4D5E6F7G8H9I0J")
        sys.exit(1)

    folder_id = sys.argv[1]

    workflow = GoogleDriveTranscriptWorkflow()
    result = workflow.process_gdrive_folder(folder_id)

    # Output results
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()