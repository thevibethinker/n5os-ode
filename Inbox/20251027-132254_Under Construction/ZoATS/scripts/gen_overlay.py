#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description="Generate a ZoATS overlay from a base profile and inputs")
    p.add_argument("--company", required=True)
    p.add_argument("--job", required=True)
    p.add_argument("--profile", default="engineer.founding")
    p.add_argument("--ingest", help="jobs@company.com", required=True)
    p.add_argument("--cc", help="zo cc address", default="zo@company.com")
    p.add_argument("--voice", help="path to founder voice note", default="")
    args = p.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_dir = root / "overlays"
    out_dir.mkdir(parents=True, exist_ok=True)

    overlay = {
        "overlay_id": f"{args.company.lower()}.{args.job}",
        "company": {
            "name": args.company,
            "industry": "",
            "values": [],
            "voice_profile": args.voice
        },
        "job": {
            "slug": args.job,
            "title": args.job.replace("-", " ").title(),
            "location": "",
            "rubric": f"profiles/{args.profile}.rubric.json",
            "email_templates": f"templates/{args.profile.split('.')[0]}.email.md"
        },
        "email": {
            "ingest_address": args.ingest,
            "cc_zo": args.cc
        }
    }

    out_path = out_dir / f"{args.company.lower()}.{args.job}.json"
    out_path.write_text(json.dumps(overlay, indent=2))
    print(str(out_path))

if __name__ == "__main__":
    main()
