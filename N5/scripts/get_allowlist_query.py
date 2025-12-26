import json
from pathlib import Path

CONFIG_FILE = Path("/home/workspace/N5/config/event_sources.json")

def main():
    if not CONFIG_FILE.exists():
        print("subject:\"n5:allowlist\"") 
        return

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except Exception:
        print("subject:\"n5:allowlist\"")
        return

    senders = config.get("senders", [])
    if not senders:
        print("from:me")
        return
    
    sender_query = " OR ".join(senders)
    final_query = f"from:({sender_query}) newer_than:2d"
    print(final_query)

if __name__ == "__main__":
    main()
