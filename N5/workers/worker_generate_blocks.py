#!/usr/bin/env python3
"""
Block Generation Worker

Orchestrates sequential generation of meeting intelligence blocks.
Each block is generated in its own turn with full context and focus.

Workflow:
1. Load meeting transcript and metadata
2. Select relevant blocks based on content
3. Queue blocks to meeting_pipeline.db
4. Generate each block sequentially
5. Update registry as blocks complete
6. Assemble final intelligence.md

Usage:
    python3 worker_generate_blocks.py --meeting-id "2025-11-15_Person1_Person2"
    python3 worker_generate_blocks.py --meeting-path "/path/to/meeting/folder"

Updated: 2026-01-03 - Consolidated to single prompt source (Prompts/Blocks/)
"""

import argparse
import asyncio
import json
import logging
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# For HTTP requests to Zo API
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

# For direct Anthropic fallback
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logger = logging.getLogger(__name__)

# === PHASE 3: Memory Integration ===
# Import memory client for semantic enrichment
try:
    sys.path.insert(0, '/home/workspace')
    from N5.cognition.n5_memory_client import N5MemoryClient
    HAS_MEMORY = True
except ImportError as e:
    logger.warning(f"Memory client not available: {e}")
    HAS_MEMORY = False


class MemoryEnrichment:
    """Provides semantic memory context for block generation"""
    
    def __init__(self):
        self.client = N5MemoryClient() if HAS_MEMORY else None
        self._cache = {}  # Cache queries within a session
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def get_stakeholder_context(self, name: str, org: str = "") -> Dict:
        """Get prior relationship context for a stakeholder"""
        if not self.client:
            return {"available": False}
        
        cache_key = f"stakeholder:{name}:{org}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Search CRM for existing profile
            crm_results = self.client.search_profile(
                "crm", 
                f"{name} {org}".strip(),
                limit=3
            )
            
            # Search prior meetings
            meeting_results = self.client.search_profile(
                "meetings",
                name,
                limit=5
            )
            
            # Search prior B08 blocks for domain authority
            b08_results = self.client.search(
                query=f"{name} domain authority",
                metadata_filters={"path": ("contains", "B08")},
                limit=3
            )
            
            context = {
                "available": True,
                "crm_profile": crm_results[0] if crm_results else None,
                "prior_meetings_count": len(meeting_results),
                "prior_meetings": meeting_results[:3],
                "prior_b08_blocks": b08_results,
                "relationship_exists": len(crm_results) > 0 or len(meeting_results) > 0
            }
            
            self._cache[cache_key] = context
            return context
            
        except Exception as e:
            logger.warning(f"Memory enrichment failed for {name}: {e}")
            return {"available": False, "error": str(e)}
    
    def get_prior_block_context(self, block_code: str, query: str) -> List[Dict]:
        """Get prior blocks of same type for comparison"""
        if not self.client:
            return []
        
        cache_key = f"block:{block_code}:{query[:50]}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            results = self.client.search(
                query=query,
                metadata_filters={"path": ("contains", block_code)},
                limit=5
            )
            self._cache[cache_key] = results
            return results
        except Exception as e:
            logger.warning(f"Prior block search failed: {e}")
            return []
    
    def get_wellness_baseline(self) -> Dict:
        """Get wellness metrics baseline for B27 comparison"""
        if not self.client:
            return {"available": False}
        
        if "wellness_baseline" in self._cache:
            return self._cache["wellness_baseline"]
        
        try:
            # Get prior B27 blocks
            b27_results = self.client.search_profile(
                "meetings",
                "B27 wellness energy stress",
                limit=10
            )
            
            # Get health profile data
            health_results = self.client.search_profile(
                "wellness",
                "heart rate sleep energy baseline",
                limit=5
            )
            
            baseline = {
                "available": True,
                "prior_b27_count": len(b27_results),
                "prior_b27_blocks": b27_results[:5],
                "health_context": health_results[:3]
            }
            
            self._cache["wellness_baseline"] = baseline
            return baseline
            
        except Exception as e:
            logger.warning(f"Wellness baseline lookup failed: {e}")
            return {"available": False, "error": str(e)}
    
    def check_intro_target_exists(self, target_name: str) -> Dict:
        """Check if intro target already exists in network (for B07)"""
        if not self.client:
            return {"available": False}
        
        cache_key = f"intro_check:{target_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            crm_results = self.client.search_profile("crm", target_name, limit=2)
            meeting_results = self.client.search_profile("meetings", target_name, limit=3)
            
            result = {
                "available": True,
                "already_in_network": len(crm_results) > 0 or len(meeting_results) > 0,
                "crm_match": crm_results[0] if crm_results else None,
                "prior_meetings": meeting_results
            }
            
            self._cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.warning(f"Intro target check failed: {e}")
            return {"available": False, "error": str(e)}
    
    def format_for_prompt(self, enrichment_data: Dict) -> str:
        """Format enrichment data as context string for block prompts"""
        if not enrichment_data.get("available"):
            return "No prior context available."
        
        lines = []
        
        if enrichment_data.get("relationship_exists"):
            lines.append("⭐ PRIOR RELATIONSHIP DETECTED")
            if enrichment_data.get("prior_meetings_count"):
                lines.append(f"  - Prior meetings: {enrichment_data['prior_meetings_count']}")
            if enrichment_data.get("crm_profile"):
                lines.append(f"  - CRM profile exists: {enrichment_data['crm_profile'].get('path', 'unknown')}")
        
        if enrichment_data.get("prior_b08_blocks"):
            lines.append("\nPrior B08 context (domain authority baseline):")
            for b08 in enrichment_data["prior_b08_blocks"][:2]:
                lines.append(f"  - {b08.get('path', 'unknown')[:60]}...")
        
        if enrichment_data.get("already_in_network"):
            lines.append("\n⚠️ TARGET ALREADY IN NETWORK - flag for deduplication")
        
        return "\n".join(lines) if lines else "No enrichment context."


