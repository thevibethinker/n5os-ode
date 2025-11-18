---
created: 2025-11-11
last_edited: 2025-11-14
version: 1.0
---

# Outstanding Questions & Ambiguities

## Product & Technical

### **Employer Portal Detail Pages**
**Question:** Should individual skills/responsibilities have deep-dive detail pages?  
**Context:** Danny deprioritized, Ilse saw value as demo enabler, Logan flagged it as interactive conversation starter  
**Ambiguity:** Is the value in having editable/interactive JD for employers, or just visual display?  
**Resolution Path:** Get feedback from early employer users in staging; measure whether they click into details  
**Owner:** Danny (engineering decision), Ilse (product validation)

---

### **Multi-User Employer Accounts**
**Question:** How should multiple team members from same employer collaborate on candidate review?  
**Current State:** Only one user per employer account  
**Logan's Suggestion:** Notes feature for individual reviewers, eventually crowd-source prioritization across team  
**Ambiguity:** Multi-user access model not yet designed; permissions/visibility unclear  
**Resolution Path:** Design doc before Emory deployment (avoid building for one-off case)  
**Owner:** Ilse (product), Danny (engineering)

---

### **Candidate Ranking/Reordering**
**Question:** Should employers be able to re-rank candidates or reorder skills by importance?  
**Context:** Logan's visual instinct seeing the skills list  
**Current Capability:** Display-only; no reordering  
**Ambiguity:** Is this conversation starter vs. core feature?  
**Resolution Path:** Track UX behavior in staging (do users try to drag/reorder?); iterate if needed  
**Owner:** Danny (engineering), Logan (UX feedback)

---

### **BS Detection Deployment & Cost**
**Question:** What's the maximum acceptable per-user cost for fraud detection?  
**Context:** Current cost $0.20-0.30 per user (5+ stories); came down from $1/user  
**Ambiguity:** Pricing model may change with volume; margin impact not yet modeled  
**Resolution Path:** Model cost-per-hire scenario, compare against customer LTV  
**Owner:** Ilse (technical), Logan/Vrijen (business metrics)

---

### **Email Domain Configuration**
**Question:** Who has access to DNS records / domain registrar for Careerspan domain?  
**Context:** Email verification needed for Firebase password reset  
**Current State:** Danny mentioned Vrijen and Ilse likely have access  
**Ambiguity:** Unclear if this is a known blocker or surprise discovery  
**Resolution Path:** Danny confirms needed DNS records, Vrijen/Ilse provide domain registrar credentials  
**Owner:** Danny (request), Vrijen/Ilse (execution)

---

## Go-to-Market & Positioning

### **Narrative Framing: "Moonshot" vs. "Strategic Integration"**
**Question:** What's the right framing of Careerspan for Darwin Box and similar acquirers?  
**Context:** Vrijen positioned it as "moonshot" in a boring company's wheelhouse; Logan pitched "internal mobility" angle  
**Ambiguity:** Different team members may have different mental models of value prop  
**Resolution Path:** GTM refinement work (Ilya + Ilse) should produce canonical messaging  
**Owner:** Ilya (primary), Ilse (validation), Vrijen (final approval)

---

### **Internal Mobility as Primary vs. Secondary Angle**
**Question:** Should Careerspan pivot to emphasize internal mobility over external recruitment?  
**Context:** Logan discovered it resonates with enterprise acquirers; original positioning was external candidate matching  
**Ambiguity:** Is this a GTM reframe or fundamental product direction?  
**Resolution Path:** Test with Darwin Box conversation early next week; gather more acquirer feedback  
**Owner:** Logan (strategy), Vrijen (CEO decision)

---

### **Customer-Facing Language for Non-Technical Buyers**
**Question:** How do we describe Careerspan's AI/matching capability to non-technical audiences?  
**Context:** Ilya struggling to find compelling descriptors beyond technical explanations  
**Ambiguity:** What's the "dazzling" way to explain matching without buzzwords?  
**Resolution Path:** Ilya iteration + team review (probably Tuesday/Wednesday)  
**Owner:** Ilya (wordsmithing), team (feedback)

---

### **Video Production: Demo Data vs. Customer Data**
**Question:** Does animated video need to use customer's real job description and candidates, or is demo data acceptable?  
**Context:** Ilya clarified that realistic demo data is sufficient (common industry practice)  
**Ambiguity:** Are there specific customer use cases we should showcase first?  
**Resolution Path:** Finalize storyboard before animator starts; lock messaging before animation locks it in  
**Owner:** Ilya (storyboard), Logan (use case selection)

---

## Acquisition & Business Strategy

### **Timing of Acquisition Conversations**
**Question:** Is 5-7 day pause before Darwin Box follow-up the right call?  
**Context:** Vrijen advocated for "no rush" narrative; Ilse wanted more time for refining GTM  
**Ambiguity:** Could delay hurt momentum? Or is breathing room strategically essential?  
**Resolution Path:** Re-evaluate Tuesday if Darwin Box signals urgency; otherwise, proceed as planned  
**Owner:** Vrijen + Logan (joint decision)

---

