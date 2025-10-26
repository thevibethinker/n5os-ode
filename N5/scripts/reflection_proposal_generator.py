#!/usr/bin/env python3
import argparse, json, logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
REFL_ROOT = WORKSPACE / "N5/records/reflections"
REGISTRY = REFL_ROOT / "registry/registry.json"
PROPOSALS_DIR = WORKSPACE / "Records/Reflections/Proposals"
BELIEFS_DIR = WORKSPACE / "Knowledge/V-Beliefs"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def naive_key_points(text: str) -> list[str]:
    # Extremely lightweight heuristic; will be replaced by better extractor
    lines = [l.strip(" \t-•") for l in text.splitlines() if l.strip()]
    points = []
    for l in lines:
        if len(l.split()) > 4 and l[0].isupper():
            points.append(l)
    return points[:12]


def generate_proposal_md(reflection_path: Path, summary_path: Path, detail_path: Path) -> str:
    raw = load_text(reflection_path)
    key_points = naive_key_points(raw)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    social_angles = []
    for p in key_points[:6]:
        social_angles.append({
            "hook": f"What if {p.split()[0].lower()} isn\'t the real problem?",
            "angle": p,
            "formats": {
                "linkedin": f"Hook → 2-3 lines context → takeaway → CTA\n\n• {p}\n\nCTA: Want the full breakdown?",
                "tweet": f"{p} — thread incoming?"
            }
        })

    memo_angles = []
    for p in key_points[:6]:
        memo_angles.append({
            "thesis": p,
            "structure": ["Context", "Evidence", "Implications", "Action"]
        })

    md = [
        f"# Reflection Proposal\n\nProcessed: {stamp}\n\n",
        f"Source: `{reflection_path}`\n\n",
        "## Key Points (draft)\n",
        *[f"- {kp}\n" for kp in key_points],
        "\n## Social Angles (draft)\n",
        *[f"- Hook: {a['hook']}\n  - Angle: {a['angle']}\n  - LinkedIn: {a['formats']['linkedin']}\n  - Tweet: {a['formats']['tweet']}\n\n" for a in social_angles],
        "## Executive Memo Options (draft)\n",
        *[f"- Thesis: {m['thesis']}\n  - Structure: {', '.join(m['structure'])}\n\n" for m in memo_angles],
        "---\n",
        "Which of these do you want me to create? Reply with selections and I\'ll generate the outputs."
    ]
    return "".join(md)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reflection", required=True, help="Absolute path to reflection text file")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--detail", required=True)
    args = parser.parse_args()

    proposal_md = generate_proposal_md(Path(args.reflection), Path(args.summary), Path(args.detail))
    out_path = PROPOSALS_DIR / (Path(args.reflection).stem + "_proposal.md")
    save_text(out_path, proposal_md)
    logger.info(f"✓ Proposal written: {out_path}")
    print(str(out_path))

if __name__ == "__main__":
    main()
