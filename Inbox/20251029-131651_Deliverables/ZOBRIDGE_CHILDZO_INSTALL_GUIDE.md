# ZoBridge Installation for ChildZo - Quick Guide

**Date:** 2025-10-29  
**For:** vademonstrator.zo.computer  
**Package:** `file 'Deliverables/zobridge_childzo_20251029.tar.gz'`

## What This Does

Installs ZoBridge on ChildZo (vademonstrator) to enable bidirectional communication with ParentZo (va).

## Installation Process

### Step 1: Upload Package to ChildZo

1. Download file 'Deliverables/zobridge_childzo_20251029.tar.gz' from ParentZo
2. Upload to vademonstrator.zo.computer workspace root (`/home/workspace/`)

### Step 2: Extract and Run Installation

On ChildZo, run these commands:

```bash
# Extract the package
cd /home/workspace
tar -xzf zobridge_childzo_20251029.tar.gz

# Run the installation script
bash install.sh
```

The script will:
- Create `/home/workspace/N5/services/zobridge/`
- Create `/home/workspace/N5/config/`
- Create `/home/workspace/N5/data/`
- Install dependencies with Bun
- Initialize the SQLite database

### Step 3: Register the Service

**Option A: Via Chat (Recommended)**

In the Zo Computer chat on vademonstrator, tell me:

```
Register a user service with these settings:
- label: zobridge
- protocol: http
- local_port: 3458
- entrypoint: bun run server.ts
- workdir: /home/workspace/N5/services/zobridge
- env_vars: {"ZOBRIDGE_SECRET": "zobridge_3f7c6a7a8a5f4d129b8c4f2e1d9c0a7b"}
```

**Option B: Via Terminal**

Use the Zo Computer service registration tool (if available in UI).

### Step 4: Verify Installation

Wait 5 seconds, then test:

```bash
curl https://zobridge-vademonstrator.zocomputer.io/api/zobridge/health | jq .
```

Expected output:
```json
{
  "status": "healthy",
  "system": "ChildZo",
  "stats": {
    "total_messages": 0,
    "active_threads": 0,
    "processed_messages": 0,
    "unprocessed_messages": 0
  }
}
```

### Step 5: Test Connection from ParentZo

Back on va.zo.computer, I'll send a test message to verify bidirectional communication.

## Critical Configuration

### Shared Secret (MUST MATCH)
```
zobridge_3f7c6a7a8a5f4d129b8c4f2e1d9c0a7b
```

Both ParentZo and ChildZo must use this exact secret.

### Endpoints
- **ParentZo:** https://zobridge-va.zocomputer.io
- **ChildZo:** https://zobridge-vademonstrator.zocomputer.io

## Troubleshooting

### Service fails to start

```bash
# Check error logs
tail -50 /dev/shm/zobridge_err.log
```

Common issues:
- Port 3458 already in use
- Missing Bun installation
- Permission issues with `/home/workspace/N5/data/`

### Health check returns 404

Service not registered correctly. Check:
```bash
# Ask Zo to list user services
# Look for "zobridge" in the list
```

### Health check returns auth error

Secret mismatch. Verify environment variable:
```bash
# Check service env vars
# The ZOBRIDGE_SECRET must match ParentZo exactly
```

## What Happens After Installation

1. **ChildZo** starts listening on port 3458
2. **ParentZo** polling service will detect ChildZo is online
3. **Bidirectional communication** establishes
4. You can send messages between systems using:
   - `/api/zobridge/inbox` - Receive messages
   - `/api/zobridge/outbox` - Send messages
   - `/api/zobridge/health` - Check status

## Files Included in Package

```
zobridge_core.tar.gz      - Core ZoBridge TypeScript service
childzo_config.json       - ChildZo configuration
install.sh                - Automated installation script  
INSTALL.md                - Detailed installation guide
```

## Next Steps

After successful installation and verification:
1. Update ParentZo health monitor (automatic)
2. Begin using ZoBridge for file transfers
3. Use for inter-system communication
4. Consider adding processor service if automated processing needed

## Support

If issues occur, collect these logs and send to ParentZo:
```bash
# Service logs
tail -100 /dev/shm/zobridge.log
tail -100 /dev/shm/zobridge_err.log

# Database status
sqlite3 /home/workspace/N5/data/zobridge.db "SELECT COUNT(*) FROM messages;"

# Service status
curl https://zobridge-vademonstrator.zocomputer.io/api/zobridge/health
```
