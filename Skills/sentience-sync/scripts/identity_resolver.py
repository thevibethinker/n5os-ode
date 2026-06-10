#!/usr/bin/env python3
"""
Confidence-tiered identity resolution against a local local contact index.
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

LOGGER = logging.getLogger(__name__)

EXACT = "exact"
STRONG = "strong"
UNCERTAIN = "uncertain"
UNMATCHED = "unmatched"

HONORIFIC_TOKENS = {
    "mr",
    "mrs",
    "ms",
    "miss",
    "dr",
    "prof",
    "professor",
    "sir",
    "jr",
    "sr",
    "ii",
    "iii",
    "iv",
    "phd",
    "md",
    "jd",
    "mba",
    "esq",
}

COMPANY_STOPWORDS = {
    "inc",
    "incorporated",
    "llc",
    "ltd",
    "limited",
    "corp",
    "corporation",
    "company",
    "co",
    "group",
    "holdings",
}

SELF_NAME_ALIASES = {"primary user", "primary", "primary user"}
SELF_SINGLE_TOKEN_ALIASES = {"v"}


@dataclass(slots=True)
class Resolution:
    entity_type: str
    query: str
    tier: str
    local_record_id: str | None
    confidence_score: float
    candidates: list[dict[str, Any]]
    reason: str
    index_age_hours: float | None = None
    index_stale: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CompanyRecord:
    id: str
    name: str
    domain: str | None
    description: str | None
    alias_keys: frozenset[str]


@dataclass(frozen=True, slots=True)
class PersonRecord:
    id: str
    name: str
    first_name_norm: str
    full_name_norm: str
    email: str | None
    company_id: str | None
    company_name: str | None
    company_domain: str | None
    company_alias_keys: frozenset[str]


class IdentityResolver:
    def __init__(self, index_path: str = "Skills/sentience-sync/data/local_contact_index.json") -> None:
        self.index_path = Path(index_path)
        self.raw_index = json.loads(self.index_path.read_text(encoding="utf-8"))
        self.synced_at = _parse_timestamp(self.raw_index.get("synced_at"))
        self.index_age_hours = _hours_since(self.synced_at)
        self.index_is_stale = self.index_age_hours is None or self.index_age_hours > 48
        if self.index_is_stale:
            LOGGER.warning(
                "local contact index is stale: path=%s synced_at=%s age_hours=%s",
                self.index_path,
                self.raw_index.get("synced_at"),
                None if self.index_age_hours is None else round(self.index_age_hours, 2),
            )

        self.companies = self._build_company_records(self.raw_index.get("companies", []))
        self._company_by_domain: dict[str, list[CompanyRecord]] = {}
        self._company_by_alias: dict[str, list[CompanyRecord]] = {}
        for company in self.companies:
            if company.domain:
                self._company_by_domain.setdefault(company.domain, []).append(company)
            for alias in company.alias_keys:
                self._company_by_alias.setdefault(alias, []).append(company)

        self.people = self._build_person_records(self.raw_index.get("people", []))
        self._people_by_email: dict[str, list[PersonRecord]] = {}
        self._people_by_full_name: dict[str, list[PersonRecord]] = {}
        self._people_by_first_name: dict[str, list[PersonRecord]] = {}
        for person in self.people:
            if person.email:
                self._people_by_email.setdefault(person.email, []).append(person)
            if person.full_name_norm:
                self._people_by_full_name.setdefault(person.full_name_norm, []).append(person)
            if person.first_name_norm:
                self._people_by_first_name.setdefault(person.first_name_norm, []).append(person)

        self._self_records = [
            person
            for person in self.people
            if person.full_name_norm in SELF_NAME_ALIASES
            or (
                person.first_name_norm == "primary"
                and _normalize_text(person.name).endswith("user")
            )
        ]
        self._self_record_ids = {person.id for person in self._self_records}
        self._self_emails = {person.email for person in self._self_records if person.email}
        self._self_name_aliases = set(SELF_NAME_ALIASES)
        for person in self._self_records:
            if person.full_name_norm:
                self._self_name_aliases.add(person.full_name_norm)
            if person.first_name_norm:
                self._self_name_aliases.add(person.first_name_norm)

    def index_status(self) -> dict[str, Any]:
        return {
            "index_path": str(self.index_path),
            "synced_at": self.raw_index.get("synced_at"),
            "index_age_hours": self.index_age_hours,
            "stale": self.index_is_stale,
        }

    def resolve_person(
        self,
        name: str,
        company: str | None = None,
        email: str | None = None,
    ) -> Resolution:
        query_name = str(name or "").strip()
        query_email = _normalize_email(email)
        query = query_email or query_name

        if self._is_self_reference(query_name, query_email):
            return self._build_resolution(
                entity_type="person",
                query=query,
                tier=UNMATCHED,
                local_record_id=None,
                confidence_score=0.0,
                candidates=[],
                reason="self reference filtered",
            )

        if query_email:
            matches = self._dedupe_people(self._people_by_email.get(query_email, []))
            if len(matches) == 1:
                return self._build_person_match(
                    query=query,
                    tier=EXACT,
                    reason="email match",
                    confidence_score=1.0,
                    matches=matches,
                )
            if len(matches) > 1:
                return self._build_person_resolution(
                    query=query,
                    tier=UNCERTAIN,
                    reason="multiple email matches",
                    confidence_score=0.65,
                    candidates=matches,
                )

        name_key = _normalize_name_key(query_name)
        if not name_key:
            return self._build_resolution(
                entity_type="person",
                query=query,
                tier=UNMATCHED,
                local_record_id=None,
                confidence_score=0.0,
                candidates=[],
                reason="missing person identity",
            )

        company_aliases = _company_alias_keys(company)
        name_tokens = name_key.split()
        full_name_matches = self._dedupe_people(self._people_by_full_name.get(name_key, []))

        if len(name_tokens) >= 2:
            if not full_name_matches:
                return self._build_resolution(
                    entity_type="person",
                    query=query,
                    tier=UNMATCHED,
                    local_record_id=None,
                    confidence_score=0.0,
                    candidates=[],
                    reason="no index match",
                )
            if company_aliases:
                company_matches = self._filter_people_by_company(full_name_matches, company_aliases)
                if len(company_matches) == 1:
                    return self._build_person_match(
                        query=query,
                        tier=STRONG,
                        reason="full name and company match",
                        confidence_score=0.95,
                        matches=company_matches,
                    )
                if len(company_matches) > 1:
                    return self._build_person_resolution(
                        query=query,
                        tier=UNCERTAIN,
                        reason="multiple matches",
                        confidence_score=0.62,
                        candidates=company_matches,
                    )
                if len(full_name_matches) == 1:
                    only_match = full_name_matches[0]
                    if not only_match.company_alias_keys:
                        return self._build_person_match(
                            query=query,
                            tier=STRONG,
                            reason="full name match",
                            confidence_score=0.91,
                            matches=full_name_matches,
                        )
                    return self._build_person_resolution(
                        query=query,
                        tier=UNCERTAIN,
                        reason="company context mismatch",
                        confidence_score=0.58,
                        candidates=full_name_matches,
                    )
                return self._build_person_resolution(
                    query=query,
                    tier=UNCERTAIN,
                    reason="multiple matches",
                    confidence_score=0.6,
                    candidates=full_name_matches,
                )

            if len(full_name_matches) == 1:
                return self._build_person_match(
                    query=query,
                    tier=STRONG,
                    reason="full name match",
                    confidence_score=0.93,
                    matches=full_name_matches,
                )
            return self._build_person_resolution(
                query=query,
                tier=UNCERTAIN,
                reason="multiple matches",
                confidence_score=0.61,
                candidates=full_name_matches,
            )

        first_name_matches = self._dedupe_people(self._people_by_first_name.get(name_key, []))
        if not first_name_matches:
            return self._build_resolution(
                entity_type="person",
                query=query,
                tier=UNMATCHED,
                local_record_id=None,
                confidence_score=0.0,
                candidates=[],
                reason="no index match",
            )

        if company_aliases:
            company_matches = self._filter_people_by_company(first_name_matches, company_aliases)
            if len(company_matches) == 1:
                return self._build_person_match(
                    query=query,
                    tier=STRONG,
                    reason="first name and company match",
                    confidence_score=0.9,
                    matches=company_matches,
                )
            if len(company_matches) > 1:
                return self._build_person_resolution(
                    query=query,
                    tier=UNCERTAIN,
                    reason="multiple matches",
                    confidence_score=0.56,
                    candidates=company_matches,
                )
            return self._build_person_resolution(
                query=query,
                tier=UNCERTAIN,
                reason="company context did not disambiguate",
                confidence_score=0.5,
                candidates=first_name_matches,
            )

        return self._build_person_resolution(
            query=query,
            tier=UNCERTAIN,
            reason="partial name match",
            confidence_score=0.45 if len(first_name_matches) == 1 else 0.4,
            candidates=first_name_matches,
        )

    def resolve_company(self, name: str, domain: str | None = None) -> Resolution:
        query_name = str(name or "").strip()
        query_domain = _normalize_domain(domain)
        query = query_domain or query_name

        if query_domain:
            domain_matches = self._dedupe_companies(self._company_by_domain.get(query_domain, []))
            if len(domain_matches) == 1:
                return self._build_company_match(
                    query=query,
                    tier=EXACT,
                    reason="domain match",
                    confidence_score=1.0,
                    matches=domain_matches,
                )
            if len(domain_matches) > 1:
                return self._build_company_resolution(
                    query=query,
                    tier=UNCERTAIN,
                    reason="multiple domain matches",
                    confidence_score=0.66,
                    candidates=domain_matches,
                )

        company_aliases = _company_alias_keys(query_name)
        if not company_aliases:
            return self._build_resolution(
                entity_type="company",
                query=query,
                tier=UNMATCHED,
                local_record_id=None,
                confidence_score=0.0,
                candidates=[],
                reason="missing company identity",
            )

        matches = self._match_companies_by_aliases(company_aliases)
        if len(matches) == 1:
            return self._build_company_match(
                query=query,
                tier=STRONG,
                reason="company alias match",
                confidence_score=0.92,
                matches=matches,
            )
        if len(matches) > 1:
            return self._build_company_resolution(
                query=query,
                tier=UNCERTAIN,
                reason="multiple matches",
                confidence_score=0.55,
                candidates=matches,
            )
        return self._build_resolution(
            entity_type="company",
            query=query,
            tier=UNMATCHED,
            local_record_id=None,
            confidence_score=0.0,
            candidates=[],
            reason="no index match",
        )

    def resolve_entities(self, entities: dict[str, Any]) -> list[Resolution]:
        results: list[Resolution] = []

        for person in entities.get("people", []):
            if isinstance(person, dict):
                name = str(person.get("name") or person.get("full_name") or "").strip()
                company = person.get("company_hint") or person.get("company")
                email = person.get("email")
            else:
                name = str(person or "").strip()
                company = None
                email = None
            if name or email:
                results.append(self.resolve_person(name=name, company=company, email=email))

        for company in entities.get("companies", []):
            if isinstance(company, dict):
                name = str(company.get("name") or "").strip()
                domain = company.get("domain_hint") or company.get("domain")
            else:
                name = str(company or "").strip()
                domain = None
            if name or domain:
                results.append(self.resolve_company(name=name, domain=domain))

        return results

    def _build_company_records(self, items: Iterable[dict[str, Any]]) -> list[CompanyRecord]:
        records: list[CompanyRecord] = []
        for item in items:
            name = str(item.get("name") or "").strip()
            domain = _normalize_domain(item.get("domain"))
            records.append(
                CompanyRecord(
                    id=str(item.get("id") or ""),
                    name=name,
                    domain=domain,
                    description=str(item.get("description") or "").strip() or None,
                    alias_keys=frozenset(_company_alias_keys(name, domain)),
                )
            )
        return records

    def _build_person_records(self, items: Iterable[dict[str, Any]]) -> list[PersonRecord]:
        companies_by_id = {company.id: company for company in self.companies}
        records: list[PersonRecord] = []
        for item in items:
            first_name = str(item.get("first_name") or "").strip()
            last_name = str(item.get("last_name") or "").strip()
            name = " ".join(part for part in [first_name, last_name] if part).strip()
            email = _normalize_email(item.get("email"))
            company_id = str(item.get("company") or "").strip() or None
            company_record = companies_by_id.get(company_id or "")
            first_name_norm = _normalize_name_key(first_name)
            full_name_norm = _normalize_name_key(name)
            records.append(
                PersonRecord(
                    id=str(item.get("id") or ""),
                    name=name or (email or ""),
                    first_name_norm=first_name_norm,
                    full_name_norm=full_name_norm,
                    email=email,
                    company_id=company_id,
                    company_name=company_record.name if company_record else None,
                    company_domain=company_record.domain if company_record else None,
                    company_alias_keys=frozenset(
                        _company_alias_keys(
                            company_record.name if company_record else None,
                            company_record.domain if company_record else None,
                        )
                    ),
                )
            )
        return records

    def _build_resolution(
        self,
        *,
        entity_type: str,
        query: str,
        tier: str,
        local_record_id: str | None,
        confidence_score: float,
        candidates: list[dict[str, Any]],
        reason: str,
    ) -> Resolution:
        return Resolution(
            entity_type=entity_type,
            query=query,
            tier=tier,
            local_record_id=local_record_id,
            confidence_score=confidence_score,
            candidates=candidates,
            reason=reason,
            index_age_hours=self.index_age_hours,
            index_stale=self.index_is_stale,
        )

    def _build_person_match(
        self,
        *,
        query: str,
        tier: str,
        reason: str,
        confidence_score: float,
        matches: list[PersonRecord],
    ) -> Resolution:
        return self._build_person_resolution(
            query=query,
            tier=tier,
            reason=reason,
            confidence_score=confidence_score,
            candidates=matches,
            local_record_id=matches[0].id if matches else None,
        )

    def _build_person_resolution(
        self,
        *,
        query: str,
        tier: str,
        reason: str,
        confidence_score: float,
        candidates: list[PersonRecord],
        local_record_id: str | None = None,
    ) -> Resolution:
        materialized = [self._person_candidate(person) for person in candidates]
        return self._build_resolution(
            entity_type="person",
            query=query,
            tier=tier,
            local_record_id=local_record_id,
            confidence_score=confidence_score,
            candidates=materialized,
            reason=reason,
        )

    def _build_company_match(
        self,
        *,
        query: str,
        tier: str,
        reason: str,
        confidence_score: float,
        matches: list[CompanyRecord],
    ) -> Resolution:
        return self._build_company_resolution(
            query=query,
            tier=tier,
            reason=reason,
            confidence_score=confidence_score,
            candidates=matches,
            local_record_id=matches[0].id if matches else None,
        )

    def _build_company_resolution(
        self,
        *,
        query: str,
        tier: str,
        reason: str,
        confidence_score: float,
        candidates: list[CompanyRecord],
        local_record_id: str | None = None,
    ) -> Resolution:
        materialized = [self._company_candidate(company) for company in candidates]
        return self._build_resolution(
            entity_type="company",
            query=query,
            tier=tier,
            local_record_id=local_record_id,
            confidence_score=confidence_score,
            candidates=materialized,
            reason=reason,
        )

    def _filter_people_by_company(
        self,
        people: Iterable[PersonRecord],
        company_aliases: set[str],
    ) -> list[PersonRecord]:
        matches = []
        for person in people:
            if person.company_alias_keys.intersection(company_aliases):
                matches.append(person)
        return self._dedupe_people(matches)

    def _match_companies_by_aliases(self, aliases: set[str]) -> list[CompanyRecord]:
        matches: list[CompanyRecord] = []
        for alias in aliases:
            matches.extend(self._company_by_alias.get(alias, []))
        return self._dedupe_companies(matches)

    def _dedupe_people(self, people: Iterable[PersonRecord]) -> list[PersonRecord]:
        unique = {person.id: person for person in people if person.id and person.id not in self._self_record_ids}
        return sorted(unique.values(), key=lambda person: (person.name.lower(), person.email or "", person.id))

    def _dedupe_companies(self, companies: Iterable[CompanyRecord]) -> list[CompanyRecord]:
        unique = {company.id: company for company in companies if company.id}
        return sorted(unique.values(), key=lambda company: (company.name.lower(), company.domain or "", company.id))

    def _person_candidate(self, person: PersonRecord) -> dict[str, Any]:
        return {
            "id": person.id,
            "name": person.name,
            "email": person.email,
            "company_id": person.company_id,
            "company_name": person.company_name,
            "company_domain": person.company_domain,
        }

    def _company_candidate(self, company: CompanyRecord) -> dict[str, Any]:
        return {
            "id": company.id,
            "name": company.name,
            "domain": company.domain,
            "description": company.description,
        }

    def _is_self_reference(self, name: str | None, email: str | None) -> bool:
        if email and email in self._self_emails:
            return True
        name_key = _normalize_name_key(name)
        if not name_key:
            return False
        if name_key in self._self_name_aliases:
            return True
        return len(name_key.split()) == 1 and name_key in SELF_SINGLE_TOKEN_ALIASES


def _normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"www\.", "", text)
    text = re.sub(r"[^a-z0-9@.\- ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_email(value: Any) -> str | None:
    email = _normalize_text(value)
    return email or None


def _normalize_domain(value: Any) -> str | None:
    text = _normalize_text(value)
    if not text:
        return None
    if "@" in text and " " not in text:
        text = text.rsplit("@", 1)[1]
    text = text.strip("/")
    if "/" in text:
        text = text.split("/", 1)[0]
    if not text:
        return None
    return text


def _normalize_name_key(value: Any) -> str:
    tokens = _normalize_text(value).split()
    filtered: list[str] = []
    for token in tokens:
        if token in HONORIFIC_TOKENS:
            continue
        if len(token) == 1 and len(tokens) > 1:
            continue
        filtered.append(token)
    if not filtered:
        filtered = tokens
    return " ".join(filtered)


def _company_alias_keys(*values: Any) -> set[str]:
    aliases: set[str] = set()
    for value in values:
        if not value:
            continue
        text = _normalize_text(value)
        if not text:
            continue
        domain = _normalize_domain(value)
        if domain:
            labels = [label for label in domain.split(".") if label and label != "www"]
            if labels:
                aliases.add(labels[0])
                aliases.add(" ".join(labels))
                aliases.add("".join(labels))
            if len(labels) >= 2:
                if labels[-2] in {"co", "com", "org", "net"} and len(labels) >= 3:
                    aliases.add(labels[-3])
                else:
                    aliases.add(labels[-2])

        text = re.sub(r"\b(?:ai|io|com|co|org|net)\b", " ", text)
        tokens = [token for token in text.split() if token not in COMPANY_STOPWORDS]
        if not tokens:
            continue
        aliases.add(" ".join(tokens))
        aliases.add("".join(tokens))
    return {alias for alias in aliases if alias}


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _hours_since(timestamp: datetime | None) -> float | None:
    if timestamp is None:
        return None
    return (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600.0


__all__ = ["EXACT", "STRONG", "UNCERTAIN", "UNMATCHED", "IdentityResolver", "Resolution"]