# === PHASE 4: LLM Integration ===
class LLMClient:
    """
    LLM client for block generation.
    
    Uses Zo /zo/ask API (preferred) with Anthropic direct API fallback.
    """
    
    ZO_API_URL = "https://api.zo.computer/zo/ask"
    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    
    def __init__(self):
        self.zo_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
        self.anthropic_client = None
        
        if HAS_ANTHROPIC:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        
        self._check_availability()
    
    def _check_availability(self):
        """Check which API is available"""
        if self.zo_token:
            logger.info("LLM: Using Zo /zo/ask API")
            self.mode = "zo"
        elif self.anthropic_client:
            logger.info("LLM: Using Anthropic direct API")
            self.mode = "anthropic"
        else:
            logger.warning("LLM: No API available - will return placeholders")
            self.mode = "placeholder"
    
    def is_available(self) -> bool:
        return self.mode != "placeholder"
    
    async def generate_async(self, prompt: str, max_tokens: int = 4096) -> str:
        """Generate completion using async Zo API"""
        if self.mode != "zo" or not HAS_AIOHTTP:
            return self._generate_sync(prompt, max_tokens)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.ZO_API_URL,
                    headers={
                        "authorization": self.zo_token,
                        "content-type": "application/json"
                    },
                    json={"input": prompt},
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("output", "")
                    else:
                        error = await resp.text()
                        logger.error(f"Zo API error {resp.status}: {error}")
                        return self._generate_sync(prompt, max_tokens)
        except Exception as e:
            logger.error(f"Zo API failed: {e}, falling back to sync")
            return self._generate_sync(prompt, max_tokens)
    
    def _generate_sync(self, prompt: str, max_tokens: int = 4096) -> str:
        """Synchronous generation with Anthropic fallback"""
        if self.mode == "placeholder":
            return "[LLM not available - placeholder content]"
        
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model=self.DEFAULT_MODEL,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except Exception as e:
                logger.error(f"Anthropic API failed: {e}")
                return f"[LLM generation failed: {e}]"
        
        return "[No LLM backend available]"
    
    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        """
        Generate completion (sync wrapper).
        
        Tries async Zo API first, falls back to sync Anthropic.
        """
        if self.mode == "zo" and HAS_AIOHTTP:
            try:
                return asyncio.run(self.generate_async(prompt, max_tokens))
            except RuntimeError:
                # Already in async context
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(self.generate_async(prompt, max_tokens))
        else:
            return self._generate_sync(prompt, max_tokens)
    
    def build_block_prompt(
        self,
        block_template: str,
        transcript: str,
        meeting_id: str,
        enrichment_context: str = "",
        metadata: Dict = None
    ) -> str:
        """
        Build the full prompt for block generation.
        
        Replaces template variables with actual content:
        - {{transcript}} -> meeting transcript
        - {{meeting_id}} -> meeting identifier
        - {{enrichment_context}} -> semantic memory context
        - {{convo_id}} -> provenance tracking
        """
        # Strip YAML frontmatter from template
        if block_template.startswith("---"):
            parts = block_template.split("---", 2)
            if len(parts) >= 3:
                block_template = parts[2].strip()
        
        # Build the prompt
        prompt = f"""You are generating a meeting intelligence block.

MEETING ID: {meeting_id}
GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ET

{f'PRIOR CONTEXT (from semantic memory):{chr(10)}{enrichment_context}{chr(10)}' if enrichment_context else ''}

BLOCK GENERATION INSTRUCTIONS:
{block_template}

---

MEETING TRANSCRIPT:
{transcript}

---

Generate the block now. Output ONLY the markdown content for this block, starting with the block header (# B##: Block Name).
Do not include any explanations or meta-commentary before or after the block content.
"""
        return prompt


