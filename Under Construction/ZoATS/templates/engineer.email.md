# ZoATS Email Templates — Founding Engineer

## Clarifying Questions (Candidate Passes Quick-Test)
Subject: Quick follow-up on your application to {{company.name}}

Hi {{candidate.first_name}},

Thanks for applying for {{job.title}}. To move quickly, could you reply with brief answers to the below?

1) Tell us about a time you shipped something end-to-end alone. What was hard, and how did you overcome it?
2) Point us to a piece of work that best reflects your craft. Why this?
3) What about {{company.name}} specifically resonates with you?

Thanks!
— {{company.name}} team

---

## Polite Rejection (Quick-Test Fail)
Subject: Thanks for applying to {{company.name}}

Hi {{candidate.first_name}},

Thanks again for your interest in {{company.name}}. At this time, we’re moving forward with candidates whose experience more closely matches the role. We’ll keep your info on file for future opportunities.

Wishing you the best,
— {{company.name}} team

---

## Finalist Digest (Internal)
Subject: {{job.title}} finalists — {{date}}

Top candidates and why:

{{#each finalists}}
- {{this.name}} — Score {{this.score}}: {{this.summary}}
  - Ultra-signals: {{this.signals}}
  - Probe: {{this.probes}}
{{/each}}
