# Proposed User Rule Addition
**For Auto-Loading Planning Prompt**

Add this to your CONDITIONAL RULES section:

---

**CONDITION:** When building, refactoring, or modifying significant N5 system components (scripts, workflows, infrastructure, automation, architectural decisions) → **RULE:**

```
Load file 'Knowledge/architectural/planning_prompt.md' FIRST before any 
design or implementation work. Apply the design values (Simple Over Easy, 
Flow Over Pools, Maintenance Over Organization, Code Is Free/Thinking Is 
Expensive, Nemawashi). Use Think→Plan→Execute framework. Identify trap 
doors explicitly. Follow 70% Think+Plan, 20% Review, 10% Execute time 
distribution.
```

---

**This replaces your current rule:**
```
CONDITION: When I request building, refactoring, or modifying significant 
system components (scripts, workflows, infrastructure, automation) → RULE: 
Load file 'Knowledge/architectural/architectural_principles.md' FIRST...
```

**New workflow:**
1. Load planning prompt (philosophy)
2. Apply design thinking
3. Load architectural principles index
4. Load 1-2 specific principles as needed (Rule-of-Two)
5. Design → implement → review

---

**Ready to add this rule to your settings?**
