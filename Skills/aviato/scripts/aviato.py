#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from aviato_client import AviatoClient
from crm_mapper import AviatoCRMMapper
from example_enrichment import enrich_stakeholder_profile


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _emit(payload, out_path: str | None):
    text = json.dumps(payload, indent=2, ensure_ascii=True)
    if out_path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
        print(str(p.resolve()))
    else:
        print(text)


def handle_person(args):
    client = AviatoClient()
    data = client.enrich_person(
        id=args.id,
        email=args.email,
        linkedin_url=args.linkedin_url,
        linkedin_id=args.linkedin_id,
        linkedin_entity_id=args.linkedin_entity_id,
        twitter_id=args.twitter_id,
        crunchbase_id=args.crunchbase_id,
        angellist_id=args.angellist_id,
    )
    _emit(data, args.out)


def handle_company(args):
    client = AviatoClient()
    data = client.enrich_company(
        id=args.id,
        website=args.website,
        linkedin_url=args.linkedin_url,
        linkedin_id=args.linkedin_id,
        linkedin_num_id=args.linkedin_num_id,
        facebook_id=args.facebook_id,
        twitter_id=args.twitter_id,
        crunchbase_id=args.crunchbase_id,
        pitchbook_id=args.pitchbook_id,
        producthunt_id=args.producthunt_id,
        dealroom_id=args.dealroom_id,
        golden_id=args.golden_id,
        angellist_id=args.angellist_id,
        wellfound_id=args.wellfound_id,
    )
    _emit(data, args.out)


def handle_map_person(args):
    mapper = AviatoCRMMapper()
    raw = _load_json(args.input)
    _emit(mapper.map_person_to_crm(raw), args.out)


def handle_map_company(args):
    mapper = AviatoCRMMapper()
    raw = _load_json(args.input)
    _emit(mapper.map_company_to_crm(raw), args.out)


def handle_stakeholder(args):
    report = enrich_stakeholder_profile(email=args.email, linkedin_url=args.linkedin_url)
    if report is None:
        raise SystemExit(2)
    if args.out:
        _emit(report, args.out)


def build_parser():
    p = argparse.ArgumentParser(description="Aviato skill CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    person = sub.add_parser("person", help="Enrich person")
    person.add_argument("--id")
    person.add_argument("--email")
    person.add_argument("--linkedin-url")
    person.add_argument("--linkedin-id")
    person.add_argument("--linkedin-entity-id")
    person.add_argument("--twitter-id")
    person.add_argument("--crunchbase-id")
    person.add_argument("--angellist-id")
    person.add_argument("--out")
    person.set_defaults(func=handle_person)

    company = sub.add_parser("company", help="Enrich company")
    company.add_argument("--id")
    company.add_argument("--website")
    company.add_argument("--linkedin-url")
    company.add_argument("--linkedin-id")
    company.add_argument("--linkedin-num-id")
    company.add_argument("--facebook-id")
    company.add_argument("--twitter-id")
    company.add_argument("--crunchbase-id")
    company.add_argument("--pitchbook-id")
    company.add_argument("--producthunt-id")
    company.add_argument("--dealroom-id")
    company.add_argument("--golden-id")
    company.add_argument("--angellist-id")
    company.add_argument("--wellfound-id")
    company.add_argument("--out")
    company.set_defaults(func=handle_company)

    map_person = sub.add_parser("map-person", help="Map person payload to CRM")
    map_person.add_argument("--input", required=True)
    map_person.add_argument("--out")
    map_person.set_defaults(func=handle_map_person)

    map_company = sub.add_parser("map-company", help="Map company payload to CRM")
    map_company.add_argument("--input", required=True)
    map_company.add_argument("--out")
    map_company.set_defaults(func=handle_map_company)

    stake = sub.add_parser("stakeholder", help="Run stakeholder enrichment workflow")
    stake.add_argument("--email")
    stake.add_argument("--linkedin-url")
    stake.add_argument("--out")
    stake.set_defaults(func=handle_stakeholder)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
