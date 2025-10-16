# Processing Error Log

**Meeting ID:** 2025-10-13_internal-team  
**Request File:** 2025-10-13_internal-team_request.json  
**Error Date:** 2025-10-16 05:07 ET  
**Error Type:** Excluded Meeting Type + No Substantive Content

## Reason for Exclusion

This meeting request was moved to failed/ for the following reasons:

### 1. **Excluded Meeting Type**
- Classification: `INTERNAL_TEAM` 
- Per `file N5/config/stakeholder_rules.json`, internal team meetings are excluded from stakeholder processing
- Rationale: Internal Careerspan team standups don't require full stakeholder intelligence workflow

### 2. **No Substantive Content**
- Transcript consists entirely of Fireflies bot testing
- No strategic decisions, commitments, or stakeholder intelligence to extract
- Sample content: Testing basic math queries to Fireflies ("what's 1 trillion minus 1?")

### 3. **Incomplete Registry Definition**
- Registry references `INTERNAL_STANDUP_TEAM` with blocks B40-B48
- These blocks are not defined in `file N5/prefs/block_type_registry.json` v1.5
- Internal meeting processing system appears incomplete

## Transcript Summary

**Participants:** Ilse Funkhouser, Fireflies AI Notetaker (Logan)  
**Duration:** ~3 minutes  
**Content:** Testing Fireflies bot functionality with basic queries

## Recommendation

**Option 1:** If internal standup processing is needed:
- Define B40-B48 blocks in block_type_registry.json
- Create simplified workflow for internal meetings (focus on action items, not CRM/Howie integration)

**Option 2:** Continue excluding internal meetings:
- Update webhook/request generator to filter out internal meetings before creating requests
- Detection criteria: participants from mycareerspan.com domain only, or explicit "internal" classification

## Files Created

- Transcript downloaded: `file N5/inbox/transcripts/2025-10-13_internal-team_converted.txt`
- Error log: This file
- Request file will be moved to failed/ folder

---

**Status:** ❌ Not processed (excluded type, no substantive content)
