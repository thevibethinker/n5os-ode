# INTERNAL_DECISIONS

---

## Strategic Decisions

| ID | Decision | Type | Rationale | Related Tactical |
|----|----------|------|-----------|------------------|
| D1 | Don't over-index on salary filtering | Product | Salary is not the primary driving force for job selection; adds complexity without proportional value. B2B focus means company-driven matches matter more. | T1 |
| D2 | Prioritize B2B company-driven workflow over B2C complexity | Product | Reduces relevance of complex B2C filtering (salary, location); aligns with business model direction | T1 |

---

## Tactical Decisions

| ID | Decision | Type | Rationale | Supports Strategic |
|----|----------|------|-----------|-------------------|
| T1 | Continue game plan migration (remove target_job field, align role_match_score with role_preferences) | Product | Cleaner architecture, saves money, more flexible matching | D1, D2 |
| T2 | Keep salary as text input (not bands) but adjust filtering weight | Product | Captures nuanced requirements (role-dependent salary expectations) while parsing once per user, not per job | D1 |
| T3 | Delay AI confidence and gender feature releases | Product | Game plan migration is higher priority for system stability | T1 |

---

## Holistic Pushes

**Initiative**: Game Plan Migration Completion  
**Strategic Rationale**: [D1, D2] Simplify architecture, reduce costs, align with B2B direction  
**Tactical Execution**: [T1] Complete migration → [T3] Delay other features → Test in production  
**Dependencies**: Danny's backend work, migration scripts  
**Success Criteria**: Production migration complete, role matching works correctly with role_preferences

---

## Resolved Tactical Debates

**Debate**: Should salary requirements be text input (semantic parsing) vs. structured bands?

**Positions**:
- Danny: Bands are cheaper/easier to filter (no AI parsing needed)
- Ilse: Text input captures nuanced requirements (role-dependent salary expectations)

**Resolution**: Keep text input [T2]

**Rationale**: 
1. Current user base is small (parsing cost negligible)
2. B2B model means companies pay for vetting 500 candidates (margins work)
3. Text input allows parsing once per user (not per job) for role-dependent salary bands
4. Captures more information that's valuable long-term even if more complex short-term

**Logan's Input**: Don't over-complicate salary; it's not the core value prop and isn't always in job postings. User desperation/flexibility varies over time. [D1]
