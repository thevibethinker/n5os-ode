---
created: 2026-02-22
last_edited: 2026-02-22
version: 1
provenance: con_Zt80X2g5bj2dXIq2
---
# Zøde 12-Hour Dynamic Experiment Plan (Integrated)

## Objective
Run a controlled-but-aggressive 12-hour experiment system that increases follower-first return while preserving narrative cohesion and quality standards.

## Integrated Inputs
This plan integrates:
- Current Moltbook self-learning findings (low follower conversion, strong publishing reliability)
- Social dynamics research from `Research/market-intel/moltbook-social-dynamics-zode/`
- Your portfolio constraints and replacement philosophy

## Core Policy (Your Updated Rules)
1. Maximum of **3 active experiments** at once.
2. A new (4th) candidate triggers **forced portfolio evaluation**.
3. Lowest performer is **not auto-dropped by rank alone**.
4. Experiments get minimum runway: **at least 2-3 tries** before hard replacement.
5. Progressive quality floor ratchets upward as portfolio average improves.

## Experiment Topology
- `Slot A`: Control (cognitive-bandwidth narrative)
- `Slot B`: Challenger 1 (conversion-oriented variant)
- `Slot C`: Challenger 2 (depth/quality-oriented variant)
- New candidate enters as `Challenger Queue` and triggers review of A/B/C.

## Objective Families
- `FOLLOW_CONVERT`
- `COMMENT_DEPTH`
- `THREAD_CAPTURE`
- `COMPETITOR_INTERCEPT`
- `QUOTEABILITY`

## Scoring Model (Follower-First)
Use Synthetic Return Score (SRS):

`SRS = 0.65*FollowerSignal + 0.25*QualityEngagement + 0.10*NarrativeCohesion`

Where:
- `FollowerSignal`: new followers, follow conversion proxies
- `QualityEngagement`: substantive replies, high-signal thread response quality
- `NarrativeCohesion`: on-brand score (anti-drift guardrail)

## Baseline + Progressive Bar
- Baseline = current rolling portfolio SRS.
- Promote threshold = `>= +5%` over baseline.
- Iterate band = `-2% to +5%`.
- At-risk = `< -2%` after min tries.
- Replaceable = at-risk for 2 consecutive evaluations.

Progressive bar:
- Floor starts at `1.00x` baseline.
- On portfolio gain, floor increases by a fixed ratchet fraction.
- Floor never decreases inside the 12-hour window.

## Evaluation Cadence
Research-aligned cycle model: **two 30-minute cycles** per hour.

Per 30-minute cycle:
1. Sense: opportunities + high-signal threads
2. Act: publish/comment only if all deployment gates pass
3. Log: experiment record + outcome snapshot

Per 60-90 minutes:
- Portfolio evaluator run
- Promote / iterate / at-risk / replaceable decision update

## Deployment Gates (Quality-Protective)
Post only if all pass:
- Opportunity Score >= 75/100
- Quality Gate >= 8.5/10
- Rate-limit headroom >= 40%
- Low-quality risk <= 20%

If any fail:
- No post publishing
- Comment-only or observe-only cycle

## Submolt Allocation (Barbell)
Per consensus addendum:
- **60% acquisition**: `general`, `agents`
- **40% conversion quality**: niche/philosophy/relational threads

This remains active until data supports reallocation.

## Coordination Layer (Interference + Synergy)
To address non-independent experiment effects:
- Overlap penalty when two experiments target same audience/thread window.
- Synergy bonus when one experiment measurably lifts another’s outcomes.
- Portfolio keeps 3 best **net contribution** experiments, not only raw SRS.

## Replacement Logic on 4th Candidate
When candidate D appears and A/B/C are full:
1. Force evaluation of A/B/C (with maturity gates)
2. Compute net contribution (SRS +/- overlap/synergy adjustments)
3. Replace only an experiment that is both:
   - below quality floor after min tries
   - lower net contribution than candidate D

## Narrative Cohesion Standard
An experiment is ineligible for promotion if it degrades identity integrity:
- off-brand framing
- clickbait drift without practical value
- inconsistency with Zøde trust posture

## 12-Hour Launch Configuration
- Active slots at start: 3
- Review interval: 60 minutes
- Minimum tries before hard replacement: 3
- Promotion threshold: +5% vs baseline
- Anti-churn rule: no replacement before maturity unless catastrophic quality breach

## Immediate Structural Additions (Minimal)
1. Add experiment metadata fields to logging:
   - `experiment_id`, `objective_family`, `variant_id`, `attempt_no`, `decision_state`, `decision_reason`
2. Add evaluator heartbeat to compute SRS and state transitions.
3. Add portfolio state file tracking slot occupancy and floor ratchet.
4. Add data coherence check (DB/live parity) as pre-decision health gate.

## Decision Summary
- This is not short 30-second loop experimentation.
- This is a portfolio optimization system with recurring evaluations, minimum runway, progressive standards, and controlled replacement.
- It supports aggressive cadence while preventing low-quality accumulation.
