# W4: Email Worker Handoff
**Worker ID:** W4-EMAIL  
**Spawned From:** con_MuvXIR7jXZjZxlND (Build Orchestrator)  
**Dependencies:** W1 (Schema), W3 (Integration) must complete first  
**Estimated Time:** 50 minutes

---

## Your Mission

Build the **coaching email system** that sends Arsenal manager-voiced motivational alerts to V when his team status changes or warning thresholds are crossed.

You're creating the **voice of the Gaffer** - firm but motivational, data-driven but human, pushing V toward excellence.

---

## Context

V wants automated emails from an "Arsenal manager" persona that:
- Warn him when performance is slipping
- Celebrate promotions and achievements
- Provide motivation during tough stretches
- Use football/Arsenal terminology naturally
- Feel personal, not robotic

**Critical:** These emails represent the system's personality. Get the voice right.

---

## Deliverables

### 1. `coaching_email_system.py`

A module that:
- Generates context-aware email templates
- Integrates with Gmail API (V has `use_app_gmail` available)
- Implements rate limiting (max 1 email/day, configurable)
- Supports dry-run mode for testing
- Logs all emails sent

### 2. Email Templates (5 types)

**A. Status Change Emails**
```
Promotion: "Welcome to the First Team"
Demotion: "You've been dropped to Reserves"
```

**B. Warning Emails**
```
Performance Alert: "2 days away from demotion"
Streak Lost: "Your 14-day streak has ended"
```

**C. Achievement Emails**
```
Elite Unlock: "You've earned Invincible status"
Milestone: "30 days as First Team Starter"
```

**D. Weekly Summary** (optional)
```
Week in Review: Performance recap + next week outlook
```

**E. Motivation Emails**
```
Transfer List Warning: "Last chance to save your Arsenal career"
```

---

## Technical Requirements

### Gmail Integration
V has Gmail connected via `use_app_gmail`. Use it like this:

```python
# First, list available tools
tools = list_app_tools(app_slug="gmail")

# Then send email
use_app_gmail(
    tool_name="gmail-send-email",
    configured_props={
        "to": "va@zo.computer",  # V's email
        "subject": "[Arsenal Performance Alert] ...",
        "body": email_body_html,
        "bodyType": "html"  # Support HTML for formatting
    }
)
```

### Rate Limiting Logic
```python
class EmailRateLimiter:
    """Prevent email spam"""
    
    def should_send_email(self, email_type: str, last_sent: datetime) -> bool:
        # Max 1 status change email per day
        # Max 1 warning email per day
        # Achievement emails can override
        pass
    
    def get_last_sent(self, email_type: str) -> Optional[datetime]:
        # Query email_log table
        pass
```

### Dry-Run Mode
```python
class CoachingEmailSystem:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
    
    def send_email(self, template: EmailTemplate):
        if self.dry_run:
            print(f"[DRY-RUN] Would send: {template.subject}")
            print(template.body)
            # Log to file for V's review
        else:
            # Actually send via Gmail
            pass
```

---

## Voice Guidelines: The Arsenal Manager

**Tone Characteristics:**
- **Direct but supportive** - "You're better than this"
- **Data-driven** - References specific metrics
- **Football terminology** - "Clean sheet", "on the bench", "transfer window"
- **High standards** - Expects excellence, disappointed by mediocrity
- **Motivational** - Believes V can achieve more

**Examples:**

**Demotion Email:**
```
Subject: [Arsenal Performance Alert] Dropped to Reserves

Vrijen,

I've had to make a tough decision. Based on your recent performances, 
you're being moved to the Reserves effective immediately.

The numbers don't lie:
• Last 7 days: 78% average (need 90%+)
• 4 consecutive days below standard
• Expected output: 5 emails/day, delivered: 3.2/day

You've got the talent, but talent without output doesn't win matches. 
The First Team demands consistency. Show me 3 days of 90%+ performance 
and we'll talk about bringing you back.

The squad needs you. Time to prove you belong.

— The Gaffer
Arsenal Productivity FC
```

**Promotion Email:**
```
Subject: [Arsenal Performance Alert] ⭐ First Team Call-Up

Vrijen,

Outstanding work. You've earned your spot in the First Team.

Your performance over the last week has been exactly what this club 
demands:
• 128% average (top 5 of 7 days)
• 2 days above 125% (elite standard)
• 6-day streak of meeting expectations

This is where you belong. Now maintain it. The First Team isn't about 
one good week—it's about sustained excellence. Keep this standard and 
you'll be wearing the captain's armband before long.

Welcome back.

— The Gaffer
Arsenal Productivity FC
```

**Warning Email:**
```
Subject: [Arsenal Performance Alert] ⚠️ Performance Review

Vrijen,

You're 2 days away from being dropped to the Reserves. 

I know you can turn this around, but I need to see it on the pitch:
• Yesterday: 65% (need 90%)
• Today: 72% (need 90%)
• Tomorrow: MUST hit 90%+ or face demotion

No excuses. No explanations. Just results.

Show me what you're made of.

— The Gaffer
```

---

## Database Schema (from W1)