### **Negotiation Readiness: When Do We Involve Ilya?**
**Question:** At what stage of acquisition conversation should Ilya join for defensive support?  
**Context:** Ilya expressed caution about early involvement; prefers debrief analysis phase  
**Ambiguity:** Is current plan (debrief only) best, or should Ilya observe later-stage conversations?  
**Resolution Path:** Weekly briefing will establish rhythm; Ilya can assess engagement level call-by-call  
**Owner:** Ilya + Logan (joint decision, made in call)

---

### **Valuation & Asking Price**
**Question:** What's our target valuation or price range for acquisition?  
**Context:** Ilya warned against lowballing but also cautioned against overvaluation (Groupon example)  
**Ambiguity:** No explicit ask price discussed; timing of price discussion unclear  
**Resolution Path:** Ilya to develop pricing strategy before Phase 2 conversations advance  
**Owner:** Vrijen (CEO), Ilya (strategy), Logan (execution)

---

### **Competitive Threats or Other Buyers**
**Question:** Are Darwin Box and the 15-20 targets the full addressable buyer base, or are there other acquirers?  
**Context:** Logan mentioned DAO and others "still cooking"; Vrijen holding back details  
**Ambiguity:** How many serious conversations are actually in pipeline vs. exploratory?  
**Resolution Path:** Weekly briefing will provide transparency; Ilya to help evaluate each  
**Owner:** Logan (pipeline management), Vrijen (strategy)

---

### **Impact on Product Development During Acquisition**
**Question:** How much bandwidth should acquisition conversations consume vs. product work?  
**Context:** Not explicitly discussed, but Danny mentioned he's heads-down on GTM page 18; Logan taking 5-10 targets/week  
**Ambiguity:** No explicit allocation or trade-off framework established  
**Resolution Path:** Track in weekly briefing; escalate if acquisition work is blocking Emory or other ship dates  
**Owner:** Vrijen (CEO pacing), team (reporting)

---

## Execution & Logistics

### **Animator Selection Timeline**
**Question:** Can animator be selected and briefed in time to hit production schedule?  
**Context:** 3-6 day delivery lead time; storyboard needs to be locked first  
**Ambiguity:** Is storyboard ready today, or does it slip another day or two?  
**Resolution Path:** Ilya to complete storyboard by end of week; Logan starts animator outreach in parallel  
**Owner:** Logan (execution), Ilya (dependency)

---

### **Rockle's Role in Demo Designs**
**Question:** Is Rockle (mentioned as not attending because "moving somewhere fancy") still involved in design work?  
**Context:** Ilse referenced "Rockle's designs" for deal breaker review; Rockle no longer at company  
**Ambiguity:** Who owns design iteration if Rockle has left?  
**Resolution Path:** Clarify with Ilse; identify new design owner if needed  
**Owner:** Ilse (clarification)

---

### **Ilya's 1-on-1 with Vrijen**
**Question:** What's the agenda for Ilya + Vrijen sync later today/tomorrow?  
**Context:** Vrijen mentioned "operations update" but no specific topics  
**Ambiguity:** Is this team/headcount, strategy, or something else?  
**Resolution Path:** Vrijen and Ilya to align on agenda separately  
**Owner:** Vrijen + Ilya

---

## Areas of Potential Misalignment

### **Employer Portal Scope**
- **Danny's view:** Stop at MVP; detail pages are "unproven"
- **Ilse's view:** Detail pages could be good conversation starter
- **Logan's view:** Reordering capability might be visual misunderstanding vs. actual feature need
- **Resolution needed:** User testing in staging (not design debate)

---

### **Acquisition Priority**
- **Vrijen's view:** Strategic but not desperate; take time to refine narrative
- **Logan's view:** Momentum matters; want to stack conversations back-to-back
- **Ilya's view:** Careful, defensive stance; don't rush into unfavorable terms
- **Resolution needed:** Clarify go/no-go decision-making framework upfront

---

### **GTM Messaging**
- **Ilya's view:** Customer-facing language needs major refinement; messaging should be "dazzling"
- **Ilse's view:** Product itself speaks for itself; messaging refinement is nice but not blocking
- **Logan's view:** Internal mobility angle may resonate better than original narrative
- **Resolution needed:** Publish canonical messaging by end of week (Ilya deliverable)

---

## Flagged Items for Follow-Up

| Item | Priority | Owner | Next Action |
|------|----------|-------|------------|
| Email domain verification | 🔴 Blocker | Danny | Research needed, credentials request to Vrijen/Ilse |
| GTM language finalization | 🟡 High | Ilya | Complete by end of week (Fri) |
| Video storyboard lock-in | 🟡 High | Ilya | Complete by tomorrow or Thursday |
| Animator selection | 🟡 High | Logan | Start outreach by tomorrow AM |
| Darwin Box materials prep | 🟡 High | Vrijen | Prepare by end of week |
| Multi-user account design | 🟡 Medium | Ilse + Danny | Before Emory deployment (if needed) |
| Acquisition debrief rhythm | 🟡 Medium | Logan | Establish weekly cadence starting Tue |
| BS detection dashboard integration | 🟡 Medium | Ilse + Danny | End of week |

