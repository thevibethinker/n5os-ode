---
created: 2026-01-20
last_edited: 2026-01-20
version: 2.0
provenance: con_MtBZzXOqgq2zInUN
---

# Vrijen LinkedIn Retrospective — Build Plan

**Slug:** `vrijen-linkedin-retro`  
**Title:** "Vrijen LinkedIn Retrospective — January 2026"  
**Status:** Ready for workers  
**Data Source:** `Datasets/linkedin-full-pre-jan-10/data.duckdb`  
**Deployment:** Integrated into `Sites/vrijenattawar-staging/` at `/projects/linkedin`

---

## Decisions (Locked)

| Decision | Choice |
|----------|--------|
| Name | "Vrijen LinkedIn Retrospective — January 2026" |
| Deployment | Integrated into vrijenattawar.com under `/projects/linkedin` |
| Privacy | Scrub all names; pseudonymize titles (e.g., "Executive at FAANG") |
| Discovery | Easter egg mechanism (TBD in Wave 4) |
| GitHub | Add to site (username: `vrijenattawar`) |
| Build approach | Parallel workers via orchestrator |

---

## Site Context

**Current vrijenattawar.com structure:**
- `/` → PersonalLanding (main page)
- `/mind` → MindMap
- `/analytics` → Analytics
- `/demos/*` → Demo pages

**Will add:**
- `/projects` → Projects index (Easter egg entry point)
- `/projects/linkedin` → LinkedIn Retrospective dashboard

**Tech stack:** React + Vite + TypeScript, Hono server backend, shadcn/ui components

---

## Architecture

```
Sites/vrijenattawar-staging/
├── src/
│   ├── pages/
│   │   ├── projects/
│   │   │   ├── ProjectsIndex.tsx      # Easter egg landing
│   │   │   └── LinkedInRetro.tsx      # Main dashboard
│   │   └── ...existing pages
│   ├── components/
│   │   └── linkedin/
│   │       ├── NetworkUniverse.tsx    # Force-directed graph
│   │       ├── CareerArc.tsx          # Timeline visualization
│   │       ├── NetworkComposition.tsx # Who you know analysis
│   │       ├── MessagingInsights.tsx  # Conversation patterns
│   │       ├── ContentActivity.tsx    # Posts/comments/reactions
│   │       ├── SearchBehavior.tsx     # What you search for
│   │       └── charts/                # Shared chart components
│   └── lib/
│       ├── linkedin-queries.ts        # DuckDB query functions
│       └── privacy.ts                 # Name scrubbing utilities
├── server.ts                          # Add API routes for queries
└── data/ → symlink to dataset
```

---

## Privacy Layer

**Name scrubbing rules:**
- Replace all names with pseudonyms: "Person A", "Person B", etc.
- Consistent pseudonyms per conversation/relationship (same person = same pseudonym)
- V's own name can appear

**Title pseudonymization:**
- FAANG → "FAANG" (keep)
- Specific company titles → "[Seniority] at [Category]"
  - "Chief of Staff at Netflix" → "Executive at FAANG"
  - "Software Engineer at Stripe" → "Engineer at Fintech Unicorn"
  - "Founder at [Startup]" → "Startup Founder"
- Categories: FAANG, Fintech, Enterprise SaaS, Startup, VC/PE, Consulting, Academia

---

## Wave Structure

### Wave 1: Foundation (2 workers, parallel)
Sets up routing, privacy layer, and query infrastructure.

| Worker | Task | Dependencies |
|--------|------|--------------|
| W1.1 | Site routing + page shells | None |
| W1.2 | Privacy utilities + DuckDB query layer | None |

### Wave 2: Core Visualizations (4 workers, parallel)
All visualization components. Can run fully parallel after Wave 1.

