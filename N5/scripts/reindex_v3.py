import os
import re
import json
import sqlite3
from pathlib import Path

DB_PATH = Path("N5/data/crm_v3.db")
PROFILES_DIR = Path("N5/crm_v3/profiles")
OUTPUT_INDEX = Path("N5/data/crm_v3_index.jsonl")

def extract_field(content, field):
    match = re.search(f"^{field}:\\s*['\"]?(.+?)['\"]?\\s*$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""

def generate_index():
    if not DB_PATH.exists():
        print(f"Error: DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    profiles = list(PROFILES_DIR.glob("*.yaml"))
    print(f"Indexing {len(profiles)} V3 profiles via Regex...")
    
    index_entries = []
    queued_count = 0
    
    for f in profiles:
        if f.name == "archive" or f.is_dir(): continue
        
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            
            # Simple field extraction
            name = extract_field(content, "name")
            if not name:
                # Fallback to header
                header_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                name = header_match.group(1).strip() if header_match else f.stem.split("-")[0]
                
            email = extract_field(content, "email")
            org = extract_field(content, "organization")
            status = extract_field(content, "enrichment_status")
            p_type = extract_field(content, "person_type")

            entry = {
                "slug": f.stem,
                "name": name,
                "email": email,
                "organization": org,
                "yaml_path": f"N5/crm_v3/profiles/{f.name}",
                "md_path": f"Personal/Knowledge/CRM/individuals/{f.stem}.md"
            }
            index_entries.append(entry)

            # Auto-queue logic
            if email and email != "*Not yet enriched*" and p_type != "internal":
                # Check if profile exists in DB
                c.execute("SELECT id FROM profiles WHERE email = ?", (email,))
                profile_row = c.fetchone()
                
                if profile_row:
                    profile_id = profile_row[0]
                    # Check if already in queue or processing
                    c.execute("SELECT id FROM enrichment_queue WHERE profile_id = ? AND status IN ('queued', 'processing')", (profile_id,))
                    if not c.fetchone():
                        c.execute("""
                            INSERT INTO enrichment_queue (profile_id, priority, scheduled_for, checkpoint, trigger_source)
                            VALUES (?, ?, datetime('now'), ?, ?)
                        """, (profile_id, 50, 'auto_fix', 'pipeline_normalization'))
                        queued_count += 1
                else:
                    # Create profile in DB if missing but file exists
                    # (This handles the case where files exist but DB is missing them)
                    try:
                        c.execute("""
                            INSERT INTO profiles (email, name, yaml_path, source, enrichment_status)
                            VALUES (?, ?, ?, ?, ?)
                        """, (email, name, entry["yaml_path"], 'reindex_sync', 'pending'))
                        profile_id = c.lastrowid
                        c.execute("""
                            INSERT INTO enrichment_queue (profile_id, priority, scheduled_for, checkpoint, trigger_source)
                            VALUES (?, ?, datetime('now'), ?, ?)
                        """, (profile_id, 50, 'auto_fix', 'new_discovery'))
                        queued_count += 1
                    except sqlite3.IntegrityError:
                        pass # Email collision, handled above

        except Exception as e:
            print(f"Error indexing {f.name}: {e}")

    with open(OUTPUT_INDEX, 'w') as out:
        for entry in index_entries:
            out.write(json.dumps(entry) + "\n")
            
    conn.commit()
    conn.close()
    print(f"Index created at {OUTPUT_INDEX}")
    print(f"Processed {len(index_entries)} entries.")
    print(f"Queued {queued_count} profiles for enrichment.")

if __name__ == "__main__":
    generate_index()

