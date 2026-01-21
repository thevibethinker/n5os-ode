---
created: 2026-01-20
last_edited: 2026-01-20
version: 1.0
type: build_plan
status: draft
provenance: con_8VvViqhKBZ2hJtSW
---

# Plan: Careerspan Founder Scan Management Integration

**Objective:** Add two new Careerspan API capabilities (scan access management + system status) while establishing a categorization system for N5 scripts.

**Trigger:** V wants to manage employer scan access and credits via Zo, following the same atomic script pattern as `set_employer_password.py`.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- Surface unknowns HERE at the TOP. Resolve before proceeding. -->
- [x] Where should scripts live? → `N5/scripts/` alongside `set_employer_password.py` ✓
- [x] Combined or atomic scripts? → Atomic (one script per capability) ✓
- [x] What categorization system? → Add `product` field to frontmatter taxonomy with values `careerspan`, `zo` ✓
- [ ] **Test employer email?** → V to provide before dry-run testing
- [ ] **Test job/lead ID?** → V to provide before dry-run testing
- [ ] **FOUNDER_AUTH_TOKEN location?** → Confirm it's in Zo Secrets (Settings > Developers)

---

## Checklist

### Phase 1: Schema & Taxonomy Extension
- ☐ Update `frontmatter_taxonomy.json` to add `product` dimension with `careerspan`, `zo`, `n5` values
- ☐ Document the new taxonomy field in a reference doc
- ☐ Test: Validate JSON is well-formed

### Phase 2: Scan Access Management Script
- ☐ Create `manage_employer_scan_access.py` in `N5/scripts/`
- ☐ Add docstring frontmatter with `product: careerspan` and full usage docs
- ☐ Implement all five operations: enable, disable, add credits, set org restrictions
- ☐ Add `--confirm` requirement for all mutations
- ☐ Add `--dry-run` mode (mandatory first output)
- ☐ Add audit logging to `N5/logs/careerspan_audit.jsonl`
- ☐ Test: Dry-run with test employer email

### Phase 3: System Status Script
- ☐ Create `founder_scan_system_status.py` in `N5/scripts/`
- ☐ Add docstring frontmatter with `product: careerspan`
- ☐ Implement status fetch (read-only, no confirm needed)
- ☐ Format output for human readability (tables, timestamps)
- ☐ Test: Run against prod API

### Phase 4: Retrofit & Validation
- ☐ Update `set_employer_password.py` to include `product: careerspan` frontmatter
- ☐ Create validation checklist for prod deployment
- ☐ Document all three Careerspan scripts in README

---

## Phase 1: Schema & Taxonomy Extension

### Affected Files
- `N5/config/frontmatter_taxonomy.json` - UPDATE - add `product` field
- `N5/docs/script-frontmatter-standard.md` - CREATE - document the standard

### Changes

**1.1 Extend Taxonomy JSON:**

Add new top-level key `products` to the existing taxonomy:

```json
{
  "types": [...existing...],
  "categories": [...existing...],
  "owners": [...existing...],
  "statuses": [...existing...],
  "products": [
    "careerspan",
    "zo",
    "n5",
    "standalone"
  ]
}
```

- `careerspan` = Careerspan product API integrations
- `zo` = Zo platform integrations (future)
- `n5` = Internal N5 system scripts
- `standalone` = General utilities with no product affiliation

**1.2 Create Standard Documentation:**

Document the script frontmatter pattern. Scripts should have:

```python
#!/usr/bin/env python3
"""Short description.

---
product: careerspan
version: 1.0
created: 2026-01-20
requires_confirm: true
audit_log: N5/logs/careerspan_audit.jsonl
---

Usage examples:
  ...
"""
```

### Unit Tests
- `python3 -c "import json; json.load(open('N5/config/frontmatter_taxonomy.json'))"` → No errors
- Grep for `products` key exists in file

---

## Phase 2: Scan Access Management Script

### Affected Files
- `N5/scripts/manage_employer_scan_access.py` - CREATE - main capability script
- `N5/logs/careerspan_audit.jsonl` - CREATE (on first use) - audit trail

### Changes

**2.1 Script Structure:**

Mirror the pattern from `set_employer_password.py`:
- Standard library only (urllib, json, argparse)
- `FOUNDER_AUTH_TOKEN` from environment
- Same base URL and timeout patterns
- Comprehensive error handling with helpful messages

**2.2 CLI Interface:**

```bash
# Enable scanning and add credits
python3 N5/scripts/manage_employer_scan_access.py user@example.com \
  --enable \
  --credits 10 \
  --confirm

# Add credits only
python3 N5/scripts/manage_employer_scan_access.py user@example.com \
  --credits 5 \
  --confirm

# Disable scanning
python3 N5/scripts/manage_employer_scan_access.py user@example.com \
  --disable \
  --confirm

# Set org restrictions (by name)
python3 N5/scripts/manage_employer_scan_access.py user@example.com \
  --org-scanning-enabled \
  --allowed-orgs "Acme Corp" "Beta Inc" \
  --confirm

# Dry run (always outputs what WOULD happen)
python3 N5/scripts/manage_employer_scan_access.py user@example.com \
  --enable --credits 10 \
  --dry-run
```

