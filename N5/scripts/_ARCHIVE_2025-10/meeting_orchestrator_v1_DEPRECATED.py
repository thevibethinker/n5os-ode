#!/usr/bin/env python3
"""
Meeting Processing Orchestrator v2.0
Transforms meeting transcripts into actionable intelligence.
"""
import asyncio
import json
import logging
import os
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Careerspan" / "Meetings"
LISTS_DIR = WORKSPACE / "N5" / "lists"
LOGS_DIR = WORKSPACE / "N5" / "logs" / "meeting-process"
DB_PATH = WORKSPACE / "Knowledge" / "crm" / "crm.db"

# Ensure directories exist
MEETINGS_DIR.mkdir(parents=True, exist_ok=True)
LISTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_db_conn():
    """Get database connection with Row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def upsert_individual(conn, individual):
    """
    Insert or update individual record.
    Returns individual_id.
    
    Args:
        individual: dict with keys: full_name, email, title, company,
                   primary_category, status, tags, source_type, notes,
                   markdown_file_path, etc.
    """
    cursor = conn.cursor()
    
    # Try to find existing by email or name
    if individual.get('email'):
        cursor.execute("SELECT id FROM individuals WHERE email = ?", 
                      (individual['email'],))
    else:
        cursor.execute("SELECT id FROM individuals WHERE full_name = ?", 
                      (individual['full_name'],))
    
    row = cursor.fetchone()
    
    if row:
        # Update existing
        individual_id = row['id']
        cursor.execute("""
            UPDATE individuals SET
                title = ?, company = ?, email = ?,
                primary_category = ?, status = ?, tags = ?,
                notes = ?, markdown_file_path = ?
            WHERE id = ?
        """, (
            individual.get('title'),
            individual.get('company'),
            individual.get('email'),
            individual.get('primary_category', 'other'),
            individual.get('status', 'prospect'),
            individual.get('tags'),
            individual.get('notes'),
            individual.get('markdown_file_path'),
            individual_id
        ))
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO individuals (
                full_name, title, company, email, 
                primary_category, status, tags, source_type,
                notes, markdown_file_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            individual['full_name'],
            individual.get('title'),
            individual.get('company'),
            individual.get('email'),
            individual.get('primary_category', 'other'),
            individual.get('status', 'prospect'),
            individual.get('tags'),
            individual.get('source_type'),
            individual.get('notes'),
            individual.get('markdown_file_path')
        ))
        individual_id = cursor.lastrowid
    
    return individual_id

def insert_interaction(conn, individual_id, interaction):
    """
    Insert interaction record.
    
    Args:
        individual_id: FK to individuals table
        interaction: dict with keys: interaction_type, interaction_date,
                    subject, summary, notes_file_path
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interactions (
            individual_id, interaction_type, interaction_date,
            subject, summary, notes_file_path
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        individual_id,
        interaction['interaction_type'],
        interaction['interaction_date'],
        interaction.get('subject'),
        interaction.get('summary'),
        interaction.get('notes_file_path')
    ))
    return cursor.lastrowid


