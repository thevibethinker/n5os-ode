#!/usr/bin/env python3
"""
Zoputer Client - va-side API client for Archetype Zo communication

Communicates with zoputer.zo.computer via /zo/ask API.
All calls are logged to the dual-sided audit system.

Usage:
    python3 N5/scripts/zoputer_client.py ping
    python3 N5/scripts/zoputer_client.py status
    python3 N5/scripts/zoputer_client.py export --skill <skill-name> [--version X.Y.Z] [--notes "..."]

Requires:
    ZOPUTER_API_KEY environment variable (zoputer's API key)
"""

import argparse
import json
import os
import sys
import time
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional
import hashlib
import uuid

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import requests
except ImportError:
    print("Error: requests library required. Run: pip install requests")
    sys.exit(1)

# Configuration
ZOPUTER_API_URL = "https://api.zo.computer/zo/ask"
TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # seconds

# Audit logger path
AUDIT_LOGGER = Path("/home/workspace/Skills/audit-system/scripts/audit_logger.py")


def get_api_key() -> str:
    """Get the zoputer API key from environment."""
    key = os.environ.get("ZOPUTER_API_KEY")
    if not key:
        print("Error: ZOPUTER_API_KEY environment variable not set")
        print("Add it in Zo Settings > Developers > Secrets")
        sys.exit(1)
    return key


def log_audit(entry_type: str, direction: str, payload: dict, correlation_id: Optional[str] = None) -> None:
    """Log to the audit system if available."""
    if not AUDIT_LOGGER.exists():
        return
    
    import subprocess
    try:
        cmd = [
            "python3", str(AUDIT_LOGGER),
            "log",
            "--type", entry_type,
            "--direction", direction,
            "--payload", json.dumps(payload),
        ]
        if correlation_id:
            cmd.extend(["--correlation-id", correlation_id])
        
        subprocess.run(cmd, capture_output=True, timeout=5)
    except Exception:
        pass  # Don't fail operations if audit logging fails


