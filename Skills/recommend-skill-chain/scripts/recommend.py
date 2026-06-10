#!/usr/bin/env python3
"""
recommend-skill-chain: recommend an ordered chain of atomic visual skills for a spec.

Pipeline:
  1. Load spec (file or inline text).
  2. Load catalog (skills with chain_metadata).
  3. Heuristic prefilter — flag obvious conflicts (e.g., bolder + distill).
  4. Call /zo/ask with structured-output schema to pick chain or ask clarifying Q.
  5. Validate, write JSON.

NOTE: Reconstructed from compiled bytecode (original source was lost);
behavior matches the original CLI surface and decision logic.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from load_catalog import load_catalog

try:
    import requests
except ImportError:
    sys.stderr.write("ERROR: pip install requests\n")
    sys.exit(2)

ZO_API_URL = "https://api.zo.computer/zo/ask"
MODEL_NAME = os.environ.get("RECOMMEND_CHAIN_MODEL", "anthropic:claude-fable-5")

FLAVOR_CONFLICTS = (
    ("bold", "minimal"),
    ("bold", "subtle"),
    ("playful", "serious"),
    ("dense", "airy"),
    ("ornate", "minimal"),
    ("loud", "quiet"),
)

FLAVOR_WORDS = (
    "bold", "minimal", "playful", "serious", "dense", "airy", "elegant",
    "raw", "polished", "experimental", "professional", "warm", "cold",
    "calm", "energetic", "swiss", "zine", "editorial", "high-end", "luxury",
    "technical", "maximalist", "restrained", "confident", "joyful",
    "terminal", "utilitarian",
)

DIRECTOR_SKILL_PATH = "/home/workspace/Skills/frontend-visual-director/SKILL.md"

SYSTEM_PROMPT = (
    "You are a visual design chain recommender. Given a SPEC and a CATALOG of atomic skills, "
    "output an ordered chain of skills to apply, a director delegation, OR a clarifying question "
    "if the spec is too ambiguous to act on. Rules:\n"
    "- Only use skills present in the catalog.\n"
    "- Respect composes_poorly_with: never put conflicting skills in one chain.\n"
    "- Order matters: generators first, transforms middle, evaluate last.\n"
    "- A chain should end with an evaluate-stage skill when one exists.\n"
    "- Prefer 2-5 skills. Do not pad the chain.\n"
    "- If the spec lacks a target or a flavor direction, ask a clarifying question instead.\n"
)

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": ["chain", "clarifying_question", "director_delegation"]},
        "chain": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "reasoning": {"type": "string"},
                    "when_to_use": {"type": "string"},
                    "expected_effect": {"type": "string"},
                },
                "required": ["skill", "reasoning"],
            },
        },
        "rationale": {"type": "string"},
        "skipped_skills": {"type": "array", "items": {"type": "string"}},
        "question": {"type": "string"},
        "why_uncertain": {"type": "string"},
        "options": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["kind"],
}


def load_spec(spec_arg):
    if spec_arg == "-":
        return sys.stdin.read()
    p = Path(spec_arg)
    if p.exists() and p.is_file():
        return p.read_text(errors="ignore")
    return spec_arg


def find_conflicts(spec_text):
    low = spec_text.lower()
    hits = []
    for a, b in FLAVOR_CONFLICTS:
        if a in low and b in low:
            hits.append(f"{a} vs {b}")
    return hits


def build_heuristic_signals(spec_text):
    low = spec_text.lower()
    signals = []
    words = len(spec_text.split())
    if words < 20:
        signals.append(f"- spec is very short ({words} words) — likely needs spec-writing or clarification first")
    for a, b in FLAVOR_CONFLICTS:
        if a in low and b in low:
            signals.append(f"- conflicting flavor: spec mentions both '{a}' and '{b}'")
    if not any(w in low for w in FLAVOR_WORDS):
        signals.append("- no flavor/mood words detected in spec — output may default to modal aesthetic")
    return "\n".join(signals) if signals else "- (no red flags detected)"


def deterministic_clarification(spec_text, target):
    """Deterministic short-circuits that don't need the LLM."""
    conflicts = find_conflicts(spec_text)
    if conflicts:
        return {
            "kind": "clarifying_question",
            "question": "This spec has conflicting visual signals. Which direction is primary, and which is only a guardrail?",
            "why_uncertain": "Conflicts detected: " + ", ".join(conflicts)
            + ". Picking a chain now would either cancel itself out or over-optimize for the wrong axis.",
            "options": [
                "Amplify the design first; keep restraint only as a guardrail.",
                "Distill the design first; use one bold accent only where it serves hierarchy.",
                "Run spec-writing first to turn the tension into a concrete taste direction.",
            ],
        }
    words = len(spec_text.split())
    if words < 12:
        return {
            "kind": "clarifying_question",
            "question": "What flavor, audience, and success scenario should drive this visual chain?",
            "why_uncertain": f"The spec is only {words} words, so the recommender would default toward generic design patterns.",
            "options": [],
        }
    if not target and ("existing" in spec_text.lower() or "current" in spec_text.lower()):
        return {
            "kind": "clarifying_question",
            "question": "What target should the chain operate on?",
            "why_uncertain": "The spec references an existing surface, but no URL, file path, route, or component target was provided.",
            "options": [],
        }
    return None


