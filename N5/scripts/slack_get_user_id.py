#!/usr/bin/env python3
"""Get your Slack user ID for whitelist configuration."""
import sys
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.secrets import get_secret

def main():
    """Get user ID by email or display name."""
    bot_token = get_secret('SLACK_N5_BOT_SECRET') or get_secret('SLACK_BOT_TOKEN')
    client = WebClient(token=bot_token)
    
    try:
        # Get all users
        response = client.users_list()
        
        # Look for Vrijen
        for user in response['members']:
            if user.get('deleted') or user.get('is_bot'):
                continue
                
            profile = user.get('profile', {})
            email = profile.get('email', '').lower()
            real_name = profile.get('real_name', '').lower()
            display_name = profile.get('display_name', '').lower()
            
            if any([
                'vrijen' in email,
                'vrijen' in real_name,
                'vrijen' in display_name,
                'attawar' in email
            ]):
                print(f"\n✅ Found your Slack user:")
                print(f"   User ID: {user['id']}")
                print(f"   Name: {profile.get('real_name', 'N/A')}")
                print(f"   Email: {email or 'N/A'}")
                print(f"\n📋 Add this to your whitelist config:")
                print(f"   {user['id']}")
                return user['id']
        
        print("❌ Could not find user. All users:")
        for user in response['members']:
            if not user.get('deleted') and not user.get('is_bot'):
                profile = user.get('profile', {})
                print(f"  {user['id']}: {profile.get('real_name', 'Unknown')}")
                
    except SlackApiError as e:
        if e.response['error'] == 'missing_scope':
            print(f"❌ Missing Slack scope: {e.response.get('needed', 'users:read')}")
            print("\nYou need to add the 'users:read' scope to your Slack app:")
            print("1. Go to: https://api.slack.com/apps/A09P2SHEFRQ/oauth")
            print("2. Under 'Scopes' → 'Bot Token Scopes', add: users:read")
            print("3. Reinstall the app to your workspace")
            print("4. Run this script again")
        else:
            print(f"❌ Slack API error: {e}")

if __name__ == "__main__":
    main()

