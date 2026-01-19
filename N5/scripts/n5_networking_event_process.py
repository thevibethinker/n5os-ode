#!/usr/bin/env python3
"""
Networking Event Processor - Individual-Centric CRM
Processes networking events with verbal dump interface and stakeholder profiling.

Version: 1.0.0
"""
import asyncio
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import sqlite3

# Add N5 scripts to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/home/workspace")

from blocks.llm_client import get_client
from blocks.stakeholder_profile_generator import generate_stakeholder_profile

# Unified database connection
try:
    from N5.scripts.db_paths import get_db_connection, N5_CORE_DB
    DB_PATH = N5_CORE_DB
except ImportError:
    DB_PATH = Path("/home/workspace/N5/data/n5_core.db")
    def get_db_connection(readonly=False):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
CRM_BASE = WORKSPACE / "Knowledge" / "crm"
CRM_INDIVIDUALS = CRM_BASE / "individuals"
CRM_EVENTS = CRM_BASE / "events"
CRM_FOLLOWUPS = CRM_BASE / "follow-ups"
CRM_INDEX = CRM_BASE / "index.jsonl"
EVENTS_INDEX = CRM_BASE / "events" / "index.jsonl"
NETWORKING_LIST = WORKSPACE / "N5" / "lists" / "networking-contacts.jsonl"
ESSENTIAL_LINKS = WORKSPACE / "N5" / "prefs" / "communication" / "essential-links.json"
VOICE_PREFS = WORKSPACE / "N5" / "prefs" / "communication" / "voice.md"


def get_db_conn():
    """Get database connection with Row factory - uses unified n5_core.db"""
    return get_db_connection(readonly=False)


def upsert_individual(conn, individual):
    """
    Insert or update individual record in unified people table.
    Returns individual_id.
    
    Args:
        individual: dict with keys: full_name, email, title, company,
                   primary_category, status, tags, source_type, notes,
                   markdown_file_path, etc.
    """
    cursor = conn.cursor()
    
    # Try to find existing by email or name
    if individual.get('email'):
        cursor.execute("SELECT id FROM people WHERE email = ?", 
                      (individual['email'],))
    else:
        cursor.execute("SELECT id FROM people WHERE full_name = ?", 
                      (individual['full_name'],))
    
    row = cursor.fetchone()
    
    if row:
        # Update existing
        individual_id = row['id']
        cursor.execute("""
            UPDATE people SET
                full_name = COALESCE(?, full_name),
                email = COALESCE(?, email),
                title = COALESCE(?, title),
                company = COALESCE(?, company),
                category = COALESCE(?, category),
                status = COALESCE(?, status),
                tags = COALESCE(?, tags),
                markdown_path = COALESCE(?, markdown_path),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            individual.get('full_name'),
            individual.get('email'),
            individual.get('title'),
            individual.get('company'),
            individual.get('primary_category'),
            individual.get('status', 'active'),
            json.dumps(individual.get('tags', [])) if individual.get('tags') else None,
            individual.get('markdown_file_path'),
            individual_id
        ))
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO people (
                full_name, email, title, company, category, status, tags, 
                markdown_path, source_db, first_contact_date, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'), CURRENT_TIMESTAMP)
        """, (
            individual['full_name'],
            individual.get('email'),
            individual.get('title'),
            individual.get('company'),
            individual.get('primary_category', 'NETWORKING'),
            individual.get('status', 'active'),
            json.dumps(individual.get('tags', [])) if individual.get('tags') else None,
            individual.get('markdown_file_path'),
            'networking_event'
        ))
        individual_id = cursor.lastrowid
    
    conn.commit()
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


@dataclass
class Individual:
    """Individual profile data structure."""
    id: str
    name: str
    context: str
    company: str
    role: str
    connection_channels: List[str]
    relationship_depth: int
    tags: List[str]
    mutual_acquaintances: List[str]
    first_contact: str
    last_contact: str
    events: List[str]
    profile_path: str
    status: str
    enrichment_status: str = "pending"
    enrichment_priority: str = "medium"


@dataclass
class EventData:
    """Event data structure."""
    id: str
    name: str
    date: str
    location: str
    event_type: str
    purpose: str
    people_met: List[str]
    high_priority: List[str]
    log_path: str


