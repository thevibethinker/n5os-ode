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

- [ ] Identify the canonical Zo Ingress IP for this instance.
- [ ] Provide a clear "Copy-Paste" table of DNS records for V.
- [ ] Monitor DNS propagation.
- [ ] Test root domain (`vrijenattawar.com`) vs subdomain (`www.vrijenattawar.com`) to ensure SSL and routing are consistent.

---

## Deliverables

1. DNS Migration Guide (Markdown).
2. Status report once the "Cord Cut" is verified.
3. Cleanup of any legacy Squarespace metadata in the site code.

