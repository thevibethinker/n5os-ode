# Exclusion Log: 2025-10-15_internal-team

**Processed:** 2025-10-22 18:38 ET  
**Status:** EXCLUDED from processing  
**Reason:** Internal team meeting (stakeholder_rules.json v1.1.0)

## Classification Details

- **Meeting Type:** internal
- **Participants:** Daily team stand-up
- **Source:** Google Drive ID 143nK5I0Y7T6AhhkeYcDLEf2oSa1aemsT

## Business Rule Applied

Per `file N5/config/stakeholder_rules.json`:

```json
"internal_team": {
  "exclude": true,
  "reasoning": "Internal Careerspan team members",
  "domains": ["mycareerspan.com", "careerspan.com"]
}
```

Internal meetings (daily stand-ups, team coordination, internal discussions) are excluded from the stakeholder intelligence system. They should not generate:
- CRM profiles
- Stakeholder blocks
- Weekly review entries
- Meeting intelligence records

## Recommendation

If you need to track internal meeting notes, consider a separate workflow for internal documentation that doesn't go through the external stakeholder processing pipeline.

---

**Next Action:** System will continue to next eligible meeting request (if any).
