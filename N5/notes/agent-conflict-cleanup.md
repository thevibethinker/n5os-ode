---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_bNkhbzAAGUKcUwU5
---

# Agent Conflict Cleanup

## Summary
- Pending: identify duplicates and stale agents once we decide which agents should remain.
- Awaiting explicit approval before disabling or modifying any scheduled agents.

## Recent Findings (from latest gate run)
1. **Delivery overlap (email channel)** — agents `ad169b76-5219-437b-8f69-f6305b5e20ba`, `a3d247a3-6060-4fae-a299-f5f888f2e8d1`, `e14728fc-cdf2-4a98-87d5-a50f87eac9ed`, `35523e05-6112-4708-894e-6bdb932566ac`, `99b51da6-4331-4f34-aa29-bcf8bb656ccd` share `email:` delivery. Action: determine if these represent duplicate digests or redundant notifications and keep only the canonical stream.
2. **Delivery overlap (SMS channel)** — agents `f5ec46f0-cb52-4614-b9ad-f2a0af5f0dd3`, `9048181e-7134-471a-bbaa-d6d19f2daf83`, `f1ad33d5-5ab7-465e-a688-3a3d21b96fb5` all send to `sms:` routes. Action: verify whether each SMS is still in use or if one agent can be paused.

## Recommendations (Draft)
1. Review each conflict cluster and choose one representative agent per delivery channel.
2. Mark duplicates as disabled (document the decision in this note) once V approves.
3. Confirm no stale agents remain (`next_run: null`) before turning on blocking mode.

## Next Steps
- Re-run the gate script with `--dry-run --summary --check-log` after confirming no new agents were created.
- Update this note with final decisions and link to log entries by timestamp.
