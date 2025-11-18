---
created: 2025-11-13
last_edited: 2025-11-13
version: 1.0
---

# OUTSTANDING_QUESTIONS

**Feedback**: - [ ] Useful

---

## Critical Clarifications Needed

| Question | Context | Owner | Priority |
|----------|---------|-------|----------|
| **How does Aaron maintain sync between technical docs and implementation code?** | Vrijen asked if docs lag behind code changes; Aaron mentioned prompting AI to update docs, but mechanism wasn't fully explored | Aaron | HIGH |
| **What specifically should go in B blocks for a specific use case?** | Generic structure is clear, but Vrijen may want domain-specific block templates for different meeting types (partnership vs. internal standups vs. client calls) | Vrijen | MEDIUM |
| **Can Persona switching be made automatic with explicit routing?** | Vrijen asked if embedding switching instructions IN the persona improves automatic switching; Aaron seemed open but didn't confirm testing this | Both | MEDIUM |
| **How does Aaron manage GitHub integration with Zo?** | Aaron mentioned it's "the next level" but scary; didn't discuss what blockers exist or what success looks like | Aaron | LOW |
| **What's the failure mode when technical debt IS accumulated in Zo builds?** | Vrijen said "it's an absolute untangle"; Aaron agrees but hasn't detailed specific cases. What does this look like? | Both | LOW |
| **How to decide: Persona-based routing vs. Rule-based prompt routing?** | Both approaches work; when should one prefer one over the other? | Both | LOW |

## Exploration Gaps

- **Aaron's actual prompt templates**: Structure is clear (research → plan → technical docs → code), but exact prompts/wording not shared
- **Vrijen's B## block generation process**: Demonstrated outcome but not the exact LLM instructions used to generate them
- **Versioning strategy for knowledge layers**: Both have layered systems; how do they handle version conflicts between layers?
- **Rollback/revision workflow**: When middle layer is wrong, how do they update it without cascading errors through other layers?
- **Scale testing**: Both systems work for personal workflows; not discussed whether patterns hold at team/org scale

## Implicit Assumptions to Validate

1. **Planning discipline scales universally**: Works for Zo; does it apply to other platforms/languages?
2. **Explicit routing >> semantic routing**: True for LLMs today; will this hold with future models?
3. **Three-layer compression (raw → middle → distilled) is optimal**: Both independently arrived at it, but optimal for what? Different problems might need 2 or 4 layers.
4. **Technical debt in "vibe coding" is primary blocker, not speed**: Aaron assumes planning overhead pays off; true for all contexts?

