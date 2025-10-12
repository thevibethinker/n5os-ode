```markdown
# Accuracy Boundaries Assessment

**Purpose:** Define what inferences are acceptable vs. unacceptable in meeting prep digests  
**Method:** Rate actual statements from test output  
**Rating Scale:**
- ✅ **ACCEPTABLE** — Reasonable inference given available data
- ⚠️ **BORDERLINE** — Needs refinement or qualification
- ❌ **UNACCEPTABLE** — Speculation masquerading as fact

---

## Category 1: Historical Relationship Assumptions

### Statement 1A
**What system said:**  
"This appears to be first substantive meeting based on limited email history"

**Data available:**
- 2 Gmail results from Oct 1-2 (calendar acceptance + scheduling confirmation)
- Gmail API returns max 3 results
- No knowledge of history before Oct 1

**Rating:** ❌


**Your notes:**
Way too simplistic an assumption that limited history implies limited history. Checking a limited number of interactions does not mean there is actually limited history. Additionally, let's see if you can get the API limit to return more results or search for more results. It feels like you used a Python script here instead of an LLM, which is why the result came out so poor.

---

### Statement 1B
**What system said:**  
"No prior email history suggests this may be initial connection or referral-based meeting"

**Data available:**
- 0 Gmail results found for epak171@gmail.com
- Gmail domain (personal email)
- No calendar description

**Rating:** ❌


**Your notes:**


---

## Category 2: Strategic Context & Objectives

### Statement 2A
**What system said:**  
"You mentioned wanting to 'figure out how we can supercharge this for mutual benefit'"

**Data available:**
- Direct quote from actual Gmail thread (Oct 11)
- Verifiable fact from email content

**Rating:** ❌



**Your notes:**
It's a shitty quote with no context and nothing of real value conveyed

---

### Statement 2B
**What system said:**  
"Active partnership discussion ongoing"

**Data available:**
- 3 Gmail exchanges Oct 11 showing back-and-forth about PM communities, FOHE pilot
- Calendar meeting scheduled
- Recent engagement (same week)

**Rating:** ❌

**Your notes:**
It's a shitty quote with no context and nothing of real value conveyed

---

### Statement 2C
**What system said (in prep actions):**  
"Prepare specific asks about partnership acceleration"

**Data available:**
- Email context shows partnership discussion
- No explicit calendar description with meeting purpose
- System inferred "acceleration" as objective

**Rating:** ❌

**Your notes:**


---

## Category 3: Meeting Characterization

### Statement 3A
**What system said (BLUF):**  
"Connect with Michael Maher to michael maher x vrijen"

**Data available:**
- Calendar title: "Michael Maher x Vrijen"
- No description
- System just repeated title in lowercase

**Rating:** ___

**Your notes:**


---

### Statement 3B
**What system said (BLUF):**  
"Connect with Fei (Nira) to discuss partnership progress and next steps"

**Data available:**
- Calendar title: "Vrijen Attawar and Nira Team"
- Gmail shows partnership discussion with updates/questions
- System inferred "progress and next steps"

**Rating:** ___

**Your notes:**


---

### Statement 3C
**What system said:**  
"Consider: What value are you getting from this community? Any specific connections to pursue?"

**Data available:**
- Group event with 100+ attendees
- Recurring monthly community meeting
- No prior context about V's engagement level

**Rating:** ___

**Your notes:**


---

## Category 4: Stakeholder Characterization

### Statement 4A
**What system said:**  
"Fei is engaged and enthusiastic based on recent exchange"

**Data available:**
- Fei wrote "awesome ! Look forward" in response
- Proactively asked "anything new?" before meeting
- Two positive engagement signals

**Rating:** ___

**Your notes:**


---

### Statement 4B
**What system said:**  
"Michael is MBA Career Advisor - Tech at Cornell SC Johnson College of Business"

**Data available:**
- Email signature or LinkedIn data (implied)
- Verifiable fact about role

**Rating:** ___

**Your notes:**


---

### Statement 4C
**What system said:**  
"Gmail domain indicates individual (not corporate)"

**Data available:**
- Email: epak171@gmail.com
- Observable fact about domain

**Rating:** ___

**Your notes:**


---

## Category 5: Prep Actions (Generic)

### Statement 5A
**What system said (for every meeting):**  
"Review last interaction and prepare 1-2 specific asks"

**Data available:**
- Generic advice applied uniformly
- Not customized to meeting context
- No specific strategy proposed

**Rating:** ___

**Your notes:**


---

### Statement 5B
**What system said (for every meeting):**  
"Set explicit outcome: what decision or next step do you need?"

**Data available:**
- Generic advice applied uniformly
- Outcome-focused framing
- No specific outcome proposed

**Rating:** ___

**Your notes:**


---

## Category 6: Summary Statements

### Statement 6A
**What system said:**  
"Back-to-back meetings from 3:00-5:30pm with only 30-min breaks. Consider energy management and transition time."

**Data available:**
- Calendar shows: 15:00, 15:30, 16:00, 17:00 meetings
- Calculated from timestamps
- Practical observation about schedule density

**Rating:** ___

**Your notes:**


---

### Statement 6B
**What system said:**  
"**Nira meeting** has most context and active momentum - prepare specific asks about partnership acceleration"

**Data available:**
- Nira has 3 recent emails with substantive content
- Others have 0-2 emails
- System prioritized based on available context depth

**Rating:** ___

**Your notes:**


---

### Statement 6C
**What system said:**  
"**Elaine P** - understand meeting context (who made intro? what's the objective?)"

**Data available:**
- No email history
- No calendar description
- System flagged as needing clarification

**Rating:** ___

**Your notes:**


---

## Additional Statements to Rate

**Add any other statements from the digest that you think illustrate boundary questions:**

### Custom 1
**What system said:**  


**Data available:**


**Rating:** ___

**Your notes:**


---

## After Rating: Pattern Analysis

Once you've rated these, I'll analyze patterns to create rules like:

**Example rules that might emerge:**
- ✅ "Quote directly from emails when attributing statements"
- ✅ "Observe factual characteristics (domain type, scheduling patterns)"
- ⚠️ "Characterize relationship status with qualifier: 'appears to be' or 'limited history suggests'"
- ❌ "Never claim 'first meeting' or 'initial connection' without verification"
- ❌ "Never infer specific strategic objectives unless explicitly stated in calendar/email"

---

**Instructions:**
1. Rate each statement using the scale (✅ / ⚠️ / ❌)
2. Add notes explaining your reasoning
3. Add any additional problematic statements you notice
4. I'll convert your ratings into explicit accuracy rules
```