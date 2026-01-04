"""
Morning Digest (MorningOS v2)
-----------------------------
The ONE daily digest that moves the needle.

Sections:
1. Bio-Context: Sleep quality, resting HR, health advisory
2. Today's Workout: Training plan with coaching
3. The Landscape: Today's calendar events
4. Top 3 Today: Highest-priority action items
5. Reconnects: 2-3 people to reach out to
6. The Nudge: CTA to start morning flow

Rules: See N5/prefs/operations/digest-rules.md

Usage:
    python3 morning_digest.py [--dry-run] [--email] [--date YYYY-MM-DD]
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

# Add workspace to path for N5 lib imports
sys.path.insert(0, '/home/workspace')
from N5.lib.paths import (
    N5_ROOT, N5_DIGESTS_DIR, PRODUCTIVITY_DB, WORKOUTS_DB, WELLNESS_DB
)

# CRM database path
CRM_DB_PATH = N5_ROOT / "data" / "crm_v3.db"
LISTS_DIR = Path("/home/workspace/Lists")

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

    async def get_top_3_today(self):
        """Module 4: Top 3 Today (highest-priority action items)"""
        items = []

        try:
            # Source 1: must-contact.jsonl
            must_contact_path = LISTS_DIR / "must-contact.jsonl"
            if must_contact_path.exists():
                with open(must_contact_path, 'r') as f:
                    for line in f:
                        try:
                            item = json.loads(line.strip())
                            priority = item.get('priority', 'L')
                            # Fix 1: Accept H or M priority (was H-only)
                            if item.get('status') == 'open' and priority in ('H', 'M'):
                                items.append({
                                    'title': item.get('title', 'Untitled'),
                                    'context': item.get('body', '')[:100] + '...' if len(item.get('body', '')) > 100 else item.get('body', ''),
                                    'source': 'must-contact',
                                    'created': item.get('created_at', ''),
                                    'priority': priority
                                })
                        except json.JSONDecodeError:
                            continue

            # Source 2: ideas.jsonl (high priority with urgent tags)
            ideas_path = LISTS_DIR / "ideas.jsonl"
            if ideas_path.exists():
                with open(ideas_path, 'r') as f:
                    for line in f:
                        try:
                            item = json.loads(line.strip())
                            tags = item.get('tags', [])
                            priority = item.get('priority', 'L')
                            # Fix 1: Accept H or M priority with urgent tags
                            if priority in ('H', 'M') and any(t in tags for t in ['today', 'urgent', 'now']):
                                items.append({
                                    'title': item.get('title', 'Untitled'),
                                    'context': item.get('body', '')[:100] + '...' if len(item.get('body', '')) > 100 else item.get('body', ''),
                                    'source': 'ideas',
                                    'created': item.get('created_at', ''),
                                    'priority': priority
                                })
                        except json.JSONDecodeError:
                            continue

            # Sort by priority (H first) then created date (FIFO)
            items.sort(key=lambda x: (0 if x.get('priority') == 'H' else 1, x.get('created', '')))
            top_items = items[:3]

            # Fix 2: Data freshness warning
            if top_items:
                oldest_created = min((x.get('created', '')[:10] for x in top_items if x.get('created')), default='')
                if oldest_created:
                    try:
                        oldest_date = datetime.datetime.strptime(oldest_created, "%Y-%m-%d").date()
                        days_old = (self.today - oldest_date).days
                        if days_old > 7:
                            logger.warning(f"Top 3 Today items are {days_old} days old - consider refreshing lists")
                    except ValueError:
                        pass

            # Fix 3: Graceful degradation
            if not top_items:
                return "✨ No urgent items today. Protect this clarity or review your lists."

            formatted = []
            for item in top_items:
                formatted.append(f"- **{item['title']}**\n  {item['context']}\n  *(from {item['source']})*")

            return "\n\n".join(formatted)

        except Exception as e:
            logger.error(f"Top 3 Today fetch failed: {e}")
            return "Action items unavailable."

    async def get_reconnects(self):
        """Module 5: Reconnects (2-3 people to reach out to)"""
        try:
            if not CRM_DB_PATH.exists():
                return "CRM database not found. Run CRM setup."

            conn = sqlite3.connect(CRM_DB_PATH)
            cursor = conn.cursor()

            # Fix 4: Add last_suggested_at column if missing
            cursor.execute("PRAGMA table_info(profiles)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'last_suggested_at' not in columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN last_suggested_at DATE")
                conn.commit()

            # Fix 4: Exclude recently suggested contacts (within 7 days)
            cursor.execute("""
                SELECT name, category, last_contact_at, yaml_path, id
                FROM profiles
                WHERE last_contact_at IS NOT NULL
                  AND date(last_contact_at) < date('now', '-30 days')
                  AND category IN ('INVESTOR', 'NETWORKING', 'COMMUNITY', 'FOUNDER')
                  AND (last_suggested_at IS NULL OR date(last_suggested_at) < date('now', '-7 days'))
                ORDER BY last_contact_at ASC
                LIMIT 3
            """)

            rows = cursor.fetchall()
            
            # Fix 4: Update last_suggested_at for returned contacts
            if rows:
                profile_ids = [row[4] for row in rows]
                cursor.executemany(
                    "UPDATE profiles SET last_suggested_at = date('now') WHERE id = ?",
                    [(pid,) for pid in profile_ids]
                )
                conn.commit()
            
            conn.close()

            if not rows:
                return "Network is healthy. No reconnects needed this week."

            formatted = []
            for name, category, last_contact, yaml_path, profile_id in rows:
                # Calculate days since contact
                try:
                    last_date = datetime.datetime.strptime(last_contact, "%Y-%m-%d").date()
                    days_ago = (self.today - last_date).days
                    time_str = f"{days_ago} days ago"
                except:
                    time_str = "unknown"

                # Try to get context from yaml file
                context = ""
                if yaml_path:
                    yaml_full_path = Path("/home/workspace") / yaml_path
                    if yaml_full_path.exists():
                        try:
                            content = yaml_full_path.read_text()[:500]
                            # Extract title or first line as context
                            for line in content.split('\n'):
                                if line.startswith('title:') or line.startswith('# '):
                                    context = line.replace('title:', '').replace('#', '').strip()[:60]
                                    break
                        except:
                            pass

                cat_display = category.title() if category else "Contact"
                line = f"- **{name}** ({cat_display})\n  Last contact: {time_str}"
                if context:
                    line += f"\n  _{context}_"
                formatted.append(line)

            return "\n\n".join(formatted)

        except Exception as e:
            logger.error(f"Reconnects fetch failed: {e}")
            return "Reconnects unavailable. Check CRM data."

    async def get_bio_context(self):
        """Module 0: Bio-Context (Sleep + Vitals) from daily_wellness table"""
        try:
            conn = sqlite3.connect(WELLNESS_DB)
            cursor = conn.cursor()

            # Get most recent wellness data that has sleep data
            cursor.execute("""
                SELECT date, sleep_duration_hours, sleep_efficiency, resting_hr
                FROM daily_wellness
                WHERE sleep_duration_hours IS NOT NULL
                ORDER BY date DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()

            if not row:
                return "**Sleep data not synced yet.** Check Fitbit sync."

            date, sleep_hours, sleep_efficiency, resting_hr = row

            # Calculate advisory based on sleep quality
            advisory = ""
            if sleep_hours and sleep_hours < 6:
                advisory = "⚠️ **DEFICIT MODE:** <6hrs sleep. Protect focus, avoid big decisions, front-load caffeine before 2pm."
            elif sleep_efficiency and sleep_efficiency < 70:
                advisory = "⚠️ **LOW EFFICIENCY:** Poor sleep quality. Consider lighter cognitive load today."
            elif sleep_hours:
                advisory = "✅ **NOMINAL:** Sleep within healthy range. Full cognitive capacity available."
            else:
                advisory = "⚠️ **DATA INCOMPLETE:** Sleep data may be partial."

            # Format output
            duration_str = f"{sleep_hours:.1f}hrs" if sleep_hours else "--"
            efficiency_str = f"{sleep_efficiency}%" if sleep_efficiency else "--"
            hr_str = f"{resting_hr:.0f}" if resting_hr else "--"
            
            # Get nutrition status
            nutrition_status = await self.get_nutrition_status()

            return f"""**Last Night ({date}):**
| Sleep | {duration_str} | Efficiency | {efficiency_str} |
|-------|---------|------------|------------------|
| Resting HR | {hr_str} bpm | | |

{advisory}

{nutrition_status}"""

        except Exception as e:
            logger.error(f"Bio-context fetch failed: {e}")
            return "Bio-context unavailable. Check Fitbit sync."

    async def get_nutrition_status(self):
        """Get current stack count and recent BioLog mood pattern for nutrition summary."""
        try:
            # Count current supplements
            stack_path = Path("/home/workspace/Personal/Health/stack/current_supplements.yaml")
            stack_count = 0
            if stack_path.exists():
                content = stack_path.read_text()
                # Count YAML list items (lines starting with '  - name:')
                stack_count = content.count("- name:")
            
            # Get recent BioLog mood patterns (last 7 days)
            journal_db = Path("/home/workspace/N5/data/journal.db")
            mood_summary = ""
            if journal_db.exists():
                conn = sqlite3.connect(journal_db)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT mood, COUNT(*) as cnt
                    FROM bio_snapshots
                    WHERE created_at >= datetime('now', '-7 days')
                    AND mood IS NOT NULL AND mood != ''
                    GROUP BY mood
                    ORDER BY cnt DESC
                    LIMIT 3
                """)
                moods = cursor.fetchall()
                conn.close()
                
                if moods:
                    mood_summary = f"7-day mood: {', '.join([m[0] for m in moods])}"
            
            # Build nutrition line
            budget_emoji = "🟢" if stack_count <= 8 else "🟡" if stack_count <= 10 else "🔴"
            nutrition_line = f"**💊 Stack:** {stack_count}/10 {budget_emoji}"
            if mood_summary:
                nutrition_line += f" | {mood_summary}"
            
            return nutrition_line
            
        except Exception as e:
            logger.warning(f"Nutrition status fetch failed: {e}")
            return "**💊 Stack:** Unable to fetch"

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

    def generate_markdown(self, bio_context, workout, landscape, top_3_today, reconnects):
        """Generate the ONE daily digest markdown."""
        date_str = self.today.strftime("%A, %B %d")

        md = f"""# 🌅 Good Morning, V.
