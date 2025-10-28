# N5 Credential Management Audit
**Date**: 2025-10-28  
**Purpose**: Establish baseline protocol for credential management

---

## Current State

### Existing Credential Storage
1. **`N5/config/slack_credentials.json`** ❌ Filesystem storage
   - Slack bot token
   - Slack user token
   - Slack webhook URL
   
2. **`N5/config/credentials/google_service_account.json`** ❌ Filesystem storage
   - Google service account credentials

### Zo Environment Variables (Discovered)
- `ZO_USER` - User handle
- `ZO_CLIENT_IDENTITY_TOKEN` - Zo identity token

---

## Target State: Zero Filesystem Credentials

**Principle**: All secrets in Zo's secrets manager, accessed via environment variables

**Benefits**:
- ✅ Centralized management
- ✅ Encrypted at rest
- ✅ No accidental git commits
- ✅ Easy rotation
- ✅ Audit trail
- ✅ Follows industry best practices

---

## Proposed Protocol

### 1. Naming Convention
```
<SERVICE>_<CREDENTIAL_TYPE>_<ENVIRONMENT>

Examples:
- SLACK_BOT_TOKEN
- SLACK_WEBHOOK_URL
- GOOGLE_SERVICE_ACCOUNT_JSON
- GITHUB_API_TOKEN
```

### 2. Access Pattern (Python)
```python
import os

def get_secret(key: str, required: bool = True) -> str:
    """Get secret from environment variable."""
    value = os.getenv(key)
    if required and not value:
        raise ValueError(f"Required secret {key} not found")
    return value
```

### 3. Migration Steps
1. Add secrets to Zo settings → Secrets
2. Update scripts to read from env vars
3. Delete filesystem credential files
4. Add to `.gitignore` (prevent future filesystem storage)
5. Document in N5/docs

---

## Implementation Plan

### Phase 1: Create Standard Library (5 min)
- Create `N5/lib/secrets.py`
- Standard secret access functions
- Error handling and validation

### Phase 2: Migrate Existing Credentials (10 min)
- Add Slack credentials to Zo secrets
- Add Google credentials to Zo secrets
- Update slack_send.py and slack_read.py
- Test functionality

### Phase 3: Clean Up (5 min)
- Delete JSON credential files
- Update .gitignore
- Create protection rules

### Phase 4: Documentation (5 min)
- Update N5/docs with protocol
- Add to architectural principles
- Create quick reference

---

## Files to Update

1. `N5/scripts/slack_send.py` - Use secrets lib
2. `N5/scripts/slack_read.py` - Use secrets lib
3. Any scripts using `google_service_account.json`
4. `.gitignore` - Block credential files
5. `N5/docs/credential-management.md` - New protocol doc

---

## Next Actions

**For V:**
1. Go to https://va.zo.computer/settings
2. Find "Secrets" or "Environment Variables" section
3. Add these secrets:
   ```
   SLACK_BOT_TOKEN=xoxb-5255246858917-9782841117974-mZew0VoLxmVwheIMZK4cbZAd
   SLACK_USER_TOKEN=xoxp-5255246858917-5258199128962-9769370390487-c369ef6f964a8ac0
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/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
   ```
4. Confirm they're saved

**For AI:**
1. Create secrets management library
2. Refactor all credential access
3. Clean up filesystem
4. Document protocol
