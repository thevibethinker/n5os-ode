"""
Fireflies.ai GraphQL API Client
Fetches transcript data via GraphQL API
"""

import logging
from typing import Optional, Dict, Any, List
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

from .config import Config

logger = logging.getLogger(__name__)

class FirefliesClient:
    """GraphQL client for Fireflies.ai API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.get_api_key()
        
        transport = RequestsHTTPTransport(
            url="https://api.fireflies.ai/graphql",
            headers={"Authorization": f"Bearer {self.api_key}"},
            verify=True,
            retries=3,
        )
        
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
    
    def get_transcript(self, transcript_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full transcript data by ID
        
        Returns:
            Dict with keys: id, title, date, duration, participants, sentences, summary
        """
        query = gql("""
            query GetTranscript($transcriptId: String!) {
                transcript(id: $transcriptId) {
                    id
                    title
                    date
                    duration
                    participants
                    transcript_url
                    audio_url
                    video_url
                    sentences {
                        index
                        text
                        raw_text
                        start_time
                        end_time
                        speaker_name
                        speaker_id
                    }
                    summary {
                        keywords
                        action_items
                        outline
                        shorthand_bullet
                        overview
                    }
                    organizer_email
                    meeting_attendees {
                        displayName
                        email
                        name
                        location
                    }
                }
            }
        """)
        
        try:
            result = self.client.execute(query, variable_values={"transcriptId": transcript_id})
            transcript_data = result.get("transcript")
            
            if not transcript_data:
                logger.error(f"No transcript data returned for ID: {transcript_id}")
                return None
            
            logger.info(f"Fetched transcript {transcript_id}: {transcript_data.get('title', 'Untitled')}")
            return transcript_data
            
        except Exception as e:
            logger.error(f"Failed to fetch transcript {transcript_id}: {e}")
            return None
    
    def list_transcripts(
        self, 
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        List recent transcripts with optional date filtering
        
        Returns:
            List of transcript summaries (id, title, date, duration)
        """
        query = gql("""
            query ListTranscripts($limit: Int) {
                transcripts(limit: $limit) {
                    id
                    title
                    date
                    duration
                    organizer_email
                }
            }
        """)
        
        try:
            result = self.client.execute(query, variable_values={"limit": limit})
            transcripts = result.get("transcripts", [])
            
            logger.info(f"Listed {len(transcripts)} transcripts")
            return transcripts
            
        except Exception as e:
            logger.error(f"Failed to list transcripts: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test API connection and authentication"""
        try:
            transcripts = self.list_transcripts(limit=1)
            logger.info("Fireflies API connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Fireflies API connection test FAILED: {e}")
            return False
    
    def convert_to_zo_format(self, fireflies_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Fireflies transcript format to Zo transcript format
        
        Args:
            fireflies_data: Raw Fireflies transcript data
            
        Returns:
            Zo-compatible transcript dict
        """
        sentences = fireflies_data.get("sentences", [])
        
        # Build full text
        full_text = " ".join([s.get("text", "") for s in sentences])
        
        # Convert sentences to utterances
        utterances = []
        for sentence in sentences:
            utterances.append({
                "speaker": sentence.get("speaker_name", "Unknown"),
                "start": int(sentence.get("start_time", 0) * 1000),  # Convert to ms
                "end": int(sentence.get("end_time", 0) * 1000),
                "text": sentence.get("text", "")
            })
        
        # Build Zo format
        zo_transcript = {
            "text": full_text,
            "utterances": utterances,
            "source_file": None,  # Will be set if audio downloaded
            "mime_type": "audio/mpeg",
            "duration_seconds": fireflies_data.get("duration", 0),
            "fireflies_id": fireflies_data.get("id"),
            "fireflies_title": fireflies_data.get("title"),
            "fireflies_date": fireflies_data.get("date"),
            "fireflies_participants": fireflies_data.get("participants", []),
            "fireflies_organizer": fireflies_data.get("organizer"),
            "fireflies_summary": fireflies_data.get("summary"),
            "gdrive_id": None  # Will be set later if uploaded to GDrive
        }
        
        return zo_transcript


