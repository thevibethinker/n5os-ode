# N5 Secrets Management Migration Guide

**Created:** 2025-10-26  
**Status:** Implementation Ready  
**Related:** P34 Architectural Principle

---

## Overview

This guide walks through migrating existing scattered credentials to the centralized N5 Secrets Manager.

## Quick Start

```bash
# 1. Test the secrets manager
python3 N5/scripts/n5_secrets.py list

# 2. Add your first secret
python3 N5/scripts/n5_secrets.py set example_key \
  --value "your-secret-value" \
  --type api_key \
  --service example \
  --owner test_script \
  --purpose "Testing secrets manager" \
  --rotation-days 90

# 3. Retrieve the secret
python3 N5/scripts/n5_secrets.py get example_key

# 4. Check in your code
python3 -c "
from n5_secrets import SecretsManager
secrets = SecretsManager()
value = secrets.get('example_key')
print(f'Secret: {value}')
"
```

---

## Current Secrets Audit

### ✅ Found Credentials

#### 1. N8N API Key
- **Current Location:** `N5/services/n8n_processor/.env`
- **Value:** JWT token (eyJhbG...)
- **Used By:** n8n_processor service
- **Purpose:** N8N workflow automation API access

#### 2. Tally API Key
- **Current Location:** `N5/config/tally_api_key.env`
- **Value:** tly-qMW...
- **Used By:** Form sync scripts
- **Purpose:** Tally form data retrieval

#### 3. ZoBridge Secret
- **Current Location:** 
  - `N5/services/zobridge/zobridge.config.json` (hardcoded)
  - Environment variable `ZOBRIDGE_SECRET`
- **Value:** zobridge_3f7c6a7a8a5f4d129b8c4f2e1d9c0a7b
- **Used By:** ZoBridge relay service
- **Purpose:** Inter-Zo authentication

#### 4. Google Service Account
- **Current Location:** `N5/config/credentials/google_service_account.json`
- **Value:** Full service account JSON with private key
- **Used By:** Google Drive sync, Calendar integrations
- **Purpose:** Google API access

#### 5. OpenAI API Key
- **Current Location:** Environment variable (not in files)
- **Referenced In:** `N5/scripts/summarize_segments.py`
- **Purpose:** LLM-based transcript summarization

---

## Migration Steps

### Phase 1: Backup Current State

```bash
# Create backup directory
mkdir -p /home/workspace/N5/backups/secrets-migration-$(date +%Y%m%d)

# Backup all credential files
cp N5/services/n8n_processor/.env N5/backups/secrets-migration-$(date +%Y%m%d)/
cp N5/config/tally_api_key.env N5/backups/secrets-migration-$(date +%Y%m%d)/
cp N5/config/credentials/google_service_account.json N5/backups/secrets-migration-$(date +%Y%m%d)/
cp N5/services/zobridge/zobridge.config.json N5/backups/secrets-migration-$(date +%Y%m%d)/

# Backup master key
cp N5/config/.secrets.key N5/backups/secrets-migration-$(date +%Y%m%d)/

echo "✓ Backups created"
```

### Phase 2: Import Secrets

