# Stakeholder Auto-Tagging System — Implementation Complete (Phase 0)

**Date:** 2025-10-12  
**Status:** ✅ PHASE 0 COMPLETE — Ready for Phase 1 Build  
**Next:** Build email scanner and pattern analyzer

---

## What We Accomplished Today

### 1. ✅ Complete Tag Taxonomy Consolidation

**Created centralized master reference:**
- `file 'N5/docs/TAG-TAXONOMY-MASTER.md'` — Single source of truth for all N5 tagging
- Unified 12 tag categories (stakeholder, relationship, priority, engagement, context, etc.)
- Documented hashtag format with Howie bracket translation
- Added partner subtypes (collaboration vs. channel)

**Consolidated existing documentation:**
- Reviewed `file 'N5/docs/calendar-tagging-system-COMPLETE.md'` (Howie V-OS brackets)
- Reviewed `file 'N5/docs/howie-zo-harmonization-complete.md'` (Howie integration)
- Streamlined and centralized all tag references

---

### 2. ✅ Tag Format Decision: Hashtags Internally

**Adopted Option A:**
- Use hashtags (`#stakeholder:investor`) for all N5 internal systems
- Translate to brackets (`[LD-INV]`) for Howie calendar events
- Best ergonomics: single `#` prefix, self-documenting, standard convention

**Benefits:**
- More efficient to type and read
- No memorization required (`#stakeholder:investor` vs `[LD-INV]`)
- Extensible (N5-only tags like `#relationship:*` without impacting Howie)
- Future-proof (can propose to Howie after proving internally)

---

### 3. ✅ Configuration Files Created

**`N5/config/tag_mapping.json`**
- Bidirectional translation: hashtags ↔ brackets
- Auto-inheritance rules (e.g., `#stakeholder:investor` → `#priority:critical`)
- N5-only tag filters
- Regex patterns for dynamic tags (`#followup:external_7`)

**`N5/config/tag_taxonomy.json`**
- Complete tag catalog with descriptions
- Howie bracket mappings per tag
- Default priority levels per stakeholder type
- Extensibility markers for context tags

---

### 4. ✅ Retroactive Tagging Applied

**Hamoon Ekhtiari (FutureFit)** — `file 'N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/stakeholder_profile.md'`

**Verified tags added:**
- `#stakeholder:partner:collaboration` — Integration partnership
- `#relationship:new` — First meeting, exploratory
- `#priority:normal` — Not urgent
- `#engagement:needs_followup` — V to follow up within 2 weeks
- `#context:hr_tech` — Career support platform, 200K+ users

**Howie V-OS equivalent:** `[LD-NET] [A-1] *`

---

**Alex Caveny (Wisdom Partners)** — `file 'N5/records/meetings/2025-09-24_alex-caveny-wisdom-partners/stakeholder_profile.md'`

**Profile created with verified tags:**
- `#stakeholder:advisor` — Strategic coaching, GTM insights
- `#relationship:active` — Ongoing twice-monthly sessions
- `#priority:high` — Strategic value, shaped GTM strategy
- `#context:enterprise` — Former hiring manager perspective
- `#engagement:responsive` — High-quality insights

**Howie V-OS equivalent:** None (advisor is N5-only)

**Profile includes:**
- Background and expertise
- Validated hypotheses (H-GTM-008, H-GTM-009, H-GTM-010)
- Key insights on hiring manager pain points
- Coaching focus areas
- Engagement management (2x/month cadence)

---

### 5. ✅ Tag Taxonomy Enhancements

**Added partner subtypes:**
- `#stakeholder:partner:collaboration` — Integration/co-marketing partnerships
- `#stakeholder:partner:channel` — Distribution/resale partnerships

**Reason:** Too broad to just say "partner" — need to distinguish collaboration from channel relationships

**Both map to Howie's `[LD-NET]`** but N5 maintains granular distinction internally

---

## Tag Taxonomy Summary

### 12 Tag Categories (Hashtag Format)

1. **`#stakeholder:*`** — Primary contact classification (investor, advisor, partner, etc.)
2. **`#relationship:*`** — Relationship state (new, warm, active, cold, dormant)
3. **`#priority:*`** — Business priority (critical, high, normal, low)
4. **`#engagement:*`** — Communication behavior (responsive, slow, needs_followup)
5. **`#context:*`** — Industry/domain (hr_tech, venture_capital, enterprise, etc.)
6. **`#type:*`** — Meeting type (discovery, partnership, followup, recurring)
7. **`#status:*`** — Meeting/relationship status (active, postponed, awaiting, inactive)
8. **`#schedule:*`** — Timing constraints (within_5d, 5d_plus, 10d_plus)
9. **`#align:*`** — Coordination needs (logan, ilse, founders)
10. **`#accommodation:*`** — Flexibility approach (minimal, baseline, full)
11. **`#availability:*`** — Scheduling preferences (weekend_ok, weekend_preferred)
12. **`#followup:*`** — Follow-up reminders (external_N, logan_N, vrijen_N)