class MeetingOrchestrator:
    """Orchestrates meeting processing pipeline."""
    
    def __init__(
        self,
        transcript_source: str,
        meeting_types: List[str],
        stakeholder_types: List[str],
        mode: str = "full",
        output_format: str = "markdown"
    ):
        self.transcript_source = transcript_source
        self.meeting_types = meeting_types
        self.stakeholder_types = stakeholder_types
        self.mode = mode
        self.output_format = output_format
        
        self.meeting_id = self._generate_meeting_id()
        self.metadata: Dict[str, Any] = {}
        self.output_dir: Optional[Path] = None
        self.processing_start = datetime.now(timezone.utc)
        self.errors: List[Dict[str, str]] = []
        
    def _generate_meeting_id(self) -> str:
        """Generate unique 6-character meeting ID."""
        return uuid.uuid4().hex[:6]
    
    async def process(self) -> Path:
        """Main processing pipeline."""
        try:
            logger.info(f"Starting meeting processing (ID: {self.meeting_id})")
            
            # Step 1: Fetch transcript
            transcript_content, transcript_meta = await self._fetch_transcript()
            self.transcript_content = transcript_content  # store for downstream
            logger.info(f"Transcript fetched: {transcript_meta['size_bytes']} bytes, {transcript_meta['line_count']} lines")
            
            # Step 2: Extract meeting metadata
            meeting_info = await self._extract_meeting_info(transcript_content)
            self.meeting_info = meeting_info  # store for downstream
            logger.info(f"Meeting info extracted: {meeting_info['participants_count']} participants")
            
            # Step 3: Create output directory
            self.output_dir = await self._create_output_directory(meeting_info)
            logger.info(f"Output directory: {self.output_dir}")

            # NEW STEP: Update CRM
            await self._update_crm_database(meeting_info)
            
            # Step 4: Save transcript
            await self._save_transcript(transcript_content, self.output_dir)
            
            # Step 5: Lookup meeting history
            meeting_history = await self._lookup_meeting_history(meeting_info)
            logger.info(f"Found {len(meeting_history)} previous meetings with stakeholder")
            
            # Step 6: Fetch email history
            email_history = await self._fetch_email_history(meeting_info)
            email_found = email_history is not None
            logger.info(f"Email history: {'found' if email_found else 'not found'}")
            
            # Step 7: Generate blocks
            blocks_generated = await self._generate_blocks(
                transcript_content,
                meeting_info,
                meeting_history,
                email_history
            )
            logger.info(f"Generated {len(blocks_generated)} blocks")
            
            # Step 8: Generate dashboard
            await self._generate_dashboard(blocks_generated, meeting_info)
            logger.info("Dashboard generated")

            # Step 9: Generate Deliverables
            await self._generate_deliverables_step()
            logger.info("Deliverable generation complete")

            # Step 10: Integrate with lists
            await self._integrate_lists(blocks_generated)
            logger.info("Lists integration complete")
            
            # Step 11: Save metadata
            await self._save_metadata(
                meeting_info,
                transcript_meta,
                meeting_history,
                email_found,
                blocks_generated
            )
            logger.info("Metadata saved")
            
            processing_duration = (datetime.now(timezone.utc) - self.processing_start).total_seconds()
            logger.info(f"Processing complete in {processing_duration:.1f}s: {self.output_dir}")
            
            return self.output_dir
            
        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            self._log_error("orchestrator", str(e), "critical")
            raise
    
    async def _update_crm_database(self, meeting_info: Dict[str, Any]):
        """Update the CRM database with meeting attendees."""
        if not self.output_dir:
            logger.warning("Output directory not set, skipping CRM database update.")
            return

        conn = get_db_conn()
        try:
            participants = meeting_info.get("participants", [])
            if not participants:
                logger.info("No participants found in meeting info to update CRM.")
                return

            for participant_name in participants:
                # Filter out own name
                if "vrijen" in participant_name.lower():
                    continue

                individual_data = {
                    'full_name': participant_name,
                    'status': 'active'
                }

                individual_id = upsert_individual(conn, individual_data)

                interaction_data = {
                    'interaction_type': 'meeting',
                    'interaction_date': meeting_info.get("date"),
                    'subject': f"Meeting: {meeting_info.get('stakeholder_primary', 'General')}",
                    'summary': f"Attended meeting on {meeting_info.get('date')}. Meeting type: {', '.join(self.meeting_types)}",
                    'notes_file_path': str(self.output_dir.relative_to(WORKSPACE))
                }
                insert_interaction(conn, individual_id, interaction_data)

            conn.commit()
            logger.info(f"Successfully updated CRM for {len(participants)} participants.")

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update CRM database: {e}", exc_info=True)
            self._log_error("crm_integrator", str(e), "warning") # Non-critical
        finally:
            conn.close()
    
    async def _generate_deliverables_step(self):
        """Initializes and runs the DeliverableOrchestrator."""
        logger.info("Kicking off deliverable generation...")
        try:
            from deliverable_orchestrator import DeliverableOrchestrator
            
            # Prepare context defensively (attributes may not exist if earlier steps failed)
            transcript_content = getattr(self, 'transcript_content', '')
            meeting_info = getattr(self, 'meeting_info', {})

            deliverable_context = {
                "transcript_content": transcript_content,
                "meeting_info": meeting_info,
                "meeting_types": self.meeting_types,
                "stakeholder_types": self.stakeholder_types,
                "output_dir": str(self.output_dir / "DELIVERABLES")
            }

            orchestrator = DeliverableOrchestrator(deliverable_context)
            generated_deliverables = await orchestrator.generate_deliverables()

            if generated_deliverables:
                logger.info(f"Successfully generated {len(generated_deliverables)} deliverables.")
                self.metadata.setdefault("deliverables", []).extend(generated_deliverables)
            else:
                logger.info("No deliverables were generated for this meeting.")

        except Exception as e:
            logger.error(f"Deliverable generation step failed: {e}", exc_info=True)
            self._log_error("deliverable_orchestrator", str(e), "error")
            # This is a non-critical step, so we log the error but don't raise it further

    async def _fetch_transcript(self) -> Tuple[str, Dict[str, Any]]:
        """Fetch transcript from source."""
        # Check if Google Drive ID
        if len(self.transcript_source) > 20 and '/' not in self.transcript_source:
            # Google Drive file ID
            logger.info(f"Fetching from Google Drive: {self.transcript_source}")
            # TODO: Implement Google Drive fetch
            raise NotImplementedError("Google Drive fetch not yet implemented")
        
        # Local file path
        transcript_path = Path(self.transcript_source)
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {self.transcript_source}")
        
        content = transcript_path.read_text(encoding='utf-8')
        
        # Calculate metadata
        sha256 = hashlib.sha256(content.encode()).hexdigest()
        size_bytes = len(content.encode())
        line_count = len(content.splitlines())
        
        return content, {
            "type": "local_file",
            "identifier": str(transcript_path),
            "sha256": sha256,
            "size_bytes": size_bytes,
            "line_count": line_count
        }
    
    async def _extract_meeting_info(self, transcript: str) -> Dict[str, Any]:
        """Extract meeting metadata from transcript."""
        from blocks.meeting_info_extractor import extract_meeting_info
        
        try:
            info = await extract_meeting_info(transcript)
            return info
        except Exception as e:
            self._log_error("meeting_info_extractor", str(e), "error")
            # Return defaults
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "participants": [],
                "participants_count": 0,
                "duration_minutes": 0,
                "stakeholder_primary": self.stakeholder_types[0] if self.stakeholder_types else "unknown"
            }
    
    async def _create_output_directory(self, meeting_info: Dict[str, Any]) -> Path:
        """Create output directory with structured naming."""
        date = meeting_info.get("date", datetime.now().strftime("%Y-%m-%d"))
        time = meeting_info.get("time", datetime.now().strftime("%H%M")).replace(":", "")
        meeting_type = self.meeting_types[0] if self.meeting_types else "general"
        stakeholder = meeting_info.get("stakeholder_primary", "unknown").replace(" ", "-").lower()
        
        folder_name = f"{date}_{time}_{meeting_type}_{stakeholder}"
        output_dir = MEETINGS_DIR / folder_name
        
        # Handle duplicates
        if output_dir.exists():
            folder_name = f"{folder_name}_{self.meeting_id[:4]}"
            output_dir = MEETINGS_DIR / folder_name
        
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "OUTPUTS").mkdir(exist_ok=True)
        (output_dir / "INTELLIGENCE").mkdir(exist_ok=True)
        
        return output_dir
    
    async def _save_transcript(self, content: str, output_dir: Path):
        """Save transcript to output directory."""
        transcript_path = output_dir / "transcript.txt"
        transcript_path.write_text(content, encoding='utf-8')
    
    async def _lookup_meeting_history(self, meeting_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find previous meetings with stakeholder."""
        from blocks.meeting_history_lookup import lookup_meeting_history
        
        try:
            stakeholder = meeting_info.get("stakeholder_primary", "")
            history = await lookup_meeting_history(stakeholder)
            return history
        except Exception as e:
            self._log_error("meeting_history_lookup", str(e), "warning")
            return []
    
    async def _fetch_email_history(self, meeting_info: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Fetch email history with stakeholders."""
        from blocks.email_history_fetcher import fetch_email_history
        
        try:
            participants = meeting_info.get("participants", [])
            # Filter out your own name
            external_participants = [p for p in participants if "vrijen" not in p.lower()]
            
            if not external_participants:
                return None
            
            history = await fetch_email_history(external_participants)
            return history
        except Exception as e:
            self._log_error("email_history_fetcher", str(e), "warning")
            return None
    
    async def _generate_blocks(
        self,
        transcript: str,
        meeting_info: Dict[str, Any],
        meeting_history: List[Dict[str, Any]],
        email_history: Optional[List[Dict[str, Any]]]
    ) -> List[str]:
        """Generate all required blocks based on meeting type and mode."""
        blocks_generated = []
        
        # Determine which blocks to generate based on mode
        if self.mode == "quick":
            blocks_to_generate = ["action_items"]
        elif self.mode == "essential":
            blocks_to_generate = ["follow_up_email", "action_items", "decisions"]
        else:  # full
            blocks_to_generate = [
                "follow_up_email",
                "action_items",
                "decisions",
                "key_insights",
                "stakeholder_profile",
                # Conditional blocks
                "warm_intros",
                "risks",
                "opportunities",
                "user_research",
                "competitive_intel",
            ]
            
            # Add category-specific blocks
            if "sales" in self.meeting_types:
                blocks_to_generate.append("deal_intelligence")
            if any(t in self.meeting_types for t in ["coaching", "networking"]):
                blocks_to_generate.append("career_insights")
            if "fundraising" in self.meeting_types:
                blocks_to_generate.append("investor_thesis")
            if "community_partnerships" in self.meeting_types:
                blocks_to_generate.append("partnership_scope")
        
        # Generate each block
        for block_name in blocks_to_generate:
            try:
                success = await self._generate_single_block(
                    block_name,
                    transcript,
                    meeting_info,
                    meeting_history,
                    email_history
                )
                if success:
                    blocks_generated.append(block_name)
            except Exception as e:
                logger.error(f"Failed to generate block '{block_name}': {e}")
                self._log_error(block_name, str(e), "error")
        
        return blocks_generated
    
    async def _generate_single_block(
        self,
        block_name: str,
        transcript: str,
        meeting_info: Dict[str, Any],
        meeting_history: List[Dict[str, Any]],
        email_history: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Generate a single block."""
        logger.info(f"Generating block: {block_name}")
        
        # Import block generator
        try:
            if block_name == "follow_up_email":
                from blocks.follow_up_email_generator import generate_follow_up_email
                await generate_follow_up_email(
                    transcript, meeting_info, email_history, meeting_history,
                    self.meeting_types, self.output_dir
                )
            elif block_name == "action_items":
                from blocks.action_items_extractor import generate_action_items
                await generate_action_items(transcript, meeting_info, self.output_dir)
            elif block_name == "decisions":
                from blocks.decisions_extractor import generate_decisions
                await generate_decisions(transcript, meeting_info, self.output_dir)
            elif block_name == "key_insights":
                from blocks.key_insights_extractor import generate_key_insights
                await generate_key_insights(transcript, meeting_info, self.output_dir)
            elif block_name == "stakeholder_profile":
                from blocks.stakeholder_profile_generator import generate_stakeholder_profile
                await generate_stakeholder_profile(
                    transcript, meeting_info, meeting_history, self.meeting_types, self.output_dir
                )
            elif block_name == "warm_intros":
                from blocks.warm_intro_detector import generate_warm_intros
                generated = await generate_warm_intros(transcript, meeting_info, self.output_dir)
                return generated > 0  # Only count as success if intros found
            elif block_name == "risks":
                from blocks.risks_detector import generate_risks
                generated = await generate_risks(transcript, meeting_info, self.output_dir)
                return generated > 0
            elif block_name == "opportunities":
                from blocks.opportunities_detector import generate_opportunities
                generated = await generate_opportunities(transcript, meeting_info, self.output_dir)
                return generated > 0
            elif block_name == "user_research":
                from blocks.user_research_extractor import generate_user_research
                generated = await generate_user_research(transcript, meeting_info, self.output_dir)
                return generated > 0
            elif block_name == "competitive_intel":
                from blocks.competitive_intel_extractor import generate_competitive_intel
                generated = await generate_competitive_intel(transcript, meeting_info, self.output_dir)
                return generated > 0
            elif block_name == "deal_intelligence":
                from blocks.deal_intelligence_generator import generate_deal_intelligence
                await generate_deal_intelligence(transcript, meeting_info, self.output_dir)
            elif block_name == "career_insights":
                from blocks.career_insights_generator import generate_career_insights
                await generate_career_insights(transcript, meeting_info, self.output_dir)
            elif block_name == "investor_thesis":
                from blocks.investor_thesis_generator import generate_investor_thesis
                await generate_investor_thesis(transcript, meeting_info, self.output_dir)
            elif block_name == "partnership_scope":
                from blocks.partnership_scope_generator import generate_partnership_scope
                await generate_partnership_scope(transcript, meeting_info, self.output_dir)
            else:
                logger.warning(f"Unknown block type: {block_name}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating {block_name}: {e}")
            raise
    
    async def _generate_dashboard(self, blocks_generated: List[str], meeting_info: Dict[str, Any]):
        """Generate REVIEW_FIRST.md dashboard."""
        from blocks.dashboard_generator import generate_dashboard
        
        try:
            await generate_dashboard(
                self.meeting_id,
                meeting_info,
                blocks_generated,
                self.metadata,
                self.output_dir
            )
        except Exception as e:
            self._log_error("dashboard_generator", str(e), "error")
            # Non-critical, continue
    
    async def _integrate_lists(self, blocks_generated: List[str]):
        """Integrate generated blocks into N5 lists."""
        from blocks.list_integrator import integrate_with_lists
        
        try:
            await integrate_with_lists(
                self.output_dir,
                blocks_generated,
                self.meeting_id,
                self.metadata
            )
        except Exception as e:
            self._log_error("list_integrator", str(e), "warning")
            # Non-critical, continue
    
    async def _save_metadata(
        self,
        meeting_info: Dict[str, Any],
        transcript_meta: Dict[str, Any],
        meeting_history: List[Dict[str, Any]],
        email_history_found: bool,
        blocks_generated: List[str]
    ):
        """Save structured metadata."""
        processing_duration = (datetime.now(timezone.utc) - self.processing_start).total_seconds()
        
        self.metadata = {
            "meeting_id": self.meeting_id,
            "date": meeting_info.get("date"),
            "time": meeting_info.get("time"),
            "timezone": "America/New_York",
            "meeting_type": self.meeting_types,
            "stakeholder_primary": meeting_info.get("stakeholder_primary"),
            "stakeholders_all": meeting_info.get("participants", []),
            "stakeholder_types": self.stakeholder_types,
            "organization": meeting_info.get("organization"),
            "participants_count": meeting_info.get("participants_count", 0),
            "duration_minutes": meeting_info.get("duration_minutes", 0),
            "previous_meetings_count": len(meeting_history),
            "previous_meeting_ids": [m.get("meeting_id") for m in meeting_history],
            "email_history_found": email_history_found,
            "intelligence": {
                # Will be populated by blocks
                "risks_count": 0,
                "opportunities_count": 0,
                "warm_intros_count": 0,
                "decisions_count": 0,
                "action_items_count": 0,
                "insights_count": 0
            },
            "processing": {
                "version": "2.0.0",
                "mode": self.mode,
                "duration_seconds": int(processing_duration),
                "blocks_generated": len(blocks_generated),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "errors": self.errors if self.errors else []
            },
            "transcript_source": transcript_meta,
            "approval": {
                "status": "pending_review"
            }
        }
        
        metadata_path = self.output_dir / "_metadata.json"
        metadata_path.write_text(json.dumps(self.metadata, indent=2), encoding='utf-8')
    
    def _log_error(self, component: str, message: str, severity: str):
        """Log an error to internal tracking."""
        self.errors.append({
            "component": component,
            "message": message,
            "severity": severity
        })


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process meeting transcript")
    parser.add_argument("transcript_source", help="Transcript source (file path or Google Drive ID)")
    parser.add_argument("--type", required=True, help="Meeting type(s), comma-separated")
    parser.add_argument("--stakeholder", required=True, help="Stakeholder type(s), comma-separated")
    parser.add_argument("--mode", default="full", choices=["full", "essential", "quick"])
    parser.add_argument("--output-format", default="markdown", choices=["markdown", "gmail-draft", "json"])
    
    args = parser.parse_args()
    
    meeting_types = [t.strip() for t in args.type.split(",")]
    stakeholder_types = [s.strip() for s in args.stakeholder.split(",")]
    
    orchestrator = MeetingOrchestrator(
        transcript_source=args.transcript_source,
        meeting_types=meeting_types,
        stakeholder_types=stakeholder_types,
        mode=args.mode,
        output_format=args.output_format
    )
    
    output_dir = await orchestrator.process()
    print(f"\n✅ Processing complete: {output_dir}")
    print(f"📊 Review: {output_dir / 'REVIEW_FIRST.md'}")


if __name__ == "__main__":
    asyncio.run(main())
