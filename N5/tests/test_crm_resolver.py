#!/usr/bin/env python3

import sqlite3
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, "/home/workspace/N5/scripts")

from crm_identity_resolver import CRMIdentityResolver
from crm_resolver import IdentityResolver


class CRMResolverTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "resolver_test.db"
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT,
                linkedin_url TEXT,
                company TEXT,
                markdown_path TEXT
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO people (full_name, email, linkedin_url, company, markdown_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("Alice Example", "alice@example.com", "https://linkedin.com/in/alice", "Acme", "Personal/Knowledge/CRM/individuals/alice-example.md"),
                ("Bob Smith", "bob1@example.com", "https://linkedin.com/in/bob-smith", "Acme", "Personal/Knowledge/CRM/individuals/bob-smith.md"),
                ("Bob Smith", "bob2@example.com", "https://linkedin.com/in/bob-smith-2", "Beta", "Personal/Knowledge/CRM/individuals/bob-smith-2.md"),
            ],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_email_exact_autolinks(self):
        resolver = CRMIdentityResolver(db_path=str(self.db_path), auto_link_threshold=0.99)
        result = resolver.auto_link(email="ALICE@EXAMPLE.COM")
        self.assertEqual(result.person_id, 1)
        self.assertEqual(result.method, "email_exact")
        self.assertEqual(result.confidence, 1.0)

    def test_linkedin_is_normalized(self):
        resolver = CRMIdentityResolver(db_path=str(self.db_path), auto_link_threshold=0.99)
        result = resolver.auto_link(linkedin_url="https://linkedin.com/in/alice/")
        self.assertEqual(result.person_id, 1)
        self.assertEqual(result.method, "linkedin_exact")

    def test_name_ambiguous_without_company(self):
        resolver = CRMIdentityResolver(db_path=str(self.db_path), auto_link_threshold=0.99)
        result = resolver.resolve(name="Bob Smith")
        self.assertIsNone(result.person_id)
        self.assertEqual(result.method, "name_ambiguous")

    def test_name_company_disambiguates(self):
        resolver = CRMIdentityResolver(db_path=str(self.db_path), auto_link_threshold=0.99)
        resolved = resolver.resolve(name="Bob Smith", company="Acme")
        self.assertEqual(resolved.person_id, 2)
        self.assertEqual(resolved.method, "name_company_exact")
        auto = resolver.auto_link(name="Bob Smith", company="Acme")
        self.assertIsNone(auto.person_id)
        self.assertTrue(auto.method.startswith("below_threshold:"))

    def test_compat_wrapper_uses_same_resolution(self):
        resolver = IdentityResolver(db_path=str(self.db_path), auto_link_threshold=0.99)
        result = resolver.resolve_person(email="alice@example.com")
        self.assertIsNotNone(result)
        self.assertEqual(result.person_id, 1)
        self.assertEqual(result.match_type, "EMAIL_EXACT")


if __name__ == "__main__":
    unittest.main()
