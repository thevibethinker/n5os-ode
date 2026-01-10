#!/usr/bin/env python3
"""
W5: Draft Generator for X Thought Leader Engine
Generates 4 voice variants per tweet using position matching and V's voice config.
"""

import sqlite3
import json
import uuid
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "db" / "tweets.db"
CONFIG_PATH = PROJECT_ROOT / "config"
POSITIONS_DB = Path("/home/workspace/N5/db/positions.db")

sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, "/home/workspace/Integrations/Pangram")
from position_matcher import match_positions, get_position_context

# Pangram AI detection (optional but recommended)
try:
    from pangram_validator import PangramValidator, validate_text
    PANGRAM_AVAILABLE = True
except ImportError:
    PANGRAM_AVAILABLE = False


class DraftGenerator:
    """Generates tweet drafts in V's voice variants."""
    
    VARIANTS = ["supportive", "challenging", "spicy", "comedic"]
    MAX_CHARS = 280
    PANGRAM_THRESHOLD = 0.3  # 30% AI max to pass
    PANGRAM_MAX_RETRIES = 2  # Max regeneration attempts
    
    def __init__(self, pangram_enabled: bool = False):
        self.voice_config = self._load_voice_config()
        self.voice_examples = self._load_voice_examples()
        self.pangram_enabled = pangram_enabled and PANGRAM_AVAILABLE
        self.pangram_validator = None
        if self.pangram_enabled:
            self.pangram_validator = PangramValidator(threshold=self.PANGRAM_THRESHOLD)
        
    def _load_voice_config(self) -> dict:
        """Load voice variants configuration."""
        config_file = CONFIG_PATH / "voice_variants.yaml"
        with open(config_file) as f:
            return yaml.safe_load(f)
    
    def _load_voice_examples(self) -> str:
        """Load voice examples markdown."""
        examples_file = CONFIG_PATH / "voice_examples.md"
        with open(examples_file) as f:
            return f.read()
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _check_repetition(self, draft_content: str, conn: sqlite3.Connection) -> bool:
        """Check if draft is too similar to recently posted tweets."""
        cursor = conn.execute("""
            SELECT our_content FROM posted_tweets 
            ORDER BY posted_at DESC LIMIT 50
        """)
        recent = [row["our_content"].lower() for row in cursor.fetchall()]
        
        draft_lower = draft_content.lower()
        draft_words = set(draft_lower.split())
        
        for posted in recent:
            posted_words = set(posted.split())
            if len(draft_words & posted_words) / max(len(draft_words), 1) > 0.7:
                return True  # Too similar
        return False
    
    def _enforce_char_limit(self, text: str) -> str:
        """Enforce 280 character limit, trimming intelligently if needed."""
        if len(text) <= self.MAX_CHARS:
            return text
        
        truncated = text[:self.MAX_CHARS - 3].rsplit(' ', 1)[0] + "..."
        return truncated
    
    def _validate_pangram(self, text: str) -> tuple[bool, int, str]:
        """
        Validate text against Pangram AI detection.
        
        Returns: (passed, ai_percent, message)
        """
        if not self.pangram_enabled or not self.pangram_validator:
            return True, 0, "Pangram disabled"
        
        try:
            result = self.pangram_validator.check(text)
            return result.passed, result.ai_percent, f"{result.ai_percent}% AI"
        except Exception as e:
            return True, 0, f"Pangram error: {e}"
    
    def _generate_with_pangram_validation(
        self,
        prompt: str,
        variant: str,
        max_retries: int = None
    ) -> tuple[str, dict]:
        """
        Generate draft with Pangram validation and automatic retry.
        
        Returns: (draft_content, pangram_info)
        """
        if max_retries is None:
            max_retries = self.PANGRAM_MAX_RETRIES
        
        pangram_info = {
            "enabled": self.pangram_enabled,
            "attempts": [],
            "final_passed": None,
            "final_ai_percent": None
        }
        
        for attempt in range(max_retries + 1):
            draft_content = self._call_llm(prompt)
            draft_content = self._enforce_char_limit(draft_content)
            
            passed, ai_percent, msg = self._validate_pangram(draft_content)
            
            pangram_info["attempts"].append({
                "attempt": attempt + 1,
                "content": draft_content,
                "ai_percent": ai_percent,
                "passed": passed
            })
            
            if passed or not self.pangram_enabled:
                pangram_info["final_passed"] = passed
                pangram_info["final_ai_percent"] = ai_percent
                return draft_content, pangram_info
            
            if attempt < max_retries:
                # Modify prompt for retry with Pangram feedback
                prompt = self._add_pangram_feedback_to_prompt(
                    prompt, draft_content, ai_percent, attempt + 1
                )
        
        # Return best attempt (lowest AI score) if all failed
        best = min(pangram_info["attempts"], key=lambda x: x["ai_percent"])
        pangram_info["final_passed"] = False
        pangram_info["final_ai_percent"] = best["ai_percent"]
        return best["content"], pangram_info
    
    def _add_pangram_feedback_to_prompt(self, prompt: str, failed_draft: str, ai_percent: int, attempt: int) -> str:
        """Add Pangram feedback to prompt for retry generation."""
        feedback = f"""

---

PANGRAM AI DETECTION FEEDBACK (Attempt {attempt} failed: {ai_percent}% AI detected)

Your previous draft was flagged as AI-generated:
"{failed_draft}"

To pass Pangram (target: <30% AI), apply these fixes:
- Add specific numbers or dollar amounts
- Vary sentence length dramatically (include 2-4 word sentences)  
- Break template patterns with organic filler
- Add personality markers (profanity, self-deprecation, parentheticals)
- Replace generic references with specifics
- Use period after name in intro, not em-dash

Generate a MORE NATURAL version that sounds like authentic human writing.
Generate ONLY the tweet text, nothing else:"""
        
        return prompt + feedback
    
    def get_correlated_tweets(self, min_score: float = 0.3, limit: int = 10) -> list[dict]:
        """Get tweets with position correlations ready for drafting."""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT t.id, t.content, t.author_username, t.created_at,
                       t.correlation_score, t.status
                FROM tweets t
                WHERE t.status = 'correlated' 
                  AND t.correlation_score >= ?
                ORDER BY t.correlation_score DESC, t.created_at DESC
                LIMIT ?
            """, (min_score, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_positions_for_tweet(self, tweet_id: str) -> list[dict]:
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
    
    def build_generation_prompt(
        self,
        tweet_content: str,
        tweet_author: str,
        variant: str,
        positions: list[dict]
    ) -> str:
        """Build the generation prompt for Claude."""
        variant_config = self.voice_config.get('variants', {}).get(variant, {})
        generation_rules = self.voice_config.get('generation_rules', {})
        
        # Format positions context - use correct field names from position_correlations
        position_context = "\n".join([
            f"- [{p['position_id']}] {p['position_title']} (similarity: {p['similarity_score']:.2f})"
            for p in positions[:3]
        ])
        
        # Extract variant-specific guidance
        patterns = variant_config.get('patterns', [])
        patterns_str = "\n".join([f"  - {p}" for p in patterns[:5]])
        
        authentic_examples = variant_config.get('authentic_examples', [])
        examples_str = "\n".join([f'  "{ex}"' for ex in authentic_examples[:3]])
        
        avoid_list = variant_config.get('avoid', [])
        avoid_str = ", ".join(avoid_list) if avoid_list else "n/a"
        
        # Voice markers from generation rules
        voice_markers = generation_rules.get('voice_markers', {})
        preferred_punct = voice_markers.get('preferred_punctuation', [])
        preferred_structures = voice_markers.get('preferred_structures', [])
        finance_terms = voice_markers.get('finance_crossover_terms', [])
        
        anti_patterns = generation_rules.get('anti_patterns', [])
        anti_patterns_str = ", ".join([f'"{p}"' for p in anti_patterns[:6]])
        
        max_length = variant_config.get('max_length', 280)
        emoji_policy = variant_config.get('emoji_policy', 'rare')
        
        prompt = f"""Generate a tweet reply in V's authentic voice using the '{variant}' variant.