# Constants - PHASE 1: Consolidated to single source of truth
BLOCKS_DIR = Path("/home/workspace/Prompts/Blocks")  # User-invokable prompts with latest features
DB_PATH = Path("/home/workspace/N5/data/meeting_pipeline.db")
WORKSPACE_ROOT = Path("/home/workspace")

# Block prompt filename mapping (maps block_code to prompt filename)
BLOCK_PROMPT_MAP = {
    "B01": "Generate_B01.prompt.md",
    "B02": "Generate_B02.prompt.md",
    "B03": "Generate_B03.prompt.md",
    "B04": "Generate_B04.prompt.md",
    "B05": "Generate_B05.prompt.md",
    "B06": "Generate_B06.prompt.md",
    "B07": "Generate_B07.prompt.md",
    "B08": "Generate_B08.prompt.md",
    "B09": "Generate_B09.prompt.md",  # NEW: Collaboration Terms
    "B10": "Generate_B10.prompt.md",  # NEW: Relationship Trajectory
    "B11": "Generate_B11.prompt.md",
    "B12": "Generate_B12.prompt.md",  # NEW: Technical Infrastructure
    "B13": "Generate_B13.prompt.md",
    "B14": "Generate_B14.prompt.md",
    "B15": "Generate_B15.prompt.md",
    "B16": "Generate_B16.prompt.md",
    "B17": "Generate_B17.prompt.md",
    "B20": "Generate_B20.prompt.md",
    "B21": "Generate_B21.prompt.md",
    "B22": "Generate_B22.prompt.md",
    "B23": "Generate_B23.prompt.md",
    "B24": "Generate_B24.prompt.md",
    "B25": "Generate_B25.prompt.md",
    "B26": "Generate_B26.prompt.md",
    "B27": "Generate_B27.prompt.md",
    "B31": "Generate_B31.prompt.md",  # NEW: Stakeholder Research
    "B32": "Generate_B32.prompt.md",  # NEW: Thought Provoking Ideas
}


