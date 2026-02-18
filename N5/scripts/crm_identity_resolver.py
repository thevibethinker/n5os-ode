#!/usr/bin/env python3
"""High-precision CRM identity resolver for n5_core people records."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Optional

try:
    from db_paths import PEOPLE_TABLE, get_db_connection
except ModuleNotFoundError:
    from N5.scripts.db_paths import PEOPLE_TABLE, get_db_connection


@dataclass
class ResolveResult:
    person_id: Optional[int]
    confidence: float
    method: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    markdown_path: Optional[str] = None


class CRMIdentityResolver:
    def __init__(self, auto_link_threshold: float = 0.99, db_path: Optional[str] = None):
        self.auto_link_threshold = auto_link_threshold
        self.db_path = db_path

    @staticmethod
    def _norm(text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip().lower())

    @staticmethod
    def _norm_linkedin(url: Optional[str]) -> str:
        if not url:
            return ""
        normalized = url.strip().lower()
        normalized = re.sub(r"^https?://", "", normalized)
        normalized = normalized.rstrip("/")
        return normalized

    def _get_connection(self) -> sqlite3.Connection:
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        return get_db_connection(readonly=True)

    @staticmethod
    def _row_to_result(row: sqlite3.Row, confidence: float, method: str) -> ResolveResult:
        return ResolveResult(
            person_id=int(row["id"]),
            confidence=confidence,
            method=method,
            full_name=row["full_name"],
            email=row["email"],
            markdown_path=row["markdown_path"],
        )

    def resolve(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        company: Optional[str] = None,
        linkedin_url: Optional[str] = None,
    ) -> ResolveResult:
        norm_name = self._norm(name)
        norm_email = self._norm(email)
        norm_company = self._norm(company)
        norm_linkedin = self._norm_linkedin(linkedin_url)

        if not (norm_email or norm_name or norm_linkedin):
            return ResolveResult(person_id=None, confidence=0.0, method="no_signal")

        conn = self._get_connection()
        try:
            if norm_email:
                rows = conn.execute(
                    f"SELECT id, full_name, email, markdown_path FROM {PEOPLE_TABLE} WHERE lower(email)=?",
                    (norm_email,),
                ).fetchall()
                if len(rows) == 1:
                    return self._row_to_result(rows[0], 1.0, "email_exact")
                if len(rows) > 1:
                    return ResolveResult(person_id=None, confidence=0.0, method="email_ambiguous")

            if norm_linkedin:
                rows = conn.execute(
                    f"""
                    SELECT id, full_name, email, markdown_path, linkedin_url
                    FROM {PEOPLE_TABLE}
                    WHERE linkedin_url IS NOT NULL
                    """
                ).fetchall()
                matches = [
                    row for row in rows
                    if self._norm_linkedin(row["linkedin_url"]) == norm_linkedin
                ]
                if len(matches) == 1:
                    return self._row_to_result(matches[0], 0.995, "linkedin_exact")
                if len(matches) > 1:
                    return ResolveResult(person_id=None, confidence=0.0, method="linkedin_ambiguous")

            if not norm_name:
                return ResolveResult(person_id=None, confidence=0.0, method="name_missing")

            name_rows = conn.execute(
                f"""
                SELECT id, full_name, email, company, markdown_path
                FROM {PEOPLE_TABLE}
                WHERE lower(full_name)=?
                """,
                (norm_name,),
            ).fetchall()

            if len(name_rows) == 1:
                confidence = 0.97
                if norm_company and self._norm(name_rows[0]["company"]) == norm_company:
                    confidence = 0.985
                return self._row_to_result(name_rows[0], confidence, "name_exact_unique")

            if len(name_rows) > 1:
                if norm_company:
                    company_rows = [
                        row for row in name_rows
                        if self._norm(row["company"]) == norm_company
                    ]
                    if len(company_rows) == 1:
                        return self._row_to_result(company_rows[0], 0.975, "name_company_exact")
                    if len(company_rows) > 1:
                        return ResolveResult(person_id=None, confidence=0.0, method="name_company_ambiguous")
                return ResolveResult(person_id=None, confidence=0.0, method="name_ambiguous")

            return ResolveResult(person_id=None, confidence=0.0, method="no_candidate")
        finally:
            conn.close()

    def auto_link(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        company: Optional[str] = None,
        linkedin_url: Optional[str] = None,
    ) -> ResolveResult:
        result = self.resolve(name=name, email=email, company=company, linkedin_url=linkedin_url)
        if result.person_id is None:
            return result
        if result.confidence < self.auto_link_threshold:
            return ResolveResult(
                person_id=None,
                confidence=result.confidence,
                method=f"below_threshold:{result.method}",
                full_name=result.full_name,
                email=result.email,
                markdown_path=result.markdown_path,
            )
        return result