ORIGINAL TWEET by @{tweet_author}:
"{tweet_content}"

RELEVANT POSITIONS V HOLDS:
{position_context}

---

VARIANT: {variant.upper()}
Description: {variant_config.get('description', '')}
Stance: {variant_config.get('stance', '')}

PATTERN TEMPLATES (adapt, don't copy verbatim):
{patterns_str}

AUTHENTIC V EXAMPLES (match this energy):
{examples_str}

AVOID in this variant: {avoid_str}

---

V'S VOICE FINGERPRINT:
- Signature punctuation: Em-dash (—) for pivots, colon for setups, semicolon for parallels
- Signature structures: slash-stacking (X/Y/Z), *asterisk actions*, rhetorical escalation
- Finance crossover terms: {", ".join(finance_terms)}
- NEVER say: {anti_patterns_str}
- Emoji policy: {emoji_policy}

---

REFERENCE (V's actual voice):
{self.voice_examples[:1500]}

---

CONSTRAINTS:
- MUST be under {max_length} characters
- MUST sound authentically like V (confident, precise, slight edge)
- MUST connect to at least one of V's positions listed above
- Should engage with the original tweet's point
- No hashtags
- Add value — don't just agree

Generate ONLY the tweet text, nothing else:"""
        
        return prompt
    
    def generate_drafts_for_tweet(
        self,
        tweet_id: str,
        use_llm: bool = True
    ) -> list[dict]:
        """Generate all 4 variants for a single tweet."""
        with self._get_conn() as conn:
            # Idempotency check: skip if drafts already exist
            existing = conn.execute(
                "SELECT COUNT(*) FROM drafts WHERE tweet_id = ?", (tweet_id,)
            ).fetchone()[0]
            if existing > 0:
                raise ValueError(f"Drafts already exist for tweet {tweet_id}. Use --show-drafts to view.")
            
            cursor = conn.execute(
                "SELECT id, content, author_username FROM tweets WHERE id = ?",
                (tweet_id,)
            )
            tweet = cursor.fetchone()
            if not tweet:
                raise ValueError(f"Tweet {tweet_id} not found")
            
            positions = self.get_positions_for_tweet(tweet_id)
            if not positions:
                raise ValueError(f"No position correlations for tweet {tweet_id}")
            
            drafts = []
            position_ids = json.dumps([p["position_id"] for p in positions])
            
            for variant in self.VARIANTS:
                prompt = self.build_generation_prompt(
                    tweet["content"],
                    tweet["author_username"],
                    variant,
                    positions
                )
                
                if use_llm:
                    draft_content = self._call_llm(prompt)
                else:
                    draft_content = f"[{variant.upper()}] Mock draft for testing"
                
                draft_content = self._enforce_char_limit(draft_content)
                
                if self._check_repetition(draft_content, conn):
                    draft_content = f"[FLAGGED-REPETITION] {draft_content}"
                
                draft_id = str(uuid.uuid4())
                
                conn.execute("""
                    INSERT INTO drafts (id, tweet_id, variant, content, position_ids, generation_prompt)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (draft_id, tweet_id, variant, draft_content, position_ids, prompt))
                
                drafts.append({
                    "id": draft_id,
                    "tweet_id": tweet_id,
                    "variant": variant,
                    "content": draft_content,
                    "position_ids": position_ids
                })
            
            conn.execute(
                "UPDATE tweets SET status = 'drafted' WHERE id = ?",
                (tweet_id,)
            )
            conn.commit()
            
            return drafts
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM to generate draft. Uses Zo API if available."""
        import subprocess
        
        script = f'''
import requests
import os
import sys

response = requests.post(
    "https://api.zo.computer/zo/ask",
    headers={{
        "authorization": os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", ""),
        "content-type": "application/json"
    }},
    json={{"input": """{prompt.replace('"', '\\"').replace('\n', '\\n')}"""}}
)

if response.status_code == 200:
    print(response.json().get("output", ""))
else:
    print(f"[LLM_ERROR] Status {{response.status_code}}", file=sys.stderr)
    sys.exit(1)
'''
        
        result = subprocess.run(
            ["python3", "-c", script],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return f"[LLM_ERROR] {result.stderr}"
        
        return result.stdout.strip()
    
    def get_drafts_for_tweet(self, tweet_id: str) -> list[dict]:
        """Retrieve existing drafts for a tweet."""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT id, tweet_id, variant, content, position_ids, generated_at
                FROM drafts WHERE tweet_id = ?
                ORDER BY variant
            """, (tweet_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def format_approval_message(self, tweet_id: str) -> str:
        """Format drafts for SMS approval."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT content, author_username FROM tweets WHERE id = ?",
                (tweet_id,)
            )
            tweet = cursor.fetchone()
            
            drafts = self.get_drafts_for_tweet(tweet_id)
            
            msg = f"@{tweet['author_username']}: \"{tweet['content'][:100]}...\"\n\n"
            
            for i, draft in enumerate(drafts, 1):
                variant_short = draft["variant"][0].upper()  # S, C, P, C
                msg += f"{i}({variant_short}): {draft['content']}\n\n"
            
            msg += "Reply 1-4 to post, SKIP to pass, or # + edit"
            return msg


def main():
    """CLI interface for draft generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate tweet drafts")
    parser.add_argument("--tweet-id", help="Generate drafts for specific tweet")
    parser.add_argument("--list-ready", action="store_true", help="List tweets ready for drafting")
    parser.add_argument("--min-score", type=float, default=0.3, help="Minimum correlation score")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM calls (mock mode)")
    parser.add_argument("--show-drafts", help="Show drafts for a tweet ID")
    parser.add_argument("--format-sms", help="Format approval SMS for tweet ID")
    parser.add_argument("--pangram", action="store_true", help="Enable Pangram AI detection validation")
    parser.add_argument("--pangram-check", help="Check existing draft against Pangram by draft ID")
    parser.add_argument("--pangram-test", help="Test text against Pangram (quick check)")
    
    args = parser.parse_args()
    generator = DraftGenerator(pangram_enabled=args.pangram)
    
    if args.list_ready:
        tweets = generator.get_correlated_tweets(min_score=args.min_score)
        print(f"Found {len(tweets)} tweets ready for drafting:\n")
        for t in tweets:
            print(f"  [{t['id']}] @{t['author_username']} (score: {t['correlation_score']:.2f})")
            print(f"    {t['content'][:80]}...")
            print()
    
    elif args.tweet_id:
        print(f"Generating drafts for tweet {args.tweet_id}...")
        drafts = generator.generate_drafts_for_tweet(args.tweet_id, use_llm=not args.no_llm)
        print(f"\nGenerated {len(drafts)} drafts:")
        for d in drafts:
            print(f"\n  [{d['variant'].upper()}]")
            print(f"  {d['content']}")
    
    elif args.show_drafts:
        drafts = generator.get_drafts_for_tweet(args.show_drafts)
        if not drafts:
            print("No drafts found for this tweet")
        else:
            for d in drafts:
                print(f"\n[{d['variant'].upper()}] ({d['id'][:8]})")
                print(f"{d['content']}")
    
    elif args.format_sms:
        msg = generator.format_approval_message(args.format_sms)
        print(msg)
    
    elif args.pangram_test:
        if not PANGRAM_AVAILABLE:
            print("Pangram not available. Check Integrations/Pangram/pangram_validator.py")
            sys.exit(1)
        passed, msg = validate_text(args.pangram_test)
        print(f"\n{msg}")
        print(f"Text: {args.pangram_test[:100]}..." if len(args.pangram_test) > 100 else f"Text: {args.pangram_test}")
        sys.exit(0 if passed else 1)
    
    elif args.pangram_check:
        if not PANGRAM_AVAILABLE:
            print("Pangram not available. Check Integrations/Pangram/pangram_validator.py")
            sys.exit(1)
        with generator._get_conn() as conn:
            cursor = conn.execute(
                "SELECT content, variant FROM drafts WHERE id LIKE ?",
                (f"{args.pangram_check}%",)
            )
            draft = cursor.fetchone()
            if not draft:
                print(f"Draft not found: {args.pangram_check}")
                sys.exit(1)
            
            passed, msg = validate_text(draft["content"])
            print(f"\n[{draft['variant'].upper()}] {msg}")
            print(f"Content: {draft['content']}")
            sys.exit(0 if passed else 1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()












