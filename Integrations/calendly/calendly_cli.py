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

    args = parser.parse_args()

    try:
        client = CalendlyClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if args.command == "verify":
        try:
            user = client.get_current_user()
            print("Successfully connected to Calendly.")
            print(f"User: {user['name']} ({user['email']})")
            print(f"URI: {user['uri']}")
            print(f"Organization: {user['current_organization']}")
        except Exception as e:
            print(f"Verification failed: {e}")
            sys.exit(1)

    elif args.command == "links":
        if args.list:
            user = client.get_current_user()
            links = client.list_event_types(user_uri=user['uri'])
            print(f"\nActive Scheduling Links ({len(links)}):")
            print("-" * 50)
            for link in links:
                if link.get("active"):
                    print(f"Name: {link['name']}")
                    print(f"URL:  {link['scheduling_url']}")
                    print(f"Slug: {link['slug']}")
                    print("-" * 50)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()

