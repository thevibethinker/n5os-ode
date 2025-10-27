#!/usr/bin/env python3
"""
N5 Secrets Manager - Centralized credential storage and access
Implements P23 (Secrets Management) architectural principle
"""
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional, List, Dict

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("ERROR: cryptography library required. Install: pip install cryptography", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Constants
N5_ROOT = Path.home() / "workspace" / "N5"
SECRETS_FILE = N5_ROOT / "config" / "secrets.jsonl"
KEY_FILE = N5_ROOT / "config" / ".secrets.key"
AUDIT_LOG = N5_ROOT / "data" / "secrets_audit.jsonl"


class SecretsManager:
    """Centralized secrets management for N5 system"""
    
    def __init__(self, secrets_file: Optional[Path] = None, key_file: Optional[Path] = None):
        self.secrets_file = secrets_file or SECRETS_FILE
        self.key_file = key_file or KEY_FILE
        self.audit_log = AUDIT_LOG
        
        # Ensure directories exist
        self.secrets_file.parent.mkdir(parents=True, exist_ok=True)
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self.cipher = self._init_encryption()
        
        # Ensure secrets file exists
        if not self.secrets_file.exists():
            self.secrets_file.write_text("")
            logger.info(f"✓ Created secrets file: {self.secrets_file}")
    
    def _init_encryption(self) -> Fernet:
        """Initialize Fernet cipher with master key"""
        # Try environment variable first
        key_b64 = os.getenv("N5_SECRETS_KEY")
        
        if not key_b64:
            # Try key file
            if self.key_file.exists():
                key_b64 = self.key_file.read_text().strip()
            else:
                # Generate new key
                key_b64 = Fernet.generate_key().decode()
                self.key_file.write_text(key_b64)
                self.key_file.chmod(0o600)
                logger.warning(f"⚠️  Generated new master key: {self.key_file}")
                logger.warning("⚠️  BACKUP THIS KEY - Required to decrypt secrets!")
        
        return Fernet(key_b64.encode() if isinstance(key_b64, str) else key_b64)
    
    def _encrypt(self, value: str) -> str:
        """Encrypt a secret value"""
        return self.cipher.encrypt(value.encode()).decode()
    
    def _decrypt(self, encrypted: str) -> str:
        """Decrypt a secret value"""
        return self.cipher.decrypt(encrypted.encode()).decode()
    
    def _load_secrets(self) -> Dict[str, Dict]:
        """Load all secrets from JSONL file"""
        secrets = {}
        if not self.secrets_file.exists():
            return secrets
        
        for line in self.secrets_file.read_text().strip().split("\n"):
            if not line:
                continue
            try:
                secret = json.loads(line)
                secrets[secret["id"]] = secret
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse secret line: {e}")
        
        return secrets
    
    def _save_secrets(self, secrets: Dict[str, Dict]) -> None:
        """Save all secrets to JSONL file"""
        lines = [json.dumps(secret) for secret in secrets.values()]
        self.secrets_file.write_text("\n".join(lines) + "\n" if lines else "")
        self.secrets_file.chmod(0o600)
    
    def _audit_log_entry(self, action: str, secret_id: str, success: bool = True, caller: Optional[str] = None) -> None:
        """Log secret access to audit trail"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "action": action,
            "secret_id": secret_id,
            "success": success,
            "caller": caller or self._get_caller()
        }
        with self.audit_log.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _get_caller(self) -> str:
        """Detect calling script/module"""
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            filename = caller_frame.f_code.co_filename
            return Path(filename).name
        return "unknown"
    
    def get(self, secret_id: str) -> str:
        """Get decrypted secret value by ID"""
        secrets = self._load_secrets()
        
        if secret_id not in secrets:
            self._audit_log_entry("get", secret_id, success=False)
            raise KeyError(f"Secret not found: {secret_id}")
        
        secret = secrets[secret_id]
        decrypted = self._decrypt(secret["value"])
        
        self._audit_log_entry("get", secret_id, success=True)
        return decrypted
    
    def get_full(self, secret_id: str) -> Dict:
        """Get full secret object with metadata (value decrypted)"""
        secrets = self._load_secrets()
        
        if secret_id not in secrets:
            self._audit_log_entry("get_full", secret_id, success=False)
            raise KeyError(f"Secret not found: {secret_id}")
        
        secret = secrets[secret_id].copy()
        secret["value"] = self._decrypt(secret["value"])
        
        self._audit_log_entry("get_full", secret_id, success=True)
        return secret
    
    def set(
        self,
        id: str,
        value: str,
        type: str,
        service: str,
        owner: str,
        purpose: str,
        rotation_days: int = 90,
        tags: Optional[list[str]] = None,
        expires: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """Add or update a secret"""
        secrets = self._load_secrets()
        
        now = datetime.now(timezone.utc).isoformat() + "Z"
        is_update = id in secrets
        
        secret = {
            "id": id,
            "value": self._encrypt(value),
            "type": type,
            "service": service,
            "created": secrets[id]["created"] if is_update else now,
            "last_rotated": now if is_update else None,
            "rotation_days": rotation_days,
            "owner": owner,
            "purpose": purpose,
            "tags": tags or [],
            "expires": expires,
            "metadata": metadata or {}
        }
        
        secrets[id] = secret
        self._save_secrets(secrets)
        
        action = "update" if is_update else "create"
        self._audit_log_entry(action, id, success=True)
        logger.info(f"✓ {action.capitalize()}d secret: {id}")
    
    def rotate(self, secret_id: str, new_value: str) -> None:
        """Rotate a secret (update value and last_rotated timestamp)"""
        secrets = self._load_secrets()
        
        if secret_id not in secrets:
            raise KeyError(f"Secret not found: {secret_id}")
        
        secrets[secret_id]["value"] = self._encrypt(new_value)
        secrets[secret_id]["last_rotated"] = datetime.now(timezone.utc).isoformat() + "Z"
        
        self._save_secrets(secrets)
        self._audit_log_entry("rotate", secret_id, success=True)
        logger.info(f"✓ Rotated secret: {secret_id}")
    
    def list(self, include_values: bool = False) -> List[Dict]:
        """List all secrets (without values by default)"""
        secrets = self._load_secrets()
        result = []
        
        for secret in secrets.values():
            entry = secret.copy()
            if include_values:
                entry["value"] = self._decrypt(entry["value"])
            else:
                entry["value"] = "***REDACTED***"
            result.append(entry)
        
        self._audit_log_entry("list", "all", success=True)
        return result
    
    def delete(self, secret_id: str) -> None:
        """Delete a secret"""
        secrets = self._load_secrets()
        
        if secret_id not in secrets:
            raise KeyError(f"Secret not found: {secret_id}")
        
        del secrets[secret_id]
        self._save_secrets(secrets)
        
        self._audit_log_entry("delete", secret_id, success=True)
        logger.info(f"✓ Deleted secret: {secret_id}")
    
    def check_rotation_due(self, warning_days: int = 7) -> List[Dict]:
        """Check for secrets due for rotation"""
        secrets = self._load_secrets()
        warnings = []
        now = datetime.now(timezone.utc)
        
        for secret in secrets.values():
            last_rotated = secret.get("last_rotated") or secret["created"]
            last_rotated_dt = datetime.fromisoformat(last_rotated.replace("Z", "+00:00"))
            
            rotation_days = secret.get("rotation_days", 90)
            next_rotation = last_rotated_dt + timedelta(days=rotation_days)
            warning_threshold = next_rotation - timedelta(days=warning_days)
            
            if now >= warning_threshold:
                days_until = (next_rotation - now).days
                warnings.append({
                    "id": secret["id"],
                    "service": secret["service"],
                    "last_rotated": last_rotated,
                    "rotation_due": next_rotation.isoformat() + "Z",
                    "days_until": days_until,
                    "overdue": days_until < 0
                })
        
        return sorted(warnings, key=lambda x: x["days_until"])
    
    def export_secret(self, secret_id: str, output_file: Path) -> None:
        """Export a secret to file (encrypted)"""
        secret = self.get_full(secret_id)
        secret["value"] = self._encrypt(secret["value"])  # Re-encrypt
        output_file.write_text(json.dumps(secret, indent=2))
        output_file.chmod(0o600)
        logger.info(f"✓ Exported secret to: {output_file}")
    
    def import_secret(self, input_file: Path) -> None:
        """Import a secret from file"""
        secret = json.loads(input_file.read_text())
        secrets = self._load_secrets()
        secrets[secret["id"]] = secret
        self._save_secrets(secrets)
        logger.info(f"✓ Imported secret: {secret['id']}")


def main():
    """CLI for secrets management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="N5 Secrets Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # List command
    subparsers.add_parser("list", help="List all secrets")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a secret value")
    get_parser.add_argument("id", help="Secret ID")
    get_parser.add_argument("--full", action="store_true", help="Show full metadata")
    
    # Set command
    set_parser = subparsers.add_parser("set", help="Add/update a secret")
    set_parser.add_argument("id", help="Secret ID")
    set_parser.add_argument("--value", required=True, help="Secret value")
    set_parser.add_argument("--type", required=True, choices=["jwt", "api_key", "service_account", "password", "token"], help="Secret type")
    set_parser.add_argument("--service", required=True, help="Service name")
    set_parser.add_argument("--owner", required=True, help="Owner (script/component)")
    set_parser.add_argument("--purpose", required=True, help="Purpose description")
    set_parser.add_argument("--rotation-days", type=int, default=90, help="Rotation frequency (default: 90)")
    set_parser.add_argument("--tags", nargs="+", help="Tags")
    
    # Rotate command
    rotate_parser = subparsers.add_parser("rotate", help="Rotate a secret")
    rotate_parser.add_argument("id", help="Secret ID")
    rotate_parser.add_argument("--new-value", required=True, help="New secret value")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a secret")
    delete_parser.add_argument("id", help="Secret ID")
    
    # Check rotation command
    check_parser = subparsers.add_parser("check-rotation", help="Check secrets due for rotation")
    check_parser.add_argument("--warning-days", type=int, default=14, help="Warning threshold (default: 14)")
    
    args = parser.parse_args()
    
    try:
        manager = SecretsManager()
        
        if args.command == "list":
            secrets = manager.list()
            if not secrets:
                print("No secrets found")
            else:
                for secret in secrets:
                    print(f"{secret['id']:30} | {secret['service']:15} | {secret['type']:15} | {secret['owner']}")
        
        elif args.command == "get":
            if args.full:
                secret = manager.get_full(args.id)
                print(json.dumps(secret, indent=2))
            else:
                value = manager.get(args.id)
                print(value)
        
        elif args.command == "set":
            manager.set(
                id=args.id,
                value=args.value,
                type=args.type,
                service=args.service,
                owner=args.owner,
                purpose=args.purpose,
                rotation_days=args.rotation_days,
                tags=args.tags
            )
        
        elif args.command == "rotate":
            manager.rotate(args.id, args.new_value)
        
        elif args.command == "delete":
            manager.delete(args.id)
        
        elif args.command == "check-rotation":
            warnings = manager.check_rotation_due(args.warning_days)
            if not warnings:
                print("✓ No secrets due for rotation")
            else:
                print(f"⚠️  {len(warnings)} secret(s) due for rotation:\n")
                for w in warnings:
                    status = "OVERDUE" if w["overdue"] else f"Due in {w['days_until']} days"
                    print(f"  {w['id']:30} | {w['service']:15} | {status}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
