import yaml
import sys
from pathlib import Path

WORKSPACE = Path("/home/workspace")
MANIFEST_PATH = WORKSPACE / "N5/prefs/context_manifest.yaml"

def test_manifest():
    print(">>> TEST 1: Manifest Integrity")
    if not MANIFEST_PATH.exists():
        print("FAIL: Manifest missing")
        return
    
    try:
        with open(MANIFEST_PATH) as f:
            data = yaml.safe_load(f)
            
        groups = data.get("groups", {})
        print(f"Found {len(groups)} groups: {list(groups.keys())}")
        
        # Check for missing files
        missing_count = 0
        for g_name, g_data in groups.items():
            for file_ref in g_data.get("files", []):
                path = WORKSPACE / file_ref
                if not path.exists():
                    print(f"WARNING: File missing in group '{g_name}': {file_ref}")
                    missing_count += 1
                else:
                    pass # print(f"OK: {file_ref}")
                    
        if missing_count == 0:
            print("SUCCESS: All referenced files exist.")
        else:
            print(f"FAIL: {missing_count} referenced files are missing.")

    except Exception as e:
        print(f"FAIL: YAML Parse Error: {e}")

if __name__ == "__main__":
    test_manifest()

