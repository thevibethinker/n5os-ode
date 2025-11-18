#!/usr/bin/env python3
"""Manage Slack bot configuration and whitelist."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.secrets import get_secret

CONFIG_PATH = Path("/home/workspace/N5/config/slack_bot_config.json")


def load_config():
    """Load current config."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "authorized_users": [],
        "signing_secret": "",
        "bot_token": "",
        "rate_limit_messages": 10,
        "rate_limit_window_seconds": 60,
        "audit_log": True
    }


def save_config(config):
    """Save config to file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    print(f"✅ Config saved to {CONFIG_PATH}")


def add_user(user_id: str):
    """Add user to whitelist."""
    config = load_config()
    if user_id in config["authorized_users"]:
        print(f"⚠️  User {user_id} already authorized")
    else:
        config["authorized_users"].append(user_id)
        save_config(config)
        print(f"✅ Added {user_id} to whitelist")


def remove_user(user_id: str):
    """Remove user from whitelist."""
    config = load_config()
    if user_id in config["authorized_users"]:
        config["authorized_users"].remove(user_id)
        save_config(config)
        print(f"✅ Removed {user_id} from whitelist")
    else:
        print(f"⚠️  User {user_id} not in whitelist")


def list_users():
    """List authorized users."""
    config = load_config()
    users = config.get("authorized_users", [])
    
    if users:
        print(f"\n✅ Authorized users ({len(users)}):")
        for user_id in users:
            print(f"   - {user_id}")
    else:
        print("\n⚠️  No users authorized yet")
    
    print(f"\nRate limit: {config.get('rate_limit_messages', 10)} messages per {config.get('rate_limit_window_seconds', 60)}s")
    print(f"Audit log: {'enabled' if config.get('audit_log', True) else 'disabled'}")


def init_config():
    """Initialize config with secrets."""
    config = load_config()
    
    # Get secrets
    config["signing_secret"] = get_secret("SLACK_SIGNING_SECRET", required=False) or ""
    config["bot_token"] = get_secret("SLACK_N5_BOT_SECRET") or get_secret("SLACK_BOT_TOKEN")
    
    save_config(config)
    print("✅ Config initialized with Zo secrets")
    
    if not config["signing_secret"]:
        print("\n⚠️  WARNING: No signing secret found!")
        print("You need to add SLACK_SIGNING_SECRET to Zo secrets")
        print("Get it from: https://api.slack.com/apps/A09P2SHEFRQ/general")


def main():
    parser = argparse.ArgumentParser(description="Manage Slack bot configuration")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Add user
    add_parser = subparsers.add_parser("add", help="Add user to whitelist")
    add_parser.add_argument("user_id", help="Slack user ID")
    
    # Remove user
    remove_parser = subparsers.add_parser("remove", help="Remove user from whitelist")
    remove_parser.add_argument("user_id", help="Slack user ID")
    
    # List users
    subparsers.add_parser("list", help="List authorized users")
    
    # Init config
    subparsers.add_parser("init", help="Initialize config with secrets")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_user(args.user_id)
    elif args.command == "remove":
        remove_user(args.user_id)
    elif args.command == "list":
        list_users()
    elif args.command == "init":
        init_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

