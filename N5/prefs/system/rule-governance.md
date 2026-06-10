---
created: 2026-05-25
last_edited: 2026-05-25
version: 1.0
provenance: con_Cc4CiJkeRXB1pNxt
---

# Rule Governance

The rules engine should preserve routing and safety without becoming the workspace manual.

## Classification

Classify every proposed rule before creating or retaining it:

| Class | Keep In Rules? | Notes |
|---|---|---|
| Universal guardrail | Yes | Safety, honesty, external-action gates, durable cross-persona behavior |
| Thin router | Usually | Trigger that tells the agent which skill/doc/protocol to load |
| Procedural detail | No | Move to a skill, `AGENTS.md`, `POLICY.md`, or `N5/prefs/` |
| Folder policy | No, unless trigger is needed | Put in the most specific `AGENTS.md` or `POLICY.md` |
| Persona style | Usually no | Put in persona or communication prefs unless cross-persona enforcement is required |
| Obsolete behavior | No | Delete after V confirms decommissioning |

## Migration Standard

Do not delete a rule just because its procedure exists elsewhere. Delete only when trigger discovery is preserved by one of:

- a retained thin router rule;
- shared bootstrap docs;
- a skill trigger that is reliably available in the active harness;
- explicit decommissioning by V.

## Router Consolidation

Prefer umbrella routers over one rule per workflow. A thin router is still too granular if five adjacent workflows share the same detection layer.

Examples:

- One `workspace operations` router can cover session state, protected paths, file placement, format checks, and docs-first bootstrap.
- One `specialist routing` router can cover persona selection, Designer/Illustrator handoff, and Maintainer playbook invocation.
- One `build and debugging` router can cover Pulse, systematic debugging, graph review, and repeated-failure escalation.
- One `external action` router can cover calendar writes, outbound messages, publishing, scheduled agents, and service registration.
- One `inbound message` router can cover Telegram capture, meeting-task review replies, system notification relays, and decommissioned channels.

## Target Shape

Preferred live rule shape:

- the smallest reliable set of universal global guardrails;
- the smallest reliable set of umbrella router rules;
- 0 long procedural rules.

Use count as a diagnostic, not a goal. A healthy ruleset is usually about **12-20 rules**: enough always-loaded routing to prevent silent failure, but not enough procedural detail to become a second workspace manual.

Only push below that range when scenario tests prove trigger discovery still works. Exceed that range when a trigger would otherwise be reliably missed, a safety boundary would weaken, or V explicitly chooses redundancy over context reduction.

The goal is not arbitrary deletion. The goal is a rule layer that routes to executable memory without carrying full procedures or one-off workflow manuals.

## Scenario Gate

Before deleting or merging a router rule, test the user-facing scenario it protects. The test passes only if the agent would still load the correct skill, folder contract, policy, or preference doc without inventing behavior.

Representative scenarios:

- inbound Telegram capture or meeting-task-review replies;
- calendar writes and availability checks;
- Pulse/build/drop work;
- repeated debugging failures;
- site publishing or service creation;
- research artifact creation;
- saved article ingestion;
- public-facing writing that mentions V.