```sql
-- You'll read from these tables
CREATE TABLE team_status (
    date TEXT PRIMARY KEY,
    status TEXT NOT NULL,  -- 'transfer_list', 'reserves', etc.
    days_in_status INTEGER DEFAULT 1,
    previous_status TEXT,
    changed_at TIMESTAMP,
    reason TEXT
);

CREATE TABLE status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    from_status TEXT,
    to_status TEXT NOT NULL,
    reason TEXT,
    metrics TEXT,  -- JSON of performance data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- You'll write to this table
CREATE TABLE email_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_type TEXT NOT NULL,  -- 'demotion', 'promotion', 'warning', etc.
    subject TEXT NOT NULL,
    sent_to TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_trigger TEXT,  -- What status change triggered it
    dry_run BOOLEAN DEFAULT 0
);
```

---

## Module Structure

```python
# coaching_email_system.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict
import sqlite3
import json

@dataclass
class EmailTemplate:
    subject: str
    body: str
    email_type: str
    status_trigger: Optional[str] = None

class ArsenalCoach:
    """Generates coaching emails in Arsenal manager voice"""
    
    def demotion_email(self, current_status: str, metrics: Dict) -> EmailTemplate:
        """Generate demotion notification"""
        pass
    
    def promotion_email(self, new_status: str, metrics: Dict) -> EmailTemplate:
        """Generate promotion celebration"""
        pass
    
    def warning_email(self, days_until_demotion: int, metrics: Dict) -> EmailTemplate:
        """Generate performance warning"""
        pass
    
    def achievement_email(self, achievement: str, metrics: Dict) -> EmailTemplate:
        """Generate achievement celebration"""
        pass
    
    def weekly_summary(self, week_stats: Dict) -> EmailTemplate:
        """Generate weekly performance review"""
        pass

class EmailRateLimiter:
    """Prevents email spam"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def should_send(self, email_type: str) -> bool:
        """Check if email should be sent based on rate limits"""
        pass
    
    def log_email(self, template: EmailTemplate, dry_run: bool):
        """Record email in database"""
        pass

class CoachingEmailSystem:
    """Main interface for email system"""
    
    def __init__(self, db_path: str, dry_run: bool = True):
        self.db_path = db_path
        self.dry_run = dry_run
        self.coach = ArsenalCoach()
        self.rate_limiter = EmailRateLimiter(db_path)
    
    def send_status_change_email(self, from_status: str, to_status: str, metrics: Dict):
        """Send email for status changes"""
        pass
    
    def check_and_send_warnings(self):
        """Check if warnings should be sent"""
        pass
```

---

## Testing Requirements

### Unit Tests
```python
def test_demotion_email_contains_metrics():
    coach = ArsenalCoach()
    email = coach.demotion_email("reserves", {
        "avg_rpi": 78,
        "days_below": 4,
        "expected": 5.0,
        "actual": 3.2
    })
    assert "78%" in email.body
    assert "Reserves" in email.subject

def test_rate_limiter_blocks_duplicate_emails():
    limiter = EmailRateLimiter(":memory:")
    assert limiter.should_send("demotion") == True
    limiter.log_email(test_template, dry_run=False)
    assert limiter.should_send("demotion") == False  # Same day
```

### Integration Test
```python
def test_full_email_flow_dry_run():
    system = CoachingEmailSystem(db_path, dry_run=True)
    system.send_status_change_email(
        from_status="first_team",
        to_status="reserves",
        metrics={...}
    )
    # Verify dry-run logged, no actual email sent
```

---

## Configuration

Create `/home/workspace/N5/config/email_config.json`:
```json
{
    "dry_run": true,
    "rate_limits": {
        "status_change": 1,
        "warning": 1,
        "achievement": 3
    },
    "recipient": "va@zo.computer",
    "enabled_types": [
        "demotion",
        "promotion",
        "warning",
        "achievement"
    ]
}
```

---

## Return Artifacts

Create a summary document with:

```markdown
# W4 (Email Worker) - Completion Report

## Deliverables
- [x] coaching_email_system.py created
- [x] 5 email templates implemented
- [x] Gmail integration working
- [x] Rate limiting functional
- [x] Dry-run mode tested

## Sample Emails Generated
[Paste 2-3 example emails in dry-run mode]

## Configuration
- Default: dry_run=True
- V must approve voice before enabling

## Testing Results
- Unit tests: X/X passing
- Integration test: Dry-run successful
- Gmail API: Connected and tested

## Notes
[Any concerns about voice, recommendations for V]

Ready for V to review email voice before enabling auto-send.
```

---

## Important Notes

1. **DRY-RUN FIRST:** Never enable actual sending until V approves the voice
2. **Voice is critical:** Spend time getting the manager tone right
3. **HTML support:** Make emails readable (use simple HTML formatting)
4. **Emoji use:** Minimal and tasteful (⭐ ⚠️ 🔴 only)
5. **Signature consistency:** Always "— The Gaffer / Arsenal Productivity FC"

---

**Orchestrator:** con_MuvXIR7jXZjZxlND  
**Your Mission:** Give the system a voice. Make V want to read these emails.  
**Priority:** HIGH - This is the personality layer.

Good luck! 📧

---
**Created:** 2025-10-30 01:40 ET