def call_zoputer(prompt: str, correlation_id: Optional[str] = None) -> dict:
    """
    Call zoputer via /zo/ask API with retry logic.
    
    Args:
        prompt: The prompt to send to zoputer
        correlation_id: Optional correlation ID for audit linking
    
    Returns:
        Response dict with 'output' key
    
    Raises:
        Exception on failure after retries
    """
    api_key = get_api_key()
    
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }
    
    payload = {
        "input": prompt
    }
    
    # Log outbound request
    log_audit(
        entry_type="api_call",
        direction="va-to-zoputer",
        payload={"prompt_preview": prompt[:200], "correlation_id": correlation_id},
        correlation_id=correlation_id
    )
    
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                ZOPUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=TIMEOUT_SECONDS
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Log successful response
                log_audit(
                    entry_type="api_response",
                    direction="zoputer-to-va",
                    payload={"status": "success", "correlation_id": correlation_id},
                    correlation_id=correlation_id
                )
                
                return result
            
            elif response.status_code == 401:
                print("Error: Authentication failed. Check ZOPUTER_API_KEY.")
                log_audit(
                    entry_type="api_error",
                    direction="zoputer-to-va",
                    payload={"error": "auth_failed", "status_code": 401},
                    correlation_id=correlation_id
                )
                sys.exit(1)
            
            else:
                last_error = f"HTTP {response.status_code}: {response.text}"
        
        except requests.Timeout:
            last_error = "Request timed out"
        except requests.ConnectionError as e:
            last_error = f"Connection error: {e}"
        except Exception as e:
            last_error = f"Unexpected error: {e}"
        
        # Retry with exponential backoff
        if attempt < MAX_RETRIES - 1:
            wait_time = RETRY_BACKOFF_BASE ** attempt
            print(f"Attempt {attempt + 1} failed: {last_error}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    # All retries exhausted
    log_audit(
        entry_type="api_error",
        direction="va-to-zoputer",
        payload={"error": last_error, "retries_exhausted": True},
        correlation_id=correlation_id
    )
    
    raise Exception(f"Failed after {MAX_RETRIES} attempts: {last_error}")


def cmd_ping(args) -> int:
    """Ping zoputer to check connectivity."""
    correlation_id = f"ping-{uuid.uuid4().hex[:8]}"
    
    print("Pinging zoputer.zo.computer...")
    start_time = time.time()
    
    try:
        # Simple ping prompt
        prompt = """You are zoputer, the Archetype Zo. Respond with a JSON object:
{
  "status": "online",
  "instance": "zoputer",
  "timestamp": "<current UTC ISO timestamp>",
  "message": "Archetype Zo ready"
}
Respond ONLY with the JSON, no other text."""

        result = call_zoputer(prompt, correlation_id)
        elapsed = time.time() - start_time
        
        output = result.get("output", "")
        
        print(f"\n✓ Zoputer responded in {elapsed:.2f}s")
        print(f"Response: {output}")
        
        return 0
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n✗ Ping failed after {elapsed:.2f}s")
        print(f"Error: {e}")
        return 1


def cmd_status(args) -> int:
    """Get zoputer status and last sync info."""
    correlation_id = f"status-{uuid.uuid4().hex[:8]}"
    
    print("Checking zoputer status...")
    
    try:
        prompt = """You are zoputer, the Archetype Zo. Report your status as JSON:
{
  "status": "online",
  "instance": "zoputer",
  "timestamp": "<current UTC ISO timestamp>",
  "workspace_exists": true/false,
  "skills_count": <number of skills in Skills/ folder>,
  "prompts_count": <number of prompts in Prompts/ folder>,
  "last_export_received": "<timestamp or null if none>",
  "audit_db_exists": true/false
}

Check your filesystem and respond with accurate counts. ONLY output JSON."""

        result = call_zoputer(prompt, correlation_id)
        output = result.get("output", "")
        
        print("\nZoputer Status:")
        print("-" * 40)
        
        try:
            status = json.loads(output)
            print(f"  Instance: {status.get('instance', 'unknown')}")
            print(f"  Status: {status.get('status', 'unknown')}")
            print(f"  Skills: {status.get('skills_count', '?')}")
            print(f"  Prompts: {status.get('prompts_count', '?')}")
            print(f"  Last export: {status.get('last_export_received', 'never')}")
            print(f"  Audit DB: {'✓' if status.get('audit_db_exists') else '✗'}")
        except json.JSONDecodeError:
            print(f"  Raw response: {output}")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Status check failed: {e}")
        return 1


def bundle_skill(skill_path: Path, version: str, notes: str) -> tuple[Path, dict]:
    """
    Bundle a skill directory into a tarball with manifest.
    
    Returns:
        Tuple of (tarball_path, manifest_dict)
    """
    skill_name = skill_path.name
    
    # Create manifest
    manifest = {
        "skill_name": skill_name,
        "version": version,
        "notes": notes,
        "source": "va.zo.computer",
        "bundled_at": datetime.utcnow().isoformat(),
        "files": []
    }
    
    # Collect files
    for f in skill_path.rglob("*"):
        if f.is_file():
            rel_path = f.relative_to(skill_path)
            manifest["files"].append({
                "path": str(rel_path),
                "size": f.stat().st_size,
                "hash": hashlib.sha256(f.read_bytes()).hexdigest()[:16]
            })
    
    manifest["file_count"] = len(manifest["files"])
    
    # Create tarball
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tarball_path = Path(tmp.name)
    
    with tarfile.open(tarball_path, "w:gz") as tar:
        # Add manifest
        manifest_json = json.dumps(manifest, indent=2).encode()
        import io
        manifest_info = tarfile.TarInfo(name="manifest.json")
        manifest_info.size = len(manifest_json)
        tar.addfile(manifest_info, io.BytesIO(manifest_json))
        
        # Add skill files
        tar.add(skill_path, arcname=skill_name)
    
    return tarball_path, manifest


def cmd_export(args) -> int:
    """Export a skill to zoputer."""
    skill_path = Path(f"/home/workspace/Skills/{args.skill}")
    
    if not skill_path.exists():
        print(f"Error: Skill not found at {skill_path}")
        return 1
    
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: No SKILL.md found in {skill_path}")
        return 1
    
    correlation_id = f"export-{args.skill}-{uuid.uuid4().hex[:8]}"
    version = args.version or "1.0.0"
    notes = args.notes or ""
    
    print(f"Bundling skill: {args.skill}")
    tarball_path, manifest = bundle_skill(skill_path, version, notes)
    
    print(f"  Files: {manifest['file_count']}")
    print(f"  Version: {version}")
    
    # For now, we'll send the manifest and instruction to zoputer
    # In a real implementation, we'd upload the tarball to a signed URL
    # and have zoputer download it
    
    try:
        prompt = f"""You are zoputer, the Archetype Zo. 
A skill export has been initiated from va.zo.computer.

Skill manifest:
```json
{json.dumps(manifest, indent=2)}
```

For now, acknowledge receipt and confirm you're ready to receive exports.
Respond with JSON:
{{
  "status": "acknowledged",
  "skill_name": "{args.skill}",
  "ready_to_receive": true,
  "message": "Ready to receive skill bundle when file transfer is implemented"
}}

ONLY output JSON."""

        result = call_zoputer(prompt, correlation_id)
        output = result.get("output", "")
        
        print(f"\n✓ Export acknowledged by zoputer")
        print(f"Response: {output}")
        
        # Cleanup
        tarball_path.unlink()
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Export failed: {e}")
        if tarball_path.exists():
            tarball_path.unlink()
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Zoputer Client - communicate with Archetype Zo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 N5/scripts/zoputer_client.py ping
  python3 N5/scripts/zoputer_client.py status  
  python3 N5/scripts/zoputer_client.py export --skill content-classifier --version 1.2.0
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ping
    subparsers.add_parser("ping", help="Check connectivity to zoputer")
    
    # status
    subparsers.add_parser("status", help="Get zoputer status and info")
    
    # export
    export_parser = subparsers.add_parser("export", help="Export a skill to zoputer")
    export_parser.add_argument("--skill", required=True, help="Skill name to export")
    export_parser.add_argument("--version", help="Version string (default: 1.0.0)")
    export_parser.add_argument("--notes", help="Export notes")
    
    args = parser.parse_args()
    
    if args.command == "ping":
        sys.exit(cmd_ping(args))
    elif args.command == "status":
        sys.exit(cmd_status(args))
    elif args.command == "export":
        sys.exit(cmd_export(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
