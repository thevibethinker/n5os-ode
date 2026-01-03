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
import duckdb

# Add workspace to path for N5 lib imports
sys.path.insert(0, '/home/workspace')
from N5.lib.paths import (
    N5_ROOT, N5_DIGESTS_DIR, PRODUCTIVITY_DB, WORKOUTS_DB, WELLNESS_DB
)

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants - use centralized paths
OUTPUT_DIR = N5_DIGESTS_DIR
PROD_DB_PATH = PRODUCTIVITY_DB
HEALTH_DB_PATH = WORKOUTS_DB

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

    async def get_crm_review(self):
        """Module 6: CRM Review (Profiles needing attention)"""
        try:
            result = subprocess.run(
                ['python3', '/home/workspace/N5/scripts/crm_review_flagging.py', '--digest'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return ""
        except Exception as e:
            logger.warning(f"CRM review failed: {e}")
            return ""

    async def get_bio_context(self):
        """Module 0: Bio-Context (Sleep + Vitals)"""
        try:
            con = duckdb.connect(str(HEALTH_DB_PATH), read_only=True)
            
            # Get last night's sleep (most recent)
            sleep_data = con.execute("""
                SELECT date, sleep_score, minutes_asleep, minutes_in_bed, raw_payload_json
                FROM daily_sleep
                WHERE date = (SELECT MAX(date) FROM daily_sleep)
            """).fetchone()
            
            # Get most recent resting HR
            hr_data = con.execute("""
                SELECT date, resting_hr
                FROM daily_resting_hr
                WHERE date = (SELECT MAX(date) FROM daily_resting_hr)
            """).fetchone()
            
            con.close()
            
            if not sleep_data:
                return "**Sleep data not synced yet.** Check Fitbit sync."
            
            date, sleep_score, minutes_asleep, minutes_in_bed, raw_json = sleep_data
            resting_hr = hr_data[1] if hr_data else "--"
            
            # Calculate hours from minutes
            hours_asleep = minutes_asleep / 60 if minutes_asleep else None
            
            # Try to parse efficiency from raw JSON
            efficiency = None
            deep_minutes = None
            rem_minutes = None
            try:
                if raw_json:
                    payload = json.loads(raw_json)
                    efficiency = payload.get('efficiency')
                    levels = payload.get('levels', {})
                    summary = levels.get('summary', {})
                    deep_minutes = summary.get('deep', {}).get('minutes')
                    rem_minutes = summary.get('rem', {}).get('minutes')
            except:
                pass
            
            # Calculate advisory based on sleep quality
            advisory = ""
            if hours_asleep and hours_asleep < 6:
                advisory = "⚠️ **DEFICIT MODE:** <6hrs sleep. Protect focus, avoid big decisions, front-load caffeine before 2pm."
            elif sleep_score and sleep_score < 70:
                advisory = "⚠️ **LOW SCORE:** Poor sleep quality. Consider lighter cognitive load today."
            elif efficiency and efficiency < 70:
                advisory = "⚠️ **LOW EFFICIENCY:** Poor sleep quality. Consider lighter cognitive load today."
            elif hours_asleep:
                advisory = "✅ **NOMINAL:** Sleep within healthy range. Full cognitive capacity available."
            else:
                advisory = "⚠️ **DATA INCOMPLETE:** Sleep data may be partial."
            
            # Format output
            duration_str = f"{hours_asleep:.1f}hrs" if hours_asleep else "--"
            score_str = f"{sleep_score:.0f}" if sleep_score else "--"
            efficiency_str = f"{efficiency}%" if efficiency else "--"
            deep_str = f"{deep_minutes}min" if deep_minutes else "--"
            rem_str = f"{rem_minutes}min" if rem_minutes else "--"
            
            return f"""**Last Night ({date}):**
| Sleep | {duration_str} | Score {score_str} | Efficiency {efficiency_str} |
|-------|---------|------|-------------|
| Deep | {deep_str} | REM | {rem_str} |
| Resting HR | {resting_hr} bpm | | |

{advisory}"""
            
        except Exception as e:
            logger.error(f"Bio-context fetch failed: {e}")
            return "Bio-context unavailable. Check Fitbit sync."

    async def get_todays_workout(self):
        """Module 7: Today's Workout (from 10K Prep Plan with Vibe Trainer coaching)"""
        try:
            # Get day of week
            day_name = self.today.strftime("%A")
            
            # 10K Prep Plan schedule (from Personal/Health/WorkoutTracker/10K_Prep_Plan.md)
            schedule = {
                "Monday": {
                    "type": "Strength (Phase 2 Ramp-Up)",
                    "duration": "45m",
                    "focus": "strength",
                    "coaching": "Focus on compound movements. Your ACTN3 TT profile means you recover slower from strength work—prioritize form over volume. Keep rest periods 90-120 seconds."
                },
                "Tuesday": {
                    "type": "Engine Building",
                    "duration": "30-40m",
                    "focus": "aerobic",
                    "coaching": "Target HR: 113-131 BPM. This should feel conversational—if you can't talk, slow down. Your genetics excel here; trust the easy pace."
                },
                "Wednesday": {
                    "type": "Recovery Walk / Mobility",
                    "duration": "20m",
                    "focus": "recovery",
                    "coaching": "Active recovery day. Light movement only—walk, stretch, foam roll. Your COMT GG profile needs deliberate recovery between hard sessions."
                },
                "Thursday": {
                    "type": "The 20% Interval",
                    "duration": "35m",
                    "focus": "intervals",
                    "coaching": "4x4 protocol: 4 mins HARD (151+ BPM), 3 mins EASY. This is your 20% high-intensity work. Push hard during work sets, recover fully between."
                },
                "Friday": {
                    "type": "Strength (Phase 2 Ramp-Up)",
                    "duration": "45m",
                    "focus": "strength",
                    "coaching": "Second strength session of the week. If resting HR is 5+ BPM above baseline, consider lighter weights. Protect tomorrow's long run."
                },
                "Saturday": {
                    "type": "Engine Building (Long)",
                    "duration": "50-60m",
                    "focus": "aerobic_long",
                    "coaching": "Your longest aerobic session of the week. Stay in Zone 2 (113-131 BPM). Build that aerobic base—this is where your ACTN3 TT genetics shine."
                },
                "Sunday": {
                    "type": "Rest / Light Walk",
                    "duration": "Optional",
                    "focus": "rest",
                    "coaching": "Full rest or very light walking only. Your body adapts during rest, not during training. Honor the recovery."
                }
            }
            
            workout = schedule.get(day_name, {
                "type": "Check Plan",
                "duration": "--",
                "focus": "unknown",
                "coaching": "Consult your 10K prep plan."
            })
            
            # Calculate days until race (Feb 28, 2026)
            race_date = datetime.date(2026, 2, 28)
            days_until_race = (race_date - self.today).days
            
            # Get recent workout from wellness.db for context
            recent_context = ""
            try:
                wellness_db = WELLNESS_DB
                if wellness_db.exists():
                    conn = sqlite3.connect(wellness_db)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT ll.timestamp, ll.duration_min, ll.avg_hr, ll.vest_weight_lb
                        FROM life_logs ll
                        JOIN life_categories lc ON ll.category_id = lc.id
                        WHERE lc.slug = 'workout' AND ll.timestamp >= date('now', '-2 days')
                        ORDER BY ll.timestamp DESC LIMIT 1
                    """)
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        last_time, last_dur, last_hr, vest = row
                        vest_note = f" (with {int(vest)}lb vest)" if vest else ""
                        recent_context = f"\n*Last workout: {last_dur:.0f}min, avg HR {last_hr:.0f} BPM{vest_note}*"
            except Exception as e:
                logger.warning(f"Could not fetch recent workout: {e}")
            
            return f"""**{workout['type']}** ({workout['duration']})

> 🏃 *Vibe Trainer:* {workout['coaching']}

📅 **{days_until_race} days until race day (Feb 28)**{recent_context}"""
            
        except Exception as e:
            logger.error(f"Workout fetch failed: {e}")
            return "Workout plan unavailable. Check `file 'Personal/Health/WorkoutTracker/10K_Prep_Plan.md'`"

    def generate_markdown(self, wedge, landscape, loop, pulse, events=None, life_counter=None, crm_review=None, bio_context=None, workout=None):
        date_str = self.today.strftime("%A, %B %d")
        
        # Bio-context section
        bio_context_section = ""
        if bio_context:
            bio_context_section = f"""
### 🧬 Bio-Context
{bio_context}

---

"""
        
        # Workout section (NEW)
        workout_section = ""
        if workout:
            workout_section = f"""
### 🏋️ Today's Workout
{workout}

---

"""
        
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
        
        # Add CRM review section handling
        crm_review_section = f"\n{crm_review}\n" if crm_review else ""
        
        md = f"""
# 🌅 Good Morning, V.
*{date_str}*

---

{bio_context_section}{workout_section}### 🧠 The Wedge
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
{life_counter_section}{events_section}{crm_review_section}
---

### 🚀 The Nudge
**[▶️ START MORNING FLOW](https://va.zo.computer/chat?prompt=morning_flow)**
*(Clear Mind → Defend Time → Sync System)*
"""
        return md

    async def run(self, send=False):
        logger.info("Generating Morning Digest...")
        
        # Run parallel data fetching - add workout
        bio_context, workout, wedge, landscape, loop, pulse, events, life_counter, crm_review = await asyncio.gather(
            self.get_bio_context(),
            self.get_todays_workout(),
            self.get_wedge(),
            self.get_landscape(),
            self.get_loop(),
            self.get_pulse(),
            self.get_events(),
            self.get_life_counter(),
            self.get_crm_review()
        )
        
        content = self.generate_markdown(wedge, landscape, loop, pulse, events, life_counter, crm_review, bio_context, workout)
        
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













