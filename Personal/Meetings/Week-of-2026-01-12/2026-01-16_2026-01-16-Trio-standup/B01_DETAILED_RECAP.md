---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: 074838b3-3b6f-4e5c-a843-858a7d072141
---

# B01 - Detailed Recap

## Meeting Overview
**Date:** 2026-01-16
**Participants:** Vrijen Attawar (V), Ilse Funkhouser
**Duration:** ~5 minutes
**Type:** Product Standup / Feature Demo

## Chronological Summary

### Opening (00:00 - 00:15)
Quick greetings exchanged. Ilse had prepared a document to walk V through new features.

### Document Overview (00:15 - 00:41)
Ilse shared a document with two tabs covering AI functionality. She emphasized critical guardrails:
- **Do not give employers access without explanation**
- **Don't give too many credits** (cost control concern)

### Role-Based Email & Silent Scans (00:41 - 01:44)
Ilse demonstrated:
- Adding email addresses to roles for silent database scans
- Silent scans provide basic candidate information
- Roles must be **published** before scans work
- "Scan database" button checks access permissions first

### Threshold System Explanation (01:44 - 02:30)
Ilse clarified the threshold system:
- **Public mode**: If full analysis score > threshold → candidate gets "hey, you should apply" email
- **Silent mode**: Candidate never knows about the scan
- **Vibe check threshold**: Below this, candidates can't continue to role match
- Old "preferences check" logic has been incorporated

### Auto-Apply Feature (02:30 - 03:10)
Key feature walkthrough:
- Auto-apply works with silent scans
- Candidates are notified if they pass threshold
- Email tone is "tongue in cheek" - literally says "that's their problem now, not yours"
- **Minimum stories**: No limit enforced (but backend cap of 250 days)
- This is being enabled so V can offer it to paying customers

### Scan Safeguards (03:10 - 03:42)
Ilse explained technical safeguards:
- System prevents multiple simultaneous scans on same role
- Without this, scans would "fail in exotic and dumb ways"
- UI shows existing scans with labels like "Careerspan admin auto submission silent database scan"

### CSV Export Status (03:42 - 04:20)
Current state:
- CSV exports currently only show: email address + scores
- V wants more data ("bullshit") in exports
- Ilse acknowledges this but hasn't gotten to it yet
- Candidates who pass threshold get emails with bottom-line recommendations
- Example: "Strong move forward candidate if you can provide light onboarding"

### Value Proposition & Wrap (04:20 - 05:14)
Ilse articulated the goal:
- "You don't need to bother me" → Reduce manual coordination
- V enthusiastically agreed: "This is rock and roll"

V confirmed the goal is reducing friction in the process. Ilse signed off, noting she likely won't be back that day.

## Key Takeaways
1. **Silent scan feature is live** - Employers can scan candidate database without candidates knowing
2. **Threshold system controls visibility** - Multiple layers (vibe check, full analysis, auto-apply)
3. **Cost guardrails in place** - 250 day cap, credit warnings
4. **CSV exports are minimal** - Enhancement needed for richer data
5. **Team moving toward automation** - Reducing V-Ilse coordination overhead
