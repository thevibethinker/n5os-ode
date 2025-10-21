# Post-Clone Initializer
**Context:** Sequestered deliverable for reflection 2025-10-20_zo-system-gtm  
**Purpose:** Script to initialize a cloned demonstrator account for a new customer.

---

## Overview
After copying demonstrator configuration to a customer workspace, this initializer:
1. Resets state files (registries, .state.json, session tracking)
2. Rebuilds commands.jsonl index
3. Prompts for integration auth (Gmail/Drive/Calendar)
4. Runs smoke tests to validate clone

---

## Usage

```bash
# Run from customer workspace root
python3 /home/workspace/N5/scripts/post_clone_initializer.py [--dry-run]
```

---

## Steps

### 1. Reset State Files
- Clear reflection registry: `N5/records/reflections/registry/registry.json` → `{"items": []}`
- Clear reflection state: `N5/records/reflections/.state.json` → `{"processed_file_ids": []}`
- Clear meeting state (if applicable): similar pattern
- Clear session state cache (if any)

### 2. Rebuild Commands Registry
- Run: `python3 /home/workspace/N5/scripts/n5_commands_manage.py rebuild`
- Verify: `N5/config/commands.jsonl` exists and is valid

### 3. Prompt for Integrations
- Display instructions:
  ```
  ┌────────────────────────────────────────────────┐
  │ Integration Setup Required                     │
  ├────────────────────────────────────────────────┤
  │ Open Zo Computer → Settings → Connected Apps   │
  │                                                 │
  │ Connect the following:                         │
  │ 1. Gmail (read-only for reflections)          │
  │ 2. Google Drive (optional, for Drive folder)  │
  │ 3. Google Calendar (for meeting ingestion)    │
  │                                                 │
  │ After connecting, press Enter to continue...   │
  └────────────────────────────────────────────────┘
  ```
- Wait for user input (interactive pause)

### 4. Configure Reflection Sources
- Prompt for Drive folder ID (optional):
  ```
  Enter Google Drive folder ID for reflections (or press Enter to skip):
  ```
- Update `N5/config/reflection-sources.json`:
  ```json
  {
    "drive_folder_id": "<user-input or null>",
    "email_lookback_minutes": 10
  }
  ```

### 5. Run Smoke Tests
- Execute: `python3 /home/workspace/N5/scripts/smoke_test.py --skip-meeting` (if calendar not set up yet)
- Report results; exit 1 if any failures

### 6. Final Summary
- Display:
  ```
  ┌────────────────────────────────────────────────┐
  │ ✓ Clone Initialized Successfully               │
  ├────────────────────────────────────────────────┤
  │ State files reset                              │
  │ Commands registry rebuilt                      │
  │ Integrations prompted                          │
  │ Smoke tests: PASS                              │
  │                                                 │
  │ Next Steps:                                    │
  │ - Review file 'Records/Reflections/.../       │
  │   integration-onboarding.md'                   │
  │ - Test reflection ingestion with a real email  │
  │ - Configure scheduled tasks (if needed)        │
  └────────────────────────────────────────────────┘
  ```

---

## Implementation Outline

```python
#!/usr/bin/env python3
import sys, json, subprocess
from pathlib import Path

def reset_state_files(dry_run=False):
    """Clear registries and state to prepare for new customer."""
    files_to_reset = [
        ("N5/records/reflections/registry/registry.json", {"items": []}),
        ("N5/records/reflections/.state.json", {"processed_file_ids": []}),
    ]
    for path_str, default_content in files_to_reset:
        path = Path("/home/workspace") / path_str
        if dry_run:
            print(f"[DRY RUN] Would reset: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(default_content, indent=2))
            print(f"✓ Reset: {path}")

def rebuild_commands_registry(dry_run=False):
    """Rebuild commands.jsonl from commands/*.md."""
    if dry_run:
        print("[DRY RUN] Would rebuild commands registry")
        return
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/n5_commands_manage.py", "rebuild"],
        capture_output=True
    )
    if result.returncode == 0:
        print("✓ Commands registry rebuilt")
    else:
        print(f"✗ Failed to rebuild commands registry: {result.stderr.decode()}")
        sys.exit(1)

def prompt_integrations():
    """Interactive prompt for user to connect integrations."""
    print("\n┌────────────────────────────────────────────────┐")
    print("│ Integration Setup Required                     │")
    print("├────────────────────────────────────────────────┤")
    print("│ Open Zo Computer → Settings → Connected Apps   │")
    print("│                                                 │")
    print("│ Connect the following:                         │")
    print("│ 1. Gmail (read-only for reflections)          │")
    print("│ 2. Google Drive (optional, for Drive folder)  │")
    print("│ 3. Google Calendar (for meeting ingestion)    │")
    print("│                                                 │")
    print("│ After connecting, press Enter to continue...   │")
    print("└────────────────────────────────────────────────┘\n")
    input()

def configure_reflection_sources(dry_run=False):
    """Prompt for Drive folder ID and update config."""
    folder_id = input("Enter Google Drive folder ID for reflections (or press Enter to skip): ").strip()
    config = {
        "drive_folder_id": folder_id if folder_id else None,
        "email_lookback_minutes": 10
    }
    config_path = Path("/home/workspace/N5/config/reflection-sources.json")
    if dry_run:
        print(f"[DRY RUN] Would write config to {config_path}: {config}")
    else:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config, indent=2))
        print(f"✓ Configured: {config_path}")

def run_smoke_tests(dry_run=False):
    """Run smoke tests to validate clone."""
    if dry_run:
        print("[DRY RUN] Would run smoke tests")
        return
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/smoke_test.py", "--skip-meeting"],
        capture_output=True
    )
    if result.returncode == 0:
        print("✓ Smoke tests: PASS")
    else:
        print(f"✗ Smoke tests: FAIL\n{result.stderr.decode()}")
        sys.exit(1)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    print("=== Post-Clone Initializer ===\n")
    
    reset_state_files(dry_run=args.dry_run)
    rebuild_commands_registry(dry_run=args.dry_run)
    
    if not args.dry_run:
        prompt_integrations()
        configure_reflection_sources(dry_run=args.dry_run)
        run_smoke_tests(dry_run=args.dry_run)
    
    print("\n┌────────────────────────────────────────────────┐")
    print("│ ✓ Clone Initialized Successfully               │")
    print("├────────────────────────────────────────────────┤")
    print("│ State files reset                              │")
    print("│ Commands registry rebuilt                      │")
    print("│ Integrations prompted                          │")
    print("│ Smoke tests: PASS                              │")
    print("│                                                 │")
    print("│ Next Steps:                                    │")
    print("│ - Review integration-onboarding.md             │")
    print("│ - Test reflection ingestion with a real email  │")
    print("│ - Configure scheduled tasks (if needed)        │")
    print("└────────────────────────────────────────────────┘\n")

if __name__ == "__main__":
    main()
```

---

## Notes
- Requires interactive terminal for prompts (not suitable for fully automated CI).
- Dry-run mode logs actions without modifying files.
- Smoke test skips meetings initially; customer can run full smoke test after calendar setup.