class BlockOrchestrator:
    """Orchestrates sequential block generation for meetings"""
    
    def __init__(self, meeting_path: Path):
        self.meeting_path = meeting_path
        self.meeting_id = meeting_path.name
        self.transcript_path = self._find_transcript()
        
        # Initialize database
        self._init_db()
        
        # Initialize LLM and memory systems
        self.llm = LLMClient()
        self.memory = MemoryEnrichment()
        
        logger.info(f"LLM available: {self.llm.is_available()} (mode: {self.llm.mode})")
        logger.info(f"Memory available: {self.memory.is_available()}")
    
    def _init_db(self):
        """Initialize database connection and ensure schema exists."""
        db_path = WORKSPACE_ROOT / "N5" / "runtime" / "meeting_pipeline.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_conn = sqlite3.connect(str(db_path))
        self.db_conn.row_factory = sqlite3.Row
        
        # Ensure blocks table exists with current schema
        cursor = self.db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                id TEXT PRIMARY KEY,
                meeting_id TEXT NOT NULL,
                block_code TEXT NOT NULL,
                block_name TEXT NOT NULL,
                priority INTEGER DEFAULT 50,
                category TEXT DEFAULT 'contextual',
                status TEXT DEFAULT 'queued',
                queued_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                error_message TEXT,
                output_path TEXT,
                content TEXT,
                size_bytes INTEGER,
                UNIQUE(meeting_id, block_code)
            )
        """)
        self.db_conn.commit()
        logger.debug("Database initialized with blocks table")
    
    def _find_transcript(self) -> Optional[Path]:
        """Find transcript file in meeting folder"""
        candidates = [
            "transcript.md",
            "transcript.transcript.md",
            f"{self.meeting_id}.transcript.md"
        ]
        
        for candidate in candidates:
            path = self.meeting_path / candidate
            if path.exists():
                return path
        
        # Search for any .transcript.md file
        transcripts = list(self.meeting_path.glob("*.transcript.md"))
        if transcripts:
            return transcripts[0]
        
        logger.error(f"No transcript found in {self.meeting_path}")
        return None
    
    def load_transcript(self) -> str:
        """Load meeting transcript content"""
        if not self.transcript_path:
            raise FileNotFoundError("Transcript not found")
        
        with open(self.transcript_path, 'r') as f:
            return f.read()
    
    def select_blocks(self, transcript: str) -> List[Dict]:
        """
        Select which blocks to generate based on meeting content.
        
        PHASE 2: Updated selection logic with new block types (B09, B10, B12, B31, B32)
        
        Returns list of block definitions with:
        - block_code: B##
        - block_name: NAME
        - priority: 0-100
        - category: core/recommended/contextual
        """
        # Core blocks - always generate
        selected = [
            {"block_code": "B01", "block_name": "DETAILED_RECAP", "priority": 100, "category": "core"},
            {"block_code": "B02", "block_name": "COMMITMENTS", "priority": 95, "category": "core"},
            {"block_code": "B26", "block_name": "MEETING_METADATA", "priority": 90, "category": "core"},
        ]
        
        # Recommended blocks - usually generate
        selected.extend([
            {"block_code": "B03", "block_name": "DECISIONS", "priority": 80, "category": "recommended"},
            {"block_code": "B05", "block_name": "ACTION_ITEMS", "priority": 75, "category": "recommended"},
            {"block_code": "B21", "block_name": "KEY_MOMENTS", "priority": 70, "category": "recommended"},
        ])
        
        # Contextual blocks - generate based on content
        transcript_lower = transcript.lower()
        word_count = len(transcript_lower.split())
        
        # --- NEW BLOCK: B09 Collaboration Terms ---
        # Trigger on partnership/deal keywords
        partnership_keywords = [
            "partnership", "collaboration", "joint venture", "equity", "revenue share",
            "licensing", "white label", "distribution", "contract", "agreement",
            "terms", "scope", "deliverables", "milestone", "payment"
        ]
        if any(kw in transcript_lower for kw in partnership_keywords):
            selected.append({"block_code": "B09", "block_name": "COLLABORATION_TERMS", "priority": 72, "category": "contextual"})
        
        # --- NEW BLOCK: B10 Relationship Trajectory ---
        # Trigger for recurring contacts (substantial meetings with relationship history potential)
        if word_count > 800:  # Longer meetings suggest deeper relationships
            selected.append({"block_code": "B10", "block_name": "RELATIONSHIP_TRAJECTORY", "priority": 68, "category": "contextual"})
        
        # --- NEW BLOCK: B12 Technical Infrastructure ---
        # Trigger on technical implementation keywords
        technical_keywords = [
            "api", "integration", "platform", "infrastructure", "architecture",
            "webhook", "sdk", "endpoint", "authentication", "oauth",
            "database", "schema", "migration", "deployment", "aws", "gcp", "azure"
        ]
        if any(kw in transcript_lower for kw in technical_keywords):
            selected.append({"block_code": "B12", "block_name": "TECHNICAL_INFRASTRUCTURE", "priority": 64, "category": "contextual"})
        
        # Check for technical content (legacy B11)
        if any(word in transcript_lower for word in ["technical", "architecture", "implementation", "code"]):
            selected.append({"block_code": "B11", "block_name": "TECHNICAL_DETAILS", "priority": 65, "category": "contextual"})
        
        # Check for business/strategy
        if any(word in transcript_lower for word in ["strategy", "business model", "revenue", "market", "competition"]):
            selected.append({"block_code": "B06", "block_name": "BUSINESS_CONTEXT", "priority": 60, "category": "contextual"})
        
        # Check for stakeholder discussion
        if word_count > 500:  # Substantial meeting
            selected.append({"block_code": "B08", "block_name": "STAKEHOLDER_INTELLIGENCE", "priority": 55, "category": "contextual"})
        
        # Check for open questions
        if "?" in transcript or "question" in transcript_lower:
            selected.append({"block_code": "B04", "block_name": "OPEN_QUESTIONS", "priority": 50, "category": "contextual"})
        
        # Check for deliverables
        if any(word in transcript_lower for word in ["send", "deliver", "email", "follow up", "deck", "document"]):
            selected.append({"block_code": "B25", "block_name": "DELIVERABLES", "priority": 45, "category": "contextual"})
        
        # Check for risks (using B13 instead of B10 which is now Relationship Trajectory)
        if any(word in transcript_lower for word in ["risk", "concern", "worry", "problem", "challenge"]):
            selected.append({"block_code": "B13", "block_name": "RISKS_OPPORTUNITIES", "priority": 40, "category": "contextual"})
        
        # Check for introductions/networking (B07 Warm Intros)
        if any(word in transcript_lower for word in ["introduce", "connect", "know someone", "meet"]):
            selected.append({"block_code": "B07", "block_name": "WARM_INTRODUCTIONS", "priority": 35, "category": "contextual"})
        
        # --- NEW BLOCK: B31 Stakeholder Research ---
        # Trigger when specific companies, products, or competitive landscape discussed
        research_keywords = [
            "competitor", "alternative", "market leader", "pricing", "their product",
            "they're doing", "heard about", "looked into", "researched"
        ]
        if any(kw in transcript_lower for kw in research_keywords):
            selected.append({"block_code": "B31", "block_name": "STAKEHOLDER_RESEARCH", "priority": 52, "category": "contextual"})
        
        # --- NEW BLOCK: B32 Thought Provoking Ideas ---
        # Trigger for strategic/conceptual discussions
        thought_keywords = [
            "what if", "imagine", "future", "vision", "possibility", "paradigm",
            "rethink", "innovate", "disrupt", "transform", "opportunity"
        ]
        if any(kw in transcript_lower for kw in thought_keywords) and word_count > 600:
            selected.append({"block_code": "B32", "block_name": "THOUGHT_PROVOKING_IDEAS", "priority": 30, "category": "contextual"})
        
        # Sort by priority
        selected.sort(key=lambda x: x["priority"], reverse=True)
        
        logger.info(f"Selected {len(selected)} blocks for generation")
        for block in selected:
            logger.info(f"  - {block['block_code']}_{block['block_name']} (pri: {block['priority']})")
        
        return selected
    
    def queue_blocks(self, blocks: List[Dict]):
        """Queue blocks to meeting_pipeline.db"""
        cursor = self.db_conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        for block in blocks:
            block_id = f"{self.meeting_id}_{block['block_code']}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO blocks 
                (id, meeting_id, block_code, block_name, priority, category, status, queued_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (
                block_id,
                self.meeting_id,
                block['block_code'],
                block['block_name'],
                block['priority'],
                block.get('category', 'contextual'),
                now
            ))
        
        self.db_conn.commit()
        logger.info(f"Queued {len(blocks)} blocks to registry")
    
    def get_prompt_path(self, block_code: str) -> Optional[Path]:
        """Get the prompt file path for a block code"""
        prompt_filename = BLOCK_PROMPT_MAP.get(block_code)
        if prompt_filename:
            return BLOCKS_DIR / prompt_filename
        return None
    
    def _get_enrichment_for_block(self, block: Dict, transcript: str) -> str:
        """Get appropriate memory enrichment based on block type"""
        block_code = block['block_code']
        
        if not self.memory.is_available():
            return ""
        
        # B07: Warm Introductions - check if targets already exist
        if block_code == "B07":
            # Extract potential intro targets from transcript (basic extraction)
            # More sophisticated extraction could be done here
            return ""  # Let the block prompt handle it
        
        # B08, B10, B31: Stakeholder-related blocks
        if block_code in ["B08", "B10", "B31"]:
            # Get general stakeholder context
            context = self.memory.get_stakeholder_context("", "")
            return self.memory.format_for_prompt(context)
        
        # B27: Wellness - get baseline for comparison
        if block_code == "B27":
            baseline = self.memory.get_wellness_baseline()
            if baseline.get("available"):
                lines = [f"Prior B27 blocks available: {baseline.get('prior_b27_count', 0)}"]
                if baseline.get("health_context"):
                    lines.append("Health profile data available for baseline comparison")
                return "\n".join(lines)
            return ""
        
        # For other blocks, get prior blocks of same type for comparison
        prior_blocks = self.memory.get_prior_block_context(
            block_code, 
            f"{block['block_name']} meeting intelligence"
        )
        if prior_blocks:
            return f"Prior {block_code} blocks found: {len(prior_blocks)} (for style/format reference)"
        
        return ""
    
    def generate_block(self, block: Dict, transcript: str) -> str:
        """
        Generate a single block using LLM.
        
        PHASE 4: Full LLM integration with memory enrichment.
        """
        block_code = block['block_code']
        block_name = block['block_name']
        
        # Load block prompt template
        prompt_file = self.get_prompt_path(block_code)
        
        if not prompt_file or not prompt_file.exists():
            logger.warning(f"Prompt template not found for {block_code}: {prompt_file}")
            return f"# {block_code}: {block_name}\n\n[Generation skipped - prompt template missing]"
        
        with open(prompt_file, 'r') as f:
            block_template = f.read()
        
        logger.info(f"Generating {block_code}_{block_name} using {prompt_file.name}...")
        
        # Get memory enrichment context
        enrichment_context = self._get_enrichment_for_block(block, transcript)
        if enrichment_context:
            logger.info(f"  Memory enrichment: {len(enrichment_context)} chars")
        
        # Check if LLM is available
        if not self.llm.is_available():
            logger.warning(f"LLM not available, returning placeholder for {block_code}")
            return f"""# {block_code}: {block_name}

