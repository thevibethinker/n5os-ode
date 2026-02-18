# P34: Centralized Secrets Management

**Category:** Security  
**Priority:** Critical  
**Related:** P2 (SSOT), P5 (Anti-Overwrite), P19 (Error Handling)

---

## Principle

**All API keys, tokens, passwords, and credentials MUST be stored in an encrypted secrets manager. Never store secrets in plaintext files, environment variables (except platform-managed), or hardcoded in scripts.**

---

## Why This Matters

**Security risks of scattered secrets:**
- Accidental git commits exposing credentials
- No audit trail
- No rotation tracking
- Difficult to revoke
- Duplicates across files

**Benefits of centralized management:**
- Encrypted at rest
- Full audit trail
- Rotation tracking
- Single source of truth
- Git-protected by design
- Easy revocation

---

## Implementation

### Standard Access Pattern

```python
#!/usr/bin/env python3
from pathlib import Path
import sys

# Load secrets manager
sys.path.insert(0, str(Path.home() / "workspace" / "N5" / "scripts"))
from n5_secrets import SecretsManager

def main():
    secrets = SecretsManager()
    
    # Get secret (logs access automatically)
    api_key = secrets.get("service_api_key")
    
    # Use secret
    make_api_call(api_key)
    
    # Never print or log the actual value
    logger.info("API call successful (key: service_api_key)")
```

### CLI Interface

```bash
# List all secrets (metadata only, not values)
python3 N5/scripts/n5_secrets.py list

# Get a secret (logs access)
python3 N5/scripts/n5_secrets.py get service_api_key

# Set a new secret
python3 N5/scripts/n5_secrets.py set stripe_key \
  --value "sk_live_..." \
  --service "stripe" \
  --rotation-days 90

# Rotate a secret
python3 N5/scripts/n5_secrets.py rotate service_key --value "new_key"

# Check rotation status
python3 N5/scripts/n5_secrets.py check-rotation
```

### Storage Format

**Location:** `N5/config/secrets.jsonl` (encrypted)  
**Master Key:** `N5/config/.secrets.key` (protected 0600)  
**Audit Log:** `N5/data/secrets_audit.jsonl` (tracks access)

**Each secret stored as:**
```json
{
  "key": "service_api_key",
  "encrypted_value": "gAAAAABm...",
  "service": "service_name",
  "type": "api_key",
  "created_at": "2025-10-26T12:00:00Z",
  "last_rotated": "2025-10-26T12:00:00Z",
  "rotation_days": 90
}
```

---

## Categories & Standards

### API Keys
- **Rotation:** 90 days
- **Format:** Usually `sk_`, `pk_`, or service prefix
- **Usage:** Third-party service authentication

### Service Accounts
- **Rotation:** 180 days
- **Format:** JSON files or long-lived tokens
- **Usage:** Cloud providers (GCP, AWS, etc.)

### Passwords
- **Rotation:** 60 days
- **Format:** High-entropy strings
- **Usage:** Database credentials, admin passwords

### Tokens
- **Rotation:** 30 days
- **Format:** JWT, OAuth, session tokens
- **Usage:** Short-lived authentication

### Platform-Managed Secrets
- **Rotation:** Managed by platform
- **Format:** Environment variables
- **Usage:** Read from `os.getenv()` directly
- **Note:** Don't duplicate in secrets manager

---

## Git Protection

**Required in `.gitignore`:**
```
# Secrets Management (P34)
N5/config/secrets.jsonl
N5/config/.secrets.key
N5/config/credentials/
**/.*env
```

**Exception:** `.env.template` files allowed (no actual secrets)

---

## Master Key Backup

**CRITICAL:** The master key is required to decrypt all secrets. Loss = permanent data loss.

### Backup Storage

**Primary:**
1. Copy `.secrets.key` to secure password manager
2. Label: "N5 Secrets Master Key - [instance]"
3. Include date created

**Secondary:**
1. Print key to paper, store in physical safe
2. Or: Encrypted USB in secure location
3. Label with date and recovery instructions

### Recovery Test

**Quarterly verification:**
```bash
# 1. Backup current key
cp N5/config/.secrets.key N5/config/.secrets.key.backup

# 2. Test recovery from backup
# (Retrieve from password manager)
echo "[paste key]" > N5/config/.secrets.key.test

# 3. Verify access
python3 N5/scripts/n5_secrets.py list

# 4. Restore
rm N5/config/.secrets.key.test N5/config/.secrets.key.backup
```

### Key Rotation

**If master key compromised:**
1. Generate new master key
2. Re-encrypt all secrets with new key
3. Rotate all service credentials
4. Update backup storage
5. Audit all recent access

---

## Migration Guide

### Moving from Scattered Secrets to Centralized

```bash
# 1. Audit current secrets
grep -r "api_key\|password\|token\|secret" --include="*.py" --include="*.sh"

# 2. Move each to secrets manager
python3 N5/scripts/n5_secrets.py set service_key --value "..."

# 3. Update code to use secrets manager
# Before:
API_KEY = "hardcoded_key"

# After:
from n5_secrets import SecretsManager
secrets = SecretsManager()
API_KEY = secrets.get("service_key")

# 4. Remove plaintext files
rm old_credentials.env

# 5. Update .gitignore
echo "N5/config/secrets.jsonl" >> .gitignore
```

---

## Common Mistakes

❌ Storing secrets in git-tracked files
❌ Printing secrets in logs
❌ No rotation schedule
❌ No master key backup
❌ Duplicating platform-managed secrets

**Fix:** Follow this principle strictly. Security is non-negotiable.

---

## Related Principles

- **P2 (SSOT):** One place for all secrets
- **P5 (Anti-Overwrite):** Audit trail prevents silent overwrites
- **P19 (Error Handling):** Handle missing secrets gracefully

---

**Security is cumulative:** One leaked secret can compromise entire system.