| Worker | Task | Dependencies |
|--------|------|--------------|
| W2.1 | Network Universe + Network Composition | W1.* |
| W2.2 | Career Arc + Connection Growth Timeline | W1.* |
| W2.3 | Messaging Insights (conversations, patterns) | W1.* |
| W2.4 | Content Activity (posts, comments, reactions) | W1.* |

### Wave 3: Extended Analysis (2 workers, parallel)
Bonus analyses unique to V's dataset.

| Worker | Task | Dependencies |
|--------|------|--------------|
| W3.1 | Search Behavior + Learning Journey | W1.* |
| W3.2 | Job Applications Timeline + Correlations | W1.* |

### Wave 4: Polish & Integration (2 workers, sequential)
Easter egg, GitHub, final assembly.

| Worker | Task | Dependencies |
|--------|------|--------------|
| W4.1 | Easter egg discovery mechanism + Projects index | W2.*, W3.* |
| W4.2 | GitHub integration + QA + deploy | W4.1 |

---

## Visualization Specifications

### Core (from Logan, adapted)

**1. Network Universe**
- Force-directed graph of connections
- Nodes sized by message frequency
- Colored by industry/category (pseudonymized)
- Clickable for aggregate stats (not individual names)

**2. Career Arc**
- Horizontal timeline of positions
- Vertical bands showing connection growth per era
- Milestone markers for role changes

**3. Connection Growth Over Time**
- Area chart by month
- Overlay with career milestones
- Cumulative vs. monthly views

**4. Top Conversations (pseudonymized)**
- Bar chart: "Person A - 342 messages"
- Show title category, not name
- Aggregate stats only

**5. Content Timeline**
- Posts, comments, reactions by month
- Stacked area chart
- Highlight viral/high-engagement periods

### Extended (V's unique data)

**6. Network Composition**
- Pie/treemap: What industries are your connections in?
- Seniority distribution (IC vs Manager vs Exec vs Founder)
- Company category breakdown (FAANG, Startup, etc.)

**7. Search Behavior**
- Word cloud of search queries
- Search frequency over time
- Categories: People searches vs. Job searches vs. Topic searches

**8. Learning Journey**
- LinkedIn Learning courses completed
- Topics/skills studied
- Completion rate over time

**9. Job Application Timeline**
- When you applied to jobs
- Companies (pseudonymized by category)
- Correlation with other activity

**10. Messaging Velocity**
- Messages sent/received per month
- Response patterns
- Conversation depth (messages per unique person)

---

## Data Queries (Reference)

```sql
-- Network composition by company category
SELECT 
  CASE 
    WHEN company ILIKE '%google%' OR company ILIKE '%meta%' OR company ILIKE '%apple%' 
         OR company ILIKE '%amazon%' OR company ILIKE '%microsoft%' OR company ILIKE '%netflix%'
    THEN 'FAANG'
    WHEN company ILIKE '%stripe%' OR company ILIKE '%plaid%' OR company ILIKE '%square%'
    THEN 'Fintech'
    -- ... more categories
    ELSE 'Other'
  END as category,
  COUNT(*) as count
FROM connections
GROUP BY 1
ORDER BY count DESC;

-- Connection growth by month
SELECT 
  date_trunc('month', connected_on) as month,
  COUNT(*) as new_connections,
  SUM(COUNT(*)) OVER (ORDER BY date_trunc('month', connected_on)) as cumulative
FROM connections
WHERE connected_on IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- Top conversation partners (will be pseudonymized in display)
SELECT 
  CASE WHEN is_from_v THEN recipient_names ELSE sender_name END as counterparty,
  COUNT(*) as message_count
FROM messages
GROUP BY 1
ORDER BY message_count DESC
LIMIT 20;
```

---

## Success Criteria

- [ ] All visualizations render with real data
- [ ] No PII visible (names scrubbed, titles pseudonymized)
- [ ] Easter egg discovery works
- [ ] GitHub link added to main site
- [ ] Responsive on mobile
- [ ] Page load < 3s
