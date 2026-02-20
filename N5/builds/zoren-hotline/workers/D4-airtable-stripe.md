---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.0
provenance: con_gFL5uhApy1RZtlSJ
drop_id: D4
title: Airtable Schema + Stripe Integration
status: pending
dependencies: []
---

# D4: Airtable Schema + Stripe Integration

## Objective
Set up FounderMaxxing Airtable base. Configure Stripe phone collection on existing payment links. Build Stripe webhook → Airtable member activation flow.

## Inputs
- Stripe products: prod_U0mBuPgOyPHy5c (Founding 15), prod_U0mBG5x8TQwOcl (Standard), prod_U0mBLTQMlMdtwt (Zo-to-Zo)
- State machine: prospect → applicant → approved → member → churned

## Outputs
- New Airtable base: "FounderMaxxing"
- Tables: Members, Calls, Applications
- Stripe payment links updated with phone collection
- Stripe webhook handler (can be zo.space API route on Zoputer or standalone)

## Airtable Schema

### Members Table
| Field | Type | Notes |
|-------|------|-------|
| Name | Single line text | |
| Email | Email | From Stripe |
| Phone | Phone | Primary key for matching |
| Status | Single select | prospect/applicant/approved/member/churned |
| Tier | Single select | founding-15/standard/zo-to-zo |
| Stripe Customer ID | Single line text | |
| Stripe Subscription ID | Single line text | |
| Joined Date | Date | When payment confirmed |
| Total Calls | Number | Rollup |
| Last Call | Date | |
| Notes | Long text | |
| Screening Notes | Long text | From intake calls |

### Calls Table
| Field | Type | Notes |
|-------|------|-------|
| Call ID | Single line text | VAPI call ID |
| Member | Link to Members | |
| Timestamp | Date | |
| Duration (sec) | Number | |
| Summary | Long text | |
| Pathway | Single select | intake/support/cobuild/faq |
| Outcome | Single select | qualified/needs-followup/not-fit/member-support |

### Applications Table
| Field | Type | Notes |
|-------|------|-------|
| Member | Link to Members | |
| Application Date | Date | |
| Screening Notes | Long text | AI-generated from call |
| Status | Single select | pending/approved/rejected/waitlisted |
| Approved By | Single line text | |
| Approved Date | Date | |
| Payment Link Sent | Checkbox | |

## Acceptance Criteria
- [ ] Airtable base created with all three tables
- [ ] Stripe payment links have phone collection enabled
- [ ] Stripe webhook receives checkout.session.completed
- [ ] Webhook creates/updates Member record in Airtable
- [ ] Member status transitions from approved → member on payment
- [ ] Phone → email association stored
