# Mobius Maneuver: Bootstrap Guidance System

**Purpose:** Secure, unidirectional communication from mature N5 → bootstrap N5  
**Date:** 2025-10-18  
**Status:** Active

---

## What is the Mobius Maneuver?

A "Mobius maneuver" where the mature N5 system guides its own bootstrap in a fresh environment:

- **Source (this workspace):** Provides read-only guidance
- **Target (new workspace):** Queries for help, receives instructions
- **Security:** Unidirectional - new system CANNOT modify source
- **Purpose:** Expert guidance during bootstrap process

---

## Architecture

```
┌─────────────────────────────────────┐
│  SOURCE: Mature N5 (va.zo.computer) │
│  ┌───────────────────────────────┐  │
│  │ Bootstrap Advisor Server      │  │
│  │ - Read-only HTTP endpoints    │  │
│  │ - Diagnostic guidance         │  │
│  │ - Troubleshooting help        │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │ HTTPS (read-only)
               ▼
┌─────────────────────────────────────┐
│  TARGET: Bootstrap N5 (new.zo)      │
│  ┌───────────────────────────────┐  │
│  │ Bootstrap Client              │  │
│  │ - Sends queries               │  │
│  │ - Receives guidance           │  │
│  │ - Implements locally          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Security:** Source has NO ability to write to target. All changes implemented by target based on advice.

---

## Source Setup (Already Complete)

### 1. Advisor Server Running

**Service:** `n5-bootstrap-advisor`  
**URL:** `https://n5-bootstrap-advisor-va.zocomputer.io`  
**Port:** 8765  
**Status:** ✅ Active

### 2. Available Endpoints

#### GET Endpoints (Read-only)
- `/health` - Health check
- `/bootstrap/principles` - Architectural principles
- `/bootstrap/structure` - Directory structure
- `/bootstrap/scripts` - Script guidance
- `/bootstrap/config` - Config guidance
- `/bootstrap/checklist` - Complete checklist
- `/bootstrap/help/<topic>` - Contextual help

#### POST Endpoints (Query)
- `/bootstrap/query` - Structured queries
  - Types: `error`, `next_step`, `validate`, `troubleshoot`

---

## Target Setup (In New Workspace)

### 1. Extract Bootstrap Package

```bash
cd /home/workspace
tar -xzf N5_Bootstrap_Package.tar.gz
cd N5_Bootstrap_Package
```

### 2. Set Up Client

The client is included in the package:

```bash
# Make executable
chmod +x scripts/bootstrap_client.py

# Test connection
python3 scripts/bootstrap_client.py --health
```

Expected output:
```json
{
  "status": "healthy",
  "service": "N5 Bootstrap Advisor",
  "version": "1.0.0",
  "mode": "read-only",
  "message": "Mobius maneuver active"
}
```

### 3. Interactive Mode

```bash
python3 scripts/bootstrap_client.py --interactive
```

Commands available:
- `health` - Check connection
- `checklist` - Get bootstrap checklist
- `next` - Get next step
- `error <msg>` - Diagnose error
- `help <topic>` - Get contextual help
- `structure` - Show directory structure
- `troubleshoot <issue>` - Troubleshoot

---

## Common Usage Patterns

### Pattern 1: Following the Checklist

```bash
# Get complete checklist
python3 scripts/bootstrap_client.py --checklist

# Follow each phase
# After completing phase, get next step
python3 scripts/bootstrap_client.py --next-step 1
python3 scripts/bootstrap_client.py --next-step 2
# etc.
```

### Pattern 2: Error Diagnosis

```bash
# When you hit an error
python3 scripts/bootstrap_client.py --error "FileNotFoundError: No such file: N5/config/commands.jsonl"

# Or in interactive mode
> error FileNotFoundError: No such file
```

### Pattern 3: Contextual Help

```bash
# Get help on specific topics
python3 scripts/bootstrap_client.py --help-topic session_state
python3 scripts/bootstrap_client.py --help-topic commands
python3 scripts/bootstrap_client.py --help-topic conditional_rules
```

### Pattern 4: Troubleshooting Issues

```bash
# In interactive mode
> troubleshoot conditional_rules
> troubleshoot commands_not_found
> troubleshoot scripts_failing
```

---

## Bootstrap Workflow with Mobius

### Phase 1: Initial Setup

