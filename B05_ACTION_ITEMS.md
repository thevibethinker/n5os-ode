---
created: 2026-01-20
last_edited: 2026-01-20
version: 1.0
provenance: con_NaE0XWDKGZ9WbDYj
---

### Accounting / Compliance Questions

**Q: For which period are we packaging the Indian finances—January 1 through December?**  
Status: Answered  
Context: RBI wants the annual books and CPA certification for the 2024 run; we need the right calendar year to submit before closing 2025.  
Answer: The team confirmed January 1–December 24 and will deliver the final numbers to the 24th deadline.

**Q: Can you send both the calendar year figures and the Indian fiscal year (April–March) pack?**  
Status: Answered (final data pending)  
Context: The Indian team sometimes closes April–March, so providing both protects us from a mismatch when the accountants review.  
Answer: Vineet confirmed we will deliver both the annual and the fiscal-year outputs once the two or three open line items are resolved after the 31st.

### Loan Documentation Questions

**Q: Do you need the $190,000 loan agreement to process the transaction in the books?**  
Status: Answered (action item)  
Context: The accounting team needs formal documentation to shift the entry from an investment placeholder to a loan liability.  
Answer: Vrijen will drop a draft that makes the change official so the books can be fixed.

**Q: Is the loan interest-bearing or non-interest-bearing?**  
Status: Answered  
Context: Classification changes how it is reported—liability versus equity—and which ledgers it hits.  
Answer: It is non-interest-bearing, so it will be booked as a liability, not income.

**Q: Once you finalize this, do you have any document handy to depict the loan terms?**  
Status: Answered (preparation underway)  
Context: The team wants a paper trail to support the new classification.  
Answer: Vrijen will prepare and drop the supporting document shortly.

### Payroll / Refund Questions

**Q: Is the payroll refund something we have to push through before closing the books, or can it stay open?**  
Status: Answered  
Context: The refund impacts W-2 computation for the U.S. employee and the payroll GL, so it matters for the 2025 close.  
Answer: Vineet advised completing the refund now so the payroll totals and W-2s align before year-end.

**Q: Is it in her interest to cut the refund on such short notice?**  
Status: Answered (reluctant but necessary)  
Context: Vrijen wanted to avoid asking the employee for $4,500 on 24-hour notice but was told the W-2 impact makes it worth doing.  
Answer: The team agreed that the payroll accuracy takes precedence and that higher taxes later would be preferable to mismatched filings.

### Supporting Documentation Questions

**Q: What is the Upwork spend for, and can you send the supporting invoice?**  
Status: Answered (partial)  
Context: The accounting team will likely ask for documentation on large transactions; they need to classify production versus marketing.  
Answer: Vrijen clarified it is video production/marketing; most invoices are available today, but the Upwork submittal will follow when Logan recovers.  

**Q: Do we have supporting documents for NY Weekly News and the other large line items ($3,100, $2,300, $5,000)?**  
Status: Answered (review in progress)  
Context: The acquisition/audited reviewers may demand backup for high-dollar expenses, so the team wanted confirmation they exist.  
Answer: Vrijen is double-checking NY Weekly News and will prioritize gathering the remaining invoices once the link Vineet sends arrives.  

### Product & Monetization Questions (2026-01-12)

**Q: So to clarify, are we delivering a pre-built Zo product (with an automated process and platform cut) or teaching students how to build from scratch?**  
Status: Answered  
Context: Packaging the offering determines pricing, support load, and whether the revenue comes from product access or repeated cohorts.  
Answer: Speigel wants the Zo product as the revenue engine—sell access via a Gumroad/Notion-style storefront with optional teaching on how to customize it, rather than relying solely on repeated cohort instruction.  

**Q: Does Notion let creators charge for templates and similar pre-built workflows?**  
Status: Answered  
Context: We were hunting for an existing monetization model to justify charging for Zo templates instead of only consulting hours.  
Answer: Yes—creators sell templates on Notion, Canva, and Gumroad, so Zo can follow that playbook and keep a platform cut while folks receive premium workflows.  

**Q: Can you think of a decent MVP that charges $10–$30, avoids accounts/auth, and simply returns a session-based output after Stripe payment?**  
Status: Unanswered (Action item)  
Context: Vrijen is cautious about engineering authentication and state management, so a stateless MVP would let us launch faster while still monetizing career/productivity coaching.  
Answer: TBD  

### Implementation & Zo Questions (2026-01-12)

**Q: Does the solution require persistent state, or can we treat each run as a session that clears when the browser refreshes?**  
Status: Answered  
Context: Choosing a session-only architecture avoids the complexity of storing private data and reduces security concerns for the first release.  
Answer: Vrijen confirmed we can keep everything in the session—once the browser refreshes, the inputs clear, so we should design around session-based flows until we have a reason to add persistence.

### Questions Raised (2026-01-15 Chat)

#### Product & Integration Questions

**Q: Which tab should I be looking at?**  
Status: Answered  
Context: Tiffany was trying to follow along on the shared sheet while Vrijen pulled up the data-partnership columns.  
Answer: Vrijen was loading the correct tab and reminded Tiffany it had been shared to his personal account so she could reference it.

**Q: What do these data integrations actually look like from a product perspective?**  
Status: Answered  
Context: Tiffany needed a concise narrative to fill the spreadsheet and explain the partner value when pushing integrations.  
Answer: Vrijen framed the partnerships as prebuilt recipes (CRM, trading bot, LinkedIn workflows) where Zo users pick a template, plug in partner APIs, and gain automation plus access to partner data as a subscription, while partners earn new customers through Zo.

