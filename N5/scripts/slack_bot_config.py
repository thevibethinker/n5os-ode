#!/usr/bin/env python3
"""Manage Slack bot configuration and whitelist."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.secrets import get_secret

CONFIG_PATH = Path("/home/workspace/N5/config/slack_bot_config.json")


def load_config():
    """Load current config."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "authorized_users": [],
        "scoped_authorized_users": {},
        "channel_routes": {},
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
    scoped_users = config.get("scoped_authorized_users", {})
    
    if users:
        print(f"\n✅ Authorized users ({len(users)}):")
        for user_id in users:
            print(f"   - {user_id}")
    else:
        print("\n⚠️  No users authorized yet")

    if scoped_users:
        print(f"\n✅ Scoped users ({len(scoped_users)}):")
        for user_id, policy in scoped_users.items():
            channels = policy.get("channels", [])
            allow_dm = policy.get("allow_dm", False)
            print(f"   - {user_id}: channels={channels}, allow_dm={allow_dm}")
    else:
        print("\n⚠️  No scoped users configured")

    routes = config.get("channel_routes", {})
    if routes:
        print(f"\n✅ Channel routes ({len(routes)}):")
        for channel_id, route_key in routes.items():
            print(f"   - {channel_id} -> {route_key}")
    
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


def set_scoped_user(user_id: str, channels: list[str], allow_dm: bool):
    """Set channel-scoped authorization policy for a user."""
    config = load_config()
    scoped = config.setdefault("scoped_authorized_users", {})
    scoped[user_id] = {
        "channels": channels,
        "allow_dm": allow_dm
    }
    save_config(config)
    print(f"✅ Scoped policy set for {user_id}: channels={channels}, allow_dm={allow_dm}")


def remove_scoped_user(user_id: str):
    """Remove channel-scoped authorization policy for a user."""
    config = load_config()
    scoped = config.setdefault("scoped_authorized_users", {})
    if user_id in scoped:
        del scoped[user_id]
        save_config(config)
        print(f"✅ Removed scoped policy for {user_id}")
    else:
        print(f"⚠️  No scoped policy found for {user_id}")


def set_channel_route(channel_id: str, route_key: str):
    """Set route key for a channel."""
    config = load_config()
    routes = config.setdefault("channel_routes", {})
    routes[channel_id] = route_key
    save_config(config)
    print(f"✅ Route set: {channel_id} -> {route_key}")


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

    scoped_add = subparsers.add_parser("scope-set", help="Set scoped user authorization")
    scoped_add.add_argument("user_id", help="Slack user ID")
    scoped_add.add_argument("--channels", required=True, help="Comma-separated Slack channel IDs")
    scoped_add.add_argument("--allow-dm", action="store_true", help="Allow DMs for this scoped user")

    scoped_remove = subparsers.add_parser("scope-remove", help="Remove scoped user authorization")
    scoped_remove.add_argument("user_id", help="Slack user ID")

    route_set = subparsers.add_parser("route-set", help="Set channel route key")
    route_set.add_argument("channel_id", help="Slack channel ID")
    route_set.add_argument("route_key", help="Route key label")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_user(args.user_id)
    elif args.command == "remove":
        remove_user(args.user_id)
    elif args.command == "list":
        list_users()
    elif args.command == "init":
        init_config()
    elif args.command == "scope-set":
        channels = [c.strip() for c in args.channels.split(",") if c.strip()]
        set_scoped_user(args.user_id, channels, args.allow_dm)
    elif args.command == "scope-remove":
        remove_scoped_user(args.user_id)
    elif args.command == "route-set":
        set_channel_route(args.channel_id, args.route_key)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
