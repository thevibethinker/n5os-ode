# Quick Test Prompt - Strategic Partner

**Copy this to new thread:**

---

Hi! I need to test the **Strategic Partner** cognitive engine (Phase 1 MVP).

### Setup
Please read:
- `file 'N5/commands/strategic-partner.md'`
- `file 'N5/scripts/strategic_partner_session.py'`
- `file 'Documents/STRATEGIC-PARTNER-PHASE-1-COMPLETE.md'`

### Run Test
```bash
cd /home/workspace
python3 N5/scripts/strategic_partner_session.py --interactive --mode aggressive --challenge 8
```

### Test Challenge
Paste this when prompted:

**Context:** Careerspan approached by "TalentOS" (HR platform, 500K users) for white-label partnership.

**Opportunity:**
- $50K upfront + 20% rev share
- 10K-15K potential customers (2-3% conversion)
- Decision needed in 2 weeks

**Tension:**
- Pro: Massive distribution, validation, revenue
- Con: No direct customer relationship, low rev share, 3+ months dev time
- Reality: We're focused on B2C/SMB, not enterprise
- Resource: 4-person team, already stretched

**My scattered thinking:**
- Could be breakthrough for scale
- But we need to own customer relationship
- 20% feels low - should be 30-40%?
- What if it distracts from core GTM?
- What about exclusivity? Haven't even asked
- Timing terrible - launching new onboarding
- But 15K customers = instant PMF validation
- Opportunity cost of 3 months is huge
- Should we pursue enterprise at all right now?

**Need:** Stress test aggressively, surface assumptions, identify blind spots, structure decision, clear next actions.

---

### Evaluate

Check that it:
1. Loads N5 context automatically
2. Suggests appropriate mode (aggressive/venture)
3. Applies Careerspan defaults (challenge=7+)
4. Challenges assumptions aggressively (target: 10-15)
5. Identifies blind spots (target: 3-5)
6. Detects contradictions (enterprise vs. B2C)
7. Generates session synthesis with quality metrics
8. Stages pending updates (NOT auto-applied)
9. Adds topics to weekly review tracker
10. Provides 4-6 actionable next steps

### Return Results

Provide:
- Evaluation score (items passed / 38 total)
- Quality metrics (insights, assumptions, blind spots count)
- Key excerpts showing challenge quality
- File verification (synthesis, pending updates, topics)
- What worked well / needs improvement

Full evaluation criteria in `file 'Documents/STRATEGIC-PARTNER-TEST-EXPORT.md'`

---

**Pass threshold: 30/38 items ✓**
