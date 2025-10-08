#!/usr/bin/env python3
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
import asyncio
import aiohttp
import hashlib

# Setup logging per N5OS
LOG_DIR = '/home/workspace/Knowledge/logs/Email'
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Voice Schema for blurb/ticket generation
VOICE_CONFIG = {
    "blurb_tone": "concise",
    "ticket_formality": "balanced", 
    "cta_style": "soft",
    "warm_intro_tone": "connector-style"
}

class BlurbTicketGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
    async def llm_query(self, session: aiohttp.ClientSession, prompt: str, model: str = "gpt-4o-mini") -> str:
        """LLM query for content generation"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 400
        }
        
        try:
            async with session.post("https://api.openai.com/v1/chat/completions", 
                                  headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    logger.error(f"LLM query failed: {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"LLM query exception: {e}")
            return ""

    async def detect_warm_intro_opportunities(self, session: aiohttp.ClientSession, 
                                            content_map: Dict) -> List[Dict]:
        """Use LLM to detect warm introduction opportunities"""
        prompt = f"""
        Analyze this content map for warm introduction opportunities. Look for:
        - Multiple people mentioned who don't know each other
        - Shared interests, complementary skills, or business synergies
        - Explicit requests for connections or networking
        
        Content: {json.dumps(content_map, indent=2)}
        
        Return a JSON list of opportunities with fields:
        - person_a: name
        - person_b: name  
        - connection_rationale: why they should connect
        - priority: high/medium/low
        - intro_context: brief context for introduction
        """
        
        result = await self.llm_query(session, prompt)
        try:
            return json.loads(result) if result else []
        except json.JSONDecodeError:
            logger.warning("Failed to parse warm intro opportunities from LLM")
            return []

    async def generate_blurb(self, session: aiohttp.ClientSession, content: Dict) -> str:
        """Generate concise blurb from content"""
        prompt = f"""
        Create a concise blurb (2-3 sentences max) capturing the key essence of this content.
        Use {VOICE_CONFIG['blurb_tone']} tone. Focus on main insights or outcomes.
        
        Content: {json.dumps(content, indent=2)}
        """
        return await self.llm_query(session, prompt)

    async def generate_follow_up_email(self, session: aiohttp.ClientSession, 
                                     content_map: Dict, recipient_context: Dict) -> str:
        """Generate follow-up email per Function [02] specs"""
        prompt = f"""
        Generate a follow-up email using these specifications:
        - Voice: {VOICE_CONFIG['ticket_formality']} formality, {VOICE_CONFIG['cta_style']} CTA
        - Structure: greeting → context reference → key insights → soft next step
        - Length: 150-250 words
        - Avoid generic pleasantries
        
        Meeting content: {json.dumps(content_map, indent=2)}
        Recipient context: {json.dumps(recipient_context, indent=2)}
        """
        return await self.llm_query(session, prompt)

    async def generate_warm_intro_email(self, session: aiohttp.ClientSession, 
                                      opportunity: Dict) -> Dict:
        """Generate warm introduction emails for both parties"""
        prompt_template = """
        Generate a warm introduction email with {VOICE_CONFIG['warm_intro_tone']} tone:
        - Brief intro of both parties
        - Clear connection rationale
        - Soft CTA encouraging connection
        - 100-150 words max
        
        Opportunity: {opportunity}
        Recipient: {recipient}
        """
        
        emails = {}
        for recipient in ['person_a', 'person_b']:
            other_person = 'person_b' if recipient == 'person_a' else 'person_a'
            prompt = prompt_template.format(
                opportunity=json.dumps(opportunity, indent=2),
                recipient=opportunity[recipient]
            )
            emails[recipient] = await self.llm_query(session, prompt)
            
        return emails

    def create_ticket(self, ticket_type: str, content: Dict, priority: str = "medium") -> Dict:
        """Create standardized ticket format"""
        ticket_id = hashlib.md5(f"{ticket_type}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        return {
            "ticket_id": ticket_id,
            "type": ticket_type,
            "priority": priority,
            "created": datetime.now().isoformat(),
            "status": "pending_approval",
            "content": content,
            "voice_config": VOICE_CONFIG
        }

    async def process_content_map(self, content_map: Dict, output_dir: str, dry_run: bool = False) -> Dict:
        """Main processing pipeline for content map"""
        results = {
            "blurbs": [],
            "follow_up_emails": [],
            "warm_intro_tickets": [],
            "processing_log": []
        }
        
        async with aiohttp.ClientSession() as session:
            # Generate main blurb
            blurb = await self.generate_blurb(session, content_map)
            if blurb:
                results["blurbs"].append({
                    "content": blurb,
                    "source": "main_content_map"
                })
                logger.info(f"Generated main blurb: {blurb[:50]}...")

            # Detect warm intro opportunities
            warm_opportunities = await self.detect_warm_intro_opportunities(session, content_map)
            logger.info(f"Detected {len(warm_opportunities)} warm intro opportunities")
            
            for opportunity in warm_opportunities:
                # Generate warm intro emails
                intro_emails = await self.generate_warm_intro_email(session, opportunity)
                
                # Create ticket for warm intro
                ticket = self.create_ticket("warm_introduction", {
                    "opportunity": opportunity,
                    "emails": intro_emails
                }, priority=opportunity.get("priority", "medium"))
                
                results["warm_intro_tickets"].append(ticket)
                logger.info(f"Created warm intro ticket {ticket['ticket_id']} for {opportunity['person_a']} <-> {opportunity['person_b']}")

            # Generate follow-up emails for participants (if participant data exists)
            if "participants" in content_map:
                for participant in content_map["participants"]:
                    email = await self.generate_follow_up_email(session, content_map, participant)
                    if email:
                        results["follow_up_emails"].append({
                            "recipient": participant.get("name", "unknown"),
                            "email": email
                        })

        # Save results if not dry run
        if not dry_run:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"blurb_tickets_{timestamp}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {os.path.abspath(output_file)}")
        
        return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate blurbs and tickets from content map")
    parser.add_argument("content_map", help="Path to content_map.json")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.content_map):
        logger.error(f"Content map not found: {args.content_map}")
        return 1
    
    # Load content map
    with open(args.content_map, 'r') as f:
        content_map = json.load(f)
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process
    generator = BlurbTicketGenerator()
    results = asyncio.run(generator.process_content_map(content_map, args.output_dir, args.dry_run))
    
    # Summary output
    print(f"\nProcessing Summary:")
    print(f"- Blurbs generated: {len(results['blurbs'])}")
    print(f"- Follow-up emails: {len(results['follow_up_emails'])}")
    print(f"- Warm intro tickets: {len(results['warm_intro_tickets'])}")
    
    if args.dry_run:
        print("\nDry run completed - no files saved")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())