#!/usr/bin/env python3
"""
Coaching Email System - Arsenal Manager Voice
Sends motivational/alert emails when team status changes.

Usage:
    python3 coaching_email_system.py --check
    python3 coaching_email_system.py --check --send
    python3 coaching_email_system.py --test-template promotion
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import sqlite3
import argparse
import sys
import logging

DB_PATH = "/home/workspace/productivity_tracker.db"
RECIPIENT_EMAIL = "va@zo.computer"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


class EmailTemplate:
    """Arsenal manager-voiced email template"""
    
    @staticmethod
    def status_change_promotion(status: str, prev_status: str, metrics: Dict) -> Dict:
        """Promotion celebration email"""
        
        status_map = {
            'first_team': ('First Team', '⭐'),
            'invincible': ('Invincible', '🔥'),
            'legend': ('Legend', '👑')
        }
        
        new_status, icon = status_map.get(status, (status.replace('_', ' ').title(), '🎯'))
        
        subject = f"[Arsenal Performance Alert] {icon} {new_status} Call-Up"
        
        body = f"""Vrijen,

Outstanding work. You've earned your spot in the {new_status}.

Your performance over the last week has been exactly what this club demands:
• {metrics['top5_avg']:.1f}% average (top 5 of 7 days)
• {metrics['days_in_status']} days maintaining this standard
• Previous level: {prev_status.replace('_', ' ').title()}

This is where you belong. Now maintain it. The {new_status} isn't about one good week—it's about sustained excellence. Keep this standard and you'll keep climbing.

Welcome to the {new_status}.

— The Gaffer
Arsenal Productivity FC"""
        
        return {'subject': subject, 'body': body}
    
    @staticmethod
    def status_change_demotion(status: str, prev_status: str, metrics: Dict) -> Dict:
        """Demotion alert email"""
        
        status_map = {
            'transfer_list': 'Transfer List',
            'reserves': 'Reserves',
            'squad_member': 'Squad'
        }
        
        new_status = status_map.get(status, status.replace('_', ' ').title())
        
        subject = f"[Arsenal Performance Alert] Dropped to {new_status}"
        
        body = f"""Vrijen,

I've had to make a tough decision. Based on your recent performances, you're being moved to the {new_status} effective immediately.

The numbers don't lie:
• Last 7 days: {metrics['top5_avg']:.1f}% average (need better)
• Consecutive poor days: {metrics.get('consecutive_poor_days', 0)}
• Previous level: {prev_status.replace('_', ' ').title()}

You've got the talent, but talent without output doesn't win matches. Show me consistent 90%+ performance and we'll talk about bringing you back.

The squad needs you. Time to prove you belong.

— The Gaffer
Arsenal Productivity FC"""
        
        return {'subject': subject, 'body': body}
    
    @staticmethod
    def elite_unlock(status: str, metrics: Dict) -> Dict:
        """Elite tier unlock celebration"""
        
        if status == 'invincible':
            title = 'Invincible Status'
            icon = '🔥'
            message = "You've unlocked the Invincible tier. This is elite territory."
        else:  # legend
            title = 'Legend Status'
            icon = '👑'
            message = "You've reached Legend status. The absolute pinnacle."
        
        subject = f"[Arsenal Achievement] {icon} {title} Unlocked"
        
        body = f"""Vrijen,

{message}

Performance that got you here:
• {metrics['top5_avg']:.1f}% average (top 5 of 7 days)
• Elite standard: 125%+ consistently

This is what greatness looks like. You're in rarified air now. The question isn't whether you can reach this level—you've proven you can. The question is: can you stay here?

Show me.