**Q: Where does the revenue stream land for Zo and the data partners?**  
Status: Answered  
Context: Tiffany wanted to understand monetization before ranking partners so the team could pitch the right model.  
Answer: Vrijen said the partners are exhausted enterprise channels and are chasing consumer subscriptions; Zo can package the data, resell access, and drive traffic back to partners, creating subscription revenue and referral value.

**Q: What does the Nine integration look like?**  
Status: Answered  
Context: Tiffany was clarifying whether Nine was the same kind of CRM data as Aviato before annotating the sheet.  
Answer: Vrijen explained Nine surfaces human and investment history for due diligence, so users can prep richer notes before meetings and investors can shorten their prep time.

**Q: What is the implementation plan with Calendly?**  
Status: Answered  
Context: Tiffany was populating the implementation column and needed the workflow that ties Calendly into Zo.  
Answer: Vrijen described tying into the Calendly API so Zo can map natural-language requests to the right invite, alert on new bookings, enrich leads with Aviato, and automate follow-ups.

**Q: Would Condo also let Zo send LinkedIn messages, or is it read-only?**  
Status: Answered (needs validation)  
Context: Tiffany was curious whether the LinkedIn messaging partner could both surface history and allow outbound replies.  
Answer: Vrijen believes so but has not tried it; he planned to test the webhook flow and send a message to confirm write capability.

#### Product & Experimental Use Cases

**Q: What would a blockchain/data play like Dune look like inside Zo?**  
Status: Answered  
Context: Tiffany wanted to keep the “make money” compass but needed a concrete experience to add to the list.  
Answer: Vrijen said it would look like building trading/news bots or curated DD feeds where users spot trends, track shifts, and coordinate community insight inside Zo instead of scattered tools.

#### Onboarding & User Research Questions

**Q: What have folks told you about their first moment inside Zo, and is there a file-structure story that helps with the blank slate?**  
Status: Unanswered (Action item: capture whatever file-structure or onboarding experiments Ben/PMs are vetting and summarize the plan).  
Context: Vrijen raised the onboarding pain point from user research, and Tiffany looped Ben in live but no concrete answer surfaced.  
Answer: TBD—product needs to document any small experiments (e.g., default folders, desktop metaphors) and share before the next partner push.

**Q: What exact solution is Zo considering to make the new-user workspace less overwhelming beyond the greeting prompt?**  
Status: Unanswered (Action item: follow up with Ben/PM for the specific next steps they are testing so we can reference a decision).  
Context: Tiffany asked Ben in the moment whether anything specific was in flight after highlighting the blank workspace, but the defense was limited to “we can do more.”  
Answer: TBD—need a concrete proposal (default files, animated transition, or onboarding story) to reference in future asks.



### B05 Questions (2026-01-15 Debrief on Selling Careerspan from Ray)

#### Buyer Interest & Positioning Questions

**Q: What is the interest from the Calendly person—more you and your skills, or a strategic product angle?**  
Status: Answered  
Context: We needed to know whether to frame this inbound lead as a talent acquisition or a product/tech opportunity so the pitch and diligence focus correctly.  
Answer: The Calendly conversation is primarily about me, my skills, and the team rather than the platform, so we keep the emphasis on the people side unless stronger product demand emerges.

**Q: Would Calendly have any need for the tech, or is this purely a talent story?**  
Status: Answered  
Context: Understanding whether to highlight product demos versus personal expertise helps us prioritize what to prepare for each outreach.  
Answer: It feels like a pure talent move—if concrete tech interest surfaces, we can reintroduce the platform later, but for now we sell the people and the mission expertise.

#### Deal Structure & Strategy Questions

**Q: Is there anything essential we should know before we start selling—the dos, the don’ts, and early pitfalls to avoid?**  
Status: Answered  
Context: We wanted a checklist from someone who’s navigated a tight exit so we do not repeat mistakes and treat this like a confident sales process.  
Answer: Treat it like a sales funnel—stay skeptical until a yes is real, cultivate at least two live bids, time conversations so negotiations land simultaneously, understand asset vs. share structures, talk to a lawyer, and be ready to compare scenarios that mix upfront cash with earnouts.

**Q: How much have you raised so far?**  
Status: Answered  
Context: Buyers view the cap table and funding mix when sizing risk and knowing whom to keep in the loop during diligence.  
Answer: Roughly $1M of equity plus another $200K–$300K of founder-provided debt.

**Q: Is that a mix of family, friends, and angels instead of institutional capital?**  
Status: Answered  
Context: Institutional investors may require approvals, so we needed to know if any bureaucratic blockers exist.  
Answer: It’s non-institutional—mostly family office and angel support, with no VC or corporate funds.

**Q: Do you understand the difference between asset purchases and the alternative exit structure that transfers shares?**  
Status: Answered  
Context: Knowing the structure helps us anticipate tax, liability, and transactional complexity before term sheets arrive.  
Answer: Asset purchases are cleaner and license the work, whereas share transfers carry the risk of earnout-heavy structures; buyers will push to tie value to earnouts while we push for cash, so walk through both paths with counsel.

#### Personal Fit & Runway Questions

**Q: What are you optimizing for next, and are you willing to stay tied to the company for multiple years?**  
Status: Answered  
Context: Buyers need clarity on the founders’ availability post-deal to plan integration and talent retention.  
Answer: Logan and I expect one of us (likely me) to stay, but we want to cap obligations at roughly a year so I keep flexibility while ensuring the head of AI lands in a good spot.

**Q: From a cash perspective, how urgent is this? How much runway do you have?**  
Status: Answered  
Context: Runway determines how much leverage we retain—if the pressure is high, we need to be cautious about accepting symbolic offers.  
Answer: There is roughly a three-month window before the situation becomes untenable, so we are motivated but still working to keep multiple conversations alive so we avoid single lowball outcomes.

**Unanswered questions/action items:** None this round—every question surfaced during the call received a response.

