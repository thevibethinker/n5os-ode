---
created: 2025-11-20
last_edited: 2025-11-20
version: 1.0
---

# Deliverables

## Immediate Deliverables (Pre-Rollout)

### 1. 3-Story Engagement Gate Implementation
**What:** Technical configuration in Practice Interviews platform
**Who Delivers:** Jeff Chen (Practice Interviews)
**Timeline:** ASAP / before user rollout
**Specifications:**
- Automated trigger: when Careerspan user completes 3 career stories
- Gates Practice Interviews feature access (blocks below threshold)
- Tested and functional before live deployment

**Acceptance Criteria:**
- ✓ Configuration in Practice Interviews backend complete
- ✓ Gate successfully prevents sub-3-story users from accessing platform
- ✓ Tested with at least one test user
- ✓ Ready for production deployment

---

### 2. User-Facing Email Announcement
**What:** Email template to announce Practice Interviews partnership to Careerspan community
**Who Delivers:** Logan (Careerspan)
**Timeline:** Before rollout (draft by EOD this week ideally)
**Specifications:**
- Recipient: Careerspan users who meet 3-story threshold
- Message positioning: Exclusive partnership benefit for engaged members
- Tone: Encouraging, value-focused
- Includes: What Practice Interviews is, how to use it, why it matters
- CTA: Clear instructions for accessing platform
- Jeff Chen approval required before send

**Acceptance Criteria:**
- ✓ Draft sent to Jeff for review
- ✓ Language and brand positioning approved by Jeff
- ✓ Mobile-friendly formatting
- ✓ Clear CTA button / link

**Reference Materials Needed:** Jeff to provide existing Practice Interviews marketing copy for baseline tone/messaging

---

### 3. Auto-Email Milestone Trigger
**What:** Automated workflow that sends email when user hits 3-story milestone
**Who Delivers:** Logan (Careerspan automation setup)
**Timeline:** Concurrent with email draft (ideally live when gate is deployed)
**Specifications:**
- Trigger: "User completes 3rd career story"
- Sends: Email from Deliverable #2 (User-Facing Email Announcement)
- Includes: Link to Practice Interviews platform
- Pre-populated credentials: "Your access is already activated"
- Follow-up: Optional second email 1 week later if no login detected

**Acceptance Criteria:**
- ✓ Trigger fires correctly in test environment
- ✓ Email sends within 5 minutes of story #3 completion
- ✓ Email includes correct login instructions
- ✓ User can access Practice Interviews immediately after email

---

### 4. Analytics Dashboard / Reporting Framework
**What:** Real-time visibility into Careerspan user engagement with Practice Interviews
**Who Delivers:** Jeff Chen (provides admin dashboard), Logan (may build additional Careerspan-side reporting)
**Timeline:** Live on day of rollout
**Specifications:**
- Access: Admin panel at app.practiceinterviews.com (all three admins can view)
- Metrics tracked:
  - Users signed up from Careerspan
  - Login frequency
  - Total questions attempted
  - Average score (by user, aggregate)
  - Interview Academy completion rate %
  - Behavioral vs. hypothetical performance breakdown
  - Peak usage times/patterns
- Frequency: Updated real-time as users engage
- Reporting: Weekly summary sent to all three stakeholders

**Acceptance Criteria:**
- ✓ Dashboard shows Careerspan cohort separately
- ✓ All metrics listed above visible
- ✓ Data refreshes within 1 hour of user activity

---

## Secondary Deliverables (Post-Launch / Contingent)

### 5. Custom Careerspan-Specific Demo Video
**What:** Branded onboarding video for Careerspan users (more detailed than generic demo)
**Who Delivers:** Jeff Chen (Practice Interviews) + Careerspan marketing input
**Timeline:** 3-4 weeks post-launch (subject to initial adoption metrics)
**Specifications:**
- Duration: 3-5 minutes
- Audience: Careerspan users new to Practice Interviews
- Content:
  - Why this tool matters for career outcomes
  - How to use core features (add users, view analytics, answer questions)
  - Real Careerspan user success stories / testimonials (if available)
  - Integration with career story development
- Depth: Intermediate level (more guidance than current generic demo)
- Delivery: Embedded in welcome email or Careerspan platform

**Acceptance Criteria:**
- ✓ Video produced and tested
- ✓ Brand alignment with Careerspan
- ✓ 40%+ engagement rate on first send
- ✓ Drives measurable increase in Practice Interviews logins

---

### 6. Attribution Tracking Query / Report
**What:** Documentation of how to track Practice Interviews engagement → job outcomes
**Who Delivers:** Logan (Careerspan) + Apply AI technical team
**Timeline:** 4-6 weeks post-launch
**Specifications:**
- Defines: "Full product usage" (both Careerspan + Practice Interviews activity)
- Links: Practice Interviews engagement metrics to Careerspan job outcomes
- Identifies: Users who got offers after using both platforms
- Provides: Weekly/monthly cohort-level reporting
- Data sources: Careerspan job outcome data + Practice Interviews analytics
- Enables: Future monetization/partnership expansion discussions

**Acceptance Criteria:**
- ✓ Attribution model documented
- ✓ Queries written and tested on historical data
- ✓ First monthly report delivered showing baseline

---

## Non-Deliverables (Handled Manually / Already Exists)

- Admin access setup (already done during call)
- Platform login credentials (already set up)
- Practice Interviews platform itself (already built by Jeff)
- Careerspan user database (already exists)

---

## Deliverable Timeline Summary

| Deliverable | Status | Target Date | Owner |
|-------------|--------|------------|-------|
| 3-Story Gate | 🔴 Not Started | EOW 11/24 | Jeff |
| User Email | 🔴 Not Started | EOW 11/24 | Logan |
| Auto-Trigger | 🔴 Not Started | EOW 11/24 | Logan |
| Analytics Dashboard | 🟢 Ready | Day 1 | Jeff |
| Custom Demo | ⏳ Contingent | 12/4-12/11 | Jeff |
| Attribution Tracking | ⏳ Contingent | 12/1-12/15 | Logan + Apply AI |

---

## Success Metrics (Post-Delivery)

Once all deliverables are deployed, partnership success is measured by:
1. **Adoption:** 40%+ of eligible Careerspan users (3+ stories) sign up within 2 weeks
2. **Engagement:** Average 10+ questions attempted per user within first month
3. **Learning:** 30%+ of users attempt Interview Academy modules
4. **Retention:** 60%+ active users (at least 1 login) in week 3+
5. **Attribution:** Trackable increase in job offers for users engaging with both platforms
