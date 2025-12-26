#!/usr/bin/env python3
"""Backfill Short.io links into the local catalog."""
import argparse
import logging
import requests
from shortio_link_service import load_secret, persist_link_record

logging.basicConfig(format="%(asctime)sZ %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE = "https://api.short.io"
LINKS_ENDPOINT = "/api/links"
DOMAINS_ENDPOINT = "/api/domains"


def fetch_domains(api_key: str):
    url = f"{API_BASE}{DOMAINS_ENDPOINT}"
    headers = {"Authorization": api_key}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_links(api_key: str, domain_id: int, page: int = 1, limit: int = 100):
    url = f"{API_BASE}{LINKS_ENDPOINT}"
    headers = {"Authorization": api_key}
    params = {"domain_id": domain_id, "page": page, "limit": limit}
    response = requests.get(url, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill Short.io links")
    parser.add_argument("--domain-id", type=int, help="Short.io domain ID to target")
    parser.add_argument("--limit", type=int, default=100, help="Number of links per page")
    args = parser.parse_args()

    api_key = load_secret()
    if not api_key:
        logger.error("SHORT_IO_KEY is missing; aborting backfill.")
        return 1

    try:
        domain_id = args.domain_id
        if not domain_id:
            domains = fetch_domains(api_key)
            if not domains:
                logger.error("No domains returned from Short.io.")
                return 1
            domain = domains[0]
            domain_id = domain.get("id")
            logger.info("Using domain %s (%s)", domain_id, domain.get("hostname"))

        total = 0
        page = 1
        while True:
            payload = fetch_links(api_key, domain_id, page=page, limit=args.limit)
            links = payload.get("links") or []
            if not links:
                logger.info("No more links to backfill (page %s empty).", page)
                break

            for entry in links:
                persist_link_record(entry)
                total += 1

            logger.info("Processed page %s (%s links)", page, len(links))
            if len(links) < args.limit:
                logger.info("Last page reached.")
                break
            page += 1

        logger.info("Backfilled %s links", total)
        return 0

    except requests.RequestException as exc:
        logger.error("HTTP error during backfill: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