**N5-only tags (not synced to Howie):**
- `#relationship:*`
- `#engagement:*`
- `#context:*`
- `#stakeholder:customer`
- `#stakeholder:vendor`
- `#stakeholder:advisor`

---

## System Architecture (Approved)

### Phase 0: Planning & Setup ✅ COMPLETE
- [x] Tag taxonomy consolidated
- [x] Hashtag format adopted
- [x] Configuration files created
- [x] Translation layer designed
- [x] Retroactive tags applied to existing profiles

---

### Phase 1A: Email Scanner (THIS WEEK)
**Goal:** Discover external contacts from meeting-related emails

**Tasks:**
1. Build `N5/scripts/scan_meeting_emails.py`
2. Integrate Gmail API (reuse from meeting monitor)
3. Identify meeting invitations/confirmations
4. Extract external participant emails
5. **NEW:** Basic enrichment (domain analysis)
6. Store discovered contacts in staging area

**Output:** List of new contacts with basic metadata + enrichment

---

### Phase 1B: Pattern Analyzer + Web Enrichment (NEXT WEEK)
**Goal:** Auto-suggest tags based on email patterns + web research

**Tasks:**
1. Build `N5/scripts/analyze_stakeholder_patterns.py`
2. Implement 7 signal analysis types
3. **NEW:** Build `N5/scripts/enrich_stakeholder_contact.py` enrichment module
4. **NEW:** Integrate web search for company/person background
5. **NEW:** Add LinkedIn profile lookup (authenticated access via view_webpage)
6. Generate tag suggestions with confidence scores
7. Test with Hamoon + Alex profiles (validation)

**Output:** Profiles with suggested tags + enriched background data

---

### Phase 1C: LinkedIn & Deep Research (WEEK 3)
**Goal:** Rich profile enrichment with due diligence

**Tasks:**
1. Implement LinkedIn profile parsing (extract role, company, experience)
2. Integrate existing deep-research-due-diligence command
3. Auto-trigger deep research for investors and high-priority contacts
4. Cache enrichment data (avoid redundant lookups)
5. Add enriched data to weekly review format

**Output:** Fully enriched profiles with due diligence highlights

---

### Phase 2: Weekly Review Workflow (WEEK 3)
**Goal:** Automated weekly digest with tag suggestions

**Tasks:**
1. Build `N5/scripts/generate_stakeholder_review.py`
2. Compile new/updated contacts from past 7 days
3. Format digest (markdown) with suggested tags
4. Create scheduled task (Sundays 6pm ET)
5. Add SMS notification ("Weekly stakeholder review ready")

**Output:** Weekly review digest delivered via app + SMS

---

### Phase 3: Tag Application & Storage (WEEK 3-4)
**Goal:** Process V's feedback and apply verified tags

**Tasks:**
1. Build `N5/scripts/apply_verified_tags.py`
2. Parse review responses (approve, edit, skip)
3. Apply verified tags to profiles
4. Update CRM contact registry
5. Mark profiles as "reviewed" with timestamp

**Output:** Profiles with verified tags ready for downstream systems

---

### Phase 4: Howie Integration (WEEK 4+)
**Goal:** Provide context API for Howie queries

**Tasks:**
1. Build `N5/scripts/howie_context_api.py`
2. Implement tag-based contact queries
3. Generate V-OS tag recommendations (hashtag → bracket)
4. Return enriched context for meeting prep
5. Document integration spec for Howie team

**Output:** Query interface for Howie to access contact intelligence

---

## Files Created/Modified

### New Files Created ✅
- `N5/docs/TAG-TAXONOMY-MASTER.md` — Centralized tag reference
- `N5/docs/STAKEHOLDER-TAGGING-COMPLETE.md` — This summary
- `N5/config/tag_mapping.json` — Hashtag ↔ bracket translation
- `N5/config/tag_taxonomy.json` — Full tag catalog
- `N5/records/meetings/2025-09-24_alex-caveny-wisdom-partners/stakeholder_profile.md` — Alex's profile

### Files Modified ✅
- `N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/stakeholder_profile.md` — Added verified tags
- `N5/docs/STAKEHOLDER-TAGGING-HANDOFF.md` — Updated status

