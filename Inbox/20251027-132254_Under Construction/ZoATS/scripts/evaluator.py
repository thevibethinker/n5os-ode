#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def load_json(p: Path):
    return json.loads(Path(p).read_text())

def score_candidate(rubric: dict, evidence: dict, weights: dict) -> dict:
    def w(key, default=0.0):
        return weights.get(key, default)

    must = sum(c.get("score", 0) * c.get("weight", 1.0) for c in rubric.get("must_haves", []))
    nice = sum(c.get("score", 0) * c.get("weight", 1.0) for c in rubric.get("nice_to_haves", []))
    story = evidence.get("story_authenticity", 0)
    cross = evidence.get("crossref_signals", 0)

    total = (
        must * w("must_have", 0.5) +
        nice * w("nice_to_have", 0.15) +
        story * w("story_authenticity", 0.2) +
        cross * w("crossref_signals", 0.15)
    )

    return {
        "score": round(total, 3),
        "components": {
            "must_haves": must,
            "nice_to_haves": nice,
            "story_authenticity": story,
            "crossref_signals": cross
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rubric", help="Path to role rubric JSON")
    ap.add_argument("evidence", help="Path to candidate evidence JSON")
    ap.add_argument("--weights", default="../configs/scoring.defaults.json")
    args = ap.parse_args()

    rubric = load_json(Path(args.rubric))
    evidence = load_json(Path(args.evidence))
    weights = load_json(Path(args.weights))

    result = score_candidate(rubric, evidence, weights["weights"] | {"thresholds": weights.get("thresholds", {})})
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