*{date_str}*

---

### 🧬 Bio-Context
{bio_context}

---

### 🏋️ Today's Workout
{workout}

---

### 🗺️ The Landscape
{landscape}

---

### 🎯 Top 3 Today
{top_3_today}

---

### 🤝 Reconnects
{reconnects}

---

### 🚀 The Nudge
**[▶️ START MORNING FLOW](https://va.zo.computer/chat?prompt=morning_flow)**
*(Clear Mind → Defend Time → Sync System)*

---
*Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET")}*
"""
        return md

    async def run(self, send=False, dry_run=False):
        logger.info("Generating Morning Digest (v2)...")

        # Run parallel data fetching - only the sections we need
        bio_context, workout, landscape, top_3_today, reconnects = await asyncio.gather(
            self.get_bio_context(),
            self.get_todays_workout(),
            self.get_landscape(),
            self.get_top_3_today(),
            self.get_reconnects()
        )

        content = self.generate_markdown(bio_context, workout, landscape, top_3_today, reconnects)

        # Save to file
        filename = f"morning-digest-{self.today.strftime('%Y-%m-%d')}.md"
        filepath = OUTPUT_DIR / filename

        if dry_run:
            logger.info(f"[DRY RUN] Would save to: {filepath}")
            print(content)
            return content

        filepath.write_text(content)
        logger.info(f"Digest saved to {filepath}")

        # Verify file was written
        if not filepath.exists() or filepath.stat().st_size == 0:
            logger.error(f"Failed to write digest to {filepath}")
            return None

        logger.info(f"Verified: {filepath} ({filepath.stat().st_size} bytes)")

        if send:
            logger.info("Sending email via Zo...")
            email_prompt = f"Send this markdown content as an email to me with subject '🌅 MorningOS: {self.today.strftime('%b %d')}'. Content:\n\n{content}"
            self._run_zo(email_prompt)

        return content

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate the ONE daily digest (MorningOS v2)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    parser.add_argument("--email", action="store_true", help="Send digest via email")
    parser.add_argument("--date", type=str, help="Target date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--json", action="store_true", help="Output JSON for automation")
    args = parser.parse_args()

    digest = MorningDigest()

    # Override date if specified
    if args.date:
        try:
            digest.today = datetime.date.fromisoformat(args.date)
            logger.info(f"Using date: {digest.today}")
        except ValueError:
            logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD.")
            sys.exit(1)

    if args.json:
        content = asyncio.run(digest.run(send=False, dry_run=args.dry_run))
        output_path = OUTPUT_DIR / f"morning-digest-{digest.today.strftime('%Y-%m-%d')}.md"
        print(json.dumps({
            "status": "success" if content else "error",
            "filepath": str(output_path),
            "date": digest.today.isoformat(),
            "dry_run": args.dry_run
        }))
    else:
        asyncio.run(digest.run(send=args.email, dry_run=args.dry_run))
















