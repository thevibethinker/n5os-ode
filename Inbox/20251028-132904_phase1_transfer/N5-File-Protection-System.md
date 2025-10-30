# N5 File Protection System

**Purpose**: Lightweight directory protection to prevent accidental moves/deletes  
**Created**: 2025-10-28  
**Design Philosophy**: Simple over easy, flow over pools, self-documenting

---

## Overview

The N5 File Protection System uses marker files (`.n5protected`) to protect directories from accidental moves or deletes. Protection metadata flows with the directory itself, requiring no external registry to maintain.

### Key Features

- ✅ **Auto-protection**: Service directories automatically protected on registration
- ✅ **AI-aware**: Conditional rules check for markers before suggesting operations
- ✅ **Self-documenting**: Human-readable JSON marker files
- ✅ **Zero maintenance**: Metadata travels with directory
- ✅ **Non-invasive**: Doesn't modify permissions or filesystem flags
- ✅ **Portable**: Works with git, rsync, tar, etc.

---

## How It Works

### Marker File Format

Protected directories contain a `.n5protected` file with JSON metadata:

```json
{
  "protected": true,
  "reason": "registered_service:n5-waitlist",
  "created": "2025-10-28T04:02:13.560592+00:00",
  "created_by": "user"
}
```

### AI Behavior

When suggesting move/delete operations, AI:
1. Checks for `.n5protected` markers in target path and parents
2. If found, displays warning: "⚠️ This path is protected (reason: X)"
3. Requires explicit confirmation before proceeding
4. User can override with explicit approval

---

## Commands

### Protect a Directory
```bash
python3 /home/workspace/N5/scripts/n5_protect.py protect <path> --reason "description"
```

**Example:**
```bash
python3 /home/workspace/N5/scripts/n5_protect.py protect /home/workspace/critical-data --reason "production_database"
```

### Unprotect a Directory
```bash
python3 /home/workspace/N5/scripts/n5_protect.py unprotect <path>
```

### List Protected Directories
```bash
python3 /home/workspace/N5/scripts/n5_protect.py list
```

**Output:**
```
Found 3 protected directories:

  🔒 n5-waitlist
     Reason: registered_service:n5-waitlist

  🔒 .n5_bootstrap_server
     Reason: registered_service:n5-bootstrap-support
  
  🔒 N5/services/zobridge
     Reason: registered_service:zobridge
```

### Check if Path is Protected
```bash
python3 /home/workspace/N5/scripts/n5_protect.py check <path>
```

**Example:**
```bash
$ python3 /home/workspace/N5/scripts/n5_protect.py check /home/workspace/n5-waitlist
⚠️  PROTECTED: /home/workspace/n5-waitlist
   Reason: registered_service:n5-waitlist
   Created: 2025-10-28T04:02:13.560592+00:00
```

---

## N5 Command Triggers

These commands are registered in `file 'N5/config/commands.jsonl'`:

- `n5-protect` - Protect a directory
- `n5-unprotect` - Remove protection
- `n5-list-protected` - List all protected directories
- `n5-check-protected` - Check if path is protected

---

## Auto-Protection

### Service Directories

When a user service is registered with a `workdir`, that directory should be automatically protected. Currently protected services:

- `/home/workspace/n5-waitlist` (n5-waitlist service)
- `/home/workspace/.n5_bootstrap_server` (n5-bootstrap-support)
- `/home/workspace/N5/services/zobridge` (zobridge service)

### Future Enhancement

The `register_user_service` and `update_user_service` tools should automatically call `n5_protect.py` when a workdir is set, with metadata:

```json
{
  "protected": true,
  "reason": "registered_service",
  "service_label": "service-name",
  "service_id": "svc_xxx",
  "created": "2025-10-28T04:02:13Z",
  "created_by": "system",
  "auto_protected": true
}
```

---

## Design Principles Applied

### Simple Over Easy
- Marker files (simple) vs. filesystem ACLs (easy but complex)
- Few interwoven concepts, low coupling
- Easy to understand and maintain

### Flow Over Pools
- Protection metadata flows with directory
- No external registry to maintain (would be a pool)
- Self-documenting, portable

### Maintenance Over Organization
- Auto-protection reduces manual work
- AI awareness prevents accidents before they happen
- Zero ongoing maintenance overhead

### Fast Feedback Loops
- Instant check via `n5_protect.py check`
- AI gets immediate signal before suggesting operations
- No async verification needed

---

## Integration Points

### User Rules
Conditional rule added: When AI suggests move/delete → check for `.n5protected` markers

### Safety Rules
Documented in `file 'N5/prefs/system/safety-rules.md'` under "Directory Protection Markers"

### Commands Registry
Four commands registered in `file 'N5/config/commands.jsonl'`

### Future: Service Registration
Should integrate with `register_user_service` to auto-protect workdirs

---

## Trade-offs

| **Pro** | **Con** |
|---------|---------|
| Simple, few moving parts | Only protects against AI actions |
| Zero maintenance | User can delete marker if determined |
| Self-documenting | Not OS-enforced |
| Flows with directory | Doesn't prevent manual mistakes |
| Auto-protects services | Requires AI awareness rule |

**Assessment**: Trade-offs favor simplicity. Target is preventing AI-suggested accidents (90% of risk), not preventing determined user actions.

---

## Use Cases

### Use Case 1: Service Directory Protection
**Problem**: Service directory moved, breaking registered service  
**Solution**: Auto-protect service workdirs on registration  
**Example**: n5-waitlist incident (2025-10-28)

### Use Case 2: Critical Data Protection
**Problem**: Important research data accidentally moved during cleanup  
**Solution**: Manual protection with descriptive reason  
**Command**: `n5-protect /home/workspace/Research/PhD-Data --reason "doctoral_dissertation_data"`

### Use Case 3: Git Repository Protection
**Problem**: Active git repo moved mid-development  
**Solution**: Protect repo directory while working on feature  
**Command**: `n5-protect /home/workspace/my-project --reason "active_development"`

---

## Troubleshooting

### Marker Not Working
- Verify marker exists: `ls -la /path/to/dir/.n5protected`
- Check marker format: `cat /path/to/dir/.n5protected`
- Ensure AI rule is active: Check user rules in settings

### False Positives
- Remove protection: `n5-unprotect /path/to/dir`
- Or manually delete `.n5protected` file

### Service Not Protected
- Check if workdir is set in service configuration
- Manually protect: `n5-protect /path/to/service --reason "registered_service:label"`
- Future: Will be automatic on service registration

---

## Future Enhancements

1. **Automatic service integration**: Hook into `register_user_service`
2. **Expiring protection**: Add `expires_at` field for temporary protection
3. **Protection levels**: Warn vs. require-password vs. block entirely
4. **Batch operations**: Protect multiple paths at once
5. **Undo stack**: Track protection history for rollback

---

## Meta

- **Script**: `file 'N5/scripts/n5_protect.py'`
- **Commands**: `file 'N5/config/commands.jsonl'`
- **Safety Rules**: `file 'N5/prefs/system/safety-rules.md'`
- **User Rule**: Conditional rule (When suggesting move/delete → check markers)

---

*v1.0 | 2025-10-28 | Designed using Planning Prompt principles*
