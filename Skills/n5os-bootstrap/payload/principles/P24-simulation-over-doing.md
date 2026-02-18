# P24: Simulation Over Doing

**Category:** Design Philosophy  
**Priority:** High  
**Related:** P25 (Code Is Free), P26 (Fast Feedback Loops)

---

## Principle

**Simulate outcomes before executing. Dry-runs, previews, and "what-if" analysis prevent expensive mistakes.**

Before any destructive or irreversible operation, simulate it. Show the user what *would* happen, get confirmation, then execute.

---

## Pattern

### Standard Implementation

Every significant operation should support:

```python
def operation(target, dry_run=False):
    """Execute operation with optional dry-run."""
    changes = compute_changes(target)
    
    if dry_run:
        logger.info(f"[DRY RUN] Would perform: {changes}")
        return changes
    
    logger.info(f"Executing: {changes}")
    execute_changes(changes)
    verify_state(target)
    return changes

# Usage
operation(target, dry_run=True)   # Preview
operation(target, dry_run=False)  # Execute
```

### CLI Pattern

```bash
# Preview
./script.py --dry-run

# Execute
./script.py
```

---

## Examples

### File Operations
```python
# Bad: Direct execution
os.remove(file)

# Good: Simulate first
def safe_delete(file, dry_run=False):
    if not os.path.exists(file):
        raise FileNotFoundError(f"{file} not found")
    
    size = os.path.getsize(file)
    if dry_run:
        logger.info(f"[DRY RUN] Would delete: {file} ({size} bytes)")
        return
    
    os.remove(file)
    logger.info(f"✓ Deleted: {file} ({size} bytes)")
```

### Database Operations
```python
# Bad: Direct write
db.execute("DELETE FROM users WHERE last_login < '2020-01-01'")

# Good: Simulate first
def cleanup_users(cutoff_date, dry_run=False):
    count = db.query("SELECT COUNT(*) FROM users WHERE last_login < ?", cutoff_date)
    
    if dry_run:
        logger.info(f"[DRY RUN] Would delete {count} users")
        return count
    
    db.execute("DELETE FROM users WHERE last_login < ?", cutoff_date)
    logger.info(f"✓ Deleted {count} users")
    return count
```

### API Calls
```python
# Bad: Direct send
api.send_email(recipients, subject, body)

# Good: Simulate first
def send_campaign(recipients, template, dry_run=False):
    emails = [render_template(template, r) for r in recipients]
    
    if dry_run:
        logger.info(f"[DRY RUN] Would send {len(emails)} emails")
        logger.info(f"Preview: {emails[0]}")
        return emails
    
    for email in emails:
        api.send_email(email)
    
    logger.info(f"✓ Sent {len(emails)} emails")
    return emails
```

---

## Benefits

1. **Catch errors early:** See mistakes before they happen
2. **Build confidence:** User knows exactly what will happen
3. **Iterative refinement:** Test parameters without consequences
4. **Audit trail:** Log shows what was simulated vs executed

---

## Implementation Checklist

For any operation that:
- Deletes data
- Modifies state
- Costs money
- Sends messages
- Is irreversible

Require:
- [ ] `--dry-run` flag
- [ ] Clear "[DRY RUN]" prefix in logs
- [ ] Preview of changes
- [ ] Confirmation before execution
- [ ] Verification after execution

---

## Common Mistakes

❌ Forgetting to verify after execution
❌ Unclear dry-run output (doesn't show what would happen)
❌ Requiring dry-run (should be optional)
❌ Simulation diverges from actual execution (different code paths)

**Fix:** Use the same code path for dry-run and execution. Only the final write differs.

---

## Related Principles

- **P7 (Dry-Run):** Every destructive operation requires dry-run support
- **P25 (Code Is Free):** Adding dry-run is cheap, mistakes are expensive
- **P26 (Fast Feedback Loops):** Dry-run enables rapid iteration

---

**Pattern:** Preview → Confirm → Execute → Verify
