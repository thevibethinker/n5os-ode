#!/usr/bin/env python3
"""
CRM V3 Entity Deduplicator
Deduplicates entities across multiple CRM sources using email as primary key.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class ProfileEntity:
    """Represents a deduplicated profile entity."""
    
    CATEGORY_PRIORITY = {
        "ADVISOR": 5,
        "INVESTOR": 4,
        "COMMUNITY": 3,
        "NETWORKING": 2,
        "OTHER": 1,
    }
    
    def __init__(self, email: str):
        self.email = email.lower().strip() if email else None
        self.names = []
        self.categories = []
        self.organizations = []
        self.linkedin_urls = []
        self.notes = []
        self.meeting_counts = []
        self.contact_dates = []
        self.sources = []
        self.raw_records = []
    
    def add_source(self, source: str, record: Dict):
        """Add a source record to this entity."""
        self.sources.append(source)
        self.raw_records.append(record)
        
        if record.get("name"):
            self.names.append(record["name"])
        if record.get("category"):
            self.categories.append(record["category"])
        if record.get("organization"):
            self.organizations.append(record["organization"])
        if record.get("linkedin_url"):
            self.linkedin_urls.append(record["linkedin_url"])
        if record.get("notes"):
            self.notes.append(f"[{source}] {record['notes']}")
        if record.get("meeting_count"):
            self.meeting_counts.append(int(record["meeting_count"]))
        if record.get("last_contact_date"):
            self.contact_dates.append(record["last_contact_date"])
    
    def get_canonical_name(self) -> str:
        """Return the most complete name (longest)."""
        if not self.names:
            return "Unknown"
        return max(self.names, key=len)
    
    def get_canonical_category(self) -> str:
        """Return highest priority category."""
        if not self.categories:
            return "OTHER"
        
        return max(
            self.categories,
            key=lambda c: self.CATEGORY_PRIORITY.get(c.upper(), 0)
        )
    
    def get_canonical_organization(self) -> Optional[str]:
        """Return first non-null organization."""
        return next((org for org in self.organizations if org), None)
    
    def get_canonical_linkedin(self) -> Optional[str]:
        """Return first non-null LinkedIn URL."""
        return next((url for url in self.linkedin_urls if url), None)
    
    def get_total_meetings(self) -> int:
        """Sum meeting counts from all sources."""
        return sum(self.meeting_counts) if self.meeting_counts else 0
    
    def get_latest_contact_date(self) -> Optional[str]:
        """Return most recent contact date."""
        if not self.contact_dates:
            return None
        
        valid_dates = [str(d) for d in self.contact_dates if d]
        if not valid_dates:
            return None
        
        return max(valid_dates)
    
    def get_merged_notes(self) -> str:
        """Merge all notes chronologically."""
        return "\n\n".join(self.notes) if self.notes else ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for migration."""
        return {
            "email": self.email,
            "name": self.get_canonical_name(),
            "category": self.get_canonical_category(),
            "organization": self.get_canonical_organization(),
            "linkedin_url": self.get_canonical_linkedin(),
            "total_meetings": self.get_total_meetings(),
            "last_contact_date": self.get_latest_contact_date(),
            "merged_notes": self.get_merged_notes(),
            "sources": ", ".join(set(self.sources)),
            "source_count": len(self.sources),
        }


