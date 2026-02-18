#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "/home/workspace/N5/scripts")

from meeting_crm_linker import extract_participants_from_b03, extract_participants_from_folder_name


class MeetingCRMLinkerExtractionTests(unittest.TestCase):
    def test_b03_ignores_section_headers(self):
        with tempfile.TemporaryDirectory() as td:
            meeting_dir = Path(td)
            (meeting_dir / "B08_STAKEHOLDER_INTELLIGENCE.md").write_text(
                """## STAKEHOLDER_INTELLIGENCE

### Foundational Profile
### What Resonated
### Strategic Alignment Assessment
### CRM Integration
""",
                encoding="utf-8",
            )
            participants = extract_participants_from_b03(meeting_dir)
            self.assertEqual(participants, [])

    def test_b03_extracts_name_field(self):
        with tempfile.TemporaryDirectory() as td:
            meeting_dir = Path(td)
            (meeting_dir / "B08_STAKEHOLDER_INTELLIGENCE.md").write_text(
                """### Participant
**Name:** Jacob Bank
""",
                encoding="utf-8",
            )
            participants = extract_participants_from_b03(meeting_dir)
            self.assertEqual(participants, ["Jacob Bank"])

    def test_folder_name_truncates_descriptors(self):
        participants = extract_participants_from_folder_name(
            "2025-09-04_Jacob-bank-relay-Educational"
        )
        self.assertEqual(participants, ["Jacob Bank"])


if __name__ == "__main__":
    unittest.main()
