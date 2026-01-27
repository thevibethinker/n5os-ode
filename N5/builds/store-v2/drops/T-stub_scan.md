---
build_slug: store-v2
drop_type: tidying
hygiene_check: stub_scan
auto_generated: true
---

---
template_type: hygiene_check
hygiene_phase: tidying
auto_fix: false
priority: 3
---

# Stub Scan Hygiene Check

## Scope

Detects incomplete implementation markers that indicate unfinished work:
- TODO/FIXME/HACK comments
- `NotImplementedError` and `raise NotImplemented`
- Placeholder strings ("TBD", "PLACEHOLDER", "XXX")
- Empty function/method bodies
- `pass` statements in non-abstract methods

## Purpose

Stubs indicate work that was scoped but not completed. Finding stubs after a build suggests:
- A Drop didn't complete its scope
- Work was intentionally deferred
- Implementation was blocked

These MUST be escalated for review.

## Commands

```bash
BUILD_DIR="N5/builds/${BUILD_SLUG}"
ARTIFACTS_DIR="${BUILD_DIR}/artifacts"

# TODO/FIXME/HACK comments
grep -rn "TODO\|FIXME\|HACK\|XXX" "$ARTIFACTS_DIR" --include="*.py" --include="*.ts" --include="*.js"

# NotImplementedError
grep -rn "NotImplementedError\|raise NotImplemented" "$ARTIFACTS_DIR" --include="*.py"

# Placeholder strings
grep -rn "PLACEHOLDER\|TBD\|STUB\|TODO:" "$ARTIFACTS_DIR" --include="*.py" --include="*.ts" --include="*.json"

# Empty function bodies (Python)
grep -Pzo "def \w+\([^)]*\):\s*\n\s*(pass|\.\.\.)\s*\n" "$ARTIFACTS_DIR"/*.py 2>/dev/null

# TypeScript: Empty functions
grep -Pzo "function \w+\([^)]*\)\s*{\s*}" "$ARTIFACTS_DIR"/*.ts 2>/dev/null
```

## Output Schema

```json
{
  "findings": [
    {
      "type": "todo_comment",
      "file": "scripts/main.py",
      "line": 42,
      "content": "# TODO: implement error handling",
      "severity": "medium"
    },
    {
      "type": "not_implemented",
      "file": "scripts/api.py",
      "line": 78,
      "function": "process_webhook",
      "severity": "high"
    },
    {
      "type": "empty_body",
      "file": "scripts/handlers.py",
      "line": 15,
      "function": "on_complete",
      "body": "pass",
      "severity": "high"
    },
    {
      "type": "placeholder_string",
      "file": "config.json",
      "line": 12,
      "content": "\"api_key\": \"PLACEHOLDER\"",
      "severity": "medium"
    }
  ],
  "auto_fixable": [],
  "requires_review": [
    {
      "type": "not_implemented",
      "severity": "high",
      "issue": "Function has NotImplementedError",
      "recommendation": "Either implement or mark as intentionally abstract"
    }
  ],
  "summary": {
    "total_stubs": 8,
    "high_severity": 3,
    "medium_severity": 5,
    "by_type": {
      "todo_comment": 4,
      "not_implemented": 2,
      "empty_body": 1,
      "placeholder_string": 1
    }
  }
}
```

## Auto-Fix Rules

**auto_fix: false**

Stubs indicate incomplete work and MUST be escalated. Auto-fixing would:
- Hide incomplete features
- Create silent failures
- Mask scope creep

## Severity Classification

| Type | Severity | Rationale |
|------|----------|-----------|
| `not_implemented` | HIGH | Runtime error if called |
| `empty_body` | HIGH | Silent no-op, likely bug |
| `todo_comment` | MEDIUM | May be acceptable tech debt |
| `placeholder_string` | MEDIUM | May cause runtime issues |
| `hack_comment` | LOW | Technical debt marker |

## Escalation Triggers

- ANY `not_implemented` → Immediate escalation
- ANY `empty_body` in non-abstract class → Immediate escalation
- >3 TODO comments in single file → Escalate
- Placeholder in config/secrets → HIGH priority escalation

## Expected Resolution

When this check finds stubs, orchestrator must:
1. Identify which Drop was responsible for that code
2. Determine if work was intentionally deferred
3. Either complete the work or document deferral reason
4. Update build AAR with stub disposition


## Build Context
- **Build Slug**: store-v2
- **Build Dir**: N5/builds/store-v2

## Deposit Location
Write your deposit to: N5/builds/store-v2/deposits/T-stub_scan.json

## Required Deposit Schema
```json
{
  "drop_id": "T-stub_scan",
  "build_slug": "store-v2",
  "check_type": "stub_scan",
  "findings": [...],
  "auto_fixable": [...],
  "requires_review": [...],
  "health_contribution": 0.0-1.0
}
```
