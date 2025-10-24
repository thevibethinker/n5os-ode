# Founder Intake → Tuned Weights (Worked Example, v0.1)

Role/Stage: Founding Engineer — Seed
Pass threshold: 0.72 (unchanged)

Founder inputs (one-pager):
- Must-win strengths (90 days): Ownership, Systems, Speed
- Top risks (6 months): Shipping thin verticals; reliability under load
- Team complement: Strong PM partnership; decent comms; need deeper systems
- Evidence preference: Portfolio/work samples before live interviews
- AI posture: Useful but not mandatory (overlay off by default)

Base weights (rubric.fe.seed.v1.json):
- Ownership 0.14, Speed 0.10, Systems 0.12, Product Sense 0.10, Collaboration 0.08,
  Communication 0.08, Technical Depth 0.12, Craft 0.10, Resilience 0.06 (sum=1.00)

Adjustment logic:
- Boost Ownership (+0.02) and Systems (+0.02), modest boost to Speed (+0.01)
- Reduce lower-priority areas pro-rata (Collab, Comm, Craft)

Resulting tuned weights (normalized):
- Ownership 0.16, Speed 0.11, Systems 0.14, Product Sense 0.10, Collaboration 0.07,
  Communication 0.07, Technical Depth 0.12, Craft 0.09, Resilience 0.06 (sum=1.00)

JSON patch (conceptual):


Apply via overlay or manual edit to rubrics/rubric.fe.seed.v1.json.
