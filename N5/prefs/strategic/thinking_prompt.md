# Strategic Thinking Framework
**Mental Models & Decision Frameworks for N5**

**Version:** 2.0  
**Created:** 2025-11-02  
**Updated:** 2025-11-02
**Load When:** Strategic decisions, complex problem-solving, design trade-offs

---

## Purpose

Mental models and frameworks for strategic thinking. Complements planning_prompt (HOW to build) with cognitive tools (HOW to think).

## Core Thinking Modes

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
**Example:** Fixing one script breaks another → Need system-level view

### 3. Inversion

Think backwards from failure to avoid it.

**Steps:**
1. Instead of "How do I succeed?", ask "How do I fail?"
2. List all failure modes
3. Design to avoid them

**When to use:** Risk assessment, robustness design
**Example:** "What makes this unmaintainable?" → Then do opposite

### 4. Analogical Thinking

Transfer patterns from one domain to another.

**Process:**
1. Find structurally similar problem in different domain
2. Extract the pattern/principle
3. Apply adapted version to current problem

**When to use:** Stuck on novel problem, need fresh perspective
**Example:** File system = library → Apply Dewey Decimal thinking (categorization by purpose, not format)

---

## Decision Frameworks

### Eisenhower Matrix (Urgency vs. Importance)

|           | Urgent | Not Urgent |
|-----------|--------|------------|
| Important | Do now | Schedule   |
| Not Important | Delegate | Eliminate  |

**Application in N5:**
- Do now: P0 bugs, user-facing breaks
- Schedule: Technical debt, refactors
- Delegate: Automate with scripts/agents
- Eliminate: Nice-to-haves that complicate

### Cost of Reversal (Bezos Two-Way Door)

Make reversible decisions quickly, irreversible decisions slowly.

**Two-way doors (fast):**
- File organization
- Script language (within reason)
- Log verbosity
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
**Example:** Building new system → Spike → Learn → Iterate

---

## Mental Models Library

### 1. Circle of Competence

Know what you know, know what you don't know.

**Application:**
- Inside circle: Act confidently
- Edge of circle: Learn carefully
- Outside circle: Get help or delegate

**In N5:** AI architecture is outside my circle → Ask V about design decisions

### 2. Margin of Safety

Build buffers against error and uncertainty.

**Application:**
- Estimate 8 hrs? Plan for 10
- Disk usage at 60%? Alert at 70%, act at 80%
- One backup? Keep three

### 3. Opportunity Cost

Choosing X means not choosing Y.

**Application:**
- Building feature A = not building feature B
- Time on refactor = not time on new capabilities
- Complexity added = maintenance cost forever

**Always ask:** "What am I NOT doing by choosing this?"

### 4. Compounding

Small improvements accumulate exponentially.

**Application:**
- 1% better daily = 37x better yearly
- Good habits compound (fast feedback loops)
- Bad habits compound (tech debt)

**Focus on:** Repeating actions, foundational improvements

### 5. Feedback Loops

Output becomes input for next cycle.

**Types:**
- **Reinforcing:** Rich get richer (compound interest, network effects)
- **Balancing:** Thermostat, homeostasis

**Application:**
- Fast feedback = reinforcing loop for learning
- Automated alerts = balancing loop for system health

### 6. Second-Order Thinking

What happens next? And then?

**Steps:**
1. What's the immediate consequence?
2. What happens after that?
3. And then what?

**Example:**
- Add feature → Users want more → Code becomes complex → Maintenance burden grows
- Better to say no early than remove later

### 7. Asymmetry

Risk/reward not equal on both sides.

**Types:**
- **Upside asymmetry:** Small cost, huge potential gain (experiments)
- **Downside asymmetry:** Small mistake, catastrophic result (trap doors)

**Application:**
- Embrace upside asymmetry (cheap experiments)
- Avoid downside asymmetry (trap doors)

### 8. Constraints

Constraints drive creativity.

**Application:**
- 10k char limit forces clarity
- JSONL format forces simplicity
- No database forces clever file usage

**Principle:** Don't fight constraints, use them

### 9. Redundancy

Backup systems for critical functions.

**Types:**
- **Active redundancy:** Both systems running (load balancing)
- **Passive redundancy:** Backup activates on failure

**Application in N5:**
- Git commits (passive redundancy)
- Multiple data sources (active redundancy)
- Backup scripts before major refactors

### 10. Skin in the Game

Having something to lose ensures alignment.

**Application:**
- Use my own tools daily (dog fooding)
- V's system depends on N5 (real stakes)
- Test in production conditions (not just dev)

### 11. Via Negativa

Improvement by subtraction, not addition.

**Principle:** Sometimes the best action is removal.

**Application:**
- Delete dead code (not comment out)
- Remove unused features
- Simplify by removing, not adding abstraction

