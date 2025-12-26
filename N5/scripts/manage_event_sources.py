import json
import argparse
import re
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path("/home/workspace/N5/config/event_sources.json")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input JSON file with emails")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    if not CONFIG_FILE.exists():
        print(f"Config file not found: {CONFIG_FILE}")
        return

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        config = {"senders": [], "domains": [], "last_updated": ""}

    try:
        with open(input_path, "r") as f:
            emails = json.load(f)
    except json.JSONDecodeError:
        print("Invalid JSON in input file")
        return

    new_senders = 0
    
    # Handle list of emails
    if isinstance(emails, dict): # Handle single email wrapper if applicable
        emails = [emails]
        
    for email in emails:
        body = email.get("body", "") or email.get("snippet", "")
        # Regex to find original sender in forwarded email
        # Pattern: "From: Sender Name <sender@example.com>" or just "From: sender@example.com"
        match = re.search(r"From:.*<([^>]+)>|From:\s*([^\s<]+@[^\s<]+)", body, re.IGNORECASE)
        
        sender = None
        if match:
            if match.group(1):
                sender = match.group(1).lower()
            elif match.group(2):
                sender = match.group(2).lower()
        
        if sender:
            if "@" in sender and sender not in config["senders"]:
                config["senders"].append(sender)
                new_senders += 1
                print(f"Added sender: {sender}")

    if new_senders > 0:
        config["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Updated {CONFIG_FILE} with {new_senders} new senders.")
    else:
        print("No new senders found.")

if __name__ == "__main__":
    main()
