#!/usr/bin/env python3
"""
CRM Calendar Webhook Health Monitor

Background service that continuously monitors webhook health and sends
SMS alerts when issues are detected.

Monitoring checks:
1. Webhook expiration status (expires within 24 hours)
2. Last notification received time (> 24 hours without notifications)
3. Event processing errors (5+ errors in 24 hours)
4. Service availability (renewal worker, handler endpoint)

This provides early warning of webhook failures before they impact
meeting preparation workflows.
"""

import sys
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sqlite3
import json

sys.path.append('/home/workspace/N5/scripts')

try:
    from crm_calendar_helpers import (
        load_config,
        setup_logging,
        send_sms_alert,
        load_webhook_metadata
    )
except ImportError as e:
    print(f"Failed to import helpers: {e}")
    sys.exit(1)

# Application state
app_state = {
    'logger': None,
    'config': None,
    'check_count': 0,
    'alert_count': 0,
    'last_check': None,
    'last_alert': None,
    'alert_cooldowns': {}  # Track last alert time per alert type
}

# Alert types with cooldown periods (seconds)
ALERT_COOLDOWNS = {
    'webhook_expiring': 86400,      # Once per day
    'no_notifications': 43200,       # Every 12 hours
    'processing_errors': 21600,      # Every 6 hours
    'health_check_failed': 3600,     # Every hour
    'service_unavailable': 7200      # Every 2 hours
}


def is_in_cooldown(alert_type: str) -> bool:
    """
    Check if an alert is in cooldown period.
    
    Args:
        alert_type: Type of alert
        
    Returns:
        bool: True if alert should be suppressed (in cooldown)
    """
    last_alert = app_state['alert_cooldowns'].get(alert_type)
    if not last_alert:
        return False
    
    cooldown_seconds = ALERT_COOLDOWNS.get(alert_type, 3600)
    last_alert_time = datetime.fromisoformat(last_alert)
    time_since_alert = datetime.utcnow() - last_alert_time
    
    return time_since_alert.total_seconds() < cooldown_seconds


def record_alert(alert_type: str) -> None:
    """Record that an alert was sent"""
    app_state['alert_cooldowns'][alert_type] = datetime.utcnow().isoformat()
    app_state['alert_count'] += 1
    app_state['last_alert'] = datetime.utcnow().isoformat()
    app_state['logger'].info(f"Alert recorded: {alert_type}")


def check_webhook_expiration() -> tuple[bool, str]:
    """
    Check if webhook is expiring soon.
    
    Returns:
        tuple: (is_critical, message)
    """
    try:
        metadata = load_webhook_metadata()
        
        if not metadata or 'expiration_ms' not in metadata:
            return True, "❌ Webhook metadata not found or invalid"
        
        expiration_ms = metadata['expiration_ms']
        expiration_dt = datetime.fromtimestamp(expiration_ms / 1000)
        
        now = datetime.utcnow()
        time_remaining = expiration_dt - now
        
        # Alert if expires within 24 hours
        if time_remaining < timedelta(hours=24):
            hours_remaining = time_remaining.total_seconds() / 3600
            
            if time_remaining < timedelta(hours=0):
                return True, f"🚨 Webhook EXPIRED! Expired {abs(hours_remaining):.1f} hours ago"
            elif time_remaining < timedelta(hours=6):
                return True, f"🚨 Critical: Webhook expires in {hours_remaining:.1f} hours!"
            else:
                return True, f"⚠️ Warning: Webhook expires in {hours_remaining:.1f} hours"
        
        return False, f"✓ Webhook expires in {time_remaining.days} days (healthy)"
        
    except Exception as e:
        app_state['logger'].error(f"Error checking webhook expiration: {e}")
        return True, f"❌ Error checking expiration: {str(e)[:50]}..."


def check_last_notification() -> tuple[bool, str]:
    """
    Check how long ago the last webhook notification was received.
    
    Returns:
        tuple: (is_concerning, message)
    """
    try:
        with sqlite3.connect('/home/workspace/N5/data/n5_core.db') as conn:
            cursor = conn.cursor()
            
            # Query webhook health table
            cursor.execute(
                """SELECT last_received_at 
                   FROM webhook_health 
                   WHERE service = 'google_calendar'
                   ORDER BY id DESC 
                   LIMIT 1"""
            )
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return False, "ℹ️ No notifications received yet (may be normal)"
            
            last_received = datetime.fromisoformat(result[0])
            time_since_notification = datetime.utcnow() - last_received
            hours_since = time_since_notification.total_seconds() / 3600
            
            # Alert if no notifications in 24+ hours (for active calendars)
            threshold_hours = app_state['config'].get('health', {}).get('alert_on_no_notifications_hours', 24)
            
            if hours_since > threshold_hours:
                return True, f"⚠️ No notifications in {(hours_since):.1f} hours (threshold: {threshold_hours}h)"
            elif hours_since > 12:
                return False, f"ℹ️ No notifications in {(hours_since):.1f} hours (acceptable)"
            else:
                return False, f"✓ Recent notification {(hours_since):.1f} hours ago"
                
    except Exception as e:
        app_state['logger'].error(f"Error checking last notification: {e}")
        return False, f"❌ Error checking notifications: {str(e)[:50]}..."