```bash
# 1. Check advisor connection
python3 scripts/bootstrap_client.py --health

# 2. Get directory structure
python3 scripts/bootstrap_client.py --interactive
> structure

# 3. Create directories based on advice
mkdir -p N5/{scripts,config,schemas,commands,prefs}
mkdir -p Knowledge Lists Documents Records Exports

# 4. Verify
python3 scripts/bootstrap_client.py --next-step 0
```

### Phase 2: Copy Files

```bash
# Get guidance
> scripts
> config

# Follow instructions to copy files
# Then validate
> next
```

### Phase 3: Setup Rules

```bash
# Get help on conditional rules
> help conditional_rules

# Follow instructions to add to Zo settings
# Test by asking Zo to load a file
```

### Phase 4: Test & Troubleshoot

```bash
# If error occurs
> error <your error message>

# Get diagnostic and solutions
# Implement solutions
# Continue
```

---

## Query Types Explained

### Error Diagnosis
```json
{
  "type": "error",
  "context": {
    "error": "FileNotFoundError: ...",
    "phase": "scripts"
  }
}
```

Returns diagnosis and solutions.

### Next Step
```json
{
  "type": "next_step",
  "context": {
    "phase": 2,
    "completed": ["structure", "scripts"]
  }
}
```

Returns next action with verification command.

### Validate Setup
```json
{
  "type": "validate",
  "context": {}
}
```

Returns validation checklist.

### Troubleshoot Issue
```json
{
  "type": "troubleshoot",
  "context": {
    "issue": "conditional_rules"
  }
}
```

Returns troubleshooting guide.

---

## Security Model

### Source Protection
- ✅ Read-only endpoints only
- ✅ No POST that modifies source
- ✅ No file write capabilities
- ✅ Stateless (no session storage)
- ✅ Public endpoints (no auth needed)

### Target Safety
- ✅ Target implements advice locally
- ✅ Target controls all changes
- ✅ Source cannot push changes
- ✅ Target can ignore advice

**Result:** Safe, helpful guidance without risk.

---

## Troubleshooting the Mobius Maneuver

### Client Can't Connect

**Problem:** `Connection refused` or timeout

**Solutions:**
1. Check URL is correct: `https://n5-bootstrap-advisor-va.zocomputer.io`
2. Test in browser first
3. Check internet connection
4. Verify service is running (on source)

### No Response

**Problem:** Client hangs or no data returned

**Solutions:**
1. Check `/health` endpoint first
2. Increase timeout (edit script)
3. Check for firewall issues
4. Try different endpoint

### Advice Doesn't Work

**Problem:** Following advice but still failing

**Solutions:**
1. Double-check you implemented exactly as advised
2. Query again with more context
3. Use interactive mode to debug step-by-step
4. Share full error message for better diagnosis

---

## For the Target Zo AI

When you're in the new workspace being bootstrapped:

1. **Use the client frequently** - It's your lifeline to expert guidance
2. **Start with health check** - Verify connection first
3. **Follow checklist sequentially** - Don't skip phases
4. **Query on ANY error** - The advisor knows common issues
5. **Use interactive mode** - Easier than CLI flags
6. **Ask for help topics** - Contextual help is detailed
7. **Validate after each phase** - Catch issues early

**Key insight:** You're not alone. The mature system is guiding you through its own rebuild.

---

## Service Management (Source)

### Check Status
```bash
# View service logs
cat /dev/shm/n5-bootstrap-advisor.log

# List services
python3 -c "from list_user_services import *; list_user_services()"
```

### Restart Service
```bash
# If needed (already running)
# Service auto-restarts on failure
```

### Stop Service
```bash
# Only if you want to disable
# (Not recommended during active bootstrap)
```

---

## Extending the Advisor

The advisor server can be extended with:

1. **More endpoints** - Add to handler
2. **More diagnoses** - Add to `common_errors`
3. **More help topics** - Add to `help_topics`
4. **File serving** - Serve specific files on request
5. **State tracking** - Track bootstrap progress (optional)

---

## Success Criteria

Bootstrap is complete when target can:

1. ✅ Run `/init-state-session` successfully
2. ✅ Add knowledge: `/knowledge-add`
3. ✅ Create lists: `/lists-add`
4. ✅ Process commands without advisor
5. ✅ All core scripts executable
6. ✅ Conditional rules working
7. ✅ No advisor queries needed for basic ops

**At that point:** The Mobius maneuver is complete. Target is self-sufficient.

---

**The mature system teaching itself to be reborn.** 🚀

**Active now | v1.0.0 | 2025-10-18**
