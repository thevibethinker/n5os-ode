#!/usr/bin/env python3
"""
Daily Newsletter Scanner and SMS Delivery
Scans Gmail for newsletters received in the last 24 hours and delivers a digest via SMS.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import base64
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


class NewsletterScanner:
    """Scans Gmail for newsletters and creates SMS-friendly digests."""
    
    def __init__(self):
        self.gmail_service = None
        self.sms_client = None
        
    async def initialize_gmail(self):
        """Initialize Gmail service (requires authentication via Pipedream)."""
        try:
            # Gmail service would be initialized here via Pipedream integration
            logger.info("Gmail service initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gmail: {e}")
            return False
    
    async def query_newsletters(self, hours: int = 24, max_results: int = 20) -> list:
        """
        Query Gmail for newsletter emails from the past N hours.
        
        Args:
            hours: Number of hours to look back
            max_results: Maximum emails to retrieve
            
        Returns:
            List of email objects with newsletter content
        """
        try:
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            time_str = time_threshold.strftime("%Y/%m/%d")
            
            # Search query for newsletters
            query = f'(from:newsletter OR from:digest OR subject:newsletter OR subject:digest) after:{time_str}'
            
            logger.info(f"Querying Gmail with: {query}")
            
            # Gmail query would execute here via Pipedream
            # For now, returning placeholder structure
            emails = await self._mock_gmail_query(query, max_results)
            
            logger.info(f"Found {len(emails)} newsletters")
            return emails
            
        except Exception as e:
            logger.error(f"Failed to query newsletters: {e}")
            return []
    
    async def _mock_gmail_query(self, query: str, max_results: int) -> list:
        """Mock Gmail query for development."""
        # This would be replaced with actual Gmail API call
        return []
    
    def extract_newsletter_info(self, email: dict) -> dict:
        """
        Extract key information from a newsletter email.
        
        Args:
            email: Email object from Gmail
            
        Returns:
            Dictionary with title, sender, and summary
        """
        try:
            headers = email.get('payload', {}).get('headers', [])
            body_parts = email.get('payload', {}).get('parts', [])
            
            # Extract headers
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            
            # Clean sender name
            sender_name = sender.split('<')[0].strip() if '<' in sender else sender
            
            # Extract body
            text_body = ""
            for part in body_parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        text_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
            
            # Generate brief summary (first 150 chars of meaningful content)
            summary = self._generate_summary(text_body, subject)
            
            return {
                'subject': subject,
                'sender': sender_name,
                'summary': summary,
                'received_at': email.get('internalDate')
            }
            
        except Exception as e:
            logger.error(f"Error extracting newsletter info: {e}")
            return None
    
    def _generate_summary(self, body: str, subject: str) -> str:
        """Generate a brief summary from email body."""
        # Remove common footer content and clean up
        lines = body.split('\n')
        
        # Filter out empty lines and common footer patterns
        meaningful_lines = []
        for line in lines:
            line = line.strip()
            if (line and 
                len(line) > 10 and 
                not line.startswith('http') and
                not line.startswith('©') and
                'Unsubscribe' not in line):
                meaningful_lines.append(line)
        
        # Take first meaningful lines (up to 2 sentences)
        summary = ' '.join(meaningful_lines[:2]) if meaningful_lines else subject
        
        # Truncate to 150 characters
        if len(summary) > 150:
            summary = summary[:147] + '...'
        
        return summary
    
    async def create_sms_digest(self, newsletters: list) -> str:
        """
        Create an SMS-friendly digest from newsletters.
        
        Args:
            newsletters: List of newsletter info dictionaries
            
        Returns:
            Formatted SMS message (under 1000 characters)
        """
        if not newsletters:
            return "📰 No newsletters received in the past 24 hours."
        
        today = datetime.now().strftime("%b %d")
        digest = f"📰 Newsletter Digest - {today}\n\n"
        
        for i, nl in enumerate(newsletters[:10], 1):  # Limit to 10 for SMS length
            if nl:
                digest += f"• {nl['subject'][:50]}\n  {nl['sender']}\n"
        
        # Ensure SMS is under 1000 characters
        if len(digest) > 900:
            digest = digest[:897] + "..."
        
        logger.info(f"Created digest ({len(digest)} chars): {digest[:100]}...")
        return digest
    
    async def send_sms_digest(self, message: str, phone_number: str) -> bool:
        """
        Send newsletter digest via SMS.
        
        Args:
            message: SMS message content
            phone_number: Recipient phone number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Sending SMS to {phone_number}: {message[:50]}...")
            
            # SMS would be sent here via Telnyx or similar service
            # For now, this is a placeholder
            logger.info("SMS sent successfully (mock)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False


async def run_daily_newsletter_scan():
    """Main entry point for daily newsletter scan."""
    logger.info("Starting daily newsletter scan...")
    
    scanner = NewsletterScanner()
    
    # Initialize Gmail
    if not await scanner.initialize_gmail():
        logger.error("Failed to initialize Gmail service")
        return False
    
    # Query newsletters from past 24 hours
    newsletters = await scanner.query_newsletters(hours=24, max_results=20)
    
    if not newsletters:
        logger.info("No newsletters found")
        return True
    
    # Extract information from each newsletter
    newsletter_info = []
    for email in newsletters:
        info = scanner.extract_newsletter_info(email)
        if info:
            newsletter_info.append(info)
    
    # Create SMS digest
    digest = await scanner.create_sms_digest(newsletter_info)
    
    # Send SMS
    # In production, this would be the user's phone number
    phone_number = "+1234567890"  # Placeholder
    success = await scanner.send_sms_digest(digest, phone_number)
    
    if success:
        logger.info("Newsletter scan completed successfully")
    else:
        logger.warning("Newsletter scan completed with errors")
    
    return success


if __name__ == "__main__":
    asyncio.run(run_daily_newsletter_scan())

