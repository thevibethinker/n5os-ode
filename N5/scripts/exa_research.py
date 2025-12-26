#!/usr/bin/env python3
"""
exa_research.py - Exa API wrapper with N5 OS integration

Core capabilities:
  - Neural search (fast semantic search)
  - Deep search (multi-query expansion + synthesis)
  - Research API (autonomous multi-step research agent)
  - Live crawl (real-time content fetch)
  - Find similar (discover related content)
  - Direct Content Library ingestion
  - Save to markdown file with clean formatting

Usage:
  python exa_research.py search "query" [--type neural|keyword|auto]
  python exa_research.py deep "query" [--save FILE] [--tags TAG ...]
  python exa_research.py research "instructions" [--schema FILE]
  python exa_research.py crawl "url" [--subpages]
  python exa_research.py similar "url"
  python exa_research.py ingest "query" [--topics TOPIC ...]

Categories (for neural search):
  company, research paper, pdf, github, tweet, personal site, linkedin profile, financial report
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Load API key
SECRETS_PATH = Path("/home/workspace/N5/config/secrets/exa_api_key.env")
API_KEY: Optional[str] = None

if SECRETS_PATH.exists():
    for line in SECRETS_PATH.read_text().strip().split("\n"):
        if line.startswith("EXA_API_KEY="):
            API_KEY = line.split("=", 1)[1].strip()
            break

if not API_KEY:
    API_KEY = os.environ.get("EXA_API_KEY")

# Content Library integration
try:
    from content_library_v3 import ContentLibraryV3
    CONTENT_LIBRARY_AVAILABLE = True
except ImportError:
    CONTENT_LIBRARY_AVAILABLE = False
    logger.warning("Content Library v3 not available")


# Patterns to strip from content (cookie notices, navigation, etc.)
NOISE_PATTERNS = [
    r'This website uses cookies.*?(?=\n\n|\Z)',
    r'We use cookies.*?(?=\n\n|\Z)',
    r'Cookie\s*(Consent|Policy|Settings).*?(?=\n\n|\Z)',
    r'\[Skip to (content|main)\].*?\n',
    r'\[Return to Blog\].*?\n',
    r'Sign up with (Apple|Google|Email).*?\n',
    r'By signing up, you agree to.*?(?=\n\n|\Z)',
    r'Maximum Storage Duration:.*?\n',
    r'\*\*Type\*\*: (HTTP Cookie|Pixel Tracker|HTML Local Storage).*?\n',
    r'!\[.*?\]\(https?://[^)]+\)',  # Remove image markdown
    r'\[!\[.*?\]\(.*?\)\]\(.*?\)',  # Remove linked images
    r'Learn more about this provider.*?\n',
    r'\\{2,}',  # Multiple backslashes
    r'\n{4,}',  # More than 3 newlines
]

COMPILED_NOISE = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in NOISE_PATTERNS]


def clean_content(text: str) -> str:
    """Remove cookie notices, navigation elements, and other noise from content."""
    if not text:
        return ""
    
    # Apply noise patterns
    for pattern in COMPILED_NOISE:
        text = pattern.sub('', text)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove lines that are just navigation/links
    lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        # Skip lines that are just markdown links or short navigation
        if stripped.startswith('[') and stripped.endswith(')') and len(stripped) < 100:
            continue
        if stripped.lower() in ('accept', 'reject', 'close', 'menu', 'skip', 'back', 'next'):
            continue
        lines.append(line)
    
    return '\n'.join(lines).strip()


def clean_url(url: str) -> str:
    """Remove tracking parameters and clean up URLs."""
    if not url:
        return ""
    
    # Unescape HTML entities
    url = url.replace('&amp;', '&')
    
    # Parse and rebuild without tracking params
    parsed = urlparse(url)
    
    # Common tracking parameters to remove
    tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
                       'ref', 'source', 'fbclid', 'gclid', 'mc_cid', 'mc_eid'}
    
    if parsed.query:
        params = parsed.query.split('&')
        clean_params = [p for p in params if not any(p.startswith(t + '=') for t in tracking_params)]
        if clean_params:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{'&'.join(clean_params)}"
        else:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    return url


def extract_domain(url: str) -> str:
    """Extract clean domain name from URL."""
    if not url:
        return "Unknown"
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    # Capitalize nicely
    parts = domain.split('.')
    if parts:
        return parts[0].title()
    return domain


def extract_best_excerpt(item: Dict[str, Any], max_length: int = 500) -> str:
    """Extract the most relevant excerpt from highlights or text."""
    # Prefer highlights
    highlights = item.get("highlights") or []
    if highlights:
        # Join highlights, clean them
        combined = " ".join(h for h in highlights if h and len(h) > 50)
        if combined:
            cleaned = clean_content(combined)
            if len(cleaned) > max_length:
                return cleaned[:max_length].rsplit(' ', 1)[0] + "..."
            return cleaned
    
    # Fall back to text
    text = item.get("text", "")
    if text:
        cleaned = clean_content(text)
        # Take first meaningful paragraph
        paragraphs = [p.strip() for p in cleaned.split('\n\n') if len(p.strip()) > 100]
        if paragraphs:
            excerpt = paragraphs[0]
            if len(excerpt) > max_length:
                return excerpt[:max_length].rsplit(' ', 1)[0] + "..."
            return excerpt
    
    return ""


@dataclass
class ExaResult:
    """Standardized result from any Exa operation."""
    success: bool
    operation: str
    query: Optional[str] = None
    results: List[Dict[str, Any]] = field(default_factory=list)
    text: Optional[str] = None
    cost_usd: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "operation": self.operation,
            "query": self.query,
            "results": self.results,
            "text": self.text,
            "cost_usd": self.cost_usd,
            "error": self.error,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def to_markdown(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Generate clean markdown document from results."""
        now = datetime.now()
        
        # Generate title from query if not provided
        if not title:
            title = self.query.title() if self.query else "Exa Research Results"
        
        # Build frontmatter
        frontmatter_lines = [
            "---",
            f"created: {now.strftime('%Y-%m-%d')}",
            f"last_edited: {now.strftime('%Y-%m-%d')}",
            "version: 1.0",
            "source: exa_research",
            f"search_type: {self.metadata.get('search_type', self.operation)}",
            f'query: "{self.query}"',
            f"result_count: {len(self.results)}",
        ]
        
        if tags:
            frontmatter_lines.append("tags:")
            for tag in tags:
                frontmatter_lines.append(f"  - {tag}")
        
        frontmatter_lines.append("---")
        
        # Build document body
        body_lines = [
            "",
            f"# {title}",
            "",
        ]
        
        if description:
            body_lines.extend([description, ""])
        
        body_lines.extend([
            f"**Query:** {self.query}  ",
            f"**Search Type:** {self.metadata.get('search_type', self.operation).title()}  ",
            f"**Retrieved:** {now.strftime('%Y-%m-%d')}",
            "",
            "---",
            "",
            "## Key Sources",
            "",
        ])
        
        # Format each result
        for i, item in enumerate(self.results, 1):
            title_text = item.get("title") or "Untitled"
            url = clean_url(item.get("url", ""))
            published = item.get("published_date", "")
            source = extract_domain(url)
            excerpt = extract_best_excerpt(item)
            
            # Format published date nicely
            if published:
                try:
                    if isinstance(published, str):
                        # Handle ISO format
                        pub_date = published.split("T")[0]
                    else:
                        pub_date = str(published)
                except:
                    pub_date = ""
            else:
                pub_date = ""
            
            body_lines.append(f"### {i}. {title_text}")
            body_lines.append("")
            body_lines.append(f"**Source:** {source}  ")
            body_lines.append(f"**URL:** {url}  ")
            if pub_date:
                body_lines.append(f"**Published:** {pub_date}")
            body_lines.append("")
            
            if excerpt:
                body_lines.append(f"> {excerpt}")
                body_lines.append("")
            
            # Add relevance note if we have highlights
            if item.get("highlights"):
                body_lines.append(f"**Relevance:** Contains key information about {self.query}.")
                body_lines.append("")
            
            body_lines.append("---")
            body_lines.append("")
        
        # Add summary section placeholder
        body_lines.extend([
            "## Summary",
            "",
            "_Add synthesis of key findings here._",
            "",
        ])
        
        return "\n".join(frontmatter_lines + body_lines)

    def save_markdown(
        self,
        filepath: Path,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Path:
        """Save results as clean markdown file."""
        content = self.to_markdown(title=title, description=description, tags=tags)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        logger.info("Saved markdown to: %s", filepath)
        return filepath


class ExaResearch:
    """Exa API client with N5 patterns."""

    CATEGORIES = [
        "company",
        "research paper",
        "pdf",
        "github",
        "tweet",
        "personal site",
        "linkedin profile",
        "financial report",
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValueError("EXA_API_KEY not found. Set it in N5/config/secrets/exa_api_key.env or environment.")
        
        try:
            from exa_py import Exa
            self.client = Exa(self.api_key)
        except ImportError:
            raise ImportError("exa-py not installed. Run: pip install exa-py")

    def search(
        self,
        query: str,
        search_type: str = "auto",
        category: Optional[str] = None,
        num_results: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        include_text: Optional[List[str]] = None,
        get_contents: bool = True,
        highlights: bool = True,
    ) -> ExaResult:
        """Neural/keyword/auto search."""
        try:
            kwargs: Dict[str, Any] = {
                "query": query,
                "type": search_type,
            }
            
            if search_type != "deep" and num_results:
                kwargs["num_results"] = num_results

            if category and category in self.CATEGORIES:
                kwargs["category"] = category
            if include_domains:
                kwargs["include_domains"] = include_domains
            if exclude_domains:
                kwargs["exclude_domains"] = exclude_domains
            if start_published_date:
                kwargs["start_published_date"] = start_published_date
            if end_published_date:
                kwargs["end_published_date"] = end_published_date
            if include_text:
                kwargs["include_text"] = include_text

            if get_contents:
                contents_config: Dict[str, Any] = {"text": {"maxCharacters": 10000}}
                if highlights:
                    contents_config["highlights"] = True
                kwargs["contents"] = contents_config
            else:
                kwargs["contents"] = False

            response = self.client.search(**kwargs)

            results = []
            for r in response.results:
                item = {
                    "title": getattr(r, "title", None),
                    "url": getattr(r, "url", None),
                    "score": getattr(r, "score", None),
                    "published_date": getattr(r, "published_date", None),
                    "author": getattr(r, "author", None),
                }
                if get_contents:
                    item["text"] = getattr(r, "text", None)
                    if highlights:
                        item["highlights"] = getattr(r, "highlights", None)
                results.append(item)

            return ExaResult(
                success=True,
                operation="search",
                query=query,
                results=results,
                metadata={
                    "search_type": search_type,
                    "category": category,
                    "num_results": len(results),
                },
            )

        except Exception as e:
            logger.error("Search failed: %s", e)
            return ExaResult(success=False, operation="search", query=query, error=str(e))

    def deep_search(
        self,
        query: str,
        category: Optional[str] = None,
    ) -> ExaResult:
        """Deep search using Exa's native deep search (type='deep')."""
        try:
            kwargs: Dict[str, Any] = {
                "query": query,
                "type": "deep",
                "contents": {"text": {"maxCharacters": 10000}, "highlights": True},
            }
            
            if category and category in self.CATEGORIES:
                kwargs["category"] = category

            response = self.client.search(**kwargs)

            results = []
            for r in response.results:
                results.append({
                    "title": getattr(r, "title", None),
                    "url": getattr(r, "url", None),
                    "score": getattr(r, "score", None),
                    "published_date": getattr(r, "published_date", None),
                    "author": getattr(r, "author", None),
                    "text": getattr(r, "text", None),
                    "highlights": getattr(r, "highlights", None),
                })

            return ExaResult(
                success=True,
                operation="deep_search",
                query=query,
                results=results,
                metadata={
                    "search_type": "deep",
                    "category": category,
                    "total_results": len(results),
                },
            )

        except Exception as e:
            logger.error("Deep search failed: %s", e)
            return ExaResult(success=False, operation="deep_search", query=query, error=str(e))

    def research(
        self,
        instructions: str,
        output_schema: Optional[Dict[str, Any]] = None,
        model: str = "exa-research",
        timeout_seconds: int = 180,
    ) -> ExaResult:
        """Use Exa Research API for autonomous multi-step research."""
        try:
            kwargs: Dict[str, Any] = {
                "model": model,
                "instructions": instructions,
            }
            if output_schema:
                kwargs["output_schema"] = output_schema

            task = self.client.research.create(**kwargs)
            research_id = getattr(task, "researchId", getattr(task, "research_id", None))

            if not research_id:
                raise ValueError("Failed to extract research ID from task response")

            logger.info("Research task created: %s", research_id)

            start = time.time()
            while time.time() - start < timeout_seconds:
                status = self.client.research.get(research_id)
                
                if status.status == "completed":
                    return ExaResult(
                        success=True,
                        operation="research",
                        query=instructions,
                        text=getattr(status, "output", None) or getattr(status, "report", None),
                        results=[{"research_id": research_id, "status": "completed"}],
                        cost_usd=getattr(status, "cost", None),
                        metadata={
                            "model": model,
                            "research_id": research_id,
                            "has_schema": output_schema is not None,
                            "search_type": "research",
                        },
                    )
                elif status.status == "failed":
                    return ExaResult(
                        success=False,
                        operation="research",
                        query=instructions,
                        error=f"Research task failed: {getattr(status, 'error', 'unknown')}",
                    )
                
                time.sleep(5)

            return ExaResult(
                success=False,
                operation="research",
                query=instructions,
                error=f"Research task timed out after {timeout_seconds}s",
            )

        except Exception as e:
            logger.error("Research failed: %s", e)
            return ExaResult(success=False, operation="research", query=instructions, error=str(e))

    def crawl(
        self,
        url: str,
        include_subpages: bool = False,
        subpage_target: Optional[int] = None,
    ) -> ExaResult:
        """Live crawl a URL (and optionally subpages)."""
        try:
            kwargs: Dict[str, Any] = {
                "urls": [url],  # Changed from 'ids' to 'urls'
                "text": True,
                "livecrawl": "always",
            }
            
            if include_subpages:
                kwargs["subpages"] = subpage_target or 5
                kwargs["subpage_target"] = subpage_target or 5

            response = self.client.get_contents(**kwargs)

            results = []
            for r in response.results:
                results.append({
                    "url": getattr(r, "url", url),
                    "title": getattr(r, "title", None),
                    "text": getattr(r, "text", None),
                    "published_date": getattr(r, "published_date", None),
                })

            return ExaResult(
                success=True,
                operation="crawl",
                query=url,
                results=results,
                text=results[0].get("text") if results else None,
                metadata={"live_crawl": True, "include_subpages": include_subpages, "search_type": "crawl"},
            )

        except Exception as e:
            logger.error("Crawl failed: %s", e)
            return ExaResult(success=False, operation="crawl", query=url, error=str(e))

    def find_similar(
        self,
        url: str,
        num_results: int = 10,
        exclude_source: bool = True,
    ) -> ExaResult:
        """Find content similar to a given URL."""
        try:
            response = self.client.find_similar_and_contents(
                url=url,
                num_results=num_results,
                exclude_source_domain=exclude_source,
                text=True,
            )

            results = []
            for r in response.results:
                results.append({
                    "url": getattr(r, "url", None),
                    "title": getattr(r, "title", None),
                    "score": getattr(r, "score", None),
                    "text": getattr(r, "text", None),
                })

            return ExaResult(
                success=True,
                operation="find_similar",
                query=url,
                results=results,
                metadata={"num_results": len(results), "search_type": "similar"},
            )

        except Exception as e:
            logger.error("Find similar failed: %s", e)
            return ExaResult(success=False, operation="find_similar", query=url, error=str(e))

    def ingest_to_content_library(
        self,
        result: ExaResult,
        topics: Optional[List[str]] = None,
        item_type: str = "link",
        max_items: int = 10,
    ) -> List[str]:
        """Ingest Exa search results directly into Content Library v3."""
        if not CONTENT_LIBRARY_AVAILABLE:
            logger.error("Content Library v3 not available")
            return []

        if not result.success or not result.results:
            logger.warning("No results to ingest")
            return []

        cl = ContentLibraryV3()
        created_ids = []

        for item in result.results[:max_items]:
            url = item.get("url")
            title = item.get("title") or "Untitled"
            text = clean_content(item.get("text", ""))

            if not url:
                continue

            # Generate deterministic ID from URL
            item_id = f"exa_{hashlib.md5(url.encode()).hexdigest()[:12]}"

            # Check if exists
            existing = cl.get(item_id)
            if existing:
                logger.info("Item already exists: %s", item_id)
                continue

            try:
                cl.add(
                    id=item_id,
                    item_type=item_type,
                    title=title,
                    url=clean_url(url),
                    content=text[:50000] if text else None,
                    source_type="exa",
                    platform=self._extract_platform(url),
                    author=item.get("author"),
                    topics=topics,
                    notes=f"Ingested from Exa {result.operation} on {datetime.now().isoformat()}. Query: {result.query}",
                )
                created_ids.append(item_id)
                logger.info("Ingested to Content Library: %s (%s)", item_id, title[:50])
            except Exception as e:
                logger.error("Failed to ingest %s: %s", url, e)

        return created_ids

    def _extract_platform(self, url: str) -> Optional[str]:
        """Extract platform from URL."""
        url_lower = url.lower()
        platforms = {
            "github.com": "github",
            "linkedin.com": "linkedin",
            "twitter.com": "twitter",
            "x.com": "twitter",
            "arxiv.org": "arxiv",
            "medium.com": "medium",
            "substack.com": "substack",
            "youtube.com": "youtube",
        }
        for domain, platform in platforms.items():
            if domain in url_lower:
                return platform
        return None


def main():
    parser = argparse.ArgumentParser(description="Exa Research API wrapper for N5 OS")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_p = subparsers.add_parser("search", help="Neural/keyword search")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--type", choices=["neural", "keyword", "auto"], default="auto")
    search_p.add_argument("--category", choices=ExaResearch.CATEGORIES)
    search_p.add_argument("--num", type=int, default=10, help="Number of results")
    search_p.add_argument("--include-domains", nargs="+", help="Only these domains")
    search_p.add_argument("--exclude-domains", nargs="+", help="Exclude these domains")
    search_p.add_argument("--no-contents", action="store_true", help="Skip fetching page contents")
    search_p.add_argument("--save", type=Path, help="Save results to markdown file")
    search_p.add_argument("--tags", nargs="+", help="Tags for saved markdown")

    # Deep search command
    deep_p = subparsers.add_parser("deep", help="Deep search with query expansion")
    deep_p.add_argument("query", help="Search query")
    deep_p.add_argument("--category", choices=ExaResearch.CATEGORIES)
    deep_p.add_argument("--save", type=Path, help="Save results to markdown file")
    deep_p.add_argument("--tags", nargs="+", help="Tags for saved markdown")
    deep_p.add_argument("--title", help="Custom title for saved document")
    deep_p.add_argument("--description", help="Description for saved document")

    # Research command
    research_p = subparsers.add_parser("research", help="Autonomous research agent")
    research_p.add_argument("instructions", help="Research instructions")
    research_p.add_argument("--schema", type=Path, help="JSON schema file for structured output")
    research_p.add_argument("--model", choices=["exa-research", "exa-research-pro"], default="exa-research")
    research_p.add_argument("--timeout", type=int, default=180, help="Timeout in seconds")
    research_p.add_argument("--save", type=Path, help="Save results to markdown file")

    # Crawl command
    crawl_p = subparsers.add_parser("crawl", help="Live crawl a URL")
    crawl_p.add_argument("url", help="URL to crawl")
    crawl_p.add_argument("--subpages", type=int, help="Number of subpages to crawl")
    crawl_p.add_argument("--save", type=Path, help="Save results to file")

    # Similar command
    similar_p = subparsers.add_parser("similar", help="Find similar content")
    similar_p.add_argument("url", help="Source URL")
    similar_p.add_argument("--num", type=int, default=10)
    similar_p.add_argument("--save", type=Path, help="Save results to markdown file")

    # Ingest command (search + add to content library)
    ingest_p = subparsers.add_parser("ingest", help="Search and ingest to Content Library")
    ingest_p.add_argument("query", help="Search query")
    ingest_p.add_argument("--type", choices=["neural", "keyword", "auto"], default="auto")
    ingest_p.add_argument("--category", choices=ExaResearch.CATEGORIES)
    ingest_p.add_argument("--topics", nargs="+", help="Topics to tag items with")
    ingest_p.add_argument("--item-type", default="link", help="Content Library item type")
    ingest_p.add_argument("--max", type=int, default=5, help="Max items to ingest")

    # Add --json and --quiet to all subparsers
    for p in [search_p, deep_p, research_p, crawl_p, similar_p, ingest_p]:
        p.add_argument("--json", action="store_true", help="Output as JSON")
        p.add_argument("--quiet", action="store_true", help="Minimal output")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    try:
        exa = ExaResearch()
    except Exception as e:
        logger.error("Failed to initialize Exa client: %s", e)
        sys.exit(1)

    result: Optional[ExaResult] = None

    if args.command == "search":
        result = exa.search(
            query=args.query,
            search_type=args.type,
            category=args.category,
            num_results=args.num,
            include_domains=args.include_domains,
            exclude_domains=args.exclude_domains,
            get_contents=not args.no_contents,
        )
        if result.success and args.save:
            result.save_markdown(args.save, tags=args.tags)

    elif args.command == "deep":
        result = exa.deep_search(
            query=args.query,
            category=args.category,
        )
        if result.success and args.save:
            result.save_markdown(
                args.save, 
                title=args.title, 
                description=args.description, 
                tags=args.tags
            )

    elif args.command == "research":
        schema = None
        if args.schema and args.schema.exists():
            schema = json.loads(args.schema.read_text())
        result = exa.research(
            instructions=args.instructions,
            output_schema=schema,
            model=args.model,
            timeout_seconds=args.timeout,
        )
        if result.success and args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            args.save.write_text(result.text or "")
            logger.info("Saved research output to: %s", args.save)

    elif args.command == "crawl":
        result = exa.crawl(
            url=args.url,
            include_subpages=args.subpages is not None,
            subpage_target=args.subpages,
        )
        if result.success and args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            args.save.write_text(result.text or "")
            logger.info("Saved crawl output to: %s", args.save)

    elif args.command == "similar":
        result = exa.find_similar(url=args.url, num_results=args.num)
        if result.success and args.save:
            result.save_markdown(args.save)

    elif args.command == "ingest":
        search_result = exa.search(
            query=args.query,
            search_type=args.type,
            category=args.category,
            num_results=args.max * 2,
        )
        
        if search_result.success:
            created = exa.ingest_to_content_library(
                result=search_result,
                topics=args.topics,
                item_type=args.item_type,
                max_items=args.max,
            )
            result = ExaResult(
                success=True,
                operation="ingest",
                query=args.query,
                results=[{"id": id} for id in created],
                metadata={
                    "ingested_count": len(created),
                    "search_results": len(search_result.results),
                    "search_type": "ingest",
                },
            )
        else:
            result = search_result

    if result:
        if args.json:
            print(result.to_json())
        else:
            if result.success:
                print(f"✓ {result.operation} completed")
                if result.results:
                    print(f"  Results: {len(result.results)}")
                    for i, r in enumerate(result.results[:5], 1):
                        title = r.get("title", r.get("url", r.get("id", "Unknown")))
                        if title:
                            title = title[:60]
                        print(f"    {i}. {title}")
                    if len(result.results) > 5:
                        print(f"    ... and {len(result.results) - 5} more")
                if result.text and not args.quiet:
                    print(f"\n--- Output ---\n{str(result.text)[:2000]}")
                    if len(str(result.text)) > 2000:
                        print(f"\n... [{len(str(result.text)) - 2000} more chars]")
            else:
                print(f"✗ {result.operation} failed: {result.error}")
                sys.exit(1)


if __name__ == "__main__":
    main()