def check_processing_errors() -> tuple[bool, int, str]:
    """
    Check for recent event processing errors.
    
    Returns:
        tuple: (has_critcal_errors, error_count, message)
    """
    try:
        with sqlite3.connect('/home/workspace/N5/data/n5_core.db') as conn:
            cursor = conn.cursor()

            # Query recent errors (last 24 hours). If table is absent, treat as zero.
            hours_to_check = 24
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='webhook_errors'")
            has_table = cursor.fetchone() is not None
            if has_table:
                cursor.execute(
                    """SELECT COUNT(*) as error_count
                       FROM webhook_errors
                       WHERE created_at >= datetime('now', '-%s hours')
                       AND resolved = 0""" % hours_to_check
                )
                result = cursor.fetchone()
                error_count = result[0] if result else 0
            else:
                error_count = 0
            
            # Get threshold from config (default: 5 errors)
            error_threshold = app_state['config'].get('health', {}).get('alert_on_errors_count', 5)
            
            if error_count >= error_threshold:
                return True, error_count, f"🚨 {error_count} processing errors in last {hours_to_check}h (threshold: {error_threshold})"
            elif error_count > 0:
                return False, error_count, f"ℹ️ {error_count} processing errors in last {hours_to_check}h (below threshold)"
            else:
                return False, 0, "✓ No processing errors detected"
                
    except Exception as e:
        app_state['logger'].error(f"Error checking processing errors: {e}")
        return False, 0, f"❌ Error checking errors: {str(e)[:50]}..."