---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
provenance: worker_generate_blocks
block_type: {block_code}
---

[LLM not available - placeholder content]

**Block:** {block_name}
**Meeting:** {self.meeting_id}
**Transcript length:** {len(transcript)} chars

To generate real content, ensure either:
- ZO_CLIENT_IDENTITY_TOKEN is set (for Zo API)
- ANTHROPIC_API_KEY is set (for direct API)
"""
        
        # Build and send prompt to LLM
        full_prompt = self.llm.build_block_prompt(
            block_template=block_template,
            transcript=transcript,
            meeting_id=self.meeting_id,
            enrichment_context=enrichment_context
        )
        
        logger.info(f"  Sending to LLM ({self.llm.mode})...")
        start_time = datetime.now()
        
        try:
            content = self.llm.generate(full_prompt)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"  Generated {len(content)} chars in {elapsed:.1f}s")
            
            # Add frontmatter if not present
            if not content.strip().startswith("---"):
                frontmatter = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
provenance: {self.meeting_id}
block_type: {block_code}
---

"""
                content = frontmatter + content
            
            return content
            
        except Exception as e:
            logger.error(f"LLM generation failed for {block_code}: {e}")
            return f"""# {block_code}: {block_name}

[Generation failed: {e}]

**Meeting:** {self.meeting_id}
"""
    
    def update_block_status(self, block: Dict, status: str, content: Optional[str] = None, file_path: Optional[str] = None):
        """Update block status in registry"""
        cursor = self.db_conn.cursor()
        block_id = f"{self.meeting_id}_{block['block_code']}"
        now = datetime.now(timezone.utc).isoformat()
        
        if status == "generating":
            cursor.execute("UPDATE blocks SET status = ?, started_at = ? WHERE id = ?", 
                          (status, now, block_id))
        elif status == "complete":
            cursor.execute("""
                UPDATE blocks SET status = ?, completed_at = ?, content = ?, size_bytes = ?, output_path = ?
                WHERE id = ?
            """, (status, now, content, len(content.encode('utf-8')) if content else 0, file_path, block_id))
        else:
            cursor.execute("UPDATE blocks SET status = ? WHERE id = ?", (status, block_id))
        
        self.db_conn.commit()
    
    def save_block_file(self, block: Dict, content: str) -> Path:
        """Save block content to individual file"""
        block_code = block['block_code']
        block_name = block['block_name']
        filename = f"{block_code}_{block_name}.md"
        file_path = self.meeting_path / filename
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Saved block to {file_path}")
        return file_path
    
    def assemble_intelligence_doc(self, blocks: List[Dict]):
        """Assemble all blocks into intelligence.md"""
        intelligence_path = self.meeting_path / "intelligence.md"
        
        with open(intelligence_path, 'w') as f:
            f.write(f"# Meeting Intelligence: {self.meeting_id}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}\n\n")
            f.write("---\n\n")
            
            for block in blocks:
                block_file = self.meeting_path / f"{block['block_code']}_{block['block_name']}.md"
                if block_file.exists():
                    with open(block_file, 'r') as bf:
                        content = bf.read()
                        f.write(content)
                        f.write("\n\n---\n\n")
        
        logger.info(f"Assembled intelligence.md at {intelligence_path}")
    
    def run(self):
        """Main orchestration workflow"""
        logger.info(f"Starting block generation for {self.meeting_id}")
        
        # Load transcript
        transcript = self.load_transcript()
        logger.info(f"Loaded transcript: {len(transcript)} chars")
        
        # Select blocks
        blocks = self.select_blocks(transcript)
        
        # Queue blocks
        self.queue_blocks(blocks)
        
        # Generate each block sequentially
        for block in blocks:
            try:
                self.update_block_status(block, "generating")
                
                content = self.generate_block(block, transcript)
                
                file_path = self.save_block_file(block, content)
                
                self.update_block_status(block, "complete", content=content, file_path=str(file_path))
                
            except Exception as e:
                logger.error(f"Failed to generate {block['block_code']}: {e}")
                self.update_block_status(block, "failed")
        
        # Assemble intelligence doc
        self.assemble_intelligence_doc(blocks)
        
        logger.info("Block generation complete!")
        self.db_conn.close()


def main():
    parser = argparse.ArgumentParser(description="Generate meeting intelligence blocks")
    parser.add_argument("--meeting-id", help="Meeting ID (folder name)")
    parser.add_argument("--meeting-path", help="Full path to meeting folder")
    
    args = parser.parse_args()
    
    if args.meeting_path:
        meeting_path = Path(args.meeting_path)
    elif args.meeting_id:
        meeting_path = WORKSPACE_ROOT / "Personal" / "Meetings" / args.meeting_id
    else:
        print("Error: Must provide --meeting-id or --meeting-path")
        return 1
    
    if not meeting_path.exists():
        print(f"Error: Meeting path not found: {meeting_path}")
        return 1
    
    orchestrator = BlockOrchestrator(meeting_path)
    orchestrator.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())








