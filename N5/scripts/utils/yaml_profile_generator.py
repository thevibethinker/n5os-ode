#!/usr/bin/env python3
"""
YAML Profile Generator for CRM V3
Generates hybrid YAML+Markdown profiles from deduplicated entities.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class YAMLProfileGenerator:
    """Generates YAML profile files for CRM V3."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text.strip('_')
    
    def extract_email_prefix(self, email: str) -> str:
        """Extract username from email (before @)."""
        if not email:
            return "unknown"
        return email.split("@")[0].replace(".", "_")
    
    def generate_filename(self, name: str, email: str) -> str:
        """Generate filename: FirstName_LastName_email_prefix.yaml"""
        name_parts = name.split()
        
        if len(name_parts) >= 2:
            first = self.slugify(name_parts[0])
            last = self.slugify(name_parts[-1])
            name_slug = f"{first.capitalize()}_{last.capitalize()}"
        else:
            name_slug = self.slugify(name).capitalize()
        
        email_prefix = self.extract_email_prefix(email)
        
        return f"{name_slug}_{email_prefix}.yaml"
    
    def format_contact_section(self, entity: Dict) -> str:
        """Format contact information section."""
        lines = ["## Contact Information"]
        
        if entity.get("email"):
            lines.append(f"- **Email:** {entity['email']}")
        
        if entity.get("linkedin_url"):
            lines.append(f"- **LinkedIn:** {entity['linkedin_url']}")
        
        if entity.get("organization"):
            lines.append(f"- **Organization:** {entity['organization']}")
        
        return "\n".join(lines)
    
    def format_metadata_section(self, entity: Dict) -> str:
        """Format metadata section."""
        lines = ["## Metadata"]
        lines.append(f"- **Sources:** {entity.get('sources', 'unknown')}")
        lines.append(f"- **Source Count:** {entity.get('source_count', 0)}")
        lines.append(f"- **Total Meetings:** {entity.get('total_meetings', 0)}")
        
        if entity.get("last_contact_date"):
            lines.append(f"- **Last Contact:** {entity['last_contact_date']}")
        
        return "\n".join(lines)
    
    def format_notes_section(self, entity: Dict) -> str:
        """Format notes/intelligence section."""
        notes = entity.get("merged_notes", "")
        
        if not notes:
            return "## Notes\n\n*No notes available from source systems.*"
        
        return f"## Notes\n\n{notes}"
    
    def generate_yaml_content(self, entity: Dict) -> str:
        """Generate complete YAML profile content."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        name = entity.get("name", "Unknown")
        email = entity.get("email", "unknown@example.com")
        category = entity.get("category", "OTHER")
        
        yaml_header = f"""---
created: {today}
last_edited: {today}
version: 1.0
source: migration_v3
email: {email}
category: {category}
relationship_strength: {self._infer_relationship_strength(entity)}
---

# {name}

{self.format_contact_section(entity)}

{self.format_metadata_section(entity)}

{self.format_notes_section(entity)}
"""
        return yaml_header
    
    def _infer_relationship_strength(self, entity: Dict) -> str:
        """Infer relationship strength from metadata."""
        meetings = entity.get("total_meetings", 0)
        category = entity.get("category", "OTHER")
        
        if meetings >= 5 or category == "ADVISOR":
            return "strong"
        elif meetings >= 2 or category in ["INVESTOR", "COMMUNITY"]:
            return "moderate"
        else:
            return "weak"
    
    def generate_profile(self, entity: Dict) -> Path:
        """Generate YAML profile file and return path."""
        name = entity.get("name", "Unknown")
        email = entity.get("email", "unknown@example.com")
        
        filename = self.generate_filename(name, email)
        filepath = self.output_dir / filename
        
        content = self.generate_yaml_content(entity)
        
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Generated profile: {filepath}")
        
        return filepath
    
    def generate_batch(self, entities: list) -> list:
        """Generate profiles for multiple entities."""
        paths = []
        
        for entity in entities:
            try:
                path = self.generate_profile(entity)
                paths.append(path)
            except Exception as e:
                logger.error(f"Failed to generate profile for {entity.get('email')}: {e}")
        
        return paths


def test_generator():
    """Test YAML profile generation."""
    logger.info("Testing YAMLProfileGenerator...")
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = YAMLProfileGenerator(tmpdir)
        
        test_entity = {
            "email": "alex.caveny@gmail.com",
            "name": "Alex Caveny",
            "category": "ADVISOR",
            "organization": "Wisdom Partners",
            "linkedin_url": "https://linkedin.com/in/alexcaveny",
            "total_meetings": 5,
            "last_contact_date": "2024-11-15",
            "merged_notes": "[crm.db] Strategic advisor\n\n[stakeholders] Founder coach",
            "sources": "crm.db, stakeholders",
            "source_count": 2,
        }
        
        path = generator.generate_profile(test_entity)
        
        assert path.exists(), f"Profile file not created: {path}"
        
        content = path.read_text()
        assert "Alex Caveny" in content
        assert "alex.caveny@gmail.com" in content
        assert "ADVISOR" in content
        assert "relationship_strength: strong" in content
        
        logger.info(f"✓ Test passed - Profile created at: {path}")
        logger.info(f"Content preview:\n{content[:500]}...")


if __name__ == "__main__":
    test_generator()

