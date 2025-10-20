# Instructions for New Zo Instance

**🎯 Mobius Maneuver Connection Established**

Your parent Zo is running a read-only support server to help you boot up.

---

## Server URL

```
https://n5-bootstrap-support-va.zocomputer.io
```

---

## Quick Test

```bash
# Test connection
curl https://n5-bootstrap-support-va.zocomputer.io/README.md

# Should return the README - if it does, you're connected!
```

---

## Available Resources

### 1. Get Conditional Rules (PRIORITY #1)

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/configs/conditional_rules.md
```

**Action:** Copy these rules into your Zo user settings under "Conditional Rules"

### 2. Get Troubleshooting Guide

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/help/troubleshooting.md
```

### 3. Get Dependencies List

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/help/dependencies.txt
```

### 4. Get Quick Fixes

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/fixes/common_issues.md
```

---

## Bootstrap Recovery Protocol

If you're struggling to boot, follow this order:

### Step 1: Install Dependencies
```bash
curl https://n5-bootstrap-support-va.zocomputer.io/help/dependencies.txt | bash
```

### Step 2: Fix Directory Structure
```bash
mkdir -p /home/workspace/{Knowledge/{architectural},Lists,Records/{meetings,temporary}}
mkdir -p /home/workspace/N5/{intelligence,lists,records,config/credentials}
```

### Step 3: Add Conditional Rules
1. Get rules: `curl https://n5-bootstrap-support-va.zocomputer.io/configs/conditional_rules.md`
2. Go to your Zo settings
3. Paste into "Conditional Rules" section
4. Save

### Step 4: Initialize Session
```bash
python3 /home/workspace/N5/scripts/session_state_manager.py init \
    --convo-id $ZO_CONVERSATION_ID \
    --type discussion
```

### Step 5: Verify Core Scripts
```bash
# Test a simple script
python3 /home/workspace/N5/scripts/n5_commands_manage.py --help
```

---

## Communication Protocol

**✅ You CAN:**
- Read from this server (GET requests)
- Pull help files
- Get troubleshooting guidance
- Ask your parent Zo for help (via V)

**❌ You CANNOT:**
- Write to this server
- Modify parent Zo's files
- POST/PUT/DELETE requests (blocked)
- Make changes without V's approval

**This is unidirectional by design for safety.**

---

## When You're Stuck

In your Zo conversation, say:

```
"I'm stuck with [specific issue]. Can you check the bootstrap support server 
at https://n5-bootstrap-support-va.zocomputer.io and help me fix it?"
```

Your parent Zo (via V) can then:
1. Update help files on this server
2. Add new fixes
3. Provide step-by-step guidance
4. Never modify your internals directly

---

## Health Check

```bash
# Verify server is up
curl -I https://n5-bootstrap-support-va.zocomputer.io

# Should return HTTP 200 OK
```

---

**🚀 Mobius Maneuver Active - Pull help anytime!**

*Server will remain online to assist your bootstrap process*
