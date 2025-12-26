import sqlite3
import json
import os
import glob
from datetime import datetime
from pathlib import Path

# Paths
DB_CONV = "/home/workspace/N5/data/conversations.db"
DB_MEET = "/home/workspace/N5/data/meeting_pipeline.db"
DB_CRM = "/home/workspace/N5/data/crm_v3.db"
DB_WELL = "/home/workspace/N5/data/wellness.db"
DB_LUMA = "/home/workspace/N5/data/luma_events.db"
SHORTIO_LINKS = "/home/workspace/N5/data/shortio_links.jsonl"
SHORTIO_CLICKS = "/home/workspace/N5/data/shortio_clicks.jsonl"
OUTPUT_PATH = "/home/workspace/Sites/zo-wrapped-2025/src/data/v2_metrics.json"

def get_db_conn(path):
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)

def extract_conversations():
    conn = get_db_conn(DB_CONV)
    cursor = conn.cursor()
    
    # Total and types
    cursor.execute("SELECT type, COUNT(*) FROM conversations GROUP BY type")
    types = dict(cursor.fetchall())
    
    # Agent vs User
    cursor.execute("SELECT COUNT(*) FROM conversations WHERE mode = 'agent' OR title LIKE 'Scheduled%' OR title LIKE 'Execute%'")
    agent_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total = cursor.fetchone()[0]
    
    # Hour distribution
    cursor.execute("SELECT strftime('%H', created_at) as hour, COUNT(*) FROM conversations GROUP BY hour ORDER BY hour")
    hours = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Day distribution
    cursor.execute("SELECT strftime('%w', created_at) as dow, COUNT(*) FROM conversations GROUP BY dow ORDER BY dow")
    dow = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return {
        "total": total,
        "types": types,
        "agent_count": agent_count,
        "user_count": total - agent_count,
        "hour_distribution": hours,
        "day_distribution": dow
    }

def extract_code_metrics():
    base_dir = "/home/workspace/N5"
    extensions = ["*.py", "*.tsx", "*.ts", "*.md", "*.json"]
    metrics = {}
    total_lines = 0
    
    for ext in extensions:
        count = 0
        lines = 0
        for f in glob.glob(f"{base_dir}/**/{ext}", recursive=True):
            count += 1
            try:
                with open(f, 'r', errors='ignore') as file:
                    lines += len(file.readlines())
            except:
                pass
        metrics[ext.replace("*.", "")] = {"files": count, "lines": lines}
        total_lines += lines
        
    return {"breakdown": metrics, "total_lines": total_lines}

def extract_meeting_metrics():
    meeting_base = "/home/workspace/Personal/Meetings"
    # Search for all subdirectories recursively and count those that look like meeting folders
    # We use a pattern that matches the standard dating and state suffix
    all_dirs = glob.glob(f"{meeting_base}/**/*", recursive=True)
    meeting_folders = [d for d in all_dirs if os.path.isdir(d) and (d.endswith("_[M]") or d.endswith("_[P]") or d.endswith("_[C]"))]
    
    # Count B*.md files across all subdirectories
    all_files = glob.glob(f"{meeting_base}/**/B*.md", recursive=True)
    
    return {
        "total_manifest": len(meeting_folders),
        "total_processed": 0, # Unifying into total_manifest for now
        "total_blocks": len(all_files)
    }

def extract_knowledge_metrics():
    knowledge_dir = Path("/home/workspace/Knowledge")
    structure = {}
    
    for item in knowledge_dir.iterdir():
        if item.is_dir():
            count = len(list(item.glob("**/*.md")))
            structure[item.name] = count
            
    return {
        "total_files": len(list(knowledge_dir.glob("**/*.md"))),
        "structure": structure
    }

def extract_shortio():
    links = 0
    clicks = 0
    
    if os.path.exists(SHORTIO_LINKS):
        with open(SHORTIO_LINKS, 'r') as f:
            links = sum(1 for _ in f)
            
    if os.path.exists(SHORTIO_CLICKS):
        with open(SHORTIO_CLICKS, 'r') as f:
            clicks = sum(1 for _ in f)
            
    return {"total_links": links, "total_clicks": clicks}

def main():
    print("Extracting ZoWrapped v2 Metrics...")
    
    data = {
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "conversations": extract_conversations(),
        "code": extract_code_metrics(),
        "meetings": extract_meeting_metrics(),
        "knowledge": extract_knowledge_metrics(),
        "shortio": extract_shortio(),
        "user": "thevibethinker"
    }
    
    # 7. B-Block Density
    try:
        b_block_counts = {}
        # Using shell to count because find/sed is faster for 3000+ files
        import subprocess
        cmd = "find /home/workspace/Personal/Meetings -name 'B[0-9]*.md' | sed 's/.*\\///' | cut -d'_' -f1 | sort | uniq -c"
        result = subprocess.check_output(cmd, shell=True).decode()
        for line in result.strip().split('\n'):
            parts = line.strip().split()
            if len(parts) == 2:
                count, block_type = parts
                b_block_counts[block_type] = int(count)
        data["meetings"]["b_blocks"] = b_block_counts
        data["meetings"]["total_blocks"] = sum(b_block_counts.values())
    except:
        data["meetings"]["b_blocks"] = {}
        data["meetings"]["total_blocks"] = 0
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Success: Metrics written to {OUTPUT_PATH}")
    print(f"Total Conversations: {data['conversations']['total']}")
    print(f"Agent/User: {data['conversations']['agent_count']} / {data['conversations']['user_count']}")

if __name__ == "__main__":
    main()





