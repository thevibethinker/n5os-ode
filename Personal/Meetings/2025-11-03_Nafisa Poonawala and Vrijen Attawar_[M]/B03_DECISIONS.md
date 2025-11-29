---
created: 2025-11-26
last_edited: 2025-11-26
version: 1.0
---

# B03 – Decisions

| # | Decision | Rationale | Owner |
|---|----------|-----------|-------|
| 1 | Treat the next 6 weeks as a structured health experiment (diet + stress + lifestyle), then re‑test before considering medication. | Avoid premature long‑term medication if lifestyle changes can materially improve markers; gives Nafisa a concrete timebox and sense of agency. | Nafisa (with medical support) |
| 2 | Use Nafisa’s Zo as a real‑world testbed for the N5OS light export/installation process. | She is an ideal non‑technical but sophisticated user; her environment is low‑risk to wipe and rebuild. | V |
| 3 | Anchor the N5OS export model around a “core system + local config” separation. | Enables V to keep evolving the canonical architecture while each user maintains their own preferences and sensitive data. | V |
| 4 | Ship more rather than less of the system (principles, prompts, personas, workflows) in the starter package. | New users will under‑invest in setup; better to over‑provide scaffolding and let them prune than expect them to build from scratch. | V |
| 5 | Use conversational onboarding (questions asked by Zo) to personalize the starter system. | Reduces cognitive overload versus handing users a dense technical README; aligns with how non‑technical users naturally interact. | V |
| 6 | Iterate on export validity using real installation attempts (like this one) instead of purely theoretical design. | Only actual installs surface missing scripts, schemas, and safety modules; design must be reality‑tested. | V |
| 7 | Defer fully automated persona switching until reliability improves; fall back to explicit persona calls where needed. | Current auto‑switching is flaky; brittle behavior in demos or user environments would erode trust. | V |

