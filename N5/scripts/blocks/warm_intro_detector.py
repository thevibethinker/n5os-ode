#!/usr/bin/env python3
"""
Warm Intro Detector
Detects warm introduction opportunities from meetings using LLM-based analysis.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


async def generate_warm_intros(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> int:
    """
    Detect warm introduction opportunities using LLM analysis.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata (must include meeting_folder_path)
        output_dir: Directory to write output file
        
    Returns:
        Number of warm intros detected
    """
    from openai import AsyncOpenAI
    
    # Load system prompt for LLM detection
    detection_prompt = """You are analyzing a meeting transcript to detect warm introduction promises.

A warm intro opportunity exists when someone EXPLICITLY:
- Offers to introduce one person to another ("I can introduce you to...")
- Promises to make a connection ("Let me connect you with...")
- States they will facilitate a meeting ("I'll set up a call with...")

Extract ONLY explicit promises, not vague possibilities like "you should meet..." or "I know someone who..."

For each warm intro detected, extract:
- promised_by: Who is making the intro (name)
- promised_to: Who is receiving the intro (name)
- target: Who they're being introduced to (name and/or organization)
- context: Why/what for (1-2 sentences)
- timeline: Any mentioned timeframe (or "unspecified")

Return JSON array of warm intros. If none found, return empty array []."""

    try:
        client = AsyncOpenAI()
        
        # Call LLM for detection
        response = await client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {"role": "system", "content": detection_prompt},
                {"role": "user", "content": f"Meeting transcript:\n\n{transcript}"}
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        warm_intros = result.get("warm_intros", [])
        
        if not warm_intros:
            logger.info("No warm intros detected in meeting")
            return 0
        
        # Enrich with meeting metadata
        for intro in warm_intros:
            intro["meeting_id"] = meeting_info.get("meeting_id", "unknown")
            intro["meeting_date"] = meeting_info.get("meeting_date", datetime.now().strftime("%Y-%m-%d"))
            intro["detected_at"] = datetime.now().isoformat()
        
        # Write to output file
        output_file = output_dir / "B07_WARM_INTRO_BIDIRECTIONAL.json"
        with open(output_file, "w") as f:
            json.dump({
                "warm_intros": warm_intros,
                "count": len(warm_intros),
                "meeting_metadata": {
                    "meeting_id": meeting_info.get("meeting_id"),
                    "meeting_date": meeting_info.get("meeting_date"),
                    "meeting_type": meeting_info.get("meeting_type")
                }
            }, f, indent=2)
        
        logger.info(f"✓ Detected {len(warm_intros)} warm intro(s), wrote to {output_file}")
        
        # Store in database if meeting_folder_path provided
        meeting_folder = meeting_info.get("meeting_folder_path")
        if meeting_folder:
            await _store_in_database(warm_intros, meeting_folder)
        
        return len(warm_intros)
        
    except Exception as e:
        logger.error(f"Error detecting warm intros: {e}", exc_info=True)
        return 0


async def _store_in_database(warm_intros: List[Dict[str, Any]], meeting_folder: str) -> None:
    """
    Store warm intros in profiles.db
    
    Args:
        warm_intros: List of detected warm intro opportunities
        meeting_folder: Path to meeting folder for reference
    """
    import sqlite3
    from pathlib import Path
    
    db_path = Path("/home/workspace/N5/data/profiles.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure warm_intros table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warm_intros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_folder TEXT NOT NULL,
                meeting_id TEXT,
                meeting_date TEXT,
                promised_by TEXT NOT NULL,
                promised_to TEXT NOT NULL,
                target TEXT NOT NULL,
                target_org TEXT,
                context TEXT,
                timeline TEXT,
                status TEXT DEFAULT 'pending',
                detected_at TEXT NOT NULL,
                completed_at TEXT,
                notes TEXT
            )
        """)
        
        # Insert each warm intro
        for intro in warm_intros:
            cursor.execute("""
                INSERT INTO warm_intros (
                    meeting_folder, meeting_id, meeting_date,
                    promised_by, promised_to, target, target_org,
                    context, timeline, detected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meeting_folder,
                intro.get("meeting_id"),
                intro.get("meeting_date"),
                intro.get("promised_by"),
                intro.get("promised_to"),
                intro.get("target"),
                intro.get("target_org", ""),
                intro.get("context", ""),
                intro.get("timeline", "unspecified"),
                intro.get("detected_at")
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Stored {len(warm_intros)} warm intro(s) in profiles.db")
        
    except Exception as e:
        logger.error(f"Error storing warm intros in database: {e}", exc_info=True)