### Planning Documents (Conversation Workspace) ✅
- `/home/.z/workspaces/con_eceInSZIEtjzb9zS/stakeholder-auto-tagging-plan.md` — Full implementation plan
- `/home/.z/workspaces/con_eceInSZIEtjzb9zS/RETROACTIVE-TAGGING-ANALYSIS.md` — Retroactive tag analysis
- `/home/.z/workspaces/con_eceInSZIEtjzb9zS/TAG-FORMAT-PROPOSAL.md` — Hashtag format proposal

---

## Tag Examples (Real Profiles)

### Example 1: Hamoon Ekhtiari (Partnership)

**Internal N5 format:**
```markdown
## Tags

### Verified (Last reviewed: 2025-10-12)
- `#stakeholder:partner:collaboration`
- `#relationship:new`
- `#priority:normal`
- `#engagement:needs_followup`
- `#context:hr_tech`

### Howie Sync
**Recommended V-OS tags:** `[LD-NET] [A-1] *`
```

**Howie calendar description (translated):**
```
[LD-NET] [A-1] *

Purpose: Partnership exploration with FutureFit — embedded solutions integration

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.
```

---

### Example 2: Alex Caveny (Advisor)

**Internal N5 format:**
```markdown
## Tags

### Verified (Last reviewed: 2025-10-12)
- `#stakeholder:advisor`
- `#relationship:active`
- `#priority:high`
- `#context:enterprise`
- `#engagement:responsive`

### Howie Sync
**Recommended V-OS tags:** *(None — advisor is N5-only)*
```

**Howie calendar description:**
```
(No V-OS tags — internal advisor category)

Purpose: Strategic coaching session — GTM validation

---
Meeting notes shared internally only.
```

---

## Translation Layer Reference

### Hashtag → Bracket (Selected Examples)

| N5 Hashtag | Howie Bracket | Notes |
|------------|---------------|-------|
| `#stakeholder:investor` | `[LD-INV]` | Auto-sets `#priority:critical` |
| `#stakeholder:partner:collaboration` | `[LD-NET]` | Collaboration subtype |
| `#stakeholder:partner:channel` | `[LD-NET]` | Channel subtype |
| `#stakeholder:advisor` | *(N5 only)* | No Howie equivalent |
| `#priority:critical` | `!!` | Ultra-urgent |
| `#priority:high` | `[A-0]` | High value |
| `#priority:normal` | `[A-1]` | Default |
| `#schedule:5d_plus` | `[D5+]` | Schedule 5+ days out |
| `#align:logan` | `[LOG]` | Coordinate with Logan |
| `#relationship:warm` | *(N5 only)* | Internal relationship tracking |

**Full mapping:** See `N5/config/tag_mapping.json`

---

## Design Decisions Captured

### 1. Tag Format: Hashtags (Option A)
**Rationale:** More ergonomic, self-documenting, extensible
**Trade-off:** Requires translation layer for Howie
**Future:** May propose hashtags to Howie after proving internally

### 2. Partner Subtypes: Collaboration vs. Channel
**Rationale:** "Partner" too broad; need to distinguish integration from distribution
**Implementation:** Hierarchical tags (`#stakeholder:partner:collaboration`)
**Howie mapping:** Both map to `[LD-NET]`

### 3. N5-Only Tags
**Rationale:** Richer internal intelligence without complicating Howie integration
**Categories:** Relationship status, engagement behavior, industry context
**Benefit:** Can track nuanced relationship dynamics internally

### 4. Auto-Inheritance Rules
**Rationale:** Reduce manual tagging, enforce consistency
**Examples:**
- `#stakeholder:investor` → Auto-adds `#priority:critical`
- `#stakeholder:advisor` → Auto-adds `#priority:high` (suggested)
- All stakeholder types → Auto-add `#type:discovery` on first meeting

### 5. Confidence Scoring
**Rationale:** Distinguish high-confidence from tentative tag suggestions
**Levels:**
- High confidence (>80%): Likely accurate, suggest for auto-approval
- Medium confidence (60-80%): Review recommended
- Low confidence (<60%): Requires V's input

---

## Success Metrics (Defined)

### Accuracy Metrics
- **Tag suggestion accuracy:** % of suggested tags verified as correct
- **Target:** >80% accuracy for high-confidence suggestions

### Adoption Metrics
- **Review completion rate:** % of weekly reviews completed within 3 days
- **Target:** >90%

### Efficiency Metrics
- **Time to review:** Minutes spent reviewing weekly digest
- **Target:** <10 minutes per week