```bash
# 1. N8N API Key
N8N_KEY=$(grep N8N_API_KEY N5/services/n8n_processor/.env | cut -d= -f2)
python3 N5/scripts/n5_secrets.py set n8n_api_key \
  --value "$N8N_KEY" \
  --type jwt \
  --service n8n \
  --owner n8n_processor \
  --purpose "N8N workflow API access" \
  --rotation-days 90

# 2. Tally API Key
TALLY_KEY=$(grep TALLY_API_KEY N5/config/tally_api_key.env | cut -d= -f2)
python3 N5/scripts/n5_secrets.py set tally_api_key \
  --value "$TALLY_KEY" \
  --type api_key \
  --service tally \
  --owner form_sync \
  --purpose "Tally form data retrieval" \
  --rotation-days 180

# 3. ZoBridge Secret
ZOBRIDGE_SECRET=$(jq -r '.secret' N5/services/zobridge/zobridge.config.json)
python3 N5/scripts/n5_secrets.py set zobridge_secret \
  --value "$ZOBRIDGE_SECRET" \
  --type token \
  --service zobridge \
  --owner zobridge_relay \
  --purpose "Inter-Zo authentication" \
  --rotation-days 180

# 4. Google Service Account (base64 encode entire JSON)
GOOGLE_SA=$(base64 -w0 < N5/config/credentials/google_service_account.json)
python3 N5/scripts/n5_secrets.py set google_service_account \
  --value "$GOOGLE_SA" \
  --type service_account \
  --service google \
  --owner drive_sync \
  --purpose "Google Drive and Calendar API access" \
  --rotation-days 365

# 5. OpenAI API Key (if exists in environment)
if [ -n "$OPENAI_API_KEY" ]; then
  python3 N5/scripts/n5_secrets.py set openai_api_key \
    --value "$OPENAI_API_KEY" \
    --type api_key \
    --service openai \
    --owner summarize_segments \
    --purpose "LLM transcript summarization" \
    --rotation-days 90
fi

echo "✓ All secrets imported"
```

### Phase 3: Update Consumers

#### 3a. Update n8n_processor

**Create:** `N5/services/n8n_processor/load_secrets.py`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace" / "N5" / "scripts"))
from n5_secrets import SecretsManager

def get_n8n_config():
    secrets = SecretsManager()
    return {
        "api_key": secrets.get("n8n_api_key"),
        "url": "https://n8n-va.zocomputer.io",
        "zo_api_url": "http://localhost:8770"
    }
```

**Update:** n8n_processor to use load_secrets.py instead of .env

#### 3b. Update summarize_segments.py

**File:** `N5/scripts/summarize_segments.py`

```python
# Replace this line:
# "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",

# With:
from n5_secrets import SecretsManager
secrets = SecretsManager()
headers = {
    "Authorization": f"Bearer {secrets.get('openai_api_key')}",
    # ...
}
```

#### 3c. Update ZoBridge relay.ts

**File:** `N5/services/zobridge/relay.ts`

```typescript
// Replace getSecret() function:
import { execSync } from 'child_process';

function getSecret(): string {
  try {
    const secret = execSync(
      'python3 /home/workspace/N5/scripts/n5_secrets.py get zobridge_secret',
      { encoding: 'utf-8' }
    ).trim();
    return secret;
  } catch (e) {
    console.error("Failed to load zobridge_secret:", e);
    return "";
  }
}
```

#### 3d. Google Service Account Usage

```python
import base64
import json
from n5_secrets import SecretsManager

secrets = SecretsManager()
encoded = secrets.get("google_service_account")
creds = json.loads(base64.b64decode(encoded))

# Now use creds dict as normal service account
```

### Phase 4: Remove Old Files (AFTER Testing!)

```bash
# Only run after confirming everything works!

# Mark old files for deletion (don't actually delete yet)
mv N5/services/n8n_processor/.env N5/services/n8n_processor/.env.old
mv N5/config/tally_api_key.env N5/config/tally_api_key.env.old
mv N5/services/zobridge/zobridge.config.json N5/services/zobridge/zobridge.config.json.old

# Remove secret from zobridge config (keep other config)
jq 'del(.secret)' N5/services/zobridge/zobridge.config.json.old > N5/services/zobridge/zobridge.config.json

echo "⚠️  Old credential files renamed to .old - delete after 1 week of successful operation"
```

### Phase 5: Verify Git Safety

```bash
# Confirm gitignore updated
cat .gitignore | grep -A8 "Secrets Management"

# Check nothing sensitive staged
git status

# Verify secrets.jsonl is encrypted
file N5/config/secrets.jsonl

