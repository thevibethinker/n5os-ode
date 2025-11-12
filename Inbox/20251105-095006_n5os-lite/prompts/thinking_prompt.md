# Strategic Thinking Framework
**Mental Models & Decision Frameworks**

**Version:** 1.0 (N5OS Lite)  
**Created:** 2025-11-03  
**Load When:** Strategic decisions, complex problem-solving, design trade-offs

---

## Purpose

Mental models and frameworks for strategic thinking. Complements planning_prompt (HOW to build) with cognitive tools (HOW to think).

##

 Core Thinking Modes

### 1. First Principles Thinking

Break down to fundamental truths, rebuild from there.

**Steps:**
1. Identify and challenge assumptions
2. Break down problem to basic elements
3. Create new solutions from ground up

**When to use:** Novel problems, questioning existing approaches  
**Example:** "What if we didn't need a database?" → Can file system suffice?

### 2. Systems Thinking

Understanding interconnections and feedback loops.

**Key concepts:**
- Everything connects to everything
- Actions have delayed effects
- Optimize for system, not components
- Find leverage points

**When to use:** Complex interdependencies, unexpected behaviors

### 3. Inversion

Think backwards from failure to avoid it.

**Steps:**
1. Instead of "How do I succeed?", ask "How do I fail?"
2. List all failure modes
3. Design to avoid them

**When to use:** Risk assessment, robustness design

### 4. Analogical Thinking

Transfer patterns from one domain to another.

**Process:**
1. Find structurally similar problem in different domain
2. Extract the pattern/principle
3. Apply adapted version to current problem

**When to use:** Stuck on novel problem, need fresh perspective

---

## Decision Frameworks

### Cost of Reversal (Two-Way Door)

Make reversible decisions quickly, irreversible decisions slowly.

**Two-way doors (fast):**
- File organization
- Script language (within reason)
- Variable naming

**One-way doors (slow - trap doors):**
- Database choice
- Core file format
- API design
- Core architecture

**Rule:** Speed inversely proportional to cost of reversal

### 80/20 (Pareto Principle)

80% of effects come from 20% of causes.

**Application:**
- 20% of features = 80% of value
- 20% of bugs = 80% of pain
- 20% of files = 80% of changes

**Use for:** Prioritization, optimization focus

### OODA Loop (Observe-Orient-Decide-Act)

Iterative decision-making under uncertainty.

**Steps:**
1. **Observe:** Gather data, current state
2. **Orient:** Analyze, apply mental models
3. **Decide:** Choose action based on analysis
4. **Act:** Execute, then loop back to Observe

**When to use:** Dynamic situations, learning as you go

---

## Mental Models Library

### Circle of Competence

Know what you know, know what you don't know.

**Application:**
- Inside circle: Act confidently
- Edge of circle: Learn carefully
- Outside circle: Get help or delegate

### Margin of Safety

Build buffers against error and uncertainty.

**Application:**
- Estimate 8 hrs? Plan for 10
- Disk usage at 60%? Alert at 70%, act at 80%
- One backup? Keep three

### Opportunity Cost

Choosing X means not choosing Y.

**Always ask:** "What am I NOT doing by choosing this?"

### Compounding

Small improvements accumulate exponentially.

**Application:**
- 1% better daily = 37x better yearly
- Good habits compound (fast feedback loops)
- Bad habits compound (tech debt)

### Second-Order Thinking

What happens next? And then?

**Steps:**
1. What's the immediate consequence?
2. What happens after that?
3. And then what?

**Example:**
- Add feature → Users want more → Code becomes complex → Maintenance burden grows

### Asymmetry

Risk/reward not equal on both sides.

**Types:**
- **Upside asymmetry:** Small cost, huge potential gain (experiments)
- **Downside asymmetry:** Small mistake, catastrophic result (trap doors)

**Application:**
- Embrace upside asymmetry (cheap experiments)
- Avoid downside asymmetry (trap doors)

### Constraints

Constraints drive creativity.

**Principle:** Don't fight constraints, use them

### Via Negativa

Improvement by subtraction, not addition.

**Principle:** Sometimes the best action is removal.

**Application:**
- Delete dead code (not comment out)
- Remove unused features
- Simplify by removing, not adding abstraction

### Lindy Effect

The longer something has survived, the longer it's likely to continue.

**Application:**
- Mature tech (SQLite, Python) = safer bet than new framework
- Proven patterns > novel approaches
- Legacy doesn't mean bad; might mean battle-tested

---

## Problem-Solving Patterns

### The Five Whys

Ask "why" five times to find root cause.

**Example:**
1. Why did script fail? → Permissions error
2. Why permissions error? → File ownership wrong
3. Why wrong? → Created by different process
4. Why different process? → Manual intervention
5. Why manual? → No automated setup

**Solution:** Automate setup, don't manually intervene

### Rubber Duck Debugging

Explain problem out loud to find solution.

**Application:**
- Write specification doc (explaining clarifies thinking)
- Document assumptions (forces examination)
- Fresh thread test (explain to new reader)

### Divide and Conquer

Break complex problem into independent subproblems.

### Working Backwards

Start from desired end state, reverse-engineer path.

---

## Analysis Patterns

### Pre-Mortem Analysis

Imagine project has failed. Why?

**Steps:**
1. Assume project failed catastrophically
2. Everyone lists reasons why (no criticism)
3. Identify common themes
4. Design to prevent top failure modes

**When to use:** Before starting significant work  
**Value:** Surfaces hidden risks teams won't mention in regular planning

---

## Cognitive Biases to Watch For

### Confirmation Bias

Seeking information that confirms existing beliefs.

**Mitigation:**
- Actively seek disconfirming evidence
- Steel man opposing views (strongest version)
- Use Inversion (how could I be wrong?)

### Sunk Cost Fallacy

Continuing because of past investment, not future value.

**Mitigation:**
- Focus on future costs/benefits, ignore past
- Ask: "If starting fresh today, would I make this choice?"

### Planning Fallacy

Underestimating time/cost, overestimating benefits.

**Mitigation:**
- Use reference class forecasting (how long did similar projects take?)
- Add margin of safety (1.5-2x initial estimate)
- Track actual vs. estimated to calibrate

### Availability Bias

Overweighting recent or memorable events.

**Mitigation:**
- Gather actual data, not impressions
- Base rates > anecdotes

### Anchoring Bias

Over-relying on first piece of information.

**Mitigation:**
- Consider multiple references
- Start from different angles
- Use Nemawashi (explore 2-3 alternatives)

---

## When to Use Which Model

### For Strategic Decisions
- First Principles Thinking
- Cost of Reversal (Two-Way Door)
- Opportunity Cost
- Second-Order Thinking
- Pre-Mortem Analysis

### For Design Choices
- Simple Over Easy
- Constraints
- Margin of Safety
- Systems Thinking
- Via Negativa (simplify by removal)

### For Prioritization
- 80/20 (Pareto)
- Opportunity Cost

### For Risk Management
- Inversion
- Asymmetry
- Margin of Safety
- Pre-Mortem

### For Learning/Improvement
- Circle of Competence
- Compounding
- OODA Loop

### For Problem-Solving
- Five Whys (root cause)
- Divide and Conquer
- Working Backwards
- Rubber Duck
- Analogical Thinking

---

## Integration with Planning Prompt

**Planning Prompt** (operations) + **Thinking Prompt** (strategic) = Complete approach

**Load order:**
1. Planning prompt → Framework (Think→Plan→Execute)
2. Thinking prompt → Mental models for decision-making
3. Apply both to work

---

*N5OS Lite v1.0 | Extracted and sanitized for demonstration purposes*