### Quality Metrics
- **Profile completeness:** % of active contacts with verified tags
- **Target:** >70% within 30 days

### Business Impact
- **Howie context queries:** # of successful lookups
- **Meeting prep enhancement:** % of meetings with enriched stakeholder context
- **Relationship tracking:** # of contacts with updated status

---

## Next Actions (Immediate)

### For V:
1. ✅ Review completed work (tags applied, profiles created)
2. ⏳ Approve Phase 1 build start (email scanner + pattern analyzer)
3. ⏳ Provide any additional stakeholders to retroactively tag

### For Zo (Phase 1A — This Week):
1. Build email scanner script
2. Integrate Gmail API (reuse meeting monitor code)
3. Test with real Gmail data
4. Discover 10-20 contacts for validation

### For Zo (Phase 1B — Next Week):
1. Build pattern analyzer
2. Implement 7 signal types
3. Generate tag suggestions for discovered contacts
4. Present to V for feedback before weekly review automation

---

## Open Questions

1. **Email scanner scope:** How far back should we scan? (Suggest: 90 days)
2. **Contact deduplication:** How to handle multiple email addresses for same person?
3. **Confidence thresholds:** What % confidence requires manual review vs. auto-suggest?
4. **Profile enrichment:** Should we auto-fetch LinkedIn data during discovery? **→ YES, V confirmed**
5. **Deep research triggers:** Auto-run for all investors? Only on V's request? **→ Auto for investors, optional for others**
6. **LinkedIn rate limiting:** How many profiles/hour is safe to avoid throttling? (Suggest: max 12/hour = 5 min gaps)
7. **Web search scope:** Company + person, or just company? **→ Both**

---

## Risk Mitigation

### Risk 1: Low Tag Accuracy
**Mitigation:** Start with high-confidence signals only (domain, clear keywords)
**Monitoring:** Track accuracy after first weekly review, adjust logic

### Risk 2: Email Scanner False Positives
**Mitigation:** Filter internal emails, require meeting context
**Validation:** Manual review of first 20 discovered contacts

### Risk 3: Review Fatigue
**Mitigation:** Keep digest concise (<10 contacts/week), highlight high-confidence
**Adjustment:** Allow bulk approval for obvious cases

### Risk 4: Howie Integration Complexity
**Mitigation:** Start with simple query API, test thoroughly
**Phasing:** V-OS recommendations first, then context queries

---

## Documentation Index

**Master References:**
- `file 'N5/docs/TAG-TAXONOMY-MASTER.md'` — Complete tag reference
- `file 'N5/config/tag_mapping.json'` — Translation mappings
- `file 'N5/config/tag_taxonomy.json'` — Full tag catalog

**Planning Documents:**
- `file 'N5/docs/STAKEHOLDER-TAGGING-COMPLETE.md'` — This summary (Phase 0 complete)
- `file '/home/.z/workspaces/con_eceInSZIEtjzb9zS/stakeholder-auto-tagging-plan.md'` — Full implementation plan
- `file '/home/.z/workspaces/con_eceInSZIEtjzb9zS/TAG-FORMAT-PROPOSAL.md'` — Hashtag format rationale

**Existing Documentation (Integrated):**
- `file 'N5/docs/calendar-tagging-system-COMPLETE.md'` — Howie V-OS brackets
- `file 'N5/docs/howie-zo-harmonization-complete.md'` — Howie integration

**Example Profiles:**
- `file 'N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/stakeholder_profile.md'` — Partnership example
- `file 'N5/records/meetings/2025-09-24_alex-caveny-wisdom-partners/stakeholder_profile.md'` — Advisor example

---

## Enrichment Integration (V's Request)

### Overview
Integrate web search, LinkedIn access, and due diligence research into stakeholder discovery and tagging workflow.

**Data sources:**
1. **Email metadata** (always available) — Name, company, communication patterns
2. **LinkedIn** (if discoverable) — Role, experience, industry, company size
3. **Web search** (company/person) — Company background, funding, news, industry
4. **Deep research** (on-demand) — Full dossiers for high-priority contacts (investors, strategic)

**See:** `file '/home/.z/workspaces/con_eceInSZIEtjzb9zS/ENRICHMENT-INTEGRATION-PLAN.md'` for full spec

---

### LinkedIn Access Protocol

**Method:** Use `view_webpage` tool with LinkedIn URLs  
**Authentication:** V is already signed in via Zo's browser — always assume authenticated access  
**Never:** Ask V to sign in or authenticate  

