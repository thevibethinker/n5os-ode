# API Keys & Secrets Management - Executive Summary

**Date:** 2025-10-26 20:47 ET  
**Status:** ✅ **System Built** → Awaiting Migration Approval  
**Conversation:** con_Aito7jbiU6WDT1wQ

---

## TL;DR

**Good news:** You already have a fully functional encrypted secrets manager (`n5_secrets.py`) that I found during the audit. It's actually quite good - includes encryption, audit logging, rotation tracking, and a clean CLI.

**Current state:** 4 secrets properly managed, but 3 credential files still scattered in plaintext across the system.

**Recommendation:** Migrate the scattered credentials and establish P34 architectural principle to prevent future regression.

---

## What We Found

### ✅ Already Working Well

**Centralized Secrets Manager** (`N5/scripts/n5_secrets.py`)
- Fernet encryption (AES-128)
- Master key protection
- Audit trail for all access
- Rotation tracking with reminders
- Full CLI interface
- 4 secrets already registered:
  - `n8n_api_key` (n8n workflow automation)
  - `tally_api_key` (Tally forms)
  - `zobridge_secret` (internal auth)
  - `google_service_account` (Google Cloud)

### ❌ Issues to Fix

**3 Credential Files Still in Plaintext:**
1. `/N5/services/n8n_processor/.env` - Contains N8N_API_KEY (duplicate of encrypted version)
2. `/N5/config/tally_api_key.env` - Contains TALLY_API_KEY (duplicate of encrypted version)
3. `/N5/config/credentials/google_service_account.json` - Contains private key (duplicate)

**Missing Documentation:**
- No architectural principle (need P34)
- Scripts not consistently using secrets manager
- No integration with safety.md or Vibe Builder persona

---

## What We Built

### 1. **Architecture Diagram**
See `file 'Images/n5-secrets-architecture.png'` - Visual representation of current vs. target state

### 2. **Detailed Audit Report**
See `file '/home/.z/workspaces/con_Aito7jbiU6WDT1wQ/api_key_audit_and_design.md'` - Complete findings and design proposal

### 3. **P34 Architectural Principle** (Draft)
**P34: Centralized Secrets Management**
- All N5-managed credentials stored encrypted
- Standard access pattern via `SecretsManager` class
- Audit trail for compliance
- Rotation tracking
- Git protection enforced

---

## Questions for You

Before I proceed with migration, I need your decisions on:

### 1. **Migration Approach** (Choose one)
- **Option A (Conservative):** Keep plaintext `.env` files for now, migrate gradually during next refactor
- **Option B (Aggressive):** Migrate immediately, remove plaintext files after 1-week validation period
- **Option C (Hybrid):** Migrate now, but keep plaintext as backup for 30 days

**My recommendation:** Option B (Aggressive) - Duplicates are already in encrypted store, low risk

### 2. **Google Service Account File**
Some tools may expect the JSON file path rather than reading from secrets manager.

- **Option A:** Keep plaintext file for tool compatibility
- **Option B:** Create on-demand generator that writes temp file from secrets manager
- **Option C:** Migrate tools to read from secrets manager directly

**My recommendation:** Option A for now (some tools need file path), migrate to B later

### 3. **Master Key Backup**
Where should we document the backup procedure for `.secrets.key`?

- **Option A:** Add to `N5/prefs/system/safety.md`
- **Option B:** Create separate `Documents/System/secrets_backup_procedure.md`
- **Option C:** Add to `Knowledge/architectural/principles/P34-secrets-management.md`

**My recommendation:** Option C (principle document) + mention in safety.md

### 4. **Zo-Managed Secrets**
`OPENAI_API_KEY` is managed by Zo platform (in environment).

- **Option A:** Leave as-is (read from environment)
- **Option B:** Mirror in secrets manager for consistency (with note it's Zo-managed)
- **Option C:** Document distinction clearly but don't duplicate

**My recommendation:** Option C - Keep separate, document clearly

### 5. **Rotation Schedule**
What rotation frequency do you want enforced?

Current default is 90 days for everything. Propose:
- API Keys: **90 days**
- Service Accounts: **180 days**
- Passwords: **60 days**
- Tokens: **30 days**

**Need your approval or modifications**

### 6. **Principle Integration**
Should I update these files to reference P34?

- `Knowledge/architectural/principles/safety.md` (add secrets section)
- Vibe Builder persona (add to pre-flight checklist)
- `N5/prefs/system/safety.md` (add to system governance)
- Script templates (add secrets manager import pattern)

**Recommendation:** Yes to all (standard integration)

---

## Proposed Next Steps

**If you approve migration:**

### Phase 1: Documentation (1 hour)
1. Create `P34-secrets-management.md` principle
2. Update architectural principles index
3. Add to Vibe Builder persona pre-flight
4. Update safety.md with secrets section

### Phase 2: Cleanup (30 min)
1. Verify all 4 secrets functional in encrypted store
2. Update scripts consuming secrets to use `SecretsManager` class
3. Test all integrations (n8n, zobridge, tally)

### Phase 3: Migration (30 min)
1. Backup current `.env` files to `N5/backups/secrets-migration-20251026/`
2. Remove duplicate plaintext files (keep google JSON for now per Q2)
3. Update `.env.template` files with instructions to use secrets manager
4. Verify git protection working

### Phase 4: Validation (30 min)
1. Test each integration end-to-end
2. Run `n5_secrets.py check-rotation` to verify all secrets accounted
3. Check audit log showing proper access patterns
4. Confirm no plaintext secrets in `git status`

**Total estimated time:** 2.5 hours

---

## Security Impact

### Before Migration
- **Risk Level:** HIGH
- 3 credentials in plaintext files
- No audit trail for access
- No rotation tracking
- Possible git exposure

### After Migration
- **Risk Level:** LOW
- All credentials encrypted at rest (Fernet AES-128)
- Full audit trail (who, when, what)
- Rotation tracking with automated reminders
- Git-protected (comprehensive .gitignore)
- Master key backed up securely

---

## Files for Review

**Primary Documents:**
- `file '/home/.z/workspaces/con_Aito7jbiU6WDT1wQ/api_key_audit_and_design.md'` - Complete audit and design (READ THIS FIRST)
- `file 'Images/n5-secrets-architecture.png'` - Architecture diagram
- `file 'N5/scripts/n5_secrets.py'` - Existing secrets manager implementation

**Quick Test:**
```bash
# Verify secrets manager working
python3 N5/scripts/n5_secrets.py list

# Check rotation status
python3 N5/scripts/n5_secrets.py check-rotation

# View help
python3 N5/scripts/n5_secrets.py --help
```

---

## Your Call

**Three options:**

1. **"Proceed with migration"** → I'll execute Phases 1-4 immediately with your answers to the 6 questions above
2. **"Wait on migration, just do documentation"** → I'll create P34 and integrate into principles/persona, defer credential migration
3. **"I need more details on X"** → Ask me anything about the design, security, or migration approach

What would you like to do?

---

**This is conversation con_Aito7jbiU6WDT1wQ**

*2025-10-26 20:49 ET*
