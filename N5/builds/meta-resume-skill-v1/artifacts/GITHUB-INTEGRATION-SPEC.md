---
created: 2026-01-30
last_edited: 2026-01-30
version: 1.0
provenance: con_jMehIeVWhVi3ZQd8
---

# GitHub Integration Specification

## Overview

The GitHub module fetches and formats candidate coding activity for the "By The Numbers" page. This provides objective, unfakeable evidence of coding behavior.

## Data Points to Capture

### Core Metrics (Always)

| Metric | API Source | Display |
|--------|------------|---------|
| **Public Repos** | `GET /users/{username}` → `public_repos` | Number |
| **Total Contributions (12mo)** | GraphQL contributionsCollection | Number |
| **Top Languages** | `GET /users/{username}/repos` → aggregate `language` | Top 3 with % |
| **Account Age** | `GET /users/{username}` → `created_at` | "Since YYYY" |
| **Last Push Date** | `GET /users/{username}/events` → most recent PushEvent | "X days ago" |
| **Followers** | `GET /users/{username}` → `followers` | Number |

### Extended Metrics (If Available)

| Metric | API Source | Display |
|--------|------------|---------|
| **Contribution Calendar** | GraphQL contributionCalendar | Visual grid |
| **Longest Streak** | Derived from calendar | "X days" |
| **Commits This Year** | GraphQL totalCommitContributions | Number |
| **PRs Opened** | GraphQL totalPullRequestContributions | Number |
| **Issues Opened** | GraphQL totalIssueContributions | Number |
| **Code Reviews** | GraphQL totalPullRequestReviewContributions | Number |

### Repo Highlights (Top 3 by Stars)

| Field | Source |
|-------|--------|
| Repo name | `name` |
| Description | `description` |
| Stars | `stargazers_count` |
| Language | `language` |
| Last updated | `pushed_at` |

---

## API Implementation

### REST API (Public, No Auth Required)

```python
import requests

def get_github_profile(username: str) -> dict:
    """Fetch basic GitHub profile data."""
    base_url = f"https://api.github.com/users/{username}"
    
    # Profile
    profile = requests.get(base_url).json()
    
    # Repos (for language aggregation)
    repos = requests.get(f"{base_url}/repos?per_page=100&sort=pushed").json()
    
    # Recent activity
    events = requests.get(f"{base_url}/events?per_page=30").json()
    
    return {
        "username": profile.get("login"),
        "name": profile.get("name"),
        "public_repos": profile.get("public_repos"),
        "followers": profile.get("followers"),
        "created_at": profile.get("created_at"),
        "bio": profile.get("bio"),
        "repos": repos,
        "events": events
    }
```

### GraphQL API (For Contribution Data — Requires Token)

```python
import requests
import os

def get_contribution_data(username: str) -> dict:
    """Fetch contribution calendar via GraphQL."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return {"error": "GITHUB_TOKEN not set"}
    
    query = """
    query($username: String!) {
        user(login: $username) {
            contributionsCollection {
                totalCommitContributions
                totalPullRequestContributions
                totalIssueContributions
                totalPullRequestReviewContributions
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
    """
    
    response = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": query, "variables": {"username": username}}
    )
    
    return response.json()
```

---

## Output Format

### Markdown (For Meta Resume)

```markdown
### GitHub: [@hardikp](https://github.com/hardikp)

| Metric | Value |
|--------|-------|
| **Public Repos** | 23 |
| **Contributions (12mo)** | 847 |
| **Top Languages** | Python (45%), TypeScript (30%), Java (15%) |
| **Account Since** | 2018 |
| **Last Active** | 3 days ago |
| **Followers** | 156 |

#### Top Repositories

| Repo | Description | ⭐ | Language |
|------|-------------|---|----------|
| [ml-platform](https://github.com/hardikp/ml-platform) | ML SaaS infrastructure | 234 | Python |
| [data-pipelines](https://github.com/hardikp/data-pipelines) | ETL framework | 89 | Python |
| [react-dashboard](https://github.com/hardikp/react-dashboard) | Analytics UI | 45 | TypeScript |

#### Contribution Activity

🟩🟩🟩🟩🟩🟩🟩 Jan
🟩🟩🟩🟨🟨🟩🟩 Feb
🟩🟨🟨🟨🟩🟩🟩 Mar
...
```

