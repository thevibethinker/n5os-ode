import os
import re
import yaml
import sqlite3
from pathlib import Path
import shutil

DB_PATH = Path("N5/data/crm_v3.db")
PROFILES_DIR = Path("N5/crm_v3/profiles")
MD_DIR = Path("Personal/Knowledge/CRM/individuals")

def camel_case(text):
    if not text or text == "*Not yet enriched*":
        return ""
    # Remove special chars and capitalize words
    words = re.findall(r'[a-zA-Z0-9]+', text)
    return "".join(w.capitalize() for w in words)

def clean_yaml_content(content_str):
    """
    Manually fix common N5 YAML issues before parsing.
    Specifically: email: *Not yet enriched* -> email: '*Not yet enriched*'
    """
    content_str = re.sub(r":\s+\*Not yet enriched\*", r": '*Not yet enriched*'", content_str)
    return content_str

def get_metadata(filepath):
    """Extract name and organization using regex to avoid YAML parsing errors on messy files."""
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    content = clean_yaml_content(content)
    
    name_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    org_match = re.search(r"\*\*Organization:\*\*\s*(.+)$", content, re.MULTILINE)
    
    # Fallback to YAML parse if regex fails
    try:
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            name = name_match.group(1).strip() if name_match else data.get("name", "")
            org = org_match.group(1).strip() if org_match else data.get("organization", "")
        else:
            name = name_match.group(1).strip() if name_match else ""
            org = org_match.group(1).strip() if org_match else ""
    except:
        name = name_match.group(1).strip() if name_match else ""
        org = org_match.group(1).strip() if org_match else ""

    return name, org

def normalize():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    files = list(PROFILES_DIR.glob("*.yaml"))
    print(f"Found {len(files)} profiles to normalize.")

    processed_count = 0
    rename_map = {} # old_path -> new_path

    for f in files:
        if f.name == "archive": continue
        
        name, org = get_metadata(f)
        
        # Clean Name and Org for filename
        clean_name = camel_case(name)
        clean_org = camel_case(org)
        
        if not clean_name:
            # Fallback to current filename stem
            clean_name = camel_case(f.stem.split("_")[0])

        new_stem = f"{clean_name}-{clean_org}" if clean_org else clean_name
        new_filename = f"{new_stem}.yaml"
        new_path = PROFILES_DIR / new_filename
        
        # Handle collisions
        if new_path.exists() and new_path != f:
            counter = 1
            while (PROFILES_DIR / f"{new_stem}-{counter}.yaml").exists():
                counter += 1
            new_filename = f"{new_stem}-{counter}.yaml"
            new_path = PROFILES_DIR / new_filename

        if f != new_path:
            print(f"Normalizing: {f.name} -> {new_filename}")
            
            # 1. Update YAML content if possible (fix the quotes)
            try:
                raw = f.read_text()
                fixed_raw = clean_yaml_content(raw)
                # Ensure the header matches the new name
                if name:
                    fixed_raw = re.sub(r"^#\s+.+$", f"# {name}", fixed_raw, flags=re.MULTILINE)
                f.write_text(fixed_raw)
            except Exception as e:
                print(f"  ⚠ Failed to clean YAML content for {f.name}: {e}")

            # 2. Rename YAML file
            try:
                os.rename(f, new_path)
            except Exception as e:
                print(f"  ❌ Failed to rename {f.name}: {e}")
                continue

            # 3. Update Database
            old_rel_path = f"N5/crm_v3/profiles/{f.name}"
            new_rel_path = f"N5/crm_v3/profiles/{new_filename}"
            c.execute("UPDATE profiles SET yaml_path = ?, name = ? WHERE yaml_path = ?", (new_rel_path, name, old_rel_path))
            
            # 4. Sync Markdown file
            old_md = MD_DIR / f"{f.stem}.md"
            new_md = MD_DIR / f"{new_path.stem}.md"
            if old_md.exists():
                print(f"  Syncing MD: {old_md.name} -> {new_md.name}")
                os.rename(old_md, new_md)

            processed_count += 1

    conn.commit()
    conn.close()
    print(f"\nNormalization complete. {processed_count} profiles updated.")

if __name__ == "__main__":
    normalize()

