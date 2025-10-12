#!/usr/bin/env python3
"""
Email Analyzer for Weekly Summary System

Analyzes Gmail threads for meeting participants and CRM contacts to build
compounding understanding of relationships over time.

Version: 1.0.0
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


class EmailAnalyzer:
    """Analyze email activity for weekly summaries"""
    
    def __init__(self, gmail_tool=None):
        """
        Initialize email analyzer
        
        Args:
            gmail_tool: Zo's Gmail API tool (use_app_gmail)
        """
        self.gmail_tool = gmail_tool
        
    def get_recent_emails_for_person(
        self, 
        email_address: str, 
        lookback_days: int = 30
    ) -> List[Dict]:
        """
        Get email threads involving specific person in last N days
        
        Args:
            email_address: Email address to search for
            lookback_days: Days to look back (default: 30)
            
        Returns:
            List of email thread summaries
        """
        if not self.gmail_tool:
            log.warning("Gmail tool not available, returning empty results")
            return []
        
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=lookback_days)
            
            # Format for Gmail API
            after_date = start_date.strftime('%Y/%m/%d')
            
            # Search query: from OR to this person, after date
            query = f"(from:{email_address} OR to:{email_address}) after:{after_date}"
            
            log.info(f"Searching Gmail for: {email_address} (last {lookback_days} days)")
            
            # Use Gmail API tool
            results = self.gmail_tool('gmail-find-email', {
                'q': query,
                'maxResults': 50,
                'withTextPayload': True
            })
            
            if not results or not results.get('messages'):
                log.info(f"No emails found for {email_address}")
                return []
            
            # Parse results
            threads = []
            for message in results.get('messages', []):
                thread = {
                    'id': message.get('id'),
                    'thread_id': message.get('threadId'),
                    'snippet': message.get('snippet', ''),
                    'date': message.get('internalDate'),  # Unix timestamp ms
                    'subject': self._extract_subject(message),
                    'from': self._extract_sender(message),
                    'to': self._extract_recipients(message)
                }
                threads.append(thread)
            
            log.info(f"Found {len(threads)} email threads for {email_address}")
            return threads
            
        except Exception as e:
            log.error(f"Error fetching emails for {email_address}: {e}")
            return []
    
    def get_emails_for_multiple_people(
        self,
        email_addresses: List[str],
        lookback_days: int = 30
    ) -> Dict[str, List[Dict]]:
        """
        Get emails for multiple people
        
        Args:
            email_addresses: List of email addresses
            lookback_days: Days to look back
            
        Returns:
            Dict mapping email -> list of threads
        """
        results = {}
        
        for email in email_addresses:
            threads = self.get_recent_emails_for_person(email, lookback_days)
            if threads:
                results[email] = threads
        
        return results
    
    def analyze_email_activity(
        self,
        email_threads: Dict[str, List[Dict]]
    ) -> Dict[str, Dict]:
        """
        Analyze email activity to summarize volume, topics, recency
        
        Args:
            email_threads: Dict mapping email -> threads
            
        Returns:
            Dict with analysis per person
        """
        analysis = {}
        
        for email, threads in email_threads.items():
            if not threads:
                continue
            
            # Count threads and messages
            thread_count = len(threads)
            
            # Get most recent date
            most_recent = None
            for thread in threads:
                if thread.get('date'):
                    # Convert Unix timestamp (ms) to datetime
                    thread_date = datetime.fromtimestamp(
                        int(thread['date']) / 1000,
                        tz=timezone.utc
                    )
                    if not most_recent or thread_date > most_recent:
                        most_recent = thread_date
            
            # Extract topics from subjects
            subjects = [t.get('subject', '') for t in threads if t.get('subject')]
            topics = self._extract_topics(subjects)
            
            analysis[email] = {
                'email_count': thread_count,
                'last_contact': most_recent.strftime('%Y-%m-%d') if most_recent else 'Unknown',
                'topics': topics[:5],  # Top 5 topics
                'recent_subjects': subjects[:3]  # 3 most recent subjects
            }
        
        return analysis
    
    def identify_key_threads(
        self,
        email_threads: Dict[str, List[Dict]],
        top_n: int = 5
    ) -> List[Dict]:
        """
        Surface most important conversations
        
        Args:
            email_threads: Dict mapping email -> threads
            top_n: Number of key threads to return
            
        Returns:
            List of key thread summaries
        """
        all_threads = []
        
        # Flatten all threads with context
        for email, threads in email_threads.items():
            for thread in threads:
                thread['participant'] = email
                all_threads.append(thread)
        
        # Sort by date (most recent first)
        all_threads.sort(
            key=lambda t: int(t.get('date', 0)),
            reverse=True
        )
        
        # Take top N
        key_threads = []
        for thread in all_threads[:top_n]:
            key_threads.append({
                'participant': thread['participant'],
                'subject': thread.get('subject', 'No subject'),
                'snippet': thread.get('snippet', ''),
                'date': thread.get('date')
            })
        
        return key_threads
    
    def identify_high_activity_contacts(
        self,
        email_analysis: Dict[str, Dict],
        threshold: int = 2
    ) -> List[tuple]:
        """
        Identify contacts with high email activity
        
        Args:
            email_analysis: Output from analyze_email_activity()
            threshold: Minimum emails to be considered high activity
            
        Returns:
            List of (email, activity_data) tuples sorted by volume
        """
        high_activity = []
        
        for email, data in email_analysis.items():
            if data.get('email_count', 0) >= threshold:
                high_activity.append((email, data))
        
        # Sort by email count descending
        high_activity.sort(key=lambda x: x[1]['email_count'], reverse=True)
        
        return high_activity
    
    # Helper methods
    
    def _extract_subject(self, message: Dict) -> str:
        """Extract subject from message"""
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name') == 'Subject':
                return header.get('value', 'No subject')
        return 'No subject'
    
    def _extract_sender(self, message: Dict) -> str:
        """Extract sender from message"""
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name') == 'From':
                return header.get('value', '')
        return ''
    
    def _extract_recipients(self, message: Dict) -> str:
        """Extract recipients from message"""
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name') == 'To':
                return header.get('value', '')
        return ''
    
    def _extract_topics(self, subjects: List[str]) -> List[str]:
        """
        Extract common topics from email subjects
        
        Simple approach: identify repeated keywords
        """
        if not subjects:
            return []
        
        # Count word frequency (excluding common words)
        stopwords = {'re', 'fwd', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        word_counts = defaultdict(int)
        
        for subject in subjects:
            words = subject.lower().split()
            for word in words:
                word = word.strip('[]():,.')
                if len(word) > 3 and word not in stopwords:
                    word_counts[word] += 1
        
        # Sort by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return top topics (words appearing multiple times)
        topics = [word for word, count in sorted_words if count > 1]
        
        return topics[:10]  # Top 10 topics


def main():
    """Test email analyzer"""
    print("Email Analyzer v1.0.0")
    print("=" * 50)
    print("This module is designed to be imported by weekly_summary.py")
    print("It requires Zo's Gmail API tool to function.")
    print("")
    print("Example usage:")
    print("  from email_analyzer import EmailAnalyzer")
    print("  analyzer = EmailAnalyzer(gmail_tool=use_app_gmail)")
    print("  threads = analyzer.get_recent_emails_for_person('user@example.com')")
    print("")


if __name__ == "__main__":
    main()
