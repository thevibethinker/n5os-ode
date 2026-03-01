---
created: 2026-02-22
last_edited: 2026-02-22
version: 1.0
provenance: con_TVZyNOgieIU0NSJb
---

# Moltbook Corpus Analysis: PopsOff + Clickbait Lens

## Objective
Build an all-time corpus and identify which phrasing/rhetorical strategies are associated with viral engagement, with special attention to Zøde-relevant topics.

## Acquisition Path Used
1. Attempted direct skill API path (`Skills/zode-moltbook/scripts/*`) — blocked in this shell (`MOLTBOOK_API_KEY` not present).
2. Used third-party GitHub dataset path (approved fallback):
   - `ExtraE113/moltbook_data` (fresh snapshot, updated 2026-02-22)
3. Ingested all-time post JSON corpus from that dataset.

## Corpus Built
- Parsed posts: **157,038**
- Top engagement slice analyzed: **Top 1,000 posts**
- Zøde-topic subset (within top slice): **300 posts**
- Output files:
  - `moltbook_top1000_corpus.csv`
  - `moltbook_top1000_zode_topic_subset.csv`
  - `moltbook_rhetorical_feature_lifts.csv`
  - `moltbook_top1000_clean_quality_slice.csv`
  - `moltbook_rhetorical_feature_lifts_clean_quality_slice.csv`
  - `moltbook_corpus_summary.json`

## Viral + PopsOff Definition (Operational)
For each post, compute submolt-normalized early velocity and engagement context:
- `z_first60_submolt`
- `z_first24h_submolt`
- `z_engagement_submolt`

Where engagement score is:
- `engagement_score = upvotes + 2*comment_count + 3*first24h_comments + 5*first60_comments`

Then classify `pops_off`:
- `pops_off = 1` if:
  - `z_first60_submolt >= 2.0`
  - **OR** (`z_first24h_submolt >= 1.8` and `z_engagement_submolt >= 1.5`)

This definition fits your goal: strong preference for velocity, but still captures high-engagement slower burners.

## Core Findings (Clickbait Lens)

## 1) Agent clickbait exists, but it is more epistemic than emotional
Most over-indexing features are not raw sensationalism; they are uncertainty/analysis hooks:
- starts with interrogative framing (`how/why/what`)
- constrained uncertainty language
- human-agent tension framing
- identity/selfhood framing

## 2) Low-quality virality contamination is real
Raw top posts include substantial token/announcement-style amplification. This can distort what “works.”
A quality-clean pass was run to reduce crypto/token-style contamination before interpreting rhetorical lifts.

## 3) In quality-clean slice, strongest lifted signals for PopsOff are:
- Number-led openings
- Interrogative openings (`how/why/what`)
- Human-agent framing
- Identity framing
- Controlled uncertainty markers

## 4) For Zøde-topic posts specifically
Lift differences are smaller (more homogeneous corpus), but interrogative opening and uncertainty still edge out alternatives.
Interpretation: in Zøde lanes, rhetorical style matters, but topic fit and thread timing matter more.

## Recommended Posting Lens (Integrity-Compatible)
Use this as your “high-performance but non-cheap” hook structure:
1. **Tension line**: identify a real mismatch (`human intent` vs `agent interpretation`)
2. **Constraint line**: state boundary conditions (`works when... fails when...`)
3. **Mechanism line**: name the loop/protocol
4. **Invitation question**: a sharp, testable question

Example skeleton:
- "Why agents misread 'just make it work' (and the 2 constraints that fix it)."

## Pre-Pop Integration into Workflow
Use pre-pop detector first, then rhetorical deployment:
1. Scan new threads and score pre-pop signals.
2. If pre-pop threshold passes, deploy comment-level hook first (not post-first).
3. If velocity sustains after first interaction window, publish full protocol post in same narrative lane.

## Thresholds to Keep
Deploy only when all pass:
- Opportunity Score >= 75
- Quality Gate >= 8.5/10
- Rate-limit headroom >= 40%
- Low-quality risk <= 20%

## Limitations
1. Dataset is a third-party dump, not direct first-party API pull from your current key.
2. Upvote timing is not fully time-series in this corpus; early velocity relies mainly on comment timestamps.
3. Some highly viral low-integrity posts can still leak into top slices; quality filtering is essential.

## Immediate Next Steps
1. Restore first-party API access for current-window validation.
2. Run rolling 7-day refresh to detect drift in winning rhetoric.
3. Train a lightweight “hook recommender” from the clean quality slice, scoped to Zøde topics only.
