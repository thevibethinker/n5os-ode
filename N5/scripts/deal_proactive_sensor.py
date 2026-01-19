#!/usr/bin/env python3
"""
Proactive Deal Sensor — Worker 6 (Proactive Sensing)

Uses unified n5_core.db database with people table and deal_roles junction.

Purpose:
- Detect potential NEW deals/contacts that don't exist in the database
- Broker signals: "I can introduce you to...", "Let me connect you with..."
- Deal signals: Company mentioned in acquisition/partnership context
- Leadership signals: Executive at known target company
- Send SMS approval requests to V before creating
- Process approval responses (Y/N/Info)

CLI:
  # Analyze text for new entity signals
  python3 deal_proactive_sensor.py --text "John can intro us to Workday CEO" --source meeting

  # Process approval response
  python3 deal_proactive_sensor.py --approval "Y" --pending-id abc123
  
  # List pending approvals
  python3 deal_proactive_sensor.py --list-pending
  
  # Dry run (no SMS sent, no DB writes)
  python3 deal_proactive_sensor.py --text "..." --source email --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from db_paths import get_db_connection, N5_CORE_DB
from deal_llm_prompts import NEW_DEAL_DETECTION_PROMPT


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class DetectedEntity:
    """An entity detected as potentially new to the database."""
    entity_type: str  # 'broker', 'deal', 'leadership'
    name: str
    company: Optional[str]
    context: str
    signal_strength: str  # 'strong', 'medium', 'weak'
    source: str  # 'meeting', 'email', 'sms', 'kondo'
    source_text: str
    recommended_action: str  # 'create_deal', 'track_contact', 'follow_up', 'ignore'
    pipeline: Optional[str] = None  # 'careerspan', 'zo'


@dataclass
class ApprovalRequest:
    """A pending approval request for a detected entity."""
    id: str
    entity_type: str
    name: str
    company: Optional[str]
    context: str
    source_text: str
    pipeline: Optional[str]
    status: str  # 'pending', 'approved', 'declined', 'info_sent'
    created_at: str


@dataclass
class ApprovalResult:
    """Result of processing an approval response."""
    success: bool
    action: str  # 'created', 'declined', 'info', 'not_found', 'error'
    message: str
    created_id: Optional[str] = None


@dataclass
class SensorResult:
    """Result of running the proactive sensor on text."""
    entities_detected: List[DetectedEntity]
    entities_queued: int
    sms_formatted: List[str]
    dry_run: bool


# =============================================================================
# Detection Patterns
# =============================================================================

BROKER_PATTERNS = [
    r"(?:can|will|let me)\s+(?:introduce|connect|intro)\s+(?:you\s+)?(?:to|with)",
    r"know\s+(?:someone|people|folks)\s+(?:at|from|who)",
    r"(?:I'll|I'd|I\s+will)\s+make\s+(?:an?\s+)?intro",
    r"make\s+an?\s+intro\s+to",
    r"(?:happy|glad)\s+to\s+(?:introduce|connect)",
    r"could\s+(?:introduce|connect)\s+you",
    r"(?:my|a)\s+friend\s+(?:at|from|works at)",
    r"(?:I|we)\s+(?:have|got)\s+(?:a\s+)?contact\s+at",
]

DEAL_PATTERNS = [
    r"(?:looking|interested)\s+(?:to|in)\s+(?:acquire|buy|purchase)",
    r"(?:acquisition|merger)\s+(?:target|opportunity|candidate)",
    r"(?:want|interested)\s+(?:to|in)\s+(?:integrate|partner|distribute)",
    r"(?:potential|possible)\s+(?:acquisition|partnership|deal)",
    r"(?:they|we)(?:'re|'d like to|\s+are)\s+(?:interested|looking)",
]

LEADERSHIP_PATTERNS = [
    r"\b(?:CEO|CTO|CFO|COO|CPO|CMO|CHRO)\b",
    r"\b(?:Chief\s+(?:\w+\s+)?Officer)\b",
    r"\b(?:VP|Vice President)\s+(?:of\s+)?",
    r"\b(?:Head|Director)\s+(?:of\s+)?",
    r"\bfounder\b",
    r"\b(?:President|Managing Director|General Manager)\b",
]

# Name extraction patterns
NAME_PATTERN = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b"
COMPANY_PATTERN = r"\b(?:at|from|with)\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\b"


# =============================================================================
# Proactive Sensor Class
# =============================================================================

class DealProactiveSensor:
    def __init__(
        self,
        llm_callable: Optional[Callable[[str], str]] = None,
        sms_callable: Optional[Callable[[str], bool]] = None,
    ):
        self.llm_callable = llm_callable or self._default_llm_callable
        self.sms_callable = sms_callable  # If None, SMS won't be sent
        self._ensure_tables()

    def _default_llm_callable(self, prompt: str) -> str:
        """Default LLM stub - returns empty for heuristic fallback."""
        return ""

    def connect(self):
        """Get database connection using unified db_paths."""
        return get_db_connection()

    def _ensure_tables(self):
        """Ensure pending_approvals table exists."""
        conn = self.connect()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS pending_approvals (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                name TEXT NOT NULL,
                company TEXT,
                context TEXT,
                source_text TEXT,
                pipeline TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                resolved_at TEXT,
                resolution_note TEXT
            )
        """)
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_pending_status 
            ON pending_approvals(status)
        """)
        conn.commit()
        conn.close()

    # -------------------------
    # Entity Detection
    # -------------------------

    def detect_entities(self, text: str, source: str) -> List[DetectedEntity]:
        """
        Detect potential new entities in text using LLM + heuristic fallback.
        
        Returns list of DetectedEntity objects.
        """
        entities = []
        
        # Try LLM-based detection first
        llm_entities = self._detect_entities_llm(text, source)
        if llm_entities:
            entities.extend(llm_entities)
        
        # Heuristic fallback if LLM didn't return results
        if not entities:
            entities = self._detect_entities_heuristic(text, source)
        
        return entities

    def _detect_entities_llm(self, text: str, source: str) -> List[DetectedEntity]:
        """Use LLM for entity detection."""
        prompt = NEW_DEAL_DETECTION_PROMPT.format(content=text, source=source)
        
        try:
            response = self.llm_callable(prompt)
            if not response:
                return []
            
            # Parse JSON from response
            data = self._safe_json_loads(response)
            if not data:
                return []
            
            if not data.get("has_new_deal_signal"):
                return []
            
            # Map LLM output to DetectedEntity
            entity_type = data.get("deal_type", "broker")
            if entity_type == "acquisition":
                entity_type = "deal"
            elif entity_type == "partnership":
                entity_type = "deal"
            
            name = data.get("contact_name") or data.get("company_name") or "[Unknown]"
            company = data.get("company_name") if data.get("contact_name") else None
            
            return [DetectedEntity(
                entity_type=entity_type,
                name=name,
                company=company,
                context=data.get("summary", ""),
                signal_strength=data.get("signal_strength", "medium"),
                source=source,
                source_text=text[:500],
                recommended_action=data.get("recommended_action", "track_contact"),
                pipeline=data.get("suggested_pipeline"),
            )]
            
        except Exception as e:
            print(f"[proactive_sensor] LLM detection error: {e}", file=sys.stderr)
            return []

    def _detect_entities_heuristic(self, text: str, source: str) -> List[DetectedEntity]:
        """Heuristic-based entity detection."""
        entities = []
        text_lower = text.lower()
        
        # Check for broker signals
        for pattern in BROKER_PATTERNS:
            if re.search(pattern, text_lower):
                # Extract potential name
                names = re.findall(NAME_PATTERN, text)
                name = names[0] if names else "[Name to extract]"
                
                # Extract potential company
                companies = re.findall(COMPANY_PATTERN, text)
                company = companies[0] if companies else None
                
                # Get context (sentence containing the pattern)
                context = self._extract_context(text, pattern)
                
                entities.append(DetectedEntity(
                    entity_type="broker",
                    name=name,
                    company=company,
                    context=context,
                    signal_strength="medium",
                    source=source,
                    source_text=text[:500],
                    recommended_action="track_contact",
                    pipeline=None,
                ))
                break
        
        # Check for leadership signals (if no broker found)
        if not entities:
            for pattern in LEADERSHIP_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Extract name near the title
                    names = re.findall(NAME_PATTERN, text)
                    name = names[0] if names else "[Name to extract]"
                    
                    companies = re.findall(COMPANY_PATTERN, text)
                    company = companies[0] if companies else None
                    
                    context = self._extract_context(text, pattern)
                    
                    entities.append(DetectedEntity(
                        entity_type="leadership",
                        name=name,
                        company=company,
                        context=context,
                        signal_strength="medium",
                        source=source,
                        source_text=text[:500],
                        recommended_action="track_contact",
                        pipeline="careerspan",
                    ))
                    break
        
        # Check for deal signals
        if not entities:
            for pattern in DEAL_PATTERNS:
                if re.search(pattern, text_lower):
                    companies = re.findall(COMPANY_PATTERN, text)
                    company = companies[0] if companies else "[Company to extract]"
                    
                    context = self._extract_context(text, pattern)
                    
                    entities.append(DetectedEntity(
                        entity_type="deal",
                        name=company,
                        company=company,
                        context=context,
                        signal_strength="medium",
                        source=source,
                        source_text=text[:500],
                        recommended_action="create_deal",
                        pipeline="careerspan",
                    ))
                    break
        
        return entities

    def _extract_context(self, text: str, pattern: str) -> str:
        """Extract the sentence containing the pattern."""
        match = re.search(pattern, text.lower())
        if not match:
            return text[:150]
        
        # Find sentence boundaries around the match
        start = text.rfind(".", 0, match.start())
        end = text.find(".", match.end())
        
        start = 0 if start == -1 else start + 1
        end = len(text) if end == -1 else end + 1
        
        return text[start:end].strip()[:200]

    def _safe_json_loads(self, text: str) -> Optional[dict]:
        """Parse JSON from potentially messy LLM output."""
        if not text:
            return None
        
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            try:
                return json.loads(text)
            except Exception:
                pass
        
        # Find first JSON object
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        
        return None

    # -------------------------
    # Database Checks
    # -------------------------

    def is_entity_known(self, entity: DetectedEntity) -> bool:
        """Check if entity already exists in database (people or deals table)."""
        conn = self.connect()
        c = conn.cursor()
        
        name_lower = entity.name.lower()
        
        if entity.entity_type in ["broker", "leadership"]:
            # Check people table (unified CRM)
            c.execute("""
                SELECT 1 FROM people 
                WHERE LOWER(full_name) LIKE ?
                LIMIT 1
            """, (f"%{name_lower}%",))
        else:
            # Check deals
            c.execute("""
                SELECT 1 FROM deals 
                WHERE LOWER(company) LIKE ?
                LIMIT 1
            """, (f"%{name_lower}%",))
        
        result = c.fetchone()
        conn.close()
        return result is not None

    # -------------------------
    # Approval Queue
    # -------------------------

    def queue_approval(self, entity: DetectedEntity) -> str:
        """Queue entity for SMS approval. Returns approval ID."""
        conn = self.connect()
        c = conn.cursor()
        
        approval_id = str(uuid.uuid4())[:8]
        
        c.execute("""
            INSERT INTO pending_approvals 
            (id, entity_type, name, company, context, source_text, pipeline, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            approval_id,
            entity.entity_type,
            entity.name,
            entity.company,
            entity.context,
            entity.source_text,
            entity.pipeline,
            datetime.now().isoformat(),
        ))
        
        conn.commit()
        conn.close()
        return approval_id

    def get_pending(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Get a pending approval by ID."""
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT * FROM pending_approvals WHERE id = ?", (approval_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return ApprovalRequest(
            id=row["id"],
            entity_type=row["entity_type"],
            name=row["name"],
            company=row["company"],
            context=row["context"],
            source_text=row["source_text"],
            pipeline=row["pipeline"],
            status=row["status"],
            created_at=row["created_at"],
        )

    def list_pending(self) -> List[ApprovalRequest]:
        """List all pending approvals."""
        conn = self.connect()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM pending_approvals 
            WHERE status = 'pending'
            ORDER BY created_at DESC
        """)
        rows = c.fetchall()
        conn.close()
        
        return [ApprovalRequest(
            id=row["id"],
            entity_type=row["entity_type"],
            name=row["name"],
            company=row["company"],
            context=row["context"],
            source_text=row["source_text"],
            pipeline=row["pipeline"],
            status=row["status"],
            created_at=row["created_at"],
        ) for row in rows]

    # -------------------------
    # SMS Formatting
    # -------------------------

    def format_approval_sms(self, entity: DetectedEntity, approval_id: str) -> str:
        """Format SMS for approval request."""
        emoji = {
            "broker": "🤝",
            "deal": "🏢",
            "leadership": "👔",
        }.get(entity.entity_type, "🆕")
        
        type_label = {
            "broker": "broker",
            "deal": "deal target",
            "leadership": "leadership contact",
        }.get(entity.entity_type, "contact")
        
        company_part = f" ({entity.company})" if entity.company and entity.company != entity.name else ""
        
        context_preview = entity.context[:100]
        if len(entity.context) > 100:
            context_preview += "..."
        
        return f"""{emoji} New {type_label} detected:
{entity.name}{company_part}

Context: "{context_preview}"

Add to database? Reply:
Y - Add
N - Skip
Info - More details

[{approval_id}]"""

    # -------------------------
    # Approval Processing
    # -------------------------

    def process_approval(self, approval_id: str, response: str) -> ApprovalResult:
        """Process V's approval response (Y/N/Info)."""
        pending = self.get_pending(approval_id)
        if not pending:
            return ApprovalResult(
                success=False,
                action="not_found",
                message=f"Approval [{approval_id}] not found or already processed.",
            )
        
        response_upper = response.strip().upper()
        conn = self.connect()
        c = conn.cursor()
        
        if response_upper == "Y":
            # Create the entity
            created_id = self._create_entity(pending)
            
            c.execute("""
                UPDATE pending_approvals 
                SET status = 'approved', resolved_at = ?, resolution_note = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), f"Created as {created_id}", approval_id))
            conn.commit()
            conn.close()
            
            return ApprovalResult(
                success=True,
                action="created",
                message=f"✓ Created {pending.entity_type}: {pending.name}",
                created_id=created_id,
            )
        
        elif response_upper == "N":
            c.execute("""
                UPDATE pending_approvals 
                SET status = 'declined', resolved_at = ?, resolution_note = 'User declined'
                WHERE id = ?
            """, (datetime.now().isoformat(), approval_id))
            conn.commit()
            conn.close()
            
            return ApprovalResult(
                success=True,
                action="declined",
                message=f"✓ Skipped {pending.name}",
            )
        
        elif response_upper == "INFO":
            # Return more context
            conn.close()
            
            full_context = pending.source_text or pending.context
            return ApprovalResult(
                success=True,
                action="info",
                message=f"""📋 Full context for {pending.name}:

Source text:
"{full_context}"

Reply Y to add, N to skip.
[{approval_id}]""",
            )
        
        else:
            conn.close()
            return ApprovalResult(
                success=False,
                action="error",
                message=f"Unknown response: {response}. Reply Y, N, or Info.",
            )

    def _create_entity(self, pending: ApprovalRequest) -> str:
        """Create entity in database from approved request.
        
        For broker/leadership: Creates person in people table + deal_role entry
        For deal: Creates deal in deals table
        """
        conn = self.connect()
        c = conn.cursor()
        now = datetime.now().isoformat()
        
        if pending.entity_type in ["broker", "leadership"]:
            # Create in people table (unified CRM)
            c.execute("""
                INSERT INTO people (full_name, company, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                pending.name,
                pending.company,
                now,
                now,
            ))
            
            person_id = c.lastrowid
            
            # If there's a pipeline hint, create a placeholder deal_role
            # The role maps: broker -> 'broker', leadership -> 'leadership'
            # Note: No deal_id yet - this creates an unlinked person
            # which can be linked to deals later via deal_roles
            
            conn.commit()
            conn.close()
            return f"person-{person_id}"
        
        else:
            # Create in deals
            company_slug = (pending.company or pending.name).lower().replace(" ", "-")[:20]
            deal_id = f"cs-acq-{company_slug}"
            
            # Handle collision
            c.execute("SELECT id FROM deals WHERE id = ?", (deal_id,))
            if c.fetchone():
                deal_id = f"{deal_id}-{str(uuid.uuid4())[:4]}"
            
            c.execute("""
                INSERT INTO deals (
                    id, deal_type, company, pipeline, stage, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                deal_id,
                "acquisition",
                pending.company or pending.name,
                pending.pipeline or "careerspan",
                "identified",
                now,
                now,
            ))
            
            conn.commit()
            conn.close()
            return deal_id

    # -------------------------
    # Main Entry Point
    # -------------------------

    def process_text(
        self, 
        text: str, 
        source: str, 
        dry_run: bool = False,
        send_sms: bool = True,
    ) -> SensorResult:
        """
        Main entry point: detect new entities and queue for approval.
        
        Args:
            text: Content to analyze
            source: Source type (meeting, email, sms, kondo)
            dry_run: If True, don't write to DB or send SMS
            send_sms: If True and sms_callable is set, send SMS
            
        Returns:
            SensorResult with detection results
        """
        # Detect entities
        entities = self.detect_entities(text, source)
        
        if not entities:
            return SensorResult(
                entities_detected=[],
                entities_queued=0,
                sms_formatted=[],
                dry_run=dry_run,
            )
        
        # Filter out known entities
        new_entities = [e for e in entities if not self.is_entity_known(e)]
        
        if not new_entities:
            return SensorResult(
                entities_detected=entities,
                entities_queued=0,
                sms_formatted=[],
                dry_run=dry_run,
            )
        
        # Queue for approval and format SMS
        sms_messages = []
        queued_count = 0
        
        for entity in new_entities:
            if dry_run:
                approval_id = f"dry-{str(uuid.uuid4())[:4]}"
            else:
                approval_id = self.queue_approval(entity)
                queued_count += 1
            
            sms = self.format_approval_sms(entity, approval_id)
            sms_messages.append(sms)
            
            # Send SMS if callable is provided and not dry run
            if send_sms and self.sms_callable and not dry_run:
                try:
                    self.sms_callable(sms)
                except Exception as e:
                    print(f"[proactive_sensor] SMS send error: {e}", file=sys.stderr)
        
        return SensorResult(
            entities_detected=new_entities,
            entities_queued=queued_count,
            sms_formatted=sms_messages,
            dry_run=dry_run,
        )


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Proactive Deal Sensor - Detect potential new deals/contacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze text for new entity signals
  python3 deal_proactive_sensor.py --text "John can intro us to Workday CEO" --source meeting
  
  # Process approval response
  python3 deal_proactive_sensor.py --approval "Y" --pending-id abc123
  
  # List pending approvals
  python3 deal_proactive_sensor.py --list-pending
  
  # Dry run
  python3 deal_proactive_sensor.py --text "..." --source email --dry-run
        """
    )
    
    # Detection mode
    parser.add_argument(
        "--text", "-t",
        help="Text content to analyze for new entities"
    )
    parser.add_argument(
        "--source", "-s",
        choices=["meeting", "email", "sms", "kondo"],
        default="meeting",
        help="Source of the text (default: meeting)"
    )
    
    # Approval mode
    parser.add_argument(
        "--approval", "-a",
        help="Process approval response (Y/N/Info)"
    )
    parser.add_argument(
        "--pending-id", "-p",
        help="Approval ID to process"
    )
    
    # List mode
    parser.add_argument(
        "--list-pending", "-l",
        action="store_true",
        help="List all pending approvals"
    )
    
    # Options
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Don't make any changes or send SMS"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    sensor = DealProactiveSensor()
    
    # Mode: List pending
    if args.list_pending:
        pending = sensor.list_pending()
        if args.json:
            print(json.dumps([asdict(p) for p in pending], indent=2))
        elif not pending:
            print("No pending approvals.")
        else:
            print(f"Pending approvals ({len(pending)}):\n")
            for p in pending:
                company_part = f" ({p.company})" if p.company else ""
                print(f"  [{p.id}] {p.entity_type}: {p.name}{company_part}")
                print(f"         Created: {p.created_at}")
                print()
        return
    
    # Mode: Process approval
    if args.approval:
        if not args.pending_id:
            print("Error: --pending-id required with --approval", file=sys.stderr)
            sys.exit(1)
        
        result = sensor.process_approval(args.pending_id, args.approval)
        
        if args.json:
            print(json.dumps(asdict(result), indent=2))
        else:
            print(result.message)
        
        sys.exit(0 if result.success else 1)
    
    # Mode: Detect entities
    if args.text:
        result = sensor.process_text(
            text=args.text,
            source=args.source,
            dry_run=args.dry_run,
            send_sms=False,  # CLI doesn't send SMS directly
        )
        
        if args.json:
            output = {
                "entities_detected": [asdict(e) for e in result.entities_detected],
                "entities_queued": result.entities_queued,
                "sms_messages": result.sms_formatted,
                "dry_run": result.dry_run,
            }
            print(json.dumps(output, indent=2))
        else:
            if not result.entities_detected:
                print("No new entities detected.")
            else:
                prefix = "[DRY RUN] " if result.dry_run else ""
                print(f"{prefix}Detected {len(result.entities_detected)} new entity(ies):\n")
                for entity in result.entities_detected:
                    company_part = f" ({entity.company})" if entity.company else ""
                    print(f"  {entity.entity_type.upper()}: {entity.name}{company_part}")
                    print(f"    Signal: {entity.signal_strength}")
                    print(f"    Context: {entity.context[:80]}...")
                    print()
                
                if result.sms_formatted:
                    print("SMS approval message(s):\n")
                    for sms in result.sms_formatted:
                        print("-" * 40)
                        print(sms)
                        print()
        return
    
    # No mode specified
    parser.print_help()


if __name__ == "__main__":
    main()
