#!/usr/bin/env python3
"""
LinkedIn Intelligence Module for Meeting Prep Digest
Extracts posts, DMs, profile data using authenticated Zo browser.
Auto-enriches stakeholder profiles with new intelligence.

Author: N5 OS
Version: 2.0.0
Date: 2025-10-14
"""

import logging
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path("/home/workspace/N5/runtime/linkedin_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_TTL = timedelta(hours=24)

# Profiles directory
PROFILES_DIR = Path("/home/workspace/Knowledge/crm/individuals")


class LinkedInIntel:
    """LinkedIn intelligence extractor using authenticated Zo browser."""
    
    def __init__(self, view_webpage_tool: Optional[Callable] = None):
        """
        Initialize LinkedIn intelligence module.
        
        Args:
            view_webpage_tool: Function to fetch webpages with authenticated browser
                             Signature: view_webpage_tool(url: str) -> Dict with 'content' key
        """
        self.view_webpage_tool = view_webpage_tool
        self.cache_dir = Path("/home/workspace/N5/runtime/linkedin_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl_hours = 24
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key."""
        safe_key = re.sub(r'[^\w\-]', '_', cache_key)
        return self.cache_dir / f"{safe_key}.json"
    
    def _read_cache(self, cache_key: str) -> Optional[Dict]:
        """Read from cache if not expired."""
        cache_file = self._get_cache_path(cache_key)
        if not cache_file.exists():
            return None
        
        try:
            data = json.loads(cache_file.read_text())
            cached_time = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
            
            if datetime.now() - cached_time < CACHE_TTL:
                logger.info(f"Cache hit: {cache_key}")
                return data.get('data')
            else:
                logger.info(f"Cache expired: {cache_key}")
                return None
        except Exception as e:
            logger.warning(f"Cache read error for {cache_key}: {e}")
            return None
    
    def _write_cache(self, cache_key: str, data: any):
        """Write data to cache with timestamp."""
        cache_file = self._get_cache_path(cache_key)
        try:
            cache_file.write_text(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'data': data
            }, indent=2))
            logger.info(f"Cached: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache write error for {cache_key}: {e}")
    
    def get_recent_posts(self, profile_url: str, limit: int = 3) -> List[Dict]:
        """
        Fetch recent posts from LinkedIn profile.
        
        Args:
            profile_url: Full LinkedIn profile URL
            limit: Number of recent posts to return (default 3)
        
        Returns:
            List of dicts with: content, date, engagement, themes
        """
        cache_key = f"posts_{profile_url}"
        cached = self._read_cache(cache_key)
        if cached:
            return cached[:limit]
        
        if not self.view_webpage_tool:
            logger.warning("view_webpage tool not available")
            return []
        
        try:
            # Navigate to activity/posts page
            activity_url = f"{profile_url.rstrip('/')}/recent-activity/all/"
            logger.info(f"Fetching posts from {activity_url}")
            
            result = self.view_webpage_tool(activity_url)
            html = result.get('html', '') if isinstance(result, dict) else ''
            
            if not html:
                logger.warning(f"No HTML returned for {activity_url}")
                return []
            
            posts = self._parse_posts_from_html(html, limit)
            self._write_cache(cache_key, posts)
            return posts
        
        except Exception as e:
            logger.error(f"Error fetching posts from {profile_url}: {e}")
            return []
    
    def _parse_posts_from_html(self, html: str, limit: int) -> List[Dict]:
        """Parse LinkedIn posts from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        # Find post containers (LinkedIn uses various class names)
        post_containers = soup.find_all('div', class_=re.compile(r'feed-shared-update-v2|profile-creator-shared-feed-update'))
        
        for container in post_containers[:limit]:
            try:
                post = {}
                
                # Extract post content
                content_elem = container.find('span', class_=re.compile(r'break-words|feed-shared-text'))
                if content_elem:
                    post['content'] = content_elem.get_text(strip=True)[:500]  # Truncate long posts
                else:
                    continue  # Skip if no content
                
                # Extract date
                time_elem = container.find('time') or container.find('span', class_=re.compile(r'visually-hidden'))
                if time_elem:
                    post['date'] = time_elem.get('datetime', time_elem.get_text(strip=True))
                else:
                    post['date'] = 'Recent'
                
                # Extract engagement
                reactions_elem = container.find('span', class_=re.compile(r'social-details-social-counts__reactions-count'))
                comments_elem = container.find('span', string=re.compile(r'\d+\s+comments?', re.I))
                
                engagement = []
                if reactions_elem:
                    reactions = reactions_elem.get_text(strip=True)
                    if reactions:
                        engagement.append(f"{reactions} reactions")
                if comments_elem:
                    comments = comments_elem.get_text(strip=True)
                    if comments:
                        engagement.append(comments)
                
                post['engagement'] = ', '.join(engagement) if engagement else 'No engagement data'
                
                # Detect themes from content
                post['themes'] = self._detect_themes(post['content'])
                
                posts.append(post)
            
            except Exception as e:
                logger.warning(f"Error parsing individual post: {e}")
                continue
        
        return posts
    
    def _detect_themes(self, content: str) -> List[str]:
        """Detect themes/topics from post content using keywords."""
        themes = []
        content_lower = content.lower()
        
        theme_keywords = {
            'Career Development': ['career', 'job', 'hiring', 'opportunity', 'growth'],
            'Leadership': ['leadership', 'management', 'leading', 'team', 'culture'],
            'Product Launch': ['launch', 'announcing', 'excited to share', 'new product', 'releasing'],
            'Company News': ['company', 'organization', 'announcement', 'milestone'],
            'Industry Insights': ['industry', 'trend', 'market', 'future of'],
            'Partnership': ['partner', 'collaboration', 'working with', 'join forces'],
            'Event/Speaking': ['speaking', 'event', 'conference', 'workshop', 'webinar'],
            'Thought Leadership': ['believe', 'think', 'perspective', 'view on', 'opinion']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(kw in content_lower for kw in keywords):
                themes.append(theme)
        
        return themes[:3]  # Max 3 themes
    
    def get_linkedin_messages(self, person_name: str, profile_url: Optional[str] = None) -> List[Dict]:
        """
        Fetch recent LinkedIn DMs with this person.
        
        Args:
            person_name: Full name to search for
            profile_url: Optional profile URL for better matching
        
        Returns:
            List of dicts with: direction (sent/received), preview, date, unread_status
        """
        cache_key = f"messages_{person_name.lower().replace(' ', '_')}"
        cached = self._read_cache(cache_key)
        if cached:
            return cached
        
        if not self.view_webpage_tool:
            logger.warning("view_webpage tool not available")
            return []
        
        try:
            # Navigate to messaging
            messaging_url = "https://www.linkedin.com/messaging/"
            logger.info(f"Fetching messages from {messaging_url}")
            
            result = self.view_webpage_tool(messaging_url)
            html = result.get('html', '') if isinstance(result, dict) else ''
            
            if not html:
                logger.warning("No HTML returned from messaging")
                return []
            
            messages = self._parse_messages_from_html(html, person_name)
            self._write_cache(cache_key, messages)
            return messages
        
        except Exception as e:
            logger.error(f"Error fetching LinkedIn messages: {e}")
            return []
    
    def _parse_messages_from_html(self, html: str, person_name: str) -> List[Dict]:
        """Parse LinkedIn messages from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        messages = []
        
        # Find conversation threads
        threads = soup.find_all('li', class_=re.compile(r'msg-conversation-listitem'))
        
        # Look for thread matching person name
        target_thread = None
        for thread in threads:
            name_elem = thread.find('h3', class_=re.compile(r'msg-conversation-listitem__participant-names'))
            if name_elem and person_name.lower() in name_elem.get_text(strip=True).lower():
                target_thread = thread
                break
        
        if not target_thread:
            logger.info(f"No LinkedIn conversation found with {person_name}")
            return []
        
        # Extract last 3 messages from thread
        # Note: This is a simplified parser - actual LinkedIn HTML structure varies
        msg_previews = target_thread.find_all('p', class_=re.compile(r'msg-conversation-listitem__message-snippet'))
        
        for preview_elem in msg_previews[:3]:
            try:
                msg = {
                    'preview': preview_elem.get_text(strip=True)[:200],
                    'date': 'Recent',  # LinkedIn doesn't always show dates in preview
                    'unread_status': 'read'  # Default assumption
                }
                
                # Check for unread indicator
                if target_thread.find('div', class_=re.compile(r'unread')):
                    msg['unread_status'] = 'unread'
                
                messages.append(msg)
            except Exception as e:
                logger.warning(f"Error parsing message preview: {e}")
                continue
        
        return messages
    
    def get_profile_summary(self, profile_url: str) -> Dict:
        """
        Fetch current profile summary.
        
        Args:
            profile_url: Full LinkedIn profile URL
        
        Returns:
            Dict with: current_role, headline, about, company
        """
        cache_key = f"profile_{profile_url}"
        cached = self._read_cache(cache_key)
        if cached:
            return cached
        
        if not self.view_webpage_tool:
            logger.warning("view_webpage tool not available")
            return {}
        
        try:
            logger.info(f"Fetching profile from {profile_url}")
            result = self.view_webpage_tool(profile_url)
            html = result.get('html', '') if isinstance(result, dict) else ''
            
            if not html:
                logger.warning(f"No HTML returned for {profile_url}")
                return {}
            
            profile = self._parse_profile_from_html(html)
            self._write_cache(cache_key, profile)
            return profile
        
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            return {}
    
    def _parse_profile_from_html(self, html: str) -> Dict:
        """Parse LinkedIn profile from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        profile = {}
        
        try:
            # Extract headline
            headline_elem = soup.find('div', class_=re.compile(r'text-body-medium|top-card-layout__headline'))
            if headline_elem:
                profile['headline'] = headline_elem.get_text(strip=True)
            
            # Extract current role
            role_elem = soup.find('div', class_=re.compile(r'inline-show-more-text--is-collapsed-with-line-clamp'))
            if role_elem:
                profile['current_role'] = role_elem.get_text(strip=True)
            
            # Extract company
            company_elem = soup.find('span', class_=re.compile(r'top-card-link__anchor-text'))
            if company_elem:
                profile['company'] = company_elem.get_text(strip=True)
            
            # Extract about section
            about_elem = soup.find('div', class_=re.compile(r'display-flex ph5 pv3'))
            if about_elem:
                about_text = about_elem.get_text(strip=True)
                profile['about'] = about_text[:500] if about_text else ''
        
        except Exception as e:
            logger.warning(f"Error parsing profile fields: {e}")
        
        return profile
    
    def detect_person_goals(self, profile: Dict, posts: List[Dict]) -> List[str]:
        """
        Infer person's goals from profile and recent posts.
        
        Args:
            profile: Profile dict from get_profile_summary
            posts: Posts list from get_recent_posts
        
        Returns:
            List of inferred goals/priorities
        """
        goals = []
        
        # Analyze headline and about
        combined_text = f"{profile.get('headline', '')} {profile.get('about', '')}"
        combined_lower = combined_text.lower()
        
        # Goal detection patterns
        if 'hiring' in combined_lower or 'recruiting' in combined_lower:
            goals.append("Building team / actively hiring")
        
        if 'founder' in combined_lower or 'co-founder' in combined_lower:
            goals.append("Growing/scaling company")
        
        if 'career coach' in combined_lower or 'career development' in combined_lower:
            goals.append("Helping others with career growth")
        
        if 'looking for' in combined_lower or 'seeking' in combined_lower:
            goals.append("Exploring new opportunities")
        
        # Analyze post themes
        all_themes = []
        for post in posts:
            all_themes.extend(post.get('themes', []))
        
        # Most common themes indicate focus areas
        from collections import Counter
        theme_counts = Counter(all_themes)
        top_themes = [theme for theme, count in theme_counts.most_common(2)]
        
        for theme in top_themes:
            if theme == 'Product Launch':
                goals.append("Launching new products/services")
            elif theme == 'Partnership':
                goals.append("Building strategic partnerships")
            elif theme == 'Thought Leadership':
                goals.append("Establishing thought leadership in industry")
        
        return goals[:4]  # Max 4 goals
    
    def enrich_stakeholder_profile(self, email: str, linkedin_data: Dict, dry_run: bool = False) -> Tuple[bool, List[str]]:
        """
        Enrich stakeholder profile with LinkedIn intelligence.
        
        Args:
            email: Stakeholder email (to find profile)
            linkedin_data: Dict with posts, messages, profile_summary, goals
            dry_run: If True, only log what would be added
        
        Returns:
            (success: bool, changes: List[str])
        """
        # Find profile file
        profile_file = None
        for pf in PROFILES_DIR.glob("*.md"):
            content = pf.read_text()
            if email.lower() in content.lower():
                profile_file = pf
                break
        
        if not profile_file:
            logger.warning(f"No profile found for {email}")
            return False, []
        
        changes = []
        current_content = profile_file.read_text()
        new_sections = []
        
        # Add LinkedIn posts section if not exists
        if linkedin_data.get('posts') and '## Recent LinkedIn Activity' not in current_content:
            posts_md = self._format_posts_section(linkedin_data['posts'])
            new_sections.append(f"\n## Recent LinkedIn Activity\n\n{posts_md}\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*")
            changes.append("Added Recent LinkedIn Activity section")
        
        # Add LinkedIn messages section if not exists  
        if linkedin_data.get('messages') and '## LinkedIn Messages' not in current_content:
            messages_md = self._format_messages_section(linkedin_data['messages'])
            new_sections.append(f"\n## LinkedIn Messages\n\n{messages_md}\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*")
            changes.append("Added LinkedIn Messages section")
        
        # Add goals section if not exists
        if linkedin_data.get('goals') and '## Inferred Goals' not in current_content:
            goals_md = '\n'.join(f"- {goal}" for goal in linkedin_data['goals'])
            new_sections.append(f"\n## Inferred Goals\n\n{goals_md}\n*Detected: {datetime.now().strftime('%Y-%m-%d')}*")
            changes.append("Added Inferred Goals section")
        
        if not new_sections:
            logger.info(f"No new data to add for {email}")
            return True, []
        
        # Apply updates
        if dry_run:
            logger.info(f"[DRY RUN] Would add {len(new_sections)} sections to {profile_file.name}")
            return True, changes
        
        try:
            updated_content = current_content.rstrip() + '\n' + ''.join(new_sections)
            profile_file.write_text(updated_content)
            logger.info(f"✓ Enriched profile: {profile_file.name}")
            return True, changes
        except Exception as e:
            logger.error(f"Failed to enrich profile: {e}")
            return False, []
    
    def _format_posts_section(self, posts: List[Dict]) -> str:
        """Format posts for profile markdown."""
        lines = []
        for i, post in enumerate(posts, 1):
            lines.append(f"### Post {i} ({post.get('date', 'Recent')})")
            lines.append(f"{post.get('content', 'No content')}\n")
            
            themes = post.get('themes', [])
            engagement = post.get('engagement', 'No engagement data')
            if themes:
                lines.append(f"*Themes: {', '.join(themes)}*")
            if engagement != "No engagement data":
                lines.append(f"*{engagement}*")
            lines.append("")  # Blank line
        
        return '\n'.join(lines)
    
    def _format_messages_section(self, messages: List[Dict]) -> str:
        """Format LinkedIn messages for profile markdown."""
        if not messages:
            return "*No recent LinkedIn messages found*"
        
        lines = []
        for i, msg in enumerate(messages, 1):
            lines.append(f"{i}. {msg.get('preview', 'No preview')}")
            lines.append(f"   *{msg.get('date', 'Recent')} · {msg.get('unread_status', 'read')}*")
            lines.append("")
        
        return '\n'.join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Intelligence Tool")
    parser.add_argument("--email", help="Stakeholder email to enrich")
    parser.add_argument("--profile-url", help="LinkedIn profile URL to fetch")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without saving")
    
    args = parser.parse_args()
    
    # Note: In standalone mode, view_webpage tool is not available
    # This is meant to be used as a library with tool injection
    intel = LinkedInIntel()
    
    if args.email:
        # Find profile
        for pf in PROFILES_DIR.glob("*.md"):
            content = pf.read_text()
            if args.email.lower() in content.lower():
                print(f"Found profile: {pf.name}")
                # In real use, would pass view_webpage tool and fetch data
                print("Note: Requires view_webpage tool injection for actual data fetching")
                break
        else:
            print(f"Profile not found for {args.email}")
    
    elif args.profile_url:
        print("Note: Requires view_webpage tool injection for actual data fetching")
        print(f"Would fetch from: {args.profile_url}")
