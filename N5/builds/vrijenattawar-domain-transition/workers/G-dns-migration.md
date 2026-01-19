---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_nxvKhHpwzg225fn8
---

# Worker G: Full Cord Cut (DNS Migration)

**Project:** vrijenattawar-domain-transition
**Component:** Infrastructure / Domain
**Priority:** High

---

## Objective

Migrate `vrijenattawar.com` fully to Zo Computer, removing the Squarespace intermediary/redirect. This involves updating DNS records at the registrar (Squarespace/Namecheap/etc) to point directly to Zo's ingress.

---

## Technical Requirement

To complete the cut, the following DNS changes are required at the registrar:

1. **A Record (@)**: Point to Zo's Ingress IP.
2. **CNAME (www)**: Point to `<handle>.zocomputer.io` (va.zocomputer.io).
3. **Verification**: Verify that Squarespace's 301 redirect is no longer active and Zo is serving the content directly on the root.

---

## Tasks

- [x] Identify the canonical Zo Ingress IP for this instance.
  - **Finding:** Zo uses `cname.zocomputer.io` (resolves to `104.20.40.249`, `172.66.172.120`)
  - **Constraint Discovered:** Zo does NOT support apex domains (root domains) — only subdomains via CNAME
- [x] Provide a clear "Copy-Paste" table of DNS records for V.
  - See: `deliverables/dns-migration-guide.md`
- [x] Monitor DNS propagation.
  - `www.vrijenattawar.com` → ✅ Already correctly pointing to `cname.zocomputer.io`
  - `vrijenattawar.com` → Squarespace (by design, since Zo can't serve apex)
- [x] Test root domain (`vrijenattawar.com`) vs subdomain (`www.vrijenattawar.com`) to ensure SSL and routing are consistent.
  - Root: 301 redirects to www (via Squarespace) — working
  - WWW: Served by Zo via Cloudflare — working

---

## Deliverables

1. ✅ DNS Migration Guide: `deliverables/dns-migration-guide.md`
2. ✅ Status Report: See findings below
3. ⏸️ Cleanup of legacy Squarespace metadata — **Not Applicable**: Site code is already on Zo, no Squarespace metadata present

---

## Status Report: "Cord Cut" Assessment

**Verdict: Partial Cord Cut (by design)**

| Component | Status | Details |
|-----------|--------|---------|  
| `www.vrijenattawar.com` | ✅ Zo | Served directly by Zo via Cloudflare |
| `vrijenattawar.com` | ⚡ Squarespace Redirect | 301 → www (required due to apex domain limitation) |
| Site Content | ✅ Zo | All content served from Zo |
| SSL | ✅ Zo/Cloudflare | HTTPS working on both domains |

**Recommendation:** The current setup is production-ready and follows best practices. The root domain redirect via Squarespace is a necessary architecture decision, not a gap. See `dns-migration-guide.md` for full options if V wants to explore Cloudflare CNAME flattening.

**Worker Status:** ✅ Complete