### JSON (For Programmatic Use)

```json
{
    "username": "hardikp",
    "profile_url": "https://github.com/hardikp",
    "metrics": {
        "public_repos": 23,
        "contributions_12mo": 847,
        "followers": 156,
        "account_age_years": 8,
        "days_since_last_push": 3
    },
    "languages": {
        "Python": 0.45,
        "TypeScript": 0.30,
        "Java": 0.15,
        "Other": 0.10
    },
    "top_repos": [
        {
            "name": "ml-platform",
            "url": "https://github.com/hardikp/ml-platform",
            "description": "ML SaaS infrastructure",
            "stars": 234,
            "language": "Python"
        }
    ],
    "contribution_calendar": {
        "total": 847,
        "longest_streak": 34,
        "current_streak": 12
    }
}
```

---

## Missing Profile Handling

When GitHub username is not provided or profile doesn't exist:

```markdown
### GitHub

> ⚠️ **GitHub not provided.** No public code profile available for this candidate.
> 
> **Recommended interview probe:** "Walk me through your most recent coding project. Can you show me the repo?"
```

When profile exists but is sparse (< 5 repos, < 50 contributions):

```markdown
### GitHub: [@username](https://github.com/username)

| Metric | Value |
|--------|-------|
| **Public Repos** | 3 |
| **Contributions (12mo)** | 12 |

> ⚠️ **Limited public activity.** This candidate has minimal public GitHub presence. This may indicate:
> - Primary work in private repos (common for enterprise developers)
> - Recent account creation
> - Preference for other platforms (GitLab, Bitbucket)
> 
> **Recommended interview probe:** "Your public GitHub is sparse. Where does most of your code live?"
```

---

## Script Interface

```bash
# Fetch and format GitHub data
python3 Skills/meta-resume-generator/scripts/github_fetch.py \
    --username hardikp \
    --output json \
    > github_data.json

# With token for full contribution data
GITHUB_TOKEN=xxx python3 Skills/meta-resume-generator/scripts/github_fetch.py \
    --username hardikp \
    --output markdown \
    --include-calendar
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--username` | GitHub username (required) | — |
| `--output` | Output format: `json`, `markdown` | `json` |
| `--include-calendar` | Include contribution calendar (requires token) | false |
| `--top-repos` | Number of top repos to include | 3 |

---

## Rate Limits

- **Unauthenticated:** 60 requests/hour (REST)
- **Authenticated:** 5,000 requests/hour (REST), 5,000 points/hour (GraphQL)

For batch processing, always use authenticated requests.

---

## Integration with Generator

The main `generate.py` script will:

1. Check if `github_username` exists in input data
2. If yes: Call `github_fetch.py` and include output in Page 3
3. If no: Include "GitHub not provided" warning block
4. Cache GitHub data in the processed output folder to avoid re-fetching

---

## Language Aggregation Algorithm

```python
def aggregate_languages(repos: list) -> dict:
    """Aggregate language usage across repos, weighted by repo size."""
    lang_bytes = {}
    
    for repo in repos:
        lang = repo.get("language")
        size = repo.get("size", 0)
        if lang:
            lang_bytes[lang] = lang_bytes.get(lang, 0) + size
    
    total = sum(lang_bytes.values())
    if total == 0:
        return {}
    
    # Convert to percentages, sort by usage
    lang_pct = {lang: bytes/total for lang, bytes in lang_bytes.items()}
    sorted_langs = sorted(lang_pct.items(), key=lambda x: -x[1])
    
    # Return top 5
    return dict(sorted_langs[:5])
```

---

## Contribution Calendar Visualization

For markdown/text output, use emoji grid:

```
🟩 = 4+ contributions
🟨 = 1-3 contributions  
⬜ = 0 contributions
```

Render as 7 rows (days) × 52 columns (weeks), or simplified monthly summary.

For Gamma/HTML, can embed SVG or use CSS grid with colored cells.
