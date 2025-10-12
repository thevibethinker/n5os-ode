---
date: "2025-10-12T00:00:00Z"
version: 2.0
category: quality
priority: high
---
# Quality Principles

These principles ensure outputs are accurate, complete, and verifiable.

## 1) Human-Readable First

**Purpose:** Humans review and edit; machines consume

**Rules:**
- Generate human-readable outputs before any machine format.
- JSON skeletons are derived from the human text, not vice versa.
- Markdown is preferred for documentation and reports.

**When to apply:**
- Documentation generation
- Report creation
- Data export formats

---

## 15) Complete Before Claiming Complete

**Purpose:** Prevent premature "done" declarations

**Rules:**
- Never mark work as "complete" or "production-ready" until ALL stated objectives are met.
- If implementing a design with 23 sections, ensure all 23 sections are present and functional.
- Test with production configuration, not development proxies.
- Define "complete" explicitly before starting work.

**When to apply:**
- System implementations
- Feature development
- Workflow automation
- Documentation projects

**Anti-patterns:**
- Saying "v2.1 complete" when only 59% of sections are implemented
- Marking as done when tests haven't been run
- Shipping with known gaps and calling them "future enhancements"

**Example from thread export refactoring (2025-10-12):**
- Design specified 23 sections across 6 files
- Must verify all 23 sections exist and function
- Must test with production LLM, not development substitute

---

## 16) Accuracy Over Sophistication

**Purpose:** Trustworthy information beats impressive speculation

**Rules:**
- When uncertain, state facts conservatively rather than adding "sophisticated" speculation.
- Make assumptions explicit and flag them as such.
- Prefer simple, accurate output over impressive, speculative output.
- If you don't know, say so—don't fill gaps with plausible-sounding content.
- NEVER invent technical limitations that don't exist.

**When to apply:**
- Meeting summaries
- Strategic analysis
- Data interpretation
- Knowledge extraction
- API and technical documentation

**Anti-patterns:**
- Adding strategic context that "sounds smart" but isn't grounded in data
- Inferring relationships without evidence
- Embellishing facts to seem more insightful
- Confusing speculation with analysis
- **Inventing API limitations without checking documentation**

**Example from meeting digest accuracy issues (2025-10-12):**
- Bad: "Strategic partnership aimed at market expansion" (speculative)
- Good: "Partnership discussed; specific goals not stated in transcript" (accurate)

**CRITICAL ANTI-PATTERN: False API Limitations (2025-10-12):**
- **What happened:** Claimed Gmail API had "3-message limit" in test queries
- **Reality:** Gmail API supports:
  - Up to 500 results per query
  - Pagination via `pageToken` to get thousands more
  - Date filters (`after:`, `before:`) for time ranges
  - Progressive searches going farther back in time
- **The error:** The "3-message limitation" was my own artificial constraint for testing, NOT a real API limit
- **Lesson:** If you don't know an API's actual limits, say so. Don't invent plausible-sounding limitations.
- **Rule:** When working with APIs, either cite documentation or explicitly state "I don't know the actual limits"

---

## 18) State Verification is Mandatory

**Purpose:** Confirm operations succeeded

**Rules:**
- Systems that write state must verify writes succeeded.
- Check that files exist, have expected content, and are not truncated.
- Provide explicit verification steps in documentation.
- Log verification results.

**When to apply:**
- File writes
- Database updates
- Configuration changes
- State transitions in workflows

**Anti-patterns:**
- Writing state file and assuming success without checking
- No post-write validation
- Silent partial writes
- Trusting error codes without content verification

**Implementation:**
- After write: check file exists
- Verify file size > 0
- Validate structure (e.g., valid JSON)
- Compare checksums if critical
- Log verification result

**Example from test cycle requirements (2025-10-12):**
- Not enough to `write(file, data)`
- Must: `write() → verify_exists() → verify_size() → verify_structure()`

---

## 21) Document All Assumptions, Placeholders, and Stubs

**Purpose:** Make temporary/incomplete implementations explicit and trackable

**Rules:**
- Track EVERY assumption you make during implementation
- Document ALL placeholders ("TODO", "FIXME", "placeholder for...")
- List ALL stubs, simulations, or mock implementations
- Create a manifest of what's incomplete
- Never silently leave placeholder code without documentation

**When to apply:**
- System implementations with placeholder logic
- Scripts with stub functions
- Designs with assumptions about future work
- Any code that says "TODO: implement actual..."

**Implementation:**
- Create `ASSUMPTIONS.md` or add section to implementation doc
- Comment every placeholder: `# PLACEHOLDER: actual LLM call goes here`
- List stubs at top of file or in module docstring
- Include in handoff documentation

**Format for tracking:**
```markdown
## Assumptions Made
1. Gmail API has 3-message limit (VERIFY THIS - may be wrong)
2. User wants JSON output (not confirmed)

## Placeholders
1. Line 45: extract_lessons_llm() - Returns empty list, needs LLM call
2. Line 89: authenticate() - Stub returning True

## Stubs/Simulations
1. mock_api_response() - Not real API, simulated for testing
```

**Anti-patterns:**
- Writing placeholder code and forgetting it exists
- Assuming someone will "figure it out later"
- Leaving TODO comments without tracking them centrally
- Not documenting what's incomplete when handing off work
- Treating placeholders as if they're real implementations

**Why this matters:**
- Prevents confusion about what's actually done
- Makes it easy to find incomplete work
- Allows proper estimation of remaining effort
- Reduces the chance of shipping placeholder code

**Example from lessons system implementation (2025-10-12):**
- Created `extract_lessons_llm()` with placeholder
- Documented it returns empty list
- BUT: Didn't create manifest of ALL assumptions made
- Should have: Listed every stub, every assumption, every TODO in one place
