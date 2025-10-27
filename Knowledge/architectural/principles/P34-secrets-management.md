# P34: Centralized Secrets Management

**Category:** Security, Critical  
**Status:** Active  
**Created:** 2025-10-26  
**Related:** P2 (SSOT), P5 (Anti-Overwrite), P19 (Error Handling), P21 (Document Assumptions)

---

## Principle

**All API keys, tokens, passwords, and credentials used by N5 systems MUST be stored in the encrypted secrets manager (`N5/scripts/n5_secrets.py`). Never store secrets in plaintext files, environment variables (except Zo-managed), or hardcoded in scripts.**

---

## Why This Matters

**Security risks of scattered secrets:**
- Accidental git commits exposing credentials
- No audit trail of who accessed what
- No rotation tracking or reminders
- Difficult to revoke compromised credentials
- Violation of compliance requirements
- Duplicates across multiple files

**Benefits of centralized management:**
- Encrypted at rest (Fernet AES-128)
- Full audit trail (who, when, what)
- Rotation tracking with automated reminders
- Single source of truth (P2)
- Git-protected by design
- Easy revocation and rollover

---

## Implementation

### Standard Access Pattern

```python
#!/usr/bin/env python3
from pathlib import Path
import sys

# Add N5 scripts to path
sys.path.insert(0, str(Path.home() / "workspace" / "N5" / "scripts"))
from n5_secrets import SecretsManager

def main():
    secrets = SecretsManager()
    
    # Get secret (logs access automatically)
    api_key = secrets.get("n8n_api_key")
    
    # Use secret
    make_api_call(api_key)
    
    # Never print or log the actual secret value
    logger.info("API call successful (key: n8n_api_key)")

if __name__ == "__main__":
    main()
```

### CLI Interface

```bash
# List all secrets (shows metadata only, not values)
python3 N5/scripts/n5_secrets.py list

# Get a secret (logs access)
python3 N5/scripts/n5_secrets.py get n8n_api_key

# Set a new secret
python3 N5/scripts/n5_secrets.py set stripe_api_key \
  --value "sk_live_..." \
  --service "stripe" \
  --type "api_key" \
  --context "payment_processor" \
  --rotation-days 90

# Rotate a secret (marks old as rotated, requires new value)
python3 N5/scripts/n5_secrets.py rotate n8n_api_key --value "new_key_here"

# Check rotation status
python3 N5/scripts/n5_secrets.py check-rotation

# Delete a secret (careful!)
python3 N5/scripts/n5_secrets.py delete old_unused_key
```

### Storage Format

**Location:** `/home/workspace/N5/config/secrets.jsonl` (encrypted)  
**Master Key:** `/home/workspace/N5/config/.secrets.key` (protected 0600)  
**Audit Log:** `/home/workspace/N5/data/secrets_audit.jsonl` (plaintext, tracks access)

**Each secret stored as:**
```json
{
  "key": "n8n_api_key",
  "encrypted_value": "gAAAAABm...",
  "service": "n8n",
  "type": "api_key",
  "context": "n8n_processor",
  "created_at": "2025-10-26T12:00:00Z",
  "last_rotated": "2025-10-26T12:00:00Z",
  "rotation_days": 90,
  "metadata": {}
}
```

---

## Categories & Standards

### API Keys
- **Rotation:** 90 days
- **Format:** Usually starts with `sk_`, `pk_`, or service-specific prefix
- **Usage:** Third-party service authentication

### Service Accounts
- **Rotation:** 180 days
- **Format:** JSON files or long-lived tokens
- **Usage:** Google Cloud, AWS, etc.
- **Special:** Keep original JSON for tool compatibility, store in secrets manager as well

### Passwords
- **Rotation:** 60 days
- **Format:** High-entropy strings
- **Usage:** Database credentials, admin passwords

### Tokens
- **Rotation:** 30 days
- **Format:** JWT, OAuth tokens, session tokens
- **Usage:** Short-lived authentication

### Zo-Managed Secrets
- **Rotation:** Managed by Zo platform
- **Format:** Environment variables (OPENAI_API_KEY, etc.)
- **Usage:** Read from `os.getenv()` directly
- **Note:** Do NOT duplicate in secrets manager - Zo handles these

---

## Git Protection

**Required in `.gitignore`:**
```
# Secrets Management (P34)
N5/config/secrets.jsonl
N5/config/.secrets.key
N5/config/credentials/
N5/services/*/.env
N5/data/secrets_audit.jsonl
**/tally_api_key.env
```

**Exception:** `.env.template` files are allowed (no actual secrets)

---

## Master Key Backup Procedure

**CRITICAL:** The master key (`/home/workspace/N5/config/.secrets.key`) is required to decrypt all secrets. Loss = permanent data loss.

### Backup Storage

**Primary Backup:**
1. Copy `.secrets.key` to secure password manager (1Password, LastPass, etc.)
2. Label as: "N5 Secrets Master Key - va.zo.computer"
3. Include date created and last verified

**Secondary Backup:**
1. Print key to paper, store in physical safe
2. Or: Store in encrypted USB drive in secure location
3. Label with date and recovery instructions

### Recovery Test

**Quarterly verification (every 90 days):**
```bash
# 1. Backup current key
cp N5/config/.secrets.key N5/config/.secrets.key.backup

# 2. Test recovery from backup
# (Simulate: retrieve from password manager)
echo "[paste key from backup]" > N5/config/.secrets.key.test

# 3. Verify secrets accessible
python3 N5/scripts/n5_secrets.py list

# 4. Restore if test successful
rm N5/config/.secrets.key.test N5/config/.secrets.key.backup
```

