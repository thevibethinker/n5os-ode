import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from identity_resolver import EXACT, STRONG, UNCERTAIN, UNMATCHED, IdentityResolver


def _write_index(tmp_path: Path, *, synced_at: str) -> Path:
    payload = {
        "synced_at": synced_at,
        "people": [
            {
                "id": "person-ahmed",
                "first_name": "Ahmed",
                "last_name": "Rashad",
                "email": "ahmed@perle.ai",
                "job_title": "Founder",
                "company": "company-perle",
                "linkedin": "",
            },
            {
                "id": "person-teddy",
                "first_name": "Teddy",
                "last_name": "Schoenfeld",
                "email": "teddy@sentience.ai",
                "job_title": "Founder",
                "company": "company-sentience",
                "linkedin": "",
            },
            {
                "id": "person-sam-alpha",
                "first_name": "Sam",
                "last_name": "Alpha",
                "email": "sam.alpha@alpha.io",
                "job_title": "",
                "company": "company-alpha",
                "linkedin": "",
            },
            {
                "id": "person-sam-beta",
                "first_name": "Sam",
                "last_name": "Beta",
                "email": "sam.beta@beta.io",
                "job_title": "",
                "company": "company-beta",
                "linkedin": "",
            },
            {
                "id": "person-sam-gamma",
                "first_name": "Sam",
                "last_name": "Gamma",
                "email": "sam.gamma@beta.io",
                "job_title": "",
                "company": "company-beta",
                "linkedin": "",
            },
            {
                "id": "person-v",
                "first_name": "Primary",
                "last_name": "User",
                "email": "primary@example.com",
                "job_title": "",
                "company": None,
                "linkedin": "",
            },
        ],
        "companies": [
            {
                "id": "company-perle",
                "name": "Perle.ai",
                "domain": "perle.ai",
                "description": "",
            },
            {
                "id": "company-sentience",
                "name": "Sentience",
                "domain": "sentience.ai",
                "description": "",
            },
            {
                "id": "company-alpha",
                "name": "Alpha Ventures",
                "domain": "alpha.io",
                "description": "",
            },
            {
                "id": "company-beta",
                "name": "Beta Works",
                "domain": "beta.io",
                "description": "",
            },
        ],
        "deals": [],
    }
    path = tmp_path / "local_contact_index.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_email_based_exact_match(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolution = resolver.resolve_person(name="Ahmed", email="ahmed@perle.ai")

    assert resolution.tier == EXACT
    assert resolution.local_record_id == "person-ahmed"
    assert resolution.confidence_score == 1.0
    assert resolution.reason == "email match"


def test_full_name_and_company_is_strong(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolution = resolver.resolve_person(name="Teddy Schoenfeld", company="Sentience")

    assert resolution.tier == STRONG
    assert resolution.local_record_id == "person-teddy"
    assert resolution.reason == "full name and company match"


def test_first_name_only_without_company_stays_uncertain(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolution = resolver.resolve_person(name="Sam")

    assert resolution.tier == UNCERTAIN
    assert resolution.reason == "partial name match"
    assert [candidate["id"] for candidate in resolution.candidates] == [
        "person-sam-alpha",
        "person-sam-beta",
        "person-sam-gamma",
    ]


def test_first_name_plus_company_can_be_strong(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolution = resolver.resolve_person(name="Ahmed", company="Perle")

    assert resolution.tier == STRONG
    assert resolution.local_record_id == "person-ahmed"
    assert resolution.reason == "first name and company match"


def test_first_name_with_conflicting_company_remains_uncertain(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolution = resolver.resolve_person(name="Ahmed", company="Sentience")

    assert resolution.tier == UNCERTAIN
    assert resolution.local_record_id is None
    assert resolution.reason == "company context did not disambiguate"


def test_no_match_is_unmatched(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolution = resolver.resolve_person(name="Yakaira Núñez")

    assert resolution.tier == UNMATCHED
    assert resolution.candidates == []
    assert resolution.reason == "no index match"


def test_company_alias_normalization(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolution = resolver.resolve_company(name="Perle")

    assert resolution.tier == STRONG
    assert resolution.local_record_id == "company-perle"
    assert resolution.reason == "company alias match"


def test_self_reference_is_filtered(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolution = resolver.resolve_person(name="Primary User")

    assert resolution.tier == UNMATCHED
    assert resolution.reason == "self reference filtered"
    assert resolution.candidates == []


def test_stale_index_logs_warning_and_reports_age(tmp_path, caplog):
    with caplog.at_level("WARNING"):
        resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-01T00:00:00+00:00")))

    status = resolver.index_status()

    assert resolver.index_is_stale is True
    assert status["stale"] is True
    assert status["index_age_hours"] > 48
    assert "stale" in caplog.text.lower()


def test_resolve_entities_handles_normalized_payload_shape(tmp_path):
    resolver = IdentityResolver(str(_write_index(tmp_path, synced_at="2026-04-09T14:00:00+00:00")))

    resolutions = resolver.resolve_entities(
        {
            "people": [
                {"name": "Teddy Schoenfeld", "company_hint": "Sentience"},
                {"name": "Primary User"},
            ],
            "companies": [{"name": "Perle", "domain_hint": None}],
        }
    )

    assert [resolution.tier for resolution in resolutions] == [STRONG, UNMATCHED, STRONG]
    assert [resolution.entity_type for resolution in resolutions] == ["person", "person", "company"]