def check_database_connectivity() -> tuple[bool, str]:
    """Check if database is accessible"""
    try:
        with sqlite3.connect('/home/workspace/N5/data/n5_core.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True, "✓ Database connectivity OK"
    except Exception as e:
        return False, f"❌ Database connectivity failed: {str(e)[:50]}..."


def check_services_availability() -> tuple[bool, List[str]]:
    """
    Check if required services are available.
    
    Returns:
        tuple: (all_available, list of status messages)
    """
    import socket
    
    services = []
    issues = []
    
    # Check webhook handler (port 8778)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8778))
        sock.close()
        
        if result == 0:
            services.append("✓ Webhook handler (port 8778)")
        else:
            issues.append("❌ Webhook handler unavailable (port 8778)")
    except Exception as e:
        issues.append(f"❌ Could not check webhook handler: {str(e)[:30]}...")
    
    # Check renewal worker (port 8766)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8766))
        sock.close()
        
        if result == 0:
            services.append("✓ Renewal worker (port 8766)")
        else:
            # TCP services might not accept connections, check if process runs
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if 'crm_calendar_webhook_renewal.py' in cmdline:
                        services.append("ℹ️ Renewal worker running (process found)")
                        break
                except Exception:
                    continue
            else:
                issues.append("⚠️ Renewal worker status unknown (port 8766 not listening)")
    except Exception as e:
        issues.append(f"ℹ️ Could not verify renewal worker: {str(e)[:30]}...")
    
    return len(issues) == 0, services + issues


def perform_health_check() -> tuple[bool, List[str]]:
    """
    Perform complete health check and return results.
    
    Returns:
        tuple: (all_healthy, list of detailed status messages)
    """
    app_state['logger'].info("Starting health check...")
    
    all_healthy = True
    messages = []
    
    # Check 1: Database connectivity
    db_ok, db_msg = check_database_connectivity()
    if not db_ok:
        all_healthy = False
        if not is_in_cooldown('health_check_failed'):
            messages.append(db_msg)
            send_sms_alert(f"🚨 CRM Webhook Health: {db_msg}")
            record_alert('health_check_failed')
    else:
        messages.append(db_msg)
    
    # Check 2: Webhook expiration
    if db_ok:  # Only check if DB is accessible
        exp_critical, exp_msg = check_webhook_expiration()
        if exp_critical:
            all_healthy = False
            if not is_in_cooldown('webhook_expiring'):
                messages.append(exp_msg)
                send_sms_alert(exp_msg)
                record_alert('webhook_expiring')
        elif '⚠️' in exp_msg or '🚨' in exp_msg:
            messages.append(exp_msg)
        else:
            messages.append(exp_msg)
    
    # Check 3: Last notification received
    if db_ok:
        notif_concerning, notif_msg = check_last_notification()
        if notif_concerning:
            all_healthy = False
            if not is_in_cooldown('no_notifications'):
                messages.append(notif_msg)
                send_sms_alert(notif_msg)
                record_alert('no_notifications')
        elif '⚠️' in notif_msg:
            messages.append(notif_msg)
        else:
            messages.append(notif_msg)
    
    # Check 4: Processing errors
    if db_ok:
        has_errors, error_count, error_msg = check_processing_errors()
        if has_errors:
            all_healthy = False
            if not is_in_cooldown('processing_errors'):
                messages.append(error_msg)
                send_sms_alert(error_msg)
                record_alert('processing_errors')
        elif error_count > 0:
            messages.append(error_msg)
        else:
            messages.append(error_msg)
    
    # Check 5: Services availability
    services_ok, services_msgs = check_services_availability()
    if not services_ok:
        all_healthy = False
        if not is_in_cooldown('service_unavailable'):
            # Summarize service issues
            issue_count = len([m for m in services_msgs if '❌' in m])
            if issue_count > 0:
                alert_msg = f"⚠️ Service availability issues: {issue_count} services affected"
                send_sms_alert(alert_msg)
                record_alert('service_unavailable')
    
    # Add services status to messages
    messages.append("\n📡 Service Status:")
    messages.extend(services_msgs)
    
    return all_healthy, messages


async def health_monitor():
    """Main health monitoring loop"""
    try:
        app_state['logger'].info("Starting health monitor...")
        
        # Get check interval from config (default: 1 hour)
        check_interval_hours = app_state['config'].get('health', {}).get('check_interval_hours', 1)
        check_interval_seconds = check_interval_hours * 3600
        
        app_state['logger'].info(f"Check interval: {check_interval_hours} hour(s)")
        
        # Perform initial health check
        all_healthy, messages = perform_health_check()
        
        # Log initial results
        app_state['logger'].info("=" * 70)
        app_state['logger'].info("INITIAL HEALTH CHECK RESULTS")
        app_state['logger'].info("=" * 70)
        for msg in messages:
            app_state['logger'].info(msg)
        app_state['logger'].info("=" * 70)
        
        # Main monitoring loop
        while True:
            app_state['check_count'] += 1
            app_state['last_check'] = datetime.utcnow().isoformat()
            
            app_state['logger'].info(f"\n{'=' * 70}")
            app_state['logger'].info(f"HEALTH CHECK #{app_state['check_count']}")
            app_state['logger'].info(f"{'=' * 70}")
            
            # Perform health check
            all_healthy, messages = perform_health_check()
            
            # Log results
            status_emoji = "✅" if all_healthy else "⚠️"
            app_state['logger'].info(f"Overall Status: {status_emoji}")
            
            for msg in messages:
                app_state['logger'].info(msg)
            
            # Log periodic statistics
            if app_state['check_count'] % 24 == 0:  # Every 24 checks
                log_monitoring_stats()
            
            # Sleep until next check
            app_state['logger'].info(f"Next check in {check_interval_hours} hour(s)...")
            await asyncio.sleep(check_interval_seconds)
    
    except KeyboardInterrupt:
        app_state['logger'].info("Health monitor stopped by user")
        log_monitoring_stats()
    except Exception as e:
        app_state['logger'].error(f"Fatal error in health monitor: {e}", exc_info=True)
        raise


def log_monitoring_stats():
    """Log current monitoring statistics"""
    app_state['logger'].info("=" * 70)
    app_state['logger'].info("MONITORING STATISTICS")
    app_state['logger'].info("=" * 70)
    app_state['logger'].info(f"Check count:           {app_state['check_count']}")
    app_state['logger'].info(f"Alert count:           {app_state['alert_count']}")
    app_state['logger'].info(f"Last check:            {app_state['last_check']}")
    app_state['logger'].info(f"Last alert:            {app_state['last_alert']}")
    
    # Log active cooldowns
    active_cooldowns = []
    for alert_type, last_time in app_state['alert_cooldowns'].items():
        if last_time:
            time_since = datetime.utcnow() - datetime.fromisoformat(last_time)
            hours = time_since.total_seconds() / 3600
            active_cooldowns.append(f"{alert_type}: {hours:.1f}h ago")
    
    if active_cooldowns:
        app_state['logger'].info("Alert cooldowns:")
        for cooldown in active_cooldowns:
            app_state['logger'].info(f"  • {cooldown}")
    
    app_state['logger'].info("=" * 70)


async def main():
    """Main entry point for health monitor"""
    import traceback
    
    parser = argparse.ArgumentParser(description='CRM Calendar Webhook Health Monitor')
    parser.add_argument('--config', default='/home/workspace/N5/config/calendar_webhook.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    # Load configuration
    app_state['config'] = load_config(args.config)
    
    # Setup logging
    log_file = app_state['config'].get('logging', {}).get('health_monitor', '/dev/shm/crm-webhook-health.log')
    app_state['logger'] = setup_logging(log_file)
    
    # Display startup info
    print("=" * 70)
    print("CRM CALENDAR WEBHOOK HEALTH MONITOR")
    print("=" * 70)
    print(f"Config file: {args.config}")
    print(f"Log file: {log_file}")
    print(f"Alert cooldowns: {len(ALERT_COOLDOWNS)} types configured")
    print("=" * 70)
    print("Monitor running in background...")
    print("Check logs for detailed status.")
    print("Will send SMS alerts when issues detected.")
    print("=" * 70)
    
    try:
        await health_monitor()
    except KeyboardInterrupt:
        print("\nShutting down...")
        log_monitoring_stats()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

