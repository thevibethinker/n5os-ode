#!/usr/bin/env python3
"""
N5 Minimal Bootstrap - Connects to parent Zo and pulls what's needed
SLIM: Just connection + directory structure, parent provides the rest
"""

import os
import sys
import urllib.request
from pathlib import Path

PARENT_URL = "https://n5-bootstrap-support-va.zocomputer.io"
WORKSPACE = Path("/home/workspace")

def print_step(msg):
    print(f"\n{'='*60}\n{msg}\n{'='*60}")

def fetch_from_parent(endpoint):
    """Fetch content from parent Zo"""
    try:
        url = f"{PARENT_URL}/{endpoint}"
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Failed to fetch {endpoint}: {e}")
        return None

def create_directories():
    """Create N5 directory structure"""
    print_step("Creating N5 directory structure...")
    
    dirs = [
        "N5/scripts", "N5/config/credentials", "N5/schemas",
        "N5/commands", "N5/prefs/operations", "N5/prefs/system",
        "N5/prefs/communication", "N5/records/meetings",
        "N5/lists", "N5/intelligence", "Knowledge/architectural",
        "Documents", "Lists", "Records/Personal", "Records/Temporary"
    ]
    
    for d in dirs:
        (WORKSPACE / d).mkdir(parents=True, exist_ok=True)
        print(f"✓ {d}")

def setup_conditional_rules():
    """Fetch and display conditional rules from parent"""
    print_step("Fetching conditional rules from parent Zo...")
    
    rules = fetch_from_parent("configs/conditional_rules.md")
    if rules:
        rules_file = WORKSPACE / "N5" / "CONDITIONAL_RULES.md"
        rules_file.write_text(rules)
        print(f"✓ Saved to: {rules_file}")
        print("\n⚠️  IMPORTANT: Add these rules to your Zo settings!")
        print("   Settings → User Rules → Conditional Rules")
    else:
        print("⚠️  Could not fetch rules - you can add them manually later")

def create_bootstrap_client():
    """Create client script for ongoing parent communication"""
    print_step("Creating parent Zo connection client...")
    
    client_script = WORKSPACE / "N5" / "scripts" / "n5_connect_parent.py"
    client_code = f'''#!/usr/bin/env python3
import urllib.request, sys
PARENT = "{PARENT_URL}"
if len(sys.argv) < 2:
    print("Usage: python3 n5_connect_parent.py <endpoint>")
    sys.exit(1)
try:
    with urllib.request.urlopen(f"{{PARENT}}/{{sys.argv[1]}}", timeout=10) as r:
        print(r.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
'''
    client_script.write_text(client_code)
    client_script.chmod(0o755)
    print(f"✓ Created: {client_script}")

def create_readme():
    """Create basic README"""
    readme = WORKSPACE / "Documents" / "N5.md"
    readme.write_text(f'''# N5 OS - Minimal Bootstrap

Connected to parent at: {PARENT_URL}

## Next Steps
1. Add conditional rules from N5/CONDITIONAL_RULES.md to Zo settings
2. Get help: python3 N5/scripts/n5_connect_parent.py help/troubleshooting.md
3. Ask your Zo AI for guidance (it has the bootstrap persona)

## Philosophy
Minimal bootstrap. Pull what you need from parent when you need it.
''')
    print(f"✓ Created: {readme}")

def main():
    print("\n╔═══════════════════════════════════════╗")
    print("║   N5 MINIMAL BOOTSTRAP v1.0.0         ║")
    print("╚═══════════════════════════════════════╝\n")
    
    print_step("Testing parent Zo connection...")
    test = fetch_from_parent("README.md")
    print("✓ Connected!" if test else "⚠️  Connection issue (will continue anyway)")
    
    create_directories()
    setup_conditional_rules()
    create_bootstrap_client()
    create_readme()
    
    print_step("✅ BOOTSTRAP COMPLETE")
    print("""
Next: 
1. Add rules from N5/CONDITIONAL_RULES.md to Zo settings
2. Read Documents/N5.md
3. Ask Zo AI: "Help me set up N5"
    """)

if __name__ == "__main__":
    main()
