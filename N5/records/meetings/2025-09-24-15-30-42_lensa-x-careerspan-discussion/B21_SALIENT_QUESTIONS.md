# B21: SALIENT_QUESTIONS

```json
{
  "questions": [
    {
      "text": "Clarify Lensa’s business model and compensation (CPC/CPA) and what counts as success.",
      "why_it_matters": "Align incentives and tracking to evaluate ROI for the test and potential scale-up.",
      "speaker": "Vrijen",
      "timestamp": "04:03–06:05",
      "action_hint": "Document success metrics (registrations, alert engagement, CPA/CPC targets) before launch.",
      "origin": "explicit"
    },
    {
      "text": "Preferred ingestion/distribution paths (XML feed, Jobs API, co-registration).",
      "why_it_matters": "Determines engineering effort, latency, and data cleanliness for job distribution.",
      "speaker": "Mai",
      "timestamp": "06:23",
      "action_hint": "Start with XML filtered to product roles and SF/NY/Boston; evaluate API later.",
      "origin": "explicit"
    },
    {
      "text": "Volume vs. quality tradeoff for CPC evaluation.",
      "why_it_matters": "Careerspan’s model emphasizes quality; CPC targets may require minimum throughput.",
      "speaker": "Vrijen",
      "timestamp": "07:55–08:51",
      "action_hint": "Set baseline volume expectations for test and consider CPA or hybrid metrics if needed.",
      "origin": "implicit"
    },
    {
      "text": "Signup friction and routing (keep user flow low-friction while routing to Lensa).",
      "why_it_matters": "Higher conversion on registrations and alerts increases monetization potential.",
      "speaker": "Mai",
      "timestamp": "12:29–13:36",
      "action_hint": "Use direct application paths to Lensa for test; measure conversion drop-offs.",
      "origin": "explicit"
    }
  ],
  "secondary_questions": [
    "Geo and category scoping to contain processing cost (product roles; SF/NY/Boston)",
    "Cadence of feed updates (weekly to start) and job freshness (every ~3 days)"
  ]
}
```