— The Gaffer
Arsenal Productivity FC"""
        
        return {'subject': subject, 'body': body}


class CoachingEmailSystem:
    """Manages sending coaching emails with rate limiting"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.db_path = DB_PATH
    
    def check_for_triggers(self) -> List[Dict]:
        """Check if any email triggers have fired"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get today's status
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT status, days_in_status, previous_status, top5_avg, date
            FROM team_status_history
            WHERE date = ?
        """, (today,))
        
        today_status = cursor.execute("""
            SELECT status, days_in_status, previous_status, top5_avg, date
            FROM team_status_history
            WHERE date = ?
        """, (today,)).fetchone()
        
        conn.close()
        
        if not today_status:
            logger.info("No status data for today yet")
            return []
        
        triggers = []
        
        # Check if status changed today
        if today_status['previous_status'] and today_status['previous_status'] != today_status['status']:
            status_tier_order = ['transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend']
            current_idx = status_tier_order.index(today_status['status'])
            prev_idx = status_tier_order.index(today_status['previous_status'])
            
            if current_idx > prev_idx:
                # Promotion
                if today_status['status'] in ['invincible', 'legend'] and today_status['days_in_status'] == 1:
                    trigger_type = 'elite_unlock'
                else:
                    trigger_type = 'promotion'
            else:
                # Demotion
                trigger_type = 'demotion'
            
            triggers.append({
                'type': trigger_type,
                'status': today_status['status'],
                'previous_status': today_status['previous_status'],
                'metrics': dict(today_status)
            })
        
        return triggers
    
    def generate_email(self, trigger: Dict) -> Optional[Dict]:
        """Generate email based on trigger"""
        trigger_type = trigger['type']
        status = trigger['status']
        prev_status = trigger['previous_status']
        metrics = trigger['metrics']
        
        if trigger_type == 'promotion':
            return EmailTemplate.status_change_promotion(status, prev_status, metrics)
        elif trigger_type == 'demotion':
            return EmailTemplate.status_change_demotion(status, prev_status, metrics)
        elif trigger_type == 'elite_unlock':
            return EmailTemplate.elite_unlock(status, metrics)
        
        return None
    
    def should_send(self, trigger_type: str) -> bool:
        """Check rate limits - max 1 coaching email per day"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='coaching_emails'
        """)
        
        if not cursor.fetchone():
            # Create table
            cursor.execute("""
                CREATE TABLE coaching_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_type TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    sent_to TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status_trigger TEXT,
                    dry_run BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()
        
        # Check if we've sent a coaching email today
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) FROM coaching_emails
            WHERE DATE(sent_at) = ? AND dry_run = 0
        """, (today,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count == 0
    
    def log_email(self, email_type: str, subject: str, status_trigger: str):
        """Log email send to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO coaching_emails (email_type, subject, sent_to, status_trigger, dry_run)
            VALUES (?, ?, ?, ?, ?)
        """, (email_type, subject, RECIPIENT_EMAIL, status_trigger, 1 if self.dry_run else 0))
        
        conn.commit()
        conn.close()
    
    def send_email(self, email_data: Dict, trigger_type: str, status_trigger: str):
        """Send email (dry-run or actual)"""
        subject = email_data['subject']
        body = email_data['body']
        
        if self.dry_run:
            print("\n" + "="*70)
            print("[DRY-RUN] Would send coaching email:")
            print("="*70)
            print(f"To: {RECIPIENT_EMAIL}")
            print(f"Subject: {subject}")
            print("-"*70)
            print(body)
            print("="*70 + "\n")
        else:
            # Actually send via Gmail
            logger.info(f"Sending email: {subject}")
            # Note: Requires Gmail integration - placeholder for now
            # use_app_gmail(tool_name="gmail-send-email", configured_props={...})
            logger.warning("Gmail integration not yet implemented - email not sent")
        
        # Log it
        self.log_email(trigger_type, subject, status_trigger)
    
    def process_triggers(self, send: bool = False):
        """Main processing loop"""
        triggers = self.check_for_triggers()
        
        if not triggers:
            logger.info("No email triggers found for today")
            return 0
        
        for trigger in triggers:
            logger.info(f"Found trigger: {trigger['type']} - {trigger['status']}")
            
            # Check rate limits
            if not send:
                logger.info("[CHECK MODE] Trigger found but --send flag not provided")
                email_data = self.generate_email(trigger)
                if email_data:
                    print(f"\nWould send: {email_data['subject']}")
                continue
            
            if not self.should_send(trigger['type']):
                logger.info(f"Rate limit: Already sent coaching email today")
                continue
            
            # Generate and send
            email_data = self.generate_email(trigger)
            if email_data:
                self.send_email(
                    email_data, 
                    trigger['type'],
                    f"{trigger['previous_status']} → {trigger['status']}"
                )
        
        return len(triggers)


def main():
    parser = argparse.ArgumentParser(description='Arsenal Coaching Email System')
    parser.add_argument('--check', action='store_true', help='Check for email triggers')
    parser.add_argument('--send', action='store_true', help='Actually send emails (requires --check)')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Dry run mode (default: True)')
    parser.add_argument('--test-template', choices=['promotion', 'demotion', 'elite'], help='Test email template')
    
    args = parser.parse_args()
    
    system = CoachingEmailSystem(dry_run=args.dry_run if not args.send else False)
    
    if args.test_template:
        # Test templates
        test_metrics = {
            'top5_avg': 128.5,
            'days_in_status': 7,
            'consecutive_poor_days': 0
        }
        
        if args.test_template == 'promotion':
            email = EmailTemplate.status_change_promotion('first_team', 'squad_member', test_metrics)
        elif args.test_template == 'demotion':
            email = EmailTemplate.status_change_demotion('reserves', 'first_team', test_metrics)
        elif args.test_template == 'elite':
            email = EmailTemplate.elite_unlock('invincible', test_metrics)
        
        print("\n" + "="*70)
        print(f"Subject: {email['subject']}")
        print("-"*70)
        print(email['body'])
        print("="*70 + "\n")
        
        return 0
    
    if args.check:
        return system.process_triggers(send=args.send)
    
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
