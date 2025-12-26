#!/usr/bin/env python3
import os
import sqlite3
import json
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path("/home/workspace")
CONVOS_DB = WORKSPACE_ROOT / "N5/data/conversations.db"
OUTPUT_FILE = WORKSPACE_ROOT / "N5/data/zo_wrapped_raw.json"

def run_cmd(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def get_git_stats(path):
    if not (path / ".git").exists():
        return None
    
    # Commit Count in 2025
    commit_count = run_cmd('git log --since="2025-01-01" --oneline | wc -l', cwd=path)
    
    # Lines added/deleted in 2025
    git_diff = run_cmd('git log --since="2025-01-01" --pretty=tformat: --numstat | awk \'{ add += $1; subs += $2; loc += $1 - $2 } END { printf "%s,%s,%s", add, subs, loc }\'', cwd=path)
    
    # Hour distribution
    hours_log = run_cmd("git log --since='2025-01-01' --format='%ad' --date=format:'%H'", cwd=path)
    
    return {
        "commits": commit_count,
        "loc": git_diff,
        "hours": hours_log.split('\n') if hours_log else []
    }

def get_db_stats():
    if not CONVOS_DB.exists():
        return {"error": "Conversations DB not found"}
    
    conn = sqlite3.connect(CONVOS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    stats = {}
    
    # Conversations per type
    cursor.execute("SELECT type, COUNT(*) as count FROM conversations GROUP BY type")
    stats["convo_types"] = {row["type"]: row["count"] for row in cursor.fetchall()}
    
    # Sub-types (from mode)
    cursor.execute("SELECT mode, COUNT(*) as count FROM conversations WHERE mode != '' GROUP BY mode ORDER BY count DESC LIMIT 10")
    stats["sub_types"] = {row["mode"]: row["count"] for row in cursor.fetchall()}
    
    # Total count
    cursor.execute("SELECT COUNT(*) as count FROM conversations")
    stats["total_conversations"] = cursor.fetchone()["count"]

    # Persona Usage (Deterministic: scan for set_active_persona in titles/tags)
    personas = ["Builder", "Strategist", "Architect", "Teacher", "Researcher", "Debugger", "Writer"]
    persona_counts = {persona: 0 for persona in personas}
    for persona in personas:
        cursor.execute(f"SELECT COUNT(*) as count FROM conversations WHERE (tags LIKE ? OR title LIKE ?) AND created_at LIKE '2025%'", (f"%{persona}%", f"%{persona}%"))
        persona_counts[persona] = cursor.fetchone()["count"]
    stats["persona_usage"] = persona_counts

    # Artifacts count (try a different query)
    cursor.execute("SELECT COUNT(*) as count FROM artifacts")
    stats["total_artifacts"] = cursor.fetchone()["count"]
    
    # Total Issues encountered
    cursor.execute("SELECT COUNT(*) as count FROM issues")
    stats["total_issues"] = cursor.fetchone()["count"]

    conn.close()
    return stats

def get_fs_stats():
    sites_path = WORKSPACE_ROOT / "Sites"
    prompts_path = WORKSPACE_ROOT / "Prompts"
    
    sites = [d.name for d in sites_path.iterdir() if d.is_dir()]
    prompts = [f.stem.replace(".prompt", "") for f in prompts_path.glob("*.prompt.md")]
    
    # File type breakdown in Projects and Sites
    file_types = {}
    for ext in ['*.py', '*.tsx', '*.ts', '*.md', '*.json']:
        count = len(list(WORKSPACE_ROOT.rglob(ext)))
        file_types[ext] = count
        
    return {
        "sites_count": len(sites),
        "sites_list": sites,
        "prompts_count": len(prompts),
        "prompts_list": prompts,
        "file_types": file_types
    }

def get_token_estimate():
    # Estimate tokens from workspace size
    total_size = 0
    workspaces_dir = Path("/home/.z/workspaces")
    if not workspaces_dir.exists():
        return 0
    
    # Walk all files in workspaces and sum size
    for f in workspaces_dir.rglob("*"):
        if f.is_file():
            total_size += f.stat().st_size
            
    # Heuristic: 1 token approx 4 characters, 1 byte approx 1 character
    return total_size // 4

def get_n5_mechanics():
    meetings_path = WORKSPACE_ROOT / "Personal/Meetings"
    
    # Meeting Stats
    manifests = run_cmd(f"find {meetings_path} -name 'manifest.json' | wc -l")
    blocks = run_cmd(f"find {meetings_path} -name 'B*.md' | wc -l")
    processed = run_cmd(f"find {meetings_path} -name '*_[P]' -type d | wc -l")
    manifested = run_cmd(f"find {meetings_path} -name '*_[M]' -type d | wc -l")
    
    # Lists
    lists_count = run_cmd(f"find {WORKSPACE_ROOT / 'Lists'} -type f | wc -l")
    
    # Cornerstone Tasks
    # We can get this from list_scheduled_tasks results or by scanning titles for ⇱
    # For the script, we'll use a placeholder or scan a known file.
    
    return {
        "meetings": {
            "total_manifests": int(manifests) if manifests.isdigit() else 0,
            "total_blocks": int(blocks) if blocks.isdigit() else 0,
            "state_p": int(processed) if processed.isdigit() else 0,
            "state_m": int(manifested) if manifested.isdigit() else 0
        },
        "lists_count": int(lists_count) if lists_count.isdigit() else 0
    }

def main():
    print(f"Starting extraction at {datetime.now()}")
    
    db_stats = get_db_stats()
    fs_stats = get_fs_stats()
    
    # Command Usage: count mentions of prompt names in DB
    command_usage = {}
    if "error" not in db_stats:
        conn = sqlite3.connect(CONVOS_DB)
        cursor = conn.cursor()
        for prompt in fs_stats["prompts_list"]:
            cursor.execute("SELECT COUNT(*) FROM conversations WHERE (focus LIKE ? OR objective LIKE ? OR tags LIKE ?) AND created_at LIKE '2025%'", (f"%{prompt}%", f"%{prompt}%", f"%{prompt}%"))
            count = cursor.fetchone()[0]
            if count > 0:
                command_usage[prompt] = count
        conn.close()

    git_stats = {}
    repos = [WORKSPACE_ROOT / "N5", WORKSPACE_ROOT / "Sites"]
    for repo_dir in repos:
        if repo_dir.exists():
            for item in repo_dir.iterdir():
                if item.is_dir() and (item / ".git").exists():
                    stats = get_git_stats(item)
                    if stats:
                        git_stats[item.name] = stats
    
    total_commits = sum(int(s["commits"] or 0) for s in git_stats.values())
    
    # Extract total loc from the comma-separated string
    total_loc = 0
    for s in git_stats.values():
        if s["loc"] and "," in s["loc"]:
            try:
                total_loc += int(s["loc"].split(",")[2])
            except (ValueError, IndexError):
                pass

    # Get n5 mechanics
    n5_stats = get_n5_mechanics()
    
    # Final assembly
    results = {
        "timestamp": datetime.now().isoformat(),
        "git": {
            "total_commits": total_commits,
            "total_loc": total_loc,
            "repos": git_stats
        },
        "db": db_stats,
        "fs": fs_stats,
        "n5": n5_stats,
        "command_usage": command_usage,
        "links": {
            "github": "https://github.com/vrijenattawar",
            "twitter": "https://twitter.com/thevibethinker",
            "linkedin": "https://www.linkedin.com/in/vrijenattawar"
        }
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Extraction complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()







