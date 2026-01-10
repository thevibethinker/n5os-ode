#!/usr/bin/env python3
"""
Angles Generator for X Thought Leader Engine

Primary interface: surfaces angles, hooks, and cultural moments to spark V's own tweets.
Drafts are backup only — require V's spark first.

Philosophy: Build the muscle, don't outsource the creative work.
"""

import sqlite3
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "db" / "tweets.db"
CONFIG_PATH = PROJECT_ROOT / "config"
POSITIONS_DB = Path("/home/workspace/N5/data/positions.db")


class AnglesGenerator:
    """Generates creative angles and hooks for tweet engagement."""
    
    ANGLE_TYPES = [
        "flip",           # Invert the premise
        "lived",          # Your direct experience
        "proxy",          # What this is really about
        "spicy",          # Provocative take
        "systemic",       # Zoom out to system level
        "question",       # Socratic probe
    ]
    
    def __init__(self):
        self.voice_config = self._load_voice_config()
        self.positions = self._load_positions()
    
    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _load_voice_config(self) -> dict:
        config_file = CONFIG_PATH / "voice_variants.yaml"
        if not config_file.exists():
            return {}
        with open(config_file) as f:
            return yaml.safe_load(f)
    
    def _load_positions(self) -> list[dict]:
        """Load V's positions for context."""
        if not POSITIONS_DB.exists():
            return []
        
        conn = sqlite3.connect(POSITIONS_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT id as position_id, title, insight as core_claim, confidence
            FROM positions
            WHERE stability != 'superseded'
            ORDER BY confidence DESC
            LIMIT 50
        """)
        positions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return positions
    
    def get_tweet_with_positions(self, tweet_id: str) -> Optional[dict]:
        """Get tweet and its correlated positions."""
        with self._get_conn() as conn:
            # Get tweet
            cursor = conn.execute("""
                SELECT t.*, ma.username, ma.display_name
                FROM tweets t
                JOIN monitored_accounts ma ON t.account_id = ma.id
                WHERE t.id = ?
            """, (tweet_id,))
            tweet = cursor.fetchone()
            if not tweet:
                return None
            
            tweet_dict = dict(tweet)
            
            # Get correlated positions
            cursor = conn.execute("""
                SELECT pc.position_id, pc.position_title, pc.similarity_score
                FROM position_correlations pc
                WHERE pc.tweet_id = ?
                ORDER BY pc.similarity_score DESC
                LIMIT 5
            """, (tweet_id,))
            tweet_dict['positions'] = [dict(row) for row in cursor.fetchall()]
            
            return tweet_dict
    
    def generate_angles(self, tweet_id: str, use_llm: bool = True) -> dict:
        """
        Generate creative angles for a tweet.
        
        Returns dict with:
        - tweet: the original tweet
        - positions: correlated positions
        - angles: list of angle dicts with type, hook, and expansion
        - cultural_moments: topical references that could add weight
        """
        tweet_data = self.get_tweet_with_positions(tweet_id)
        if not tweet_data:
            return {"error": f"Tweet not found: {tweet_id}"}
        
        result = {
            "tweet_id": tweet_id,
            "tweet": {
                "author": f"@{tweet_data['username']}",
                "content": tweet_data['content'],
                "posted_at": tweet_data.get('created_at', tweet_data.get('posted_at', '')),
            },
            "positions": tweet_data['positions'],
            "angles": [],
            "cultural_moments": [],
            "draft_available": False,
        }
        
        if use_llm:
            llm_result = self._generate_angles_llm(tweet_data)
            result["angles"] = llm_result.get("angles", [])
            result["cultural_moments"] = llm_result.get("cultural_moments", [])
        else:
            # Mock mode
            result["angles"] = [
                {"type": "flip", "hook": "[Mock] Invert the premise", "expansion": "..."},
                {"type": "lived", "hook": "[Mock] Your 10 years in career coaching", "expansion": "..."},
                {"type": "spicy", "hook": "[Mock] Provocative framing", "expansion": "..."},
            ]
        
        return result
    
    def _generate_angles_llm(self, tweet_data: dict) -> dict:
        """Call LLM to generate angles."""
        position_context = "\n".join([
            f"- {p['position_title']} (score: {p['similarity_score']:.2f})"
            for p in tweet_data.get('positions', [])
        ])
        
        prompt = f"""You are helping V (Vrijen Attawar) develop angles for a tweet response.

V's background: 10 years career coaching, founder of Careerspan (AI-powered hiring), building in public, direct/spicy voice.

ORIGINAL TWEET by @{tweet_data['username']}:
"{tweet_data['content']}"

RELEVANT POSITIONS V HOLDS:
{position_context}

Generate 4-6 creative ANGLES (not full tweets) that V can riff on. Each angle should be a spark, not a finished product.

ANGLE TYPES to consider:
- flip: Invert or subvert the premise
- lived: Draw on V's direct experience (coaching, building Careerspan)
- proxy: What is this REALLY about underneath?
- spicy: Provocative or contrarian take
- systemic: Zoom out to system/incentive level
- question: Socratic probe that reframes

Also suggest 1-2 CULTURAL MOMENTS (current memes, recent events, zeitgeist references) that could make the response more topical/weighted.

Output as JSON:
{{
  "angles": [
    {{"type": "flip", "hook": "One-line hook", "expansion": "2-3 sentence expansion of the angle"}},
    ...
  ],
  "cultural_moments": [
    {{"reference": "Name of meme/moment", "connection": "How it connects to this tweet"}}
  ]
}}

JSON only, no markdown:"""

        result = subprocess.run(
            ["python3", "/home/workspace/N5/scripts/llm_call.py", prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return {"angles": [], "cultural_moments": [], "error": result.stderr}
        
        try:
            # Parse JSON from response
            response = result.stdout.strip()
            # Handle potential markdown wrapping
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response)
        except json.JSONDecodeError:
            return {"angles": [], "cultural_moments": [], "raw": result.stdout}
    
    def draft_from_spark(self, tweet_id: str, spark: str, variant: str = "authentic") -> str:
        """
        Generate a draft ONLY after V provides a spark/direction.
        
        This is the backup flow — V must provide initial creative direction.
        """
        tweet_data = self.get_tweet_with_positions(tweet_id)
        if not tweet_data:
            return f"[ERROR] Tweet not found: {tweet_id}"
        
        position_context = "\n".join([
            f"- {p['position_title']}"
            for p in tweet_data.get('positions', [])[:3]
        ])
        
        prompt = f"""Generate a tweet reply in V's voice.

ORIGINAL TWEET by @{tweet_data['username']}:
"{tweet_data['content']}"

V'S SPARK/DIRECTION:
"{spark}"

RELEVANT POSITIONS:
{position_context}

V's voice: Direct, specific, occasionally profane, uses em-dashes and parentheticals, 
draws on 10 years career coaching experience. Never corporate, never hedging.

Generate ONLY the tweet text (max 280 chars). Build on V's spark, don't replace it:"""

        result = subprocess.run(
            ["python3", "/home/workspace/N5/scripts/llm_call.py", prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return f"[LLM_ERROR] {result.stderr}"
        
        draft = result.stdout.strip()
        
        # Enforce char limit
        if len(draft) > 280:
            draft = draft[:277].rsplit(' ', 1)[0] + "..."
        
        return draft
    
    def format_angles_display(self, angles_result: dict) -> str:
        """Format angles for display."""
        if "error" in angles_result:
            return f"Error: {angles_result['error']}"
        
        lines = []
        
        # Tweet header
        tweet = angles_result["tweet"]
        lines.append(f"═══════════════════════════════════════════════════════")
        lines.append(f"📣 {tweet['author']}:")
        lines.append(f'"{tweet["content"]}"')
        lines.append("")
        
        # Position matches
        if angles_result["positions"]:
            lines.append("📍 POSITION MATCHES:")
            for p in angles_result["positions"][:3]:
                lines.append(f"   • {p['position_title']} ({p['similarity_score']:.0%})")
            lines.append("")
        
        # Angles
        lines.append("🎯 ANGLES:")
        for i, angle in enumerate(angles_result.get("angles", []), 1):
            lines.append(f"   [{angle.get('type', '?').upper()}] {angle.get('hook', '')}")
            if angle.get('expansion'):
                lines.append(f"      → {angle['expansion']}")
            lines.append("")
        
        # Cultural moments
        if angles_result.get("cultural_moments"):
            lines.append("🌍 CULTURAL MOMENTS:")
            for cm in angles_result["cultural_moments"]:
                lines.append(f"   • {cm.get('reference', '')}: {cm.get('connection', '')}")
            lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("💡 Pick an angle, riff on it. Draft backup: provide your spark.")
        
        return "\n".join(lines)
    
    def list_pending_tweets(self, min_score: float = 0.3, limit: int = 10) -> list[dict]:
        """List tweets awaiting engagement, sorted by position correlation."""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT DISTINCT 
                    t.id, t.content, t.created_at as posted_at,
                    ma.username, ma.display_name,
                    MAX(pc.similarity_score) as top_score,
                    COUNT(pc.position_id) as position_count
                FROM tweets t
                JOIN monitored_accounts ma ON t.account_id = ma.id
                JOIN position_correlations pc ON t.id = pc.tweet_id
                WHERE t.status IN ('new', 'correlated')
                  AND pc.similarity_score >= ?
                GROUP BY t.id
                ORDER BY top_score DESC
                LIMIT ?
            """, (min_score, limit))
            
            return [dict(row) for row in cursor.fetchall()]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate angles for tweet engagement")
    parser.add_argument("--tweet-id", help="Generate angles for specific tweet")
    parser.add_argument("--pending", action="store_true", help="List pending tweets")
    parser.add_argument("--min-score", type=float, default=0.3, help="Minimum correlation score")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM calls (mock mode)")
    parser.add_argument("--draft", help="Generate draft from your spark (requires --tweet-id)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    generator = AnglesGenerator()
    
    if args.pending:
        tweets = generator.list_pending_tweets(min_score=args.min_score)
        if args.json:
            print(json.dumps(tweets, indent=2))
        else:
            print(f"\n📋 PENDING TWEETS ({len(tweets)} with score >= {args.min_score}):\n")
            for t in tweets:
                print(f"  [{t['id'][:8]}] @{t['username']} ({t['top_score']:.0%} match, {t['position_count']} positions)")
                print(f"           \"{t['content'][:80]}...\"" if len(t['content']) > 80 else f"           \"{t['content']}\"")
                print()
    
    elif args.tweet_id and args.draft:
        # Draft from V's spark
        draft = generator.draft_from_spark(args.tweet_id, args.draft)
        print(f"\n📝 DRAFT (from your spark):\n")
        print(f"   {draft}")
        print(f"\n   [{len(draft)} chars]")
    
    elif args.tweet_id:
        # Generate angles
        result = generator.generate_angles(args.tweet_id, use_llm=not args.no_llm)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(generator.format_angles_display(result))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()







