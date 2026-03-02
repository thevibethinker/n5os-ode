---
name: zoren-hotline
description: "[DEPRECATED] The Vibe Pill Hotline — Zøren voice AI concierge. Transferred to Zoputer on 2026-03-02. va-side runtime expunged. Archives at N5/archives/zoren-hotline-deprecated-20260302/."
compatibility: Created for Zo Computer (Zoputer deployment)
metadata:
  author: va.zo.computer
  version: 1.0
  updated: 2026-03-02
  brand: The Vibe Pill
  concierge: Zøren
  phone: (415) 340-8017
  status: deprecated
  deprecated_date: 2026-03-02
  transferred_to: zoputer
  zoputer_endpoint: https://zoren-hotline-native-zoputer.zocomputer.io
---

# ⚠️ DEPRECATED — Transferred to Zoputer

**Effective:** 2026-03-02
**Status:** va-side implementation deprecated and expunged
**Phone:** +1 415-340-8017 now routes to Zoputer endpoint: `https://zoren-hotline-native-zoputer.zocomputer.io`

## What happened

The Zøren hotline (Vibe Pill voice AI concierge) was fully transferred from va to Zoputer.

**va-side teardown completed:**
- Service `zoren-hotline-webhook` (svc_EMlC6VztSCo, port 4243) deleted
- Runtime scripts, prompts, and references removed
- Knowledge base (`Knowledge/vibe-pill-hotline/`, 112 files) archived and deleted
- Dataset (`Datasets/vibe-pill-calls/`) archived and deleted
- Build artifacts (`N5/builds/zoren-hotline/`) archived and deleted
- Port 4243 freed in PORT_REGISTRY

**Archives preserved at:** `N5/archives/zoren-hotline-deprecated-20260302/`
- `knowledge-vibe-pill-hotline.tar.gz`
- `datasets-vibe-pill-calls.tar.gz`
- `builds-zoren-hotline.tar.gz`
- `skills-zoren-hotline-runtime.tar.gz`

**Git history preserved.** No commits were rewritten.

## Secrets requiring manual rotation

These va-side secrets were used by the old hotline and should be revoked/rotated in [Settings → Advanced](/?t=settings&s=advanced):

- `VAPI_HOTLINE_SECRET`
- `VAPI_API_KEY` (⚠️ shared with Zoseph + Career Coaching Hotline — rotate carefully)
- `ANTHROPIC_API_KEY` (⚠️ shared — do NOT revoke, just audit access)
- `AGENTMAIL_API_KEY`
- `AIRTABLE_API_KEY` (⚠️ shared with many services — do NOT revoke)
- `STRIPE_SECRET_KEY` (⚠️ shared — do NOT revoke)
- `ZO_API_KEY` / `ZOPUTER_API_KEY`

**Recommendation:** Only revoke `VAPI_HOTLINE_SECRET` and `ZOPUTER_API_KEY` outright. The others are shared with active va services. For shared keys, audit that Zoputer has its own copies, then consider rotation on a schedule.