### Key Rotation

**If master key compromised:**
1. Generate new master key
2. Decrypt all secrets with old key
3. Re-encrypt with new key
4. Update backups immediately
5. Investigate breach vector

**Script:** `python3 N5/scripts/n5_secrets.py rotate-master-key` (TODO: implement)

---

## Common Patterns

### Pattern 1: Script Needs One Secret
```python
from n5_secrets import SecretsManager

secrets = SecretsManager()
api_key = secrets.get("service_api_key")
```

### Pattern 2: Script Needs Multiple Secrets
```python
secrets = SecretsManager()
config = {
    "n8n_key": secrets.get("n8n_api_key"),
    "openai_key": os.getenv("OPENAI_API_KEY"),  # Zo-managed
}
```

### Pattern 3: Service Account JSON
```python
# For tools requiring file path
google_creds_path = Path.home() / "workspace" / "N5" / "config" / "credentials" / "google_service_account.json"

# For direct usage
secrets = SecretsManager()
google_creds_dict = json.loads(secrets.get("google_service_account"))
```

### Pattern 4: Conditional Secret (dev vs prod)
```python
secrets = SecretsManager()
if is_production:
    api_key = secrets.get("stripe_live_key")
else:
    api_key = secrets.get("stripe_test_key")
```

---

## Anti-Patterns

### ❌ DON'T: Hardcode secrets
```python
API_KEY = "sk_live_abc123..."  # NEVER DO THIS
```

### ❌ DON'T: Store in .env without encryption
```bash
# .env file
API_KEY=secret_value  # Vulnerable to git commits
```

### ❌ DON'T: Pass secrets as command-line args
```bash
./script.py --api-key sk_live_abc123  # Visible in ps, logs
```

### ❌ DON'T: Log secret values
```python
logger.info(f"Using API key: {api_key}")  # Exposes in logs
```

### ✅ DO: Use secrets manager + reference by name
```python
secrets = SecretsManager()
api_key = secrets.get("stripe_api_key")
logger.info("API call successful (key: stripe_api_key)")  # Safe
```

---

## Integration Points

### With P2 (SSOT)
- Secrets manager is THE single source for all credentials
- No duplicates across `.env`, config files, or hardcoded values

### With P5 (Anti-Overwrite)
- Setting existing secret requires `--force` flag
- Rotation creates audit trail of old → new transition

### With P19 (Error Handling)
- Scripts must handle `SecretNotFoundError` gracefully
- Provide helpful error messages with recovery steps

### With P21 (Document Assumptions)
- Document which secrets each script requires
- Include in script docstrings and README files

---

## Migration Checklist

When adding new integration requiring secrets:

- [ ] Add secret to secrets manager with `set` command
- [ ] Set appropriate `rotation_days` for secret type
- [ ] Update script to use `SecretsManager` class
- [ ] Remove any plaintext `.env` or config files
- [ ] Test secret access end-to-end
- [ ] Document secret requirement in script docstring
- [ ] Add to `.gitignore` if new file pattern
- [ ] Verify audit log shows access

---

## Monitoring & Maintenance

### Daily
- Audit log reviewed automatically (anomaly detection TODO)

### Weekly
- Review `secrets_audit.jsonl` for unusual access patterns

### Monthly
- Run `check-rotation` and plan upcoming rotations

### Quarterly
- Test master key backup recovery
- Review all secrets for continued necessity
- Audit third-party service access logs

### Annually
- Consider master key rotation (major operation)
- Review and update rotation policies

---

## Current Secrets Inventory

**As of 2025-10-26:**

| Secret Key | Service | Type | Context | Rotation |
|------------|---------|------|---------|----------|
| n8n_api_key | n8n | api_key | n8n_processor | 90d |
| tally_api_key | tally | api_key | n5_system | 90d |
| zobridge_secret | zobridge | token | zobridge_relay | 30d |
| google_service_account | google_cloud | service_account | n5_system | 180d |

**Zo-Managed (not in secrets manager):**
- `OPENAI_API_KEY` - LLM API access
- `ZO_CONVERSATION_ID` - Conversation context
- `CONVERSATION_WORKSPACE` - Workspace path

---

## References

**Implementation:** `file 'N5/scripts/n5_secrets.py'`  
**Backup Location:** `file 'N5/backups/secrets-migration-20251026/plaintext-credentials-backup.tar.gz'`  
**Git Protection:** `file '.gitignore'` (lines for P34)  
**Audit Log:** `file 'N5/data/secrets_audit.jsonl'`

---

## Questions & Edge Cases

**Q: What if secrets manager script itself has bugs?**  
A: Master key + encrypted secrets stored separately. Manual decryption possible via Python Fernet library directly.

**Q: What if I need to share a secret with external developer?**  
A: Use secure channel (1Password shared vault, encrypted email). Never plaintext. Consider short-lived tokens.

**Q: Service requires .env file format?**  
A: Create `.env.template` with instructions to use secrets manager. Or: generate `.env` dynamically from secrets manager at runtime.

**Q: How to handle secrets in scheduled tasks?**  
A: Scheduled tasks run as same user, have access to secrets manager. No special handling needed.

**Q: What about database connection strings?**  
A: Store full connection string as secret, or store password component only and construct string dynamically.

---

## Version History

- **v1.0** (2025-10-26): Initial principle, consolidated from scattered implementations
- Migration from plaintext to encrypted: 2025-10-26

---

**Status:** ✅ Active, enforced across all N5 systems

*Related: P2 (SSOT), P5 (Anti-Overwrite), P19 (Error Handling), P21 (Document Assumptions)*
