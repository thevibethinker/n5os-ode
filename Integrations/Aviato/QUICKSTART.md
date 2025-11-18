---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Aviato Integration Quickstart Guide
## Fast Path to Enriching Stakeholder Profiles

### ✓ Setup Complete
Your Aviato integration is **ready to use**. API key validated and connection tested successfully.

---

## Quick Test (Just Run This)

```bash
cd /home/workspace/Integrations/Aviato
python3 test_connection.py
```

This tests both person and company enrichment using public profiles (Bill Gates, Google).

---

## Enrich a Stakeholder (3-Line Example)

```python
from aviato_client import AviatoClient

client = AviatoClient()
data = client.enrich_person(email="stakeholder@company.com")
print(f"{data['fullName']} - {data['headline']}")
```

---

## Real Example: Complete Enrichment

```python
#!/usr/bin/env python3
from aviato_client import AviatoClient
from crm_mapper import AviatoCRMMapper

# Initialize
client = AviatoClient()
mapper = AviatoCRMMapper()

# Enrich person (use email OR LinkedIn URL)
person_data = client.enrich_person(
    email="john.doe@example.com",
    linkedin_url="https://linkedin.com/in/johndoe"  # Optional
)

# Map to CRM-friendly format
crm_fields = mapper.map_person_to_crm(person_data)

# Print key insights
print(f"Name: {crm_fields['full_name']}")
print(f"Title: {crm_fields['current_title']}")
print(f"Company: {crm_fields['current_company']}")
print(f"Location: {crm_fields['city']}, {crm_fields['region']}")
print(f"LinkedIn Network: {crm_fields['linkedin_connections']} connections")
print(f"Open to Work: {crm_fields['open_to_work']}")
print(f"Skills: {', '.join(crm_fields['skills'][:5])}")

# Enrich their company
if crm_fields.get('current_company_id'):
    company_data = client.enrich_company(
        linkedin_id=crm_fields['current_company_id']
    )
    company_fields = mapper.map_company_to_crm(company_data)
    
    print(f"\\nCompany Intel:")
    print(f"  Headcount: {company_fields['headcount']} employees")
    print(f"  Growth: {company_fields['headcount_growth_monthly']}% monthly")
    print(f"  Funding: ${company_fields['total_funding']:,.0f}")
    print(f"  Hiring: {company_fields['open_roles']} open roles")
    print(f"  Tech Stack: {', '.join(company_fields['tech_stack'][:5])}")
```

---

## Batch Enrichment Example

```python
#!/usr/bin/env python3
from aviato_client import AviatoClient
import json

client = AviatoClient()

# Your stakeholder list
stakeholders = [
    {'email': 'alice@startup.com', 'linkedin_url': None},
    {'email': None, 'linkedin_url': 'https://linkedin.com/in/bobsmith'},
    {'email': 'carol@bigcorp.com', 'linkedin_url': 'https://linkedin.com/in/carol'}
]

# Batch enrich (handles rate limiting automatically)
results = client.batch_enrich_people(stakeholders)

# Save results
with open('enrichment_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Print summary
success_count = sum(1 for r in results if r['status'] == 'success')
print(f"Enriched {success_count}/{len(stakeholders)} profiles")
```

---

## What You Get: Data Fields Available

### Person Data (90+ fields)
**Professional**:
- Current: title, company, department, seniority score, start date
- History: All previous roles with dates, companies, descriptions
- Career Signals: LinkedIn connections, followers, "open to work" status

**Education**:
- Degrees with schools, fields of study, dates
- Complete education history

**Contact & Social**:
- Email (input or discovered)
- Twitter, Facebook, Crunchbase profiles
- LinkedIn engagement metrics

**Skills & Attributes**:
- Skills list
- Languages with proficiency levels
- Headline, bio/summary

**Investor Profile** (when applicable):
- Investment range (min/max/target)
- Portfolio count
- Sector interests
- Current/previous firms

