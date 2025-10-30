#!/usr/bin/env python3
"""
LinkedIn Commitment Extractor

Analyzes LinkedIn messages to extract commitments, promises, and action items.
Uses LLM to identify what V owes others and what others owe V.

Usage:
    linkedin_commitment_extractor.py [--batch-size=10] [--dry-run]

Version: 1.0.0
Created: 2025-10-30
"""

import sqlite3
import argparse
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import anthropic

# Paths
WORKSPACE = Path('/home/workspace')
DB_PATH = WORKSPACE / 'Knowledge/linkedin/linkedin.db'

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# LLM Client
def get_llm_client():
    """Initialize Anthropic client"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)

def extract_commitments_from_message(client: anthropic.Anthropic, message_content: str, sender: str, conversation_context: str = "") -> List[Dict[str, Any]]:
    """
    Use LLM to extract commitments from a message.
    
    Returns list of commitments with structure:
    {
        "commitment_type": "I_OWE_THEM" | "THEY_OWE_ME" | "MUTUAL" | "INFO_ONLY",
        "what": "description of commitment",
        "deadline": "YYYY-MM-DD" or null,
        "confidence": 0.0-1.0
    }
    """
    
    prompt = f"""Analyze this LinkedIn message and extract any commitments, promises, or action items.

Message from: {sender}
Message: {message_content}

{f"Conversation context: {conversation_context}" if conversation_context else ""}

Instructions:
1. Identify explicit commitments or promises (e.g., "I'll send you the link", "Can you review this?")
2. Categorize each commitment:
   - I_OWE_THEM: The user (Vrijen/V) promised or committed to do something
   - THEY_OWE_ME: The other person promised or committed to do something
   - MUTUAL: Both parties agreed to do something together
   - INFO_ONLY: Just sharing information, no commitment

3. Extract any mentioned deadlines (be generous with interpretation - "this week", "tomorrow", "soon")
4. Assign confidence score:
   - 1.0: Explicit commitment ("I will", "I'll send")
   - 0.7: Implied commitment ("let me check", "I can look into")
   - 0.5: Soft commitment ("maybe I can", "I should")
   - 0.3: Vague intent ("we should sometime")

5. Only extract meaningful commitments, not pleasantries

Return JSON array of commitments. If none found, return empty array [].

Example response format:
[
  {{
    "commitment_type": "I_OWE_THEM",
    "what": "Send the Careerspan pricing sheet",
    "deadline": "2025-11-01",
    "confidence": 1.0
  }},
  {{
    "commitment_type": "THEY_OWE_ME",
    "what": "Review the proposal and provide feedback",
    "deadline": null,
    "confidence": 0.8
  }}
]

Return only the JSON array, no other text."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text.strip()
        
        # Parse JSON response
        commitments = json.loads(content)
        
        # Validate structure
        if not isinstance(commitments, list):
            logger.warning(f"LLM returned non-list response: {content}")
            return []
        
        return commitments
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.error(f"Response was: {content}")
        return []
    except Exception as e:
        logger.error(f"LLM extraction error: {e}")
        return []

def process_pending_messages(batch_size: int = 10, dry_run: bool = False):
    """Process messages that need commitment extraction"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get messages needing extraction
    cursor.execute("""
        SELECT 
            m.id,
            m.conversation_id,
            m.sender,
            m.content,
            m.sent_at,
            c.participant_name
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE m.commitment_extraction_needed = 1
        ORDER BY m.sent_at DESC
        LIMIT ?
    """, (batch_size,))
    
    messages = cursor.fetchall()
    
    if not messages:
        logger.info("✅ No messages need extraction")
        conn.close()
        return
    
    logger.info(f"📝 Processing {len(messages)} message(s) for commitment extraction")
    
    if dry_run:
        logger.info("🧪 DRY RUN - No database changes will be made")
    
    client = get_llm_client()
    
    processed = 0
    extracted = 0
    
    for msg in messages:
        logger.info(f"Analyzing message {msg['id']} from {msg['sender']}")
        
        try:
            # Extract commitments
            commitments = extract_commitments_from_message(
                client,
                msg['content'],
                msg['sender'],
                conversation_context=f"Conversation with {msg['participant_name']}"
            )
            
            logger.info(f"  Found {len(commitments)} commitment(s)")
            
            if not dry_run:
                # Store commitments
                for cm in commitments:
                    # Parse deadline to timestamp if present
                    deadline_ts = None
                    if cm.get('deadline'):
                        try:
                            deadline_dt = datetime.fromisoformat(cm['deadline'])
                            deadline_ts = int(deadline_dt.timestamp() * 1000)
                        except:
                            pass
                    
                    cursor.execute("""
                        INSERT INTO commitments (
                            conversation_id,
                            message_id,
                            commitment_type,
                            what,
                            deadline,
                            deadline_timestamp,
                            status,
                            confidence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        msg['conversation_id'],
                        msg['id'],
                        cm['commitment_type'],
                        cm['what'],
                        cm.get('deadline'),
                        deadline_ts,
                        'PENDING',
                        cm.get('confidence', 1.0)
                    ))
                    extracted += 1
                
                # Mark message as extracted
                cursor.execute("""
                    UPDATE messages 
                    SET commitment_extraction_needed = 0,
                        commitment_extracted_at = ?
                    WHERE id = ?
                """, (int(datetime.now().timestamp() * 1000), msg['id']))
                
                conn.commit()
            
            processed += 1
            
        except Exception as e:
            logger.error(f"  Error processing message {msg['id']}: {e}")
            
            if not dry_run:
                # Mark extraction error
                cursor.execute("""
                    UPDATE messages
                    SET extraction_error = ?
                    WHERE id = ?
                """, (str(e), msg['id']))
                conn.commit()
    
    conn.close()
    
    logger.info(f"\n✅ Processed {processed}/{len(messages)} messages")
    logger.info(f"📌 Extracted {extracted} commitments")
    
    if dry_run:
        logger.info("🧪 Dry run complete - no changes made")

def main():
    parser = argparse.ArgumentParser(
        description='Extract commitments from LinkedIn messages using LLM'
    )
    
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of messages to process (default: 10)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without making database changes')
    
    args = parser.parse_args()
    
    if not DB_PATH.exists():
        logger.error(f"❌ Database not found: {DB_PATH}")
        sys.exit(1)
    
    try:
        process_pending_messages(args.batch_size, args.dry_run)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
