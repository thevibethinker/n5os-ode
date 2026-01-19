---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: con_DzEDX5MVCiVOpEA4
---

# DNS Migration Guide: vrijenattawar.com

## Current State Assessment

| Domain | Current Pointing | Status |
|--------|-----------------|--------|
| `www.vrijenattawar.com` | ✅ `cname.zocomputer.io` → Zo | **Correctly configured** |
| `vrijenattawar.com` (root) | ❌ Squarespace IPs (198.x.x.x) | **Still through Squarespace** |

**What happens now:**
1. User visits `vrijenattawar.com` → Squarespace receives → 301 redirect to `www.vrijenattawar.com`
2. User visits `www.vrijenattawar.com` → Zo serves content directly (via Cloudflare)

---

## ⚠️ Important Constraint: Zo Does Not Support Apex Domains

Per Zo's documentation[^1]:

> **Subdomains only**: You must use a subdomain like `blog.example.com`. Apex domains (like `example.com`) are not supported because they cannot have CNAME records.

**This means:** You **cannot** point `vrijenattawar.com` directly to Zo's ingress. The architecture requires CNAME records, which are not allowed on root/apex domains per DNS standards.

---

## Options

### Option A: Keep Squarespace Redirect (Current Setup) ✅ Recommended

**How it works:**
- Root domain stays on Squarespace (redirect-only)
- Squarespace 301 redirects `vrijenattawar.com` → `www.vrijenattawar.com`
- `www` is served by Zo

**Pros:**
- Already working
- SEO-friendly (301 is a permanent redirect, search engines follow it)
- No additional configuration needed

**Cons:**
- Squarespace subscription may still be needed for redirect
- One extra hop for root domain visitors (~50-100ms)

**Action Required:** None. This is the current state.

---

### Option B: Transfer Domain to Cloudflare (CNAME Flattening)

If you want to fully cut ties with Squarespace DNS, you can transfer `vrijenattawar.com` to Cloudflare as your registrar. Cloudflare offers "CNAME flattening" which allows apex domains to effectively use CNAME-like behavior.

**How it works:**
- Transfer domain to Cloudflare Registrar
- Set up CNAME flattening for the root domain
- Both `@` and `www` resolve to Zo

**Pros:**
- Complete independence from Squarespace
- Single authoritative DNS provider
- Free SSL at edge

**Cons:**
- Domain transfer process (5-7 days)
- Need to recreate all DNS records
- Risk of downtime during transfer

**DNS Records After Transfer:**

| Type | Name | Value |
|------|------|-------|
| CNAME | `@` | `cname.zocomputer.io` (flattened) |
| CNAME | `www` | `cname.zocomputer.io` |

---

### Option C: Use Registrar's HTTP Redirect

Most registrars (including Squarespace Domains, Namecheap, etc.) offer HTTP redirect services at the DNS level. This doesn't require hosting.

**How it works:**
- Point root A record to registrar's redirect servers
- Configure redirect: `vrijenattawar.com` → `https://www.vrijenattawar.com`
- `www` continues to be served by Zo

**At Squarespace Domains:**
1. Go to DNS settings
2. Find "URL Redirect" or "Forwarding" option
3. Set: `vrijenattawar.com` → `https://www.vrijenattawar.com` (301 permanent)

---

## Verification Commands

```bash
# Check root domain
dig A vrijenattawar.com +short
# Current: 198.x.x.x (Squarespace)

# Check www subdomain  
dig CNAME www.vrijenattawar.com +short
# Current: cname.zocomputer.io ✅

# Test redirect behavior
curl -sI https://vrijenattawar.com | grep -E "^(HTTP|location)"
# Should show: 301 redirect to www

# Test www serving
curl -sI https://www.vrijenattawar.com | grep -E "^(HTTP|server)"
# Should show: cloudflare (Zo's CDN)
```

---

## Recommendation

**Keep Option A (current setup)** unless there's a specific reason to cut Squarespace completely.

The current architecture is:
- ✅ Production-ready
- ✅ SEO-friendly (301 redirect preserves link equity)
- ✅ Functional for all visitors
- ✅ `www.vrijenattawar.com` is the canonical URL (best practice)

If you want to eventually eliminate Squarespace entirely, **Option B (Cloudflare transfer)** is the cleanest long-term solution, but requires more effort.

---

## Current Technical Details

**Zo Ingress:**
- CNAME Target: `cname.zocomputer.io`
- Resolves to: `104.20.40.249`, `172.66.172.120` (Cloudflare edge)

**Squarespace IPs (current root):**
- `198.185.159.144`
- `198.185.159.145`
- `198.49.23.144`
- `198.49.23.145`

---

[^1]: https://docs.zocomputer.com/custom-domains

