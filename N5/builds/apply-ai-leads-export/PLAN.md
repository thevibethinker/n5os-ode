---
created: 2025-12-18
last_edited: 2025-12-18
version: 1.0
type: build_plan
status: draft
provenance: con_ZfdOYbRlbBeEh5lo
---

# Plan: Apply AI Leads Export Capability

**Objective:** Integrate the Apply AI Export Employer Leads API into the workspace with a CLI tool and a natural language interface for easy data retrieval and manipulation.

**Trigger:** Technical spec grokked and endpoint verified in con_ZfdOYbRlbBeEh5lo.

**Key Design Principle:** Simple over easy. Provide a clean CLI wrapper that abstracts auth and pathing, allowing V to trigger exports via natural language and then "manipulate them further" as requested.

---

## Open Questions

- [ ] None. Endpoint verified and auth token ($FOUNDER_AUTH_TOKEN) is active.

---

## Checklist

### Phase 1: Core CLI Integration
- ☑ Create `Integrations/apply_ai_leads.py` with standard CLI args
- ☑ Ensure automated directory creation for `Records/Exports/Leads/`
- ☑ Test: Run script with `--days 1` and verify CSV content
- ☑ Test: Run script with invalid auth to verify error handling

### Phase 2: Natural Language Interface
- ☑ Create `Prompts/Apply AI Leads Export.prompt.md` with `tool: true`
- ☑ Create descriptive help text for the prompt
- ☑ Test: Invoke `@Apply AI Leads Export` in chat and verify execution
- ☑ Update SESSION_STATE artifacts

---

## Phase 1: Core CLI Integration

### Affected Files
- `Integrations/apply_ai_leads.py` - CREATE - CLI wrapper for the Export Employer Leads API.
- `Records/Exports/Leads/` - CREATE - Canonical directory for lead exports.

### Changes

**1.1 Python CLI Implementation:**
- Use `argparse` for: `--days` (default 30), `--employer-email` (optional), `--output` (optional).
- Use `httpx` or `requests` for the POST call.
- Extract `FOUNDER_AUTH_TOKEN` from environment variables.
- Auto-generate output filenames: `leads_export_{timestamp}.csv`.
- Print the absolute path of the generated file to stdout for Zo's consumption.

**1.2 Directory Preparation:**
- Ensure `/home/workspace/Records/Exports/Leads/` exists.

### Unit Tests
- `python3 Integrations/apply_ai_leads.py --days 1`: verify 200 OK and file creation.
- `python3 Integrations/apply_ai_leads.py --employer-email test@test.com`: verify filter propagation.

---

## Phase 2: Natural Language Interface

### Affected Files
- `Prompts/Apply AI Leads Export.prompt.md` - CREATE - Natural language entry point.

### Changes

**2.1 Prompt Design:**
- Add YAML frontmatter with `tool: true`.
- Description: "Exports Apply AI employer leads and applicant data to a CSV file. Supports day-range filtering and employer email filtering."
- Logic: Map user natural language (e.g., "get leads for the last week") to the CLI script execution.

### Unit Tests
- `@Apply AI Leads Export last 7 days`: verify prompt triggers correct script call.

---

## Success Criteria

1. CLI tool successfully retrieves CSV data from the Apply AI endpoint.
2. Exported files are organized in `Records/Exports/Leads/`.
3. V can trigger an export using only natural language in the chat.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Cold starts on Modal | Implement 30s timeout in Python script. |
| Shelf-life/Scalability | Print warning if data volume is expected to be high (>90 days). |
| Auth Token Expiry | Return clear "401 Unauthorized" error message to chat. |

---

## Level Upper Review

Not invoked for this tactical integration.




