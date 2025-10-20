#!/usr/bin/env python3
import argparse, json, logging, os, re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
REFL_ROOT = WORKSPACE / "N5/records/reflections"
INCOMING = REFL_ROOT / "incoming"
PROCESSED = REFL_ROOT / "processed"
OUTPUTS = REFL_ROOT / "outputs"
STATE_FILE = REFL_ROOT / ".state.json"

OUTPUTS.mkdir(parents=True, exist_ok=True)

VOICE_BASE = WORKSPACE / "N5/prefs/communication/voice.md"
VOICE_SOCIAL = WORKSPACE / "N5/prefs/communication/social-media-voice.md"

def load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_run_iso": None, "processed_file_ids": []}

def save_state(state: Dict[str, Any]):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# --- Drive placeholder: we rely on Zo's Google Drive connector at command level ---
# This script assumes files are already synced into INCOMING, or are provided via --local-file.

REFLECTION_TYPES = [
    "product_strategy", "dilemma", "pitch_narrative", "announcement",
    "hiring", "founder_journal", "marketing", "ops_process"
]

def classify_reflection(text: str) -> List[str]:
    """Heuristic multi-label classifier (MVP)."""
    labels = []
    t = text.lower()
    checks = [
        ("product_strategy", ["roadmap", "product", "feature", "launch", "positioning", "gtm"]),
        ("dilemma", ["torn", "conflicted", "trade-off", "which should", "can't decide", "pros and cons"]),
        ("pitch_narrative", ["pitch", "investor", "deck", "narrative", "story arc", "vision"]),
        ("announcement", ["announce", "we're excited", "launching", "partnership", "now live"]),
        ("hiring", ["candidate", "hire", "recruiting", "job", "resume", "interview"]),
        ("founder_journal", ["i felt", "i learned", "as a founder", "we struggled", "what i realized"]),
        ("marketing", ["campaign", "performance", "ads", "conversion", "funnel"]),
        ("ops_process", ["process", "pipeline", "workflow", "sop", "system"]),
    ]
    for label, kws in checks:
        if any(kw in t for kw in kws):
            labels.append(label)
    if not labels:
        labels = ["founder_journal"]
    return labels

def decide_outputs(labels: List[str]) -> List[str]:
    """Map labels → output types."""
    outs = set()
    if "pitch_narrative" in labels or "announcement" in labels:
        outs.update(["linkedin_post", "blog_snippet"])
    if "product_strategy" in labels or "ops_process" in labels:
        outs.update(["executive_memo", "linkedin_post"])
    if "hiring" in labels:
        outs.update(["linkedin_post", "executive_memo"])
    if "founder_journal" in labels:
        outs.update(["linkedin_post"])  # journal → social voice
    if "marketing" in labels:
        outs.update(["executive_memo", "blog_snippet"])
    return list(outs or {"linkedin_post"})

def select_voice(output_type: str) -> Path:
    return VOICE_SOCIAL if output_type in {"linkedin_post", "blog_snippet"} else VOICE_BASE

def render_linkedin_post(text: str, labels: List[str]) -> str:
    # Minimal rendering; Zo will refine using the voice file when generating final copy.
    hook = """What if we're measuring the wrong thing?""" if "dilemma" in labels else """Here's a pattern I keep seeing:"""
    body = text.strip()
    cta = "What would you add?"
    return f"{hook}\n\n{body}\n\n—\nWhat stands out to you? {cta}"

def render_exec_memo(text: str, labels: List[str]) -> str:
    ts = datetime.now().strftime("%Y-%m-%d")
    return f"""# Executive Memo — Reflection Synthesis\n**Date:** {ts}\n\n## Context\n{text.strip()}\n\n## Initial Classification\n- {', '.join(labels)}\n\n## Next\n- Draft decisions/options\n- Risks + counterfactuals\n- Actions and owners\n"""

def render_blog_snippet(text: str, labels: List[str]) -> str:
    return f"""## Draft Blog Snippet\n\n{text.strip()}\n\n— Draft from reflection ({', '.join(labels)})\n"""

RENDERERS = {
    "linkedin_post": render_linkedin_post,
    "executive_memo": render_exec_memo,
    "blog_snippet": render_blog_snippet,
}

def process_file(path: Path, dry_run: bool = False) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    labels = classify_reflection(raw)
    outputs = decide_outputs(labels)

    slug = re.sub(r"[^a-z0-9-]", "-", path.stem.lower())
    out_dir = OUTPUTS / datetime.now().strftime("%Y-%m-%d") / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = {}
    for otype in outputs:
        render = RENDERERS[otype]
        content = render(raw, labels)
        fname = out_dir / f"{slug}.{ 'md' if otype!='linkedin_post' else 'post.md'}"
        if not dry_run:
            fname.write_text(content, encoding="utf-8")
        artifacts[otype] = str(fname)
        logger.info(f"✓ Generated {otype}: {fname}")

    # Persist simple manifest
    manifest = {"source": str(path), "labels": labels, "outputs": artifacts}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pull", action="store_true", help="(Placeholder) Pull from Drive via command layer")
    parser.add_argument("--process", action="store_true", help="Process files in INCOMING")
    parser.add_argument("--local-file", type=str, help="Process a single local file for testing")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    state = load_state()

    if args.local_file:
        p = Path(args.local_file)
        if not p.exists():
            logger.error(f"Not found: {p}")
            return 1
        process_file(p, dry_run=args.dry_run)
        return 0

    if args.process:
        files = list(INCOMING.glob("**/*"))
        files = [f for f in files if f.is_file() and f.suffix.lower() in {".md", ".txt"}]
        logger.info(f"Found {len(files)} incoming files")
        for f in files:
            manifest = process_file(f, dry_run=args.dry_run)
            # Move processed
            dest = PROCESSED / f.name
            if not args.dry_run:
                f.rename(dest)
            state.setdefault("processed_file_ids", []).append(f.name)
        state["last_run_iso"] = datetime.now().isoformat()
        save_state(state)
        logger.info("✓ Processing complete")
        return 0

    logger.info("Nothing to do. Use --process or --local-file.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