class CRMDeduplicator:
    """Deduplicates CRM entities across multiple sources."""
    
    def __init__(self):
        self.entities: Dict[str, ProfileEntity] = {}
        self.fuzzy_threshold = 0.80
    
    def normalize_email(self, email: Optional[str]) -> Optional[str]:
        """Normalize email to lowercase and trim."""
        if not email:
            return None
        return email.lower().strip()
    
    def name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names (0-1)."""
        if not name1 or not name2:
            return 0.0
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
    
    def find_entity_by_email(self, email: str) -> Optional[ProfileEntity]:
        """Find entity by exact email match."""
        normalized = self.normalize_email(email)
        return self.entities.get(normalized)
    
    def find_entity_by_name(self, name: str, threshold: float = None) -> Optional[ProfileEntity]:
        """Find entity by fuzzy name match (>80% similarity)."""
        if not name:
            return None
        
        threshold = threshold or self.fuzzy_threshold
        best_match = None
        best_score = 0.0
        
        for entity in self.entities.values():
            for existing_name in entity.names:
                score = self.name_similarity(name, existing_name)
                if score > best_score:
                    best_score = score
                    best_match = entity
        
        if best_score >= threshold:
            logger.info(f"Fuzzy name match: '{name}' ~= '{best_match.get_canonical_name()}' ({best_score:.2f})")
            return best_match
        
        return None
    
    def add_record(self, source: str, record: Dict):
        """Add a record from a source system."""
        email = self.normalize_email(record.get("email"))
        name = record.get("name")
        
        entity = None
        
        if email:
            entity = self.find_entity_by_email(email)
        
        if not entity and name:
            entity = self.find_entity_by_name(name)
        
        if entity:
            logger.debug(f"Merging into existing entity: {entity.email or entity.get_canonical_name()}")
            entity.add_source(source, record)
        else:
            if email:
                logger.debug(f"Creating new entity: {email}")
                entity = ProfileEntity(email)
                entity.add_source(source, record)
                self.entities[email] = entity
            else:
                logger.warning(f"Skipping record without email: {name}")
    
    def get_unique_profiles(self) -> List[ProfileEntity]:
        """Return all unique deduplicated profiles."""
        return list(self.entities.values())
    
    def get_statistics(self) -> Dict:
        """Return deduplication statistics."""
        total_sources = sum(len(e.sources) for e in self.entities.values())
        duplicates_found = total_sources - len(self.entities)
        
        return {
            "total_records": total_sources,
            "unique_profiles": len(self.entities),
            "duplicates_found": duplicates_found,
            "deduplication_rate": f"{(duplicates_found / total_sources * 100):.1f}%" if total_sources > 0 else "0%",
        }


def test_deduplicator():
    """Test deduplication logic."""
    logger.info("Testing CRMDeduplicator...")
    
    dedup = CRMDeduplicator()
    
    dedup.add_record("source1", {
        "email": "Alex.Caveny@Gmail.com",
        "name": "Alex",
        "category": "COMMUNITY",
        "organization": "Wisdom Partners",
        "meeting_count": 3,
    })
    
    dedup.add_record("source2", {
        "email": "alex.caveny@gmail.com",
        "name": "Alex Caveny",
        "category": "ADVISOR",
        "linkedin_url": "https://linkedin.com/in/alexcaveny",
        "meeting_count": 2,
    })
    
    dedup.add_record("source3", {
        "email": "john.doe@example.com",
        "name": "John Doe",
        "category": "INVESTOR",
    })
    
    profiles = dedup.get_unique_profiles()
    stats = dedup.get_statistics()
    
    logger.info(f"Test Results: {stats}")
    assert len(profiles) == 2, f"Expected 2 unique profiles, got {len(profiles)}"
    assert stats["duplicates_found"] == 1, f"Expected 1 duplicate, got {stats['duplicates_found']}"
    
    alex = dedup.find_entity_by_email("alex.caveny@gmail.com")
    assert alex is not None
    assert alex.get_canonical_name() == "Alex Caveny", f"Expected 'Alex Caveny', got '{alex.get_canonical_name()}'"
    assert alex.get_canonical_category() == "ADVISOR", f"Expected 'ADVISOR', got '{alex.get_canonical_category()}'"
    assert alex.get_total_meetings() == 5, f"Expected 5 meetings, got {alex.get_total_meetings()}"
    
    logger.info("✓ All tests passed")


if __name__ == "__main__":
    test_deduplicator()



