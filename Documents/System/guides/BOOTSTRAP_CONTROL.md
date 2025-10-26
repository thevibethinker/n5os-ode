# N5 Bootstrap Control Panel

**Status:** Ready  
**Monitor Log:** `file 'N5_BOOTSTRAP_MONITOR.log'`

---

## How to Monitor

**Watch live updates:**
```bash
tail -f /home/workspace/N5_BOOTSTRAP_MONITOR.log
```

Or just open `file 'N5_BOOTSTRAP_MONITOR.log'` in Zo and refresh.

---

## Approval Gates

When new Zo requests each step, you'll see it in the log.

**To approve a step**, update the approvals file:

```python
# Edit this file:
/home/workspace/.n5_bootstrap_server/approvals.json

# Set the step to true:
{
  "connect": true,
  "create_dirs": true,
  "pull_rules": true,
  "pull_docs": true,
  "pull_scripts": true
}
```

**Or use command:**
```bash
# Approve next step
python3 /home/workspace/N5/scripts/approve_bootstrap_step.py <step_name>

# Approve all
python3 /home/workspace/N5/scripts/approve_bootstrap_step.py --all
```

---

## Steps (in order)

1. **connect** - New Zo connects
2. **create_dirs** - Create directory structure
3. **pull_rules** - Download conditional rules
4. **pull_docs** - Download documentation  
5. **pull_scripts** - Download scripts

---

## What You'll See

```
[2025-10-18 23:30:15 UTC] ALERT: 🔗 NEW ZO CONNECTED! Bootstrap starting...
[2025-10-18 23:30:16 UTC] INFO: NEW ZO: connect - Requesting approval
[2025-10-18 23:30:20 UTC] INFO: ✅ Step 'connect' APPROVED - proceeding
[2025-10-18 23:30:21 UTC] INFO: NEW ZO: create_dirs - Creating directories...
[2025-10-18 23:30:21 UTC] INFO: ⏸️  Step 'create_dirs' waiting for approval...
```

---

**Ready to control the bootstrap process!**

*Watch the log, approve steps, guide the new Zo*