**When to use:** System feels complex, looking to simplify

### 12. Lindy Effect

The longer something has survived, the longer it's likely to continue.

**Application:**
- Mature tech (SQLite, Python) = safer bet than new framework
- Proven patterns > novel approaches
- Legacy doesn't mean bad; might mean battle-tested

**Caveat:** Doesn't apply to perishable things (food, trends)

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

**Steps:**
1. Divide problem into smaller pieces
2. Solve each piece independently
3. Combine solutions

**When to use:** Large, complex problems
**N5 Example:** P36 Orchestration Pattern applies this

### Working Backwards

Start from desired end state, reverse-engineer path.

**Steps:**
1. Define clear end goal
2. What's the step immediately before that?
3. And before that?
4. Continue until you reach current state

**When to use:** Clear goal, unclear path
**Example:** Want automated reports → Need data → Need collection → Need sources identified

---

## Analysis Patterns

### SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)

**Internal factors:**
- Strengths: What advantages do I have?
- Weaknesses: What limitations exist?

**External factors:**
- Opportunities: What can I leverage?
- Threats: What could go wrong?

**When to use:** Strategic planning, option evaluation

### Pre-Mortem Analysis

Imagine project has failed. Why?

**Steps:**
1. Assume project failed catastrophically
2. Everyone lists reasons why (no criticism)
3. Identify common themes
4. Design to prevent top failure modes

**When to use:** Before starting significant work
**Value:** Surfaces hidden risks teams won't mention in regular planning

### Force Field Analysis

Identify forces helping vs. hindering goal.

**Steps:**
1. Define goal clearly
2. List driving forces (pushing toward goal)
3. List restraining forces (pushing away from goal)
4. Strengthen drivers, weaken restraints

**When to use:** Stuck on problem, unclear why progress is slow

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
- Time spent is gone; only future matters

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
- Ask: "Is this representative or just memorable?"
- Base rates > anecdotes

### Dunning-Kruger Effect

Overconfidence from lack of knowledge.

**Mitigation:**
- Stay in circle of competence
- Measure actual performance
- Seek expert review at edge of competence

### Anchoring Bias

Over-relying on first piece of information.

**Mitigation:**
- Consider multiple references
- Start from different angles
- Use Nemawashi (explore 2-3 alternatives)

---

## Quality Check Frameworks

### Pre-Decision Checklist

Before committing to significant decision:
- ✅ Explored 2-3 alternatives (Nemawashi)
- ✅ Identified trap doors (irreversible aspects)
- ✅ Considered second-order effects
- ✅ Applied relevant mental models
- ✅ Checked for cognitive biases
- ✅ Defined success criteria
- ✅ Estimated cost to reverse

### Mid-Execution Health Check

During long-running work:
- ✅ Still solving the right problem? (Not pivoted unknowingly)
- ✅ Assumptions still valid?
- ✅ On track for objectives?
- ✅ Encountering predicted vs. unexpected issues?
- ✅ Need to invoke OODA loop (re-orient)?

### Post-Decision Review

After completing significant work:
- ✅ Did it work as planned?
- ✅ What surprised us?
- ✅ What would we do differently?
- ✅ Update mental models based on new data
- ✅ Document for future reference

---

## When to Use Which Model

### For Strategic Decisions
- First Principles Thinking
- Cost of Reversal (Two-Way Door)
- Opportunity Cost
- Second-Order Thinking
- Pre-Mortem Analysis

### For Design Choices
- Simple Over Easy (from planning_prompt)
- Constraints
- Margin of Safety
- Systems Thinking
- Via Negativa (simplify by removal)

### For Prioritization
- 80/20 (Pareto)
- Eisenhower Matrix
- Opportunity Cost
- Force Field Analysis

### For Risk Management
- Inversion
- Asymmetry
- Redundancy
- Margin of Safety
- Pre-Mortem

### For Learning/Improvement
- Circle of Competence
- Compounding
- Feedback Loops
- Skin in the Game
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
2. This prompt → Mental models (WHICH models apply)
3. Execute with both in mind

**Example flow:**
1. Problem: Should I refactor or rebuild?
2. Planning prompt says: P37 decision matrix
3. This prompt adds: 
   - Inversion (how do I fail?)
   - Second-Order (what happens next?)
   - Cost of Reversal (is this a trap door?)
   - Pre-Mortem (what could go wrong?)
4. Decide with full context

---

## Meta: Continuous Learning

**Mental models evolve.** 

As patterns emerge:
1. Document what worked
2. Add to this prompt (V approval)
3. Reference in future decisions
4. Pattern becomes automatic

**This document can only be modified by V.**

---

*v2.0 | 2025-11-02 | Expanded with cognitive biases, quality check frameworks, analysis patterns, additional mental models*