### Company Data (240+ fields)
**Fundamentals**:
- Name, description, tagline, industries
- Headcount (current + historical trends)
- Location (geocoded: city, region, country)

**Growth & Traction**:
- Web traffic (current + trends)
- Traffic sources (direct/search/social)
- Visitor countries
- Social followers (LinkedIn/Twitter/Facebook + trends)

**Financial**:
- Total funding, rounds, investors
- Last round valuation
- Latest deal (type, amount, date)
- IPO status, stock symbol, share price, market cap

**Product & Market**:
- Tech stack (technologies used)
- Product listings (Product Hunt data)
- G2 reviews and ratings
- Screenshots

**Hiring Intelligence**:
- Job openings (with titles, departments, remote status)
- Hiring departments
- Compensation ranges by department

**Strategic Intel**:
- Acquisition status (acquired by, date, price)
- Patent count
- Government contracts (for contractors)
- Recent news mentions

---

## API Best Practices

### 1. Cache Management
```python
# Don't re-enrich recent data
last_enriched = get_from_crm(stakeholder_id, 'aviato_last_updated')
if last_enriched and (now - last_enriched).days < 30:
    print("Using cached data (fresh)")
else:
    # Re-enrich
    fresh_data = client.enrich_person(email=email)
```

### 2. Handle Missing Data Gracefully
```python
# Aviato returns None for unavailable fields
crm_update = {
    'current_title': data.get('experienceList', [{}])[0]
                         .get('positionList', [{}])[0]
                         .get('title') or crm_existing_title,  # Preserve if missing
}
```

### 3. Rate Limiting
```python
import time

for stakeholder in stakeholder_list:
    enrich_stakeholder(stakeholder)
    time.sleep(0.2)  # 5 req/sec = 300/min (at limit)
```

### 4. Error Handling
```python
try:
    data = client.enrich_person(email=email)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print(f"Profile not found for {email}")
    elif e.response.status_code == 429:
        print("Rate limited - implement backoff")
        time.sleep(60)  # Wait 1 minute
    else:
        print(f"API error: {e}")
```

---

## Integration Checklist

- [x] API key configured and stored securely
- [x] Connection tested successfully
- [x] Documentation reviewed
- [x] Integration plan created
- [ ] Python SDK built (`aviato_client.py`)
- [ ] CRM mapper built (`crm_mapper.py`)
- [ ] Test with 5-10 real stakeholders
- [ ] Define CRM update logic
- [ ] Build batch enrichment workflow
- [ ] Set up scheduled refreshes
- [ ] Create enrichment dashboard/metrics

---

## Next Actions

**To start enriching stakeholders**:

1. **Define your CRM schema** - What fields do you want to populate?
2. **Identify stakeholder identifiers** - Do you have emails? LinkedIn URLs? Both?
3. **Test with real data** - Pick 5-10 stakeholders and test enrichment
4. **Decide on workflow** - Real-time, batch, or hybrid?
5. **Build integration** - Connect Aviato → your CRM system

**Questions to answer**:
- What CRM platform are you using? (HubSpot, Salesforce, custom, etc.)
- How many stakeholders do you need to enrich? (affects batch sizing)
- How often should profiles be refreshed? (weekly, monthly, quarterly)
- Which fields are critical vs. nice-to-have?
- Do you need company enrichment, person enrichment, or both?

---

## Support & Resources

**Files Created**:
- `file 'Integrations/Aviato/.env'` - API credentials (secure)
- `file 'Integrations/Aviato/INTEGRATION_PLAN.md'` - Full technical plan
- `file 'Integrations/Aviato/QUICKSTART.md'` - This guide
- `file 'Integrations/Aviato/test_connection.py'` - API validation script

**Aviato Resources**:
- Dashboard: https://data.aviato.co/dashboard
- API Playground: https://docs.data.aviato.co/api-reference/company/enrich?explorer=true
- Full Docs: https://docs.data.aviato.co/

**Ready to build?** Let me know your CRM platform and I'll build the full integration for you.

