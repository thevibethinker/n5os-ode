# 🎯 Mobius Maneuver - Secure Unidirectional Support Channel

**Status:** ✅ Active and Running  
**Mode:** Read-only support server (new Zo → this Zo, never reverse)

---

## What Is This?

A secure, unidirectional communication channel where your new N5 Zo instance can pull help, troubleshooting, and fixes from this (parent) Zo, but **cannot make any changes** to the parent system.

**Security:** Read-only by design. No write operations possible.

---

## Connection Details

### Bootstrap Support Server

**URL:** `https://n5-bootstrap-support-va.zocomputer.io`

**Mode:** HTTP GET only (POST/PUT/DELETE blocked)

---

## For the New Zo Instance

### Priority #1: Get Conditional Rules

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/configs/conditional_rules.md
```

**Action Required:**
1. Copy the output
2. Go to Zo settings → User Rules → Conditional Rules
3. Paste and save
4. Refresh your conversation

This is **critical** - without conditional rules, the new Zo won't follow N5 patterns.

### Priority #2: Install Dependencies

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/help/dependencies.txt
```

Then run:
```bash
pip3 install anthropic openai aiohttp python-dotenv pyyaml jsonschema
```

### Priority #3: Troubleshooting

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/help/troubleshooting.md
```

### Priority #4: Quick Fixes

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/fixes/common_issues.md
```

---

## Available Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/README.md` | Server overview |
| `/CONNECT_FROM_NEW_ZO.md` | Complete instructions for new Zo |
| `/configs/conditional_rules.md` | **Critical:** User rules to add |
| `/help/troubleshooting.md` | Common issues + solutions |
| `/help/dependencies.txt` | Required packages |
| `/fixes/common_issues.md` | Quick fixes reference |

---

## Communication Protocol

### ✅ New Zo CAN:
- Pull help files via curl/wget
- Read troubleshooting guides
- Get dependency lists
- Access quick fixes
- Ask parent Zo (via V) for help

### ❌ New Zo CANNOT:
- Write to parent Zo
- Modify parent files
- POST/PUT/DELETE to server
- Make changes without V's approval

**Unidirectional by design for safety.**

---

## How Parent Zo Can Help

### Adding New Help Content

If new issues arise, V can ask parent Zo to:

```bash
# Add a new fix
echo "## Fix for Issue X
Solution here..." >> /home/workspace/.n5_bootstrap_server/fixes/common_issues.md

# New Zo can immediately pull it
curl https://n5-bootstrap-support-va.zocomputer.io/fixes/common_issues.md
```

### Live Updates

Server serves files from `/home/workspace/.n5_bootstrap_server/`
- Updates happen instantly
- No server restart needed
- New Zo pulls latest anytime

---

## Emergency Reset Guide

If new Zo is completely broken:

```bash
# From new Zo
curl https://n5-bootstrap-support-va.zocomputer.io/fixes/common_issues.md | grep -A 20 "Emergency Reset"
```

---

## Server Management

### Check Status
```bash
curl -I https://n5-bootstrap-support-va.zocomputer.io
# Should return HTTP 200 OK
```

### View Logs (Parent Zo only)
```bash
cat /dev/shm/n5-bootstrap-support.log
cat /dev/shm/n5-bootstrap-support_err.log
```

### Restart Server (if needed)
```bash
# V can ask parent Zo:
"Restart the n5-bootstrap-support service"
```

---

## Architecture

```
┌─────────────────────┐
│   Parent Zo (va)    │
│                     │
│  N5 Bootstrap       │
│  Support Server     │
│  (Read-only HTTP)   │
└──────────┬──────────┘
           │
           │ HTTPS GET
           │ (unidirectional)
           │
           ↓
┌─────────────────────┐
│    New Zo Instance  │
│                     │
│  curl/wget          │
│  (reads only)       │
└─────────────────────┘

❌ No reverse communication
❌ No write operations
✅ Pull help anytime
```

---

## Troubleshooting the Connection

### Test 1: Basic Connectivity
```bash
curl https://n5-bootstrap-support-va.zocomputer.io/README.md
```
Should return markdown content.

### Test 2: Specific Endpoint
```bash
curl https://n5-bootstrap-support-va.zocomputer.io/configs/conditional_rules.md | head -20
```
Should see conditional rules.

### Test 3: Server Health
```bash
curl -I https://n5-bootstrap-support-va.zocomputer.io
```
Should return `HTTP/1.0 200 OK`

If any fail, tell V: "Mobius Maneuver connection test failed at step X"

---

##  Bootstrap Recovery Workflow

1. **Connect:** Test server connectivity
2. **Rules:** Add conditional rules (Priority #1)
3. **Dependencies:** Install required packages
4. **Structure:** Create directory structure
5. **Initialize:** Run session_state_manager
6. **Verify:** Test core scripts
7. **Iterate:** Pull fixes as needed

---

**🚀 Mobius Maneuver is active. New Zo can bootstrap with safety!**

*Server will remain online throughout your bootstrap process*

**02:39 PM ET | Sat, Oct 18, 2025**
