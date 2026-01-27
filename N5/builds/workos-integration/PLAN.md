---
created: 2026-01-25
last_edited: 2026-01-25
version: 1.1
provenance: con_SjChSE4Zz2X5Hnui
type: build_plan
status: active
---

# Plan: WorkOS AuthKit for Where’s V (invite-only)

**Objective:** Add WorkOS AuthKit to `Sites/wheres-v-staging` so the entire Where’s V site is private (login required), and access is restricted to a pre-authorized allowlist of emails.

**Trigger:** V wants a reusable “infra” auth layer (WorkOS) implemented per-site via builds, starting with Where’s V.

---

## Open Questions (must resolve during build)

1) **Exact production public URL (Zo domain)** for Where’s V.
   - Needed to set:
     - `WORKOS_REDIRECT_URI = https://<PUBLIC_DOMAIN>/callback`
     - WorkOS dashboard Redirect URI / homepage / sign-in endpoint / logout redirect.

2) **Initial allowlist**: which emails should have access?

3) **Cookie encryption secret**: `WORKOS_COOKIE_PASSWORD` (32 chars) — V will set as a Zo secret.

---

## Checklist

### Phase 0 — Setup (already done)
- ☑ Install `@workos-inc/node` into `Sites/wheres-v-staging`

### Phase 1 — Auth integration (code)
- ☐ Implement WorkOS AuthKit endpoints + sealed session cookies in `Sites/wheres-v-staging/server.ts`
- ☐ Implement global auth gate so **all routes** require auth (except `/login`, `/callback`, `/logout`, `/health`, and static assets)
- ☐ Implement allowlist enforcement via `WHERES_V_ALLOWED_EMAILS`
- ☐ Test: unauthenticated `/` and `/api/current-state` redirect to `/login`

### Phase 2 — WorkOS dashboard + secrets (manual)
- ☐ Set WorkOS production Redirect URI / homepage / sign-in endpoint / logout redirect based on the production public URL
- ☐ Disable open sign-up / configure invite-only registration
- ☐ Set Zo secrets: `WORKOS_COOKIE_PASSWORD`, `WORKOS_REDIRECT_URI`, `WHERES_V_ALLOWED_EMAILS`

### Phase 3 — Validation + production publish
- ☐ Validate end-to-end login flow and allowlist enforcement
- ☐ If/when ready: create production site folder `Sites/wheres-v/` via promotion and publish
- ☐ Test: production public URL requires login; non-allowlisted email denied

---

## Success Criteria

1) Where’s V is not viewable without logging in.
2) Only allowlisted / invited emails can access (others are denied even if they authenticate).
3) Auth persists via httpOnly sealed cookie; no tokens in localStorage.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Wrong redirect URI causes “invalid redirect” loops | Use production public URL exactly; store as `WORKOS_REDIRECT_URI`; verify in WorkOS dashboard |
| Staging/prod mismatch (ports, entrypoints) | Keep edits in staging; only promote when validated |
| Cookie settings break on HTTP vs HTTPS | Use secure cookies in production; allow dev fallback if needed |
| Invite-only not enforced purely by WorkOS settings | Add app-level allowlist gate as an independent backstop |

---

## Drops (Pulse v3)

- **D1.1 (auto):** AuthKit integration in Bun/Hono (`server.ts`)
- **D1.2 (manual):** WorkOS dashboard configuration (prod URLs, invite-only)
- **D1.3 (manual):** Zo secrets configuration (cookie password, allowlist, redirect URI)
- **D2.1 (auto):** Local validation / sanity checks
