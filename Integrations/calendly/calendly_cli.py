#!/usr/bin/env python3
import sys
import argparse
import json
from calendly_client import CalendlyClient

def main():
    parser = argparse.ArgumentParser(description="Calendly CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # verify command
    subparsers.add_parser("verify", help="Verify connection and show current user")

    # links command
    links_parser = subparsers.add_parser("links", help="Manage scheduling links")
    links_parser.add_argument("--list", action="store_true", help="List all event types")
    links_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # events command
    events_parser = subparsers.add_parser("events", help="List scheduled events")
    events_parser.add_argument("--upcoming", action="store_true", help="Show upcoming events")
    events_parser.add_argument("--count", type=int, default=10, help="Number of events to fetch")
    events_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # webhooks command
    webhooks_parser = subparsers.add_parser("webhooks", help="Manage webhook subscriptions")
    webhooks_parser.add_argument("--list", action="store_true", help="List all webhooks")
    webhooks_parser.add_argument("--register", action="store_true", help="Register Zo webhook")
    webhooks_parser.add_argument("--delete", type=str, help="Delete webhook by UUID")
    webhooks_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        client = CalendlyClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if args.command == "verify":
        try:
            user = client.get_current_user()
            print("✅ Successfully connected to Calendly.")
            print(f"User: {user['name']} ({user['email']})")
            print(f"URI: {user['uri']}")
            print(f"Organization: {user['current_organization']}")
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            sys.exit(1)

    elif args.command == "links":
        user = client.get_current_user()
        links = client.list_event_types(user_uri=user['uri'])
        active_links = [l for l in links if l.get("active")]
        
        if args.json:
            print(json.dumps(active_links, indent=2))
        else:
            print(f"\nActive Scheduling Links ({len(active_links)}):")
            print("-" * 50)
            for link in active_links:
                print(f"Name: {link['name']}")
                print(f"URL:  {link['scheduling_url']}")
                print(f"Slug: {link.get('slug', 'N/A')}")
                print(f"Duration: {link.get('duration', 'N/A')} min")
                print("-" * 50)

    elif args.command == "events":
        from datetime import datetime, timezone
        user = client.get_current_user()
        
        params = {"user_uri": user['uri'], "count": args.count}
        if args.upcoming:
            params["min_start_time"] = datetime.now(timezone.utc).isoformat()
            params["status"] = "active"
        
        events = client.list_scheduled_events(**params)
        
        if args.json:
            print(json.dumps(events, indent=2))
        else:
            print(f"\nScheduled Events ({len(events)}):")
            print("-" * 60)
            for event in events:
                start = event.get("start_time", "N/A")
                name = event.get("name", "N/A")
                status = event.get("status", "N/A")
                print(f"{start[:16]} | {name} | {status}")
            print("-" * 60)

    elif args.command == "webhooks":
        user = client.get_current_user()
        org_uri = user['current_organization']
        
        if args.list:
            webhooks = client.list_webhook_subscriptions(org_uri)
            if args.json:
                print(json.dumps(webhooks, indent=2))
            else:
                print(f"\nWebhook Subscriptions ({len(webhooks)}):")
                print("-" * 60)
                for wh in webhooks:
                    print(f"URL: {wh['callback_url']}")
                    print(f"Events: {', '.join(wh['events'])}")
                    print(f"State: {wh['state']}")
                    print(f"UUID: {wh['uri'].split('/')[-1]}")
                    print("-" * 60)
        
        elif args.register:
            webhook_url = "https://calendly-auth-va.zocomputer.io/webhook"
            events = ["invitee.created", "invitee.canceled"]
            
            try:
                result = client.create_webhook_subscription(
                    url=webhook_url,
                    events=events,
                    organization_uri=org_uri
                )
                print("✅ Webhook registered successfully!")
                print(f"URL: {result['callback_url']}")
                print(f"Events: {', '.join(result['events'])}")
                print(f"UUID: {result['uri'].split('/')[-1]}")
            except Exception as e:
                print(f"❌ Failed to register webhook: {e}")
                sys.exit(1)
        
        elif args.delete:
            try:
                client.delete_webhook_subscription(args.delete)
                print(f"✅ Webhook {args.delete} deleted.")
            except Exception as e:
                print(f"❌ Failed to delete webhook: {e}")
                sys.exit(1)
        
        else:
            print("Use --list, --register, or --delete <uuid>")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