**Example:**
```python
# Fetch LinkedIn profile (authenticated)
linkedin_url = "https://www.linkedin.com/in/sarahchen/"
profile_data = view_webpage(linkedin_url)

# Extract structured data:
# - Current role & company
# - Past experience
# - Education, skills
# - Industry classification
```

**Rate limiting:** Pause 5 seconds between LinkedIn lookups to avoid throttling

---

### Web Search Enrichment

**Company background:**
- Company description, industry
- Funding rounds, investors
- Company size, momentum metrics
- Recent news (press, funding, acquisitions)

**Person background:**
- Bio snippets, notable achievements
- Media mentions, thought leadership
- Career trajectory signals

**Tag inference:**
- Company funding → Priority level (recent funding = high)
- Industry classification → Context tags
- Job title keywords → Stakeholder type
- Company size → Enterprise vs. startup context

---

### Deep Research Integration

**Existing command:** `file 'N5/commands/deep-research-due-diligence.md'`

**Capabilities:**
- Comprehensive research dossiers on companies, individuals, VCs, nonprofits
- Executive summaries with **strategic-fit scores (1-5)**
- SWOT analysis, milestone timelines
- **Careerspan relevance** assessment (partnership, customer, investor potential)

**Auto-trigger for:**
- `#stakeholder:investor` — Always run deep research on investors
- `#type:discovery` + high web search signals — First meetings with promising entities
- V's manual request — On-demand via command

**Output in weekly review:**
```markdown
**Due diligence highlights:**
- **Firm:** Acme Ventures — $500M AUM, Fund III ($200M, 2024)
- **Investment thesis:** Early-stage B2B SaaS, 50% future-of-work/HR tech
- **Strategic fit (Careerspan):** 4/5 — Strong thesis alignment, active in HR tech
- **Recent activity:** Led $5M seed in competing HR tech (June 2024) — potential conflict
```

---

### Enhanced Weekly Review Format

**With enrichment:**
```markdown
### 1. Sarah Chen (Acme Ventures)

**Email:** sarah@acmeventures.com  
**LinkedIn:** [Profile](https://linkedin.com/in/sarahchen)  
**Current role:** Partner, Acme Ventures (VC firm)

**Suggested tags:**
- ✅ `#stakeholder:investor` (HIGH confidence - 95%)
- ✅ `#priority:critical` (HIGH confidence - 90%)
- ✅ `#context:venture_capital` (HIGH confidence - 90%)

**Reasoning:**
- **Stakeholder type:** LinkedIn confirms Partner at VC firm; domain "acmeventures.com" matches known VC
- **Priority:** Auto-elevated (investor type); recent HR tech funding activity (web search)
- **Context:** Acme focuses on early-stage SaaS, 50% allocation to future-of-work

**Due diligence highlights:**
- **Strategic fit:** 4/5 — Active thesis match, 3 portfolio companies in HR tech
- **Recent activity:** Led $5M seed round in competing startup (June 2024) — NOTE: conflict or validation?
- **Timing:** Excellent — Fund III 40% deployed, actively investing

**Careerspan relevance:**
- 🟢 **Investment potential:** High — thesis alignment, active in HR tech
- 🟡 **Risk:** Portfolio includes competitor, but different focus area
```

---

### Enrichment Module

**Script:** `N5/scripts/enrich_stakeholder_contact.py`

**Functions:**
- `enrich_contact()` — Main enrichment orchestrator
- `linkedin_enrichment()` — Fetch and parse LinkedIn profiles
- `web_search_enrichment()` — Company/person background research
- `deep_research_enrichment()` — Full due diligence dossier
- `generate_tag_suggestions()` — Infer tags from enriched data with confidence scores

**Enrichment levels:**
- **Basic:** Email domain analysis only
- **Standard:** + LinkedIn + web search
- **Deep:** + Full due diligence dossier

**Configuration:** `N5/config/enrichment_settings.json`

---

## Status Summary

**Phase 0: Planning & Setup** ✅ COMPLETE
- Tag taxonomy consolidated and streamlined
- Hashtag format adopted (Option A)
- Configuration files created
- Translation layer designed
- Retroactive tags applied to 2 profiles

**Ready for Phase 1:** Email scanner + pattern analyzer

**Timeline:**
- **Week 1 (current):** Build email scanner, test with real data
- **Week 2:** Build pattern analyzer, validate tag suggestions
- **Week 3:** Build weekly review workflow, create scheduled task
- **Week 4:** Refine based on first review cycle, begin Howie integration

---

**🎉 Phase 0 Complete! Ready to build Phase 1.**
