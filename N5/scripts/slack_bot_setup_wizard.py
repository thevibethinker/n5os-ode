#!/usr/bin/env python3
"""Interactive setup wizard for Slack bot."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.secrets import get_secret

def check_status():
    """Check current setup status."""
    print("\n🔍 Checking Slack Bot Setup Status...\n")
    
    status = {
        "bot_token": False,
        "signing_secret": False,
        "user_id_added": False,
        "service_running": False
    }
    
    # Check bot token
    bot_token = get_secret("SLACK_N5_BOT_SECRET", required=False) or get_secret("SLACK_BOT_TOKEN", required=False)
    if bot_token:
        print("✅ Bot token configured")
        status["bot_token"] = True
    else:
        print("❌ Bot token missing")
    
    # Check signing secret
    signing_secret = get_secret("SLACK_SIGNING_SECRET", required=False)
    if signing_secret:
        print("✅ Signing secret configured")
        status["signing_secret"] = True
    else:
        print("❌ Signing secret missing")
        print("   → Get it from: https://api.slack.com/apps/A09P2SHEFRQ/general")
        print("   → Add with: python3 /home/workspace/N5/lib/secrets.py set SLACK_SIGNING_SECRET")
    
    # Check config file
    config_path = Path("/home/workspace/N5/config/slack_bot_config.json")
    if config_path.exists():
        import json
        config = json.loads(config_path.read_text())
        users = config.get("authorized_users", [])
        if users:
            print(f"✅ Whitelist configured ({len(users)} user(s))")
            for user_id in users:
                print(f"   - {user_id}")
            status["user_id_added"] = True
        else:
            print("⚠️  No users in whitelist yet")
            print("   → Get your user ID: python3 /home/workspace/N5/scripts/slack_get_user_id.py")
            print("   → Add yourself: python3 /home/workspace/N5/scripts/slack_bot_config.py add <YOUR_USER_ID>")
    else:
        print("⚠️  Config file not found")
        print("   → Initialize: python3 /home/workspace/N5/scripts/slack_bot_config.py init")
    
    # Check service
    import subprocess
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
         "https://slack-bot-receiver-va.zocomputer.io/health"],
        capture_output=True,
        text=True
    )
    if result.stdout == "200":
        print("✅ Service is running")
        status["service_running"] = True
    else:
        print("❌ Service not running yet")
        print("   → Will be started after Slack configuration is complete")
    
    # Overall status
    ready_count = sum(status.values())
    print(f"\n📊 Setup Progress: {ready_count}/4 steps complete\n")
    
    if ready_count == 4:
        print("🎉 All set! Your Slack bot is ready to use!")
        print("\nTest it:")
        print("1. DM your bot: n5_os_bot_v2")
        print("2. Or mention it: @n5_os_bot_v2 hello")
    elif not status["signing_secret"]:
        print("🚨 Next step: Add signing secret (required for security)")
        print("   1. Go to: https://api.slack.com/apps/A09P2SHEFRQ/general")
        print("   2. Copy 'Signing Secret'")
        print("   3. Run: python3 /home/workspace/N5/lib/secrets.py set SLACK_SIGNING_SECRET")
    elif not status["user_id_added"]:
        print("🚨 Next step: Add your user ID to whitelist")
        print("   1. First, add scopes in Slack (see setup guide)")
        print("   2. Run: python3 /home/workspace/N5/scripts/slack_get_user_id.py")
        print("   3. Run: python3 /home/workspace/N5/scripts/slack_bot_config.py add <YOUR_ID>")
    elif not status["service_running"]:
        print("🚨 Next step: Tell Zo to start the service!")
        print("   → Let me know you're ready and I'll register the service")
    
    print(f"\n📖 Full guide: /home/workspace/N5/docs/slack-bot-setup-guide.md\n")


if __name__ == "__main__":
    check_status()