**2.3 Mandatory Guardrails:**

1. **`--confirm` required for all mutations** - Script refuses to call API without it
2. **Dry-run preview** - Before ANY mutation, print exactly what will be sent
3. **Audit logging** - Every operation (including dry-runs) logged to `N5/logs/careerspan_audit.jsonl`

**2.4 Audit Log Format:**

```json
{
  "timestamp": "2026-01-20T14:10:00Z",
  "operation": "manage_employer_scan_access",
  "employer_email": "user@example.com",
  "action": "enable_scanning_add_credits",
  "params": {"scanning_enabled": true, "credits_to_add": 10},
  "dry_run": false,
  "result": "success",
  "response": {...}
}
```

**2.5 Response Formatting:**

Pretty-print the response:
```
✓ Scan access updated for employer abc123

  Scanning:     ENABLED
  Credits:      5 → 15 (+10 added)
  Org Scanning: disabled
  
  Audit logged to: N5/logs/careerspan_audit.jsonl
```

### Unit Tests
- Dry-run with `--dry-run` flag shows payload without calling API
- Missing `--confirm` on mutation produces clear error
- Invalid email format produces helpful error
- `--help` shows all options with examples

---

## Phase 3: System Status Script

### Affected Files
- `N5/scripts/founder_scan_system_status.py` - CREATE - read-only status script

### Changes

**3.1 Script Structure:**

Simpler than the mutation script (no confirm needed, read-only):
- Standard library only
- `FOUNDER_AUTH_TOKEN` from environment
- GET request to `/etc/founder_scan_system_status`

**3.2 CLI Interface:**

```bash
# Get system status
python3 N5/scripts/founder_scan_system_status.py

# JSON output for scripting
python3 N5/scripts/founder_scan_system_status.py --json
```

**3.3 Output Format (default):**

```
═══════════════════════════════════════════════════
  Careerspan Scan System Status
  Retrieved: 2026-01-20 09:10:00 ET
═══════════════════════════════════════════════════

OVERVIEW (Last 30 Days)
  Pending:    3 scans
  Running:    2 scans
  Completed:  45 scans
  Errored:    1 scan
  
  Max Wait:   60 min
  Avg Wait:   20 min

ACTIVE SCANS
┌────────────┬───────────────┬─────────┬──────────────────┐
│ Employer   │ Scan ID       │ Status  │ Waiting          │
├────────────┼───────────────┼─────────┼──────────────────┤
│ abc123     │ 550e8400...   │ pending │ 60 min           │
│ def456     │ 660f9500...   │ running │ 45 min (started) │
└────────────┴───────────────┴─────────┴──────────────────┘
```

### Unit Tests
- `--help` works
- `--json` produces valid JSON
- Missing token produces clear error

---

## Phase 4: Retrofit & Validation

### Affected Files
- `N5/scripts/set_employer_password.py` - UPDATE - add frontmatter
- `N5/docs/careerspan-api-scripts.md` - CREATE - comprehensive docs

### Changes

**4.1 Retrofit Existing Script:**

Add frontmatter block to `set_employer_password.py` docstring:

```python
"""One-off employer password setup tool.

---
product: careerspan
version: 1.0
created: 2025-XX-XX
updated: 2026-01-20
requires_confirm: true (via --dry-run pattern)
audit_log: N5/logs/careerspan_audit.jsonl
---

Usage examples:
...
"""
```

Also add audit logging to match the new scripts.

**4.2 Create Master Documentation:**

Create `N5/docs/careerspan-api-scripts.md` documenting:
- All three scripts and their purposes
- Common patterns (auth, base URL, timeout)
- Guardrails (confirm, dry-run, audit)
- Test employer workflow
- Prod deployment checklist

**4.3 Prod Deployment Validation Checklist:**

```markdown
## Pre-Deployment Checklist

- [ ] FOUNDER_AUTH_TOKEN is set in Zo Secrets
- [ ] Dry-run tested with test employer email
- [ ] Audit log created successfully
- [ ] Error cases tested (invalid email, missing token)
- [ ] Documentation complete
- [ ] V has approved test results
```

### Unit Tests
- `set_employer_password.py --help` still works after frontmatter addition
- All three scripts have consistent `--help` formatting
- Master doc renders correctly

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `N5/config/frontmatter_taxonomy.json` | W1.1 | ✓ |
| `N5/docs/script-frontmatter-standard.md` | W1.1 | ✓ |
| `N5/scripts/manage_employer_scan_access.py` | W1.2 | ✓ |
| `N5/logs/careerspan_audit.jsonl` (pattern) | W1.2 | ✓ |
| `N5/scripts/founder_scan_system_status.py` | W1.3 | ✓ |
| `N5/scripts/set_employer_password.py` (retrofit) | W1.4 | ✓ |
| `N5/docs/careerspan-api-scripts.md` | W1.4 | ✓ |
| Validation checklist | W1.4 | ✓ |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~1,200 | ~2,000 | 1.6% | ✓ |
| W1.2 | ~2,500 | ~4,000 | 3.25% | ✓ |
| W1.3 | ~1,500 | ~2,000 | 1.75% | ✓ |
| W1.4 | ~1,800 | ~4,000 | 2.9% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [x] Wave dependencies are valid (all Wave 1, can run in parallel)
- [ ] `python3 N5/scripts/mece_validator.py careerspan-scan-mgmt` passes (run after briefs created)

