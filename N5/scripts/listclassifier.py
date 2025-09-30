#!/usr/bin/env python3
import re
from typing import List, Tuple
from urllib.parse import urlparse

def classify_list(content: str, available_slugs: List[str]) -> Tuple[str, str]:
    """
    Classify content to determine target list.
    Returns (list_slug, rationale)
    """
    content_lower = content.lower()

    # First check for URL patterns
    url_result = classify_by_url(content, available_slugs)
    if url_result[0]:
        return url_result

    # Then check for system-upgrades keywords
    system_keywords = ["system", "upgrade", "config", "audit", "workflow", "prefs", "management", "enhance", "improve"]
    if any(kw in content_lower for kw in system_keywords):
        slug = "system-upgrades"
        rationale = "Contains system/upgrade related keywords"
    else:
        slug = "ideas"
        rationale = "Default fallback"

    # Check if slug is available, fallback if not
    if slug not in available_slugs:
        if "ideas" in available_slugs:
            slug = "ideas"
            rationale += "; fallback to ideas (system-upgrades not available)"
        elif available_slugs:
            slug = available_slugs[0]
            rationale += f"; fallback to {slug} (not available)"

    return slug, rationale

def classify_by_url(content: str, available_slugs: List[str]) -> Tuple[str, str]:
    """
    Classify content based on URL patterns.
    Returns (list_slug, rationale) or ("", "") if no URL match
    """
    # Extract URLs from content
    url_pattern = r'https?://[^\s<>"\'`(){}[\]|\\^]+'
    urls = re.findall(url_pattern, content)
    
    if not urls:
        return "", ""
    
    for url in urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # LinkedIn profiles -> CRM
            if 'linkedin.com' in domain and ('/in/' in path or '/profile/' in path):
                if 'crm' in available_slugs:
                    return 'crm', 'LinkedIn profile URL detected'
                elif 'contacts' in available_slugs:
                    return 'contacts', 'LinkedIn profile URL detected (CRM not available)'
            
            # LinkedIn company pages -> CRM  
            elif 'linkedin.com' in domain and '/company/' in path:
                if 'crm' in available_slugs:
                    return 'crm', 'LinkedIn company page detected'
                elif 'contacts' in available_slugs:
                    return 'contacts', 'LinkedIn company page detected (CRM not available)'
            
            # GitHub repositories -> projects/development
            elif 'github.com' in domain and len(path.split('/')) >= 3:
                if 'projects' in available_slugs:
                    return 'projects', 'GitHub repository URL detected'
                elif 'development' in available_slugs:
                    return 'development', 'GitHub repository URL detected'
            
            # YouTube videos -> media/content
            elif 'youtube.com' in domain or 'youtu.be' in domain:
                if 'media' in available_slugs:
                    return 'media', 'YouTube video URL detected'
                elif 'content' in available_slugs:
                    return 'content', 'YouTube video URL detected'
            
            # Twitter/X posts -> social
            elif domain in ['twitter.com', 'x.com'] and '/status/' in path:
                if 'social' in available_slugs:
                    return 'social', 'Twitter/X post URL detected'
                elif 'social-media' in available_slugs:
                    return 'social-media', 'Twitter/X post URL detected'
            
            # Articles/blogs -> reading
            elif any(indicator in domain for indicator in ['medium.com', 'substack.com', 'blog.', 'article.']):
                if 'reading' in available_slugs:
                    return 'reading', 'Blog/article URL detected'
                elif 'articles' in available_slugs:
                    return 'articles', 'Blog/article URL detected'
            
            # News sites -> reading/news
            elif any(news_site in domain for news_site in ['nytimes.com', 'washingtonpost.com', 'reuters.com', 'bbc.com', 'cnn.com', 'npr.org']):
                if 'news' in available_slugs:
                    return 'news', 'News article URL detected'
                elif 'reading' in available_slugs:
                    return 'reading', 'News article URL detected'
                    
        except Exception:
            continue  # Skip malformed URLs
    
    return "", ""  # No URL patterns matched

def extract_tags(content: str, max_tags: int = 3) -> List[str]:
    """
    Extract tags from content using simple token-based approach.
    Returns list of up to max_tags tags.
    """
    # Split by whitespace and punctuation
    tokens = re.split(r'[\s\W]+', content.lower())
    # Filter tokens: length > 3, no numbers, alphabetic
    candidates = [t for t in tokens if len(t) > 3 and t.isalpha()]
    # Take unique, up to max_tags
    tags = list(dict.fromkeys(candidates))[:max_tags]
    return tags