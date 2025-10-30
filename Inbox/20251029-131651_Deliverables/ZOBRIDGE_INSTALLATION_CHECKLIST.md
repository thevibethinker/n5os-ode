# ZoBridge ChildZo Installation Checklist

**Date:** 2025-10-29  
**From:** ParentZo (va.zo.computer)  
**To:** ChildZo (vademonstrator.zo.computer)

## Pre-Installation

- [ ] Download file 'Deliverables/zobridge_childzo_20251029.tar.gz' from ParentZo
- [ ] Verify file size: ~8.4KB
- [ ] Have access to vademonstrator.zo.computer

## Installation Steps

### On ChildZo (vademonstrator.zo.computer)

- [ ] Upload `zobridge_childzo_20251029.tar.gz` to `/home/workspace/`
- [ ] Extract: `tar -xzf zobridge_childzo_20251029.tar.gz`
- [ ] Run installer: `bash install.sh`
- [ ] Verify no errors during installation

### Service Registration

- [ ] Tell ChildZo Zo to register service with:
  - label: `zobridge`
  - protocol: `http`
  - local_port: `3458`
  - entrypoint: `bun run server.ts`
  - workdir: `/home/workspace/N5/services/zobridge`
  - env_vars: `{"ZOBRIDGE_SECRET": "zobridge_3f7c6a7a8a5f4d129b8c4f2e1d9c0a7b"}`

- [ ] Wait 5 seconds for service to start

### Verification

- [ ] Health check returns 200: 
  ```bash
  curl https://zobridge-vademonstrator.zocomputer.io/api/zobridge/health
  ```

- [ ] Response shows `"system": "ChildZo"`
- [ ] Response shows `"status": "healthy"`

### On ParentZo (va.zo.computer)

- [ ] Notify me that ChildZo is installed and healthy
- [ ] I'll send test message to verify bidirectional communication
- [ ] Confirm test message received on both ends

## Success Criteria

✅ **Installation Complete When:**

1. ChildZo health endpoint responds with "healthy"
2. ParentZo can send message to ChildZo
3. ChildZo can send message to ParentZo
4. Both systems show matching message counts
5. Health monitor shows 0 consecutive failures

## Post-Installation

- [ ] Document ChildZo public endpoint: `https://zobridge-vademonstrator.zocomputer.io`
- [ ] Test file transfer capability
- [ ] Monitor logs for 24 hours to ensure stability

## Rollback Plan (If Needed)

If installation fails:

```bash
# Stop and remove service (via Zo chat)
# "Delete user service: zobridge"

# Clean up files
rm -rf /home/workspace/N5/services/zobridge
rm /home/workspace/N5/config/zobridge.config.json
rm /home/workspace/N5/data/zobridge.db
```

## Quick Reference

**Shared Secret:** `zobridge_3f7c6a7a8a5f4d129b8c4f2e1d9c0a7b`

**Endpoints:**
- ParentZo: `https://zobridge-va.zocomputer.io`
- ChildZo: `https://zobridge-vademonstrator.zocomputer.io`

**Key Files:**
- Config: `/home/workspace/N5/config/zobridge.config.json`
- Database: `/home/workspace/N5/data/zobridge.db`
- Logs: `/dev/shm/zobridge.log` and `/dev/shm/zobridge_err.log`