class NetworkingEventProcessor:
    """Main processor for networking events."""
    
    def __init__(self):
        self.llm = get_client()
        self.essential_links = self._load_essential_links()
        self.voice_prefs = self._load_voice_prefs()
        self.individuals_index = self._load_index(CRM_INDEX)
        self.events_index = self._load_index(EVENTS_INDEX)
        
    def _load_essential_links(self) -> Dict[str, Any]:
        """Load essential links from prefs."""
        if ESSENTIAL_LINKS.exists():
            with open(ESSENTIAL_LINKS) as f:
                return json.load(f)
        return {}
    
    def _load_voice_prefs(self) -> str:
        """Load voice preferences."""
        if VOICE_PREFS.exists():
            return VOICE_PREFS.read_text()
        return ""
    
    def _load_index(self, path: Path) -> Dict[str, Any]:
        """Load JSONL index."""
        if not path.exists():
            return {}
        
        index = {}
        with open(path) as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    index[item['id']] = item
        return index
    
    def _save_index(self, index: Dict[str, Any], path: Path):
        """Save JSONL index."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            for item in index.values():
                f.write(json.dumps(item) + '\n')
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text
    
    async def run(self):
        """Main interactive workflow."""
        print("\n" + "="*70)
        print("🌐 NETWORKING EVENT PROCESSOR v1.0")
        print("="*70 + "\n")
        
        # Step 1: Event Context + Bulk Paste
        event_data = await self._collect_event_context()
        contact_notes = await self._collect_bulk_notes()
        
        # Step 2: Person-by-Person Loop
        contacts = []
        print(f"\n📋 Processing {len(contact_notes)} contacts...\n")
        
        for i, note in enumerate(contact_notes, 1):
            print(f"\n--- Contact {i}/{len(contact_notes)} ---")
            print(f"Note: {note}\n")
            
            contact = await self._process_individual(note, event_data)
            if contact:
                contacts.append(contact)
        
        # Step 3: Create Event Log
        await self._create_event_log(event_data, contacts)
        
        # Step 4: Synthesis & Deliverables
        await self._execute_deliverables(contacts)
        
        # Step 5: Summary
        self._print_summary(event_data, contacts)
        
        print("\n✅ Networking event processing complete!\n")
    
    async def _collect_event_context(self) -> Dict[str, Any]:
        """Step 1: Collect event metadata."""
        print("📅 STEP 1: Event Context\n")
        
        event_name = input("Event name: ").strip()
        event_date = input("Event date (YYYY-MM-DD) [default: today]: ").strip() or datetime.now().strftime("%Y-%m-%d")
        event_location = input("Location: ").strip()
        event_type = input("Event type (e.g., conference, meetup, dinner): ").strip() or "networking_event"
        event_purpose = input("Purpose (e.g., business development, partnerships): ").strip()
        
        event_id = f"{event_date}_{self._slugify(event_name)}"
        
        return {
            "id": event_id,
            "name": event_name,
            "date": event_date,
            "location": event_location,
            "type": event_type,
            "purpose": event_purpose,
            "people_met": [],
            "high_priority": []
        }
    
    async def _collect_bulk_notes(self) -> List[str]:
        """Step 1: Collect all contact notes upfront."""
        print("\n📝 Paste all your contact notes (one person per line).")
        print("When done, type 'DONE' on a new line:\n")
        
        notes = []
        while True:
            line = input().strip()
            if line.upper() == 'DONE':
                break
            if line:
                notes.append(line)
        
        return notes
    
    async def _process_individual(self, note: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Step 2: Process individual with verbal dump interface."""
        
        # Initial extraction from note
        print("💬 Tell me everything about this person (verbal dump):")
        print("   (Just talk through what you remember - context, conversation, action items, etc.)\n")
        
        verbal_dump = []
        while True:
            line = input().strip()
            if line.upper() == 'NEXT' or line.upper() == 'DONE':
                break
            if line:
                verbal_dump.append(line)
        
        if not verbal_dump:
            print("⚠️  Skipping (no input provided)")
            return None
        
        full_context = f"{note}\n\n" + "\n".join(verbal_dump)
        
        # LLM extraction
        extracted = await self._extract_structured_data(full_context, event_data)
        
        if not extracted:
            print("⚠️  Could not extract contact info. Skipping...")
            return None
        
        # One clarifying question
        clarification = await self._generate_clarifying_question(extracted)
        if clarification:
            print(f"\n❓ Clarifying question: {clarification}")
            answer = input("   Your answer: ").strip()
            if answer:
                # Re-extract with additional context
                full_context += f"\n\nAdditional: {answer}"
                extracted = await self._extract_structured_data(full_context, event_data)
        
        # Check if individual exists
        individual_id = self._slugify(extracted['name'])
        existing = self.individuals_index.get(individual_id)
        
        if existing:
            print(f"✓ Found existing profile: {existing['name']}")
            # Update existing profile
            updated = await self._update_individual(existing, extracted, event_data)
            contact = updated
        else:
            print(f"✓ Creating new profile: {extracted['name']}")
            # Create new profile
            contact = await self._create_individual(extracted, event_data)
        
        # Generate LinkedIn message
        await self._generate_linkedin_message(contact, extracted, event_data)
        
        # Detect and queue deliverables
        await self._detect_deliverables(contact, extracted)
        
        print(f"✅ Processed: {contact['name']}\n")
        
        return contact
    
    async def _extract_structured_data(self, context: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured contact data via LLM."""
        
        prompt = f"""Extract structured contact information from this conversation context.

Event: {event_data['name']} on {event_data['date']}

Context:
{context}

Extract and return as JSON:
{{
  "name": "Full Name",
  "context": "One-line context/summary (what makes this person notable)",
  "company": "Company Name",
  "role": "Job Title",
  "connection_channels": ["linkedin", "email", etc],
  "tags": ["prospect", "advisor", etc],
  "mutual_acquaintances": ["Jane Smith", "Alex Caveny", etc],
  "background": "Brief background/experience",
  "interests": "What they care about",
  "pain_points": "Challenges they mentioned",
  "opportunities": "What they're looking for",
  "key_quotes": ["Quote 1", "Quote 2"],
  "promised_follow_ups": ["send proposal", "intro to Logan", etc],
  "priority": "high | medium | low"
}}

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = await self.llm.chat([
                {"role": "system", "content": "You are an expert at extracting structured contact information from conversational text."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return None
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return None
    
    async def _generate_clarifying_question(self, extracted: Dict[str, Any]) -> Optional[str]:
        """Generate ONE clarifying question if needed."""
        
        # Check for missing critical fields
        missing = []
        if not extracted.get('company'):
            missing.append('company')
        if not extracted.get('role'):
            missing.append('role')
        if not extracted.get('connection_channels'):
            missing.append('how to connect (LinkedIn/email/phone)')
        
        if not missing:
            return None
        
        if len(missing) == 1:
            return f"What is their {missing[0]}?"
        else:
            return f"Can you provide: {', '.join(missing)}?"
    
    async def _create_individual(self, extracted: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new individual profile."""
        
        individual_id_slug = self._slugify(extracted['name'])
        profile_path = CRM_INDIVIDUALS / f"{individual_id_slug}.md"
        
        # Build individual object
        individual = Individual(
            id=individual_id_slug,
            name=extracted['name'],
            context=extracted.get('context', ''),
            company=extracted.get('company', 'Unknown'),
            role=extracted.get('role', 'Unknown'),
            connection_channels=extracted.get('connection_channels', []),
            relationship_depth=1,  # New contact
            tags=extracted.get('tags', []),
            mutual_acquaintances=[self._slugify(name) for name in extracted.get('mutual_acquaintances', [])],
            first_contact=event_data['date'],
            last_contact=event_data['date'],
            events=[event_data['id']],
            profile_path=str(profile_path.relative_to(WORKSPACE)),
            status="active",
            enrichment_status="pending",
            enrichment_priority=extracted.get('priority', 'medium')
        )
        
        # Write profile markdown
        await self._write_individual_profile(individual, extracted, event_data)
        
        # NEW: Also write to database
        conn = get_db_conn()
        try:
            db_individual = {
                'full_name': extracted['name'],
                'title': extracted.get('role'),
                'company': extracted.get('company'),
                'email': next((ch for ch in extracted.get('connection_channels', []) if '@' in ch), None),
                'primary_category': extracted.get('tags', ['prospect'])[0],
                'status': 'active',
                'tags': ','.join(extracted.get('tags', [])),
                'source_type': 'event',
                'notes': extracted.get('context'),
                'markdown_file_path': str(profile_path.relative_to(WORKSPACE))
            }
            
            individual_id_db = upsert_individual(conn, db_individual)
            
            # Record the event interaction
            interaction = {
                'interaction_type': 'event',
                'interaction_date': event_data['date'],
                'subject': f"Met at {event_data.get('name')}",
                'summary': extracted.get('context'),
                'notes_file_path': str(profile_path.relative_to(WORKSPACE))
            }
            
            insert_interaction(conn, individual_id_db, interaction)
            
            conn.commit()
            logger.info(f"✓ Added {db_individual['full_name']} to CRM database")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"✗ Database error: {e}")
        finally:
            conn.close()

        # Update index
        self.individuals_index[individual_id_slug] = asdict(individual)
        self._save_index(self.individuals_index, CRM_INDEX)
        
        # Add to networking list
        await self._add_to_networking_list(individual)
        
        return asdict(individual)
    
    async def _update_individual(self, existing: Dict[str, Any], extracted: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing individual profile."""
        
        # Update fields
        existing['last_contact'] = event_data['date']
        if event_data['id'] not in existing['events']:
            existing['events'].append(event_data['id'])
        
        # Merge tags
        new_tags = extracted.get('tags', [])
        existing['tags'] = list(set(existing['tags'] + new_tags))
        
        # Merge mutual acquaintances
        new_mutuals = [self._slugify(name) for name in extracted.get('mutual_acquaintances', [])]
        existing['mutual_acquaintances'] = list(set(existing.get('mutual_acquaintances', []) + new_mutuals))
        
        # Re-write profile with updated relationship history
        await self._append_relationship_history(existing, extracted, event_data)
        
        # NEW: Also write to database
        conn = get_db_conn()
        try:
            db_individual = {
                'full_name': existing['name'],
                'title': existing.get('role'),
                'company': existing.get('company'),
                'email': next((ch for ch in existing.get('connection_channels', []) if '@' in ch), None),
                'primary_category': existing.get('tags', ['prospect'])[0],
                'status': existing.get('status'),
                'tags': ','.join(existing.get('tags', [])),
                'notes': extracted.get('context'),
                'markdown_file_path': existing['profile_path']
            }

            individual_id_db = upsert_individual(conn, db_individual)

            # Record the event interaction
            interaction = {
                'interaction_type': 'event',
                'interaction_date': event_data['date'],
                'subject': f"Follow-up at {event_data.get('name')}",
                'summary': extracted.get('context'),
                'notes_file_path': existing['profile_path']
            }

            insert_interaction(conn, individual_id_db, interaction)

            conn.commit()
            logger.info(f"✓ Updated {db_individual['full_name']} in CRM database")

        except Exception as e:
            conn.rollback()
            logger.error(f"✗ Database error on update: {e}")
        finally:
            conn.close()

        # Update index
        self.individuals_index[existing['id']] = existing
        self._save_index(self.individuals_index, CRM_INDEX)
        
        return existing
    
    async def _write_individual_profile(self, individual: Individual, extracted: Dict[str, Any], event_data: Dict[str, Any]):
        """Write individual profile markdown."""
        
        CRM_INDIVIDUALS.mkdir(parents=True, exist_ok=True)
        profile_path = WORKSPACE / individual.profile_path
        
        # Build mutual acquaintances section
        mutual_section = ""
        if individual.mutual_acquaintances:
            mutual_links = []
            for acquaintance_id in individual.mutual_acquaintances:
                acquaintance = self.individuals_index.get(acquaintance_id)
                if acquaintance:
                    mutual_links.append(f"- [{acquaintance['name']}](./{acquaintance_id}.md)")
                else:
                    # Not yet in CRM
                    name = acquaintance_id.replace('-', ' ').title()
                    mutual_links.append(f"- {name} (not yet in CRM)")
            
            mutual_section = "\n**Mutual Acquaintances**:\n" + "\n".join(mutual_links) + "\n"
        
        content = f"""# {individual.name}

**One-Line Context**: {individual.context}

**Company**: {individual.company}  
**Role**: {individual.role}  
**Connection Channels**: {", ".join(individual.connection_channels)}  
**Relationship Depth**: {individual.relationship_depth} (New Contact)  
**Tags**: {" ".join(f"#{tag}" for tag in individual.tags)}

**First Contact**: {individual.first_contact}  
**Last Contact**: {individual.last_contact}  
**Status**: {individual.status}
{mutual_section}
---

## Background & Experience
{extracted.get('background', 'To be updated')}

## Interests & Focus Areas
{extracted.get('interests', 'To be updated')}

## Pain Points & Challenges
{extracted.get('pain_points', 'To be updated')}

## Opportunities & Needs
{extracted.get('opportunities', 'To be updated')}

## Key Quotes
{self._format_quotes(extracted.get('key_quotes', []))}

## Relationship History
- **{event_data['date']}**: Met at {event_data['name']}
  - {extracted.get('context', 'Initial meeting')}
  - Event: [{event_data['name']}](../events/{event_data['date'][:7]}/{event_data['id']}.md)

## Follow-Ups & Action Items
{self._format_action_items(extracted.get('promised_follow_ups', []), event_data['date'])}

## Generated Materials
- [LinkedIn Message ({event_data['date']})](../follow-ups/{individual.id}_{event_data['date']}_linkedin.md)

---

## Enrichment Status
- [ ] LinkedIn profile scraped
- [ ] Company research completed  
- [ ] Recent news/announcements checked
- **Last Enrichment**: Never  
**Enrichment Priority**: {individual.enrichment_priority}

---
**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}  
**Profile Version**: 1.0
"""
        
        profile_path.write_text(content)
        logger.info(f"Created profile: {profile_path}")
    
    async def _append_relationship_history(self, existing: Dict[str, Any], extracted: Dict[str, Any], event_data: Dict[str, Any]):
        """Append new relationship history entry to existing profile."""
        
        profile_path = WORKSPACE / existing['profile_path']
        if not profile_path.exists():
            logger.warning(f"Profile not found: {profile_path}")
            return
        
        content = profile_path.read_text()
        
        # Find relationship history section and append
        new_entry = f"""- **{event_data['date']}**: Met at {event_data['name']}
  - {extracted.get('context', 'Follow-up meeting')}
  - Event: [{event_data['name']}](../events/{event_data['date'][:7]}/{event_data['id']}.md)
"""
        
        # Insert before "## Follow-Ups & Action Items"
        if "## Follow-Ups & Action Items" in content:
            content = content.replace(
                "## Follow-Ups & Action Items",
                new_entry + "\n## Follow-Ups & Action Items"
            )
        else:
            content += "\n" + new_entry
        
        # Update last updated date
        content = re.sub(
            r'\*\*Last Updated\*\*: \d{4}-\d{2}-\d{2}',
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}",
            content
        )
        
        profile_path.write_text(content)
    
    def _format_quotes(self, quotes: List[str]) -> str:
        """Format key quotes."""
        if not quotes:
            return "None captured"
        return "\n".join(f"> \"{quote}\"" for quote in quotes)
    
    def _format_action_items(self, items: List[str], date: str) -> str:
        """Format action items."""
        if not items:
            return "- [ ] No immediate action items"
        
        formatted = []
        for item in items:
            # Try to infer due date (3-7 days out)
            due_date = datetime.strptime(date, "%Y-%m-%d")
            due_date = (due_date + timedelta(days=5)).strftime("%Y-%m-%d")
            formatted.append(f"- [ ] {item.capitalize()} (due {due_date})")
        
        return "\n".join(formatted)
    
    async def _add_to_networking_list(self, individual: Individual):
        """Add individual to networking list."""
        
        NETWORKING_LIST.parent.mkdir(parents=True, exist_ok=True)
        
        list_entry = {
            "id": f"net-{individual.id}",
            "name": individual.name,
            "company": individual.company,
            "role": individual.role,
            "first_contact": individual.first_contact,
            "last_contact": individual.last_contact,
            "relationship_depth": individual.relationship_depth,
            "tags": individual.tags,
            "profile_path": individual.profile_path,
            "added": datetime.now().isoformat()
        }
        
        # Append to list
        with open(NETWORKING_LIST, 'a') as f:
            f.write(json.dumps(list_entry) + '\n')
        
        logger.info(f"Added to networking list: {individual.name}")
    
    async def _generate_linkedin_message(self, contact: Dict[str, Any], extracted: Dict[str, Any], event_data: Dict[str, Any]):
        """Generate same-day LinkedIn follow-up message."""
        
        # Build context for LLM
        promised_followups = extracted.get('promised_follow_ups', [])
        
        prompt = f"""Generate a same-day LinkedIn follow-up message.

Recipient: {contact['name']}
Role: {contact['role']} at {contact['company']}
Event: {event_data['name']} on {event_data['date']}
Relationship Depth: {contact['relationship_depth']} (New Contact)

Conversation Context:
{extracted.get('context', '')}

Pain Points Discussed:
{extracted.get('pain_points', '')}

Promised Follow-Ups:
{', '.join(promised_followups) if promised_followups else 'None'}

Requirements:
- Length: <120 words (STRICT)
- Tone: Balanced, warm (per voice.md)
- Include: Resonant detail from conversation, what we discussed, why following up
- If immediate action promised: Mention it ("I'll send the proposal this week")
- Soft CTA: "Looking forward to continuing the conversation" or similar
- Sign as "Vrijen"
- Use greeting: "Hey {{name}},"
- Use sign-off: "Best,"

Return ONLY the message text, no other formatting.
"""
        
        try:
            response = await self.llm.chat([
                {"role": "system", "content": f"You are Vrijen, founder of Careerspan. Follow voice.md guidelines:\n\n{self.voice_prefs[:1000]}"},
                {"role": "user", "content": prompt}
            ])
            
            # Save message
            message_path = CRM_FOLLOWUPS / f"{contact['id']}_{event_data['date']}_linkedin.md"
            CRM_FOLLOWUPS.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            word_count = len(response.split())
            full_message = f"""# LinkedIn Follow-Up: {contact['name']}

**Date**: {event_data['date']}  
**Event**: {event_data['name']}  
**Relationship Depth**: {contact['relationship_depth']} (New Contact)  
**Word Count**: {word_count}/120

---

{response}

---

**Status**: Draft  
**Send**: Same day  
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            
            message_path.write_text(full_message)
            logger.info(f"Generated LinkedIn message: {message_path}")
            
            if word_count > 120:
                logger.warning(f"⚠️  Message exceeds 120 words: {word_count}")
            
        except Exception as e:
            logger.error(f"Failed to generate LinkedIn message: {e}")
    
    async def _detect_deliverables(self, contact: Dict[str, Any], extracted: Dict[str, Any]):
        """Detect and queue deliverables (proposals, intros, etc.)."""
        
        promised = extracted.get('promised_follow_ups', [])
        
        # Simple keyword detection
        deliverables = []
        for item in promised:
            item_lower = item.lower()
            if 'proposal' in item_lower:
                deliverables.append({'type': 'proposal', 'contact': contact['name'], 'item': item})
            elif 'deck' in item_lower or 'pitch' in item_lower:
                deliverables.append({'type': 'deck', 'contact': contact['name'], 'item': item})
            elif 'intro' in item_lower:
                deliverables.append({'type': 'intro', 'contact': contact['name'], 'item': item})
            elif 'link' in item_lower:
                deliverables.append({'type': 'link', 'contact': contact['name'], 'item': item})
        
        # Store for execution
        contact['deliverables_queue'] = deliverables
    
    async def _create_event_log(self, event_data: Dict[str, Any], contacts: List[Dict[str, Any]]):
        """Step 3: Create event log with cross-references."""
        
        month_folder = CRM_EVENTS / event_data['date'][:7]
        month_folder.mkdir(parents=True, exist_ok=True)
        
        event_path = month_folder / f"{event_data['id']}.md"
        
        # Group contacts by priority
        high_priority = [c for c in contacts if c.get('enrichment_priority') == 'high']
        medium_priority = [c for c in contacts if c.get('enrichment_priority') == 'medium']
        general = [c for c in contacts if c.get('enrichment_priority', 'low') == 'low']
        
        def format_contact_entry(contact: Dict[str, Any]) -> str:
            profile_rel_path = f"../../individuals/{contact['id']}.md"
            return f"- **[{contact['name']}]({profile_rel_path})** - {contact['role']} at {contact['company']}\n  - **Context**: {contact.get('context', 'TBD')}\n  - **Follow-ups**: {', '.join(c.get('deliverables_queue', [{'item': 'TBD'}])[0]['item'] for c in [contact] if c.get('deliverables_queue'))}"
        
        content = f"""# {event_data['name']}

**Date**: {event_data['date']}  
**Location**: {event_data['location']}  
**Type**: {event_data['type']}  
**Purpose**: {event_data['purpose']}

---

## People Met ({len(contacts)} total)

### High Priority
{chr(10).join(format_contact_entry(c) for c in high_priority) if high_priority else '- None'}

### Medium Priority
{chr(10).join(format_contact_entry(c) for c in medium_priority) if medium_priority else '- None'}

### General Connections
{chr(10).join(format_contact_entry(c) for c in general) if general else '- None'}

---

## Event-Level Insights
- **Themes**: To be updated
- **Pain Points**: To be updated
- **Opportunities**: To be updated
- **Competition**: To be updated

## Event-Level Action Items
- [ ] Share event recap with Logan
- [ ] Add contacts to newsletter

---
**Generated**: {datetime.now().strftime("%Y-%m-%d")}  
**Total Contacts**: {len(contacts)}
"""
        
        event_path.write_text(content)
        logger.info(f"Created event log: {event_path}")
        
        # Update events index
        self.events_index[event_data['id']] = {
            "id": event_data['id'],
            "name": event_data['name'],
            "date": event_data['date'],
            "location": event_data['location'],
            "type": event_data['type'],
            "people_met": [c['id'] for c in contacts],
            "high_priority": [c['id'] for c in high_priority],
            "log_path": str(event_path.relative_to(WORKSPACE))
        }
        self._save_index(self.events_index, EVENTS_INDEX)
    
    async def _execute_deliverables(self, contacts: List[Dict[str, Any]]):
        """Step 4: Execute queued deliverables."""
        
        all_deliverables = []
        for contact in contacts:
            deliverables = contact.get('deliverables_queue', [])
            all_deliverables.extend(deliverables)
        
        if not all_deliverables:
            print("\n✓ No deliverables to execute\n")
            return
        
        print(f"\n📦 Found {len(all_deliverables)} deliverables to execute:")
        for d in all_deliverables:
            print(f"  - {d['type']}: {d['item']} for {d['contact']}")
        
        execute = input("\nExecute deliverables now? (y/n): ").strip().lower()
        if execute == 'y':
            # TODO: Integrate with deliverable_orchestrator.py
            print("✓ Deliverables queued for execution (integration pending)")
    
    def _print_summary(self, event_data: Dict[str, Any], contacts: List[Dict[str, Any]]):
        """Print final summary."""
        
        print("\n" + "="*70)
        print("📊 PROCESSING SUMMARY")
        print("="*70)
        print(f"\n🎉 Event: {event_data['name']} on {event_data['date']}")
        print(f"📍 Location: {event_data['location']}")
        print(f"\n👥 Contacts Processed: {len(contacts)}")
        
        high_priority = [c for c in contacts if c.get('enrichment_priority') == 'high']
        print(f"   - High Priority: {len(high_priority)}")
        print(f"   - Medium/General: {len(contacts) - len(high_priority)}")
        
        print(f"\n📁 Generated Files:")
        print(f"   - Individual Profiles: {len(contacts)} files in Knowledge/crm/individuals/")
        print(f"   - Event Log: Knowledge/crm/events/{event_data['date'][:7]}/{event_data['id']}.md")
        print(f"   - LinkedIn Messages: {len(contacts)} files in Knowledge/crm/follow-ups/")
        
        all_deliverables = sum(len(c.get('deliverables_queue', [])) for c in contacts)
        if all_deliverables:
            print(f"\n📦 Deliverables Queued: {all_deliverables}")
        
        print("\n" + "="*70 + "\n")


async def main():
    """Main entry point."""
    processor = NetworkingEventProcessor()
    await processor.run()


if __name__ == "__main__":
    # Missing import
    from datetime import timedelta
    
    asyncio.run(main())
