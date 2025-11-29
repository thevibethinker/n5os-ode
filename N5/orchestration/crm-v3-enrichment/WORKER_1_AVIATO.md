---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
---

# Worker 1: Aviato API Integration

**Orchestrator:** con_rMaSw6rzVNkWvsQ4
**Mission:** Replace Aviato enrichment stubs with real API calls
**Status:** READY TO EXECUTE

## Context

**What Exists:**
- ✅ Working Aviato SDK at `file 'Integrations/Aviato/aviato_client.py'`
- ✅ CRM mapper at `file 'Integrations/Aviato/crm_mapper.py'`
- ✅ API key configured in `file 'Integrations/Aviato/.env'`
- ✅ Tested with Bill Gates example (83KB enrichment report)

**What's Needed:**
- ❌ Stub code in `crm_enrichment_worker.py` lines 109-123
- ❌ No real Aviato enrichment happening for queued jobs
- ❌ Profiles showing "⚠️ STUB DATA" in intelligence blocks

**Current Stub Code:**
```python
aviato_data = {
    "name": email.split('@')[0].replace('.', ' ').title(),
    "title": "Senior Product Manager",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "note": "⚠️ STUB DATA - Aviato API not yet integrated"
}
```

## Mission

Build real Aviato enrichment that:
1. Uses existing AviatoClient SDK
2. Handles API errors gracefully (404 = person not found)
3. Maps Aviato response → CRM intelligence format
4. Returns structured data for YAML appending

## Deliverables

### 1. Create `/home/workspace/N5/scripts/enrichment/aviato_enricher.py`

**Function signature:**
```python
async def enrich_via_aviato(email: str, name: Optional[str] = None) -> dict:
    """
    Enrich profile using Aviato API.
    
    Returns:
        {
            "success": bool,
            "data": dict or None,
            "error": str or None,
            "markdown": str  # Formatted intelligence block
        }
    """
```

**Requirements:**
- Use `AviatoClient` from `Integrations/Aviato/aviato_client.py`
- Call `enrich_person_by_email(email, name)` or `enrich_person_by_linkedin_url(url)`
- Handle 404 (person not found) gracefully
- Handle rate limits (429) with backoff
- Return formatted markdown suitable for YAML appending
- Log API usage for cost tracking

**Intelligence Block Format:**
```markdown
**Aviato Professional Intelligence:**

**Current Role:**
- Title: {title}
- Company: {company}
- Location: {location}

**Professional Profile:**
- LinkedIn: {linkedin_url}
- Headline: {headline}
- Connections: {linkedin_connections}
- Open to Work: {yes/no}

**Background:**
- {num} previous roles
- {num} education entries
- Skills: {top 5 skills}

**Last Updated:** {aviato_last_updated}
**Aviato ID:** {aviato_person_id}
```

### 2. Update `/home/workspace/N5/scripts/crm_enrichment_worker.py`

**Replace lines 109-123:**
```python
# 1. Aviato enrichment (REAL)
from N5.scripts.enrichment.aviato_enricher import enrich_via_aviato

aviato_result = await enrich_via_aviato(email, profile_name)
if aviato_result['success']:
    intelligence_parts.append(aviato_result['markdown'])
else:
    # Graceful fallback
    intelligence_parts.append(f"""**Aviato Enrichment:**
Profile not found in Aviato database for {email}.
Error: {aviato_result['error']}
""")
```

### 3. Test on Real Profiles

**Test Subjects:**
```sql
-- Find profiles with known professional backgrounds
SELECT id, email, name FROM profiles 
WHERE email IN (
    'epak171@gmail.com',  -- Elaine Pak
    'konrad@aviato.co',   -- Konrad (should definitely exist!)
    'attawar.v@gmail.com' -- V himself
) LIMIT 3;
```

**Run enrichment:**
```bash
cd /home/workspace
python3 -c "
import asyncio
from N5.scripts.enrichment.aviato_enricher import enrich_via_aviato

async def test():
    result = await enrich_via_aviato('konrad@aviato.co', 'Konrad Kucharski')
    print(result['markdown'])

asyncio.run(test())
"
```

### 4. Cost/Usage Tracking

**Create:** `/home/workspace/N5/logs/aviato_usage.jsonl`

**Log format:**
```json
{"timestamp": "2025-11-18T00:10:00Z", "email": "test@example.com", "success": true, "person_found": true}
{"timestamp": "2025-11-18T00:11:00Z", "email": "nope@example.com", "success": true, "person_found": false}
```

## Validation Criteria

**Before handoff to Worker 4:**
- [ ] `aviato_enricher.py` created and working
- [ ] `crm_enrichment_worker.py` updated to use real API
- [ ] Tested on 3 real profiles successfully
- [ ] Error handling works (test with fake email)
- [ ] Rate limiting handled gracefully
- [ ] Usage logging implemented
- [ ] No stub data in test outputs

**Test Command:**
```bash
cd /home/workspace/N5/scripts/enrichment
python3 aviato_enricher.py  # Should have __main__ block for testing
```

## Key Resources

**Files to Read:**
- `file 'Integrations/Aviato/aviato_client.py'` - SDK methods
- `file 'Integrations/Aviato/crm_mapper.py'` - Field extraction patterns
- `file 'Integrations/Aviato/test_person_response.json'` - Sample response structure
- `file 'N5/scripts/crm_enrichment_worker.py'` - Current stub location

**API Documentation:**
- Aviato person/enrich: https://docs.data.aviato.co/api-reference/person/enrich
- Rate limits: Check with Aviato team
- Pricing: Check V's Aviato dashboard

## Handoff to Worker 4

**Success Message:**
```
✅ Worker 1 Complete: Aviato Integration

Deliverables:
- aviato_enricher.py (X lines)
- crm_enrichment_worker.py updated
- Tested on 3 profiles (all successful)
- Usage logging active
- Error handling validated

Ready for Worker 4 to execute enrichment queue with real Aviato data.

Test Results:
- konrad@aviato.co: ✓ Found, 8 experiences, current role: Aviato Co-founder
- epak171@gmail.com: ✓/✗ [result]
- attawar.v@gmail.com: ✓/✗ [result]
```

---

**Load this file in a new conversation to execute Worker 1.**

**Start Command:**
```
I am Worker 1 in the CRM V3 Enrichment build orchestration.

Load and execute: file 'N5/orchestration/crm-v3-enrichment/WORKER_1_AVIATO.md'

Replace Aviato stub with real API integration using existing SDK at Integrations/Aviato/.
```

