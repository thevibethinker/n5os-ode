#!/usr/bin/env python3
"""
CRM Calendar Webhook Renewal Worker

Background service that automatically renews the Google Calendar webhook
before expiration (checks daily, renews when < 2 days remaining).

Webhook lifespan: Maximum 7 days (Google Calendar API limit)
Renewal threshold: 2 days before expiration
Check interval: Every 24 hours

This service runs continuously and ensures the webhook never expires,
maintaining uninterrupted calendar event monitoring.
"""

import sys
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

sys.path.append('/home/workspace/N5/scripts')

try:
    from crm_calendar_helpers import (
        load_config,
        load_google_credentials,
        generate_unique_channel_id,
        calculate_expiration_ms,
        store_webhook_metadata,
        update_webhook_health,
        load_webhook_metadata,
        setup_logging,
        send_sms_alert
    )
except ImportError as e:
    print(f"Failed to import helpers: {e}")
    sys.exit(1)

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Error: google-api-python-client not installed")
    sys.exit(1)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']
CALENDAR_ID = 'primary'

# Application state
app_state = {
    'logger': None,
    'config': None,
    'check_count': 0,
    'renewal_count': 0,
    'error_count': 0,
    'last_check': None,
    'last_renewal': None
}


def build_calendar_service():
    """Build Google Calendar API service"""
    try:
        service_account_info = load_google_credentials()
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        service = build('calendar', 'v3', credentials=credentials)
        app_state['logger'].info("✓ Calendar service built successfully")
        return service
    except Exception as e:
        app_state['logger'].error(f"Failed to build Calendar service: {e}")
        raise


