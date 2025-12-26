#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import Counter

WORKSPACE_ROOT = Path("/home/workspace")
RAW_DATA_FILE = WORKSPACE_ROOT / "N5/data/zo_wrapped_raw.json"
FINAL_DATA_FILE = WORKSPACE_ROOT / "N5/data/zo_wrapped_metrics.json"
CONVOS_DB = WORKSPACE_ROOT / "N5/data/conversations.db"

def get_monthly_distribution():
    if not CONVOS_DB.exists():
        return {}
    
    conn = sqlite3.connect(CONVOS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT strftime('%m', created_at) as month, COUNT(*) FROM conversations WHERE created_at LIKE '2025%' GROUP BY month")
    dist = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return dist

def synthesize():
    if not RAW_DATA_FILE.exists():
        print("Raw data not found. Run extraction first.")
        return

    with open(RAW_DATA_FILE, "r") as f:
        raw = json.load(f)

    # Calculate Top Commands
    top_commands = sorted(raw.get("command_usage", {}).items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calculate Monthly Distribution
    monthly = get_monthly_distribution()
    month_names = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    peak_month_val = max(monthly, key=monthly.get) if monthly else "None"
    peak_month_name = month_names.get(peak_month_val, "None")

    # Git Hour Analysis
    all_hours = []
    if "repos" in raw.get("git", {}):
        for repo, data in raw["git"]["repos"].items():
            if data and isinstance(data, dict) and "hours" in data:
                all_hours.extend(data["hours"])
    
    peak_hour = Counter(all_hours).most_common(1)[0][0] if all_hours else "Unknown"

    # Define the Narrative
    narrative = {
        "title": "ZoWrapped 2025",
        "user": "thevibethinker",
        "milestones": {
            "total_conversations": raw["db"]["total_conversations"],
            "total_commits": raw["git"]["total_commits"],
            "sites_created": raw["fs"]["sites_count"],
            "prompts_created": raw["fs"]["prompts_count"]
        },
        "links": raw.get("links", {}),
        "n5_mechanics": raw.get("n5", {}),
        "convo_types": {k: v for k, v in raw["db"]["convo_types"].items() if k not in ["automation", "operations"]},
        "sub_types": raw["db"]["sub_types"],
        "top_commands": [{"name": k, "count": v} for k, v in top_commands],
        "peak": {
            "month": peak_month_name,
            "hour": f"{peak_hour}:00",
            "persona": "Late Night Architect" if int(peak_hour) < 5 or int(peak_hour) > 22 else "Productive Builder"
        },
        "sites": raw["fs"]["sites_list"],
        "file_growth": raw["fs"]["file_types"]
    }

    with open(FINAL_DATA_FILE, "w") as f:
        json.dump(narrative, f, indent=2)
    
    print(f"Synthesis complete. Narrative saved to {FINAL_DATA_FILE}")

if __name__ == "__main__":
    synthesize()





