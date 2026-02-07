---
created: 2026-02-02
last_edited: 2026-02-02
version: 3
provenance: con_NLOu2MVInIYnuwuf
---
# Careerspan Candidate Tracker - Schema Status

**Base:** Careerspan Candidate Tracker (`appd12asvg42woz9I`)

## ✅ Schema Complete (2026-02-02)

All required fields are present across all three tables.

| Table | Status | Field Count |
|-------|--------|-------------|
| Job Openings | ✅ Complete | 30+ fields |
| Candidates | ✅ Complete | 20+ fields |
| Employers | ✅ Complete | 20+ fields |

---

## Field Name Mappings

Some fields use slightly different names than originally specified. Use these actual names in scripts:

### Job Openings Table

| Spec Name | Actual Name | Notes |
|-----------|-------------|-------|
| Geography | `Location` | Repurposed — options: NY, SF, Bangalore, Hyderabad, Remote |
| ✓ Salary Range | `Salary Range (Checkbox)` | Checkbox with (Checkbox) suffix |
| ✓ Salary Visibility | `Salary Visibility (Checkbox)` | Checkbox with (Checkbox) suffix |
| ✓ Location/Geo | `Location/Geo (Checkbox)` | Checkbox with (Checkbox) suffix |
| ✓ Visa/Sponsorship | `Visa/Sponsorship (Checkbox)` | Checkbox with (Checkbox) suffix |
| ✓ 90-Day Success | `90-Day Success (Checkbox)` | Checkbox with (Checkbox) suffix |
| ✓ Anti-Pattern | `Anti-Pattern (Checkbox)` | Checkbox with (Checkbox) suffix |
| Salary Hidden | `Salary Hidden (Checkbox)` | Checkbox with (Checkbox) suffix |

### Single Select Field Options (Verified)

**Location (Geography):** Remote, Bangalore, Hyderabad, SF, NY  
**Intake Status:** New, Awaiting Employer Response, Round 2, Finalized, Ready for Careerspan, Active, Paused, Closed  
**Ball In Court:** Zo, Shivam, Employer, V  
**Careerspan Sync Status:** Not Added, Pending, Added, Error  
**Source Tag:** [JD], [INTEL], [RESUME]  
**Visa Sponsorship:** Yes, No, Unknown  

---

## Config Update Required

Update `config.yaml` to reflect actual field names if accessing via API:

```yaml
# Field name mappings for Airtable API
field_mappings:
  geography: "Location"  # Repurposed field
  salary_range_checked: "Salary Range (Checkbox)"
  salary_visibility_checked: "Salary Visibility (Checkbox)"
  location_geo_checked: "Location/Geo (Checkbox)"
  visa_checked: "Visa/Sponsorship (Checkbox)"
  ninety_day_checked: "90-Day Success (Checkbox)"
  anti_pattern_checked: "Anti-Pattern (Checkbox)"
```

---

*Schema verified complete 2026-02-02*
