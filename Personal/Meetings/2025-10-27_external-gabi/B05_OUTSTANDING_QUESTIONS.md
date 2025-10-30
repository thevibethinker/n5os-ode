# B05: OUTSTANDING_QUESTIONS

## 1. What causes N5 bootstrap script to break when transferring to clean Zo instances?

**Owner**: Vrijen  
**Needed by**: Before next Gabi session (1-2 days)  
**Blocker type**: UNCLEAR_REQUIREMENT (system dependencies not fully mapped)

**Unblocking action**: Debug bootstrap script to identify:
- Which dependencies/configurations are environment-specific vs transferable
- What directory structure assumptions are being made
- Whether file paths are hardcoded vs relative
- What initialization sequence is required for clean installs

**Impact if delayed**: Cannot complete Gabi's N5 setup. More broadly, this blocks scalability of N5 system to other users. If Vrijen wants to operationalize his "solutions architect" role, the system needs to be reliably transferable.

---

## 2. Should Gabi cancel her Claude subscription now or wait until N5 is fully functional?

**Owner**: Gabi (with input from Vrijen and Logan)  
**Needed by**: After seeing Logan's Claude setup (Wednesday) + after N5 is working  
**Blocker type**: NEEDS_DECISION (comparative evaluation incomplete)

**Unblocking action**: 
1. Gabi meets with Logan on Wednesday to see Claude-based workflows
2. Vrijen completes N5 installation on Gabi's Zo
3. Gabi tests both systems for 1-2 weeks
4. Gabi decides based on: feature parity, workflow fit, cost efficiency

**Impact if delayed**: Gabi continues paying $20/month for underutilized Claude. However, premature cancellation risks losing workflows/data before Zo is proven. Low urgency - a few months of overlap is cheap insurance.

---

## 3. What's the best architecture for secure data bridge between Gabi's two Zo instances (Blue Tulip + personal)?

**Owner**: Vrijen (with "proper engineer to look over it")  
**Needed by**: After basic N5 installation is working (not immediate)  
**Blocker type**: NEEDS_DECISION (security + functionality tradeoff)

**Unblocking action**:
1. Define use cases: What data needs to flow between instances? (Client templates? Personal research? Bidirectional or one-way?)
2. Map security requirements: What must stay isolated? (Client confidential data, personal financial info, etc.)
3. Design bridge architecture: API-based? Scheduled sync? Manual export/import?
4. Get engineer review for security validation

**Impact if delayed**: Gabi operates two completely siloed instances, requiring manual duplication of templates, commands, or workflows she wants in both. Inefficient but not blocking - she can function without the bridge.

---

## 4. Did VATT50 discount code properly apply to Gabi's account?

**Owner**: Vrijen  
**Needed by**: Early next week (low urgency)  
**Blocker type**: WAITING_ON_DATA (needs Zo team confirmation)

**Unblocking action**: Contact Zo team to verify discount configuration. Transcript shows code appeared to work ("applied 50% off"), but Vrijen wants to double-check.

**Impact if delayed**: Gabi might be overpaying for Zo subscription. Financial impact is small (~$9/month difference) but correcting later creates awkwardness. Better to verify now.

---

## 5. What does Logan's Claude system look like, and how does it compare to Zo + N5?

**Owner**: Gabi (gathering information) + Vrijen (interpreting implications)  
**Needed by**: After Gabi's Wednesday meeting with Logan  
**Blocker type**: WAITING_ON_DATA (need Logan session results)

**Unblocking action**: 
1. Gabi meets with Logan Wednesday
2. Gabi reports back on Logan's approach: what's working, what's painful, what's unique
3. Vrijen and Gabi compare: What can Zo+N5 do that Logan's system can't? What's Logan doing that should be adopted?

**Impact if delayed**: Gabi makes infrastructure decision with incomplete information. May invest in Zo+N5 when Claude would have been better fit, or vice versa. This is strategic evaluation, not just tactical comparison.

---

## 6. What's the long-term productization strategy for N5 system?

**Owner**: Vrijen  
**Needed by**: No specific deadline (strategic question)  
**Blocker type**: NEEDS_DECISION (business model + scope)

**Unblocking action**:
1. Document what's currently in N5 system (commands, scripts, workflows)
2. Identify what's Vrijen-specific vs generalizable
3. Define personas: Who else needs this? (AI consultants like Gabi? Founders? Knowledge workers?)
4. Decide model: Open source? Paid template? Professional services? Partnership with Zo?

**Impact if delayed**: Vrijen continues doing one-off custom installations, which doesn't scale. Each new user requires manual setup + troubleshooting. The Gabi onboarding exposed this limitation - system is too complex to "just copy over."

This is the meta-question under all the tactical issues. If N5 is becoming a product, it needs product thinking, not just technical fixes.