---

## Worker Briefs

| Wave | Worker | Title | Brief File | Focus |
|------|--------|-------|------------|-------|
| 1 | W1.1 | Schema & Taxonomy | `workers/W1.1-schema-taxonomy.md` | Extend frontmatter taxonomy |
| 1 | W1.2 | Scan Access Script | `workers/W1.2-scan-access-script.md` | Main mutation script |
| 1 | W1.3 | Status Script | `workers/W1.3-status-script.md` | Read-only status script |
| 1 | W1.4 | Retrofit & Docs | `workers/W1.4-retrofit-docs.md` | Update existing + master docs |

All workers are Wave 1 (no dependencies between them). V can launch them in parallel.

---

## Success Criteria

1. **Functional:** All three scripts work with `--dry-run` against test employer
2. **Guardrails:** No mutation possible without `--confirm` flag
3. **Auditability:** Every operation logged to `N5/logs/careerspan_audit.jsonl`
4. **Discoverability:** Scripts categorized with `product: careerspan` frontmatter
5. **Documentation:** Master doc exists with validation checklist

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Accidental prod mutation** | Mandatory `--confirm` flag; dry-run shows exact payload first |
| **Token auth failure** | Clear error message pointing to Zo Secrets |
| **API contract drift** | Pin base URL; document expected response schema |
| **Audit log corruption** | Use JSONL (append-only); include timestamp in every entry |

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| Taxonomy `products` field name | LOW | Once other scripts use it, renaming is expensive |
| Audit log path | MEDIUM | Can migrate but may lose history context |
| Script naming convention | LOW | Once referenced in docs/prompts, renaming breaks links |

**Recommendation:** Confirm `products` is the right field name (vs. `product`, `integration`, `domain`) before Phase 1.

---

## Nemawashi: Alternatives Considered

### Alternative 1: Combined CLI Tool
**Approach:** Single `careerspan-admin.py` with subcommands (`password`, `scan`, `status`)

**Pros:** Single entry point, shared auth logic, easier to discover
**Cons:** Larger script, harder to test individual ops, breaks atomic pattern

**Decision:** REJECTED - Stick with atomic scripts per V's preference

### Alternative 2: Skill-Based Structure
**Approach:** Create `Skills/careerspan/` with SKILL.md and scripts in `scripts/`

**Pros:** More discoverable, follows Skills spec, room for prompts
**Cons:** Adds folder structure complexity, scripts are currently in N5/

**Decision:** REJECTED for now - Can migrate later if Careerspan integrations grow

### Alternative 3: Category in Script Docstring Only
**Approach:** Just add `product: careerspan` to docstrings, no taxonomy update

**Pros:** Simpler, no schema changes
**Cons:** No validation, inconsistent with taxonomy system

**Decision:** REJECTED - Full taxonomy integration is more robust

---

## Level Upper Review

*(To be completed before worker handoff)*

### Counterintuitive Suggestions Received:
1. (Pending Level Upper invocation)

### Incorporated:
- (None yet)

### Rejected (with rationale):
- (None yet)

---

## API Reference (For Worker Context)

### Endpoint 1: Manage Employer Scan Access
```
POST /etc/manage_employer_scan_access
Authorization: Bearer <founder_token>

Request:
{
  "employer_email": "employer@company.com",
  "scanning_enabled": true,
  "credits_to_add": 10,
  "org_scanning_enabled": false,
  "allowed_organizations": []
}

Response:
{
  "employer_id": "abc123",
  "scanning_enabled": true,
  "previous_credits": 5,
  "credits_added": 10,
  "new_balance": 15,
  "org_scanning_enabled": false,
  "allowed_organizations": [],
  "allowed_organizations_map": {}
}
```

### Endpoint 2: Get Scan System Status
```
GET /etc/founder_scan_system_status
Authorization: Bearer <founder_token>

Response:
{
  "overall": {
    "pending_count": 3,
    "running_count": 2,
    "completed_last_30_days": 45,
    "errored_last_30_days": 1,
    "max_wait_seconds_last_30_days": 3600,
    "avg_wait_seconds_last_30_days": 1200.5
  },
  "active_scans": [...]
}
```

### Base URL
```
https://the-apply-ai--dossier-ai-all-main-fastapi-app.modal.run
```

### Auth
`FOUNDER_AUTH_TOKEN` environment variable (set in Zo Secrets)
