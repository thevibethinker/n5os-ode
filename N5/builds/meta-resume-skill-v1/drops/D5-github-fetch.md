---
drop_id: D5
build_slug: meta-resume-skill-v1
spawn_mode: auto
created: 2026-01-30
depends_on: [D3]
---

# D5: GitHub Fetch Module

## Objective

Build `Skills/meta-resume-generator/scripts/github_fetch.py` — a standalone module that fetches GitHub profile data and outputs structured JSON for the Meta Resume generator.

## Output Format

```json
{
  "username": "hardikp",
  "profile_url": "https://github.com/hardikp",
  "fetched_at": "2026-01-30T02:50:00Z",
  "account_age_years": 8.5,
  "public_repos": 42,
  "total_contributions_last_year": 847,
  "followers": 156,
  "following": 89,
  "last_active": "2026-01-28",
  "languages": {
    "Python": 45.2,
    "TypeScript": 28.1,
    "JavaScript": 15.3,
    "Go": 8.4,
    "Other": 3.0
  },
  "top_repos": [
    {
      "name": "ml-platform",
      "description": "ML SaaS infrastructure",
      "stars": 234,
      "forks": 45,
      "language": "Python",
      "last_updated": "2026-01-25"
    }
  ],
  "activity_summary": {
    "commits_last_year": 623,
    "prs_last_year": 89,
    "issues_last_year": 34,
    "reviews_last_year": 156
  },
  "contribution_calendar": [
    {"week": "2026-W01", "count": 23},
    {"week": "2026-W02", "count": 31}
  ],
  "streaks": {
    "current": 12,
    "longest": 47
  },
  "warnings": []
}
```

## CLI Interface

```bash
# Fetch by username
python3 Skills/meta-resume-generator/scripts/github_fetch.py \
  --username hardikp \
  --output github-data.json

# Fetch with GitHub token (higher rate limits, contribution calendar)
python3 Skills/meta-resume-generator/scripts/github_fetch.py \
  --username hardikp \
  --output github-data.json \
  --token $GITHUB_TOKEN
```

## API Endpoints

### REST API (no auth, 60 req/hour)
- `GET /users/{username}` — Profile basics
- `GET /users/{username}/repos?sort=updated&per_page=10` — Top repos
- `GET /repos/{owner}/{repo}/languages` — Language breakdown per repo

### GraphQL API (requires token, for contribution calendar)
```graphql
query {
  user(login: "hardikp") {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
```

## Edge Cases

### Missing Profile
```json
{
  "username": "nonexistent",
  "error": "profile_not_found",
  "warnings": ["GitHub profile not found. Verify username or check if profile is private."]
}
```

### Sparse Profile (< 5 public repos)
```json
{
  "username": "sparse-user",
  "public_repos": 3,
  "warnings": ["Sparse public profile (3 repos). Candidate may have private repos or use different platforms."]
}
```

### Rate Limited
```json
{
  "username": "hardikp",
  "error": "rate_limited",
  "retry_after": 3600,
  "warnings": ["GitHub API rate limit reached. Retry after 1 hour or use authenticated requests."]
}
```

## Implementation Notes

1. **No external dependencies** — Use only `urllib` and `json` from stdlib
2. **Graceful degradation** — If GraphQL fails (no token), skip contribution calendar
3. **Language aggregation** — Weight by repo size (bytes), not just repo count
4. **Cache-friendly** — Output includes `fetched_at` for staleness checks

## Reference

- GitHub API spec: `file 'N5/builds/meta-resume-skill-v1/artifacts/GITHUB-INTEGRATION-SPEC.md'`

## Quality Gates

- [ ] Works without auth (REST only mode)
- [ ] Works with auth (REST + GraphQL)
- [ ] Handles missing profile gracefully
- [ ] Handles sparse profile with warning
- [ ] Handles rate limiting with retry info
- [ ] Output JSON matches schema above
- [ ] No external dependencies beyond stdlib
