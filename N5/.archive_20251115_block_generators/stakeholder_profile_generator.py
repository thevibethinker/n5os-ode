#!/usr/bin/env python3
"""
Stakeholder Profile Generator (LLM-powered)
Builds comprehensive stakeholder profiles using LLM.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
import sqlite3
from blocks.llm_client import get_client

logger = logging.getLogger(__name__)

# --- CRM Database Integration ---
WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "Knowledge" / "crm" / "crm.db"

def get_db_conn():
    """Get database connection with Row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def upsert_individual(conn, individual):
    """
    Insert or update individual record.
    Returns individual_id.
    """
    cursor = conn.cursor()
    
    if individual.get('email'):
        cursor.execute("SELECT id FROM individuals WHERE email = ?", (individual['email'],))
    else:
        cursor.execute("SELECT id FROM individuals WHERE full_name = ?", (individual['full_name'],))
    
    row = cursor.fetchone()
    
    if row:
        individual_id = row['id']
        # Build SET clauses dynamically for fields that are present
        updates = []
        params = []
        for key in ['title', 'company', 'email', 'primary_category', 'status', 'tags', 'notes', 'markdown_file_path']:
            if key in individual and individual[key] is not None:
                updates.append(f"{key} = ?")
                params.append(individual[key])
        
        if updates:
            params.append(individual_id)
            cursor.execute(f"UPDATE individuals SET {', '.join(updates)} WHERE id = ?", tuple(params))
    else:
        cursor.execute("""
            INSERT INTO individuals (
                full_name, title, company, email, 
                primary_category, status, tags, source_type,
                notes, markdown_file_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            individual['full_name'], individual.get('title'), individual.get('company'),
            individual.get('email'), individual.get('primary_category', 'other'),
            individual.get('status', 'prospect'), individual.get('tags'),
            individual.get('source_type'), individual.get('notes'),
            individual.get('markdown_file_path')
        ))
        individual_id = cursor.lastrowid
    
    return individual_id

async def _update_crm_database(stakeholder_name: str, profile_content: str, profile_path: Path):
    """
    Update the CRM database with the generated stakeholder profile content.
    This enriches an existing individual record.
    """
    logger.info(f"Updating CRM database for stakeholder: {stakeholder_name}")
    conn = get_db_conn()
    try:
        individual_data = {
            'full_name': stakeholder_name,
            'notes': profile_content,
            'markdown_file_path': str(profile_path.relative_to(WORKSPACE))
        }
        
        individual_id = upsert_individual(conn, individual_data)
        conn.commit()
        logger.info(f"Successfully updated/enriched stakeholder '{stakeholder_name}' (ID: {individual_id}) in CRM database.")

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to update stakeholder profile in CRM database: {e}", exc_info=True)
    finally:
        conn.close()

# -----------------------------

async def generate_stakeholder_profile(
    transcript: str,
    meeting_info: Dict[str, Any],
    meeting_history: List[Dict],
    meeting_types: List[str],
    output_dir: Path
) -> bool:
    """
    Generate stakeholder profile using LLM.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        meeting_history: Previous meetings with stakeholder
        meeting_types: Types of meeting
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Generating stakeholder profile using LLM")
        
        llm = get_client()
        
        stakeholder = meeting_info.get('stakeholder_primary', 'Unknown')
        
        system_prompt = """You are an expert at building comprehensive stakeholder profiles from meeting transcripts.

Extract and organize:
1. **Background**: Current role, company, professional background, relevant experience
2. **Interests & Focus Areas**: What they care about, what they're working on
3. **Pain Points & Challenges**: Problems they're facing, obstacles mentioned
4. **Opportunities & Needs**: What they're looking for, gaps they want to fill
5. **Key Quotes**: Notable or revealing statements (select 2-3 most meaningful)
6. **Relationship Notes**: Communication style, preferences, connection points

Be specific and factual. Quote directly when appropriate."""

        date = meeting_info.get('date', 'Unknown')
        relationship_stage = "New" if len(meeting_history) == 0 else \
                           "Developing" if len(meeting_history) <= 2 else "Established"
        
        user_prompt = f"""Build a comprehensive profile for this stakeholder from the meeting transcript.

Stakeholder: {stakeholder}
Meeting Date: {date}
Meeting Type: {', '.join(meeting_types) if meeting_types else 'General'}
Previous Meetings: {len(meeting_history)}
Relationship Stage: {relationship_stage}

Transcript:
{transcript[:15000]}

Create a structured profile with:
- Background & Current Role
- Interests & Focus Areas  
- Pain Points & Challenges
- Opportunities & Needs
- Key Quotes (2-3 most meaningful)
- Relationship Context

Return in markdown format with clear sections and bullet points."""

        response = await llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=3000,
            temperature=0.5
        )
        
        # Format the response
        markdown = _format_profile_markdown(
            response, stakeholder, date, relationship_stage, meeting_history
        )
        
        # Write output
        output_path = output_dir / "stakeholder-profile.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        # NEW: Update CRM database
        await _update_crm_database(
            stakeholder_name=stakeholder,
            profile_content=response,  # The raw LLM response is the richest content
            profile_path=output_path
        )
        
        logger.info("Generated stakeholder profile")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate stakeholder profile: {e}", exc_info=True)
        return False


def _format_profile_markdown(
    content: str,
    stakeholder: str,
    date: str,
    relationship_stage: str,
    meeting_history: List[Dict]
) -> str:
    """Format profile content as structured markdown."""
    md = f"# Stakeholder Profile: {stakeholder}\n\n"
    md += f"**Last Updated**: {date}\n"
    md += f"**Relationship Stage**: {relationship_stage}\n"
    md += f"**Total Meetings**: {len(meeting_history) + 1}\n\n"
    md += "---\n\n"
    md += content
    return md