echo "✓ Git safety verified"
```

---

## Testing Checklist

After migration, test each integration:

### N8N Integration
```bash
# Test n8n_processor can access secret
cd N5/services/n8n_processor
python3 -c "from load_secrets import get_n8n_config; print(get_n8n_config())"
```

### Tally Integration
```bash
# Test tally secret retrieval
python3 N5/scripts/n5_secrets.py get tally_api_key
```

### ZoBridge
```bash
# Test relay.ts can load secret
cd N5/services/zobridge
# Check logs after restart
```

### Google Service Account
```bash
# Test service account decoding
python3 -c "
import base64, json
from n5_secrets import SecretsManager
secrets = SecretsManager()
encoded = secrets.get('google_service_account')
creds = json.loads(base64.b64decode(encoded))
print(f'✓ Project: {creds.get(\"project_id\", \"unknown\")}')
"
```

### OpenAI API
```bash
# Test OpenAI key (if set)
python3 -c "
from n5_secrets import SecretsManager
secrets = SecretsManager()
key = secrets.get('openai_api_key')
print(f'✓ Key length: {len(key)}')
"
```

---

## Rotation Schedule

Set up rotation monitoring:

```bash
# Check what's due for rotation
python3 N5/scripts/n5_secrets.py check-rotation --warning-days 14

# Create scheduled task (weekly check)
# Add to N5/config/scheduled_tasks.jsonl or use Zo's scheduling
```

Suggested rotation schedule:
- **JWT tokens (N8N):** 90 days
- **API keys (Tally, OpenAI):** 90-180 days
- **Service accounts (Google):** 365 days
- **Internal tokens (ZoBridge):** 180 days

---

## Troubleshooting

### "Secret not found" error
```bash
# List all secrets
python3 N5/scripts/n5_secrets.py list

# Check audit log
tail -20 N5/data/secrets_audit.jsonl
```

### "Decryption failed" error
```bash
# Verify master key exists
ls -la N5/config/.secrets.key

# Check permissions
chmod 600 N5/config/.secrets.key

# Verify environment variable (if set)
echo $N5_SECRETS_KEY
```

### Master key lost
```bash
# If you lose the master key, secrets are unrecoverable!
# This is why backups are critical

# Restore from backup
cp N5/backups/secrets-migration-YYYYMMDD/.secrets.key N5/config/
chmod 600 N5/config/.secrets.key
```

---

## Post-Migration

### 1. Backup Master Key
```bash
# Copy master key to password manager or secure location
cat N5/config/.secrets.key

# Store securely - this is your ONLY way to decrypt secrets!
```

### 2. Document New Secrets
When adding new API keys in the future:

```bash
python3 N5/scripts/n5_secrets.py set new_service_key \
  --value "..." \
  --type api_key \
  --service service_name \
  --owner script_or_service \
  --purpose "Clear description" \
  --rotation-days 90
```

### 3. Update Scripts Template
New scripts should use:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace" / "N5" / "scripts"))

from n5_secrets import SecretsManager

def main():
    secrets = SecretsManager()
    api_key = secrets.get("service_api_key")
    # Use api_key...
```

---

## Security Best Practices

1. **Never commit secrets.jsonl or .secrets.key** (gitignored)
2. **Backup master key separately** from secrets file
3. **Rotate secrets regularly** according to schedule
4. **Review audit log** periodically: `N5/data/secrets_audit.jsonl`
5. **Test after rotation** to ensure services still work
6. **Delete old .env files** after successful migration (1+ week)

---

## References

- **Implementation:** `file 'N5/scripts/n5_secrets.py'`
- **Principle:** `file 'Knowledge/architectural/principles/P34-secrets-management.md'`
- **Audit:** `file '/home/.z/workspaces/con_Aito7jbiU6WDT1wQ/secrets_audit.md'`
- **Design:** `file '/home/.z/workspaces/con_Aito7jbiU6WDT1wQ/secrets_manager_design.md'`

---

**Next Steps:**
1. Review this guide
2. Run Phase 1 (Backup)
3. Run Phase 2 (Import)
4. Test each integration
5. Update scripts (Phase 3)
6. Verify git safety
7. Remove old files after 1 week
