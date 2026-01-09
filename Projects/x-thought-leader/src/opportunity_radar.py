#!/usr/bin/env python3
"""
W5: Opportunity Radar for X Thought Leader Engine
Surfaces high-correlation engagement opportunities and provides brainstorming premises.
Replaces the old automatic draft generator.
"""

import sqlite3
import json
import uuid
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "db" / "tweets.db"
CONFIG_PATH = PROJECT_ROOT / "config"
POSITIONS_DB = Path("/home/workspace/N5/db/positions.db")

sys.path.insert(0, str(PROJECT_ROOT / "src"))
# Assuming position_matcher exists from previous system
from position_matcher import match_positions, get_position_context

class OpportunityRadar:
    """Surfaces engagement opportunities and brainstorms angles."""
    
    # Radar settings
    MIN_CORRELATION_SCORE = 0.6  # Adjusted threshold - 0.86 was too strict
    
    def __init__(self):
        self.voice_config = self._load_voice_config()
        self.voice_examples = self._load_voice_examples()
        
    def _load_voice_config(self) -> dict:
        """Load voice variants configuration."""
        config_file = CONFIG_PATH / "voice_variants.yaml"
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_voice_examples(self) -> str:
        """Load voice examples markdown."""
        examples_file = CONFIG_PATH / "voice_examples.md"
        if examples_file.exists():
            with open(examples_file) as f:
                return f.read()
        return ""
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
        
    def get_unalerted_opportunities(self, limit: int = 5) -> List[Dict]:
        """Get high-correlation tweets that haven't been alerted yet."""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT t.id, t.content, t.author_username, t.created_at,
                       t.correlation_score, t.status
                FROM tweets t
                LEFT JOIN alerts a ON t.id = a.tweet_id
                WHERE t.correlation_score >= ?
                  AND a.id IS NULL
                ORDER BY t.correlation_score DESC, t.created_at DESC
                LIMIT ?
            """, (self.MIN_CORRELATION_SCORE, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_positions_for_tweet(self, tweet_id: str) -> List[Dict]:
        """Get matched positions for a tweet."""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT position_id, position_title, similarity_score
                FROM position_correlations
                WHERE tweet_id = ?
                ORDER BY similarity_score DESC
                LIMIT 3
            """, (tweet_id,))
            return [dict(row) for row in cursor.fetchall()]

    def generate_premise(self, tweet: Dict, positions: List[Dict]) -> str:
        """Generate a brainstorming premise/angle for a tweet."""
        
        # Format positions context
        position_context = "\n".join([
            f"- [{p['position_id']}] {p['position_title']} (match: {p['similarity_score']:.2f})"
            for p in positions
        ])
        
        prompt = f"""You are V's "Twitter Radar" - a strategic engagement scout.
        
Analyze this tweet and suggest 3 distinct "premises" or angles V could use to reply.
DO NOT write the tweet. Write the *angle*.

ORIGINAL TWEET by @{tweet['author_username']}:
"{tweet['content']}"

V'S RELEVANT POSITIONS:
{position_context}

Output 3 short bullet points. Each should be a "Premise" - a core idea to riff on.
Format:
- [Stance]: [Core Idea]

Examples:
- Support: Agree with the premise but pivot to how this applies specifically to non-technical founders.
- Challenge: Push back on the idea that X is necessary; cite your experience with Y.
- Amplify: "This is exactly why..." - connect it to the broader trend of Z.

Keep it punchy. V needs to read this in 5 seconds and start writing."""

        return self._call_llm(prompt)

    def generate_draft(self, tweet_id: str, instruction: str = "") -> str:
        """Generate a full draft on demand (with optional instruction)."""
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM tweets WHERE id = ?", (tweet_id,))
            tweet = dict(cursor.fetchone())
            positions = self.get_positions_for_tweet(tweet_id)
            
        position_context = "\n".join([
            f"- {p['position_title']}" for p in positions
        ])
        
        prompt = f"""Write a tweet reply for V.

ORIGINAL TWEET by @{tweet['author_username']}:
"{tweet['content']}"

CONTEXT:
{position_context}

INSTRUCTION:
{instruction if instruction else "Write a high-impact reply in V's voice."}

V'S VOICE:
- Direct, confident, slightly edgy.
- Uses em-dashes, slash-stacking (X/Y/Z).
- No hashtags.

Draft:"""

        return self._call_llm(prompt)

    def _call_llm(self, prompt: str) -> str:
        """Call LLM via Zo API."""
        import subprocess
        
        # Simple wrapper to call Zo's self-ask API via python one-liner
        # Using a safer way to pass the prompt than f-string injection in bash
        script = f'''
import requests
import os
import sys
import json

prompt = """{prompt.replace('"', '\\"')}"""

try:
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={{
            "authorization": os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", ""),
            "content-type": "application/json"
        }},
        json={{"input": prompt}}
    )
    if response.status_code == 200:
        print(response.json().get("output", ""))
    else:
        sys.exit(1)
except Exception as e:
    sys.exit(1)
'''
        result = subprocess.run(
            ["python3", "-c", script],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def create_alert(self, tweet_id: str) -> str:
        """Record that an alert was generated for this tweet."""
        alert_id = str(uuid.uuid4())
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO alerts (id, tweet_id, status)
                VALUES (?, ?, 'pending')
            """, (alert_id, tweet_id))
            conn.commit()
        return alert_id

    def mark_alert_sent(self, alert_id: str):
        """Mark alert as sent."""
        with self._get_conn() as conn:
            conn.execute("UPDATE alerts SET status = 'sent' WHERE id = ?", (alert_id,))
            conn.commit()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="X Opportunity Radar")
    parser.add_argument("--scan", action="store_true", help="Scan for new opportunities")
    parser.add_argument("--draft", help="Generate draft for tweet ID")
    parser.add_argument("--instruction", help="Instruction for draft generation")
    
    args = parser.parse_args()
    radar = OpportunityRadar()
    
    if args.scan:
        opps = radar.get_unalerted_opportunities()
        if not opps:
            print("No new high-correlation opportunities.")
            return

        print(f"Found {len(opps)} new opportunities.")
        for opp in opps:
            positions = radar.get_positions_for_tweet(opp['id'])
            print(f"\n--- Opportunity: @{opp['author_username']} ---")
            print(f"Tweet: \"{opp['content'][:100]}...\"")
            print(f"Score: {opp['correlation_score']:.2f}")
            
            print("Brainstorming angles...")
            premise = radar.generate_premise(opp, positions)
            print(premise)
            
            # Create alert record
            radar.create_alert(opp['id'])
            
    elif args.draft:
        print(f"Generating draft for {args.draft}...")
        draft = radar.generate_draft(args.draft, args.instruction)
        print("\n--- DRAFT ---")
        print(draft)

if __name__ == "__main__":
    main()