def deterministic_director_delegation(spec_text):
    """If the request is broad and the director skill exists, delegate."""
    if not Path(DIRECTOR_SKILL_PATH).exists():
        return None
    low = spec_text.lower()
    broad_markers = ("redesign", "overhaul", "whole site", "entire", "from scratch", "every page")
    if any(m in low for m in broad_markers):
        return {
            "kind": "director_delegation",
            "rationale": "Broad frontend/design request that needs operating-model diagnosis before chain selection.",
            "delegate_to": "frontend-visual-director",
            "action_mode": "checkpoint_plan",
            "instructions": (
                "Use frontend-visual-director to classify surface size, language novelty, stakes, "
                "reference needs, and stop/go policy before selecting atomic skills."
            ),
            "fallback": (
                "If the director skill is unavailable, perform the same inline diagnosis: surface x language mode, "
                "then choose run_chain, plan_lite_then_run, checkpoint_plan, or pulse_plan."
            ),
            "why_not_chain": "Atomic chain selection is premature before design-language and execution-policy diagnosis.",
        }
    return None


def call_zo_ask(spec_text, catalog, target, signals):
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        sys.stderr.write("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set in environment\n")
        sys.exit(2)

    catalog_lines = []
    for slug, entry in catalog.items():
        catalog_lines.append(json.dumps({"skill": slug, **entry}))

    prompt = (
        SYSTEM_PROMPT
        + "\n\nSPEC:\n" + spec_text
        + ("\n\nTARGET:\n" + target if target else "")
        + "\n\nHEURISTIC SIGNALS:\n" + signals
        + "\n\nCATALOG (one JSON object per line):\n" + "\n".join(catalog_lines)
    )

    resp = requests.post(
        ZO_API_URL,
        headers={"authorization": token, "content-type": "application/json"},
        json={"input": prompt, "model_name": MODEL_NAME, "output_format": OUTPUT_SCHEMA},
        timeout=180,
    )
    resp.raise_for_status()
    out = resp.json().get("output")
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except Exception:
            return {"kind": "clarifying_question", "question": "PARSE_ERROR", "why_uncertain": out[:500], "options": []}
    return out


def normalize_result(result, catalog):
    """Drop unknown skills and resolve composes_poorly_with conflicts (keep earlier skill)."""
    if result.get("kind") != "chain":
        return result
    chain = result.get("chain") or []
    seen = []
    cleaned = []
    skipped = list(result.get("skipped_skills") or [])
    for step in chain:
        slug = step.get("skill")
        if slug not in catalog:
            skipped.append(slug)
            continue
        bad = set(catalog[slug].get("composes_poorly_with") or [])
        if bad & set(seen):
            skipped.append(slug)
            continue
        seen.append(slug)
        cleaned.append(step)
    result["chain"] = cleaned
    result["skipped_skills"] = skipped
    return result


def main():
    ap = argparse.ArgumentParser(description="Recommend a chain of visual skills for a spec")
    ap.add_argument("spec", help="Path to spec file or inline text")
    ap.add_argument("--target", default="", help="URL or path the chain operates on")
    ap.add_argument("--skills-root", default="/home/workspace/Skills")
    ap.add_argument("--out", default="-", help="Output JSON path or '-' for stdout")
    ap.add_argument("--no-llm", action="store_true", help="Skip /zo/ask, just emit catalog summary (debug)")
    args = ap.parse_args()

    spec_text = load_spec(args.spec)
    catalog = load_catalog(args.skills_root)
    if not catalog:
        sys.stderr.write("ERROR: empty catalog. Did you run the W1 enrichment?\n")
        sys.exit(1)

    delegation = deterministic_director_delegation(spec_text)
    if delegation:
        result = delegation
        result["_source"] = "deterministic_director_delegation"
    elif args.no_llm:
        result = {
            "kind": "clarifying_question",
            "question": "(--no-llm) catalog dry-run",
            "why_uncertain": f"catalog has {len(catalog)} skills",
            "options": [],
            "_source": "deterministic_prefilter",
        }
    else:
        clar = deterministic_clarification(spec_text, args.target)
        if clar:
            result = clar
            result["_source"] = "deterministic_prefilter"
        else:
            signals = build_heuristic_signals(spec_text)
            result = call_zo_ask(spec_text, catalog, args.target, signals)
            result = normalize_result(result, catalog)
            result["_source"] = "zo_ask"
            result["_heuristic_signals"] = signals

    payload = json.dumps(result, indent=2)
    if args.out == "-":
        print(payload)
    else:
        Path(args.out).write_text(payload)
        print(f"✓ wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