def check_webhook_status() -> tuple[bool, Optional[datetime], str]:
    """
    Check current webhook status and determine if renewal is needed.
    
    Returns:
        tuple: (renewal_needed, expiration_datetime, channel_id)
    """
    try:
        app_state['logger'].info("Checking webhook status...")
        
        # Load webhook metadata from database
        metadata = load_webhook_metadata()
        
        if not metadata:
            app_state['logger'].warning("No webhook metadata found")
            return False, None, ""
        
        channel_id = metadata.get('channel_id')
        expiration_ms = metadata.get('expiration_ms')
        
        if not expiration_ms:
            app_state['logger'].error("No expiration timestamp in metadata")
            return False, None, channel_id
        
        # Convert milliseconds to datetime
        expiration_dt = datetime.fromtimestamp(expiration_ms / 1000)
        
        app_state['logger'].info(
            f"Current webhook - Channel: {channel_id[:8]}..., "
            f"Expires: {expiration_dt.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        
        # Calculate time remaining
        now = datetime.utcnow()
        time_remaining = expiration_dt - now
        
        app_state['logger'].info(
            f"Time remaining: {time_remaining.days} days, "
            f"{time_remaining.seconds // 3600} hours"
        )
        
        # Check renewal threshold (from config, default 2 days)
        threshold_days = app_state['config'].get('renewal', {}).get('renew_threshold_days', 2)
        renewal_threshold = timedelta(days=threshold_days)
        
        renewal_needed = time_remaining < renewal_threshold
        
        if renewal_needed:
            app_state['logger'].warning(
                f"Renewal needed! Time remaining ({time_remaining}) < threshold ({renewal_threshold})"
            )
        else:
            app_state['logger'].info("✓ No renewal needed yet")
        
        return renewal_needed, expiration_dt, channel_id
        
    except Exception as e:
        app_state['logger'].error(f"Failed to check webhook status: {e}", exc_info=True)
        raise


def renew_webhook(service) -> Dict[str, Any]:
    """
    Renew the Google Calendar webhook by registering a new one.
    
    Args:
        service: Google Calendar API service
        
    Returns:
        dict: New webhook registration response from Google
    """
    try:
        app_state['logger'].info("Starting webhook renewal...")
        
        # Load config
        config = app_state['config']
        webhook_url = config.get('webhook', {}).get('endpoint', 'https://va.zo.computer/webhooks/calendar')
        
        # Generate new channel parameters
        channel_id = generate_unique_channel_id()
        expiration_ms = calculate_expiration_ms()
        
        app_state['logger'].info(f"Generated new channel: {channel_id[:8]}...")
        app_state['logger'].info(
            f"New expiration: {datetime.fromtimestamp(expiration_ms / 1000).strftime('%Y-%m-%d %H:%M UTC')}"
        )
        
        # Build webhook registration request
        request_body = {
            'id': channel_id,
            'type': 'web_hook',
            'address': webhook_url,
            'expiration': expiration_ms
        }
        
        app_state['logger'].info("Registering webhook with Google Calendar...")
        
        try:
            response = service.events().watch(
                calendarId=CALENDAR_ID,
                body=request_body
            ).execute()
            
            app_state['logger'].info("✓ Webhook registered successfully")
            
            # Log response details
            app_state['logger'].info(f"Channel ID: {response['id']}")
            app_state['logger'].info(f"Resource ID: {response.get('resourceId', 'N/A')}")
            app_state['logger'].info(f"Resource URI: {response.get('resourceUri', 'N/A')}")
            
            return response
            
        except HttpError as e:
            error_details = e.error_details[0] if e.error_details else {}
            reason = error_details.get('reason', 'unknown')
            message = error_details.get('message', str(e))
            
            app_state['logger'].error(f"Google Calendar API Error: {reason}")
            app_state['logger'].error(f"Message: {message}")
            
            # Log troubleshooting hints
            if reason == 'forbidden':
                app_state['logger'].error(
                    "💡 Verify Calendar API is enabled and service account has access"
                )
            elif reason == 'invalidAddress':
                app_state['logger'].error(
                    f"💡 Verify webhook URL is accessible: {webhook_url}"
                )
            
            raise
            
    except Exception as e:
        app_state['logger'].error(f"Failed to renew webhook: {e}", exc_info=True)
        raise


def update_renewal_state(webhook_response: Dict[str, Any]) -> None:
    """
    Update application state and database after successful renewal.
    
    Args:
        webhook_response: Webhook registration response from Google
    """
    try:
        app_state['logger'].info("Updating renewal state...")
        
        # Store webhook metadata (config file and database)
        store_webhook_metadata(webhook_response)
        app_state['logger'].info("✓ Webhook metadata stored")
        
        # Update webhook health record
        update_webhook_health(
            channel_id=webhook_response['id'],
            resource_id=webhook_response.get('resourceId'),
            expiration_ms=webhook_response['expiration'],
            last_received_at=None,  # Will be updated when first notification arrives
            status='ACTIVE'
        )
        app_state['logger'].info("✓ Webhook health record updated")
        
        # Update application state
        app_state['renewal_count'] += 1
        app_state['error_count'] = 0  # Reset error count after successful renewal
        app_state['last_renewal'] = datetime.utcnow().isoformat()
        
        app_state['logger'].info(f"✓ Renewal completed (total renewals: {app_state['renewal_count']})")
        
    except Exception as e:
        app_state['logger'].error(f"Failed to update renewal state: {e}", exc_info=True)
        raise


def log_renewal_summary():
    """Log current renewal statistics"""
    app_state['logger'].info("=" * 70)
    app_state['logger'].info("RENEWAL WORKER STATISTICS")
    app_state['logger'].info("=" * 70)
    app_state['logger'].info(f"Check count:     {app_state['check_count']}")
    app_state['logger'].info(f"Renewal count:   {app_state['renewal_count']}")
    app_state['logger'].info(f"Error count:     {app_state['error_count']}")
    app_state['logger'].info(f"Last check:      {app_state['last_check']}")
    app_state['logger'].info(f"Last renewal:    {app_state['last_renewal']}")
    app_state['logger'].info("=" * 70)


async def renewal_worker(force_renewal: bool = False):
    """
    Main background worker that periodically checks and renews webhooks.
    
    Args:
        force_renewal: If True, bypass time check and force renewal (for testing)
    """
    try:
        app_state['logger'].info("Starting webhook renewal worker...")
        app_state['logger'].info(f"Force renewal mode: {'ON' if force_renewal else 'OFF'}")
        
        # Build Calendar service once
        service = build_calendar_service()
        
        # Get check interval from config (default: 24 hours)
        check_interval_hours = app_state['config'].get('renewal', {}).get('check_interval_hours', 24)
        check_interval_seconds = check_interval_hours * 3600
        
        app_state['logger'].info(f"Check interval: {check_interval_hours} hours")
        app_state['logger'].info("✓ Renewal worker initialized and running")
        
        # Initial check
        if force_renewal:
            app_state['logger'].info("Force renewal requested, renewing immediately...")
            webhook_response = renew_webhook(service)
            update_renewal_state(webhook_response)
            log_renewal_summary()
        else:
            renewal_needed, expiration, channel_id = check_webhook_status()
            if renewal_needed:
                webhook_response = renew_webhook(service)
                update_renewal_state(webhook_response)
        
        # Main loop
        while True:
            try:
                app_state['logger'].info(f"\n{'=' * 70}")
                app_state['logger'].info(f"RENEWAL CHECK #{app_state['check_count'] + 1}")
                app_state['logger'].info(f"{'=' * 70}")
                
                # Record check time
                app_state['last_check'] = datetime.utcnow().isoformat()
                app_state['check_count'] += 1
                
                # Check webhook status
                renewal_needed, expiration, channel_id = check_webhook_status()
                
                if force_renewal:
                    if app_state['check_count'] > 1:
                        # On subsequent checks in force mode, just log status
                        app_state['logger'].info("Force renewal mode: skipping scheduled renewal")
                    # Don't renew again in force mode
                elif renewal_needed:
                    app_state['logger'].warning("Renewal needed!")
                    webhook_response = renew_webhook(service)
                    update_renewal_state(webhook_response)
                    
                    # Send SMS notification of successful renewal
                    expiration_human = datetime.fromtimestamp(
                        webhook_response['expiration'] / 1000
                    ).strftime('%Y-%m-%d %H:%M UTC')
                    
                    send_sms_alert(
                        f"✅ Calendar webhook renewed until {expiration_human}"
                    )
                else:
                    app_state['logger'].info("✓ No action needed")
                
                # Log periodic summary (every 10 checks)
                if app_state['check_count'] % 10 == 0:
                    log_renewal_summary()
                
                # Reset error count after successful check
                if app_state['error_count'] > 0:
                    app_state['error_count'] = 0
                
                # Sleep until next check
                app_state['logger'].info(f"Sleeping for {check_interval_hours} hours...")
                await asyncio.sleep(check_interval_seconds)
                
            except Exception as e:
                app_state['error_count'] += 1
                
                app_state['logger'].error(
                    f"Error during renewal check: {e} (error #{app_state['error_count']})",
                    exc_info=True
                )
                
                # Send SMS alert on persistent errors
                if app_state['error_count'] >= 3:
                    send_sms_alert(
                        f"🚨 Calendar webhook renewal failing: {app_state['error_count']} consecutive errors"
                    )
                
                # Wait shorter on error before retrying
                retry_delay = 3600  # 1 hour
                app_state['logger'].info(f"Retrying in {retry_delay // 60} minutes...")
                await asyncio.sleep(retry_delay)
    
    except KeyboardInterrupt:
        app_state['logger'].info("Renewal worker stopped by user")
    except Exception as e:
        app_state['logger'].error(f"Fatal error in renewal worker: {e}", exc_info=True)
        raise


async def main():
    """Main entry point for renewal worker"""
    parser = argparse.ArgumentParser(description='CRM Calendar Webhook Renewal Worker')
    parser.add_argument('--force-renew', action='store_true', help='Force immediate renewal')
    
    args = parser.parse_args()
    
    # Load configuration (uses default path from helpers)
    app_state['config'] = load_config()
    
    # Setup logging
    log_file = app_state['config'].get('logging', {}).get('renewal_worker', '/dev/shm/crm-webhook-renewal.log')
    app_state['logger'] = setup_logging(log_file)
    
    # Display startup info
    print("=" * 70)
    print("CRM CALENDAR WEBHOOK RENEWAL WORKER")
    print("=" * 70)
    print(f"Config file: {args.config}")
    print(f"Log file: {log_file}")
    print(f"Force renewal: {'YES' if args.force_renew else 'NO'}")
    print("=" * 70)
    print("Worker running in background...")
    print("Check logs for detailed status.")
    print("=" * 70)
    
    # Run worker
    try:
        await renewal_worker(force_renewal=args.force_renew)
    except KeyboardInterrupt:
        print("\nShutting down...")
        log_renewal_summary()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())


