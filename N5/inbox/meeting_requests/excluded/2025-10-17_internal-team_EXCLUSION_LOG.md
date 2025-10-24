# Exclusion Log: 2025-10-17_internal-team

**Processed:** 2025-10-22 18:38 ET  
**Status:** EXCLUDED from processing  
**Reason:** Internal team meeting (stakeholder_rules.json v1.1.0)

## Classification Details

- **Meeting Type:** internal
- **Participants:** Daily team stand-up
- **Source:** Google Drive ID 1U0RIEBjceZUvqgiUXf4dEzZj7moPF2fy
- **Note:** Original filename already marked `[INTERNAL-SKIPPED]`

## Business Rule Applied

Per `file N5/config/stakeholder_rules.json`:

```json
"internal_team": {
  "exclude": true,
  "reasoning": "Internal Careerspan team members",
  "domains": ["mycareerspan.com", "careerspan.com"]
}
```

Internal meetings (daily stand-ups, team coordination, internal discussions) are excluded from the stakeholder intelligence system.

---
