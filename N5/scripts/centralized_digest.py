#!/usr/bin/env python3
"""
Centralized Daily Digest Generator
Merges Luma events, File Flow logs, and Unsent Follow-ups into a single daily report.
"""

import json
import logging
import subprocess
import datetime
from pathlib import Path

# Setup
N5_ROOT = Path("/home/workspace/N5")
SCRIPTS_DIR = N5_ROOT / "scripts"
DIGEST_DIR = N5_ROOT / "digests"
DIGEST_DIR.mkdir(exist_ok=True, parents=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_script(script_name, args=None):
    cmd = ["python3", str(SCRIPTS_DIR / script_name)]
    if args:
        cmd.extend(args)
    try:
        logger.info(f"Running {script_name}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_name}: {e.stderr}")
        return None

def get_luma_data():
    logger.info("Fetching Luma data...")
    # --generate returns JSON with paths to generated files
    output = run_script("luma_digest.py", ["--generate"])
    if output:
        try:
            # Output might contain logs mixed with json if not careful, 
            # but luma_digest.py seems to print only json to stdout in main()
            # Let's try to find the json block if there's noise
            if "{" in output:
                json_str = output[output.find("{"):output.rfind("}")+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error("Failed to parse Luma output")
            return None
    return None

def get_file_flow_data():
    logger.info("Fetching File Flow data...")
    # Parse the log file
    log_file = N5_ROOT / "data" / "file_flow_log.jsonl"
    if not log_file.exists():
        return []
    
    entries = []
    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except:
                    continue
    except Exception as e:
        logger.error(f"Error reading file flow log: {e}")
        return []
        
    # Filter for last 24h
    recent = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for entry in entries:
        ts_str = entry.get("timestamp")
        if ts_str:
            try:
                # Handle Z or offset
                ts = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if (now - ts).total_seconds() < 86400:
                    recent.append(entry)
            except:
                pass
    return recent

def get_followups_data():
    logger.info("Fetching Follow-ups...")
    # Run the digest script
    run_script("n5_unsent_followups_digest.py")
    
    # Find latest
    log_dir = N5_ROOT / "logs"
    files = list(log_dir.glob("unsent_followups_digest_*.md"))
    if not files:
        return None
        
    latest = max(files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Latest follow-up digest: {latest}")
    return latest.read_text()

def generate_report():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    report = f"# 🗞️ Centralized Daily Digest: {date_str}\n\n"
    
    # 1. Luma
    luma_data = get_luma_data()
    report += "## 📅 Luma Event Recommendations\n\n"
    if luma_data and luma_data.get("events", 0) > 0:
        md_path = luma_data.get("digest_md_path")
        if md_path and Path(md_path).exists():
            # Read content, maybe strip header?
            luma_content = Path(md_path).read_text()
            # Remove title if redundant
            luma_content = luma_content.replace("# 🎯 Luma Event Recommendations", "")
            report += luma_content.strip() + "\n"
        else:
            report += "Events found but digest file missing.\n"
    else:
        report += "No new event recommendations today.\n"
    report += "\n---\n\n"
    
    # 2. File Flow
    file_data = get_file_flow_data()
    report += "## 📂 File Flow Highlights (Last 24h)\n\n"
    if file_data:
        for entry in file_data[:10]: # Top 10
            report += f"- **{entry.get('phase', 'Action')}**: {entry.get('notes', '')}\n"
    else:
        report += "No significant file flow activity recorded in the last 24 hours.\n"
    report += "\n---\n\n"
    
    # 3. Follow-ups
    followups = get_followups_data()
    report += "## ✉️ Unsent Follow-ups\n\n"
    if followups:
        # Extract content, remove header
        lines = followups.splitlines()
        # Skip title lines
        clean_lines = []
        skip = False
        for line in lines:
            if line.startswith("# Unsent Follow-Up"):
                continue
            if line.startswith("**Generated:**"):
                continue
            clean_lines.append(line)
        report += "\n".join(clean_lines).strip() + "\n"
    else:
        report += "No unsent follow-up digest found.\n"
        
    # Save
    output_path = DIGEST_DIR / f"centralized_digest_{date_str}.md"
    output_path.write_text(report)
    logger.info(f"Report generated: {output_path}")
    print(f"REPORT_PATH:{output_path}")

if __name__ == "__main__":
    generate_report()

