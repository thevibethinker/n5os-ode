import os
import yaml
import re
from pathlib import Path

PROFILES_DIR = Path("N5/crm_v3/profiles")
ARCHIVE_DIR = PROFILES_DIR / "archive"

def slugify(text):
    if not text or text == "*Not yet enriched*":
        return ""
    return re.sub(r'[^a-zA-Z0-9]', '', text)

def get_new_name(content, current_stem):
    # Try to get Name and Org from content
    name = content.get("person_id", "").replace("-", " ").title().replace(" ", "")
    org = slugify(content.get("organization", ""))
    
    if not name:
        # Fallback to parsing current stem if person_id is missing
        name = current_stem.split("_")[0]
        
    if org:
        new_stem = f"{name}-{org}"
    else:
        new_stem = name
        
    return new_stem

def normalize():
    print(f"Starting CRM Filename Normalization in {PROFILES_DIR}")
    files = [f for f in PROFILES_DIR.glob("*.yaml")]
    
    renames = {}
    
    for f in files:
        with open(f, 'r') as stream:
            try:
                # Use safe_load_all because some files might have multiple docs or be messy
                docs = list(yaml.safe_load_all(stream))
                if not docs:
                    continue
                content = docs[0]
            except Exception as e:
                print(f"Error reading {f.name}: {e}")
                continue
        
        new_stem = get_new_name(content, f.stem)
        new_path = PROFILES_DIR / f"{new_stem}.yaml"
        
        if new_path != f:
            # Handle collisions
            counter = 1
            while new_path.exists() or new_path in renames.values():
                new_path = PROFILES_DIR / f"{new_stem}-{counter}.yaml"
                counter += 1
            
            renames[f] = new_path

    print(f"Found {len(renames)} files to rename.")
    
    for old, new in renames.items():
        print(f"Renaming: {old.name} -> {new.name}")
        # os.rename(old, new) # Commented for dry run initially

if __name__ == "__main__":
    normalize()

