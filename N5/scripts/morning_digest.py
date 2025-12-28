"""
Morning Digest Aggregator (MorningOS)
-------------------------------------
Aggregates data from multiple N5 systems into a single 8:00 AM briefing.

Modules:
1. The Wedge: Hook/Insight (from Morning Pages history or Quotes)
2. The Landscape: Calendar + Weather + Tide
3. The Loop: Open Threads (Email Follow-up Registry)
4. The Pulse: Productivity Stats (RPI, Emails Sent)
5. The Nudge: CTA to Morning Flow

Usage:
    python3 morning_digest.py [--dry-run] [--email]
"""

import sys
import os
import json
import datetime
import logging
import asyncio
import subprocess
import sqlite3
from pathlib import Path
import re

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
N5_ROOT = Path("/home/workspace/N5")
N5_ROOT = Path("/home/workspace/N5")
OUTPUT_DIR = Path("/home/workspace/N5/digests")
PROD_DB_PATH = Path("/home/workspace/productivity_tracker.db")

class MorningDigest:
    def __init__(self):
        self.today = datetime.date.today()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
    def _run_zo(self, prompt, schema=None):
        """Helper to call Zo CLI. Always returns clean output text."""
        cmd = ["zo", prompt]
        if schema:
            cmd.extend(["--output-format", json.dumps(schema)])
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                logger.error(f"Zo CLI error: {result.stderr}")
                return None
            
            # Zo CLI always returns JSON: {"output": "...", "conversation_id": "..."}
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    if schema:
                        # When schema requested, the output field contains the structured data
                        output = data.get("output", "")
                        if isinstance(output, str):
                            try:
                                return json.loads(output)
                            except json.JSONDecodeError:
                                return None
                        return output
                    else:
                        # No schema - just extract the text output
                        text = data.get("output", "").strip()
                        # Strip Zo timestamp artifacts (e.g., "---\n*2025-12-15 00:40 ET*")
                        text = re.sub(r'\n*---\n\*\d{4}-\d{2}-\d{2}.*ET\*\s*$', '', text)
                        return text.strip()
                return data
            except json.JSONDecodeError:
                # Fallback if not JSON
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.error("Zo CLI timed out")
            return None
        except Exception as e:
            logger.error(f"Zo CLI execution failed: {e}")
            return None

    async def get_wedge(self):
        """Module 1: The Wedge (Hook/Insight)"""
        # Ask Zo for a quote or insight
        prompt = "Give me a short, inspiring quote for the morning. Just the quote and author."
        quote = self._run_zo(prompt)
        return quote or "Focus on the signal, ignore the noise."

    async def get_landscape(self):
        """Module 2: The Landscape (Calendar)"""
        # Schema for calendar events
        schema = {
            "type": "object",
            "properties": {
                "events": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "time": {"type": "string", "description": "HH:MM format"},
                            "summary": {"type": "string"}
                        },
                        "required": ["time", "summary"]
                    }
                }
            },
            "required": ["events"]
        }
        
        prompt = f"Check my Google Calendar for today ({self.today}). List the events."
        data = self._run_zo(prompt, schema)
        
        if not data or not data.get("events"):
            return "No events scheduled for today."
            
        formatted = []
        for e in data["events"]:
            formatted.append(f"- **{e['time']}**: {e['summary']}")
        return "\n".join(formatted)

    async def get_loop(self):
        """Module 3: The Loop (Open Threads)"""
        # Placeholder for EmailFollowupRegistry integration
        # In the future, this will query N5/data/email_followup.db
        return "*(Open Thread Tracking System initializing...)*"

    async def get_pulse(self):
        """Module 4: The Pulse (Stats)"""
        try:
            conn = sqlite3.connect(PROD_DB_PATH)
            cursor = conn.cursor()
            # Try to get yesterday's stats
            yesterday = self.today - datetime.timedelta(days=1)
            cursor.execute("SELECT rpi, emails_sent FROM daily_stats WHERE date = ?", (yesterday.isoformat(),))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                rpi = row[0] if row[0] is not None else "--"
                emails = row[1] if row[1] is not None else "--"
                return f"**Yesterday:** RPI {rpi} | Emails Sent {emails}"
            else:
                return "No data for yesterday."
        except Exception as e:
            logger.error(f"DB Error: {e}")
            return "Stats unavailable."

    async def get_events(self):
        """Get must-go events from the recommender."""
        try:
            result = subprocess.run(
                ["python3", str(Path(__file__).parent / "event_recommender.py"), 
                 "--format", "digest", "--days", "30", "--top", "5"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return "No must-go events this week. Check the [Events Calendar](https://events-calendar-va.zocomputer.io) for all options."
        except Exception as e:
            logger.error(f"Events fetch failed: {e}")
            return "Events unavailable."

    async def get_life_counter(self):
        """Module 5: The Habit Tracker (Life Counter summary)"""
        try:
            # Get yesterday's summary
            yesterday = (self.today - datetime.timedelta(days=1)).isoformat()
            
            result = subprocess.run(
                ["python3", str(N5_ROOT / "scripts" / "life_counter.py"), "stats", "--days", "1"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse the stats output
                lines = result.stdout.strip().split('\n')
                habits = []
                for line in lines:
                    if '│' in line and ('✅' in line or '⚠️' in line):
                        habits.append(line.strip())
                
                if habits:
                    return "**Yesterday's Habits:**\n" + "\n".join(habits)
                else:
                    return "No habits logged yesterday."
            return "No habit data available."
        except Exception as e:
            logger.error(f"Life Counter fetch failed: {e}")
            return "Habit tracker unavailable."

    def generate_markdown(self, wedge, landscape, loop, pulse, events=None, life_counter=None):
        date_str = self.today.strftime("%A, %B %d")
        
        events_section = ""
        if events:
            events_section = f"""
---

### 🎟️ Must-Go Events
{events}
"""
        
        life_counter_section = ""
        if life_counter:
            life_counter_section = f"""
---

### 📊 The Habit Tracker
{life_counter}
"""
        
        md = f"""
# 🌅 Good Morning, V.
*{date_str}*

---

### 🧠 The Wedge
> {wedge}

---

### 🗺️ The Landscape
{landscape}

---

### 🔄 The Loop
{loop}

---

### 💓 The Pulse
{pulse}
{life_counter_section}{events_section}
---

### 🚀 The Nudge
**[▶️ START MORNING FLOW](https://va.zo.computer/chat?prompt=morning_flow)**
*(Clear Mind → Defend Time → Sync System)*
"""
        return md

    async def run(self, send=False):
        logger.info("Generating Morning Digest...")
        
        # Run parallel data fetching
        wedge, landscape, loop, pulse, events, life_counter = await asyncio.gather(
            self.get_wedge(),
            self.get_landscape(),
            self.get_loop(),
            self.get_pulse(),
            self.get_events(),
            self.get_life_counter()
        )
        
        content = self.generate_markdown(wedge, landscape, loop, pulse, events, life_counter)
        
        # Save to file
        filename = f"morning-digest-{self.today.strftime('%Y-%m-%d')}.md"
        filepath = OUTPUT_DIR / filename
        filepath.write_text(content)
        logger.info(f"Digest saved to {filepath}")
        
        if send:
            logger.info("Sending email via Zo...")
            # Use Zo CLI to send the email
            email_prompt = f"Send this markdown content as an email to me with subject '🌅 MorningOS: {self.today.strftime('%b %d')}'. Content:\n\n{content}"
            self._run_zo(email_prompt)
            
        return content

if __name__ == "__main__":
    digest = MorningDigest()
    
    if "--json" in sys.argv:
        # JSON output mode for agent consumption
        import json as json_mod
        content = asyncio.run(digest.run(send=False))
        output_path = OUTPUT_DIR / f"morning-digest-{digest.today.strftime('%Y-%m-%d')}.md"
        print(json_mod.dumps({
            "status": "success",
            "filepath": str(output_path),
            "date": digest.today.isoformat()
        }))
    else:
        asyncio.run(digest.run(send="--email" in sys.argv))









