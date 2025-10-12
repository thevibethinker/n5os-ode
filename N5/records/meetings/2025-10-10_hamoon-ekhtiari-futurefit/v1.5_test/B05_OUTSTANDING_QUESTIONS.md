# OUTSTANDING_QUESTIONS

---
**Feedback**: - [ ] Useful
---

## Question 1: What are the 1-2 highest-value embedded use cases that FutureFit would actually use?

**Owner:** Vrijen (with team input)  
**Needed By:** Before drafting use case document (within 2 weeks)  
**Blocker Type:** UNCLEAR_REQUIREMENT  
**Unblocking Action:** Internal brainstorm session with team to evaluate which Careerspan capabilities translate best to embedded widgets. Consider: vibe check, values profiling, resume tailoring, gap analysis. Map each to FutureFit user workflows.  
**Impact if Delayed:** Risk sending use cases that miss the mark or don't align with FutureFit's actual user needs. Could waste Hamoon's time and damage credibility.

## Question 2: What does FutureFit's current tool integration architecture look like technically?

**Owner:** Hamoon (or FutureFit team)  
**Needed By:** Before building use case document (to ensure technical feasibility)  
**Blocker Type:** WAITING_ON_DATA  
**Unblocking Action:** Ask Hamoon directly: "To help me scope the use cases accurately, could you share a quick overview of how embedded tools typically integrate with your platform? (Auth flow, data exchange format, iframe vs. SDK, etc.)"  
**Impact if Delayed:** May propose integration approach that doesn't match their infrastructure. Could add unnecessary technical complexity or require re-scoping.

## Question 3: What specific FutureFit user pain points would benefit from better career profiling?

**Owner:** Hamoon (from his product knowledge)  
**Needed By:** Before drafting use cases  
**Blocker Type:** WAITING_ON_DATA  
**Unblocking Action:** Optional lightweight question in follow-up email: "If you think of specific pain points your users face that Careerspan's tech might address, I'd love to hear them." (Already included in follow-up email draft)  
**Impact if Delayed:** Use cases might be solution-looking-for-problem rather than solving actual FutureFit user pain. Lower chance of adoption.

## Question 4: Is FutureFit open to revenue share models, or do they prefer one-time integration fees?

**Owner:** Both (needs discussion)  
**Needed By:** If partnership progresses to pilot phase  
**Blocker Type:** NEEDS_DECISION  
**Unblocking Action:** Don't raise this in first use case document (too early). But prepare 2-3 commercial model options (rev share, integration fee, free pilot with success metrics) for when feasibility is confirmed.  
**Impact if Delayed:** Could get excited about product fit but then stall on commercial terms. Better to have options prepared.

## Question 5: Does FutureFit have data infrastructure to receive and store Careerspan's structured profile data?

**Owner:** FutureFit (technical capability)  
**Needed By:** If embedded integration moves forward  
**Blocker Type:** DEPENDENCY (technical requirement)  
**Unblocking Action:** Include in use case document: "Required Data Infrastructure" section describing what FutureFit needs to receive (JSON payload structure, data schema, storage requirements). Let them self-assess feasibility.  
**Impact if Delayed:** Could build embedded widget only to discover they can't ingest/store/use the data Careerspan generates. Integration becomes pointless.

## Question 6: What does "operational possibility" actually mean for FutureFit?

**Owner:** Hamoon (clarification needed)  
**Needed By:** To properly scope use cases  
**Blocker Type:** UNCLEAR_REQUIREMENT  
**Unblocking Action:** Interpret based on his comments: "without a ton of cycles" suggests engineering resources are scarce. "Operational possibility" likely means: Can we execute this in next quarter with current team? Frame use cases around minimal integration work.  
**Impact if Delayed:** May over-scope use cases assuming they have more capacity than they do. Gets rejected despite good product fit.
