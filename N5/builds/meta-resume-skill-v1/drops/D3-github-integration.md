---
drop_id: D3
build_slug: meta-resume-skill-v1
spawn_mode: auto
created: 2026-01-29
---

# D3: GitHub Profile Integration

## Objective

Build a module that fetches GitHub profile data and generates an "Appendix" snapshot for the Meta Resume. This is a key differentiator — founders want to see if candidates actually ship code.

## Context

**Reader:** Technical hiring manager or technical founder
**Alternative they're comparing to:** Standard recruiter pitch + resume + LinkedIn (no code signal)
**Our edge:** We show the green squares. Commit history doesn't lie.

## Requirements

### Input
- GitHub username (from decomposed data or manual input)
- Fallback: Flag when GitHub is missing

### Output: GitHub Snapshot
Generate a markdown-compatible snapshot including:

1. **Contribution Calendar** 
   - ASCII or emoji-based heatmap of last 12 months
   - Or: Summary stats ("142 contributions in the last year, most active in Oct-Nov")

2. **Recent Activity** (last 90 days)
   - Commit count
   - PRs opened/merged
   - Repos contributed to

3. **Profile Stats**
   - Public repos count
   - Top 3 languages (by repo count or commit volume)
   - Followers (social proof signal)
   - Account age
   - Last active date

4. **Red Flags to Surface**
   - Account created recently (< 1 year)
   - No activity in last 6 months
   - Very few public repos
   - Profile looks like a "portfolio" account (few commits, mostly forks)

### Missing Profile Handling
When GitHub username not provided:
```markdown
⚠️ **Missing: GitHub** — No public code profile provided. Probe coding activity in interview.
```

## Technical Approach

### Option A: GitHub API (Recommended)
```python
# Using GitHub REST API (no auth needed for public data, but rate-limited)
import requests

def get_github_stats(username):
    user = requests.get(f"https://api.github.com/users/{username}").json()
    repos = requests.get(f"https://api.github.com/users/{username}/repos").json()
    events = requests.get(f"https://api.github.com/users/{username}/events/public").json()
    # Process and return snapshot
```

Rate limits: 60 requests/hour unauthenticated. For higher volume, use GitHub token from secrets.

### Option B: GitHub GraphQL API
More efficient for contribution calendar data. Requires auth token.

### Option C: Scrape contribution calendar
Fallback if API insufficient. The SVG calendar is publicly visible.

## Deliverables

1. **Script:** `Skills/meta-resume-generator/scripts/github_snapshot.py`
   - CLI: `python3 github_snapshot.py <username> [--output-dir <path>]`
   - Output: `github-snapshot.md` (markdown formatted)
   - Output: `github-snapshot.json` (raw data for Gamma)

2. **Integration hook** for main generator to call this module

3. **Test with Hardik's GitHub** (if available) or use a known active profile

## Quality Gates

- [ ] Fetches real data from GitHub API
- [ ] Handles missing/private profiles gracefully
- [ ] Generates markdown-compatible output
- [ ] Surfaces red flags (inactive, new account, etc.)
- [ ] Works without auth (public data only)
- [ ] Rate limit aware (caches or warns)

## References

- GitHub REST API: https://docs.github.com/en/rest
- GitHub GraphQL API: https://docs.github.com/en/graphql
- Example contribution calendar: https://github.com/users/<username>/contributions
