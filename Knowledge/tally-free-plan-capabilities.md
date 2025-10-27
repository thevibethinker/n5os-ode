# Tally Free Plan Capabilities

**Created:** 2025-10-26  
**Purpose:** Document Tally free plan features for API usage

---

## Free Plan Features

### ✅ **Unlimited (Within Fair Use)**
- **Unlimited forms** - Create as many forms as needed
- **Unlimited submissions** - No cap on responses
- **Unlimited questions** - No field limits per form

### ✅ **Advanced Features (FREE)**
- Multi-page forms
- Conditional logic
- Custom "Thank You" pages
- Password protection
- Close forms on limit/date
- Form templates
- Embed anywhere
- Email notifications
- Custom domains (with limitations)
- Calculations
- Hidden fields

### ✅ **Input Types (FREE)**
- Text, Email, Number, Phone
- URL, Date, Time
- Textarea (long text)
- Multiple choice
- Checkboxes
- Dropdown
- Multi-select
- Rating
- Linear scale
- Rankings
- Matrix questions
- File uploads
- Electronic signatures
- Payments (via integrations)

### ✅ **Integrations (FREE)**
- Webhooks
- Zapier
- Make (formerly Integromat)
- Notion
- Slack
- Airtable
- Google Sheets
- HubSpot
- And many more

### ⚠️ **Limitations on Free Plan**
- Form visit analytics (last 7 days only)
- Tally branding on forms
- No workspaces for teams
- Fair use policy applies

---

## API Capabilities on Free Plan

### ✅ **Fully Supported**
1. Create unlimited forms
2. Update form settings and blocks
3. List all forms
4. Get form details
5. Delete forms
6. List submissions (paginated)
7. Get individual submissions
8. Delete submissions
9. Create/manage webhooks
10. List webhook events

### 🔄 **Rate Limits**
- **100 requests per minute**
- Recommendation: Use webhooks instead of polling

### ⚠️ **Not Explicitly Limited**
- Blocks per form
- Fields per form
- Submissions per form
- Webhooks per form

---

## Fair Use Policy

Tally's "fair use" isn't explicitly defined but generally means:
- Don't abuse the system
- Don't create spam forms
- Don't hammer the API
- Use webhooks instead of excessive polling
- Don't resell Tally as a service

**Reality:** 99% of users will never hit fair use limits. Tally's free tier is genuinely generous.

---

## What Requires Paid Plan?

### Tally Pro ($29/mo)
- Remove Tally branding
- Workspaces for teams
- Team member invitations
- Full analytics history
- Priority support

### Tally Business ($89/mo)
- Everything in Pro
- Custom subdomain
- Advanced security
- SSO
- Dedicated support

---

## Recommended Usage Pattern

For free plan with API:

1. **Create forms programmatically** when needed
2. **Use webhooks** for real-time submission notifications
3. **Poll submissions** only for historical data or backups
4. **Respect rate limits** (100/min is generous)
5. **Store form IDs** in your system for reference

---

## Sources

Based on research from:
- Tally official pricing page
- API documentation
- User reports and reviews
- Comparison with competitors (Typeform, Jotform, etc.)

The free plan is legitimately competitive with paid plans from other services.
