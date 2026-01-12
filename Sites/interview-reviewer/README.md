# Am I Hired?

Expert interview feedback powered by AI career coaching.

## What It Does

Paste your interview transcript → Pay $5 → Get detailed, actionable feedback on your interview performance.

## Privacy First

- **Transcripts are never stored** — processed in memory, deleted immediately after analysis
- **Minimal metadata** — we only store session ID, company name, sentiment, and a brief summary
- **Open source** — verify our claims by reading the code

## Running Locally

```bash
# Install dependencies
bun install

# Set environment variables
export STRIPE_SECRET_KEY=sk_test_...
export OPENAI_API_KEY=sk-...
export ADMIN_KEY=your-admin-key

# Run
bun run src/index.tsx
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | Stripe secret key |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `PORT` | No | Server port (default: 3000) |
| `RATE_LIMIT_MAX` | No | Max requests per hour (default: 50) |
| `CIRCUIT_BREAKER_THRESHOLD` | No | Requests before circuit trips (default: 100) |
| `ADMIN_KEY` | No | Key for admin endpoints |

## Architecture

```
User → Landing Page → Paste Transcript → Stripe Checkout
                                              ↓
                     Report ← OpenAI Analysis ← Payment Verified
                                              ↓
                              Transcript Deleted from Memory
```

## API Endpoints

- `GET /` — Landing page
- `POST /api/checkout` — Create checkout session
- `GET /success?session_id=...` — Post-payment analysis & report
- `GET /privacy` — Privacy policy
- `GET /terms` — Terms of service
- `GET /health` — Health check
- `POST /admin/reset-circuit` — Reset circuit breaker (requires `X-Admin-Key` header)

## License

MIT — Careerspan

