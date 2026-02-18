---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_qkaSQZCvQoQlHBTn
---

# AgentMail 3-Inbox Routing Policy (Careerspan + Hotline + Ops)

## Purpose
Define a safe, external-facing inbox operating model that supports automated processing while minimizing prompt-injection and unauthorized action risk.

## Scope
- Inbound/outbound routing policy for 3 AgentMail inboxes
- Trust classification and automation gates
- Review controls, escalation controls, and rollback controls

## Inbox Topology (v1)

1. `careerspan-intake@...`
   - Primary use: candidate, recruiter, employer, and JD intake
   - Primary outputs: structured lead/task objects; draft replies; review queue

2. `hotline@...`
   - Primary use: coaching hotline follow-up, session recaps, prep packets, scheduling coordination
   - Primary outputs: recap drafts, scheduling task candidates, follow-up reminders

3. `ops-escalations@...`
   - Primary use: incidents, failures, urgent exceptions, manual override requests
   - Primary outputs: triaged incident tickets, escalation alerts, operator decisions

## Identity Model
Use personas (`ZoPersonal`, `Zoputer`) as policy-bound operators over shared inbox context, not as separate public inbox identities.

Policy:
- Public inbox identities are function-based, not persona-based.
- Persona switching is internal decision logic only.
- External senders should never be able to select internal persona behavior by prompt.

## Security Posture (Non-Negotiable)

### Core Principle
Inbound email content is treated as untrusted data. It can propose intent but cannot authorize privileged actions.

### Hard Blocks
- No secrets disclosure or environment introspection from email instructions
- No destructive file/system actions from email-only requests
- No outbound mass messaging from email-only requests
- No account/rule/persona changes initiated from inbound email content

### Mandatory Verifications
- Sender verification (domain + known contact + thread continuity)
- Intent classification with confidence score
- Policy gate check (`auto-launch` vs `review-required`)
- Attachment safety scan + type allowlist before ingestion

## Sender Trust Tiers

1. Tier A: Trusted Internal
   - Known addresses controlled by V / verified internal operators
   - Eligible for highest automation, still bounded by safety rules

2. Tier B: Trusted External Partners
   - Known recruiters/employers/partners with prior validated thread history
   - Eligible for partial automation + draft generation

3. Tier C: Unknown External
   - New or unverified sender
   - Default to review-required and constrained responses only

4. Tier D: Suspicious/Adversarial
   - Injection patterns, spoof indicators, malware indicators, policy-evading instructions
   - Quarantine + ops escalation; no autonomous execution

## Routing Contract

## Decision Inputs
- `inbox_id`
- `sender_tier`
- `message_intent`
- `intent_confidence` (0.00-1.00)
- `action_risk` (`low` | `medium` | `high`)
- `contains_attachment` + `attachment_risk`
- `thread_state` (`new` | `known` | `disputed`)

## Policy Outputs
- `route`: `auto-process` | `draft-only` | `review-queue` | `quarantine`
- `queue`: target queue name
- `allowed_actions`: list
- `required_reviewer`: `none` | `operator`
- `sla_target_minutes`

## Automation Gate Matrix

- `auto-launch`
  - Conditions:
    - Tier A or Tier B
    - confidence >= 0.88
    - action risk = low
    - no high-risk attachments
  - Allowed actions:
    - Create/update internal task objects
    - Generate internal summaries
    - Generate reply drafts (not send) unless sender is Tier A and template-approved

- `review-required`
  - Triggered when any of:
    - confidence < 0.88
    - sender tier = C
    - action risk = medium/high
    - any policy-sensitive keyword/action requested
  - Actions:
    - Queue with structured rationale
    - Optional safe acknowledgment email

- `quarantine`
  - Triggered when:
    - sender tier = D
    - malware/spoof/injection signals
    - repeated policy bypass attempts
  - Actions:
    - No autonomous response beyond security-safe template
    - Immediate route to `ops-escalations`

## Inbox-Specific Playbooks

## 1) careerspan-intake
Primary intents:
- JD submission
- Candidate profile/resume
- Recruiter/employer request
- Status follow-up

Auto-process allowed:
- Parse entities into structured candidate/JD intake records
- Map to task candidates (`intake`, `review`, `follow-up`)
- Draft response with requested next steps

Always review-required:
- Requests containing contractual, legal, compensation, or policy exceptions
- Any instruction to contact large recipient lists

## 2) hotline
Primary intents:
- Coaching inquiry
- Session follow-up
- Scheduling and prep requests

Auto-process allowed:
- Summarize thread context
- Generate prep checklist/task candidates
- Create scheduling candidate task (not final booking) when ambiguous

Always review-required:
- Sensitive personal/life/legal/medical language
- Any request that materially alters coaching scope or billing

## 3) ops-escalations
Primary intents:
- System failure reports
- Urgent intervention requests
- Security concerns

Auto-process allowed:
- Incident object creation
- Severity classification + pager routing
- Suggested remediation checklist

Always review-required:
- Any action touching production config, credentials, or irreversible actions

## Reply Policy
- Default external behavior: draft-first
- Auto-send only for preapproved low-risk templates:
  - receipt confirmation
  - expected response-time notice
  - simple intake acknowledgment
- All non-template external replies require review in v1

## Data Model (Task Candidate)
Each routable email produces a task candidate envelope:
- `candidate_id`
- `source_inbox`
- `sender`
- `sender_tier`
- `intent`
- `confidence`
- `risk`
- `route_decision`
- `human_review_required`
- `extracted_entities`
- `proposed_actions`
- `policy_trace` (why decision was made)
- `status_sync_ref`

## Status Sync Contract
Task state transitions sync back to orchestration/memory context:
- `queued`
- `in_review`
- `approved`
- `executed`
- `blocked`
- `closed`

Minimum sync fields:
- `task_id`
- `origin_email_id`
- `current_status`
- `last_actor` (system/human)
- `updated_at`
- `resolution_note`

## Safety Controls
- Global kill switch: force all routes to `review-required`
- Inbox-level pause switch
- Quarantine threshold tuning (signal-based)
- Daily anomaly digest for false-positive/false-negative review

## Pilot Plan (14 Days)

Phase 1 (Days 1-3):
- Enable capture + classification only
- No autonomous sends

Phase 2 (Days 4-7):
- Enable auto-process for low-risk Tier A/B items
- Draft-only for external replies

Phase 3 (Days 8-14):
- Tune confidence/risk thresholds
- Validate precision/recall on routing decisions

Success metrics:
- Routing precision >= 90% for Tier A/B low-risk items
- False-negative rate <= 5% for suspicious items
- Median intake handling time reduced by >= 40%

## Recommended Expansion (when upgrading beyond 3 inboxes)
- `partner-desk@...` for employer/recruiter partnerships
- `research@...` for market and candidate intelligence intake
- `reengage@...` for dormant candidate reactivation

## Immediate Next Build Actions
1. Implement classifier + policy gate engine from this contract.
2. Wire event-to-task candidate mapper with policy trace.
3. Add review queue UI/markdown queue and ops kill switch.
4. Run 14-day pilot and publish error analysis report.
