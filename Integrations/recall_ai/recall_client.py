#!/usr/bin/env python3
"""
Recall.ai REST API Client
CLI and programmatic interface for managing meeting bots
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests

# Import config - handle both module and direct execution
try:
    from .config import RECALL_API_KEY, RECALL_REGION, get_api_url, DEFAULT_BOT_CONFIG
except ImportError:
    # Direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from config import RECALL_API_KEY, RECALL_REGION, get_api_url, DEFAULT_BOT_CONFIG

_ = (
    RECALL_REGION,
    get_api_url,
    DEFAULT_BOT_CONFIG,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RecallClient:
    """REST client for Recall.ai API"""
    
    def __init__(self, api_key: Optional[str] = None, region: Optional[str] = None):
        self.api_key = api_key or RECALL_API_KEY
        if not self.api_key:
            raise ValueError("RECALL_API_KEY environment variable not set")
        
        self.region = region or RECALL_REGION
        self.base_url = get_api_url(self.region)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        
        if not response.ok:
            logger.error(f"API error {response.status_code}: {response.text}")
            response.raise_for_status()
        
        return response.json() if response.text else {}
    
    def create_bot(
        self,
        meeting_url: str,
        bot_name: Optional[str] = None,
        join_at: Optional[str] = None,
        config_overrides: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Create a bot to join a meeting
        
        Args:
            meeting_url: Video call URL (Zoom, Meet, Teams, etc.)
            bot_name: Display name for the bot
            join_at: ISO timestamp for scheduled join (must be 10+ min in future for scheduled)
            config_overrides: Override default bot configuration
        
        Returns:
            Bot object with id, status, etc.
        """
        # Deep copy to avoid mutating the default
        import copy
        config = copy.deepcopy(DEFAULT_BOT_CONFIG)
        
        if config_overrides:
            # Deep merge overrides
            for key, value in config_overrides.items():
                if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                    config[key].update(value)
                else:
                    config[key] = value
        
        payload = {
            "meeting_url": meeting_url,
            "bot_name": bot_name or config.pop("bot_name", "Zo Notetaker"),
        }
        
        if join_at:
            payload["join_at"] = join_at
        
        # Add all config keys to payload (excluding internal keys starting with _)
        api_keys = [
            "automatic_video_output", "automatic_audio_output", 
            "automatic_leave", "transcription_options",
            "recording_mode", "recording_mode_options", "recording_config",
            "chat", "zoom", "google_meet", "breakout_room", "metadata"
        ]
        for key in api_keys:
            if key in config and config[key]:
                payload[key] = config[key]
        
        logger.info(f"Creating bot for meeting: {meeting_url}")
        result = self._request("POST", "/bot/", json=payload)
        logger.info(f"Bot created: {result.get('id')}")
        return result
    
    def get_bot(self, bot_id: str) -> Dict[str, Any]:
        """Get bot details by ID"""
        return self._request("GET", f"/bot/{bot_id}/")
    
    def list_bots(
        self,
        limit: int = 20,
        cursor: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List bots with pagination
        
        Args:
            limit: Number of results per page
            cursor: Pagination cursor
            status: Filter by status (e.g., 'done', 'in_call', 'joining')
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if status:
            params["status"] = status
        
        return self._request("GET", "/bot/", params=params)
    
    def delete_bot(self, bot_id: str) -> Dict[str, Any]:
        """Delete/cancel a scheduled bot"""
        return self._request("DELETE", f"/bot/{bot_id}/")
    
    def get_transcript(self, bot_id: str) -> Optional[Dict]:
        """Get transcript for a completed recording using new API"""
        # First check if transcript is in bot recordings
        bot = self.get_bot(bot_id)
        if bot and bot.get("recordings"):
            for recording in bot["recordings"]:
                shortcuts = recording.get("media_shortcuts", {})
                transcript_data = shortcuts.get("transcript")
                if transcript_data and transcript_data.get("data", {}).get("download_url"):
                    # Download from the URL
                    download_url = transcript_data["data"]["download_url"]
                    try:
                        response = requests.get(download_url)
                        response.raise_for_status()
                        return response.json()
                    except Exception as e:
                        logger.warning(f"Could not download transcript from URL: {e}")
        
        # Fallback: try the transcript retrieve endpoint
        url = f"{self.base_url}/bot/{bot_id}/transcript"
        try:
            response = requests.get(url, headers=self.session.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Transcript may not be ready yet
            logger.warning(f"Transcript not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return None
    
    def get_recording(self, bot_id: str) -> Dict[str, Any]:
        """Get recording URLs for a completed bot"""
        bot = self.get_bot(bot_id)
        return {
            "video_url": bot.get("video_url"),
            "audio_url": bot.get("audio_url"),
            "status": bot.get("status_changes", [])[-1] if bot.get("status_changes") else None,
        }
    
    def download_recording(
        self,
        bot_id: str,
        output_dir: str,
        include_video: bool = True,
        include_audio: bool = True,
        include_transcript: bool = True,
    ) -> Dict[str, str]:
        """
        Download all recording artifacts
        
        Returns:
            Dict of artifact type -> local file path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        bot = self.get_bot(bot_id)
        downloaded = {}
        
        # Download video
        if include_video and bot.get("video_url"):
            video_path = output_path / "video.mp4"
            logger.info(f"Downloading video to {video_path}")
            self._download_file(bot["video_url"], video_path)
            downloaded["video"] = str(video_path)
        
        # Download audio
        if include_audio and bot.get("audio_url"):
            audio_path = output_path / "audio.mp3"
            logger.info(f"Downloading audio to {audio_path}")
            self._download_file(bot["audio_url"], audio_path)
            downloaded["audio"] = str(audio_path)
        
        # Download transcript
        if include_transcript:
            try:
                transcript = self.get_transcript(bot_id)
                transcript_json = output_path / "transcript.json"
                transcript_txt = output_path / "transcript.txt"
                
                # Save raw JSON
                with open(transcript_json, "w") as f:
                    json.dump(transcript, f, indent=2)
                downloaded["transcript_json"] = str(transcript_json)
                
                # Format and save text version
                formatted = self._format_transcript(transcript)
                with open(transcript_txt, "w") as f:
                    f.write(formatted)
                downloaded["transcript_txt"] = str(transcript_txt)
                
                logger.info(f"Transcript saved to {transcript_txt}")
            except Exception as e:
                logger.warning(f"Could not download transcript: {e}")
        
        # Save participant events
        if bot.get("status_changes"):
            participants_path = output_path / "participants.json"
            with open(participants_path, "w") as f:
                json.dump({
                    "bot_id": bot_id,
                    "meeting_url": bot.get("meeting_url"),
                    "status_changes": bot.get("status_changes", []),
                    "participants": bot.get("meeting_participants", []),
                }, f, indent=2)
            downloaded["participants"] = str(participants_path)
        
        return downloaded
    
    def _download_file(self, url: str, output_path: Path) -> None:
        """Download file from URL"""
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def _format_transcript(self, transcript_data: Dict) -> str:
        """Format transcript data into readable text"""
        lines = []
        
        for word in transcript_data.get("words", []):
            speaker = word.get("speaker", "Unknown")
            text = word.get("text", "")
            start = word.get("start_time", 0)
            
            # Format timestamp as MM:SS
            minutes = int(start // 60)
            seconds = int(start % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            
            lines.append(f"{timestamp} {speaker}: {text}")
        
        return "\n".join(lines)
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            result = self.list_bots(limit=1)
            logger.info(f"Connection successful. Region: {self.region}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def check_bot_health(self, max_recording_hours: float = 4.0) -> Dict[str, Any]:
        """
        Check for stuck/failed bots
        
        Args:
            max_recording_hours: Max hours a bot can be recording before considered stuck
        
        Returns:
            Dict with stuck_bots and fatal_bots lists
        """
        result = {
            'stuck_bots': [],
            'fatal_bots': [],
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'max_recording_hours': max_recording_hours,
        }
        
        # Check for stuck bots (recording too long)
        try:
            recording_bots = self.list_bots(status='in_call_recording', limit=100)
            for bot in recording_bots.get('data', []):
                # Check when bot started recording
                status_changes = bot.get('status_changes', [])
                recording_start = None
                for change in reversed(status_changes):
                    if change.get('status') == 'in_call_recording':
                        recording_start = change.get('timestamp')
                        break
                
                if recording_start:
                    try:
                        start_time = datetime.fromisoformat(recording_start.replace('Z', '+00:00'))
                        hours_recording = (datetime.now(timezone.utc) - start_time).total_seconds() / 3600
                        if hours_recording > max_recording_hours:
                            result['stuck_bots'].append({
                                'bot_id': bot.get('id'),
                                'hours_recording': round(hours_recording, 2),
                                'meeting_url': bot.get('meeting_url'),
                                'started_at': recording_start,
                            })
                    except Exception as e:
                        logger.warning(f"Could not calculate recording time for {bot.get('id')}: {e}")
        except Exception as e:
            logger.error(f"Error checking recording bots: {e}")
        
        # Check for fatal status bots
        try:
            fatal_bots = self.list_bots(status='fatal', limit=50)
            for bot in fatal_bots.get('data', []):
                result['fatal_bots'].append({
                    'bot_id': bot.get('id'),
                    'meeting_url': bot.get('meeting_url'),
                    'error': bot.get('error_message', 'Unknown error'),
                    'status_changes': bot.get('status_changes', [])
                })
        except Exception as e:
            logger.error(f"Error checking fatal bots: {e}")
        
        return result


def main():
    parser = argparse.ArgumentParser(description="Recall.ai CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # create-bot
    create_parser = subparsers.add_parser("create-bot", help="Create a bot to join a meeting")
    create_parser.add_argument("meeting_url", help="Video call URL")
    create_parser.add_argument("--bot-name", default="Zo Notetaker", help="Bot display name")
    create_parser.add_argument("--join-at", help="ISO timestamp for scheduled join")
    
    # list-bots
    list_parser = subparsers.add_parser("list-bots", help="List bots")
    list_parser.add_argument("--limit", type=int, default=20, help="Number of results")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--older-than", type=float, help="Only include bots older than N hours")
    
    # get-bot
    get_parser = subparsers.add_parser("get-bot", help="Get bot details")
    get_parser.add_argument("bot_id", help="Bot ID")
    
    # download
    download_parser = subparsers.add_parser("download", help="Download recording artifacts")
    download_parser.add_argument("bot_id", help="Bot ID")
    download_parser.add_argument("--output-dir", required=True, help="Output directory")
    download_parser.add_argument("--no-video", action="store_true", help="Skip video download")
    download_parser.add_argument("--no-audio", action="store_true", help="Skip audio download")
    download_parser.add_argument("--no-transcript", action="store_true", help="Skip transcript download")
    
    # delete-bot
    delete_parser = subparsers.add_parser("delete-bot", help="Delete/cancel a bot")
    delete_parser.add_argument("bot_id", help="Bot ID")
    
    # test
    subparsers.add_parser("test", help="Test API connection")
    
    # health-check
    health_parser = subparsers.add_parser("health-check", help="Check for stuck/failed bots")
    health_parser.add_argument("--max-hours", type=float, default=4.0,
                              help="Max hours before a recording bot is considered stuck (default: 4.0)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = RecallClient()
    
    if args.command == "create-bot":
        result = client.create_bot(
            args.meeting_url,
            bot_name=args.bot_name,
            join_at=args.join_at,
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == "list-bots":
        result = client.list_bots(limit=args.limit, status=args.status)
        # Filter by older-than if specified
        if args.older_than:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=args.older_than)
            filtered_data = []
            for bot in result.get('data', []):
                created_at = bot.get('created_at')
                if created_at:
                    try:
                        bot_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if bot_time < cutoff:
                            filtered_data.append(bot)
                    except Exception:
                        pass
            result['data'] = filtered_data
            result['count'] = len(filtered_data)
        print(json.dumps(result, indent=2))
    
    elif args.command == "get-bot":
        result = client.get_bot(args.bot_id)
        print(json.dumps(result, indent=2))
    
    elif args.command == "download":
        result = client.download_recording(
            args.bot_id,
            args.output_dir,
            include_video=not args.no_video,
            include_audio=not args.no_audio,
            include_transcript=not args.no_transcript,
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == "delete-bot":
        result = client.delete_bot(args.bot_id)
        print(json.dumps(result, indent=2))
    
    elif args.command == "test":
        success = client.test_connection()
        sys.exit(0 if success else 1)
    
    elif args.command == "health-check":
        result = client.check_bot_health(max_recording_hours=args.max_hours)
        print(json.dumps(result, indent=2))
        
        # Exit with non-zero if issues found
        if result['stuck_bots'] or result['fatal_bots']:
            sys.exit(1)


if __name__ == "__main__":
    main()
