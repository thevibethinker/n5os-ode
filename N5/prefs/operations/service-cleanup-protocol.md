---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_u0LhWqxkPWYn44Fg
---

# Service Cleanup Protocol

**Purpose:** Maintain hygiene of user services by periodically identifying and purging stale, broken, or obsolete services.

## When to Run

- **Monthly:** Quick audit during monthly system review
- **Quarterly:** Full cleanup sweep
- **Ad-hoc:** When service count exceeds 40, or after major refactors

## Cleanup Criteria

### 🔴 Auto-Remove (No Confirmation Needed)

1. **Missing Workdir** — Service's `workdir` directory no longer exists
2. **Missing Entrypoint** — Script/binary in entrypoint path doesn't exist
3. **Duplicate Ports** — Multiple services claiming same port (keep newest)
4. **Orphaned ZoBridge** — Any `zobridge-*` service (retired system)

### 🟡 Review Before Removing

1. **HTTP 5xx/404** — Service responds with errors (may be temporarily down)
2. **Age > 90 days** — Services older than 90 days without recent restarts
3. **No entrypoint** — Services registered without entrypoint (skeleton registrations)
4. **Staging without prod** — `*-staging` services where prod version doesn't exist

### 🟢 Protected (Never Auto-Remove)

- Services with label containing `webhook` (integration dependencies)
- Services in PORT_REGISTRY with explicit protection note
- Services matching patterns in `N5/config/protected_services.txt` (if exists)

## Cleanup Procedure

### 1. Audit

```bash
# List all services with health check
python3 N5/scripts/service_audit.py --full

# Or manual:
# 1. list_user_services
# 2. Check each workdir exists
# 3. Curl each HTTP endpoint
```

### 2. Categorize

Create three lists:
- **DELETE_NOW:** Red criteria met
- **REVIEW:** Yellow criteria met  
- **KEEP:** Everything else

### 3. Execute

```bash
# For each service_id in DELETE_NOW:
delete_user_service(service_id)

# For REVIEW items: present to V for decision
```

### 4. Sync Registry

```bash
python3 N5/scripts/port_registry.py sync
```

### 5. Document

Log cleanup in `N5/logs/maintenance/service-cleanups.jsonl`:
```json
{"date": "2026-01-14", "deleted": 16, "kept": 30, "services_removed": ["label1", "label2"]}
```

## Port Reclamation

After deleting services, ports become available again. Update:
1. `N5/config/PORT_REGISTRY.md` — Remove deleted entries
2. "Next Available" sections — Recalculate if needed

## Related

- `file 'N5/config/PORT_REGISTRY.md'` — Port allocations
- `file 'N5/scripts/port_registry.py'` — Port management CLI
- [Services](/?t=sites&s=services) — UI for service management

